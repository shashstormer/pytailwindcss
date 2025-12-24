"""
Tailwind CSS class string parser.

This module provides a proper tokenizer for Tailwind class strings,
breaking them into structured components (variants, utility, value, etc.)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum
import re


class ValueType(Enum):
    """Type of value in a Tailwind class."""
    STATIC = "static"        # Predefined value like "red-500"
    ARBITRARY = "arbitrary"  # Dynamic value like "[100px]"
    FRACTION = "fraction"    # Fractional value like "1/2"


@dataclass
class TailwindToken:
    """
    Parsed representation of a Tailwind class string.
    
    Example: "hover:md:bg-red-500/50" becomes:
        raw="hover:md:bg-red-500/50"
        variants=["hover", "md"]
        utility="bg"
        value="red-500"
        value_type=ValueType.STATIC
        opacity=50
        is_negative=False
    """
    raw: str                                          # Original class string
    variants: List[str] = field(default_factory=list) # hover, md, dark, etc.
    utility: str = ""                                 # w, bg, text, etc.
    modifier: Optional[str] = None                    # x, y, t, r, etc. (directional)
    value: str = ""                                   # 4, red-500, [100px], etc.
    value_type: ValueType = ValueType.STATIC
    opacity: Optional[int] = None                     # /50 -> 50
    is_negative: bool = False                         # -mt-4 -> True
    
    @property
    def full_utility(self) -> str:
        """Get utility with modifier combined (e.g., 'px', 'mt')."""
        if self.modifier:
            return f"{self.utility}-{self.modifier}"
        return self.utility
    
    @property
    def value_parts(self) -> List[str]:
        """Split value by hyphen, respecting brackets."""
        return _split_by_hyphen(self.value)


class ClassParser:
    """
    Tokenizer for Tailwind CSS class strings.
    
    Handles parsing of complex class strings including:
    - Variants: hover:, md:, dark:, group-hover:, etc.
    - Arbitrary values: [100px], [#ff0000], [calc(100%-20px)]
    - Opacity modifiers: /50, /75
    - Negative values: -mt-4, -translate-x-1/2
    - Fractions: w-1/2, translate-x-1/2
    """
    
    # Pattern for extracting opacity modifier at the end
    OPACITY_PATTERN = re.compile(r'^(.+)/(\d+)$')
    
    # Common utility prefixes that help identify where utility starts
    UTILITY_PREFIXES = {
        # Spacing
        'p', 'px', 'py', 'pt', 'pr', 'pb', 'pl', 'ps', 'pe',
        'm', 'mx', 'my', 'mt', 'mr', 'mb', 'ml', 'ms', 'me',
        'w', 'h', 'min-w', 'min-h', 'max-w', 'max-h', 'size',
        # Layout
        'flex', 'grid', 'block', 'inline', 'hidden',
        'absolute', 'relative', 'fixed', 'sticky', 'static',
        'top', 'right', 'bottom', 'left', 'inset',
        'z', 'order',
        # Flexbox/Grid
        # Flexbox/Grid
        'basis', 'grow', 'shrink',
        'gap',
        'col',
        'row',
        'grid-cols', 'grid-rows', 'auto-cols', 'auto-rows',
        'grid-flow',
        'justify', 'justify-items', 'justify-self',
        'items', 'content', 'self',
        'place', 'place-content', 'place-items', 'place-self',
        # Typography
        'text', 'font', 'leading', 'tracking', 'indent',
        'align', 'whitespace', 'break', 'hyphens',
        'decoration', 'underline-offset',
        # Colors
        'bg', 'from', 'via', 'to',
        'border', 'divide', 'outline', 'ring', 'ring-offset',
        'shadow', 'accent', 'caret',
        'fill', 'stroke',
        # Effects
        'opacity', 'mix-blend', 'bg-blend',
        'blur', 'brightness', 'contrast', 'grayscale',
        'hue-rotate', 'invert', 'saturate', 'sepia',
        'drop-shadow', 'backdrop',
        # Transforms
        'scale', 'rotate', 'translate', 'translate-x', 'translate-y',
        'skew', 'skew-x', 'skew-y', 'origin',
        # Transitions
        'transition', 'duration', 'delay', 'ease', 'animate',
        # Borders
        'rounded', 'border-x', 'border-y', 'border-t', 'border-r', 'border-b', 'border-l',
        'border-s', 'border-e',
        'divide-x', 'divide-y',
        # Other
        'aspect', 'container', 'columns', 'object', 'overflow',
        'overscroll', 'scroll', 'snap', 'touch', 'select',
        'will-change', 'cursor', 'pointer-events', 'resize',
        'appearance', 'list', 'sr',
        'space',
        # New Layout Utils
        'break-after', 'break-before', 'break-inside',
        'box', 'box-decoration',
        'float', 'clear', 'isolate', 'isolation',
        'visible', 'invisible', 'collapse',
        'start', 'end',
        'not-sr',
        'auto-cols', 'auto-rows',
    }
    
    def parse(self, class_string: str) -> TailwindToken:
        """
        Parse a single Tailwind class into a structured token.
        
        Args:
            class_string: A single Tailwind class like "hover:bg-red-500/50"
            
        Returns:
            TailwindToken with parsed components
        """
        raw = class_string
        
        # Step 1: Extract opacity modifier (e.g., /50)
        # Be careful not to confuse fractions (w-1/2) with opacity
        # Opacity is only at the end after a valid class pattern
        opacity = None
        opacity_match = self.OPACITY_PATTERN.match(class_string)
        if opacity_match:
            # Check if this looks like a fraction value rather than opacity
            # Fractions typically appear after utilities like w-1/2, not like bg-red-500/50
            before_slash = opacity_match.group(1)
            after_slash = opacity_match.group(2)
            
            # If the part before slash ends with a digit and looks like a fraction, don't treat as opacity
            # e.g., "w-1/2" - the "1" before slash is a fraction numerator
            # vs "bg-red-500/50" - the "500" is a color shade, "/50" is opacity
            if before_slash and before_slash[-1].isdigit():
                # Check if it's a known fraction pattern
                parts = before_slash.rsplit('-', 1)
                # Check for integer or decimal number
                is_number = len(parts) == 2 and re.match(r'^\d+(\.\d+)?$', parts[1])
                if is_number and int(after_slash) <= 12:
                    # Looks like a fraction (e.g., 1/2, 3/4, 1.5/1)
                    pass  # Don't extract opacity
                else:
                    class_string = opacity_match.group(1)
                    try:
                        opacity = int(opacity_match.group(2))
                    except ValueError:
                        pass
            else:
                class_string = opacity_match.group(1)
                try:
                    opacity = int(opacity_match.group(2))
                except ValueError:
                    pass
        
        # Step 2: Extract variants (e.g., hover:, md:, dark:)
        variants, remainder = self._extract_variants(class_string)
        
        # Step 3: Check for negative prefix
        is_negative = False
        if remainder.startswith('-'):
            is_negative = True
            remainder = remainder[1:]
        
        # Step 4: Parse utility and value
        utility, modifier, value, value_type = self._parse_utility_value(remainder)
        
        return TailwindToken(
            raw=raw,
            variants=variants,
            utility=utility,
            modifier=modifier,
            value=value,
            value_type=value_type,
            opacity=opacity,
            is_negative=is_negative,
        )
    
    def parse_many(self, class_strings: List[str]) -> List[TailwindToken]:
        """Parse multiple class strings."""
        return [self.parse(cls) for cls in class_strings]
    
    def _extract_variants(self, class_string: str) -> Tuple[List[str], str]:
        """
        Extract variant prefixes from class string.
        
        "hover:md:bg-red-500" -> (["hover", "md"], "bg-red-500")
        "[mask-type:luminance]" -> ([], "[mask-type:luminance]")  # no split inside brackets
        """
        # If entire class is a bracketed expression, no variants
        if class_string.startswith('[') and class_string.endswith(']'):
            return [], class_string
        
        variants = []
        parts = self._split_by_colon_respecting_brackets(class_string)
        
        if len(parts) == 1:
            return [], class_string
        
        # The last part is the utility, everything before is variants
        remainder = parts[-1]
        variants = parts[:-1]
        
        return variants, remainder
    
    def _split_by_colon_respecting_brackets(self, text: str) -> List[str]:
        """
        Split text by colon, but not inside brackets.
        
        "hover:bg-[#ff0000]" -> ["hover", "bg-[#ff0000]"]
        "[mask-type:luminance]" -> ["[mask-type:luminance]"]
        """
        parts = []
        current = []
        bracket_depth = 0
        
        for char in text:
            if char == '[':
                bracket_depth += 1
            elif char == ']':
                bracket_depth -= 1
            elif char == ':' and bracket_depth == 0:
                parts.append(''.join(current))
                current = []
                continue
            current.append(char)
        
        if current:
            parts.append(''.join(current))
        
        return parts
    
    def _parse_utility_value(self, text: str) -> Tuple[str, Optional[str], str, ValueType]:
        """
        Parse utility name and value from text.
        
        Returns: (utility, modifier, value, value_type)
        
        Examples:
            "bg-red-500" -> ("bg", None, "red-500", STATIC)
            "w-[100px]" -> ("w", None, "[100px]", ARBITRARY)
            "px-4" -> ("p", "x", "4", STATIC)
            "translate-x-1/2" -> ("translate", "x", "1/2", FRACTION)
        """
        if not text:
            return "", None, "", ValueType.STATIC
        
        # Split by hyphen, respecting brackets
        parts = _split_by_hyphen(text)
        
        if not parts:
            return "", None, "", ValueType.STATIC
        
        # Try to find the longest matching utility prefix
        utility, modifier, value_start = self._find_utility(parts)
        
        if value_start >= len(parts):
            # No value, just utility (e.g., "block", "flex")
            value = ""
            value_type = ValueType.STATIC
        else:
            # Reconstruct value from remaining parts
            value_parts = parts[value_start:]
            value = "-".join(value_parts)
            
            # Determine value type
            if value.startswith('[') and value.endswith(']'):
                value_type = ValueType.ARBITRARY
            elif '/' in value and not value.startswith('['):
                value_type = ValueType.FRACTION
            else:
                value_type = ValueType.STATIC
        
        return utility, modifier, value, value_type
    
    def _find_utility(self, parts: List[str]) -> Tuple[str, Optional[str], int]:
        """
        Find the utility prefix in parts list.
        
        Returns: (utility, modifier, value_start_index)
        """
        # Try matching longer prefixes first
        for length in range(min(3, len(parts)), 0, -1):
            candidate = "-".join(parts[:length])
            if candidate in self.UTILITY_PREFIXES:
                # Special Check for modifiers that get swallowed by prefix match
                if candidate in ('inset', 'overscroll', 'gap', 'space') and length < len(parts):
                     next_part = parts[length]
                     if next_part in ('x', 'y'):
                          return candidate, next_part, length + 1
                
                return candidate, None, length
        
        # Check for directional modifiers (px, mx, mt, etc.)
        if len(parts) >= 1:
            first = parts[0]
            
            # Check for common patterns with modifiers
            if first in ('p', 'm') and len(parts) > 1 and parts[1] in ('x', 'y', 't', 'r', 'b', 'l', 's', 'e'):
                return first, parts[1], 2
            
            if first == 'border' and len(parts) > 1 and parts[1] in ('x', 'y', 't', 'r', 'b', 'l', 's', 'e'):
                return first, parts[1], 2
            
            if first == 'divide' and len(parts) > 1 and parts[1] in ('x', 'y'):
                return first, parts[1], 2
            
            if first == 'translate' and len(parts) > 1 and parts[1] in ('x', 'y'):
                return first, parts[1], 2
            
            if first == 'skew' and len(parts) > 1 and parts[1] in ('x', 'y'):
                return first, parts[1], 2
            
            if first == 'scale' and len(parts) > 1 and parts[1] in ('x', 'y'):
                return first, parts[1], 2
            
            if first == 'gap' and len(parts) > 1 and parts[1] in ('x', 'y'):
                return first, parts[1], 2
            
            if first == 'space' and len(parts) > 1 and parts[1] in ('x', 'y'):
                return first, parts[1], 2
            
            if first == 'rounded' and len(parts) > 1 and parts[1] in ('t', 'r', 'b', 'l', 'tl', 'tr', 'bl', 'br', 's', 'e', 'ss', 'se', 'es', 'ee'):
                return first, parts[1], 2
            
            if first == 'inset' and len(parts) > 1 and parts[1] in ('x', 'y'):
                return first, parts[1], 2
            
            if first == 'scroll' and len(parts) > 1 and parts[1] in ('m', 'p', 'mx', 'my', 'px', 'py', 'mt', 'mr', 'mb', 'ml', 'pt', 'pr', 'pb', 'pl'):
                return first, parts[1], 2
            
            if first == 'overscroll' and len(parts) > 1 and parts[1] in ('x', 'y'):
                return first, parts[1], 2
        
        # Default: first part is utility
        if parts:
            return parts[0], None, 1
        
        return "", None, 0


def _split_by_hyphen(text: str) -> List[str]:
    """
    Split text by hyphen, respecting brackets.
    
    "w-[calc(100%-20px)]" -> ["w", "[calc(100%-20px)]"]
    "bg-red-500" -> ["bg", "red", "500"]
    """
    parts = []
    current = []
    bracket_depth = 0
    paren_depth = 0
    
    for char in text:
        if char == '[':
            bracket_depth += 1
            current.append(char)
        elif char == ']':
            if bracket_depth > 0:
                bracket_depth -= 1
            current.append(char)
        elif char == '(':
            paren_depth += 1
            current.append(char)
        elif char == ')':
            if paren_depth > 0:
                paren_depth -= 1
            current.append(char)
        elif char == '-' and bracket_depth == 0 and paren_depth == 0:
            if current:
                parts.append("".join(current))
            current = []
        else:
            current.append(char)
    
    if current:
        parts.append("".join(current))
    
    return parts
