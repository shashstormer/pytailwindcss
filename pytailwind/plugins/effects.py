"""
Effects utility plugins.

Includes: opacity, shadows, filters, transitions, transforms, etc.
"""

from typing import List, Optional, Dict
from .base import UtilityPlugin, GeneratorContext
from ..parser import TailwindToken, ValueType
from ..ast import Rule, Selector, Declaration, escape_css_class


class OpacityPlugin(UtilityPlugin):
    """Plugin for opacity utilities (opacity-*)."""
    
    name = "opacity"
    prefixes = ["opacity"]
    
    STATIC_VALUES = {
        '0': '0',
        '5': '0.05',
        '10': '0.1',
        '15': '0.15',
        '20': '0.2',
        '25': '0.25',
        '30': '0.3',
        '35': '0.35',
        '40': '0.4',
        '45': '0.45',
        '50': '0.5',
        '55': '0.55',
        '60': '0.6',
        '65': '0.65',
        '70': '0.7',
        '75': '0.75',
        '80': '0.8',
        '85': '0.85',
        '90': '0.9',
        '95': '0.95',
        '100': '1',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'opacity'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'opacity', value)


class BoxShadowPlugin(UtilityPlugin):
    """Plugin for box-shadow utilities (shadow-*)."""
    
    name = "box-shadow"
    prefixes = ["shadow"]
    
    STATIC_VALUES = {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'DEFAULT': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        'inner': 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
        'none': 'none',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'shadow':
            return False
        # Check if it's a shadow utility, not shadow-color
        if token.value in self.STATIC_VALUES or not token.value or token.value_type == ValueType.ARBITRARY:
            return True
        return False
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'box-shadow', value)


