"""
Tests for layout break and box sizing utilities.
"""

import pytest
from pytailwind import Tailwind


@pytest.fixture
def tw():
    return Tailwind(include_preflight=False)


class TestLayoutBreaks:
    """Test break-after, break-before, break-inside utilities."""
    
    def test_break_after(self, tw):
        """Test break-after-* utilities."""
        css = tw.generate('<div class="break-after-column"></div>')
        assert "break-after: column" in css
        
        css = tw.generate('<div class="break-after-avoid-page"></div>')
        assert "break-after: avoid-page" in css
    
    def test_break_before(self, tw):
        """Test break-before-* utilities."""
        css = tw.generate('<div class="break-before-column"></div>')
        assert "break-before: column" in css
        
        css = tw.generate('<div class="break-before-auto"></div>')
        assert "break-before: auto" in css
    
    def test_break_inside(self, tw):
        """Test break-inside-* utilities."""
        css = tw.generate('<div class="break-inside-avoid-column"></div>')
        assert "break-inside: avoid-column" in css
        
        css = tw.generate('<div class="break-inside-avoid"></div>')
        assert "break-inside: avoid" in css


class TestBoxUtilities:
    """Test box-decoration-break and box-sizing utilities."""
    
    def test_box_decoration(self, tw):
        """Test box-decoration-* utilities."""
        css = tw.generate('<div class="box-decoration-clone"></div>')
        assert "box-decoration-break: clone" in css
        
        css = tw.generate('<div class="box-decoration-slice"></div>')
        assert "box-decoration-break: slice" in css
    
    def test_box_sizing(self, tw):
        """Test box-* sizing utilities."""
        css = tw.generate('<div class="box-border"></div>')
        assert "box-sizing: border-box" in css
        
        css = tw.generate('<div class="box-content"></div>')
        assert "box-sizing: content-box" in css
    
    def test_responsive(self, tw):
        """Test variant application."""
        css = tw.generate('<div class="md:box-border lg:break-after-page"></div>')
        assert "@media" in css
        assert "box-sizing: border-box" in css
        assert "break-after: page" in css
