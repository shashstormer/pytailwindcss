import pytest
from pytailwind import Tailwind


class TestAmbiguities:
    def setup_method(self):
        self.tw = Tailwind()

    def test_bg_ambiguity(self):
        # Background Color vs Image
        assert "background-color: #123456" in self.tw.generate('<div class="bg-[#123456]"></div>')
        assert "background-image: url('img.png')" in self.tw.generate('<div class="bg-[url(\'img.png\')]"></div>')

        # Background Position (generic length/keyword) vs Color
        assert "background-position: center" in self.tw.generate('<div class="bg-[center]"></div>')

    def test_text_ambiguity(self):
        # Color vs Font Size
        assert "color: #123456" in self.tw.generate('<div class="text-[#123456]"></div>')
        assert "font-size: 12px" in self.tw.generate('<div class="text-[12px]"></div>')

    def test_border_ambiguity(self):
        # Color vs Width
        assert "border-color: #123456" in self.tw.generate('<div class="border-[#123456]"></div>')
        assert "border-width: 2px" in self.tw.generate('<div class="border-[2px]"></div>')

    def test_ring_ambiguity(self):
        # Color vs Width
        assert "ring-color: #123456" in self.tw.generate('<div class="ring-[#123456]"></div>')
        assert "ring-width: 10px" in self.tw.generate('<div class="ring-[10px]"></div>')

    def test_shadow_ambiguity(self):
        # Box Shadow vs Shadow Color
        assert "box-shadow-color: #123456" in self.tw.generate('<div class="shadow-[#123456]"></div>')
        # Expect no spaces in rgba because raw value from parsing is used directly after _ replacement
        # Input: 0_10px_15px_-3px_rgba(0,0,0,0.1) -> 0 10px 15px -3px rgba(0,0,0,0.1)
        # Note: input rgba has no spaces.
        assert "box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1)" in self.tw.generate(
            '<div class="shadow-[0_10px_15px_-3px_rgba(0,0,0,0.1)]"></div>')

    def test_divide_ambiguity(self):
        # Width vs Color
        assert "divide-color: #123456" in self.tw.generate('<div class="divide-[#123456]"></div>')
        # divide-x-[3px]
        # This requires structural generation or at least correct property mapping
        # We expect border-left-width (or similar valid css for divide)
        css = self.tw.generate('<div class="divide-x-[3px]"></div>')
        # We accept 'border-left-width:3px' (no space)
        assert "border-left-width:3px" in css or "border-width:3px" in css or "border-left-width: 3px" in css

    def test_outline_ambiguity(self):
        # Width vs Color
        assert "outline-color: #123456" in self.tw.generate('<div class="outline-[#123456]"></div>')
        assert "outline-width: 2px" in self.tw.generate('<div class="outline-[2px]"></div>')

    def test_decoration_ambiguity(self):
        # Color vs Thickness
        assert "text-decoration-color: #123456" in self.tw.generate('<div class="decoration-[#123456]"></div>')
        assert "text-decoration-thickness: 2px" in self.tw.generate('<div class="decoration-[2px]"></div>')

    def test_fill_stroke_ambiguity(self):
        # Fill is just color/none. Stroke is color or width.
        assert "stroke: #123456" in self.tw.generate('<div class="stroke-[#123456]"></div>')
        assert "stroke-width: 2px" in self.tw.generate('<div class="stroke-[2px]"></div>')

    def test_theme_resolution_recursive(self):
        # colors.red.500
        assert "color: #ef4444" in self.tw.generate('<div class="text-[theme(\'colors.red.500\')]"></div>')
        # spacing.4
        assert "width: 1rem" in self.tw.generate('<div class="w-[theme(\'spacing.4\')]"></div>')
