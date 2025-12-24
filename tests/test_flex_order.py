"""
Tests for refined Flexbox & Order utilities.
Checks flex numeric/fraction/var, grow/shrink numeric/var, basis scale/var, order var.
"""

import pytest
from pytailwind import Tailwind

@pytest.fixture
def tw():
    return Tailwind(include_preflight=False)

class TestFlexRefinements:
    def test_flex_numeric(self, tw):
        # flex-1 is standard static, check flex-2
        css = tw.generate('<div class="flex-2"></div>')
        assert "flex: 2" in css

    def test_flex_fraction(self, tw):
        # flex-1/2 -> flex: 50%
        css = tw.generate('<div class="flex-1/2"></div>')
        assert "flex: 50%" in css
        
        # flex-1/3 -> flex: 33.3333%
        css_third = tw.generate('<div class="flex-1/3"></div>')
        # Check roughly correct value
        assert "flex: 33.3333" in css_third
        assert "%" in css_third

    def test_flex_var(self, tw):
        css = tw.generate('<div class="flex-(--my-flex)"></div>')
        assert "flex: var(--my-flex)" in css

    def test_grow_numeric(self, tw):
        css = tw.generate('<div class="grow-2"></div>')
        assert "flex-grow: 2" in css
    
    def test_grow_var(self, tw):
        css = tw.generate('<div class="grow-(--g)"></div>')
        assert "flex-grow: var(--g)" in css

    def test_shrink_numeric(self, tw):
        css = tw.generate('<div class="shrink-3"></div>')
        assert "flex-shrink: 3" in css

    def test_shrink_var(self, tw):
        css = tw.generate('<div class="shrink-(--s)"></div>')
        assert "flex-shrink: var(--s)" in css

    def test_basis_scale(self, tw):
        # basis-3xs -> 16rem
        css = tw.generate('<div class="basis-3xs"></div>')
        assert "flex-basis: var(--container-3xs, 16rem)" in css
        
        # basis-7xl -> 80rem
        css = tw.generate('<div class="basis-7xl"></div>')
        assert "flex-basis: var(--container-7xl, 80rem)" in css

    def test_basis_var(self, tw):
        css = tw.generate('<div class="basis-(--b)"></div>')
        assert "flex-basis: var(--b)" in css

    def test_order_var(self, tw):
        css = tw.generate('<div class="order-(--o)"></div>')
        assert "order: var(--o)" in css
