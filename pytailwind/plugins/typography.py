"""
Typography utility plugins.

Includes: font family, font size, font weight, text alignment, etc.
"""

from typing import List, Optional, Dict, Any
from .base import UtilityPlugin, GeneratorContext
from ..parser import TailwindToken, ValueType
from ..ast import Rule


class FontFamilyPlugin(UtilityPlugin):
    """Plugin for font-family utilities (font-sans, font-serif, font-mono)."""
    
    name = "font-family"
    prefixes = ["font"]
    
    STATIC_VALUES = {
        'sans': 'ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
        'serif': 'ui-serif, Georgia, Cambria, "Times New Roman", Times, serif',
        'mono': 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'font':
            return False
        # Match font family values, not font weights
        if token.value in self.STATIC_VALUES:
            return True
        if token.value_type == ValueType.ARBITRARY:
            return True
        return False
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'font-family', value)


class FontSizePlugin(UtilityPlugin):
    """Plugin for font-size utilities (text-xs, text-sm, text-base, etc.)."""
    
    name = "font-size"
    prefixes = ["text"]
    
    # Value: [font-size, line-height]
    STATIC_VALUES = {
        'xs': ('0.75rem', '1rem'),
        'sm': ('0.875rem', '1.25rem'),
        'base': ('1rem', '1.5rem'),
        'lg': ('1.125rem', '1.75rem'),
        'xl': ('1.25rem', '1.75rem'),
        '2xl': ('1.5rem', '2rem'),
        '3xl': ('1.875rem', '2.25rem'),
        '4xl': ('2.25rem', '2.5rem'),
        '5xl': ('3rem', '1'),
        '6xl': ('3.75rem', '1'),
        '7xl': ('4.5rem', '1'),
        '8xl': ('6rem', '1'),
        '9xl': ('8rem', '1'),
    }
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'text':
            return False
        return token.value in self.STATIC_VALUES or token.value_type == ValueType.ARBITRARY
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            font_size, line_height = self.STATIC_VALUES[token.value]
            return self.create_multi_rule(token, {
                'font-size': font_size,
                'line-height': line_height,
            })
        
        if token.value_type == ValueType.ARBITRARY:
            inner = token.value[1:-1] if token.value.startswith('[') else token.value
            inner = self._replace_underscores(inner)
            return self.create_rule(token, 'font-size', inner)
        
        return None


class FontWeightPlugin(UtilityPlugin):
    """Plugin for font-weight utilities (font-thin, font-bold, etc.)."""
    
    name = "font-weight"
    prefixes = ["font"]
    
    STATIC_VALUES = {
        'thin': '100',
        'extralight': '200',
        'light': '300',
        'normal': '400',
        'medium': '500',
        'semibold': '600',
        'bold': '700',
        'extrabold': '800',
        'black': '900',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'font':
            return False
        return token.value in self.STATIC_VALUES or token.value_type == ValueType.ARBITRARY
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'font-weight', value)


class FontStylePlugin(UtilityPlugin):
    """Plugin for font-style utilities (italic, not-italic)."""
    
    name = "font-style"
    prefixes = ["italic", "not-italic"]
    
    STATIC_VALUES = {
        'italic': 'italic',
        'not-italic': 'normal',
    }
    
    def match(self, token: TailwindToken) -> bool:
        full = token.raw.split(':')[-1]
        return full in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        full = token.raw.split(':')[-1]
        if full in self.STATIC_VALUES:
            return self.create_rule(token, 'font-style', self.STATIC_VALUES[full])
        return None


class TextAlignPlugin(UtilityPlugin):
    """Plugin for text-align utilities (text-left, text-center, etc.)."""
    
    name = "text-align"
    prefixes = ["text"]
    
    STATIC_VALUES = {
        'left': 'left',
        'center': 'center',
        'right': 'right',
        'justify': 'justify',
        'start': 'start',
        'end': 'end',
    }
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'text':
            return False
        return token.value in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'text-align', self.STATIC_VALUES[token.value])
        return None


class LineHeightPlugin(UtilityPlugin):
    """Plugin for line-height utilities (leading-*)."""
    
    name = "line-height"
    prefixes = ["leading"]
    
    STATIC_VALUES = {
        '3': '.75rem',
        '4': '1rem',
        '5': '1.25rem',
        '6': '1.5rem',
        '7': '1.75rem',
        '8': '2rem',
        '9': '2.25rem',
        '10': '2.5rem',
        'none': '1',
        'tight': '1.25',
        'snug': '1.375',
        'normal': '1.5',
        'relaxed': '1.625',
        'loose': '2',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'leading'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'line-height', value)


class LetterSpacingPlugin(UtilityPlugin):
    """Plugin for letter-spacing utilities (tracking-*)."""
    
    name = "letter-spacing"
    prefixes = ["tracking"]
    
    STATIC_VALUES = {
        'tighter': '-0.05em',
        'tight': '-0.025em',
        'normal': '0em',
        'wide': '0.025em',
        'wider': '0.05em',
        'widest': '0.1em',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'tracking'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'letter-spacing', value)


class TextDecorationPlugin(UtilityPlugin):
    """Plugin for text-decoration utilities (underline, line-through, no-underline)."""
    
    name = "text-decoration"
    prefixes = ["underline", "overline", "line-through", "no-underline"]
    
    STATIC_VALUES = {
        'underline': 'underline',
        'overline': 'overline',
        'line-through': 'line-through',
        'no-underline': 'none',
    }
    
    def match(self, token: TailwindToken) -> bool:
        full = token.raw.split(':')[-1]
        return full in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        full = token.raw.split(':')[-1]
        if full in self.STATIC_VALUES:
            return self.create_rule(token, 'text-decoration-line', self.STATIC_VALUES[full])
        return None


