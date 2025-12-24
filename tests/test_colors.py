"""
Tests for Tailwind v4 color utilities.

Tests organized by color utility category:
- Background colors (bg-*)
- Text colors (text-*)
- Border colors (border-*)
- Fill colors (fill-*)
- Stroke colors (stroke-*)
- Opacity modifiers (/50, /75)
- Color palette coverage
"""

import pytest
from pytailwind import Tailwind
from pytailwind.defaults import COLORS


@pytest.fixture
def tw():
    return Tailwind()


# ============================================================================
# COLOR PALETTE TESTS
# ============================================================================

class TestColorPaletteDefaults:
    """Test that color palette defaults are defined correctly."""
    
    @pytest.mark.parametrize("color", [
        'slate', 'gray', 'zinc', 'neutral', 'stone',
        'red', 'orange', 'amber', 'yellow', 'lime',
        'green', 'emerald', 'teal', 'cyan', 'sky',
        'blue', 'indigo', 'violet', 'purple', 'fuchsia',
        'pink', 'rose'
    ])
    def test_color_palette_exists(self, color):
        assert color in COLORS
    
    @pytest.mark.parametrize("shade", [
        '50', '100', '200', '300', '400', '500',
        '600', '700', '800', '900', '950'
    ])
    def test_color_has_all_shades(self, shade):
        """Each color should have shades 50-950."""
        for color in ['red', 'blue', 'green', 'gray']:
            assert shade in COLORS[color]
    
    def test_special_colors_exist(self):
        assert 'black' in COLORS
        assert 'white' in COLORS
        assert 'transparent' in COLORS
        assert 'inherit' in COLORS
        assert 'current' in COLORS
    
    def test_black_value(self):
        assert COLORS['black'] == '#000'
    
    def test_white_value(self):
        assert COLORS['white'] == '#fff'


# ============================================================================
# BACKGROUND COLOR TESTS
# ============================================================================

class TestBackgroundColorUtilities:
    """Test background color utilities (bg-*)."""
    
    def test_bg_red_500(self, tw):
        css = tw.generate('<div class="bg-red-500"></div>')
        assert 'background-color' in css
        assert '#ef4444' in css
    
    def test_bg_blue_300(self, tw):
        css = tw.generate('<div class="bg-blue-300"></div>')
        assert 'background-color' in css
    
    def test_bg_black(self, tw):
        css = tw.generate('<div class="bg-black"></div>')
        assert 'background-color: #000' in css
    
    def test_bg_white(self, tw):
        css = tw.generate('<div class="bg-white"></div>')
        assert 'background-color: #fff' in css
    
    def test_bg_transparent(self, tw):
        css = tw.generate('<div class="bg-transparent"></div>')
        assert 'background-color: transparent' in css


# ============================================================================
# TEXT COLOR TESTS
# ============================================================================

class TestTextColorUtilities:
    """Test text color utilities (text-*)."""
    
    def test_text_red_500(self, tw):
        css = tw.generate('<div class="text-red-500"></div>')
        assert 'color' in css
        assert '#ef4444' in css
    
    def test_text_gray_900(self, tw):
        css = tw.generate('<div class="text-gray-900"></div>')
        assert 'color' in css
    
    def test_text_white(self, tw):
        css = tw.generate('<div class="text-white"></div>')
        assert 'color: #fff' in css
    
    def test_text_black(self, tw):
        css = tw.generate('<div class="text-black"></div>')
        assert 'color: #000' in css


# ============================================================================
# BORDER COLOR TESTS
# ============================================================================

class TestBorderColorUtilities:
    """Test border color utilities (border-*)."""
    
    def test_border_red_500(self, tw):
        css = tw.generate('<div class="border-red-500"></div>')
        assert 'border-color' in css
    
    def test_border_blue_300(self, tw):
        css = tw.generate('<div class="border-blue-300"></div>')
        assert 'border-color' in css
    
    def test_border_gray_200(self, tw):
        css = tw.generate('<div class="border-gray-200"></div>')
        assert 'border-color' in css


