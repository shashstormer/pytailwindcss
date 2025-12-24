"""
Spacing utility plugins.

Includes: width, height, min/max dimensions, padding, margin, gap, etc.
"""

from typing import List, Optional, Dict, Any
from .base import (
    UtilityPlugin, SimpleUtilityPlugin, DirectionalPlugin,
    GeneratorContext
)
from ..parser import TailwindToken, ValueType
from ..ast import Rule, Selector, Declaration, escape_css_class


# Common fractional values used across many spacing utilities
FRACTIONAL_VALUES = {
    '1/2': '50%',
    '1/3': '33.333333%',
    '2/3': '66.666667%',
    '1/4': '25%',
    '2/4': '50%',
    '3/4': '75%',
    '1/5': '20%',
    '2/5': '40%',
    '3/5': '60%',
    '4/5': '80%',
    '1/6': '16.666667%',
    '2/6': '33.333333%',
    '3/6': '50%',
    '4/6': '66.666667%',
    '5/6': '83.333333%',
    '1/12': '8.333333%',
    '2/12': '16.666667%',
    '3/12': '25%',
    '4/12': '33.333333%',
    '5/12': '41.666667%',
    '6/12': '50%',
    '7/12': '58.333333%',
    '8/12': '66.666667%',
    '9/12': '75%',
    '10/12': '83.333333%',
    '11/12': '91.666667%',
}


class WidthPlugin(UtilityPlugin):
    """Plugin for width utilities (w-*)."""
    
    name = "width"
    prefixes = ["w"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'full': '100%',
        'screen': '100vw',
        'svw': '100svw',
        'lvw': '100lvw',
        'dvw': '100dvw',
        'min': 'min-content',
        'max': 'max-content',
        'fit': 'fit-content',
        **FRACTIONAL_VALUES,
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'w' and token.modifier is None
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'width', value)


class HeightPlugin(UtilityPlugin):
    """Plugin for height utilities (h-*)."""
    
    name = "height"
    prefixes = ["h"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'full': '100%',
        'screen': '100vh',
        'svh': '100svh',
        'lvh': '100lvh',
        'dvh': '100dvh',
        'min': 'min-content',
        'max': 'max-content',
        'fit': 'fit-content',
        **FRACTIONAL_VALUES,
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'h' and token.modifier is None
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'height', value)


