"""
Tests for layout positioning and display utilities.
Checks float, clear, isolation, object-position, overscroll, visibility, sr-only, and inset.
"""

import pytest
from pytailwind import Tailwind


@pytest.fixture
def tw():
    return Tailwind(include_preflight=False)


class TestFloatClear:
    def test_float(self, tw):
        assert "float: right" in tw.generate('<div class="float-right"></div>')
        assert "float: inline-start" in tw.generate('<div class="float-start"></div>')
        assert "float: none" in tw.generate('<div class="float-none"></div>')
    
    def test_clear(self, tw):
        assert "clear: left" in tw.generate('<div class="clear-left"></div>')
        assert "clear: both" in tw.generate('<div class="clear-both"></div>')
        assert "clear: inline-end" in tw.generate('<div class="clear-end"></div>')


class TestIsolation:
    def test_isolation(self, tw):
        assert "isolation: isolate" in tw.generate('<div class="isolate"></div>')
        assert "isolation: auto" in tw.generate('<div class="isolation-auto"></div>')


class TestObjectPosition:
    def test_basic(self, tw):
        assert "object-position: center" in tw.generate('<div class="object-center"></div>')
        assert "object-position: top right" in tw.generate('<div class="object-top-right"></div>')
        
    def test_arbitrary(self, tw):
        assert "object-position: 50% 50%" in tw.generate('<div class="object-[50%_50%]"></div>')
        
    def test_no_conflict_fit(self, tw):
        # Should generate object-fit, not object-position
        css = tw.generate('<div class="object-contain"></div>')
        assert "object-fit: contain" in css
        assert "object-position" not in css


class TestOverscroll:
    def test_overscroll(self, tw):
        assert "overscroll-behavior: auto" in tw.generate('<div class="overscroll-auto"></div>')
        assert "overscroll-behavior-y: contain" in tw.generate('<div class="overscroll-y-contain"></div>')
        assert "overscroll-behavior-x: none" in tw.generate('<div class="overscroll-x-none"></div>')


class TestVisibility:
    def test_visibility(self, tw):
        assert "visibility: visible" in tw.generate('<div class="visible"></div>')
        assert "visibility: hidden" in tw.generate('<div class="invisible"></div>')
        assert "visibility: collapse" in tw.generate('<div class="collapse"></div>')


class TestSrOnly:
    def test_sr_only(self, tw):
        css = tw.generate('<div class="sr-only"></div>')
        assert "position: absolute" in css
        assert "width: 1px" in css
        assert "clip: rect(0, 0, 0, 0)" in css
    
    def test_not_sr_only(self, tw):
        css = tw.generate('<div class="not-sr-only"></div>')
        assert "position: static" in css
        assert "width: auto" in css
        assert "clip: auto" in css


class TestInset:
    def test_basic_inset(self, tw):
        css = tw.generate('<div class="inset-0"></div>')
        assert "inset: 0" in css or "inset: 0px" in css
    
    def test_directions(self, tw):
        assert "top: 1rem" in tw.generate('<div class="top-4"></div>')
        assert "right: 1px" in tw.generate('<div class="right-px"></div>')
        assert "bottom: 0" in tw.generate('<div class="bottom-0"></div>')
        assert "left: 100%" in tw.generate('<div class="left-full"></div>')
    
    def test_negative(self, tw):
        css = tw.generate('<div class="-top-4"></div>')
        assert "top: -1rem" in css
        
        css = tw.generate('<div class="-left-1/2"></div>')
        # Expect left: -50%
        assert "left: -50%" in css

    def test_fractions(self, tw):
        assert "top: 33.333333%" in tw.generate('<div class="top-1/3"></div>')
        assert "inset: 50%" in tw.generate('<div class="inset-1/2"></div>')
        
    def test_logical(self, tw):
        # inset-x -> inset-inline
        assert "inset-inline: auto" in tw.generate('<div class="inset-x-auto"></div>')
        # inset-y -> inset-block
        assert "inset-block: 1rem" in tw.generate('<div class="inset-y-4"></div>')
        # start
        assert "inset-inline-start: 1px" in tw.generate('<div class="start-px"></div>')
        # end
        assert "inset-inline-end: 0" in tw.generate('<div class="end-0"></div>')

    def test_arbitrary(self, tw):
        assert "top: 13px" in tw.generate('<div class="top-[13px]"></div>')
