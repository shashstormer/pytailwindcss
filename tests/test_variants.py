"""
Comprehensive tests for all Tailwind v4 variant support.

Tests are organized by variant category:
- Pseudo-classes (hover, focus, first, etc.)
- Pseudo-elements (before, after, etc.)
- Group/Peer variants
- ARIA attribute variants
- Media query variants
- Container query variants
- Arbitrary variants
"""

import pytest
from pytailwind import Tailwind


@pytest.fixture
def tw():
    return Tailwind()


# ============================================================================
# PSEUDO-CLASS VARIANTS
# ============================================================================

class TestPseudoClassVariants:
    """Test all pseudo-class variants."""
    
    @pytest.mark.parametrize("variant,expected_pseudo", [
        # Interactive states
        ("hover", ":hover"),
        ("focus", ":focus"),
        ("active", ":active"),
        ("visited", ":visited"),
        ("target", ":target"),
        ("focus-within", ":focus-within"),
        ("focus-visible", ":focus-visible"),
        
        # Child position
        ("first", ":first-child"),
        ("last", ":last-child"),
        ("only", ":only-child"),
        ("odd", ":nth-child(odd)"),
        ("even", ":nth-child(even)"),
        ("first-of-type", ":first-of-type"),
        ("last-of-type", ":last-of-type"),
        ("only-of-type", ":only-of-type"),
        
        # Form states
        ("disabled", ":disabled"),
        ("enabled", ":enabled"),
        ("checked", ":checked"),
        ("indeterminate", ":indeterminate"),
        ("default", ":default"),
        ("optional", ":optional"),
        ("required", ":required"),
        ("valid", ":valid"),
        ("invalid", ":invalid"),
        ("in-range", ":in-range"),
        ("out-of-range", ":out-of-range"),
        ("placeholder-shown", ":placeholder-shown"),
        ("autofill", ":autofill"),
        ("read-only", ":read-only"),
        
        # Other
        ("empty", ":empty"),
    ])
    def test_pseudo_class_variant(self, tw, variant, expected_pseudo):
        html = f'<div class="{variant}:text-red-500"></div>'
        css = tw.generate(html)
        assert expected_pseudo in css
        assert "color" in css


class TestNegatedPseudoClassVariants:
    """Test negated pseudo-class variants."""
    
    @pytest.mark.parametrize("variant,expected_pseudo", [
        ("not-first", ":not(:first-child)"),
        ("not-last", ":not(:last-child)"),
        ("not-only", ":not(:only-child)"),
        ("not-disabled", ":not(:disabled)"),
        ("not-enabled", ":not(:enabled)"),
        ("not-checked", ":not(:checked)"),
        ("not-odd", ":not(:nth-child(odd))"),
        ("not-even", ":not(:nth-child(even))"),
    ])
    def test_negated_pseudo_class_variant(self, tw, variant, expected_pseudo):
        html = f'<div class="{variant}:text-red-500"></div>'
        css = tw.generate(html)
        assert expected_pseudo in css


# ============================================================================
# PSEUDO-ELEMENT VARIANTS
# ============================================================================

class TestPseudoElementVariants:
    """Test all pseudo-element variants."""
    
    @pytest.mark.parametrize("variant,expected_element", [
        ("before", "::before"),
        ("after", "::after"),
        ("first-letter", "::first-letter"),
        ("first-line", "::first-line"),
        ("marker", "::marker"),
        ("selection", "::selection"),
        ("backdrop", "::backdrop"),
        ("placeholder", "::placeholder"),
        ("file", "::file-selector-button"),
    ])
    def test_pseudo_element_variant(self, tw, variant, expected_element):
        html = f'<div class="{variant}:text-red-500"></div>'
        css = tw.generate(html)
        assert expected_element in css


# ============================================================================
# GROUP VARIANTS
# ============================================================================

class TestGroupVariants:
    """Test group variants."""
    
    @pytest.mark.parametrize("variant,expected_prefix", [
        ("group-hover", ".group:hover"),
        ("group-focus", ".group:focus"),
        ("group-active", ".group:active"),
        ("group-visited", ".group:visited"),
        ("group-disabled", ".group:disabled"),
        ("group-checked", ".group:checked"),
        ("group-first", ".group:first-child"),
        ("group-last", ".group:last-child"),
        ("group-odd", ".group:nth-child(odd)"),
        ("group-even", ".group:nth-child(even)"),
    ])
    def test_group_variant(self, tw, variant, expected_prefix):
        html = f'<div class="{variant}:text-red-500"></div>'
        css = tw.generate(html)
        assert expected_prefix in css