class SizePlugin(UtilityPlugin):
    """Plugin for size utilities (size-*) - sets both width and height."""
    
    name = "size"
    prefixes = ["size"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'full': '100%',
        'min': 'min-content',
        'max': 'max-content',
        'fit': 'fit-content',
        **FRACTIONAL_VALUES,
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'size'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_multi_rule(token, {'width': value, 'height': value})


class MinWidthPlugin(UtilityPlugin):
    """Plugin for min-width utilities (min-w-*)."""
    
    name = "min-width"
    prefixes = ["min-w"]
    
    STATIC_VALUES = {
        '0': '0px',
        'full': '100%',
        'min': 'min-content',
        'max': 'max-content',
        'fit': 'fit-content',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'min-w'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'min-width', value)


class MaxWidthPlugin(UtilityPlugin):
    """Plugin for max-width utilities (max-w-*)."""
    
    name = "max-width"
    prefixes = ["max-w"]
    
    STATIC_VALUES = {
        '0': '0rem',
        'none': 'none',
        'xs': '20rem',
        'sm': '24rem',
        'md': '28rem',
        'lg': '32rem',
        'xl': '36rem',
        '2xl': '42rem',
        '3xl': '48rem',
        '4xl': '56rem',
        '5xl': '64rem',
        '6xl': '72rem',
        '7xl': '80rem',
        'full': '100%',
        'min': 'min-content',
        'max': 'max-content',
        'fit': 'fit-content',
        'prose': '65ch',
        'screen-sm': '640px',
        'screen-md': '768px',
        'screen-lg': '1024px',
        'screen-xl': '1280px',
        'screen-2xl': '1536px',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'max-w'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'max-width', value)


class MinHeightPlugin(UtilityPlugin):
    """Plugin for min-height utilities (min-h-*)."""
    
    name = "min-height"
    prefixes = ["min-h"]
    
    STATIC_VALUES = {
        '0': '0px',
        'full': '100%',
        'screen': '100vh',
        'svh': '100svh',
        'lvh': '100lvh',
        'dvh': '100dvh',
        'min': 'min-content',
        'max': 'max-content',
        'fit': 'fit-content',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'min-h'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'min-height', value)


class MaxHeightPlugin(UtilityPlugin):
    """Plugin for max-height utilities (max-h-*)."""
    
    name = "max-height"
    prefixes = ["max-h"]
    
    STATIC_VALUES = {
        '0': '0px',
        'none': 'none',
        'full': '100%',
        'screen': '100vh',
        'svh': '100svh',
        'lvh': '100lvh',
        'dvh': '100dvh',
        'min': 'min-content',
        'max': 'max-content',
        'fit': 'fit-content',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'max-h'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'max-height', value)


class PaddingPlugin(UtilityPlugin):
    """Plugin for padding utilities (p-*, px-*, py-*, pt-*, etc.)."""
    
    name = "padding"
    prefixes = ["p", "px", "py", "pt", "pr", "pb", "pl", "ps", "pe"]
    
    # Map utility to CSS properties
    PROPERTY_MAP = {
        'p': ['padding'],
        'px': ['padding-left', 'padding-right'],
        'py': ['padding-top', 'padding-bottom'],
        'pt': ['padding-top'],
        'pr': ['padding-right'],
        'pb': ['padding-bottom'],
        'pl': ['padding-left'],
        'ps': ['padding-inline-start'],
        'pe': ['padding-inline-end'],
    }
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility in self.PROPERTY_MAP
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        
        props = self.PROPERTY_MAP.get(token.utility, ['padding'])
        if len(props) == 1:
            return self.create_rule(token, props[0], value)
        else:
            return self.create_multi_rule(token, {prop: value for prop in props})


class MarginPlugin(UtilityPlugin):
    """Plugin for margin utilities (m-*, mx-*, my-*, mt-*, etc.)."""
    
    name = "margin"
    prefixes = ["m", "mx", "my", "mt", "mr", "mb", "ml", "ms", "me"]
    
    # Map utility to CSS properties
    PROPERTY_MAP = {
        'm': ['margin'],
        'mx': ['margin-left', 'margin-right'],
        'my': ['margin-top', 'margin-bottom'],
        'mt': ['margin-top'],
        'mr': ['margin-right'],
        'mb': ['margin-bottom'],
        'ml': ['margin-left'],
        'ms': ['margin-inline-start'],
        'me': ['margin-inline-end'],
    }
    
    STATIC_VALUES = {
        'auto': 'auto',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    @property
    def supports_negative(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility in self.PROPERTY_MAP
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        
        props = self.PROPERTY_MAP.get(token.utility, ['margin'])
        if len(props) == 1:
            return self.create_rule(token, props[0], value)
        else:
            return self.create_multi_rule(token, {prop: value for prop in props})


class GapPlugin(UtilityPlugin):
    """Plugin for gap utilities (gap-*, gap-x-*, gap-y-*)."""
    
    name = "gap"
    prefixes = ["gap"]
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'gap':
            return False
        return token.modifier in (None, 'x', 'y')
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        
        if token.modifier == 'x':
            prop = 'column-gap'
        elif token.modifier == 'y':
            prop = 'row-gap'
        else:
            prop = 'gap'
        
        return self.create_rule(token, prop, value)


class SpacePlugin(UtilityPlugin):
    """Plugin for space utilities (space-x-*, space-y-*)."""
    
    name = "space"
    prefixes = ["space"]
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    @property
    def supports_negative(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'space' and token.modifier in ('x', 'y')
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        
        # space-x/y uses the lobotomized owl selector: > * + *
        selector = Selector(
            base=f".{escape_css_class(token.raw)}",
            combinator_suffix="> * + *"
        )
        
        if token.modifier == 'x':
            declarations = [Declaration(property='margin-left', value=value)]
        else:  # y
            declarations = [Declaration(property='margin-top', value=value)]
        
        return Rule(selector=selector, declarations=declarations)


class InsetPlugin(UtilityPlugin):
    """Plugin for inset/positioning utilities (inset-*, top-*, right-*, start-*, etc.)."""
    
    name = "inset"
    prefixes = ["inset", "top", "right", "bottom", "left", "start", "end"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        '0': '0px',
        'full': '100%',
        **FRACTIONAL_VALUES,
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    @property
    def supports_negative(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility == 'inset':
            return token.modifier in (None, 'x', 'y')
        return token.utility in self.prefixes
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        # Handle CSS variable shorthand
        if value is None and token.value.startswith('(') and token.value.endswith(')'):
             var_name = token.value[1:-1]
             value = f"var({var_name})"
             
        if value is None:
            return None
            
        # Handle negative values for static/fractional types
        if token.is_negative and not value.startswith('-') and value not in ('0', '0px', 'auto'):
            value = f"-{value}"
        
        if token.utility == 'inset':
            if token.modifier == 'x':
                return self.create_rule(token, 'inset-inline', value)
            elif token.modifier == 'y':
                return self.create_rule(token, 'inset-block', value)
            else:
                return self.create_rule(token, 'inset', value)
        elif token.utility == 'start':
            return self.create_rule(token, 'inset-inline-start', value)
        elif token.utility == 'end':
            return self.create_rule(token, 'inset-inline-end', value)
        else:
            return self.create_rule(token, token.utility, value)


def get_plugins() -> List[UtilityPlugin]:
    """Get all spacing-related plugins."""
    return [
        WidthPlugin(),
        HeightPlugin(),
        SizePlugin(),
        MinWidthPlugin(),
        MaxWidthPlugin(),
        MinHeightPlugin(),
        MaxHeightPlugin(),
        PaddingPlugin(),
        MarginPlugin(),
        GapPlugin(),
        SpacePlugin(),
        InsetPlugin(),
    ]
