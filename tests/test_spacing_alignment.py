"""
Tests for Spacing and Alignment utilities.
"""

import pytest
from pytailwind import Tailwind

@pytest.fixture
def tw():
    return Tailwind(include_preflight=False)

class TestSpacingVariables:
    def test_padding_vars(self, tw):
        css = tw.generate('<div class="p-(--my-pad)"></div>')
        assert "padding: var(--my-pad)" in css
        
        css = tw.generate('<div class="px-(--my-pad)"></div>')
        assert "padding-left: var(--my-pad)" in css
        assert "padding-right: var(--my-pad)" in css

    def test_margin_vars(self, tw):
        css = tw.generate('<div class="m-(--my-marg)"></div>')
        assert "margin: var(--my-marg)" in css
        
        css = tw.generate('<div class="my-(--my-marg)"></div>')
        assert "margin-top: var(--my-marg)" in css
        assert "margin-bottom: var(--my-marg)" in css

    def test_gap_vars(self, tw):
        css = tw.generate('<div class="gap-(--my-gap)"></div>')
        assert "gap: var(--my-gap)" in css
        
        css = tw.generate('<div class="gap-x-(--my-gap)"></div>')
        assert "column-gap: var(--my-gap)" in css

class TestSpaceBetween:
    def test_space_bidirectional(self, tw):
        # space-x-4
        css = tw.generate('<div class="space-x-4"></div>')
        assert "--tw-space-x-reverse: 0" in css
        assert "margin-inline-start: calc(1rem * calc(1 - var(--tw-space-x-reverse)))" in css
        assert "margin-inline-end: calc(1rem * var(--tw-space-x-reverse))" in css
        
        # space-y-4
        css = tw.generate('<div class="space-y-4"></div>')
        assert "--tw-space-y-reverse: 0" in css
        assert "margin-top: calc(1rem * calc(1 - var(--tw-space-y-reverse)))" in css
        
    def test_space_reverse(self, tw):
        css = tw.generate('<div class="space-x-reverse"></div>')
        assert "--tw-space-x-reverse: 1" in css
        
    def test_space_vars(self, tw):
        css = tw.generate('<div class="space-x-(--s)"></div>')
        assert "margin-inline-start: calc(var(--s) * calc(1 - var(--tw-space-x-reverse)))" in css

class TestAlignment:
    def test_justify_content_safe(self, tw):
        css = tw.generate('<div class="justify-center-safe"></div>')
        assert "justify-content: safe center" in css
        
        css = tw.generate('<div class="justify-start-safe"></div>')
        assert "justify-content: safe flex-start" in css

    def test_align_items_safe(self, tw):
        css = tw.generate('<div class="items-center-safe"></div>')
        assert "align-items: safe center" in css

    def test_align_content_safe(self, tw):
        css = tw.generate('<div class="content-end-safe"></div>')
        assert "align-content: safe flex-end" in css
        
    def test_align_self_safe(self, tw):
        css = tw.generate('<div class="self-center-safe"></div>')
        assert "align-self: safe center" in css

    def test_justify_items(self, tw):
        css = tw.generate('<div class="justify-items-start"></div>')
        assert "justify-items: start" in css
        
        css = tw.generate('<div class="justify-items-center-safe"></div>')
        assert "justify-items: safe center" in css

    def test_justify_self(self, tw):
        css = tw.generate('<div class="justify-self-end"></div>')
        assert "justify-self: end" in css

    def test_place_content(self, tw):
        css = tw.generate('<div class="place-content-center"></div>')
        assert "place-content: center" in css
        
        css = tw.generate('<div class="place-content-between"></div>')
        assert "place-content: space-between" in css

    def test_place_items(self, tw):
        css = tw.generate('<div class="place-items-stretch"></div>')
        assert "place-items: stretch" in css

    def test_place_self(self, tw):
        css = tw.generate('<div class="place-self-auto"></div>')
        assert "place-self: auto" in css
        
        css = tw.generate('<div class="place-self-center-safe"></div>')
        assert "place-self: safe center" in css
