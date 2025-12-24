"""
Preflight - Tailwind CSS base styles.

Preflight is a set of base styles for Tailwind projects, built on top of
modern-normalize, designed to smooth over cross-browser inconsistencies
and make it easier to work within the constraints of your design system.

Based on Tailwind CSS v4 Preflight:
https://tailwindcss.com/docs/preflight
"""

# The complete Preflight CSS as specified in Tailwind v4
PREFLIGHT_CSS = """/* Preflight - Base styles for Tailwind CSS */

/*
 * Box sizing and border reset
 * Makes box-sizing consistent and resets margins/padding
 */
*,
::after,
::before,
::backdrop,
::file-selector-button {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  border: 0 solid;
}

/*
 * Headings are unstyled
 * Helps avoid accidentally deviating from your type scale
 */
h1,
h2,
h3,
h4,
h5,
h6 {
  font-size: inherit;
  font-weight: inherit;
}

/*
 * Lists are unstyled
 * No bullets or numbers by default
 */
ol,
ul,
menu {
  list-style: none;
}

/*
 * Replaced elements are block-level
 * Helps avoid unexpected alignment issues
 */
img,
svg,
video,
canvas,
audio,
iframe,
embed,
object {
  display: block;
  vertical-align: middle;
}

/*
 * Images and videos are constrained
 * Responsive by default, preserving aspect ratio
 */
img,
video {
  max-width: 100%;
  height: auto;
}

/*
 * Hidden attribute enforcement
 * Elements with hidden attribute stay invisible
 */
[hidden]:where(:not([hidden="until-found"])) {
  display: none !important;
}
"""


def get_preflight() -> str:
    """
    Return the Preflight CSS string.
    
    Returns:
        The complete Preflight base styles as a CSS string.
        
    Example:
        >>> from pytailwind.preflight import get_preflight
        >>> css = get_preflight()
        >>> 'box-sizing: border-box' in css
        True
    """
    return PREFLIGHT_CSS


def get_preflight_layered() -> str:
    """
    Return the Preflight CSS wrapped in @layer base.
    
    This is useful when integrating with projects that use CSS layers.
    
    Returns:
        The Preflight base styles wrapped in @layer base.
        
    Example:
        >>> from pytailwind.preflight import get_preflight_layered
        >>> css = get_preflight_layered()
        >>> '@layer base' in css
        True
    """
    return f"@layer base {{\n{PREFLIGHT_CSS}}}\n"
