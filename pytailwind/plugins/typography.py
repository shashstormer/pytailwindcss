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
            # Don't match font-(weight:...)
            if token.value.startswith('(') and 'weight:' in token.value:
                return False
            return True
        return False
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        # Handle font-(family-name:--my-font) syntax
        if token.value.startswith('(') and token.value.endswith(')'):
            content = token.value[1:-1]
            if content.startswith('family-name:'):
                var_name = content[12:]
                return self.create_rule(token, 'font-family', f"var({var_name})")
            # Handle plain var case if passed like font-(--my-font)
            if content.startswith('--'):
                return self.create_rule(token, 'font-family', f"var({content})")

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
        if token.value in self.STATIC_VALUES or token.value_type == ValueType.ARBITRARY:
            return True
        # Handle modifiers like text-lg/loose (parsed as FRACTION)
        if token.value_type == ValueType.FRACTION and '/' in token.value:
            parts = token.value.split('/', 1)
            return parts[0] in self.STATIC_VALUES
        return False
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        # Handle text-(length:...)
        if token.value.startswith('(') and token.value.endswith(')'):
            content = token.value[1:-1]
            if content.startswith('length:'):
                var_name = content[7:]
                return self.create_rule(token, 'font-size', f"var({var_name})")

        font_size = None
        line_height = None

        if token.value in self.STATIC_VALUES:
            font_size, line_height = self.STATIC_VALUES[token.value]
        elif token.value_type == ValueType.ARBITRARY:
            font_size = token.value[1:-1] if token.value.startswith('[') else token.value
            font_size = self._replace_underscores(font_size)
        elif token.value_type == ValueType.FRACTION:
            # Handle text-lg/loose (where slash is part of value because not numeric)
            if '/' in token.value:
                parts = token.value.split('/', 1)
                size_part = parts[0]
                lh_part = parts[1]

                print(f"DEBUG: FRACTION size_part={size_part} lh_part={lh_part}")

                if size_part in self.STATIC_VALUES:
                    font_size, _ = self.STATIC_VALUES[size_part]
                    # Override line height
                    line_height = lh_part # Temporary storage

                    # Try to resolve lh_part
                    lh_val = context.resolve_spacing(lh_part)
                    if lh_val:
                        line_height = lh_val
                    else:
                        # Check line-height static values?
                        # Or generic static values?
                        # LineHeightPlugin has static values.
                        # Maybe we can access them? Or duplicate?
                        # Let's assume it's spacing or raw for now.
                        # Wait, 'loose' is in LineHeightPlugin.
                        # We can try to look it up there or just pass through if not found in spacing.
                        # Ideally we should look up in theme('lineHeight').
                        lh_theme = context.resolve_class_value('lineHeight', lh_part)
                        if lh_theme:
                            line_height = lh_theme
                        else:
                            # Try with lowercase key if camelCase failed?
                            lh_theme = context.resolve_class_value('line-height', lh_part)
                            if lh_theme:
                                line_height = lh_theme

        # Handle line-height modifier (e.g. text-sm/6)
        # Parser puts the modifier in token.opacity if it looks like a number
        if font_size:
            declarations = {'font-size': font_size}

            # Apply line-height modifier if present (numeric opacity OR from fraction split above)
            if token.opacity is not None:
                # Resolve from spacing scale
                lh_key = str(token.opacity)
                lh_val = context.resolve_spacing(lh_key)
                if lh_val:
                    declarations['line-height'] = lh_val
                else:
                    # Maybe it's a raw number or unitless?
                    declarations['line-height'] = lh_key
            elif line_height:
                declarations['line-height'] = line_height

            return self.create_multi_rule(token, declarations)
        
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
        # Handle font-(weight:...)
        if token.value.startswith('(') and token.value.endswith(')'):
            content = token.value[1:-1]
            if content.startswith('weight:'):
                var_name = content[7:]
                return self.create_rule(token, 'font-weight', f"var({var_name})")

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
    prefixes = ["underline", "overline", "line-through", "no-underline", "line"]
    
    STATIC_VALUES = {
        'underline': 'underline',
        'overline': 'overline',
        'line-through': 'line-through',
        'no-underline': 'none',
    }
    
    def match(self, token: TailwindToken) -> bool:
        full = token.raw.split(':')[-1]
        if full in self.STATIC_VALUES:
            return True
        # Check against reconstructed utility if parsed split
        reconstructed = f"{token.utility}-{token.value}" if token.value else token.utility
        return reconstructed in self.STATIC_VALUES
    
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
        # Don't match list-image-*
        if token.value and token.value.startswith('image'):
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


