import re
from html.parser import HTMLParser
from .defaults import COLORS
from .classes import CLASSES, DYNAMIC_VALUE, MULTI_REQUIREMENT


class ClassExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.classes = []

    def handle_starttag(self, tag, attrs):
        for attr, value in attrs:
            # Handle 'class' attribute
            if attr == 'class':
                if value:
                    self.classes.extend(value.split())
            # Handle React's 'className' (though in HTML rendered it is class, but if parsing JSX/source files)
            elif attr == 'className':
                if value:
                    self.classes.extend(value.split())


class Tailwind:
    def __init__(self, config=None):
        # We need deep copies because CLASSES contains dictionaries that might be shared references
        # But for performance we want to avoid full deep copy if possible.
        # CLASSES structure:
        # { "backgroundColor": COLORS, "margin": SPACING, "flex": {...} }
        # where COLORS and SPACING are module level dicts.

        # We make a shallow copy of CLASSES.
        self.classes = CLASSES.copy()

        # We make a shallow copy of COLORS so we can modify self.colors without affecting module COLORS
        self.colors = COLORS.copy()

        self.dynamic_value = DYNAMIC_VALUE.copy()
        self.multi_requirement = MULTI_REQUIREMENT.copy()

        if config:
            self.apply_config(config)

        self.to_css_name = {
            "animation": "animation",
            "animationDuration": "animation-duration",
            "animationTimingFunction": "animation-timing-function",
            "animationDelay": "animation-delay",
            "animationIterationCount": "animation-iteration-count",
            "animationDirection": "animation-direction",
            "animationFillMode": "animation-fill-mode",
            "animationPlayState": "animation-play-state",
            "aria": "aria",
            "aspectRatio": "aspect-ratio",
            "backgroundImage": "background-image",
            "backgroundPosition": "background-position",
            "backgroundSize": "background-size",
            "borderRadius": "border-radius",
            "borderWidth": "border-width",
            "boxShadow": "box-shadow",
            "brightness": "brightness",
            "colors": "color",
            "columns": "columns",
            "container": "container",
            "content": "content",
            "contrast": "contrast",
            "cursor": "cursor",
            "dropShadow": "drop-shadow",
            "fill": "fill",
            "flex": "flex",
            "flexBasis": "flex-basis",
            "flexGrow": "flex-grow",
            "flexShrink": "flex-shrink",
            "fontFamily": "font-family",
            "fontSize": "font-size",
            "fontWeight": "font-weight",
            "fontStyle": "font-style",
            "fromPosition": "--tw-gradient-from-position",
            "gradientColorStopPositions": "gradient-color-stop-positions",
            "grayscale": "grayscale",
            "gridAutoColumns": "grid-auto-columns",
            "gridAutoRows": "grid-auto-rows",
            "gridColumn": "grid-column",
            "gridColumnEnd": "grid-column-end",
            "gridColumnStart": "grid-column-start",
            "gridRow": "grid-row",
            "gridRowEnd": "grid-row-end",
            "gridRowStart": "grid-row-start",
            "gridTemplateColumns": "grid-template-columns",
            "gridTemplateRows": "grid-template-rows",
            "height": "height",
            "hueRotate": "hue-rotate",
            "inset": "inset",
            "invert": "invert",
            "keyframes": "keyframes",
            "leading": "line-height",
            "letterSpacing": "letter-spacing",
            "lineHeight": "line-height",
            "listStyleType": "list-style-type",
            "listStyleImage": "list-style-image",
            "margin": "margin",
            "marginRight": "margin-right",
            "marginLeft": "margin-left",
            "marginTop": "margin-top",
            "marginBottom": "margin-bottom",
            "lineClamp": "line-clamp",
            "maxHeight": "max-h",
            "maxWidth": "max-w",
            "minHeight": "min-h",
            "minWidth": "min-w",
            "marginLeftRight": "mx",
            "marginTopBottom": "my",
            "objectPosition": "object-position",
            "opacity": "opacity",
            "order": "order",
            "outlineOffset": "outline-offset",
            "outlineWidth": "outline-width",
            "paddingTop": "padding-top",
            "paddingBottom": "padding-bottom",
            "paddingRight": "padding-right",
            "paddingLeft": "padding-left",
            "ringColor": "ring-color",
            "ringOffsetWidth": "ring-offset-width",
            "ringOpacity": "ring-opacity",
            "ringWidth": "ring-width",
            "rotate": "rotate",
            "saturate": "saturate",
            "scale": "scale",
            "screens": "screens",
            "sepia": "sepia",
            "skew": "skew",
            "spacing": "spacing",
            "stroke": "stroke",
            "strokeWidth": "stroke-width",
            "supports": "supports",
            "data": "data",
            "toPosition": "--tw-gradient-to-position",
            "to": "--tw-gradient-to",
            "textAlign": "text-align",
            "textDecorationThickness": "text-decoration-thickness",
            "textUnderlineOffset": "text-underline-offset",
            "textTransform": "text-transform",
            "textWrap": "text-wrap",
            "transformOrigin": "transform-origin",
            "transitionDelay": "transition-delay",
            "transitionDuration": "transition-duration",
            "transitionProperty": "transition-property",
            "transitionTimingFunction": "transition-timing-function",
            "translate": "translate",
            "size": "size",
            "viaPosition": "--tw-gradient-via-position",
            "width": "width",
            "willChange": "will-change",
            "zIndex": "z-index",
            "backgroundColor": "background-color",
            "backgroundOpacity": "background-opacity",
            "borderColor": "border-color",
            "borderOpacity": "border-opacity",
            "borderSpacing": "border-spacing",
            "boxShadowColor": "box-shadow-color",
            "caretColor": "caret-color",
            "divideColor": "divide-color",
            "divideOpacity": "divide-opacity",
            "divideWidth": "divide-width",
            "gap": "gap",
            "gradientColorStops": "gradient-color-stops",
            "outlineColor": "outline-color",
            "padding": "padding",
            "paddingLeft": "pl",
            "paddingRight": "pr",
            "paddingTop": "pt",
            "paddingBottom": "pb",
            "paddingLeftRight": "px",
            "paddingTopBottom": "py",
            "placeholderColor": "placeholder-color",
            "placeholderOpacity": "placeholder-opacity",
            "ringOffsetColor": "ring-offset-color",
            "scrollMargin": "scroll-margin",
            "scrollPadding": "scroll-padding",
            "space": "space",
            "textColor": "color",
            "textDecorationColor": "text-decoration-color",
            "textIndent": "text-indent",
            "textOpacity": "text-opacity",
            "textDecoration": "text-decoration",
        }
        self.to_tailwind_name = {
            "animationNames": "animate",
            "animationTimingFunction": ["animate", "animation-timing-function"],
            "animationIterationCount": ["animate", "animation-direction"],
            "animationDirection": ["animate", "animation-direction"],
            "animationFillMode": ["animate", "animation-fill"],
            "animationPlayState": ["animate", "animation-play-state"],
            "aria": "aria",
            "aspectRatio": "aspect",
            "backgroundImage": "bg",
            "backgroundPosition": "bg",
            "backgroundSize": "bg",
            "borderRadius": "rounded",
            "borderWidth": "border",
            "boxShadow": "shadow",
            "brightness": "brightness",
            "colors": "colors",
            "columns": "columns",
            "container": "container",
            "content": "content",
            "contrast": "contrast",
            "cursor": "cursor",
            "display": [
                "block",
                "inline",
                "inline-block",
                "flex",
                "inline-flex",
                "grid",
                "inline-grid",
                "table",
                "inline-table",
                "table-row",
                "table-cell",
                "none",
                "hidden"
            ],
            "from": "from",
            "fromPosition": "from",
            "fill": "fill",
            "flex": "flex",
            "flexBasis": "basis",
            "flexGrow": "grow",
            "flexShrink": "shrink",
            "fontSmoothing": ["antialiased", "subpixel-antialiased"],
            "filter": [
                "blur",
                "brightness",
                "contrast",
                "drop-shadow",
                "grayscale",
                "hue-rotate",
                "invert",
                "saturate",
                "sepia"
            ],
            "backdrop-filter": ["backdrop"],
            "fontFamily": "font",
            "fontSize": "text",
            "fontWeight": "font",
            "fontStyle": [
                'italic',
                "not-italic",
            ],
            "gradientColorStopPositions": "gradient",
            "grayscale": "grayscale",
            "gridAutoColumns": "auto-cols",
            "gridAutoRows": "auto-rows",
            "gridColumn": "col",
            "gridColumnEnd": "col-end",
            "gridColumnStart": "col-start",
            "gridRow": "row",
            "gridRowEnd": "row-end",
            "gridRowStart": "row-start",
            "gridTemplateColumns": "grid-cols",
            "gridTemplateRows": "grid-rows",
            "height": "h",
            "hueRotate": "hue-rotate",
            "inset": "inset",
            "invert": "invert",
            "keyframes": "keyframes",
            "leading": "leading",
            "letterSpacing": "tracking",
            "lineHeight": "leading",
            "listStyleType": "list",
            "listStyleImage": "list",
            "margin": "m",
            "marginLeft": ["ml", "space-x"],
            "marginRight": "mr",
            "marginTop": ["mt", 'space-y'],
            "marginBottom": "mb",
            "lineClamp": "line-clamp",
            "maxHeight": "max-h",
            "maxWidth": "max-w",
            "minHeight": "min-h",
            "minWidth": "min-w",
            "marginLeftRight": "mx",
            "marginTopBottom": "my",
            "objectPosition": "object",
            "opacity": "opacity",
            "order": "order",
            "outlineOffset": "outline-offset",
            "outlineWidth": "outline",
            "position": [
                "static",
                "relative",
                "absolute",
                "fixed",
                "sticky"
            ],
            "ringColor": "ring",
            "ringOffsetWidth": "ring-offset",
            "ringOpacity": "ring-opacity",
            "ringWidth": "ring",
            "rotate": "rotate",
            "saturate": "saturate",
            "scale": "scale",
            "screens": "screens",
            "sepia": "sepia",
            "skew": "skew",
            "srOnly": "sr-only",
            "stroke": "stroke",
            "strokeWidth": "stroke",
            "supports": "supports",
            "data": "data",
            "to": "to",
            "toPosition": "to",
            "textAlign": "text",
            "textDecorationThickness": "decoration",
            "textUnderlineOffset": "underline-offset",
            "textTransform": [
                "uppercase",
                "lowercase",
                "capitalize",
                "normal-case",
            ],
            "textWrap": "text",
            "transformOrigin": "origin",
            "transitionDelay": "delay",
            "transitionDuration": "duration",
            "transitionProperty": "transition",
            "transitionTimingFunction": "ease",
            "translate": "translate",
            "via": "via",
            "viaPosition": "via",
            "size": "size",
            "width": "w",
            "willChange": "will-change",
            "zIndex": "z",

            "backgroundColor": "bg",
            "backgroundOpacity": "bg-opacity",
            "borderColor": "border",
            "borderOpacity": "border-opacity",
            "borderSpacing": "border-spacing",
            "boxShadowColor": "shadow",
            "caretColor": "caret",
            "divideColor": "divide",
            "divideOpacity": "divide-opacity",
            "divideWidth": "divide",
            "gap": "gap",
            "gradientColorStops": "gradient",
            "outlineColor": "outline",
            "overflow": "overflow",
            "padding": "p",
            "paddingLeft": "pl",
            "paddingRight": "pr",
            "paddingTop": "pt",
            "paddingBottom": "pb",
            "paddingLeftRight": "px",
            "paddingTopBottom": "py",
            "placeholderColor": "placeholder",
            "placeholderOpacity": "placeholder-opacity",
            "ringOffsetColor": "ring-offset",
            "scrollMargin": "scroll-m",
            "scrollPadding": "scroll-p",
            "space": "space",
            "textColor": "text",
            "textDecorationColor": "decoration",
            "textIndent": "indent",
            "textOpacity": "text-opacity",
            "textDecoration": [
                "none",  # No decoration
                "underline",  # Underline
                "overline",  # Overline
                "line-through",  # Line through
                "blink",  # Blink (not widely supported),
            ]
        }

    def apply_config(self, config):
        """
        Apply configuration to override or extend defaults.
        Supported keys:
        - theme: { extend: { ... } }

        Currently rudimentary support.
        """
        if not config:
            return

        theme = config.get("theme", {})
        extend = theme.get("extend", {})

        # Handle colors extension
        if "colors" in extend:
            # We must update self.colors
            self.colors.update(extend["colors"])

            # Now we must update self.classes["colors"] to point to our updated instance colors
            self.classes["colors"] = self.colors

            # We also know backgroundColor, textColor, etc use it.
            color_utilities = [
                "backgroundColor", "borderColor", "boxShadowColor", "caretColor", "divideColor",
                "gradientColorStops", "outlineColor", "placeholderColor", "ringColor", "ringOffsetColor",
                "stroke", "textColor", "textDecorationColor", "accentColor", "fill"
            ]
            for util in color_utilities:
                if util in self.classes:
                    if isinstance(self.classes[util], dict):
                        # If we don't distinguish COPY vs EXTEND here easily, let's look at `util` value.
                        current_val = self.classes[util]

                        # Create a copy of current_val and update it
                        new_val = current_val.copy()
                        new_val.update(self.colors)
                        self.classes[util] = new_val

        # Handle spacing extension
        if "spacing" in extend:
            for key, value in extend.get("spacing", {}).items():
                # Add to all spacing utilities
                spacing_utilities = [
                    "padding", "paddingTop", "paddingBottom", "paddingLeft", "paddingRight",
                    "margin", "marginTop", "marginBottom", "marginLeft", "marginRight",
                    "width", "height", "minHeight", "maxHeight", "minWidth", "maxWidth",
                    "gap", "space", "translate", "inset"
                ]
                for util in spacing_utilities:
                    if util in self.classes:
                        if isinstance(self.classes[util], dict):
                            # Similar logic: Don't mutate in place if it might be global SPACING.
                            # Create copy and update.
                            current_val = self.classes[util]
                            new_val = current_val.copy()
                            new_val[key] = value
                            self.classes[util] = new_val

    def _tailwind_gps_matched(self, first):
        matches = []
        for i in self.to_tailwind_name:
            gp = self.to_tailwind_name[i]
            if gp == first:
                matches.append(i)
            if isinstance(gp, list):
                if first in gp:
                    matches.append(i)
        return matches

    def merge_first_term(self, class_hyphen_list):
        possible = []
        class_hyphen_list = class_hyphen_list.copy()
        popped = []
        while class_hyphen_list:
            j = "-".join(class_hyphen_list)
            for i in self.to_tailwind_name:
                gp = self.to_tailwind_name[i]
                to_append = ["-".join(class_hyphen_list), popped[::-1]]
                if gp == j:
                    possible.append(to_append)
                if isinstance(gp, list):
                    if j in gp:
                        possible.append(to_append)
            popped.append(class_hyphen_list.pop())
        lis = []
        for i in possible:
            if i not in lis:
                lis.append(i)
        return lis

    def validate_arbitrary_value(self, value):
        # Prevent CSS injection via arbitrary values
        forbidden = [';', '}', '{']
        for char in forbidden:
            if char in value:
                return False
        return True

    def generate(self, page_content, minify=False):
        # Fallback to regex if parsing fails (e.g. not HTML but just a string of classes, or very malformed)
        # But try HTMLParser first.

        # NOTE: HTMLParser expects a tag to extract attributes.
        # If page_content is just a fragment without tags, it might not work well if it doesn't look like tags.
        # However, Tailwind usually works on HTML files.

        extractor = ClassExtractor()
        try:
            extractor.feed(page_content)
            classes_list = extractor.classes
        except Exception:
            # Fallback to regex if HTML parsing fails completely
            match_classes = re.compile('class\s*=\s*["\']([^"\']+)["\']')
            classes_full = match_classes.findall(page_content)
            classes_list = []
            for i in classes_full:
                classes_list.extend(i.split())

        # Deduplicate while preserving order
        unique_classes = []
        for cls in classes_list:
            if cls not in unique_classes:
                unique_classes.append(cls)
        classes_list = unique_classes

        result_css = {}
        for i in classes_list:
            ori_i = i
            opacity = i.split("/", 1)
            opacity_text = ""
            if len(opacity) == 2:
                try:
                    ori_op = opacity
                    opacity = int(opacity[-1])
                    i = ori_op[0]
                    opacity_text = f"/{opacity}"
                except Exception as e:
                    opacity = 100
            else:
                opacity = 100
            j = i.split("-")
            processors = []
            if ":" in j[0]:
                k = j[0].split(":")
                j[0] = k[-1]
                k.pop()
                processors = k
            jz = self.merge_first_term(j)
            for j2, j3 in jz:
                j = [j2]
                j.extend(j3)
                gps = self._tailwind_gps_matched(j[0])
                for gp in gps:
                    res = ""
                    gp_res = ""
                    if len(j) == 1:
                        res = self.classes[gp].get(j[0], "")
                        if not res:
                            res = self.classes[gp].get("DEFAULT", "")
                        if res:
                            gp_res = gp
                    if len(j) == 2:
                        if gp == "filter":
                            if "filter" not in j:
                                j.insert(0, "filter")
                        res = self.classes[gp].get(j[1], "")
                        if isinstance(res, dict):
                            res = res.get("DEFAULT", "")
                        if j[-1].startswith("["):
                            gp_res = self.dynamic_value.get(j[0], "")
                            if gp_res:
                                extracted_val = j[-1].replace("[", "").replace("]", "")
                                if self.validate_arbitrary_value(extracted_val):
                                    res = extracted_val
                                    if gp_res in self.multi_requirement:
                                        res = [res]
                                        for z in self.multi_requirement[gp_res]:
                                            res.append({z: res[0]})
                                else:
                                    res = ""  # Invalid arbitrary value
                            else:
                                if not res:
                                    extracted_val = j[-1].replace("[", "").replace("]", "")
                                    if self.validate_arbitrary_value(extracted_val):
                                        res = extracted_val
                        if res:
                            gp_res = gp
                    if len(j) == 3:
                        res = self.classes[gp].get(j[1], {}).get(j[2], "")
                        if j[-1].startswith("["):
                            if not res:
                                extracted_val = j[-1].replace("[", "").replace("]", "")
                                if self.validate_arbitrary_value(extracted_val):
                                    res = extracted_val
                        if res:
                            gp_res = gp
                    if len(j) == 4:
                        res = self.classes[gp].get(j[1], {}).get(j[2], {}).get(j[3], "")
                        if j[-1].startswith("["):
                            if not res:
                                extracted_val = j[-1].replace("[", "").replace("]", "")
                                if self.validate_arbitrary_value(extracted_val):
                                    res = extracted_val
                        if res:
                            gp_res = gp
                    if res:
                        if (isinstance(res, str) or (isinstance(res, list) and isinstance(res[0], str))) and gp not in [
                            "from", "to", "via"]:
                            result_css_to_add = (".%s {%s: %s;}" %
                                                 (
                                                     self.sanitize_class_name(ori_i),
                                                     self.to_css_name.get(gp_res, gp_res),
                                                     self.normalize_property_value(res)
                                                 )
                                                 )
                        else:
                            result_css_to_add = ".%s {%s}" % (
                                self.sanitize_class_name(ori_i), self.normalize_property_value(res))
                        result_css_to_add = self.process_result_value(result_css_to_add, processors)
                        if opacity < 100:
                            result_css_to_add = self.process_opacity(result_css_to_add, opacity)
                        result_css[self.sanitize_class_name(ori_i)] = result_css_to_add
        from_vals = [result_css[k] for k in result_css if "from-" in k]
        via_vals = [result_css[k] for k in result_css if "via-" in k]
        to_vals = [result_css[k] for k in result_css if "to-" in k]
        vals = []
        for key in list(result_css.keys()):
            if "from-" in key or "via-" in key or "to-" in key:
                del result_css[key]
                continue
            vals.append(result_css[key])
            del result_css[key]
        vals = vals + from_vals + via_vals + to_vals
        output = "".join(vals)
        if minify:
            output = output.replace("\n", "").replace("  ", "").replace(": ", ":").replace("; ", ";").replace(" {",
                                                                                                              "{").replace(
                ", ", ",")
        return output

    def process_opacity(self, css_class, opacity):
        hex_regex = re.compile(r"[ '\"]#[0-9a-fA-F]{3,8}")
        hexes = hex_regex.findall(css_class)
        hexes = sorted(hexes, key=len, reverse=True)
        for _hex in hexes:
            char1 = _hex[0]
            rgba = self.hex_to_rgb(_hex[1:])
            if rgba[3] == 1:
                rgba[3] = opacity / 100
            rgba = f"rgba({', '.join([str(i) for i in rgba])})"
            css_class = css_class.replace(_hex, char1 + rgba)
        return css_class

    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        if len(hex_color) == 8:
            a = int(hex_color[6:8], 16) / 255.0
        else:
            a = 1.0
        return [r, g, b, a]

    @staticmethod
    def process_result_value(result, processors):
        fin = ""
        # List of Media Query Processors
        media_query_processors = [
            "sm",  # min-width: 640px
            "md",  # min-width: 768px
            "lg",  # min-width: 1024px
            "xl",  # min-width: 1280px
            "2xl",  # min-width: 1536px
            "print",  # applies to print media
            "dark",  # prefers-color-scheme: dark
            "motion-safe",  # prefers-reduced-motion: no-preference
            "motion-reduce"  # prefers-reduced-motion: reduce
            "max-sm",
            "max-md",
            "max-lg",
            "max-xl",
            "max-2xl",
        ]

        # List of Pseudo-class Processors
        pseudo_class_processors = [
            "hover",  # :hover
            "focus",  # :focus
            "active",  # :active
            "visited",  # :visited
            "first",  # :first-child
            "last",  # :last-child
            "odd",  # :nth-child(odd)
            "even",  # :nth-child(even)
            "disabled",  # :disabled
            "group-hover",  # .group:hover .element
            "focus-within",  # :focus-within
            "focus-visible",  # :focus-visible
            "checked",  # :checked
            "required",  # :required
            "invalid",  # :invalid
            "before",  # ::before
            "after",  # ::after
            "first-of-type",  # :first-of-type
            "last-of-type",  # :last-of-type
            "only-child",  # :only-child
            "only-of-type",  # :only-of-type
            "empty",  # :empty
            "read-only",  # :read-only
            "placeholder-shown",  # :placeholder-shown
            "not-first",  # :not(:first-child)
            "not-last",  # :not(:last-child)
            "not-disabled",  # :not(:disabled)
            "not-checked",  # :not(:checked)
            "not-odd",  # :not(:nth-child(odd))
            "not-even",  # :not(:nth-child(even))
            "peer-hover",  # :hover on a sibling with the class 'peer'
            "peer-focus",  # :focus on a sibling with the class 'peer'
            "peer-active",  # :active on a sibling with the class 'peer'
            "peer-checked",  # :checked on a sibling with the class 'peer'
            "peer-required",  # :required on a sibling with the class 'peer'
            "peer-invalid",  # :invalid on a sibling with the class 'peer'
            "peer-placeholder-shown",  # :placeholder-shown on a sibling with the class 'peer'
        ]

        # List of Pseudo-element Processors
        pseudo_element_processors = [
            "before",  # ::before
            "after",  # ::after
            "first-letter",  # ::first-letter
            "first-line",  # ::first-line
            "marker",  # ::marker
            "selection",  # ::selection
            "backdrop",  # ::backdrop
            "placeholder"  # ::placeholder
        ]

        # Order processors
        ordered_processors_list = []
        ordered_processors_list.extend(pseudo_element_processors)
        ordered_processors_list.extend(pseudo_class_processors)
        ordered_processors_list.extend(media_query_processors)

        processors_ordered = []
        for processor in ordered_processors_list:
            if processor in processors:
                processors_ordered.append(processor)

        # Process the result based on the ordered processors
        for processor in processors_ordered:
            if processor == "dark":
                fin = "@media (prefers-color-scheme: dark) {%s}" % result
            elif processor == "light":
                fin = "@media (prefers-color-scheme: light) {%s}" % result
            elif processor == "hover":
                result = result.split(" {", 1)
                fin = result[0] + ":hover {" + result[1]
            elif processor == "focus":
                result = result.split(" {", 1)
                fin = result[0] + ":focus {" + result[1]
            elif processor == "active":
                result = result.split(" {", 1)
                fin = result[0] + ":active {" + result[1]
            elif processor == "visited":
                result = result.split(" {", 1)
                fin = result[0] + ":visited {" + result[1]
            elif processor == "first":
                result = result.split(" {", 1)
                fin = result[0] + ":first-child {" + result[1]
            elif processor == "last":
                result = result.split(" {", 1)
                fin = result[0] + ":last-child {" + result[1]
            elif processor == "odd":
                result = result.split(" {", 1)
                fin = result[0] + ":nth-child(odd) {" + result[1]
            elif processor == "even":
                result = result.split(" {", 1)
                fin = result[0] + ":nth-child(even) {" + result[1]
            elif processor == "disabled":
                result = result.split(" {", 1)
                fin = result[0] + ":disabled {" + result[1]
            elif processor == "group-hover":
                result = result.split(" {", 1)
                fin = ".group:hover " + result[0] + " {" + result[1]
            elif processor == "focus-within":
                result = result.split(" {", 1)
                fin = result[0] + ":focus-within {" + result[1]
            elif processor == "focus-visible":
                result = result.split(" {", 1)
                fin = result[0] + ":focus-visible {" + result[1]
            elif processor == "checked":
                result = result.split(" {", 1)
                fin = result[0] + ":checked {" + result[1]
            elif processor == "required":
                result = result.split(" {", 1)
                fin = result[0] + ":required {" + result[1]
            elif processor == "invalid":
                result = result.split(" {", 1)
                fin = result[0] + ":invalid {" + result[1]
            elif processor == "before":
                result = result.split(" {", 1)
                fin = result[0] + "::before {" + result[1]
            elif processor == "after":
                result = result.split(" {", 1)
                fin = result[0] + "::after {" + result[1]
            elif processor == "first-of-type":
                result = result.split(" {", 1)
                fin = result[0] + ":first-of-type {" + result[1]
            elif processor == "last-of-type":
                result = result.split(" {", 1)
                fin = result[0] + ":last-of-type {" + result[1]
            elif processor == "only-child":
                result = result.split(" {", 1)
                fin = result[0] + ":only-child {" + result[1]
            elif processor == "only-of-type":
                result = result.split(" {", 1)
                fin = result[0] + ":only-of-type {" + result[1]
            elif processor == "empty":
                result = result.split(" {", 1)
                fin = result[0] + ":empty {" + result[1]
            elif processor == "read-only":
                result = result.split(" {", 1)
                fin = result[0] + ":read-only {" + result[1]
            elif processor == "placeholder-shown":
                result = result.split(" {", 1)
                fin = result[0] + ":placeholder-shown {" + result[1]
            elif processor == "not-first":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:first-child) {" + result[1]
            elif processor == "not-last":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:last-child) {" + result[1]
            elif processor == "not-disabled":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:disabled) {" + result[1]
            elif processor == "not-checked":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:checked) {" + result[1]
            elif processor == "not-odd":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:nth-child(odd)) {" + result[1]
            elif processor == "not-even":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:nth-child(even)) {" + result[1]
            elif processor == "peer-hover":
                result = result.split(" {", 1)
                fin = ".peer:hover ~ " + result[0] + " {" + result[1]
            elif processor == "peer-focus":
                result = result.split(" {", 1)
                fin = ".peer:focus ~ " + result[0] + " {" + result[1]
            elif processor == "peer-active":
                result = result.split(" {", 1)
                fin = ".peer:active ~ " + result[0] + " {" + result[1]
            elif processor == "peer-checked":
                result = result.split(" {", 1)
                fin = ".peer:checked ~ " + result[0] + " {" + result[1]
            elif processor == "peer-required":
                result = result.split(" {", 1)
                fin = ".peer:required ~ " + result[0] + " {" + result[1]
            elif processor == "peer-invalid":
                result = result.split(" {", 1)
                fin = ".peer:invalid ~ " + result[0] + " {" + result[1]
            elif processor == "peer-placeholder-shown":
                result = result.split(" {", 1)
                fin = ".peer:placeholder-shown ~ " + result[0] + " {" + result[1]
            elif processor in ["sm", "md", "lg", "xl", "2xl"]:
                media_queries = {
                    "xs": "(min-width: 425px)",
                    "sm": "(min-width: 640px)",
                    "md": "(min-width: 768px)",
                    "lg": "(min-width: 1024px)",
                    "xl": "(min-width: 1280px)",
                    "2xl": "(min-width: 1536px)",
                    "max-xs": "(max-width: 425px)",
                    "max-sm": "(max-width: 640px)",
                    "max-md": "(max-width: 768px)",
                    "max-lg": "(max-width: 1024px)",
                    "max-xl": "(max-width: 1280px)",
                    "max-2xl": "(max-width: 1536px)",
                }
                fin = "@media %s {%s}" % (media_queries[processor], result)
            elif processor == "motion-safe":
                fin = "@media (prefers-reduced-motion: no-preference) {%s}" % result
            elif processor == "motion-reduce":
                fin = "@media (prefers-reduced-motion: reduce) {%s}" % result
            elif processor == "print":
                fin = "@media print {%s}" % result
            else:
                print("UNDEFINED PROCESSSOR :", processor)
                return ""
            if fin:
                result = fin
        if not fin and not processors:
            return result
        return fin.replace(";;", ";")

    @staticmethod
    def sanitize_class_name(name):
        name = (name.replace("[", "\\[").replace("]", "\\]").replace("%", "\\%").replace(":", "\\:")
                .replace("/", "\\/").replace("(", "\\(").replace(")", "\\)").replace("#", "\\#").replace(",", "\\,"))
        if name.startswith("space-x") or name.startswith("space-y"):
            name += " > * + *"
        return name

    def normalize_property_value(self, value):
        result = ""
        if isinstance(value, list):
            if len(value) == 2:
                if isinstance(value[0], str) and isinstance(value[1], dict):
                    result += value[0] + ";"
                    for key in value[1]:
                        result += self.to_css_name.get(key, key) + ":" + value[1][key] + ";"
            elif isinstance(value[0], dict):
                for key in value[0]:
                    result += self.to_css_name.get(key, key) + ":" + value[0][key] + ";"
            else:
                for i in value:
                    if not isinstance(i, str):
                        break
                else:
                    result = ", ".join(value)
        elif isinstance(value, dict):
            for key, val in value.items():
                result += f"{key}:{val};"
        else:
            result = value
        return result
