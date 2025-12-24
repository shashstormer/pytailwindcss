"""
Tests for Tailwind v4 theme variables.

Tests organized by theme variable namespace:
- Fonts (--font-*)
- Text sizes (--text-*)
- Font weights (--font-weight-*)
- Letter spacing/tracking (--tracking-*)
- Line height/leading (--leading-*)
- Border radius (--radius-*)
- Shadows (--shadow-*)
- Blur (--blur-*)
- Animations (--animate-*)
- Easing (--ease-*)
"""

import pytest
from pytailwind import Tailwind
from pytailwind.defaults import (
    FONTS, TEXT_SIZES, FONT_WEIGHTS, TRACKING, LEADING,
    RADIUS, SHADOWS, BLUR, EASING, ANIMATIONS
)


@pytest.fixture
def tw():
    return Tailwind()


# ============================================================================
# FONT FAMILY TESTS (--font-*)
# ============================================================================

class TestFontFamilyDefaults:
    """Test that font family defaults are defined correctly."""
    
    def test_fonts_dict_has_expected_keys(self):
        assert 'sans' in FONTS
        assert 'serif' in FONTS
        assert 'mono' in FONTS
    
    def test_font_sans_value(self):
        assert 'ui-sans-serif' in FONTS['sans']
        assert 'system-ui' in FONTS['sans']
    
    def test_font_serif_value(self):
        assert 'ui-serif' in FONTS['serif']
        assert 'Georgia' in FONTS['serif']
    
    def test_font_mono_value(self):
        assert 'ui-monospace' in FONTS['mono']
        assert 'Menlo' in FONTS['mono']


# ============================================================================
# TEXT SIZE TESTS (--text-*)
# ============================================================================

class TestTextSizeDefaults:
    """Test text size defaults."""
    
    @pytest.mark.parametrize("size", [
        'xs', 'sm', 'base', 'lg', 'xl',
        '2xl', '3xl', '4xl', '5xl', '6xl', '7xl', '8xl', '9xl'
    ])
    def test_text_size_exists(self, size):
        assert size in TEXT_SIZES
    
    def test_text_sizes_have_font_and_line_height(self):
        for size, value in TEXT_SIZES.items():
            assert isinstance(value, tuple)
            assert len(value) == 2  # (font-size, line-height)
    
    def test_text_xs_value(self):
        assert TEXT_SIZES['xs'] == ('0.75rem', '1rem')
    
    def test_text_base_value(self):
        assert TEXT_SIZES['base'] == ('1rem', '1.5rem')


# ============================================================================
# FONT WEIGHT TESTS (--font-weight-*)
# ============================================================================

class TestFontWeightDefaults:
    """Test font weight defaults."""
    
    @pytest.mark.parametrize("weight,expected", [
        ('thin', '100'),
        ('extralight', '200'),
        ('light', '300'),
        ('normal', '400'),
        ('medium', '500'),
        ('semibold', '600'),
        ('bold', '700'),
        ('extrabold', '800'),
        ('black', '900'),
    ])
    def test_font_weight_value(self, weight, expected):
        assert FONT_WEIGHTS[weight] == expected


# ============================================================================
# LETTER SPACING / TRACKING TESTS (--tracking-*)
# ============================================================================

class TestTrackingDefaults:
    """Test letter spacing / tracking defaults."""
    
    @pytest.mark.parametrize("tracking", [
        'tighter', 'tight', 'normal', 'wide', 'wider', 'widest'
    ])
    def test_tracking_exists(self, tracking):
        assert tracking in TRACKING
    
    def test_tracking_tighter_is_negative(self):
        assert TRACKING['tighter'].startswith('-')
    
    def test_tracking_wide_is_positive(self):
        assert not TRACKING['wide'].startswith('-')


# ============================================================================
# LINE HEIGHT / LEADING TESTS (--leading-*)
# ============================================================================

class TestLeadingDefaults:
    """Test line height / leading defaults."""
    
    @pytest.mark.parametrize("leading", [
        'none', 'tight', 'snug', 'normal', 'relaxed', 'loose'
    ])
    def test_named_leading_exists(self, leading):
        assert leading in LEADING
    
    @pytest.mark.parametrize("size", ['3', '4', '5', '6', '7', '8', '9', '10'])
    def test_numeric_leading_exists(self, size):
        assert size in LEADING
    
    def test_leading_none_value(self):
        assert LEADING['none'] == '1'
    
    def test_leading_normal_value(self):
        assert LEADING['normal'] == '1.5'


# ============================================================================
# BORDER RADIUS TESTS (--radius-*)
# ============================================================================

class TestRadiusDefaults:
    """Test border radius defaults."""
    
    @pytest.mark.parametrize("radius", [
        'none', 'xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl', '4xl', 'full'
    ])
    def test_radius_exists(self, radius):
        assert radius in RADIUS
    
    def test_radius_none_is_zero(self):
        assert RADIUS['none'] == '0px'
    
    def test_radius_full_is_max(self):
        assert RADIUS['full'] == '9999px'


# ============================================================================
# SHADOW TESTS (--shadow-*)
# ============================================================================

class TestShadowDefaults:
    """Test box shadow defaults."""
    
    @pytest.mark.parametrize("shadow", [
        '2xs', 'xs', 'sm', 'md', 'lg', 'xl', '2xl', 'inner', 'none'
    ])
    def test_shadow_exists(self, shadow):
        assert shadow in SHADOWS
    
    def test_shadow_none_value(self):
        assert SHADOWS['none'] == 'none'
    
    def test_shadow_inner_is_inset(self):
        assert 'inset' in SHADOWS['inner']


# ============================================================================
# BLUR TESTS (--blur-*)
# ============================================================================

class TestBlurDefaults:
    """Test blur filter defaults."""
    
    @pytest.mark.parametrize("blur", [
        'none', 'xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl'
    ])
    def test_blur_exists(self, blur):
        assert blur in BLUR
    
    def test_blur_none_is_zero(self):
        assert BLUR['none'] == '0'


# ============================================================================
# EASING TESTS (--ease-*)
# ============================================================================

class TestEasingDefaults:
    """Test transition timing function defaults."""
    
    @pytest.mark.parametrize("ease", ['linear', 'in', 'out', 'in-out'])
    def test_easing_exists(self, ease):
        assert ease in EASING
    
    def test_ease_linear_value(self):
        assert EASING['linear'] == 'linear'
    
    def test_ease_in_out_is_cubic_bezier(self):
        assert 'cubic-bezier' in EASING['in-out']


# ============================================================================
# ANIMATION TESTS (--animate-*)
# ============================================================================

class TestAnimationDefaults:
    """Test animation defaults."""
    
    @pytest.mark.parametrize("animation", ['none', 'spin', 'ping', 'pulse', 'bounce'])
    def test_animation_exists(self, animation):
        assert animation in ANIMATIONS
    
    def test_animation_none_value(self):
        assert ANIMATIONS['none'] == 'none'
    
    def test_animation_spin_value(self):
        assert 'spin' in ANIMATIONS['spin']
        assert 'infinite' in ANIMATIONS['spin']
