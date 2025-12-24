import pytest
from pytailwind import Tailwind

@pytest.fixture
def tw():
    return Tailwind()

class TestSizingVariables:
    def test_width_vars(self, tw):
        css = tw.generate('<div class="w-(--my-width)"></div>')
        assert "width: var(--my-width)" in css
    
    def test_height_vars(self, tw):
        css = tw.generate('<div class="h-(--my-height)"></div>')
        assert "height: var(--my-height)" in css
        
    def test_size_vars(self, tw):
        css = tw.generate('<div class="size-(--my-size)"></div>')
        assert "width: var(--my-size)" in css
        assert "height: var(--my-size)" in css

    def test_min_w_vars(self, tw):
        css = tw.generate('<div class="min-w-(--v)"></div>')
        assert "min-width: var(--v)" in css

    def test_max_w_vars(self, tw):
        css = tw.generate('<div class="max-w-(--v)"></div>')
        assert "max-width: var(--v)" in css
        
    def test_min_h_vars(self, tw):
        css = tw.generate('<div class="min-h-(--v)"></div>')
        assert "min-height: var(--v)" in css

    def test_max_h_vars(self, tw):
        css = tw.generate('<div class="max-h-(--v)"></div>')
        assert "max-height: var(--v)" in css

class TestContainerScales:
    def test_width_container(self, tw):
        css = tw.generate('<div class="w-3xs w-7xl"></div>')
        assert "width: var(--container-3xs, 16rem)" in css
        assert "width: var(--container-7xl, 80rem)" in css

    def test_min_w_container(self, tw):
        css = tw.generate('<div class="min-w-sm"></div>')
        assert "min-width: var(--container-sm, 24rem)" in css

    def test_max_w_container(self, tw):
        css = tw.generate('<div class="max-w-prose"></div>')
        assert "max-width: 65ch" in css
        
        css = tw.generate('<div class="max-w-screen-md"></div>')
        assert "max-width: 768px" in css

class TestViewportUnits:
    def test_width_viewport(self, tw):
        css = tw.generate('<div class="w-dvw w-svh"></div>')
        assert "width: 100dvw" in css
        assert "width: 100svh" in css

    def test_height_viewport(self, tw):
        css = tw.generate('<div class="h-lvh h-svw"></div>')
        assert "height: 100lvh" in css
        assert "height: 100svw" in css

    def test_size_viewport(self, tw):
        css = tw.generate('<div class="size-dvh"></div>')
        assert "width: 100dvh" in css
        assert "height: 100dvh" in css

class TestSizeUtility:
    def test_size_fraction(self, tw):
        css = tw.generate('<div class="size-1/2"></div>')
        assert "width: 50%" in css
        assert "height: 50%" in css

    def test_size_auto(self, tw):
        css = tw.generate('<div class="size-auto"></div>')
        assert "width: auto" in css
        assert "height: auto" in css

class TestMinMaxHeightLH:
    def test_min_h_lh(self, tw):
        css = tw.generate('<div class="min-h-lh"></div>')
        assert "min-height: 1lh" in css

    def test_max_h_lh(self, tw):
        css = tw.generate('<div class="max-h-lh"></div>')
        assert "max-height: 1lh" in css