class BorderRadiusPlugin(UtilityPlugin):
    """Plugin for border-radius utilities (rounded-*)."""
    
    name = "border-radius"
    prefixes = ["rounded"]
    
    STATIC_VALUES = {
        'none': '0px',
        'sm': '0.125rem',
        'DEFAULT': '0.25rem',
        'md': '0.375rem',
        'lg': '0.5rem',
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
        'full': '9999px',
    }
    
    # Directional mappings
    DIRECTIONS = {
        't': ['border-top-left-radius', 'border-top-right-radius'],
        'r': ['border-top-right-radius', 'border-bottom-right-radius'],
        'b': ['border-bottom-left-radius', 'border-bottom-right-radius'],
        'l': ['border-top-left-radius', 'border-bottom-left-radius'],
        'tl': ['border-top-left-radius'],
        'tr': ['border-top-right-radius'],
        'br': ['border-bottom-right-radius'],
        'bl': ['border-bottom-left-radius'],
        's': ['border-start-start-radius', 'border-end-start-radius'],
        'e': ['border-start-end-radius', 'border-end-end-radius'],
        'ss': ['border-start-start-radius'],
        'se': ['border-start-end-radius'],
        'ee': ['border-end-end-radius'],
        'es': ['border-end-start-radius'],
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'rounded'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        # Handle directional modifiers
        modifier = token.modifier
        
        # Get the value 
        # For rounded with just a modifier (like rounded-t), the value might be empty
        if not token.value and modifier in self.DIRECTIONS:
            value = self.STATIC_VALUES.get('DEFAULT', '0.25rem')
        elif token.value in self.STATIC_VALUES:
            value = self.STATIC_VALUES[token.value]
        elif token.value_type == ValueType.ARBITRARY:
            inner = token.value[1:-1] if token.value.startswith('[') else token.value
            value = self._replace_underscores(inner)
        else:
            value = self.resolve_value(token, context)
        
        if value is None:
            return None
        
        # Apply to specific corners or all
        if modifier in self.DIRECTIONS:
            properties = {prop: value for prop in self.DIRECTIONS[modifier]}
            return self.create_multi_rule(token, properties)
        else:
            return self.create_rule(token, 'border-radius', value)


class BorderWidthPlugin(UtilityPlugin):
    """Plugin for border-width utilities (border-*, border-t-*, etc.)."""
    
    name = "border-width"
    prefixes = ["border"]
    
    STATIC_VALUES = {
        '': '1px',  # Just "border"
        '0': '0px',
        '2': '2px',
        '4': '4px',
        '8': '8px',
    }
    
    DIRECTIONS = {
        None: ['border-width'],
        'x': ['border-left-width', 'border-right-width'],
        'y': ['border-top-width', 'border-bottom-width'],
        't': ['border-top-width'],
        'r': ['border-right-width'],
        'b': ['border-bottom-width'],
        'l': ['border-left-width'],
        's': ['border-inline-start-width'],
        'e': ['border-inline-end-width'],
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'border':
            return False
        # Match width values, not color or style
        if not token.value and token.modifier in self.DIRECTIONS:
            return True
        if token.value in self.STATIC_VALUES:
            return True
        if token.value_type == ValueType.ARBITRARY:
            # Check if it looks like a width value
            inner = token.value[1:-1] if token.value.startswith('[') else token.value
            if any(unit in inner for unit in ['px', 'rem', 'em', '%']):
                return True
        return False
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        # Determine value
        if not token.value:
            value = self.STATIC_VALUES.get('', '1px')
        elif token.value in self.STATIC_VALUES:
            value = self.STATIC_VALUES[token.value]
        elif token.value_type == ValueType.ARBITRARY:
            inner = token.value[1:-1] if token.value.startswith('[') else token.value
            value = self._replace_underscores(inner)
        else:
            return None
        
        # Apply directionally
        props = self.DIRECTIONS.get(token.modifier, ['border-width'])
        properties = {prop: value for prop in props}
        return self.create_multi_rule(token, properties)


class DivideWidthPlugin(UtilityPlugin):
    """Plugin for divide-width utilities (divide-x-*, divide-y-*)."""
    
    name = "divide-width"
    prefixes = ["divide"]
    
    STATIC_VALUES = {
        '': '1px',
        '0': '0px',
        '2': '2px',
        '4': '4px',
        '8': '8px',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'divide':
            return False
        return token.modifier in ('x', 'y')
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        # Determine value
        if not token.value:
            value = self.STATIC_VALUES.get('', '1px')
        elif token.value in self.STATIC_VALUES:
            value = self.STATIC_VALUES[token.value]
        elif token.value_type == ValueType.ARBITRARY:
            inner = token.value[1:-1] if token.value.startswith('[') else token.value
            value = self._replace_underscores(inner)
        else:
            value = self.resolve_value(token, context)
        
        if value is None:
            return None
        
        # Divide uses the > * + * pattern
        selector = Selector(
            base=f".{escape_css_class(token.raw)}",
            combinator_suffix="> * + *"
        )
        
        if token.modifier == 'x':
            declarations = [Declaration(property='border-left-width', value=value)]
        else:  # y
            declarations = [Declaration(property='border-top-width', value=value)]
        
        return Rule(selector=selector, declarations=declarations)


class RingWidthPlugin(UtilityPlugin):
    """Plugin for ring-width utilities (ring-*, ring-0, ring-2, etc.)."""
    
    name = "ring-width"
    prefixes = ["ring"]
    
    STATIC_VALUES = {
        'DEFAULT': '3px',
        '0': '0px',
        '1': '1px',
        '2': '2px',
        '4': '4px',
        '8': '8px',
        'inset': 'inset',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'ring':
            return False
        if token.modifier == 'offset':
            return False
        return token.value in self.STATIC_VALUES or not token.value or token.value_type == ValueType.ARBITRARY
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if not token.value:
            value = self.STATIC_VALUES.get('DEFAULT', '3px')
        else:
            value = self.resolve_value(token, context)
        
        if value is None:
            return None
        
        if value == 'inset':
            return self.create_rule(token, '--tw-ring-inset', 'inset')
        
        return self.create_rule(token, '--tw-ring-width', value)


class TransitionPlugin(UtilityPlugin):
    """Plugin for transition utilities (transition-*)."""
    
    name = "transition"
    prefixes = ["transition"]
    
    STATIC_VALUES = {
        'none': 'none',
        'all': 'all',
        'DEFAULT': 'color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter',
        'colors': 'color, background-color, border-color, text-decoration-color, fill, stroke',
        'opacity': 'opacity',
        'shadow': 'box-shadow',
        'transform': 'transform',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'transition'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if not token.value:
            prop = self.STATIC_VALUES.get('DEFAULT')
        else:
            prop = self.resolve_value(token, context)
        
        if prop is None:
            return None
        
        return self.create_multi_rule(token, {
            'transition-property': prop,
            'transition-timing-function': 'cubic-bezier(0.4, 0, 0.2, 1)',
            'transition-duration': '150ms',
        })


class TransitionDurationPlugin(UtilityPlugin):
    """Plugin for transition-duration utilities (duration-*)."""
    
    name = "transition-duration"
    prefixes = ["duration"]
    
    STATIC_VALUES = {
        '0': '0s',
        '75': '75ms',
        '100': '100ms',
        '150': '150ms',
        '200': '200ms',
        '300': '300ms',
        '500': '500ms',
        '700': '700ms',
        '1000': '1000ms',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'duration'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'transition-duration', value)


class TransitionDelayPlugin(UtilityPlugin):
    """Plugin for transition-delay utilities (delay-*)."""
    
    name = "transition-delay"
    prefixes = ["delay"]
    
    STATIC_VALUES = {
        '0': '0s',
        '75': '75ms',
        '100': '100ms',
        '150': '150ms',
        '200': '200ms',
        '300': '300ms',
        '500': '500ms',
        '700': '700ms',
        '1000': '1000ms',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'delay'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'transition-delay', value)


class TransitionTimingPlugin(UtilityPlugin):
    """Plugin for transition-timing-function utilities (ease-*)."""
    
    name = "transition-timing"
    prefixes = ["ease"]
    
    STATIC_VALUES = {
        'linear': 'linear',
        'in': 'cubic-bezier(0.4, 0, 1, 1)',
        'out': 'cubic-bezier(0, 0, 0.2, 1)',
        'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'ease'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'transition-timing-function', value)


class TransformPlugin(UtilityPlugin):
    """Plugin for transform origin utilities (origin-*)."""
    
    name = "transform-origin"
    prefixes = ["origin"]
    
    STATIC_VALUES = {
        'center': 'center',
        'top': 'top',
        'top-right': 'top right',
        'right': 'right',
        'bottom-right': 'bottom right',
        'bottom': 'bottom',
        'bottom-left': 'bottom left',
        'left': 'left',
        'top-left': 'top left',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'origin'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'transform-origin', value)


class ScalePlugin(UtilityPlugin):
    """Plugin for scale transform utilities (scale-*, scale-x-*, scale-y-*)."""
    
    name = "scale"
    prefixes = ["scale"]
    
    STATIC_VALUES = {
        '0': '0',
        '50': '.5',
        '75': '.75',
        '90': '.9',
        '95': '.95',
        '100': '1',
        '105': '1.05',
        '110': '1.1',
        '125': '1.25',
        '150': '1.5',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'scale':
            return False
        return token.modifier in (None, 'x', 'y')
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        
        if token.modifier == 'x':
            return self.create_rule(token, '--tw-scale-x', value)
        elif token.modifier == 'y':
            return self.create_rule(token, '--tw-scale-y', value)
        else:
            return self.create_multi_rule(token, {
                '--tw-scale-x': value,
                '--tw-scale-y': value,
            })


class RotatePlugin(UtilityPlugin):
    """Plugin for rotate transform utilities (rotate-*)."""
    
    name = "rotate"
    prefixes = ["rotate"]
    
    STATIC_VALUES = {
        '0': '0deg',
        '1': '1deg',
        '2': '2deg',
        '3': '3deg',
        '6': '6deg',
        '12': '12deg',
        '45': '45deg',
        '90': '90deg',
        '180': '180deg',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    @property
    def supports_negative(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'rotate'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, '--tw-rotate', value)


class TranslatePlugin(UtilityPlugin):
    """Plugin for translate transform utilities (translate-x-*, translate-y-*)."""
    
    name = "translate"
    prefixes = ["translate"]
    
    STATIC_VALUES = {
        'full': '100%',
        '1/2': '50%',
        '1/3': '33.333333%',
        '2/3': '66.666667%',
        '1/4': '25%',
        '3/4': '75%',
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
        if token.utility != 'translate':
            return False
        return token.modifier in ('x', 'y')
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        
        if token.modifier == 'x':
            return self.create_rule(token, '--tw-translate-x', value)
        else:  # y
            return self.create_rule(token, '--tw-translate-y', value)


class CursorPlugin(UtilityPlugin):
    """Plugin for cursor utilities (cursor-*)."""
    
    name = "cursor"
    prefixes = ["cursor"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'default': 'default',
        'pointer': 'pointer',
        'wait': 'wait',
        'text': 'text',
        'move': 'move',
        'help': 'help',
        'not-allowed': 'not-allowed',
        'none': 'none',
        'context-menu': 'context-menu',
        'progress': 'progress',
        'cell': 'cell',
        'crosshair': 'crosshair',
        'vertical-text': 'vertical-text',
        'alias': 'alias',
        'copy': 'copy',
        'no-drop': 'no-drop',
        'grab': 'grab',
        'grabbing': 'grabbing',
        'all-scroll': 'all-scroll',
        'col-resize': 'col-resize',
        'row-resize': 'row-resize',
        'n-resize': 'n-resize',
        'e-resize': 'e-resize',
        's-resize': 's-resize',
        'w-resize': 'w-resize',
        'ne-resize': 'ne-resize',
        'nw-resize': 'nw-resize',
        'se-resize': 'se-resize',
        'sw-resize': 'sw-resize',
        'ew-resize': 'ew-resize',
        'ns-resize': 'ns-resize',
        'nesw-resize': 'nesw-resize',
        'nwse-resize': 'nwse-resize',
        'zoom-in': 'zoom-in',
        'zoom-out': 'zoom-out',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'cursor'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'cursor', value)


class AnimationPlugin(UtilityPlugin):
    """Plugin for animation utilities (animate-*)."""
    
    name = "animation"
    prefixes = ["animate"]
    
    STATIC_VALUES = {
        'none': 'none',
        'spin': 'spin 1s linear infinite',
        'ping': 'ping 1s cubic-bezier(0, 0, 0.2, 1) infinite',
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce': 'bounce 1s infinite',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'animate'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'animation', value)


class FilterBlurPlugin(UtilityPlugin):
    """Plugin for blur filter utilities (blur-*)."""
    
    name = "blur"
    prefixes = ["blur"]
    
    STATIC_VALUES = {
        'none': 'blur(0)',
        'sm': 'blur(4px)',
        'DEFAULT': 'blur(8px)',
        'md': 'blur(12px)',
        'lg': 'blur(16px)',
        'xl': 'blur(24px)',
        '2xl': 'blur(40px)',
        '3xl': 'blur(64px)',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'blur'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if not token.value:
            value = self.STATIC_VALUES.get('DEFAULT')
        else:
            value = self.resolve_value(token, context)
        
        if value is None:
            return None
        
        # Wrap arbitrary values in blur()
        if token.value_type == ValueType.ARBITRARY and not value.startswith('blur('):
            value = f'blur({value})'
        
        return self.create_rule(token, 'filter', value)


def get_plugins() -> List[UtilityPlugin]:
    """Get all effects-related plugins."""
    return [
        OpacityPlugin(),
        BoxShadowPlugin(),
        BorderRadiusPlugin(),
        BorderWidthPlugin(),
        DivideWidthPlugin(),
        RingWidthPlugin(),
        TransitionPlugin(),
        TransitionDurationPlugin(),
        TransitionDelayPlugin(),
        TransitionTimingPlugin(),
        TransformPlugin(),
        ScalePlugin(),
        RotatePlugin(),
        TranslatePlugin(),
        CursorPlugin(),
        AnimationPlugin(),
        FilterBlurPlugin(),
    ]