class TextTransformPlugin(UtilityPlugin):
    """Plugin for text-transform utilities (uppercase, lowercase, capitalize, normal-case)."""
    
    name = "text-transform"
    prefixes = ["uppercase", "lowercase", "capitalize", "normal-case"]
    
    STATIC_VALUES = {
        'uppercase': 'uppercase',
        'lowercase': 'lowercase',
        'capitalize': 'capitalize',
        'normal-case': 'none',
    }
    
    def match(self, token: TailwindToken) -> bool:
        full = token.raw.split(':')[-1]
        return full in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        full = token.raw.split(':')[-1]
        if full in self.STATIC_VALUES:
            return self.create_rule(token, 'text-transform', self.STATIC_VALUES[full])
        return None


class TextOverflowPlugin(UtilityPlugin):
    """Plugin for text-overflow utilities (truncate, text-ellipsis, text-clip)."""
    
    name = "text-overflow"
    prefixes = ["truncate", "text"]
    
    def match(self, token: TailwindToken) -> bool:
        full = token.raw.split(':')[-1]
        if full == 'truncate':
            return True
        if token.utility == 'text' and token.value in ('ellipsis', 'clip'):
            return True
        return False
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        full = token.raw.split(':')[-1]
        
        if full == 'truncate':
            return self.create_multi_rule(token, {
                'overflow': 'hidden',
                'text-overflow': 'ellipsis',
                'white-space': 'nowrap',
            })
        
        if token.value == 'ellipsis':
            return self.create_rule(token, 'text-overflow', 'ellipsis')
        
        if token.value == 'clip':
            return self.create_rule(token, 'text-overflow', 'clip')
        
        return None


class WhitespacePlugin(UtilityPlugin):
    """Plugin for whitespace utilities (whitespace-*)."""
    
    name = "whitespace"
    prefixes = ["whitespace"]
    
    STATIC_VALUES = {
        'normal': 'normal',
        'nowrap': 'nowrap',
        'pre': 'pre',
        'pre-line': 'pre-line',
        'pre-wrap': 'pre-wrap',
        'break-spaces': 'break-spaces',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'whitespace'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'white-space', self.STATIC_VALUES[token.value])
        return None


class WordBreakPlugin(UtilityPlugin):
    """Plugin for word-break utilities (break-*)."""
    
    name = "word-break"
    prefixes = ["break"]
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'break':
            return False
        return token.value in ('normal', 'words', 'all', 'keep')
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value == 'normal':
            return self.create_multi_rule(token, {
                'overflow-wrap': 'normal',
                'word-break': 'normal',
            })
        if token.value == 'words':
            return self.create_rule(token, 'overflow-wrap', 'break-word')
        if token.value == 'all':
            return self.create_rule(token, 'word-break', 'break-all')
        if token.value == 'keep':
            return self.create_rule(token, 'word-break', 'keep-all')
        return None


class TextIndentPlugin(UtilityPlugin):
    """Plugin for text-indent utilities (indent-*)."""
    
    name = "text-indent"
    prefixes = ["indent"]
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'indent'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'text-indent', value)


class VerticalAlignPlugin(UtilityPlugin):
    """Plugin for vertical-align utilities (align-*)."""
    
    name = "vertical-align"
    prefixes = ["align"]
    
    STATIC_VALUES = {
        'baseline': 'baseline',
        'top': 'top',
        'middle': 'middle',
        'bottom': 'bottom',
        'text-top': 'text-top',
        'text-bottom': 'text-bottom',
        'sub': 'sub',
        'super': 'super',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'align'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'vertical-align', value)


class ListStyleTypePlugin(UtilityPlugin):
    """Plugin for list-style-type utilities (list-*)."""
    
    name = "list-style-type"
    prefixes = ["list"]
    
    STATIC_VALUES = {
        'none': 'none',
        'disc': 'disc',
        'decimal': 'decimal',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'list':
            return False
        # Don't match list-inside, list-outside
        if token.value in ('inside', 'outside'):
            return False
        return True
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'list-style-type', value)


class ListStylePositionPlugin(UtilityPlugin):
    """Plugin for list-style-position utilities (list-inside, list-outside)."""
    
    name = "list-style-position"
    prefixes = ["list"]
    
    STATIC_VALUES = {
        'inside': 'inside',
        'outside': 'outside',
    }
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'list':
            return False
        return token.value in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'list-style-position', self.STATIC_VALUES[token.value])
        return None


def get_plugins() -> List[UtilityPlugin]:
    """Get all typography-related plugins."""
    return [
        FontFamilyPlugin(),
        FontSizePlugin(),
        FontWeightPlugin(),
        FontStylePlugin(),
        TextAlignPlugin(),
        LineHeightPlugin(),
        LetterSpacingPlugin(),
        TextDecorationPlugin(),
        TextTransformPlugin(),
        TextOverflowPlugin(),
        WhitespacePlugin(),
        WordBreakPlugin(),
        TextIndentPlugin(),
        VerticalAlignPlugin(),
        ListStyleTypePlugin(),
        ListStylePositionPlugin(),
    ]
