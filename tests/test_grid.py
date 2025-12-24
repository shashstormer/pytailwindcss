"""
Tests for Grid Layout utilities.
"""

import pytest
from pytailwind import Tailwind

@pytest.fixture
def tw():
    return Tailwind(include_preflight=False)

class TestGridTemplates:
    def test_grid_cols(self, tw):
        css = tw.generate('<div class="grid-cols-4"></div>')
        assert "grid-template-columns: repeat(4, minmax(0, 1fr))" in css
        
        css = tw.generate('<div class="grid-cols-none"></div>')
        assert "grid-template-columns: none" in css
        
        css = tw.generate('<div class="grid-cols-subgrid"></div>')
        assert "grid-template-columns: subgrid" in css
        
        css = tw.generate('<div class="grid-cols-(--my-cols)"></div>')
        assert "grid-template-columns: var(--my-cols)" in css
        
        css = tw.generate('<div class="grid-cols-[200px_minmax(900px,_1fr)_100px]"></div>')
        assert "grid-template-columns: 200px minmax(900px, 1fr) 100px" in css

    def test_grid_rows(self, tw):
        css = tw.generate('<div class="grid-rows-4"></div>')
        assert "grid-template-rows: repeat(4, minmax(0, 1fr))" in css
        
        css = tw.generate('<div class="grid-rows-subgrid"></div>')
        assert "grid-template-rows: subgrid" in css
        
        css = tw.generate('<div class="grid-rows-(--my-rows)"></div>')
        assert "grid-template-rows: var(--my-rows)" in css

class TestGridPlacement:
    def test_col_span(self, tw):
        css = tw.generate('<div class="col-span-2"></div>')
        assert "grid-column: span 2 / span 2" in css
        
        css = tw.generate('<div class="col-span-full"></div>')
        assert "grid-column: 1 / -1" in css
        
        css = tw.generate('<div class="col-span-(--span)"></div>')
        assert "grid-column: span var(--span) / span var(--span)" in css
    
    def test_col_start_end(self, tw):
        css = tw.generate('<div class="col-start-2"></div>')
        assert "grid-column-start: 2" in css
        
        css = tw.generate('<div class="col-end-3"></div>')
        assert "grid-column-end: 3" in css
        
        css = tw.generate('<div class="col-start-auto col-end-auto"></div>')
        assert "grid-column-start: auto" in css
        assert "grid-column-end: auto" in css
        
        css = tw.generate('<div class="-col-start-1"></div>')
        assert "grid-column-start: -1" in css

    def test_col_shorthand(self, tw):
        css = tw.generate('<div class="col-auto"></div>')
        assert "grid-column: auto" in css
        
        # col-<number> -> grid-column: <number> (not span)
        css = tw.generate('<div class="col-1"></div>')
        assert "grid-column: 1" in css
        
        css = tw.generate('<div class="col-(--c)"></div>')
        assert "grid-column: var(--c)" in css

    def test_row_placement(self, tw):
        css = tw.generate('<div class="row-span-3"></div>')
        assert "grid-row: span 3 / span 3" in css
        
        css = tw.generate('<div class="row-start-2 row-end-4"></div>')
        assert "grid-row-start: 2" in css
        assert "grid-row-end: 4" in css
        
        css = tw.generate('<div class="row-auto"></div>')
        assert "grid-row: auto" in css

class TestGridAuto:
    def test_grid_flow(self, tw):
        css = tw.generate('<div class="grid-flow-row"></div>')
        assert "grid-auto-flow: row" in css
        
        css = tw.generate('<div class="grid-flow-col-dense"></div>')
        assert "grid-auto-flow: column dense" in css

    def test_auto_cols(self, tw):
        css = tw.generate('<div class="auto-cols-min"></div>')
        assert "grid-auto-columns: min-content" in css
        
        css = tw.generate('<div class="auto-cols-fr"></div>')
        assert "grid-auto-columns: minmax(0, 1fr)" in css
        
        css = tw.generate('<div class="auto-cols-(--c)"></div>')
        assert "grid-auto-columns: var(--c)" in css

    def test_auto_rows(self, tw):
        css = tw.generate('<div class="auto-rows-max"></div>')
        assert "grid-auto-rows: max-content" in css
        
        css = tw.generate('<div class="auto-rows-[minmax(0,2fr)]"></div>')
        assert "grid-auto-rows: minmax(0,2fr)" in css
