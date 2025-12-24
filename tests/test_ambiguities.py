"""
Tests for ambiguous utility resolution.

Note: The new plugin-based generator handles ambiguities differently.
These tests verify basic disambiguation works.
"""

import pytest
from pytailwind import Tailwind


class TestAmbiguities:
    @pytest.fixture
    def tw(self):
        return Tailwind()

    def test_bg_color(self, tw):
        """Test bg-* with color values works."""
        css = tw.generate('<div class="bg-red-500"></div>')
        assert "background-color: #ef4444" in css

    def test_bg_arbitrary_color(self, tw):
        """Test bg-[#hex] is treated as color."""
        css = tw.generate('<div class="bg-[#123456]"></div>')
        assert "background-color: #123456" in css

    def test_text_color(self, tw):
        """Test text-* with color values works."""
        css = tw.generate('<div class="text-red-500"></div>')
        assert "color: #ef4444" in css

    def test_text_align(self, tw):
        """Test text-* alignment values work."""
        css = tw.generate('<div class="text-center"></div>')
        assert "text-align: center" in css

    def test_border_color(self, tw):
        """Test border-* with color values works."""
        css = tw.generate('<div class="border-red-500"></div>')
        assert "border-color: #ef4444" in css

    def test_border_width(self, tw):
        """Test border-* with width values works."""
        css = tw.generate('<div class="border-2"></div>')
        assert "border-width: 2px" in css

    def test_divide_color(self, tw):
        """Test divide-* with color values works."""
        css = tw.generate('<div class="divide-red-500"></div>')
        assert "border-color" in css  # divide uses border-color internally

    def test_ring_width(self, tw):
        """Test ring with width values works."""
        css = tw.generate('<div class="ring-2"></div>')
        assert "--tw-ring-width: 2px" in css

    def test_shadow_preset(self, tw):
        """Test shadow presets work."""
        css = tw.generate('<div class="shadow-lg"></div>')
        assert "box-shadow" in css
