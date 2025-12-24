"""
Tests for columns utilities.
"""

import pytest
from pytailwind import Tailwind


@pytest.fixture
def tw():
    return Tailwind(include_preflight=False)


class TestColumnsUtils:
    """Test columns utilities."""
    
    def test_columns_number(self, tw):
        """Test columns-<number> utility."""
        css = tw.generate('<div class="columns-3"></div>')
        assert "columns: 3" in css
    
    def test_columns_auto(self, tw):
        """Test columns-auto utility."""
        css = tw.generate('<div class="columns-auto"></div>')
        assert "columns: auto" in css
    
    def test_columns_width_3xs(self, tw):
        """Test columns-3xs utility with var fallback."""
        css = tw.generate('<div class="columns-3xs"></div>')
        assert "columns: var(--container-3xs, 16rem)" in css
        
    def test_columns_width_md(self, tw):
        """Test columns-md utility with var fallback."""
        css = tw.generate('<div class="columns-md"></div>')
        assert "columns: var(--container-md, 28rem)" in css
    
    def test_arbitrary_value(self, tw):
        """Test columns-[value] utility."""
        css = tw.generate('<div class="columns-[30vw]"></div>')
        assert "columns: 30vw" in css
    
    def test_css_variable_shorthand(self, tw):
        """Test columns-(--var) shorthand syntax."""
        css = tw.generate('<div class="columns-(--my-columns)"></div>')
        assert "columns: var(--my-columns)" in css
    
    def test_responsive_columns(self, tw):
        """Test responsive columns utilities."""
        css = tw.generate('<div class="sm:columns-3"></div>')
        assert "@media" in css
        assert "columns: 3" in css
