"""
Color utility plugins.

Includes: background color, text color, border color, gradients, etc.
"""

from typing import List, Optional, Dict, Any
from .base import UtilityPlugin, GeneratorContext
from ..parser import TailwindToken, ValueType
from ..ast import Rule, Selector, Declaration, escape_css_class
import re


class ColorPlugin(UtilityPlugin):
    """
    Base plugin for color utilities.
    
    Handles color resolution from theme and arbitrary values.
    """
    
    # Regex for detecting hex colors
    HEX_PATTERN = re.compile(r'^#[0-9a-fA-F]{3,8}$')
    
    @property
    def supports_colors(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def resolve_color_value(self, token: TailwindToken, context: GeneratorContext) -> Optional[str]:
        """
        Resolve token to a color value.
        
        Handles:
        - Arbitrary values: [#ff0000], [rgb(255,0,0)]
        - Named colors: inherit, currentColor, transparent
        - Theme colors: red-500, blue-100
        """
        if not token.value:
            return None
        
        # Arbitrary value
        if token.value_type == ValueType.ARBITRARY:
            inner = token.value[1:-1] if token.value.startswith('[') else token.value
            inner = self._replace_underscores(inner)
            return inner
        
        # Check for special keywords
        special = {
            'inherit': 'inherit',
            'current': 'currentColor',
            'transparent': 'transparent',
            'black': '#000',
            'white': '#fff',
        }
        if token.value in special:
            return special[token.value]
        
        # Resolve from theme colors
        parts = token.value.split('-')
        color_value = context.resolve_color(*parts)
        return color_value
    
    def apply_opacity(self, color: str, opacity: Optional[int]) -> str:
        """
        Apply opacity to a color value.
        
        Converts hex to rgba if opacity is specified.
        """
        if opacity is None or opacity >= 100:
            return color
        
        # Check if it's a hex color
        if self.HEX_PATTERN.match(color):
            rgba = self._hex_to_rgba(color, opacity / 100)
            return rgba
        
        # For other formats, we can't easily apply opacity
        return color
    
    def _hex_to_rgba(self, hex_color: str, opacity: float) -> str:
        """Convert hex color to rgba with opacity."""
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])
        
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        return f"rgba({r}, {g}, {b}, {opacity})"


class BackgroundColorPlugin(ColorPlugin):
    """Plugin for background color utilities (bg-*)."""
    
    name = "background-color"
    prefixes = ["bg"]
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'bg':
            return False
        # Don't match bg-gradient-*, bg-contain, bg-cover, etc.
        if token.value and token.value.startswith('gradient'):
            return False
        if token.value in ('contain', 'cover', 'auto', 'repeat', 'no-repeat', 
                           'fixed', 'local', 'scroll', 'center', 'top', 'bottom',
                           'left', 'right', 'none', 'clip'):
            return False
        return True
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        color = self.resolve_color_value(token, context)
        if color is None:
            return None
        
        color = self.apply_opacity(color, token.opacity)
        return self.create_rule(token, 'background-color', color)


class TextColorPlugin(ColorPlugin):
    """Plugin for text color utilities (text-*)."""
    
    name = "text-color"
    prefixes = ["text"]
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'text':
            return False
        # Don't match text alignment, size, etc.
        if token.value in ('left', 'center', 'right', 'justify', 'start', 'end',
                           'xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', 
                           '5xl', '6xl', '7xl', '8xl', '9xl',
                           'wrap', 'nowrap', 'balance', 'pretty',
                           'ellipsis', 'clip'):
            return False
        return True
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        color = self.resolve_color_value(token, context)
        if color is None:
            return None
        
        color = self.apply_opacity(color, token.opacity)
        return self.create_rule(token, 'color', color)


class BorderColorPlugin(ColorPlugin):
    """Plugin for border color utilities (border-*)."""
    
    name = "border-color"
    prefixes = ["border"]
    
    DIRECTIONS = {'t', 'r', 'b', 'l', 'x', 'y', 's', 'e'}
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'border':
            return False
        # Don't match border width (numbers) or style
        if token.value in ('0', '2', '4', '8', 'DEFAULT',
                           'solid', 'dashed', 'dotted', 'double', 'hidden', 'none',
                           'collapse', 'separate'):
            return False
        # Don't match directional without color value
        if token.modifier in self.DIRECTIONS and not token.value:
            return False
        return True
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        color = self.resolve_color_value(token, context)
        if color is None:
            return None
        
        color = self.apply_opacity(color, token.opacity)
        
        # Handle directional borders
        if token.modifier == 'x':
            return self.create_multi_rule(token, {
                'border-left-color': color,
                'border-right-color': color
            })
        elif token.modifier == 'y':
            return self.create_multi_rule(token, {
                'border-top-color': color,
                'border-bottom-color': color
            })
        elif token.modifier == 't':
            return self.create_rule(token, 'border-top-color', color)
        elif token.modifier == 'r':
            return self.create_rule(token, 'border-right-color', color)
        elif token.modifier == 'b':
            return self.create_rule(token, 'border-bottom-color', color)
        elif token.modifier == 'l':
            return self.create_rule(token, 'border-left-color', color)
        elif token.modifier == 's':
            return self.create_rule(token, 'border-inline-start-color', color)
        elif token.modifier == 'e':
            return self.create_rule(token, 'border-inline-end-color', color)
        else:
            return self.create_rule(token, 'border-color', color)


