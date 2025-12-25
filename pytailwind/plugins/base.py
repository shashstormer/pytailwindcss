"""
Base classes for Tailwind CSS utility plugins.

Plugins are the primary way to extend pytailwindcss with new utilities
or customize existing behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Callable
from ..parser import TailwindToken, ValueType
from ..ast import Rule, Selector, Declaration, escape_css_class


class GeneratorContext:
    """
    Context passed to plugins during CSS generation.
    
    Provides access to configuration values like colors, spacing,
    and utility for resolving theme values.
    """
    
    def __init__(
        self,
        colors: Dict[str, Any],
        spacing: Dict[str, str],
        classes: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ):
        self.colors = colors
        self.spacing = spacing
        self.classes = classes
        self.config = config or {}
        
        # Cache for resolved values
        self._color_cache: Dict[str, str] = {}
    
    def resolve_color(self, *keys: str) -> Optional[str]:
        """
        Resolve color name to hex/rgb value.
        
        Args:
            keys: Path to color, e.g., ("red", "500") or ("white",)
            
        Returns:
            Color value like "#ef4444" or None if not found
        """
        cache_key = "-".join(keys)
        if cache_key in self._color_cache:
            return self._color_cache[cache_key]
        
        current = self.colors
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        if isinstance(current, str):
            self._color_cache[cache_key] = current
            return current
        
        return None
    
    def resolve_spacing(self, key: str) -> Optional[str]:
        """
        Resolve spacing key to CSS value.
        
        Args:
            key: Spacing key like "4", "px", "0.5"
            
        Returns:
            CSS value like "1rem" or "1px"
        """
        return self.spacing.get(key)
    
    def resolve_class_value(self, group: str, *keys: str) -> Optional[Any]:
        """
        Resolve a value from the classes dictionary.
        
        Args:
            group: Group name like "borderRadius", "fontSize"
            keys: Path to value like ("lg",) or ("x", "4")
            
        Returns:
            The value or None if not found
        """
        if group not in self.classes:
            return None
        
        current = self.classes[group]
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def get_css_property(self, group: str, to_css_name: Dict[str, str]) -> str:
        """Get CSS property name for a group."""
        return to_css_name.get(group, group)


class UtilityPlugin(ABC):
    """
    Base class for Tailwind utility plugins.
    
    To create a new utility:
    1. Subclass UtilityPlugin
    2. Define `name` and `prefixes`
    3. Implement `match()` and `generate()`
    4. Register with PluginRegistry
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier."""
        ...
    
    @property
    @abstractmethod
    def prefixes(self) -> List[str]:
        """
        Tailwind prefixes this plugin handles.
        
        Example: ["w", "width"] for width utilities
        """
        ...
    
    @property
    def css_property(self) -> Optional[str]:
        """
        CSS property to generate. 
        
        Override for simple single-property utilities.
        Return None for complex utilities that need custom generation.
        """
        return None
    
    @property
    def static_values(self) -> Dict[str, str]:
        """
        Static value mappings.
        
        Override to provide predefined value -> CSS value mappings.
        Example: {"auto": "auto", "full": "100%"}
        """
        return {}
    
    @property  
    def supports_arbitrary(self) -> bool:
        """Whether this utility supports arbitrary values like [100px]."""
        return True
    
    @property
    def supports_negative(self) -> bool:
        """Whether this utility supports negative values like -mt-4."""
        return False
    
    @property
    def supports_spacing(self) -> bool:
        """Whether this utility uses the spacing scale."""
        return False
    
    @property
    def supports_colors(self) -> bool:
        """Whether this utility uses color values."""
        return False
    
    @abstractmethod
    def match(self, token: TailwindToken) -> bool:
        """
        Returns True if this plugin handles the given token.
        
        Called by the registry to find the right plugin.
        """
        ...
    
    @abstractmethod
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        """
        Generate CSS rule for the given token.
        
        Args:
            token: Parsed Tailwind class token
            context: Generator context with theme values
            
        Returns:
            CSS Rule or None if cannot generate
        """
        ...
    
    # Helper methods for common patterns
    
    def create_rule(self, token: TailwindToken, property: str, value: str) -> Rule:
        """Create a simple rule with one property."""
        selector = Selector(base=f".{escape_css_class(token.raw)}")
        return Rule(
            selector=selector,
            declarations=[Declaration(property=property, value=value)]
        )
    
    def create_multi_rule(self, token: TailwindToken, properties: Dict[str, str]) -> Rule:
        """Create a rule with multiple properties."""
        selector = Selector(base=f".{escape_css_class(token.raw)}")
        declarations = [Declaration(property=p, value=v) for p, v in properties.items()]
        return Rule(selector=selector, declarations=declarations)
    
    def resolve_value(self, token: TailwindToken, context: GeneratorContext) -> Optional[str]:
        """
        Resolve token value to CSS value using common patterns.
        
        Checks in order:
        1. Arbitrary values [...]
        2. Static values from self.static_values
        3. Spacing scale (if supports_spacing)
        4. Color scale (if supports_colors)
        """
        if not token.value:
            # Check for DEFAULT value
            default = self.static_values.get("DEFAULT")
            if default:
                return default
            return None
        
        # Arbitrary value
        if token.value_type == ValueType.ARBITRARY:
            if self.supports_arbitrary:
                # Strip brackets and process
                if token.value.startswith('[') and token.value.endswith(']'):
                    inner = token.value[1:-1]
                elif token.value.startswith('(') and token.value.endswith(')'):
                    inner = token.value[1:-1]
                    # Auto-wrap vars
                    if inner.startswith('--'):
                        return f"var({inner})"
                else:
                    inner = token.value

                # Replace underscores with spaces (Tailwind convention)
                inner = self._replace_underscores(inner)
                return inner
            return None
        
        # Static value
        if token.value in self.static_values:
            return self.static_values[token.value]
        
        # Spacing scale
        if self.supports_spacing:
            spacing_value = context.resolve_spacing(token.value)
            if spacing_value:
                if token.is_negative and self.supports_negative:
                    return f"-{spacing_value}"
                return spacing_value
        
        # Color scale
        if self.supports_colors:
            parts = token.value.split('-')
            color_value = context.resolve_color(*parts)
            if color_value:
                return color_value
        
        return None
    
    def _replace_underscores(self, value: str) -> str:
        """Replace underscores with spaces, but not inside quotes or url()."""
        result = []
        quote = None
        in_url = False
        i = 0
        
        while i < len(value):
            char = value[i]
            
            # Check for url(
            if not quote and value[i:i+4].lower() == 'url(':
                in_url = True
                result.append(value[i:i+4])
                i += 4
                continue
            
            # Track quotes
            if char in ('"', "'", '`') and not in_url:
                if quote == char:
                    quote = None
                elif quote is None:
                    quote = char
            
            # Track url() closing
            if in_url and char == ')':
                in_url = False
            
            # Replace underscore if not in quote or url
            if char == '_' and not quote and not in_url:
                result.append(' ')
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result)


class SimpleUtilityPlugin(UtilityPlugin):
    """
    Simplified plugin for utilities with a single CSS property.
    
    Use this for straightforward utilities where:
    - One utility prefix maps to one CSS property
    - Values come from spacing, colors, or static mappings
    """
    
    def __init__(
        self,
        name: str,
        prefixes: List[str],
        css_property: str,
        static_values: Optional[Dict[str, str]] = None,
        supports_spacing: bool = False,
        supports_colors: bool = False,
        supports_arbitrary: bool = True,
        supports_negative: bool = False,
    ):
        self._name = name
        self._prefixes = prefixes
        self._css_property = css_property
        self._static_values = static_values or {}
        self._supports_spacing = supports_spacing
        self._supports_colors = supports_colors
        self._supports_arbitrary = supports_arbitrary
        self._supports_negative = supports_negative
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def prefixes(self) -> List[str]:
        return self._prefixes
    
    @property
    def css_property(self) -> str:
        return self._css_property
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self._static_values
    
    @property
    def supports_spacing(self) -> bool:
        return self._supports_spacing
    
    @property
    def supports_colors(self) -> bool:
        return self._supports_colors
    
    @property
    def supports_arbitrary(self) -> bool:
        return self._supports_arbitrary
    
    @property
    def supports_negative(self) -> bool:
        return self._supports_negative
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility in self._prefixes
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        
        return self.create_rule(token, self._css_property, value)


class DirectionalPlugin(UtilityPlugin):
    """
    Plugin for utilities with directional modifiers (x, y, t, r, b, l).
    
    Examples: padding (px, py, pt, pr, pb, pl), margin, border-width
    """
    
    # Mapping from modifier to CSS property suffixes
    DIRECTIONAL_MAP = {
        None: [''],  # All sides
        'x': ['-left', '-right'],
        'y': ['-top', '-bottom'],
        't': ['-top'],
        'r': ['-right'],
        'b': ['-bottom'],
        'l': ['-left'],
        's': ['-inline-start'],
        'e': ['-inline-end'],
    }
    
    @property
    @abstractmethod
    def css_property_base(self) -> str:
        """Base CSS property name (e.g., 'padding', 'margin')."""
        ...
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility not in self.prefixes:
            return False
        
        # Check if modifier is valid for directional utilities
        if token.modifier and token.modifier not in self.DIRECTIONAL_MAP:
            return False
        
        return True
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        
        suffixes = self.DIRECTIONAL_MAP.get(token.modifier, [''])
        
        properties = {}
        for suffix in suffixes:
            prop = f"{self.css_property_base}{suffix}"
            properties[prop] = value
        
        return self.create_multi_rule(token, properties)
