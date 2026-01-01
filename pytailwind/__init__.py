import re
from .classes import CLASSES, DYNAMIC_VALUE, MULTI_REQUIREMENT
from .defaults import COLORS, SPACING
from .conversions import  TO_CSS_NAME, TO_TAILWIND_NAME
class Tailwind:
    def __init__(self):
        self.colors = COLORS
        self.spacing = SPACING
        self.classes = CLASSES
        self.to_css_name = TO_CSS_NAME
        self.dynamic_value = DYNAMIC_VALUE
        self.to_tailwind_name = TO_TAILWIND_NAME
        self.multi_requirement = MULTI_REQUIREMENT

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

    def _resolve_properties(self, i):
        processors = []
        if ":" in i:
            k = i.split(":")
            i = k[-1]
            k.pop()
            processors = k
        j = i.split("-")
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
                            res = j[-1].replace("[", "").replace("]", "")
                            if gp_res in self.multi_requirement:
                                res = [res]
                                for z in self.multi_requirement[gp_res]:
                                    res.append({z: res[0]})
                        else:
                            if not res:
                                res = j[-1].replace("[", "").replace("]", "")
                    if res and not gp_res:
                        gp_res = gp
                if len(j) == 3:
                    res = self.classes[gp].get(j[1], {}).get(j[2], "")
                    if j[-1].startswith("["):
                        if not res:
                            res = j[-1].replace("[", "").replace("]", "")
                    if res and not gp_res:
                        gp_res = gp
                if len(j) == 4:
                    res = self.classes[gp].get(j[1], {}).get(j[2], {}).get(j[3], "")
                    if j[-1].startswith("["):
                        if not res:
                            res = j[-1].replace("[", "").replace("]", "")
                    if res and not gp_res:
                        gp_res = gp
                
                if res:
                    return res, gp_res, processors
        return None, None, []

    def generate(self, page_content):
        match_classes = re.compile('class\s*=\s*["\']([^"\']+)["\']')
        class_list = match_classes.findall(page_content)
        classes_list = []
        result_css = {}
        for i in class_list:
            i = i.split()
            for j in i:
                if j not in classes_list:
                    classes_list.append(j)
        for i in classes_list:
            ori_i = i
            res, gp_res, processors = self._resolve_properties(i)
            opacity = 100
            
            if not res and "/" in i:
                parts = i.split("/", 1)
                if len(parts) == 2:
                    try:
                        possible_opacity = int(parts[1])
                        base_res, base_gp, base_proc = self._resolve_properties(parts[0])
                        if base_res:
                            res = base_res
                            gp_res = base_gp
                            processors = base_proc
                            opacity = possible_opacity
                    except ValueError:
                        pass
            
            if res:
                if (isinstance(res, str) or (isinstance(res, list) and isinstance(res[0], str))) and gp_res not in [
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
            "light",  # prefers-color-scheme: light
            "motion-safe",  # prefers-reduced-motion: no-preference
            "motion-reduce",  # prefers-reduced-motion: reduce
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
            elif processor in ["sm", "md", "lg", "xl", "2xl", "xs", "max-xs", "max-sm", "max-md", "max-lg", "max-xl", "max-2xl"]:
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
                .replace("/", "\\/").replace("(", "\\(").replace(")", "\\)").replace("#", "\\#").replace(",", "\\,").replace(".", "\\."))
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
                for item in value:
                    if isinstance(item, dict):
                        for key in item:
                            result += self.to_css_name.get(key, key) + ":" + item[key] + ";"
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