# ============================================================================
# PEER VARIANTS
# ============================================================================

class TestPeerVariants:
    """Test peer variants."""
    
    @pytest.mark.parametrize("variant,expected_prefix", [
        ("peer-hover", ".peer:hover ~"),
        ("peer-focus", ".peer:focus ~"),
        ("peer-active", ".peer:active ~"),
        ("peer-disabled", ".peer:disabled ~"),
        ("peer-checked", ".peer:checked ~"),
        ("peer-required", ".peer:required ~"),
        ("peer-invalid", ".peer:invalid ~"),
        ("peer-valid", ".peer:valid ~"),
        ("peer-placeholder-shown", ".peer:placeholder-shown ~"),
    ])
    def test_peer_variant(self, tw, variant, expected_prefix):
        html = f'<div class="{variant}:text-red-500"></div>'
        css = tw.generate(html)
        assert expected_prefix in css


# ============================================================================
# ARIA ATTRIBUTE VARIANTS
# ============================================================================

class TestAriaVariants:
    """Test ARIA attribute variants."""
    
    @pytest.mark.parametrize("variant,expected_attr", [
        ("aria-busy", '[aria-busy="true"]'),
        ("aria-checked", '[aria-checked="true"]'),
        ("aria-disabled", '[aria-disabled="true"]'),
        ("aria-expanded", '[aria-expanded="true"]'),
        ("aria-hidden", '[aria-hidden="true"]'),
        ("aria-pressed", '[aria-pressed="true"]'),
        ("aria-readonly", '[aria-readonly="true"]'),
        ("aria-required", '[aria-required="true"]'),
        ("aria-selected", '[aria-selected="true"]'),
    ])
    def test_aria_variant(self, tw, variant, expected_attr):
        html = f'<div class="{variant}:text-red-500"></div>'
        css = tw.generate(html)
        assert expected_attr in css


# ============================================================================
# MEDIA QUERY VARIANTS
# ============================================================================

class TestMediaQueryVariants:
    """Test media query variants."""
    
    @pytest.mark.parametrize("variant,expected_query", [
        # Screen breakpoints (Tailwind v4 syntax)
        ("sm", "@media (width >= 40rem)"),
        ("md", "@media (width >= 48rem)"),
        ("lg", "@media (width >= 64rem)"),
        ("xl", "@media (width >= 80rem)"),
        ("2xl", "@media (width >= 96rem)"),
        
        # Max breakpoints (Tailwind v4 syntax)
        ("max-sm", "@media (width < 40rem)"),
        ("max-md", "@media (width < 48rem)"),
        ("max-lg", "@media (width < 64rem)"),
        ("max-xl", "@media (width < 80rem)"),
        ("max-2xl", "@media (width < 96rem)"),
    ])
    def test_screen_breakpoint_variant(self, tw, variant, expected_query):
        html = f'<div class="{variant}:text-red-500"></div>'
        css = tw.generate(html)
        assert expected_query in css


class TestMediaFeatureVariants:
    """Test media feature variants."""
    
    @pytest.mark.parametrize("variant,expected_query", [
        # Color scheme
        ("dark", "@media (prefers-color-scheme: dark)"),
        ("light", "@media (prefers-color-scheme: light)"),
        
        # Motion
        ("motion-safe", "@media (prefers-reduced-motion: no-preference)"),
        ("motion-reduce", "@media (prefers-reduced-motion: reduce)"),
        
        # Contrast
        ("contrast-more", "@media (prefers-contrast: more)"),
        ("contrast-less", "@media (prefers-contrast: less)"),
        
        # Forced colors
        ("forced-colors", "@media (forced-colors: active)"),
        
        # Pointer
        ("pointer-fine", "@media (pointer: fine)"),
        ("pointer-coarse", "@media (pointer: coarse)"),
        ("pointer-none", "@media (pointer: none)"),
        
        # Orientation
        ("portrait", "@media (orientation: portrait)"),
        ("landscape", "@media (orientation: landscape)"),
        
        # Print
        ("print", "@media print"),
    ])
    def test_media_feature_variant(self, tw, variant, expected_query):
        html = f'<div class="{variant}:text-red-500"></div>'
        css = tw.generate(html)
        assert expected_query in css


# ============================================================================
# CONTAINER QUERY VARIANTS
# ============================================================================

