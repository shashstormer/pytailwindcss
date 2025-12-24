"""
Pytailwindcss - A Python implementation of Tailwind CSS.

This module provides the Tailwind class for generating CSS from HTML content
containing Tailwind CSS utility classes.
"""

import re
import copy
from .classes import CLASSES, DYNAMIC_VALUE, MULTI_REQUIREMENT
from .defaults import COLORS, SPACING
from .conversions import TO_CSS_NAME, TO_TAILWIND_NAME
from .utils import extract_candidates, split_classes

# Core architecture imports
from .parser import ClassParser, TailwindToken, ValueType
from .ast import Stylesheet, Rule, Selector, Declaration, MediaQuery, escape_css_class
from .generator import CSSGenerator, create_generator


class Tailwind:
    """
    Main class for generating CSS from Tailwind utility classes.
    
    Usage:
        tw = Tailwind()
        css = tw.generate('<div class="p-4 text-red-500"></div>')
        print(css)  # .p-4 {padding: 1rem;}.text-red-500 {color: #ef4444;}
    """
    
    # Define groups for validation
    COLOR_GROUPS = {
        "backgroundColor", "textColor", "borderColor", "divideColor", "ringColor",
        "placeholderColor", "ringOffsetColor", "textDecorationColor", "accentColor",
        "caretColor", "fill", "stroke", "outlineColor", "boxShadowColor",
        "from", "via", "to", "gradientColorStops"
    }

    SPACING_GROUPS = {
        "padding", "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
        "paddingLeftRight", "paddingTopBottom",
        "margin", "marginTop", "marginRight", "marginBottom", "marginLeft",
        "marginLeftRight", "marginTopBottom",
        "width", "height", "minWidth", "minHeight", "maxWidth", "maxHeight",
        "gap", "space", "inset", "translate",
        "scrollMargin", "scrollPadding", "textIndent", "borderSpacing",
        "top", "right", "bottom", "left", "flexBasis", "size",
        "borderWidth", "divideWidth", "ringWidth", "ringOffsetWidth", "outlineWidth",
        "strokeWidth", "textDecorationThickness"
    }

    # Groups that accept images
    IMAGE_GROUPS = {"backgroundImage", "listStyleImage", "content"}

    def __init__(self, config=None):
        """
        Initialize the Tailwind generator.
        
        Args:
            config: Optional configuration dictionary for customizing colors,
                   spacing, screens, etc.
        """
        self.colors = copy.deepcopy(COLORS)
        self.spacing = copy.deepcopy(SPACING)
        self.classes = copy.deepcopy(CLASSES)
        self.to_css_name = copy.deepcopy(TO_CSS_NAME)
        self.dynamic_value = copy.deepcopy(DYNAMIC_VALUE)
        self.to_tailwind_name = copy.deepcopy(TO_TAILWIND_NAME)
        self.multi_requirement = copy.deepcopy(MULTI_REQUIREMENT)
        
        # Lazy-initialized generator
        self._generator = None
        
        # Dark mode configuration
        # Options:
        #   - 'media' (default): Uses prefers-color-scheme media query
        #   - 'class': Uses .dark class on parent element
        #   - 'selector': Uses custom selector (e.g., '[data-theme=dark]')
        # Can also be a tuple: ('selector', '.dark') or ('selector', '[data-theme=dark]')
        self.dark_mode = 'media'
        self.dark_mode_selector = '.dark'

        # Initialize media queries dictionary (Tailwind v4 syntax)
        self.media_queries = {
            "xs": "(width >= 30rem)",      # 480px - custom xs
            "sm": "(width >= 40rem)",      # 640px
            "md": "(width >= 48rem)",      # 768px
            "lg": "(width >= 64rem)",      # 1024px
            "xl": "(width >= 80rem)",      # 1280px
            "2xl": "(width >= 96rem)",     # 1536px
            "max-xs": "(width < 30rem)",   # < 480px
            "max-sm": "(width < 40rem)",   # < 640px
            "max-md": "(width < 48rem)",   # < 768px
            "max-lg": "(width < 64rem)",   # < 1024px
            "max-xl": "(width < 80rem)",   # < 1280px
            "max-2xl": "(width < 96rem)",  # < 1536px
        }

        # List of Media Query Processors
        self.media_query_processors = [
            "sm", "md", "lg", "xl", "2xl",
            "print", "dark", "light", "motion-safe", "motion-reduce",
            "max-sm", "max-md", "max-lg", "max-xl", "max-2xl"
        ]

        # List of Pseudo-class Processors
        self.pseudo_class_processors = [
            "hover", "focus", "active", "visited",
            "first", "last", "odd", "even", "disabled",
            "group-hover", "focus-within", "focus-visible",
            "checked", "required", "invalid",
            "first-of-type", "last-of-type", "only-child", "only-of-type",
            "empty", "read-only", "placeholder-shown",
            "not-first", "not-last", "not-disabled", "not-checked",
            "not-odd", "not-even",
            "peer-hover", "peer-focus", "peer-active",
            "peer-checked", "peer-required", "peer-invalid",
            "peer-placeholder-shown",
        ]

        # List of Pseudo-element Processors
        self.pseudo_element_processors = [
            "before", "after", "first-letter", "first-line",
            "marker", "selection", "backdrop", "placeholder"
        ]

        if config:
            self.apply_config(config)

    # ========== Configuration Methods ==========

    def apply_config(self, config):
        """Apply a configuration dictionary to customize the generator."""
        theme = config.get("theme", {})
        extend = theme.get("extend", {})
        
        # Dark mode configuration
        # Options:
        #   - 'media': Uses prefers-color-scheme media query (default)
        #   - 'class': Uses .dark class selector
        #   - ('class', 'selector'): Uses custom selector e.g. ('class', '[data-theme=dark]')
        if "darkMode" in config:
            dark_mode = config["darkMode"]
            if isinstance(dark_mode, str):
                self.dark_mode = dark_mode
                if dark_mode == 'class':
                    self.dark_mode_selector = '.dark'
            elif isinstance(dark_mode, (list, tuple)) and len(dark_mode) >= 2:
                self.dark_mode = dark_mode[0]
                self.dark_mode_selector = dark_mode[1]

        replace_colors = "colors" in theme

        # Colors
        if replace_colors:
            self.colors = theme["colors"]

        if "colors" in extend:
            self._recursive_update(self.colors, extend["colors"])

        # Spacing
        if "spacing" in theme:
            self.spacing = theme["spacing"]

        if "spacing" in extend:
            self._recursive_update(self.spacing, extend["spacing"])

        # Screens
        if "screens" in theme:
            self._update_screens(theme["screens"], replace=True)

        if "screens" in extend:
            self._update_screens(extend["screens"], replace=False)

        # Re-sync and Sort media_query_processors
        screens = list(self.media_queries.keys())

        def get_width_value(screen_name):
            mq = self.media_queries.get(screen_name, "")
            match = re.search(r'width:\s*(\d+)px', mq)
            if match:
                return int(match.group(1))
            return 999999

        others = ["print", "dark", "light", "motion-safe", "motion-reduce"]
        sorted_screens = sorted(screens, key=get_width_value)
        self.media_query_processors = sorted_screens + others

        self._update_classes_with_config(replace_colors=replace_colors)
        
        # Reset generator to pick up new config
        self._generator = None

    def _update_classes_with_config(self, replace_colors=False):
        """Update internal classes with configured colors and spacing."""
        if replace_colors:
            for gp in self.COLOR_GROUPS:
                if gp in self.classes:
                    target = self.classes[gp]
                    for color_name in COLORS:
                        if color_name in target:
                            del target[color_name]

        # Update Colors
        for gp in self.COLOR_GROUPS:
            self._merge_colors_into_group(gp)

        # Update Spacing
        for gp in self.SPACING_GROUPS:
            if gp in self.classes:
                target = self.classes[gp]
                for k, v in self.spacing.items():
                    target[k] = v

    def _merge_colors_into_group(self, gp):
        """Merge configured colors into a class group."""
        if gp not in self.classes:
            return

        target = self.classes[gp]

        for color_name, color_value in self.colors.items():
            if isinstance(color_value, dict):
                if color_name not in target:
                    target[color_name] = {}
                if isinstance(target[color_name], dict):
                    for shade, hex_val in color_value.items():
                        target[color_name][shade] = hex_val
            else:
                target[color_name] = color_value

    def _recursive_update(self, d, u):
        """Recursively update a dictionary."""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._recursive_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def _update_screens(self, screens, replace=False):
        """Update screen breakpoints."""
        if replace:
            self.media_queries = {}

        for name, value in screens.items():
            width = value
            if isinstance(value, dict):
                width = value.get("min", "")

            if width:
                self.media_queries[name] = f"(min-width: {width})"
                self.media_queries[f"max-{name}"] = f"(max-width: {width})"

    # ========== CSS Generation ==========

    @property
    def generator(self) -> CSSGenerator:
        """
        Get the CSS generator instance.
        
        Lazily initializes the generator on first access.
        """
        if self._generator is None:
            self._generator = create_generator(
                colors=self.colors,
                spacing=self.spacing,
                classes=self.classes,
                media_queries=self.media_queries,
                dark_mode=self.dark_mode,
                dark_mode_selector=self.dark_mode_selector,
            )
        return self._generator

    def generate(self, page_content: str) -> str:
        """
        Generate CSS from page content containing Tailwind classes.
        
        Args:
            page_content: HTML/JSX/template content containing Tailwind classes
            
        Returns:
            Generated CSS string
            
        Example:
            >>> tw = Tailwind()
            >>> css = tw.generate('<div class="p-4 text-red-500"></div>')
            >>> print(css)
            .p-4 {padding: 1rem;}.text-red-500 {color: #ef4444;}
        """
        return self.generator.generate(page_content)

    # ========== Utility Methods ==========

    def get_parser(self) -> ClassParser:
        """Get a class parser instance for external use."""
        return ClassParser()
    
    def parse_class(self, class_string: str) -> TailwindToken:
        """
        Parse a single Tailwind class string into a token.
        
        Useful for debugging or custom processing.
        
        Args:
            class_string: A Tailwind class like "hover:bg-red-500/50"
            
        Returns:
            Parsed TailwindToken with extracted components
            
        Example:
            >>> tw = Tailwind()
            >>> token = tw.parse_class('hover:bg-red-500/50')
            >>> print(token.variants)  # ['hover']
            >>> print(token.utility)   # 'bg'
            >>> print(token.value)     # 'red-500'
            >>> print(token.opacity)   # 50
        """
        return ClassParser().parse(class_string)
