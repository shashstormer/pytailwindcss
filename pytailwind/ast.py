"""
CSS Abstract Syntax Tree (AST) nodes.

This module provides structured nodes for CSS generation,
enabling manipulation of CSS rules before rendering to strings.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union


class CSSNode(ABC):
    """Base class for all CSS AST nodes."""
    
    @abstractmethod
    def to_css(self) -> str:
        """Render this node to a CSS string."""
        ...
    
    def __str__(self) -> str:
        return self.to_css()


@dataclass
class Declaration(CSSNode):
    """
    CSS property-value declaration.
    
    Example: "color: red;" or "margin: 1rem !important;"
    """
    property: str
    value: str
    important: bool = False
    
    def to_css(self) -> str:
        imp = " !important" if self.important else ""
        return f"{self.property}: {self.value}{imp};"


@dataclass
class Selector:
    """
    CSS selector with support for pseudo-classes and pseudo-elements.
    
    Supports:
    - Base selectors: .class-name
    - Pseudo-classes: :hover, :focus, :first-child
    - Pseudo-elements: ::before, ::after
    - Combinators: .group:hover .element, > * + *
    """
    base: str                                            # .class-name
    pseudo_classes: List[str] = field(default_factory=list)   # hover, focus, etc.
    pseudo_elements: List[str] = field(default_factory=list)  # before, after, etc.
    combinator_prefix: str = ""                          # .group:hover (for group-hover)
    combinator_suffix: str = ""                          # > * + * (for space-x)
    
    def to_css(self) -> str:
        """Render selector to CSS string."""
        pseudo_class_str = "".join(f":{pc}" for pc in self.pseudo_classes)
        pseudo_element_str = "".join(f"::{pe}" for pe in self.pseudo_elements)
        
        result = ""
        if self.combinator_prefix:
            result += self.combinator_prefix + " "
        
        result += f"{self.base}{pseudo_class_str}{pseudo_element_str}"
        
        if self.combinator_suffix:
            result += f" {self.combinator_suffix}"
        
        return result


@dataclass 
class Rule(CSSNode):
    """
    CSS rule with selector and declarations.
    
    Example: ".bg-red-500 {background-color: #ef4444;}"
    """
    selector: Selector
    declarations: List[Declaration] = field(default_factory=list)
    
    def to_css(self) -> str:
        if not self.declarations:
            return ""
        
        decls = " ".join(d.to_css() for d in self.declarations)
        return f"{self.selector.to_css()} {{{decls}}}"
    
    def add_declaration(self, property: str, value: str, important: bool = False) -> 'Rule':
        """Add a declaration to this rule. Returns self for chaining."""
        self.declarations.append(Declaration(property, value, important))
        return self


@dataclass
class MediaQuery(CSSNode):
    """
    CSS @media rule wrapper.
    
    Example: "@media (min-width: 640px) {.sm\\:bg-red-500 {...}}"
    """
    query: str
    rules: List[Rule] = field(default_factory=list)
    
    def to_css(self) -> str:
        if not self.rules:
            return ""
        
        inner = "".join(r.to_css() for r in self.rules)
        return f"@media {self.query} {{{inner}}}"
    
    def add_rule(self, rule: Rule) -> 'MediaQuery':
        """Add a rule to this media query. Returns self for chaining."""
        self.rules.append(rule)
        return self


@dataclass
class SupportsQuery(CSSNode):
    """
    CSS @supports rule wrapper.
    
    Example: "@supports (display: grid) {...}"
    """
    condition: str
    rules: List[Rule] = field(default_factory=list)
    
    def to_css(self) -> str:
        if not self.rules:
            return ""
        
        inner = "".join(r.to_css() for r in self.rules)
        return f"@supports {self.condition} {{{inner}}}"


@dataclass
class Keyframes(CSSNode):
    """
    CSS @keyframes rule.
    
    Example: "@keyframes spin { from { ... } to { ... } }"
    """
    name: str
    frames: Dict[str, List[Declaration]] = field(default_factory=dict)
    
    def to_css(self) -> str:
        if not self.frames:
            return ""
        
        frame_strs = []
        for selector, declarations in self.frames.items():
            decls = " ".join(d.to_css() for d in declarations)
            frame_strs.append(f"{selector} {{{decls}}}")
        
        inner = " ".join(frame_strs)
        return f"@keyframes {self.name} {{{inner}}}"


@dataclass
class CSSVariable(CSSNode):
    """
    CSS custom property (variable) declaration.
    
    Example: "--tw-gradient-from: #ef4444;"
    """
    name: str   # Without -- prefix
    value: str
    
    def to_css(self) -> str:
        return f"--{self.name}: {self.value};"


@dataclass
class Stylesheet(CSSNode):
    """
    Root CSS stylesheet containing multiple nodes.
    
    Manages ordering of rules for proper CSS cascade.
    """
    nodes: List[CSSNode] = field(default_factory=list)
    
    # Track media queries for grouping
    _media_groups: Dict[str, MediaQuery] = field(default_factory=dict, repr=False)
    
    def to_css(self) -> str:
        """Render all nodes to CSS string."""
        return "".join(node.to_css() for node in self.nodes)
    
    def add_rule(self, rule: Rule) -> 'Stylesheet':
        """Add a rule directly to the stylesheet."""
        self.nodes.append(rule)
        return self
    
    def add_media_rule(self, query: str, rule: Rule) -> 'Stylesheet':
        """Add a rule inside a media query, grouping by query."""
        if query not in self._media_groups:
            media = MediaQuery(query=query)
            self._media_groups[query] = media
            self.nodes.append(media)
        
        self._media_groups[query].add_rule(rule)
        return self
    
    def add_node(self, node: CSSNode) -> 'Stylesheet':
        """Add any CSS node to the stylesheet."""
        self.nodes.append(node)
        return self


# Utility functions for common patterns

def create_simple_rule(class_name: str, property: str, value: str) -> Rule:
    """Create a simple rule with one property."""
    selector = Selector(base=f".{class_name}")
    return Rule(
        selector=selector,
        declarations=[Declaration(property=property, value=value)]
    )


def create_multi_property_rule(class_name: str, properties: Dict[str, str]) -> Rule:
    """Create a rule with multiple properties."""
    selector = Selector(base=f".{class_name}")
    declarations = [Declaration(property=p, value=v) for p, v in properties.items()]
    return Rule(selector=selector, declarations=declarations)


def escape_css_class(name: str) -> str:
    """
    Escape special characters in CSS class names.
    
    "[", "]", ":", "/", etc. need to be escaped for CSS selectors.
    """
    # Characters that need escaping in CSS selectors
    special_chars = {
        '[': '\\[',
        ']': '\\]',
        ':': '\\:',
        '/': '\\/',
        '%': '\\%',
        '(': '\\(',
        ')': '\\)',
        '#': '\\#',
        ',': '\\,',
        '.': '\\.',
        "'": "\\'",
        '"': '\\"',
        '!': '\\!',
        '&': '\\&',
        '*': '\\*',
        '+': '\\+',
        '=': '\\=',
        '>': '\\>',
        '<': '\\<',
        '~': '\\~',
        '^': '\\^',
        '$': '\\$',
        '|': '\\|',
        '@': '\\@',
    }
    
    result = []
    for char in name:
        result.append(special_chars.get(char, char))
    
    return "".join(result)
