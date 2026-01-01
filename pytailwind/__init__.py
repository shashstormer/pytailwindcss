import re
import html
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
                        if "DEFAULT" in res:
                            res = res.get("DEFAULT", "")
                    if j[-1].startswith("["):
                        gp_res = self.dynamic_value.get(j[0], "")
                        
                        val = j[-1].replace("[", "").replace("]", "")
                        if j[0] == "text":
                            if any(unit in val for unit in ["px", "rem", "em", "%", "vh", "vw"]) or val.isdigit():
                                gp_res = "fontSize"
                            else:
                                gp_res = "color"
                        elif j[0] == "border":
                            if any(unit in val for unit in ["px", "rem", "em", "%"]) or val.isdigit():
                                gp_res = "borderWidth"
                            else:
                                gp_res = "borderColor"
                        elif j[0] == "bg":
                             if "url" in val:
                                gp_res = "backgroundImage"
                             elif any(unit in val for unit in ["px", "rem", "em", "%"]) or val.isdigit():
                                gp_res = "backgroundSize" # or position, but usually bg-[size]
                             else:
                                gp_res = "backgroundColor"
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



    def generate(self, page_content, minify=True):
        match_classes = re.compile(r'(?:class|className)\s*=\s*["\']([^"\']+)["\']')
        class_list = match_classes.findall(page_content)
        classes_list = []
        result_css = {}
        for i in class_list:
            i = html.unescape(i)
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
                    if minify:
                        result_css_to_add = (".%s {%s: %s;}" %
                                            (
                                                self.sanitize_class_name(ori_i),
                                                self.to_css_name.get(gp_res, gp_res),
                                                self.normalize_property_value(res)
                                            )
                                            )
                    else:
                        result_css_to_add = ".%s {\n    %s: %s;\n}" % (
                            self.sanitize_class_name(ori_i),
                            self.to_css_name.get(gp_res, gp_res),
                            self.normalize_property_value(res)
                        )

                else:
                    if minify:
                        result_css_to_add = ".%s {%s}" % (
                            self.sanitize_class_name(ori_i), self.normalize_property_value(res))
                    else:
                        css_val = self.normalize_property_value(res)
                        if ";" in css_val:
                            props = [p.strip() for p in css_val.split(";") if p.strip()]
                            formatted_props = "\n".join(f"    {p};" for p in props)
                            result_css_to_add = f".{self.sanitize_class_name(ori_i)} {{\n{formatted_props}\n}}"
                        else:
                            result_css_to_add = f".{self.sanitize_class_name(ori_i)} {{\n    {css_val}\n}}"

                result_css_to_add = self.process_result_value(result_css_to_add, processors, minify=minify)
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
        
        separator = "" if minify else "\n"
        return separator.join(vals)

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
    def process_result_value(result, processors, minify=True):
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
            nl = "" if minify else "\n"
            indent = "" if minify else "    "
            
            def format_block(wrapper_start, content, wrapper_end="}"):
                if minify:
                    return f"{wrapper_start}{{{content}{wrapper_end}"
                else:
                    indented_content = content.replace("\n", "\n    ")
                    return f"{wrapper_start} {{\n    {indented_content}\n{wrapper_end}"

            if processor == "dark":
                fin = format_block("@media (prefers-color-scheme: dark)", result)
            elif processor == "light":
                fin = format_block("@media (prefers-color-scheme: light)", result)
            elif processor == "hover":
                if minify:
                     parts = result.split(" {", 1)
                     fin = parts[0] + ":hover {" + parts[1]
                else:
                     parts = result.split(" {", 1)
                     fin = parts[0] + ":hover {" + parts[1]

            elif processor == "focus":
                parts = result.split(" {", 1)
                fin = parts[0] + ":focus {" + parts[1]
            elif processor == "active":
                parts = result.split(" {", 1)
                fin = parts[0] + ":active {" + parts[1]
            elif processor == "visited":
                parts = result.split(" {", 1)
                fin = parts[0] + ":visited {" + parts[1]
            elif processor == "first":
                parts = result.split(" {", 1)
                fin = parts[0] + ":first-child {" + parts[1]
            elif processor == "last":
                parts = result.split(" {", 1)
                fin = parts[0] + ":last-child {" + parts[1]
            elif processor == "odd":
                parts = result.split(" {", 1)
                fin = parts[0] + ":nth-child(odd) {" + parts[1]
            elif processor == "even":
                parts = result.split(" {", 1)
                fin = parts[0] + ":nth-child(even) {" + parts[1]
            elif processor == "disabled":
                parts = result.split(" {", 1)
                fin = parts[0] + ":disabled {" + parts[1]
            elif processor == "group-hover":
                parts = result.split(" {", 1)
                fin = ".group:hover " + parts[0] + " {" + parts[1]
            elif processor == "focus-within":
                parts = result.split(" {", 1)
                fin = parts[0] + ":focus-within {" + parts[1]
            elif processor == "focus-visible":
                parts = result.split(" {", 1)
                fin = parts[0] + ":focus-visible {" + parts[1]
            elif processor == "checked":
                parts = result.split(" {", 1)
                fin = parts[0] + ":checked {" + parts[1]
            elif processor == "required":
                parts = result.split(" {", 1)
                fin = parts[0] + ":required {" + parts[1]
            elif processor == "invalid":
                parts = result.split(" {", 1)
                fin = parts[0] + ":invalid {" + parts[1]
            elif processor == "before":
                parts = result.split(" {", 1)
                fin = parts[0] + "::before {" + parts[1]
            elif processor == "after":
                parts = result.split(" {", 1)
                fin = parts[0] + "::after {" + parts[1]
            elif processor == "first-of-type":
                parts = result.split(" {", 1)
                fin = parts[0] + ":first-of-type {" + parts[1]
            elif processor == "last-of-type":
                parts = result.split(" {", 1)
                fin = parts[0] + ":last-of-type {" + parts[1]
            elif processor == "only-child":
                parts = result.split(" {", 1)
                fin = parts[0] + ":only-child {" + parts[1]
            elif processor == "only-of-type":
                parts = result.split(" {", 1)
                fin = parts[0] + ":only-of-type {" + parts[1]
            elif processor == "empty":
                parts = result.split(" {", 1)
                fin = parts[0] + ":empty {" + parts[1]
            elif processor == "read-only":
                parts = result.split(" {", 1)
                fin = parts[0] + ":read-only {" + parts[1]
            elif processor == "placeholder-shown":
                parts = result.split(" {", 1)
                fin = parts[0] + ":placeholder-shown {" + parts[1]
            elif processor == "not-first":
                parts = result.split(" {", 1)
                fin = parts[0] + ":not(:first-child) {" + parts[1]
            elif processor == "not-last":
                parts = result.split(" {", 1)
                fin = parts[0] + ":not(:last-child) {" + parts[1]
            elif processor == "not-disabled":
                parts = result.split(" {", 1)
                fin = parts[0] + ":not(:disabled) {" + parts[1]
            elif processor == "not-checked":
                parts = result.split(" {", 1)
                fin = parts[0] + ":not(:checked) {" + parts[1]
            elif processor == "not-odd":
                parts = result.split(" {", 1)
                fin = parts[0] + ":not(:nth-child(odd)) {" + parts[1]
            elif processor == "not-even":
                parts = result.split(" {", 1)
                fin = parts[0] + ":not(:nth-child(even)) {" + parts[1]
            elif processor == "peer-hover":
                parts = result.split(" {", 1)
                fin = ".peer:hover ~ " + parts[0] + " {" + parts[1]
            elif processor == "peer-focus":
                parts = result.split(" {", 1)
                fin = ".peer:focus ~ " + parts[0] + " {" + parts[1]
            elif processor == "peer-active":
                parts = result.split(" {", 1)
                fin = ".peer:active ~ " + parts[0] + " {" + parts[1]
            elif processor == "peer-checked":
                parts = result.split(" {", 1)
                fin = ".peer:checked ~ " + parts[0] + " {" + parts[1]
            elif processor == "peer-required":
                parts = result.split(" {", 1)
                fin = ".peer:required ~ " + parts[0] + " {" + parts[1]
            elif processor == "peer-invalid":
                parts = result.split(" {", 1)
                fin = ".peer:invalid ~ " + parts[0] + " {" + parts[1]
            elif processor == "peer-placeholder-shown":
                parts = result.split(" {", 1)
                fin = ".peer:placeholder-shown ~ " + parts[0] + " {" + parts[1]
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
                fin = format_block(f"@media {media_queries[processor]}", result)
            elif processor == "motion-safe":
                fin = format_block("@media (prefers-reduced-motion: no-preference)", result)
            elif processor == "motion-reduce":
                fin = format_block("@media (prefers-reduced-motion: reduce)", result)
            elif processor == "print":
                 fin = format_block("@media print", result)
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
                .replace("/", "\\/").replace("(", "\\(").replace(")", "\\)").replace("#", "\\#").replace(",", "\\,").replace(".", "\\.").replace("&", "\&"))
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