class TextDecorationStylePlugin(UtilityPlugin):
    """Plugin for text-decoration-style utilities (decoration-solid, etc.)."""

    name = "text-decoration-style"
    prefixes = ["decoration"]

    STATIC_VALUES = {
        'solid': 'solid',
        'double': 'double',
        'dotted': 'dotted',
        'dashed': 'dashed',
        'wavy': 'wavy',
    }

    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'decoration':
            return False
        return token.value in self.STATIC_VALUES

    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'text-decoration-style', self.STATIC_VALUES[token.value])
        return None


class TextDecorationThicknessPlugin(UtilityPlugin):
    """Plugin for text-decoration-thickness utilities (decoration-2, decoration-[3px])."""

    name = "text-decoration-thickness"
    prefixes = ["decoration"]

    STATIC_VALUES = {
        'auto': 'auto',
        'from-font': 'from-font',
        '0': '0px',
        '1': '1px',
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
        if token.utility != 'decoration':
            return False
        if token.value in self.STATIC_VALUES:
            return True

        # Check arbitrary values
        if token.value_type == ValueType.ARBITRARY:
            inner = token.value[1:-1]

            # Reject colors
            if inner.startswith(('#', 'rgb', 'hsl', 'color', 'oklch', 'oklab', 'lab', 'lch')):
                return False

            # Accept if it looks like length, percentage, calc, or number
            if inner[0].isdigit() or inner.startswith(('calc(', 'var(')):
                return True

        return False

    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'text-decoration-thickness', value)


class TextUnderlineOffsetPlugin(UtilityPlugin):
    """Plugin for text-underline-offset utilities (underline-offset-*)."""

    name = "text-underline-offset"
    prefixes = ["underline-offset"]

    STATIC_VALUES = {
        'auto': 'auto',
        '0': '0px',
        '1': '1px',
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
        return token.utility == 'underline-offset'

    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'text-underline-offset', value)


class ContentPlugin(UtilityPlugin):
    """Plugin for content utilities (content-*)."""

    name = "content"
    prefixes = ["content"]

    STATIC_VALUES = {
        'none': 'none',
    }

    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES

    @property
    def supports_arbitrary(self) -> bool:
        return True

    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'content'

    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        # Handle arbitrary content specifically to preserve quotes
        if token.value_type == ValueType.ARBITRARY:
            inner = token.value[1:-1]
            # Replace underscores only outside of quotes is handled by _replace_underscores
            # But for content, we might want to keep underscores inside quotes
            value = self.resolve_value(token, context)
            if value:
                return self.create_rule(token, 'content', value)
            return None

        value = self.resolve_value(token, context)
        if value:
            return self.create_rule(token, 'content', value)
        return None


class HyphensPlugin(UtilityPlugin):
    """Plugin for hyphens utilities (hyphens-*)."""

    name = "hyphens"
    prefixes = ["hyphens"]

    STATIC_VALUES = {
        'none': 'none',
        'manual': 'manual',
        'auto': 'auto',
    }

    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES

    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'hyphens'

    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value:
            return self.create_rule(token, 'hyphens', value)
        return None


class TextWrapPlugin(UtilityPlugin):
    """Plugin for text-wrap utilities (text-wrap, text-nowrap, etc.)."""

    name = "text-wrap"
    prefixes = ["text"]

    STATIC_VALUES = {
        'wrap': 'wrap',
        'nowrap': 'nowrap',
        'balance': 'balance',
        'pretty': 'pretty',
    }

    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'text':
            return False
        return token.value in self.STATIC_VALUES

    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'text-wrap', self.STATIC_VALUES[token.value])
        return None


