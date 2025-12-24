"""
Tests for variant/processor handling in the new generator.

These tests verify that pseudo-classes, pseudo-elements, and media queries
are correctly applied to generated CSS.
"""

import pytest
from pytailwind import Tailwind


@pytest.fixture
def tw():
    return Tailwind()


# Pseudo-class variants
@pytest.mark.parametrize("processor,expected_selector", [
    ("hover", ":hover"),
    ("focus", ":focus"),
    ("active", ":active"),
    ("visited", ":visited"),
    ("first", ":first-child"),
    ("last", ":last-child"),
    ("odd", ":nth-child(odd)"),
    ("even", ":nth-child(even)"),
    ("disabled", ":disabled"),
    ("focus-within", ":focus-within"),
    ("focus-visible", ":focus-visible"),
    ("checked", ":checked"),
    ("required", ":required"),
    ("invalid", ":invalid"),
    ("first-of-type", ":first-of-type"),
    ("last-of-type", ":last-of-type"),
    ("only", ":only-child"),
    ("only-of-type", ":only-of-type"),
    ("empty", ":empty"),
    ("read-only", ":read-only"),
    ("placeholder-shown", ":placeholder-shown"),
])
def test_pseudo_class_variants(tw, processor, expected_selector):
    """Test that pseudo-class variants generate correct CSS selectors."""
    html = f'<div class="{processor}:text-red-500"></div>'
    css = tw.generate(html)
    assert expected_selector in css
    assert "color: #ef4444" in css


# Pseudo-element variants
@pytest.mark.parametrize("processor,expected_selector", [
    ("before", "::before"),
    ("after", "::after"),
])
def test_pseudo_element_variants(tw, processor, expected_selector):
    """Test that pseudo-element variants generate correct CSS selectors."""
    html = f'<div class="{processor}:text-red-500"></div>'
    css = tw.generate(html)
    assert expected_selector in css
    assert "color: #ef4444" in css


# Media query variants
@pytest.mark.parametrize("processor,expected_query", [
    ("sm", "@media (width >= 40rem)"),
    ("md", "@media (width >= 48rem)"),
    ("lg", "@media (width >= 64rem)"),
    ("xl", "@media (width >= 80rem)"),
    ("2xl", "@media (width >= 96rem)"),
    ("max-sm", "@media (width < 40rem)"),
    ("max-md", "@media (width < 48rem)"),
    ("max-lg", "@media (width < 64rem)"),
    ("max-xl", "@media (width < 80rem)"),
    ("max-2xl", "@media (width < 96rem)"),
    ("dark", "@media (prefers-color-scheme: dark)"),
    ("light", "@media (prefers-color-scheme: light)"),
    ("motion-safe", "@media (prefers-reduced-motion: no-preference)"),
    ("motion-reduce", "@media (prefers-reduced-motion: reduce)"),
    ("print", "@media print"),
])
def test_media_query_variants(tw, processor, expected_query):
    """Test that media query variants generate correct CSS."""
    html = f'<div class="{processor}:text-red-500"></div>'
    css = tw.generate(html)
    assert expected_query in css
    assert "color: #ef4444" in css


# Group variants
@pytest.mark.parametrize("processor,expected_part", [
    ("group-hover", ".group:hover"),
])
def test_group_variants(tw, processor, expected_part):
    """Test that group variants generate correct CSS selectors."""
    html = f'<div class="{processor}:text-red-500"></div>'
    css = tw.generate(html)
    assert expected_part in css


# Test variant combinations
def test_variant_combinations(tw):
    """Test combining pseudo-class and media query variants."""
    html = '<div class="hover:sm:text-red-500"></div>'
    css = tw.generate(html)
    assert "@media (width >= 40rem)" in css
    assert ":hover" in css


def test_dark_mode_variant(tw):
    """Test dark mode variant works correctly."""
    html = '<div class="dark:bg-gray-800"></div>'
    css = tw.generate(html)
    assert "@media (prefers-color-scheme: dark)" in css
    assert "background-color" in css
