import pytest
from pytailwind import Tailwind
from pytailwind.defaults import COLORS, SPACING

@pytest.fixture
def tw():
    return Tailwind()

# Tests for internal methods removed - those methods no longer exist in the new architecture
# The new generator uses plugins and AST for a cleaner implementation

def test_generate_simple(tw):
    html = '<div class="text-center p-4"></div>'
    css = tw.generate(html)
    assert ".text-center" in css
    assert "text-align: center;" in css
    assert ".p-4" in css
    assert "padding: 1rem;" in css

def test_generate_colors(tw):
    html = '<div class="text-red-500 bg-blue-500"></div>'
    css = tw.generate(html)
    assert ".text-red-500" in css
    assert "color: #ef4444;" in css
    assert ".bg-blue-500" in css
    assert "background-color: #3b82f6;" in css

def test_generate_opacity(tw):
    html = '<div class="text-red-500/50"></div>'
    css = tw.generate(html)
    assert ".text-red-500\\/50" in css
    assert "rgba(239, 68, 68, 0.5)" in css

def test_generate_variants(tw):
    html = '<div class="hover:text-red-500 sm:bg-white dark:text-white"></div>'
    css = tw.generate(html)
    assert ".hover\\:text-red-500:hover" in css
    assert "@media (min-width: 640px) {.sm\\:bg-white" in css
    assert "@media (prefers-color-scheme: dark) {.dark\\:text-white" in css

def test_generate_arbitrary_values(tw):
    html = '<div class="w-[100px] bg-[#123456]"></div>'
    css = tw.generate(html)
    assert ".w-\\[100px\\]" in css
    assert "width: 100px;" in css
    assert ".bg-\\[\\#123456\\]" in css
    assert "background-color: #123456;" in css

def test_generate_multi_requirement(tw):
    # px-4 -> padding-left, padding-right
    html = '<div class="px-4"></div>'
    css = tw.generate(html)
    assert ".px-4" in css
    assert "padding-left" in css
    assert "padding-right" in css

def test_generate_gradients(tw):
    # from-red-500 via-blue-500 to-green-500
    html = '<div class="from-red-500 via-blue-500 to-green-500 bg-gradient-to-r"></div>'
    css = tw.generate(html)
    assert ".from-red-500" in css
    assert "--tw-gradient-from: #ef4444" in css
    assert ".via-blue-500" in css
    assert ".to-green-500" in css

def test_generate_filter(tw):
    # blur-sm -> filter: blur(4px)
    html = '<div class="blur-sm"></div>'
    css = tw.generate(html)
    assert ".blur-sm" in css
    assert "blur(4px)" in css

def test_generate_dynamic_multi(tw):
    # Dynamic value that produces multiple properties
    # e.g. mx-[10px] -> margin-left: 10px; margin-right: 10px;
    html = '<div class="mx-[10px]"></div>'
    css = tw.generate(html)
    assert ".mx-\\[10px\\]" in css
    # New generator uses proper spacing in CSS
    assert "margin-left: 10px" in css
    assert "margin-right: 10px" in css

def test_unknown_class(tw):
    html = '<div class="unknown-class"></div>'
    css = tw.generate(html)
    assert "unknown-class" not in css

def test_empty_class_attribute(tw):
    html = '<div class=""></div>'
    css = tw.generate(html)
    assert css == ""

def test_multiple_same_class(tw):
    html = '<div class="p-4 p-4"></div>'
    css = tw.generate(html)
    # Should generate only once
    assert css.count(".p-4") == 1

def test_class_with_newline(tw):
    html = '<div class="p-4\nm-4"></div>'
    css = tw.generate(html)
    assert ".p-4" in css
    assert ".m-4" in css

def test_variants_with_opacity(tw):
    # hover:bg-red-500/50
    html = '<div class="hover:bg-red-500/50"></div>'
    css = tw.generate(html)
    # Selector: .hover\:bg-red-500\/50:hover
    assert ".hover\\:bg-red-500\\/50:hover" in css
    # RGBA check
    assert "rgba(239, 68, 68, 0.5)" in css

def test_no_classes_found(tw):
    html = '<div></div>'
    css = tw.generate(html)
    assert css == ""

def test_hex_shorthand_opacity(tw):
    # #f00 -> #ff0000. Opacity 50% -> 0.5.
    html = '<div class="bg-[#f00]/50"></div>'
    css = tw.generate(html)
    assert "rgba(255, 0, 0, 0.5)" in css

def test_border_x_0(tw):
    # border-x-0 maps to border-left-width and border-right-width
    html = '<div class="border-x-0"></div>'
    css = tw.generate(html)
    # New generator uses proper spacing in CSS
    assert "border-left-width: 0px" in css
    assert "border-right-width: 0px" in css

def test_media_query_max(tw):
    html = '<div class="max-sm:hidden"></div>'
    css = tw.generate(html)
    assert "@media (max-width: 640px)" in css
    assert "display: none;" in css

def test_margin_utilities(tw):
    """Test all margin utility variants work correctly."""
    html = '<div class="m-4 mt-2 mb-2 ml-2 mr-2 mx-4 my-4 -mt-4"></div>'
    css = tw.generate(html)
    assert ".m-4" in css
    assert ".mt-2" in css
    assert ".ml-2" in css
    assert ".mx-4" in css
    assert ".my-4" in css
    assert ".-mt-4" in css
    assert "margin-top: -1rem" in css

def test_padding_utilities(tw):
    """Test all padding utility variants work correctly."""
    html = '<div class="p-4 pt-2 pb-2 pl-2 pr-2 px-4 py-4"></div>'
    css = tw.generate(html)
    assert ".p-4" in css
    assert ".pt-2" in css
    assert ".px-4" in css
    assert ".py-4" in css

def test_width_height_utilities(tw):
    """Test width and height utilities."""
    html = '<div class="w-full h-screen w-1/2 h-auto"></div>'
    css = tw.generate(html)
    assert "width: 100%;" in css
    assert "height: 100vh;" in css
    assert "width: 50%;" in css
    assert "height: auto;" in css

def test_parser_integration(tw):
    """Test parser is accessible and works correctly."""
    token = tw.parse_class("hover:md:bg-red-500/50")
    assert token.variants == ["hover", "md"]
    assert token.utility == "bg"
    assert token.value == "red-500"
    assert token.opacity == 50

def test_flexbox_utilities(tw):
    """Test flexbox utilities work correctly."""
    html = '<div class="flex flex-col items-center justify-between gap-4"></div>'
    css = tw.generate(html)
    assert "display: flex" in css
    assert "flex-direction: column" in css
    assert "align-items: center" in css
    assert "justify-content: space-between" in css
    assert "gap: 1rem" in css

def test_negative_margin(tw):
    """Test negative margin utilities."""
    html = '<div class="-m-4 -mt-2 -mx-4"></div>'
    css = tw.generate(html)
    assert "margin: -1rem" in css
    assert "margin-top: -0.5rem" in css