class FontVariantNumericPlugin(UtilityPlugin):
    """Plugin for font-variant-numeric utilities."""

    name = "font-variant-numeric"
    # These are top-level utility names, not prefixes
    prefixes = [
        "normal-nums", "ordinal", "slashed-zero", "lining-nums",
        "oldstyle-nums", "proportional-nums", "tabular-nums",
        "diagonal-fractions", "stacked-fractions",
        "normal", "slashed", "lining", "oldstyle", "proportional", "tabular", "diagonal", "stacked"
    ]

    STATIC_VALUES = {
        'normal-nums': 'normal',
        'ordinal': 'ordinal',
        'slashed-zero': 'slashed-zero',
        'lining-nums': 'lining-nums',
        'oldstyle-nums': 'oldstyle-nums',
        'proportional-nums': 'proportional-nums',
        'tabular-nums': 'tabular-nums',
        'diagonal-fractions': 'diagonal-fractions',
        'stacked-fractions': 'stacked-fractions',
    }

    def match(self, token: TailwindToken) -> bool:
        # Check against full token value (since these are utilities themselves)
        if token.utility in self.STATIC_VALUES:
            return True
        # Try reconstructed
        reconstructed = f"{token.utility}-{token.value}" if token.value else token.utility
        return reconstructed in self.STATIC_VALUES

    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.utility in self.STATIC_VALUES:
            return self.create_rule(token, 'font-variant-numeric', self.STATIC_VALUES[token.utility])

        reconstructed = f"{token.utility}-{token.value}" if token.value else token.utility
        if reconstructed in self.STATIC_VALUES:
            # Create a rule using reconstructed utility as class name if necessary,
            # BUT wait, create_rule uses token.raw.
            # So we just need the value.
            return self.create_rule(token, 'font-variant-numeric', self.STATIC_VALUES[reconstructed])
        return None


class LineClampPlugin(UtilityPlugin):
    """Plugin for line-clamp utilities (line-clamp-*)."""

    name = "line-clamp"
    prefixes = ["line-clamp", "line"]

    @property
    def supports_arbitrary(self) -> bool:
        return True

    def match(self, token: TailwindToken) -> bool:
        if token.utility == 'line-clamp':
            return True
        # Handle split case: utility=line, value=clamp-none or something?
        # No, "line-clamp-none" -> utility="line", value="clamp-none" is unlikely.
        # "line-clamp-none" -> "line", "clamp", "none".
        # Parser splits by hyphen.
        # If parser produces utility="line", value="clamp-none".
        # We need to check if full string starts with line-clamp.
        if token.utility == 'line' and token.value and token.value.startswith('clamp'):
            return True
        return False

    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        # Handle parsed value being 'clamp-none' or 'clamp-2' if utility was split
        value_str = token.value
        if value_str and value_str.startswith('clamp-'):
            value_str = value_str[6:]

        if value_str == 'none':
            return self.create_multi_rule(token, {
                'overflow': 'visible',
                'display': 'block',
                '-webkit-box-orient': 'horizontal',
                '-webkit-line-clamp': 'none',
            })

        value = None
        if value_str and value_str.isdigit():
            value = value_str
        elif token.value_type == ValueType.ARBITRARY:
            value = token.value[1:-1]
        elif value_str and value_str.startswith('[') and value_str.endswith(']'):
            value = value_str[1:-1]

        if value:
            return self.create_multi_rule(token, {
                'overflow': 'hidden',
                'display': '-webkit-box',
                '-webkit-box-orient': 'vertical',
                '-webkit-line-clamp': value,
            })

        return None


class ListStyleImagePlugin(UtilityPlugin):
    """Plugin for list-style-image utilities (list-image-*)."""

    name = "list-style-image"
    prefixes = ["list-image", "list"]

    STATIC_VALUES = {
        'none': 'none',
    }

    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES

    @property
    def supports_arbitrary(self) -> bool:
        return True

    def match(self, token: TailwindToken) -> bool:
        if token.utility == 'list-image':
            return True
        if token.utility == 'list' and token.value and token.value.startswith('image'):
            return True
        return False

    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        # Handle parsed value being 'image-none' or 'image-[...]' if utility was split
        value_str = token.value
        if value_str and value_str.startswith('image-'):
            # This handles "list-image-none" -> value="image-none"
            # We want to pass "none" to resolve_value
            # But resolve_value uses token.value directly.
            # We should probably mutate a copy of token or rely on arbitary value parsing logic in resolve_value.
            # resolve_value handles STATIC_VALUES. 'none' is static.
            # 'image-none' is not static.

            # Create a temporary token with corrected value
            from dataclasses import replace
            stripped_value = value_str[6:]

            # Update value_type if stripped value is arbitrary
            new_value_type = token.value_type
            if stripped_value.startswith('[') and stripped_value.endswith(']'):
                new_value_type = ValueType.ARBITRARY

            token = replace(token, value=stripped_value, value_type=new_value_type)

        value = self.resolve_value(token, context)
        if value:
            return self.create_rule(token, 'list-style-image', value)
        return None