class TestContainerQueryVariants:
    """Test container query variants."""
    
    @pytest.mark.parametrize("variant,expected_query", [
        ("@sm", "@container (width >= 24rem)"),
        ("@md", "@container (width >= 28rem)"),
        ("@lg", "@container (width >= 32rem)"),
        ("@xl", "@container (width >= 36rem)"),
        ("@2xl", "@container (width >= 42rem)"),
        ("@3xl", "@container (width >= 48rem)"),
        ("@max-sm", "@container (width < 24rem)"),
        ("@max-md", "@container (width < 28rem)"),
        ("@max-lg", "@container (width < 32rem)"),
    ])
    def test_container_query_variant(self, tw, variant, expected_query):
        html = f'<div class="{variant}:text-red-500"></div>'
        css = tw.generate(html)
        assert expected_query in css


# ============================================================================
# ARBITRARY VARIANTS
# ============================================================================

class TestArbitraryVariants:
    """Test arbitrary variants like has-[...], nth-[...], etc."""
    
    def test_arbitrary_has_variant(self, tw):
        html = '<div class="has-[.child]:text-red-500"></div>'
        css = tw.generate(html)
        assert "has(" in css
    
    def test_arbitrary_nth_variant(self, tw):
        html = '<div class="nth-[3]:text-red-500"></div>'
        css = tw.generate(html)
        assert "nth-child(3)" in css
    
    def test_arbitrary_nth_last_variant(self, tw):
        html = '<div class="nth-last-[2]:text-red-500"></div>'
        css = tw.generate(html)
        assert "nth-last-child(2)" in css
    
    def test_arbitrary_aria_variant(self, tw):
        html = '<div class="aria-[sort=ascending]:text-red-500"></div>'
        css = tw.generate(html)
        assert "[aria-sort=ascending]" in css
    
    def test_arbitrary_data_variant(self, tw):
        html = '<div class="data-[state=open]:text-red-500"></div>'
        css = tw.generate(html)
        assert "[data-state=open]" in css
    
    def test_arbitrary_min_width(self, tw):
        html = '<div class="min-[500px]:text-red-500"></div>'
        css = tw.generate(html)
        assert "@media (width >= 500px)" in css
    
    def test_arbitrary_max_width(self, tw):
        html = '<div class="max-[800px]:text-red-500"></div>'
        css = tw.generate(html)
        assert "@media (width < 800px)" in css
    
    def test_arbitrary_supports(self, tw):
        html = '<div class="supports-[display:grid]:text-red-500"></div>'
        css = tw.generate(html)
        # Note: supports-[...] should generate @supports
        assert "display" in css or "@supports" in css


# ============================================================================
# COMBINED VARIANTS
# ============================================================================

class TestCombinedVariants:
    """Test combining multiple variants."""
    
    def test_hover_sm(self, tw):
        html = '<div class="hover:sm:text-red-500"></div>'
        css = tw.generate(html)
        assert "@media" in css
        assert ":hover" in css
    
    def test_dark_hover(self, tw):
        html = '<div class="dark:hover:text-red-500"></div>'
        css = tw.generate(html)
        assert "@media (prefers-color-scheme: dark)" in css
        assert ":hover" in css
    
    def test_group_hover_focus(self, tw):
        html = '<div class="group-hover:focus:text-red-500"></div>'
        css = tw.generate(html)
        assert ".group:hover" in css
        assert ":focus" in css
    
    def test_md_first(self, tw):
        html = '<div class="md:first:text-red-500"></div>'
        css = tw.generate(html)
        assert "@media (width >= 48rem)" in css
        assert ":first-child" in css


# ============================================================================
# DIRECTION VARIANTS
# ============================================================================

class TestDirectionVariants:
    """Test direction variants (rtl, ltr)."""
    
    def test_rtl_variant(self, tw):
        html = '<div class="rtl:text-right"></div>'
        css = tw.generate(html)
        assert "rtl" in css or "dir" in css
    
    def test_ltr_variant(self, tw):
        html = '<div class="ltr:text-left"></div>'
        css = tw.generate(html)
        assert "ltr" in css or "dir" in css


# ============================================================================
# STATE VARIANTS
# ============================================================================

class TestStateVariants:
    """Test state variants (open, inert)."""
    
    def test_open_variant(self, tw):
        html = '<div class="open:bg-red-500"></div>'
        css = tw.generate(html)
        assert "open" in css
    
    def test_inert_variant(self, tw):
        html = '<div class="inert:opacity-50"></div>'
        css = tw.generate(html)
        assert "inert" in css
