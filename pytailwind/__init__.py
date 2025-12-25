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
from .preflight import get_preflight, get_preflight_layered, get_properties, PREFLIGHT_CSS, PROPERTIES_CSS

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

    def __init__(self, config=None, include_preflight=True):
        """
        Initialize the Tailwind generator.
        
        Args:
            config: Optional configuration dictionary for customizing colors,
                   spacing, screens, etc.
            include_preflight: Whether to include Preflight base styles when
                              generating CSS. Defaults to True.
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
        
        # Preflight configuration
        self.include_preflight = include_preflight
        
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

    def _generate_theme_css(self) -> str:
        """Generate CSS variables for theme."""
        theme_vars = []

        # Fonts
        for key, value in self.classes.get('fontFamily', {}).items():
            if isinstance(value, list):
                val_str = ', '.join(value)
            else:
                val_str = value
            theme_vars.append(f"  --font-{key}: {val_str};")

        # Colors (simplified generation)
        # Note: A full implementation would iterate all colors recursively.
        # Here we just generate a few key ones to demonstrate the concept or iterate self.colors.
        # For full v4 parity, we would output all colors.

        # Spacing
        theme_vars.append(f"  --spacing: 0.25rem;")

        # Basic container widths (from defaults)
        theme_vars.append(f"  --container-md: 28rem;")
        theme_vars.append(f"  --container-2xl: 42rem;")
        theme_vars.append(f"  --container-7xl: 80rem;")

        return "\n".join(theme_vars)

    def generate(self, page_content: str, include_preflight: bool = None) -> str:
        """
        Generate CSS from page content containing Tailwind classes.
        
        Args:
            page_content: HTML/JSX/template content containing Tailwind classes
            include_preflight: Override instance-level preflight setting.
                              If None, uses the instance setting.
            
        Returns:
            Generated CSS string matching Tailwind v4 structure.
        """
        # Determine whether to include preflight
        should_include_preflight = include_preflight if include_preflight is not None else self.include_preflight
        
        # Generate utility CSS
        utility_css = self.generator.generate(page_content)
        
        # Build CSS parts
        parts = []
        has_content = False
        
        # Theme Layer
        if should_include_preflight:
            has_content = True
            theme_css = self._generate_theme_css()
            parts.append("@layer theme {")
            parts.append("  :root, :host {")
            parts.append(theme_css)
            parts.append("  }")
            parts.append("}")

        # Base Layer (Preflight)
        if should_include_preflight:
            has_content = True
            parts.append("@layer base {")
            parts.append(get_preflight())
            parts.append("}")

        # Properties Layer
        if should_include_preflight:
            has_content = True
            parts.append("@layer properties {")
            parts.append(get_properties())
            parts.append("}")

        # Utilities Layer
        if utility_css:
            has_content = True
            parts.append("@layer utilities {")
            parts.append(utility_css)
            parts.append("}")

        if not has_content:
            return ""

        # Prepend header
        header = [
            "/*! tailwindcss v4.1.18 | MIT License | https://tailwindcss.com */",
            "@layer properties;",
            "@layer theme, base, components, utilities;"
        ]
        return "\n".join(header + parts)

    # ========== Utility Methods ==========

    def get_preflight(self, layered: bool = False) -> str:
        """
        Get the Preflight base styles CSS.
        
        Args:
            layered: If True, wraps the CSS in @layer base.
            
        Returns:
            The Preflight CSS string.
            
        Example:
            >>> tw = Tailwind()
            >>> css = tw.get_preflight()
            >>> 'box-sizing: border-box' in css
            True
        """
        if layered:
            return get_preflight_layered()
        return get_preflight()

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
    
    def apply(self, *classes: str) -> str:
        """
        Expand utility classes into CSS declarations (like @apply directive).
        
        This allows you to inline Tailwind utility classes into custom CSS.
        
        Args:
            *classes: One or more Tailwind utility class names
            
        Returns:
            CSS declarations as a string (without the selector)
            
        Example:
            >>> tw = Tailwind()
            >>> tw.apply('rounded-lg', 'shadow-md')
            'border-radius: 0.5rem; box-shadow: ...'
        """
        declarations = []
        for class_name in classes:
            # Generate CSS for this class (without preflight)
            css = self.generate(f'<div class="{class_name}"></div>', include_preflight=False)
            if css:
                # Extract declarations from the generated rule
                # Format: .class-name {declarations}
                match = re.search(r'\{([^}]+)\}', css)
                if match:
                    # Clean up the declaration
                    decl = match.group(1).strip()
                    if not decl.endswith(';'):
                        decl += ';'
                    declarations.append(decl)
        
        return ' '.join(declarations)
    
    def spacing_value(self, multiplier: float) -> str:
        """
        Calculate a spacing value based on the theme (like --spacing() function).
        
        Uses the base spacing unit (0.25rem by default) multiplied by the given value.
        
        Args:
            multiplier: The spacing multiplier (e.g., 4 for p-4)
            
        Returns:
            Calculated spacing value as CSS string
            
        Example:
            >>> tw = Tailwind()
            >>> tw.spacing_value(4)
            'calc(var(--spacing) * 4)'
        """
        return f'calc(var(--spacing) * {multiplier})'
    
    def theme_value(self, path: str) -> str:
        """
        Access theme values using dot notation (like theme() function).
        
        Args:
            path: Dot-notation path to the theme value (e.g., 'spacing.4', 'colors.red.500')
            
        Returns:
            The theme value or empty string if not found
            
        Example:
            >>> tw = Tailwind()
            >>> tw.theme_value('spacing.4')
            '1rem'
            >>> tw.theme_value('colors.red.500')
            '#ef4444'
        """
        parts = path.split('.')
        
        # Handle spacing
        if parts[0] == 'spacing' and len(parts) > 1:
            key = parts[1]
            return self.spacing.get(key, '')
        
        # Handle colors
        if parts[0] == 'colors' and len(parts) > 1:
            color_name = parts[1]
            if color_name in self.colors:
                color_value = self.colors[color_name]
                if isinstance(color_value, dict) and len(parts) > 2:
                    shade = parts[2]
                    return color_value.get(shade, '')
                elif isinstance(color_value, str):
                    return color_value
            return ''
        
        return ''
    
    def process_css_with_apply(self, css_content: str) -> str:
        """
        Process CSS content and expand @apply directives.
        
        Args:
            css_content: CSS string that may contain @apply directives
            
        Returns:
            CSS with @apply directives expanded
            
        Example:
            >>> tw = Tailwind()
            >>> css = '''
            ... .btn {
            ...     @apply px-4 py-2 rounded-lg;
            ... }
            ... '''
            >>> tw.process_css_with_apply(css)
        """
        # Pattern to match @apply directives
        apply_pattern = re.compile(r'@apply\s+([^;]+);?')
        
        def replace_apply(match):
            classes = match.group(1).strip().split()
            return self.apply(*classes)
        
        return apply_pattern.sub(replace_apply, css_content)

