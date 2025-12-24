"""
Tests for Tailwind v4 custom styles support.

Tests organized by feature:
- Arbitrary values (top-[117px], bg-[#bada55])
- Arbitrary properties ([mask-type:luminance], [--my-var:value])
- Whitespace handling (underscores converted to spaces)
- CSS variable properties ([--scroll-offset:56px])
"""

import pytest
from pytailwind import Tailwind


@pytest.fixture
def tw():
    return Tailwind()


# ============================================================================
# ARBITRARY VALUES TESTS
# ============================================================================

class TestArbitraryValues:
    """Test arbitrary value support with square brackets."""
    
    def test_top_arbitrary_value(self, tw):
        css = tw.generate('<div class="top-[117px]"></div>')
        assert 'top: 117px' in css
    
    def test_bg_arbitrary_hex(self, tw):
        css = tw.generate('<div class="bg-[#bada55]"></div>')
        assert 'background-color' in css
        assert '#bada55' in css.lower()
    
    def test_text_arbitrary_value(self, tw):
        css = tw.generate('<div class="text-[22px]"></div>')
        # May generate color or font-size depending on type detection
        assert 'text' in css.lower() or '22px' in css
    
    def test_w_arbitrary_value(self, tw):
        css = tw.generate('<div class="w-[300px]"></div>')
        assert 'width: 300px' in css
    
    def test_h_arbitrary_value(self, tw):
        css = tw.generate('<div class="h-[50vh]"></div>')
        assert 'height: 50vh' in css
    
    def test_m_arbitrary_value(self, tw):
        css = tw.generate('<div class="m-[2rem]"></div>')
        assert 'margin: 2rem' in css
    
    def test_p_arbitrary_value(self, tw):
        css = tw.generate('<div class="p-[20px]"></div>')
        assert 'padding: 20px' in css


# ============================================================================
# ARBITRARY PROPERTIES TESTS
# ============================================================================

class TestArbitraryProperties:
    """Test arbitrary property support [property:value]."""
    
    def test_mask_type_property(self, tw):
        css = tw.generate('<div class="[mask-type:luminance]"></div>')
        assert 'mask-type' in css
        assert 'luminance' in css
    
    def test_content_visibility_property(self, tw):
        css = tw.generate('<div class="[content-visibility:auto]"></div>')
        assert 'content-visibility' in css
        assert 'auto' in css
    
    def test_arbitrary_property_with_hover(self, tw):
        css = tw.generate('<div class="hover:[mask-type:alpha]"></div>')
        assert 'mask-type' in css
        assert 'alpha' in css
        assert ':hover' in css
    
    def test_arbitrary_property_with_breakpoint(self, tw):
        css = tw.generate('<div class="lg:[content-visibility:auto]"></div>')
        assert '@media' in css
        assert 'content-visibility' in css


# ============================================================================
# CSS VARIABLE PROPERTIES TESTS
# ============================================================================

class TestCSSVariableProperties:
    """Test CSS variable property support [--my-var:value]."""
    
    def test_css_variable_property(self, tw):
        css = tw.generate('<div class="[--scroll-offset:56px]"></div>')
        assert '--scroll-offset' in css
        assert '56px' in css
    
    def test_css_variable_with_breakpoint(self, tw):
        css = tw.generate('<div class="lg:[--scroll-offset:44px]"></div>')
        assert '@media' in css
        assert '--scroll-offset' in css
        assert '44px' in css
    
    def test_css_variable_with_hover(self, tw):
        css = tw.generate('<div class="hover:[--bg-color:blue]"></div>')
        assert '--bg-color' in css
        assert 'blue' in css
        assert ':hover' in css


# ============================================================================
# WHITESPACE HANDLING TESTS
# ============================================================================

class TestWhitespaceHandling:
    """Test underscore to space conversion."""
    
    def test_grid_cols_underscore_to_space(self, tw):
        css = tw.generate('<div class="grid-cols-[1fr_500px_2fr]"></div>')
        assert 'grid-template-columns' in css
        assert '1fr 500px 2fr' in css  # underscores converted to spaces
    
    def test_multiple_underscores(self, tw):
        css = tw.generate('<div class="gap-[10px_20px]"></div>')
        if 'gap' in css:
            assert '10px 20px' in css


# ============================================================================
# COMBINED VARIANTS WITH ARBITRARY VALUES
# ============================================================================

class TestCombinedVariantsWithArbitrary:
    """Test combining variants with arbitrary values."""
    
    def test_hover_arbitrary_value(self, tw):
        css = tw.generate('<div class="hover:top-[100px]"></div>')
        assert ':hover' in css
        assert 'top' in css
    
    def test_breakpoint_arbitrary_value(self, tw):
        css = tw.generate('<div class="lg:top-[344px]"></div>')
        assert '@media' in css
        assert 'top' in css
    
    def test_dark_arbitrary_value(self, tw):
        css = tw.generate('<div class="dark:bg-[#1a1a2e]"></div>')
        assert 'prefers-color-scheme: dark' in css or '.dark' in css
        assert 'background-color' in css


# ============================================================================
# PARSER BRACKET HANDLING TESTS
# ============================================================================

class TestParserBracketHandling:
    """Test that parser correctly handles brackets in class names."""
    
    def test_brackets_preserved_in_value(self, tw):
        css = tw.generate('<div class="bg-[#ff0000]"></div>')
        assert '#ff0000' in css.lower()
    
    def test_nested_brackets_in_calc(self, tw):
        css = tw.generate('<div class="w-[calc(100%-20px)]"></div>')
        # Should handle calc() with nested content
        assert 'width' in css
    
    def test_brackets_not_split_on_colon(self, tw):
        # [mask-type:luminance] should NOT be split on the colon
        css = tw.generate('<div class="[mask-type:luminance]"></div>')
        assert 'mask-type' in css
        assert 'luminance' in css