# ============================================================================
# FILL AND STROKE COLOR TESTS
# ============================================================================

class TestFillStrokeColorUtilities:
    """Test fill and stroke color utilities for SVGs."""
    
    def test_fill_green_500(self, tw):
        css = tw.generate('<svg class="fill-green-500"></svg>')
        assert 'fill:' in css or 'fill :' in css
    
    def test_stroke_pink_700(self, tw):
        css = tw.generate('<svg class="stroke-pink-700"></svg>')
        assert 'stroke:' in css or 'stroke :' in css
    
    def test_fill_current(self, tw):
        css = tw.generate('<svg class="fill-current"></svg>')
        assert 'fill' in css


# ============================================================================
# OPACITY MODIFIER TESTS
# ============================================================================

class TestColorOpacityModifiers:
    """Test color opacity modifiers (/50, /75, etc.)."""
    
    def test_bg_black_50(self, tw):
        css = tw.generate('<div class="bg-black/50"></div>')
        assert 'background-color' in css
        assert 'rgba' in css or '0.5' in css
    
    def test_text_white_75(self, tw):
        css = tw.generate('<div class="text-white/75"></div>')
        assert 'color' in css
        assert 'rgba' in css or '0.75' in css
    
    def test_bg_red_500_opacity_50(self, tw):
        css = tw.generate('<div class="bg-red-500/50"></div>')
        assert 'background-color' in css
    
    def test_bg_blue_500_opacity_100(self, tw):
        css = tw.generate('<div class="bg-blue-500/100"></div>')
        assert 'background-color' in css
    
    @pytest.mark.parametrize("opacity", [
        '0', '5', '10', '20', '25', '30', '40', '50',
        '60', '70', '75', '80', '90', '95', '100'
    ])
    def test_various_opacity_levels(self, tw, opacity):
        css = tw.generate(f'<div class="bg-black/{opacity}"></div>')
        assert 'background-color' in css


# ============================================================================
# DARK MODE COLOR TESTS
# ============================================================================

class TestDarkModeColors:
    """Test dark mode color utilities."""
    
    def test_dark_bg_gray_800(self, tw):
        css = tw.generate('<div class="dark:bg-gray-800"></div>')
        assert '@media (prefers-color-scheme: dark)' in css
        assert 'background-color' in css
    
    def test_dark_text_white(self, tw):
        css = tw.generate('<div class="dark:text-white"></div>')
        assert '@media (prefers-color-scheme: dark)' in css
        assert 'color' in css
    
    def test_combined_light_dark_bg(self, tw):
        css = tw.generate('<div class="bg-white dark:bg-gray-900"></div>')
        assert 'bg-white' in css or '#fff' in css
        assert '@media (prefers-color-scheme: dark)' in css


# ============================================================================
# HOVER STATE COLOR TESTS
# ============================================================================

class TestHoverStateColors:
    """Test hover state color utilities."""
    
    def test_hover_bg_blue_500(self, tw):
        css = tw.generate('<div class="hover:bg-blue-500"></div>')
        assert ':hover' in css
        assert 'background-color' in css
    
    def test_hover_text_red_500(self, tw):
        css = tw.generate('<div class="hover:text-red-500"></div>')
        assert ':hover' in css
        assert 'color' in css


# ============================================================================
# ARBITRARY COLOR VALUE TESTS
# ============================================================================

class TestArbitraryColorValues:
    """Test arbitrary color values in brackets."""
    
    def test_bg_arbitrary_hex(self, tw):
        css = tw.generate('<div class="bg-[#ff5500]"></div>')
        assert 'background-color' in css
        assert '#ff5500' in css.lower()
    
    def test_text_arbitrary_hex(self, tw):
        css = tw.generate('<div class="text-[#123456]"></div>')
        assert 'color' in css
        assert '#123456' in css.lower()
    
    def test_bg_arbitrary_rgb(self, tw):
        css = tw.generate('<div class="bg-[rgb(255,0,0)]"></div>')
        assert 'background-color' in css