class DivideColorPlugin(ColorPlugin):
    """Plugin for divide color utilities (divide-*)."""
    
    name = "divide-color"
    prefixes = ["divide"]
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'divide':
            return False
        # Don't match divide-x, divide-y (those are divideWidth)
        if token.modifier in ('x', 'y'):
            return False
        # Don't match divide width values
        if token.value in ('0', '2', '4', '8', 'reverse'):
            return False
        return True
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        color = self.resolve_color_value(token, context)
        if color is None:
            return None
        
        color = self.apply_opacity(color, token.opacity)
        
        # Divide uses the > * + * pattern
        selector = Selector(
            base=f".{escape_css_class(token.raw)}",
            combinator_suffix="> * + *"
        )
        return Rule(
            selector=selector,
            declarations=[Declaration(property='border-color', value=color)]
        )


class RingColorPlugin(ColorPlugin):
    """Plugin for ring color utilities (ring-*)."""
    
    name = "ring-color"
    prefixes = ["ring"]
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'ring':
            return False
        # Don't match ring width (numbers)
        if token.value in ('0', '1', '2', '4', '8', 'DEFAULT', 'inset'):
            return False
        # Don't match ring-offset-*
        if token.modifier == 'offset':
            return False
        return True
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        color = self.resolve_color_value(token, context)
        if color is None:
            return None
        
        color = self.apply_opacity(color, token.opacity)
        return self.create_rule(token, '--tw-ring-color', color)


class RingOffsetColorPlugin(ColorPlugin):
    """Plugin for ring offset color utilities (ring-offset-*)."""
    
    name = "ring-offset-color"
    prefixes = ["ring-offset"]
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'ring' or token.modifier != 'offset':
            return False
        # Ring offset width is numeric
        if token.value.isdigit():
            return False
        return True
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        color = self.resolve_color_value(token, context)
        if color is None:
            return None
        
        color = self.apply_opacity(color, token.opacity)
        return self.create_rule(token, '--tw-ring-offset-color', color)


class GradientPlugin(ColorPlugin):
    """Plugin for gradient color stops (from-*, via-*, to-*)."""
    
    name = "gradient"
    prefixes = ["from", "via", "to"]
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility in ('from', 'via', 'to')
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        color = self.resolve_color_value(token, context)
        if color is None:
            return None
        
        color = self.apply_opacity(color, token.opacity)
        
        if token.utility == 'from':
            var_name = '--tw-gradient-from'
            # Also update stops
            stops = f"var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position)"
            return self.create_multi_rule(token, {
                var_name: color,
                '--tw-gradient-to': f"{color.replace('1)', '0)')} " if 'rgba' in color else 'transparent',
                '--tw-gradient-stops': stops,
            })
        elif token.utility == 'via':
            var_name = '--tw-gradient-via'
            stops = f"var(--tw-gradient-from) var(--tw-gradient-from-position), {color} var(--tw-gradient-via-position), var(--tw-gradient-to) var(--tw-gradient-to-position)"
            return self.create_multi_rule(token, {
                var_name: color,
                '--tw-gradient-stops': stops,
            })
        else:  # to
            return self.create_rule(token, '--tw-gradient-to', color)


class FillPlugin(ColorPlugin):
    """Plugin for SVG fill utilities (fill-*)."""
    
    name = "fill"
    prefixes = ["fill"]
    
    STATIC_VALUES = {
        'none': 'none',
        'current': 'currentColor',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'fill'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        # Check static values first
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'fill', self.STATIC_VALUES[token.value])
        
        color = self.resolve_color_value(token, context)
        if color is None:
            return None
        
        color = self.apply_opacity(color, token.opacity)
        return self.create_rule(token, 'fill', color)


class StrokeColorPlugin(ColorPlugin):
    """Plugin for SVG stroke color utilities (stroke-*)."""
    
    name = "stroke-color"
    prefixes = ["stroke"]
    
    STATIC_VALUES = {
        'none': 'none',
        'current': 'currentColor',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'stroke':
            return False
        # Don't match stroke width (numeric values)
        if token.value and token.value.replace('.', '').isdigit():
            return False
        return True
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        # Check static values first
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'stroke', self.STATIC_VALUES[token.value])
        
        color = self.resolve_color_value(token, context)
        if color is None:
            return None
        
        color = self.apply_opacity(color, token.opacity)
        return self.create_rule(token, 'stroke', color)


class AccentColorPlugin(ColorPlugin):
    """Plugin for accent color utilities (accent-*)."""
    
    name = "accent-color"
    prefixes = ["accent"]
    
    STATIC_VALUES = {
        'auto': 'auto',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'accent'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'accent-color', self.STATIC_VALUES[token.value])
        
        color = self.resolve_color_value(token, context)
        if color is None:
            return None
        
        color = self.apply_opacity(color, token.opacity)
        return self.create_rule(token, 'accent-color', color)


class CaretColorPlugin(ColorPlugin):
    """Plugin for caret color utilities (caret-*)."""
    
    name = "caret-color"
    prefixes = ["caret"]
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'caret'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        color = self.resolve_color_value(token, context)
        if color is None:
            return None
        
        color = self.apply_opacity(color, token.opacity)
        return self.create_rule(token, 'caret-color', color)


def get_plugins() -> List[UtilityPlugin]:
    """Get all color-related plugins."""
    return [
        BackgroundColorPlugin(),
        TextColorPlugin(),
        BorderColorPlugin(),
        DivideColorPlugin(),
        RingColorPlugin(),
        RingOffsetColorPlugin(),
        GradientPlugin(),
        FillPlugin(),
        StrokeColorPlugin(),
        AccentColorPlugin(),
        CaretColorPlugin(),
    ]
