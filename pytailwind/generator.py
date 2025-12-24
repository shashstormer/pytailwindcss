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
    
    # Pseudo-class mappings
    PSEUDO_CLASSES = {
        'hover': 'hover',
        'focus': 'focus',
        'active': 'active',
        'visited': 'visited',
        'first': 'first-child',
        'last': 'last-child',
        'odd': 'nth-child(odd)',
        'even': 'nth-child(even)',
        'disabled': 'disabled',
        'enabled': 'enabled',
        'checked': 'checked',
        'required': 'required',
        'invalid': 'invalid',
        'valid': 'valid',
        'focus-within': 'focus-within',
        'focus-visible': 'focus-visible',
        'first-of-type': 'first-of-type',
        'last-of-type': 'last-of-type',
        'only-child': 'only-child',
        'only-of-type': 'only-of-type',
        'empty': 'empty',
        'read-only': 'read-only',
        'placeholder-shown': 'placeholder-shown',
        'default': 'default',
        'indeterminate': 'indeterminate',
        'autofill': 'autofill',
    }
    
    # Negated pseudo-classes
    NEGATED_PSEUDO_CLASSES = {
        'not-first': 'not(:first-child)',
        'not-last': 'not(:last-child)',
        'not-disabled': 'not(:disabled)',
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
    }
    
    # Group variants (require parent selector)
    GROUP_VARIANTS = {
        'group-hover': ('.group:hover', ''),
        'group-focus': ('.group:focus', ''),
        'group-active': ('.group:active', ''),
    }
    
    # Peer variants (require sibling selector)
    PEER_VARIANTS = {
        'peer-hover': ('.peer:hover ~', ''),
        'peer-focus': ('.peer:focus ~', ''),
        'peer-active': ('.peer:active ~', ''),
        'peer-checked': ('.peer:checked ~', ''),
        'peer-required': ('.peer:required ~', ''),
        'peer-invalid': ('.peer:invalid ~', ''),
        'peer-placeholder-shown': ('.peer:placeholder-shown ~', ''),
    }
    
    def __init__(
        self,
        colors: Dict,
        spacing: Dict,
        classes: Dict,
        media_queries: Dict[str, str],
    ):
        self.parser = ClassParser()
        self.registry = PluginRegistry()
        self.media_queries = media_queries
        
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
                
                if media_query:
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
        
        for variant in token.variants:
            # Skip media query variants (handled separately)
            if variant in self.media_queries:
                continue
            if variant in ('dark', 'light', 'print', 'motion-safe', 'motion-reduce'):
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
                combinator_prefix = self.GROUP_VARIANTS[variant][0]
            # Peer variants
            elif variant in self.PEER_VARIANTS:
                combinator_prefix = self.PEER_VARIANTS[variant][0]
        
        # Create new selector with variants applied
        new_selector = Selector(
            base=selector.base,
            pseudo_classes=pseudo_classes,
            pseudo_elements=pseudo_elements,
            combinator_prefix=combinator_prefix,
            combinator_suffix=selector.combinator_suffix,
        )
        
        return Rule(selector=new_selector, declarations=rule.declarations)
    
    def _get_media_query(self, token: TailwindToken) -> Optional[str]:
        """Get media query string for token variants."""
        for variant in token.variants:
            # Check screen breakpoints
            if variant in self.media_queries:
                return self.media_queries[variant]
            
            # Check special media queries
            if variant == 'dark':
                return '(prefers-color-scheme: dark)'
            if variant == 'light':
                return '(prefers-color-scheme: light)'
            if variant == 'print':
                return 'print'
            if variant == 'motion-safe':
                return '(prefers-reduced-motion: no-preference)'
            if variant == 'motion-reduce':
                return '(prefers-reduced-motion: reduce)'
        
        return None


def create_generator(
    colors: Dict,
    spacing: Dict,
    classes: Dict,
    media_queries: Dict[str, str],
) -> CSSGenerator:
    """
    Factory function to create a CSS generator.
    
    Args:
        colors: Color theme dictionary
        spacing: Spacing scale dictionary
        classes: Static class mappings
        media_queries: Media query mappings
        
    Returns:
        Configured CSSGenerator instance
    """
    return CSSGenerator(
        colors=colors,
        spacing=spacing,
        classes=classes,
        media_queries=media_queries,
    )
