"""
CSS generator using the new plugin-based architecture.

This module provides the new generation logic that uses the parser,
AST, and plugin system for more maintainable CSS generation.
"""

from typing import Dict, List, Optional, Set
from .parser import ClassParser, TailwindToken
from .ast import (
    Stylesheet, Rule, MediaQuery, Selector, Declaration,
    escape_css_class
)
from .plugins.base import GeneratorContext
from .plugins.registry import PluginRegistry
from .plugins import spacing, colors, layout, typography, effects
from .utils import extract_candidates, split_classes
import re


class CSSGenerator:
    """
    CSS generator using the plugin-based architecture.
    
    This class orchestrates parsing class strings, dispatching to plugins,
    applying variants, and rendering the final CSS.
    """
    
    # Pseudo-class mappings (Tailwind v4 complete)
    PSEUDO_CLASSES = {
        # Interactive states
        'hover': 'hover',
        'focus': 'focus',
        'active': 'active',
        'visited': 'visited',
        'target': 'target',
        'focus-within': 'focus-within',
        'focus-visible': 'focus-visible',
        
        # Child position
        'first': 'first-child',
        'last': 'last-child',
        'only': 'only-child',
        'odd': 'nth-child(odd)',
        'even': 'nth-child(even)',
        'first-of-type': 'first-of-type',
        'last-of-type': 'last-of-type',
        'only-of-type': 'only-of-type',
        
        # Form states
        'disabled': 'disabled',
        'enabled': 'enabled',
        'checked': 'checked',
        'indeterminate': 'indeterminate',
        'default': 'default',
        'optional': 'optional',
        'required': 'required',
        'valid': 'valid',
        'invalid': 'invalid',
        'user-valid': 'user-valid',
        'user-invalid': 'user-invalid',
        'in-range': 'in-range',
        'out-of-range': 'out-of-range',
        'placeholder-shown': 'placeholder-shown',
        'autofill': 'autofill',
        'read-only': 'read-only',
        
        # Other
        'empty': 'empty',
    }
    
    # Negated pseudo-classes
    NEGATED_PSEUDO_CLASSES = {
        'not-first': 'not(:first-child)',
        'not-last': 'not(:last-child)',
        'not-only': 'not(:only-child)',
        'not-disabled': 'not(:disabled)',
        'not-enabled': 'not(:enabled)',
        'not-checked': 'not(:checked)',
        'not-odd': 'not(:nth-child(odd))',
        'not-even': 'not(:nth-child(even))',
    }
    
    # Pseudo-elements
    PSEUDO_ELEMENTS = {
        'before': 'before',
        'after': 'after',
        'first-letter': 'first-letter',
        'first-line': 'first-line',
        'marker': 'marker',
        'selection': 'selection',
        'backdrop': 'backdrop',
        'placeholder': 'placeholder',
        'file': 'file-selector-button',
        'details-content': 'details-content',
    }
    
    # Group variants (require parent selector)
    GROUP_VARIANTS = {
        'group-hover': '.group:hover',
        'group-focus': '.group:focus',
        'group-active': '.group:active',
        'group-visited': '.group:visited',
        'group-disabled': '.group:disabled',
        'group-checked': '.group:checked',
        'group-first': '.group:first-child',
        'group-last': '.group:last-child',
        'group-odd': '.group:nth-child(odd)',
        'group-even': '.group:nth-child(even)',
        'group-focus-within': '.group:focus-within',
        'group-focus-visible': '.group:focus-visible',
    }
    
    # Peer variants (require sibling selector)
    PEER_VARIANTS = {
        'peer-hover': '.peer:hover ~',
        'peer-focus': '.peer:focus ~',
        'peer-active': '.peer:active ~',
        'peer-visited': '.peer:visited ~',
        'peer-disabled': '.peer:disabled ~',
        'peer-checked': '.peer:checked ~',
        'peer-required': '.peer:required ~',
        'peer-invalid': '.peer:invalid ~',
        'peer-valid': '.peer:valid ~',
        'peer-placeholder-shown': '.peer:placeholder-shown ~',
        'peer-first': '.peer:first-child ~',
        'peer-last': '.peer:last-child ~',
        'peer-odd': '.peer:nth-child(odd) ~',
        'peer-even': '.peer:nth-child(even) ~',
        'peer-focus-visible': '.peer:focus-visible ~',
    }
    
    # ARIA attribute variants
    ARIA_VARIANTS = {
        'aria-busy': '[aria-busy="true"]',
        'aria-checked': '[aria-checked="true"]',
        'aria-disabled': '[aria-disabled="true"]',
        'aria-expanded': '[aria-expanded="true"]',
        'aria-hidden': '[aria-hidden="true"]',
        'aria-pressed': '[aria-pressed="true"]',
        'aria-readonly': '[aria-readonly="true"]',
        'aria-required': '[aria-required="true"]',
        'aria-selected': '[aria-selected="true"]',
    }
    
    # State variants
    STATE_VARIANTS = {
        'open': 'is([open], :popover-open, :open)',
        'inert': 'is([inert], [inert] *)',
    }
    
    # Direction variants
    DIRECTION_VARIANTS = {
        'rtl': 'where(:dir(rtl), [dir="rtl"], [dir="rtl"] *)',
        'ltr': 'where(:dir(ltr), [dir="ltr"], [dir="ltr"] *)',
    }
    
    # Media feature variants
    MEDIA_FEATURE_VARIANTS = {
        # Color scheme
        'dark': '(prefers-color-scheme: dark)',
        'light': '(prefers-color-scheme: light)',
        
        # Motion
        'motion-safe': '(prefers-reduced-motion: no-preference)',
        'motion-reduce': '(prefers-reduced-motion: reduce)',
        
        # Contrast
        'contrast-more': '(prefers-contrast: more)',
        'contrast-less': '(prefers-contrast: less)',
        
        # Forced colors
        'forced-colors': '(forced-colors: active)',
        
        # Inverted colors
        'inverted-colors': '(inverted-colors: inverted)',
        
        # Pointer
        'pointer-fine': '(pointer: fine)',
        'pointer-coarse': '(pointer: coarse)',
        'pointer-none': '(pointer: none)',
        'any-pointer-fine': '(any-pointer: fine)',
        'any-pointer-coarse': '(any-pointer: coarse)',
        'any-pointer-none': '(any-pointer: none)',
        
        # Orientation
        'portrait': '(orientation: portrait)',
        'landscape': '(orientation: landscape)',
        
        # Scripting
        'noscript': '(scripting: none)',
        
        # Print
        'print': 'print',
    }
    
    # Container query breakpoints
    CONTAINER_QUERIES = {
        '@3xs': '(width >= 16rem)',
        '@2xs': '(width >= 18rem)',
        '@xs': '(width >= 20rem)',
        '@sm': '(width >= 24rem)',
        '@md': '(width >= 28rem)',
        '@lg': '(width >= 32rem)',
        '@xl': '(width >= 36rem)',
        '@2xl': '(width >= 42rem)',
        '@3xl': '(width >= 48rem)',
        '@4xl': '(width >= 56rem)',
        '@5xl': '(width >= 64rem)',
        '@6xl': '(width >= 72rem)',
        '@7xl': '(width >= 80rem)',
        '@max-3xs': '(width < 16rem)',
        '@max-2xs': '(width < 18rem)',
        '@max-xs': '(width < 20rem)',
        '@max-sm': '(width < 24rem)',
        '@max-md': '(width < 28rem)',
        '@max-lg': '(width < 32rem)',
        '@max-xl': '(width < 36rem)',
        '@max-2xl': '(width < 42rem)',
        '@max-3xl': '(width < 48rem)',
        '@max-4xl': '(width < 56rem)',
        '@max-5xl': '(width < 64rem)',
        '@max-6xl': '(width < 72rem)',
        '@max-7xl': '(width < 80rem)',
    }
    
    def __init__(
        self,
        colors: Dict,
        spacing: Dict,
        classes: Dict,
        media_queries: Dict[str, str],
        dark_mode: str = 'media',
        dark_mode_selector: str = '.dark',
    ):
        self.parser = ClassParser()
        self.registry = PluginRegistry()
        self.media_queries = media_queries
        
        # Dark mode configuration
        # 'media' = use prefers-color-scheme media query
        # 'class' or 'selector' = use selector-based dark mode
        self.dark_mode = dark_mode
        self.dark_mode_selector = dark_mode_selector
        
        # Create generator context
        self.context = GeneratorContext(
            colors=colors,
            spacing=spacing,
            classes=classes,
        )
        
        # Register all default plugins
        self._register_default_plugins()
    
    def _register_default_plugins(self):
        """Register all built-in utility plugins."""
        for plugin in spacing.get_plugins():
            self.registry.register(plugin)
        
        for plugin in colors.get_plugins():
            self.registry.register(plugin)
        
        for plugin in layout.get_plugins():
            self.registry.register(plugin)
        
        for plugin in typography.get_plugins():
            self.registry.register(plugin)
        
        for plugin in effects.get_plugins():
            self.registry.register(plugin)
    
    def generate(self, page_content: str) -> str:
        """
        Generate CSS from page content.
        
        Args:
            page_content: HTML/JSX/template content containing Tailwind classes
            
        Returns:
            Generated CSS string
        """
        # Extract class candidates
        candidates = extract_candidates(page_content)
        
        # Split into individual class tokens
        class_strings: List[str] = []
        seen: Set[str] = set()
        
        for candidate in candidates:
            tokens = split_classes(candidate)
            for token in tokens:
                if token and token not in seen:
                    class_strings.append(token)
                    seen.add(token)
        
        # Parse and generate
        stylesheet = Stylesheet()
        media_groups: Dict[str, List[Rule]] = {}
        container_groups: Dict[str, List[Rule]] = {}
        
        # Track gradient classes for ordering
        from_rules = []
        via_rules = []
        to_rules = []
        
        for class_string in class_strings:
            token = self.parser.parse(class_string)
            rule = self._generate_rule(token)
            
            if rule:
                # Apply variants to the rule
                rule = self._apply_variants(rule, token)
                
                # Check for media query variants
                media_query = self._get_media_query(token)
                container_query = self._get_container_query(token)
                
                if container_query:
                    container_groups.setdefault(container_query, []).append(rule)
                elif media_query:
                    media_groups.setdefault(media_query, []).append(rule)
                else:
                    # Special ordering for gradients
                    if token.utility == 'from':
                        from_rules.append(rule)
                    elif token.utility == 'via':
                        via_rules.append(rule)
                    elif token.utility == 'to':
                        to_rules.append(rule)
                    else:
                        stylesheet.add_rule(rule)
        
        # Add gradient rules in correct order
        for rule in from_rules:
            stylesheet.add_rule(rule)
        for rule in via_rules:
            stylesheet.add_rule(rule)
        for rule in to_rules:
            stylesheet.add_rule(rule)
        
        # Add media query groups
        for query, rules in media_groups.items():
            for rule in rules:
                stylesheet.add_media_rule(query, rule)
        
        # Add container query groups
        for query, rules in container_groups.items():
            for rule in rules:
                stylesheet.add_container_rule(query, rule)
        
        return stylesheet.to_css()
    
    def _generate_rule(self, token: TailwindToken) -> Optional[Rule]:
        """Generate a CSS rule for a parsed token."""
        return self.registry.generate(token, self.context)
    
    def _apply_variants(self, rule: Rule, token: TailwindToken) -> Rule:
        """Apply variant modifiers to a rule."""
        if not token.variants:
            return rule
        
        selector = rule.selector
        pseudo_classes = list(selector.pseudo_classes)
        pseudo_elements = list(selector.pseudo_elements)
        combinator_prefix = selector.combinator_prefix
        attribute_selectors = []
        
        for variant in token.variants:
            # Skip media/container query variants (handled separately)
            if variant in self.media_queries:
                continue
            if variant in self.CONTAINER_QUERIES:
                continue
            
            # Handle dark/light based on dark mode config
            if variant == 'dark':
                if self.dark_mode == 'media':
                    continue  # Handled as media query
                else:
                    # Class/selector-based dark mode
                    combinator_prefix = f'{self.dark_mode_selector} ' if not self.dark_mode_selector.endswith(' ') else self.dark_mode_selector
                    continue
            if variant == 'light':
                if self.dark_mode == 'media':
                    continue  # Handled as media query
                # For class-based, we could support a light selector too if configured
                continue
            
            # Skip other media feature variants (handled as media queries)
            if variant in self.MEDIA_FEATURE_VARIANTS:
                continue
            
            # Handle arbitrary variants
            if self._is_arbitrary_variant(variant):
                arbitrary_selector = self._handle_arbitrary_variant(variant)
                if arbitrary_selector:
                    if arbitrary_selector.startswith('['):
                        attribute_selectors.append(arbitrary_selector)
                    elif arbitrary_selector.startswith(':'):
                        pseudo_classes.append(arbitrary_selector[1:])
                    else:
                        pseudo_classes.append(arbitrary_selector)
                continue
            
            # Pseudo-classes
            if variant in self.PSEUDO_CLASSES:
                pseudo_classes.append(self.PSEUDO_CLASSES[variant])
            elif variant in self.NEGATED_PSEUDO_CLASSES:
                pseudo_classes.append(self.NEGATED_PSEUDO_CLASSES[variant])
            # Pseudo-elements
            elif variant in self.PSEUDO_ELEMENTS:
                pseudo_elements.append(self.PSEUDO_ELEMENTS[variant])
            # Group variants
            elif variant in self.GROUP_VARIANTS:
                combinator_prefix = self.GROUP_VARIANTS[variant]
            # Peer variants
            elif variant in self.PEER_VARIANTS:
                combinator_prefix = self.PEER_VARIANTS[variant]
            # ARIA variants
            elif variant in self.ARIA_VARIANTS:
                attribute_selectors.append(self.ARIA_VARIANTS[variant])
            # State variants
            elif variant in self.STATE_VARIANTS:
                pseudo_classes.append(self.STATE_VARIANTS[variant])
            # Direction variants
            elif variant in self.DIRECTION_VARIANTS:
                pseudo_classes.append(self.DIRECTION_VARIANTS[variant])
            # Child selector (*)
            elif variant == '*':
                selector_base = selector.base
                new_base = f":is({selector_base} > *)"
                selector = Selector(base=new_base)
            # Descendant selector (**)
            elif variant == '**':
                selector_base = selector.base
                new_base = f":is({selector_base} *)"
                selector = Selector(base=new_base)
        
        # Build attribute suffix
        attr_suffix = ''.join(attribute_selectors)
        
        # Create new selector with variants applied
        new_selector = Selector(
            base=selector.base + attr_suffix,
            pseudo_classes=pseudo_classes,
            pseudo_elements=pseudo_elements,
            combinator_prefix=combinator_prefix,
            combinator_suffix=selector.combinator_suffix,
        )
        
        return Rule(selector=new_selector, declarations=rule.declarations)
    
    def _is_arbitrary_variant(self, variant: str) -> bool:
        """Check if a variant is arbitrary (contains [...])."""
        return '[' in variant and ']' in variant
    
    def _handle_arbitrary_variant(self, variant: str) -> Optional[str]:
        """Handle arbitrary variants like has-[...], nth-[...], aria-[...], data-[...]."""
        # Match pattern: prefix-[value]
        match = re.match(r'^(\w+(?:-\w+)*)-\[(.+)\]$', variant)
        if not match:
            return None
        
        prefix, value = match.groups()
        value = value.replace('_', ' ')  # Replace underscores with spaces
        
        # Handle different arbitrary variant types
        if prefix == 'has':
            return f'has({value})'
        elif prefix == 'not':
            return f'not({value})'
        elif prefix == 'is':
            return f'is({value})'
        elif prefix == 'where':
            return f'where({value})'
        elif prefix == 'nth':
            return f'nth-child({value})'
        elif prefix == 'nth-last':
            return f'nth-last-child({value})'
        elif prefix == 'nth-of-type':
            return f'nth-of-type({value})'
        elif prefix == 'nth-last-of-type':
            return f'nth-last-of-type({value})'
        elif prefix == 'aria':
            return f'[aria-{value}]'
        elif prefix == 'data':
            return f'[data-{value}]'
        elif prefix == 'group':
            return f'.group:{value}'
        elif prefix == 'peer':
            return f'.peer:{value} ~'
        elif prefix == 'supports':
            # This is handled as media query
            return None
        elif prefix == 'min':
            # This is handled as media query
            return None
        elif prefix == 'max':
            # This is handled as media query
            return None
        
        return None
    
    def _get_media_query(self, token: TailwindToken) -> Optional[str]:
        """Get media query string for token variants."""
        for variant in token.variants:
            # Check screen breakpoints
            if variant in self.media_queries:
                return self.media_queries[variant]
            
            # Handle dark/light variants based on configuration
            if variant == 'dark':
                if self.dark_mode == 'media':
                    return self.MEDIA_FEATURE_VARIANTS['dark']
                # For class/selector mode, dark is handled in _apply_variants
                continue
            if variant == 'light':
                if self.dark_mode == 'media':
                    return self.MEDIA_FEATURE_VARIANTS['light']
                continue
            
            # Check other media feature variants (excluding dark/light handled above)
            if variant in self.MEDIA_FEATURE_VARIANTS and variant not in ('dark', 'light'):
                return self.MEDIA_FEATURE_VARIANTS[variant]
            
            # Handle arbitrary min-[...] and max-[...]
            if variant.startswith('min-[') and variant.endswith(']'):
                value = variant[5:-1]
                return f'(width >= {value})'
            if variant.startswith('max-[') and variant.endswith(']'):
                value = variant[5:-1]
                return f'(width < {value})'
            
            # Handle arbitrary supports-[...]
            if variant.startswith('supports-[') and variant.endswith(']'):
                value = variant[10:-1].replace('_', ' ')
                return f'@supports ({value})'
        
        return None
    
    def _get_container_query(self, token: TailwindToken) -> Optional[str]:
        """Get container query string for token variants."""
        for variant in token.variants:
            # Check container query variants
            if variant in self.CONTAINER_QUERIES:
                return self.CONTAINER_QUERIES[variant]
            
            # Handle arbitrary @min-[...] and @max-[...]
            if variant.startswith('@min-[') and variant.endswith(']'):
                value = variant[6:-1]
                return f'(width >= {value})'
            if variant.startswith('@max-[') and variant.endswith(']'):
                value = variant[6:-1]
                return f'(width < {value})'
        
        return None


def create_generator(
    colors: Dict,
    spacing: Dict,
    classes: Dict,
    media_queries: Dict[str, str],
    dark_mode: str = 'media',
    dark_mode_selector: str = '.dark',
) -> CSSGenerator:
    """
    Factory function to create a CSS generator.
    
    Args:
        colors: Color theme dictionary
        spacing: Spacing scale dictionary
        classes: Static class mappings
        media_queries: Media query mappings
        dark_mode: 'media' for prefers-color-scheme, 'class' or 'selector' for selector-based
        dark_mode_selector: CSS selector for class/selector-based dark mode
        
    Returns:
        Configured CSSGenerator instance
    """
    return CSSGenerator(
        colors=colors,
        spacing=spacing,
        classes=classes,
        media_queries=media_queries,
        dark_mode=dark_mode,
        dark_mode_selector=dark_mode_selector,
    )