class FontSmoothingPlugin(UtilityPlugin):
    """Plugin for font-smoothing utilities (antialiased, subpixel-antialiased)."""

    name = "font-smoothing"
    prefixes = ["antialiased", "subpixel-antialiased", "subpixel"]

    def match(self, token: TailwindToken) -> bool:
        if token.utility in ('antialiased', 'subpixel-antialiased'):
            return True
        if token.utility == 'subpixel' and token.value == 'antialiased':
            return True
        return False

    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        utility = token.utility
        if utility == 'subpixel' and token.value == 'antialiased':
            utility = 'subpixel-antialiased'

        if utility == 'antialiased':
            return self.create_multi_rule(token, {
                '-webkit-font-smoothing': 'antialiased',
                '-moz-osx-font-smoothing': 'grayscale',
            })
        elif utility == 'subpixel-antialiased':
            return self.create_multi_rule(token, {
                '-webkit-font-smoothing': 'auto',
                '-moz-osx-font-smoothing': 'auto',
            })
        return None


class FontStretchPlugin(UtilityPlugin):
    """Plugin for font-stretch utilities (font-condensed, font-expanded, etc.)."""

    name = "font-stretch"
    prefixes = ["font-stretch", "font"]

    STATIC_VALUES = {
        'normal': 'normal',
        'ultra-condensed': 'ultra-condensed',
        'extra-condensed': 'extra-condensed',
        'condensed': 'condensed',
        'semi-condensed': 'semi-condensed',
        'semi-expanded': 'semi-expanded',
        'expanded': 'expanded',
        'extra-expanded': 'extra-expanded',
        'ultra-expanded': 'ultra-expanded',
    }

    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES

    @property
    def supports_arbitrary(self) -> bool:
        return True

    def match(self, token: TailwindToken) -> bool:
        if token.utility == 'font-stretch':
            return True
        # Handle parsed utility 'font' and value 'stretch-*'
        if token.utility == 'font' and token.value and token.value.startswith('stretch-'):
            return True
        return False

    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        # Handle parsed value being 'stretch-expanded' if utility was split
        value_str = token.value
        if value_str and value_str.startswith('stretch-'):
            from dataclasses import replace
            stripped_value = value_str[8:]

            # Update value_type if stripped value is arbitrary
            new_value_type = token.value_type
            if stripped_value.startswith('[') and stripped_value.endswith(']'):
                new_value_type = ValueType.ARBITRARY
            # Handle percentage values like '50%'
            elif stripped_value.endswith('%'):
                new_value_type = ValueType.ARBITRARY

            token = replace(token, value=stripped_value, value_type=new_value_type)

        # Also check original token value for percentages if it wasn't split (e.g. font-stretch-50% -> utility=font-stretch, value=50%)
        elif token.value and token.value.endswith('%'):
             from dataclasses import replace
             token = replace(token, value_type=ValueType.ARBITRARY)

        value = self.resolve_value(token, context)
        # Fallback: if value is a percentage string, use it directly even if resolve_value failed (e.g. if it wasn't marked arbitrary properly)
        if value is None and token.value and token.value.endswith('%'):
            value = token.value

        if value is None:
            return None
        return self.create_rule(token, 'font-stretch', value)


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
        TextDecorationStylePlugin(),
        TextDecorationThicknessPlugin(),
        TextUnderlineOffsetPlugin(),
        ContentPlugin(),
        HyphensPlugin(),
        TextWrapPlugin(),
        FontVariantNumericPlugin(),
        LineClampPlugin(),
        ListStyleImagePlugin(),
        FontSmoothingPlugin(),
        FontStretchPlugin(),
    ]
