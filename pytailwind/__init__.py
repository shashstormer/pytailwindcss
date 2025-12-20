import re
import copy
from .classes import CLASSES, DYNAMIC_VALUE, MULTI_REQUIREMENT
from .defaults import COLORS, SPACING
from .conversions import TO_CSS_NAME, TO_TAILWIND_NAME
from .utils import extract_candidates, split_classes, split_by_hyphen, replace_underscores_safe


class Tailwind:
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
        self.colors = copy.deepcopy(COLORS)
        self.spacing = copy.deepcopy(SPACING)
        self.classes = copy.deepcopy(CLASSES)
        self.to_css_name = copy.deepcopy(TO_CSS_NAME)
        self.dynamic_value = copy.deepcopy(DYNAMIC_VALUE)
        self.to_tailwind_name = copy.deepcopy(TO_TAILWIND_NAME)
        self.multi_requirement = copy.deepcopy(MULTI_REQUIREMENT)

        # Initialize media queries dictionary
        self.media_queries = {
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

        # List of Media Query Processors
        # Will be re-generated based on media_queries
        self.media_query_processors = [
            "sm", "md", "lg", "xl", "2xl",
            "print", "dark", "light", "motion-safe", "motion-reduce",
            "max-sm", "max-md", "max-lg", "max-xl", "max-2xl"
        ]

        # List of Pseudo-class Processors
        self.pseudo_class_processors = [
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
        self.pseudo_element_processors = [
            "before",  # ::before
            "after",  # ::after
            "first-letter",  # ::first-letter
            "first-line",  # ::first-line
            "marker",  # ::marker
            "selection",  # ::selection
            "backdrop",  # ::backdrop
            "placeholder"  # ::placeholder
        ]

        if config:
            self.apply_config(config)

    def apply_config(self, config):
        theme = config.get("theme", {})
        extend = theme.get("extend", {})

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
        # Get all keys from self.media_queries
        screens = list(self.media_queries.keys())

        # Helper to extract pixel value for sorting
        def get_width_value(screen_name):
            # Try to get pixel value from media query string
            # e.g. "(min-width: 640px)" -> 640
            mq = self.media_queries.get(screen_name, "")
            match = re.search(r'width:\s*(\d+)px', mq)
            if match:
                return int(match.group(1))
            return 999999  # Fallback for non-pixel or complex queries

        # Separate min and max queries if needed, or just sort all by width
        # Tailwind usually sorts min-width queries ascending.
        # Max-width queries (if any) usually go after or before?
        # Let's sort all known screens by width.
        # But we also have non-screen processors like 'print', 'dark' etc.

        # Existing non-screen processors:
        others = ["print", "dark", "light", "motion-safe", "motion-reduce"]

        # Identify screens (keys in media_queries)
        # Note: media_queries includes 'max-sm' which I generated.

        sorted_screens = sorted(screens, key=get_width_value)

        self.media_query_processors = sorted_screens + others

        self._update_classes_with_config(replace_colors=replace_colors)

    def _update_classes_with_config(self, replace_colors=False):
        if replace_colors:
            # Remove default colors from color_groups
            for gp in self.COLOR_GROUPS:
                if gp in self.classes:
                    target = self.classes[gp]
                    # We want to remove keys that are in default COLORS
                    # Iterate over default COLORS to remove them
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
                # If color_value is string
                target[color_name] = color_value

    def _recursive_update(self, d, u):
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._recursive_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def _update_screens(self, screens, replace=False):
        if replace:
            # Clear existing media queries
            # But we should be careful if we want to keep non-screen things?
            # self.media_queries ONLY contains screens (sm, md, etc).
            # So clearing it is safe if we are replacing screens.
            self.media_queries = {}

        for name, value in screens.items():
            width = value
            if isinstance(value, dict):
                width = value.get("min", "")

            if width:
                self.media_queries[name] = f"(min-width: {width})"
                # Also generate max- variant?
                # Standard Tailwind behavior for theme.screens:
                # If you define screens, they are used for min-width breakpoints.
                # It doesn't automatically generate max-width variants unless configured?
                # But pytailwind seems to rely on them.
                # I'll keep generating them to maintain feature parity with defaults.
                self.media_queries[f"max-{name}"] = f"(max-width: {width})"

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

    def resolve_theme(self, value):
        """
        Resolves theme('...') inside arbitrary values.
        """
        match = re.match(r"theme\(['\"](.+?)['\"]\)", value)
        if not match:
            return value

        path = match.group(1).split('.')

        # Traverse configuration to find the value
        # Start with a virtual root combining colors, spacing, screens?
        # Standard Tailwind theme() can access any key in the theme.
        # But here we have flattened colors and spacing into self.colors, self.spacing etc.
        # But we also applied config so we might have new things.
        # Ideally we should keep 'theme' object structure.
        # But 'self.colors' contains the merged colors.

        # Map common top-level keys to self attributes
        current = None

        root_key = path[0]
        if root_key == 'colors':
            current = self.colors
        elif root_key == 'spacing':
            current = self.spacing
        elif root_key == 'screens':
            # self.media_queries stores complete strings, not just widths
            # But theme('screens.sm') should return the width e.g. '640px'
            # We don't easily have the width map if we only stored media queries.
            # But users usually ask for colors or spacing.
            pass
        else:
            # Fallback or other keys like 'fontFamily' which are in self.classes but scattered?
            # Actually, `self.classes` keys are mapped from `TO_TAILWIND_NAME`.
            # e.g. theme('fontFamily.sans') -> self.classes['fontFamily']['sans']?
            # Let's check if we can look into self.classes using TO_TAILWIND_NAME reverse mapping?
            # Or TO_CSS_NAME?
            # If root_key is 'fontSize', self.classes['fontSize'] exists.

            # Let's try to find it in self.classes
            if root_key in self.classes:
                current = self.classes[root_key]

        if current is None:
            # Try to map root_key via TO_TAILWIND_NAME?
            # e.g. theme('margin.4') -> margin is in spacing.
            # But usually theme() uses keys like 'colors', 'spacing', 'fontFamily'.
            pass

        # Traverse the rest of the path
        if current:
            for key in path[1:]:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return value  # Failed to resolve

            if isinstance(current, (str, int, float)):
                return str(current)
            elif isinstance(current, list):
                # e.g. fontSize can be list [size, lineHeight]
                return str(current[0])

        return value

    @staticmethod
    def looks_like_color(value):
        if not value: return False
        if value.startswith("#") or value.startswith("rgb") or value.startswith("hsl"):
            return True
        if value in ["transparent", "inherit", "currentColor", "white", "black"]:
            return True
        return False

    @staticmethod
    def looks_like_url(value):
        return "url(" in value

    def validate_arbitrary_value(self, group, value):
        """
        Returns True if value is valid for the group.
        """
        is_color = self.looks_like_color(value)
        is_url = self.looks_like_url(value)

        if group in self.COLOR_GROUPS:
            return is_color

        if group in self.IMAGE_GROUPS:
            return is_url or "gradient" in value or value == "none"

        if group in self.SPACING_GROUPS:
            # Spacing should not be color or url usually
            if is_color or is_url: return False
            return True

        if group in ["backgroundPosition", "backgroundSize", "backgroundRepeat", "backgroundClip"]:
            if is_color or is_url: return False
            return True

        if group in ["borderCollapse", "borderStyle"]:
            if is_color or is_url: return False
            if any(u in value for u in ["px", "rem", "em", "%", "vh", "vw"]): return False
            if value[0].isdigit(): return False
            return True

        if group == "fontSize":
            if is_color: return False
            return True

        if group == "boxShadow":
            # Shadow can contain color but it's complex string
            # e.g. "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
            # It starts with length usually.
            if value.startswith("#"): return False  # pure color is likely boxShadowColor
            return True

        if group in ["textAlign", "verticalAlign", "textTransform", "textWrap", "fontStyle", "fontSmoothing"]:
            # Keywords only usually. Definitely not color or url.
            if is_color or is_url: return False
            # Also usually not length?
            if any(u in value for u in ["px", "rem", "em", "%", "vh", "vw"]):
                return False
            return True

        # Default allow if we don't know constraints?
        return True

    def generate(self, page_content):
        # Improved candidate extraction
        candidates = extract_candidates(page_content)

        # Split candidates into class tokens
        classes_list = []
        seen = set()

        for candidate in candidates:
            tokens = split_classes(candidate)
            for token in tokens:
                if token not in seen:
                    classes_list.append(token)
                    seen.add(token)

        # Original generation logic
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
                    i = ori_op[0]
                    opacity = 100
            else:
                opacity = 100
            processors = []
            if ":" in i:
                k = i.split(":")
                i = k[-1]
                k.pop()
                processors = k

            # Use split_by_hyphen instead of i.split("-")
            j = split_by_hyphen(i)

            jz = self.merge_first_term(j)

            best_match = None

            for j2, j3 in jz:
                if best_match: break

                j = [j2]
                j.extend(j3)
                gps = self._tailwind_gps_matched(j[0])

                for gp in gps:
                    res = ""
                    gp_res = ""
                    is_arbitrary = False

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
                            is_arbitrary = True

                            # Extract value
                            raw_val = j[-1].replace("[", "").replace("]", "")
                            raw_val = replace_underscores_safe(raw_val)  # Safer replace
                            raw_val = self.resolve_theme(raw_val)

                            # Validate
                            if self.validate_arbitrary_value(gp, raw_val):
                                res = raw_val
                                gp_res = gp

                                # Handle multi-requirement (e.g. padding x/y)
                                if gp in self.multi_requirement:
                                    res_list = [res]
                                    for z in self.multi_requirement[gp]:
                                        res_list.append({z: res})
                                    res = res_list
                            else:
                                res = ""  # Invalid for this group
                        else:
                            if res:
                                gp_res = gp

                    # Sequential checks for length updates (e.g. filter insertion above)
                    if len(j) == 3:
                        # Fix for crash: use safe check before calling .get()
                        val = self.classes[gp].get(j[1], {})
                        if isinstance(val, dict):
                            res = val.get(j[2], "")
                        else:
                            # Try combining keys (e.g. bg-left-bottom -> left-bottom)
                            combined_key = f"{j[1]}-{j[2]}"
                            res = self.classes[gp].get(combined_key, "")

                        if j[-1].startswith("["):
                            # Path validation: Ensure intermediate keys exist if we are nested
                            # e.g. text-red-[...] -> red must exist in classes[gp]
                            root = self.classes[gp]
                            path_valid = False
                            if isinstance(root, dict) and j[1] in root:
                                path_valid = True

                            if path_valid:
                                is_arbitrary = True
                                raw_val = j[-1].replace("[", "").replace("]", "")
                                raw_val = replace_underscores_safe(raw_val)
                                raw_val = self.resolve_theme(raw_val)

                                if self.validate_arbitrary_value(gp, raw_val):
                                    res = raw_val
                                    gp_res = gp

                                    # Handle Divide/Border structural generation
                                    if gp == "divideWidth" or gp == "borderWidth":
                                        axis = j[1]
                                        if axis == "x":
                                            res = [{"border-left-width": raw_val, "border-right-width": raw_val}]
                                        elif axis == "y":
                                            res = [{"border-top-width": raw_val, "border-bottom-width": raw_val}]
                                else:
                                    res = ""
                            else:
                                res = ""  # Path invalid, skip arbitrary check

                        if res:
                            gp_res = gp

                    if len(j) == 4:
                        res = self.classes[gp].get(j[1], {}).get(j[2], {}).get(j[3], "")
                        if j[-1].startswith("["):
                            # Path validation
                            root = self.classes[gp]
                            path_valid = False
                            if isinstance(root, dict) and j[1] in root:
                                sub = root[j[1]]
                                if isinstance(sub, dict) and j[2] in sub:
                                    path_valid = True

                            if path_valid:
                                is_arbitrary = True
                                raw_val = j[-1].replace("[", "").replace("]", "")
                                raw_val = replace_underscores_safe(raw_val)
                                raw_val = self.resolve_theme(raw_val)

                                if self.validate_arbitrary_value(gp, raw_val):
                                    res = raw_val
                                    gp_res = gp
                                else:
                                    res = ""
                            else:
                                res = ""

                        if res:
                            gp_res = gp

                    if res and gp_res:
                        # We found a valid match.

                        # Generate CSS string
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

                        best_match = result_css_to_add
                        break  # Found valid gp match

            if best_match:
                result_css[self.sanitize_class_name(ori_i)] = best_match

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
        return "".join(vals)

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

    def hex_to_rgb(self, hex_color):
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

    def process_result_value(self, result, processors):
        fin = ""

        # Order processors
        ordered_processors_list = []
        ordered_processors_list.extend(self.pseudo_element_processors)
        ordered_processors_list.extend(self.pseudo_class_processors)
        ordered_processors_list.extend(self.media_query_processors)

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
            elif processor in self.media_queries:
                fin = "@media %s {%s}" % (self.media_queries[processor], result)
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
                .replace("/", "\\/").replace("(", "\\(").replace(")", "\\)").replace("#", "\\#").replace(",", "\\,")).replace(".", "\\.")
        if name.startswith("space-x") or name.startswith("space-y") or name.startswith("divide-x") or name.startswith(
                "divide-y"):
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
