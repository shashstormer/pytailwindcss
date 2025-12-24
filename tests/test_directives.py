"""
Tests for Tailwind v4 functions and directives.

Tests organized by feature:
- @apply directive (apply() method)
- --spacing() function (spacing_value() method)
- theme() function (theme_value() method)
- process_css_with_apply() for processing CSS files
"""

import pytest
from pytailwind import Tailwind


@pytest.fixture
def tw():
    return Tailwind()


# ============================================================================
# @APPLY DIRECTIVE TESTS
# ============================================================================

class TestApplyDirective:
    """Test @apply directive functionality via apply() method."""
    
    def test_apply_single_class(self, tw):
        result = tw.apply('p-4')
        assert 'padding' in result
        assert '1rem' in result
    
    def test_apply_multiple_classes(self, tw):
        result = tw.apply('rounded-lg', 'shadow-md')
        assert 'border-radius' in result
        assert 'box-shadow' in result
    
    def test_apply_margin(self, tw):
        result = tw.apply('m-4')
        assert 'margin' in result
        assert '1rem' in result
    
    def test_apply_color_class(self, tw):
        result = tw.apply('bg-red-500')
        assert 'background-color' in result
        assert '#ef4444' in result
    
    def test_apply_text_class(self, tw):
        result = tw.apply('text-white')
        assert 'color' in result
        assert '#fff' in result
    
    def test_apply_flex(self, tw):
        result = tw.apply('flex')
        assert 'display' in result
        assert 'flex' in result
    
    def test_apply_items_center(self, tw):
        result = tw.apply('items-center')
        assert 'align-items' in result
        assert 'center' in result
    
    def test_apply_border_radius(self, tw):
        result = tw.apply('rounded-lg')
        assert 'border-radius' in result
        assert '0.5rem' in result
    
    def test_apply_empty_returns_empty(self, tw):
        result = tw.apply()
        assert result == ''
    
    def test_apply_unknown_class_returns_empty(self, tw):
        result = tw.apply('does-not-exist')
        assert result == ''


# ============================================================================
# SPACING FUNCTION TESTS
# ============================================================================

class TestSpacingFunction:
    """Test --spacing() function via spacing_value() method."""
    
    def test_spacing_4(self, tw):
        result = tw.spacing_value(4)
        assert 'calc(var(--spacing) * 4)' == result
    
    def test_spacing_1(self, tw):
        result = tw.spacing_value(1)
        assert 'calc(var(--spacing) * 1)' == result
    
    def test_spacing_decimal(self, tw):
        result = tw.spacing_value(0.5)
        assert 'calc(var(--spacing) * 0.5)' == result
    
    def test_spacing_large(self, tw):
        result = tw.spacing_value(96)
        assert 'calc(var(--spacing) * 96)' == result


# ============================================================================
# THEME FUNCTION TESTS
# ============================================================================

class TestThemeFunction:
    """Test theme() function via theme_value() method."""
    
    def test_theme_spacing(self, tw):
        result = tw.theme_value('spacing.4')
        assert result == '1rem'
    
    def test_theme_spacing_1(self, tw):
        result = tw.theme_value('spacing.1')
        assert result == '0.25rem'
    
    def test_theme_spacing_px(self, tw):
        result = tw.theme_value('spacing.px')
        assert result == '1px'
    
    def test_theme_color_red_500(self, tw):
        result = tw.theme_value('colors.red.500')
        assert result == '#ef4444'
    
    def test_theme_color_blue_300(self, tw):
        result = tw.theme_value('colors.blue.300')
        assert result == '#93c5fd'
    
    def test_theme_color_black(self, tw):
        result = tw.theme_value('colors.black')
        assert result == '#000'
    
    def test_theme_color_white(self, tw):
        result = tw.theme_value('colors.white')
        assert result == '#fff'
    
    def test_theme_invalid_path_returns_empty(self, tw):
        result = tw.theme_value('invalid.path')
        assert result == ''
    
    def test_theme_invalid_color_returns_empty(self, tw):
        result = tw.theme_value('colors.notacolor.500')
        assert result == ''


# ============================================================================
# PROCESS CSS WITH @APPLY TESTS
# ============================================================================

class TestProcessCssWithApply:
    """Test process_css_with_apply() for processing CSS files."""
    
    def test_simple_apply(self, tw):
        css = '.btn { @apply p-4; }'
        result = tw.process_css_with_apply(css)
        assert 'padding' in result
        assert '.btn' in result
        assert '@apply' not in result
    
    def test_multiple_classes_in_apply(self, tw):
        css = '.card { @apply p-4 m-2 rounded-lg; }'
        result = tw.process_css_with_apply(css)
        assert 'padding' in result
        assert 'margin' in result
        assert 'border-radius' in result
        assert '@apply' not in result
    
    def test_multiple_apply_directives(self, tw):
        css = '''
        .btn { @apply px-4 py-2; }
        .card { @apply p-6 shadow-lg; }
        '''
        result = tw.process_css_with_apply(css)
        assert '@apply' not in result
        assert '.btn' in result
        assert '.card' in result
    
    def test_apply_with_other_properties(self, tw):
        css = '''
        .custom {
            color: blue;
            @apply rounded-lg;
            font-size: 16px;
        }
        '''
        result = tw.process_css_with_apply(css)
        assert 'border-radius' in result
        assert 'color: blue' in result
        assert 'font-size: 16px' in result
    
    def test_no_apply_returns_unchanged(self, tw):
        css = '.simple { color: red; }'
        result = tw.process_css_with_apply(css)
        assert result == css


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestDirectivesIntegration:
    """Integration tests for directives and functions."""
    
    def test_apply_with_theme_colors(self, tw):
        """Test that apply uses theme colors correctly."""
        result = tw.apply('bg-blue-500', 'text-white')
        assert 'background-color' in result
        assert 'color' in result
    
    def test_theme_and_apply_consistent(self, tw):
        """Test that theme values match what apply uses."""
        theme_color = tw.theme_value('colors.red.500')
        apply_result = tw.apply('text-red-500')
        assert theme_color in apply_result
    
    def test_spacing_values_consistent(self, tw):
        """Test that spacing values are consistent."""
        theme_spacing = tw.theme_value('spacing.4')
        apply_result = tw.apply('p-4')
        assert theme_spacing in apply_result
