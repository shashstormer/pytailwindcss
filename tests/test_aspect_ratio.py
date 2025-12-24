"""
Tests for aspect-ratio utilities.
"""

import pytest
from pytailwind import Tailwind


@pytest.fixture
def tw():
    return Tailwind(include_preflight=False)


class TestAspectRatioUtils:
    """Test aspect-ratio utilities."""
    
    def test_aspect_auto(self, tw):
        """Test aspect-auto utility."""
        css = tw.generate('<div class="aspect-auto"></div>')
        assert "aspect-ratio: auto" in css
    
    def test_aspect_square(self, tw):
        """Test aspect-square utility."""
        css = tw.generate('<div class="aspect-square"></div>')
        assert "aspect-ratio: 1 / 1" in css
    
    def test_aspect_video(self, tw):
        """Test aspect-video utility."""
        css = tw.generate('<div class="aspect-video"></div>')
        assert "aspect-ratio: 16 / 9" in css
    
    def test_numeric_ratio_3_2(self, tw):
        """Test aspect-3/2 utility."""
        css = tw.generate('<div class="aspect-3/2"></div>')
        assert "aspect-ratio: 3/2" in css
    
    def test_numeric_ratio_4_3(self, tw):
        """Test aspect-4/3 utility."""
        css = tw.generate('<div class="aspect-4/3"></div>')
        assert "aspect-ratio: 4/3" in css
        
    def test_numeric_decimal_ratio(self, tw):
        """Test aspect-ratio with decimals."""
        css = tw.generate('<div class="aspect-1.5/1"></div>')
        assert "aspect-ratio: 1.5/1" in css
    
    def test_arbitrary_value(self, tw):
        """Test aspect-[value] utility."""
        css = tw.generate('<div class="aspect-[4/3]"></div>')
        assert "aspect-ratio: 4/3" in css
    
    def test_arbitrary_calc(self, tw):
        """Test aspect-[calc(...)] utility."""
        css = tw.generate('<div class="aspect-[calc(4*3+1)/3]"></div>')
        assert "aspect-ratio: calc(4*3+1)/3" in css
    
    def test_css_variable_shorthand(self, tw):
        """Test aspect-(--var) shorthand syntax."""
        css = tw.generate('<div class="aspect-(--my-aspect-ratio)"></div>')
        assert "aspect-ratio: var(--my-aspect-ratio)" in css
    
    def test_responsive_aspect_ratio(self, tw):
        """Test responsive aspect-ratio utilities."""
        css = tw.generate('<div class="md:aspect-square"></div>')
        assert "@media" in css
        assert "aspect-ratio: 1 / 1" in css
    
    def test_invalid_ratio_ignored(self, tw):
        """Test invalid ratio format is ignored."""
        css = tw.generate('<div class="aspect-invalid"></div>')
        assert "aspect-ratio" not in css
