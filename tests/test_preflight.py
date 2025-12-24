"""
Tests for Preflight base styles.

Preflight is a set of base styles built on top of modern-normalize that
smooths over cross-browser inconsistencies.

Tests organized by feature:
- Preflight CSS content verification
- Include/exclude preflight in generation
- @layer base support
"""

import pytest
from pytailwind import Tailwind
from pytailwind.preflight import get_preflight, get_preflight_layered, PREFLIGHT_CSS


# ============================================================================
# PREFLIGHT CSS CONTENT TESTS
# ============================================================================

class TestPreflightCSSContent:
    """Test that Preflight CSS contains expected rules."""
    
    def test_preflight_contains_box_sizing(self):
        """Test box-sizing reset is present."""
        css = get_preflight()
        assert "box-sizing: border-box" in css
    
    def test_preflight_contains_margin_reset(self):
        """Test margin reset is present."""
        css = get_preflight()
        assert "margin: 0" in css
    
    def test_preflight_contains_padding_reset(self):
        """Test padding reset is present."""
        css = get_preflight()
        assert "padding: 0" in css
    
    def test_preflight_contains_border_reset(self):
        """Test border reset is present."""
        css = get_preflight()
        assert "border: 0 solid" in css
    
    def test_preflight_contains_heading_reset(self):
        """Test headings are unstyled."""
        css = get_preflight()
        assert "h1," in css
        assert "h6 {" in css
        assert "font-size: inherit" in css
        assert "font-weight: inherit" in css
    
    def test_preflight_contains_list_reset(self):
        """Test lists are unstyled."""
        css = get_preflight()
        assert "ol," in css
        assert "ul," in css
        assert "list-style: none" in css
    
    def test_preflight_contains_replaced_elements_block(self):
        """Test replaced elements are block-level."""
        css = get_preflight()
        assert "img," in css
        assert "svg," in css
        assert "video," in css
        assert "display: block" in css
        assert "vertical-align: middle" in css
    
    def test_preflight_contains_image_constraints(self):
        """Test images are constrained."""
        css = get_preflight()
        assert "max-width: 100%" in css
        assert "height: auto" in css
    
    def test_preflight_contains_hidden_attribute(self):
        """Test hidden attribute enforcement."""
        css = get_preflight()
        assert "[hidden]" in css
        assert "display: none !important" in css


# ============================================================================
# PREFLIGHT MODULE FUNCTIONS TESTS
# ============================================================================

class TestPreflightModuleFunctions:
    """Test preflight module functions."""
    
    def test_get_preflight_returns_string(self):
        """Test get_preflight returns a string."""
        css = get_preflight()
        assert isinstance(css, str)
        assert len(css) > 0
    
    def test_preflight_css_constant_matches_function(self):
        """Test PREFLIGHT_CSS constant matches get_preflight() function."""
        assert PREFLIGHT_CSS == get_preflight()
    
    def test_get_preflight_layered_wraps_in_layer(self):
        """Test get_preflight_layered wraps CSS in @layer base."""
        css = get_preflight_layered()
        assert "@layer base {" in css
        assert "box-sizing: border-box" in css
    
    def test_get_preflight_layered_ends_with_closing_brace(self):
        """Test layered CSS has proper closing brace."""
        css = get_preflight_layered()
        assert css.strip().endswith("}")


# ============================================================================
# TAILWIND CLASS PREFLIGHT INTEGRATION TESTS
# ============================================================================

class TestTailwindPreflightIntegration:
    """Test Preflight integration with Tailwind class."""
    
    def test_tailwind_includes_preflight_by_default(self):
        """Test Tailwind includes Preflight by default."""
        tw = Tailwind()
        assert tw.include_preflight is True
    
    def test_tailwind_can_disable_preflight(self):
        """Test Tailwind can be initialized without Preflight."""
        tw = Tailwind(include_preflight=False)
        assert tw.include_preflight is False
    
    def test_generate_includes_preflight_by_default(self):
        """Test generate() includes Preflight CSS by default."""
        tw = Tailwind()
        css = tw.generate('<div class="p-4"></div>')
        assert "box-sizing: border-box" in css
        assert ".p-4" in css
    
    def test_generate_excludes_preflight_when_disabled(self):
        """Test generate() excludes Preflight when disabled at init."""
        tw = Tailwind(include_preflight=False)
        css = tw.generate('<div class="p-4"></div>')
        assert "box-sizing: border-box" not in css
        assert ".p-4" in css
    
    def test_generate_can_override_preflight_setting(self):
        """Test generate() can override include_preflight setting."""
        # Default includes preflight, override to exclude
        tw = Tailwind(include_preflight=True)
        css = tw.generate('<div class="p-4"></div>', include_preflight=False)
        assert "box-sizing: border-box" not in css
        assert ".p-4" in css
        
        # Default excludes preflight, override to include
        tw = Tailwind(include_preflight=False)
        css = tw.generate('<div class="p-4"></div>', include_preflight=True)
        assert "box-sizing: border-box" in css
        assert ".p-4" in css
    
    def test_generate_empty_content_returns_preflight_only(self):
        """Test generate() with empty content returns only Preflight."""
        tw = Tailwind(include_preflight=True)
        css = tw.generate('<div></div>')
        # Should return preflight even with no utility classes
        assert "box-sizing: border-box" in css
    
    def test_generate_empty_content_without_preflight(self):
        """Test generate() with empty content and no preflight returns empty."""
        tw = Tailwind(include_preflight=False)
        css = tw.generate('<div></div>')
        assert css == ""
    
    def test_get_preflight_method(self):
        """Test Tailwind.get_preflight() method."""
        tw = Tailwind()
        css = tw.get_preflight()
        assert "box-sizing: border-box" in css
        assert "@layer base" not in css
    
    def test_get_preflight_method_layered(self):
        """Test Tailwind.get_preflight(layered=True) method."""
        tw = Tailwind()
        css = tw.get_preflight(layered=True)
        assert "@layer base {" in css
        assert "box-sizing: border-box" in css


# ============================================================================
# PREFLIGHT WITH VARIANTS AND UTILITIES TESTS
# ============================================================================

class TestPreflightWithUtilities:
    """Test Preflight works correctly with utilities."""
    
    def test_preflight_before_utilities(self):
        """Test Preflight CSS appears before utility CSS."""
        tw = Tailwind()
        css = tw.generate('<div class="p-4 text-red-500"></div>')
        
        # Find positions
        preflight_pos = css.find("box-sizing: border-box")
        utility_pos = css.find(".p-4")
        
        assert preflight_pos < utility_pos, "Preflight should come before utilities"
    
    def test_preflight_with_hover_variant(self):
        """Test Preflight works with hover variants."""
        tw = Tailwind()
        css = tw.generate('<div class="hover:bg-red-500"></div>')
        assert "box-sizing: border-box" in css
        assert ":hover" in css
    
    def test_preflight_with_media_query_variant(self):
        """Test Preflight works with media query variants."""
        tw = Tailwind()
        css = tw.generate('<div class="md:text-center"></div>')
        assert "box-sizing: border-box" in css
        assert "@media" in css
