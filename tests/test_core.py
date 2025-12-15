import pytest
from pytailwind import Tailwind
from pytailwind.defaults import COLORS, SPACING

@pytest.fixture
def tw():
    return Tailwind()

def test_tailwind_gps_matched(tw):
    # Test single match
    matches = tw._tailwind_gps_matched("text")
    # 'text' matches multiple groups in TO_TAILWIND_NAME
    assert "textColor" in matches
    assert "textAlign" in matches
    assert "fontSize" in matches

    # Test list match
    matches = tw._tailwind_gps_matched("block")
    assert "display" in matches

def test_merge_first_term(tw):
    # Test with hyphens
    # text-red-500 -> text matches textColor
    # but 'text-red' doesn't match anything directly as a key
    # Let's check logic:
    # 1. joins whole list "text-red-500". no match
    # 2. pops 500. joins "text-red". no match
    # 3. pops red. joins "text". match!
    # returns [['text', ['red', '500']]]

    res = tw.merge_first_term(["text", "red", "500"])
    assert len(res) > 0
    # Check if we have the expected split
    found = False
    for item in res:
        if item[0] == "text" and item[1] == ["red", "500"]:
            found = True
            break
    assert found

    # Test with something that needs merging
    # bg-red-500
    res = tw.merge_first_term(["bg", "red", "500"])
    # bg matches backgroundColor, backgroundImage, etc.
    found = False
    for item in res:
        if item[0] == "bg" and item[1] == ["red", "500"]:
            found = True
            break
    assert found

    # Test merge logic where partial match works
    # e.g. "grid-cols-3" -> "gridTemplateColumns" uses "grid-cols" as key in TO_TAILWIND_NAME
    # ["grid", "cols", "3"] -> "grid-cols" match?
    res = tw.merge_first_term(["grid", "cols", "3"])
    found = False
    for item in res:
        if item[0] == "grid-cols" and item[1] == ["3"]:
            found = True
            break
    assert found

def test_process_opacity(tw):
    # Test hex to rgba conversion with opacity
    css = ".bg-red-500 {background-color: #ef4444;}"
    processed = tw.process_opacity(css, 50)
    assert "rgba" in processed
    assert "0.5" in processed
    # ef4444 -> 239, 68, 68
    assert "239, 68, 68" in processed

    # Test ignoring if alpha already present (not implemented in code, but code sets alpha to opacity/100 if alpha is 1)
    css_rgba = ".text-custom {color: #ffffff00;}"
    # hex_to_rgb handles 8 chars. alpha is 0.0.
    # process_opacity: if rgba[3] == 1: ...
    processed = tw.process_opacity(css_rgba, 50)
    # Alpha should remain 0.0 because it wasn't 1
    assert "rgba" in processed
    assert ", 0.0)" in processed

def test_hex_to_rgb(tw):
    assert tw.hex_to_rgb("#ffffff") == [255, 255, 255, 1.0]
    assert tw.hex_to_rgb("000000") == [0, 0, 0, 1.0]
    assert tw.hex_to_rgb("#fff") == [255, 255, 255, 1.0]
    assert tw.hex_to_rgb("#ff000080") == [255, 0, 0, 128/255.0]

def test_process_result_value(tw):
    # Hover
    res = tw.process_result_value(".foo {color: red;}", ["hover"])
    assert ".foo:hover {color: red;}" == res

    # Dark mode
    res = tw.process_result_value(".foo {color: white;}", ["dark"])
    assert "@media (prefers-color-scheme: dark) {.foo {color: white;}}" == res

    # Light mode
    res = tw.process_result_value(".foo {color: black;}", ["light"])
    assert "@media (prefers-color-scheme: light) {.foo {color: black;}}" == res

    # Media query sm
    res = tw.process_result_value(".foo {width: 100%;}", ["sm"])
    assert "@media (min-width: 640px) {.foo {width: 100%;}}" == res

    # Multiple processors (hover + sm)
    # Order matters: sm wraps hover
    res = tw.process_result_value(".foo {color: red;}", ["hover", "sm"])
    assert "@media (min-width: 640px) {.foo:hover {color: red;}}" == res

    # Pseudo-elements
    res = tw.process_result_value(".foo {content: '';}", ["before"])
    assert ".foo::before {content: '';}" == res

    # Undefined processor
    res = tw.process_result_value(".foo {color: red;}", ["unknown"])
    # It should return empty string because processors list is not empty (contains "unknown"),
    # but "unknown" is filtered out, so `fin` is empty.
    # Note: If filtering logic is used, and no valid processors found, it returns "".
    assert "" == res

    # Multiple valid + one unknown
    # "unknown" is ignored. "hover" is applied.
    res = tw.process_result_value(".foo {color: red;}", ["hover", "unknown"])
    assert ".foo:hover {color: red;}" == res

def test_sanitize_class_name(tw):
    assert tw.sanitize_class_name("w-1/2") == "w-1\\/2"
    assert tw.sanitize_class_name("hover:bg-red-500") == "hover\\:bg-red-500"
    assert tw.sanitize_class_name("[&_p]:mt-4") == "\\[&_p\\]\\:mt-4"

    # Test space-x / space-y special handling
    res = tw.sanitize_class_name("space-x-4")
    assert res.endswith(" > * + *")
    assert "space-x-4" in res

def test_normalize_property_value(tw):
    # String
    assert tw.normalize_property_value("10px") == "10px"
    # List of strings
    assert tw.normalize_property_value(["10px", "solid", "red"]) == "10px, solid, red"
    # Dict
    assert tw.normalize_property_value({"color": "red", "background": "white"}) == "color:red;background:white;"

    # List where [0] is string and [1] is dict
    # Used in fontSize in classes.py: ['0.75rem', {"lineHeight": '1rem'}]
    res = tw.normalize_property_value(['1rem', {"lineHeight": '1.5rem'}])
    assert "1rem;" in res
    assert "line-height:1.5rem;" in res

    # List where items are not strings/dicts (fallback)
    # The code says: for i in value: if not isinstance(i, str): break. else: join.
    # If it breaks, it might return empty string or partial?
    # Actually, if the loop breaks, `else` block of for-loop is skipped. result remains "".
    # Wait, the code:
    #             else:
    #                 for i in value:
    #                     if not isinstance(i, str):
    #                         break
    #                 else:
    #                     result = ", ".join(value)
    # So if there is a non-string, result is "".
    assert tw.normalize_property_value([1, 2]) == ""

def test_generate_simple(tw):
    html = '<div class="text-center p-4"></div>'
    css = tw.generate(html)
    assert ".text-center" in css
    assert "text-align: center;" in css
    assert ".p-4" in css
    assert "padding: 1rem;" in css

def test_generate_colors(tw):
    html = '<div class="text-red-500 bg-blue-500"></div>'
    css = tw.generate(html)
    assert ".text-red-500" in css
    assert "color: #ef4444;" in css
    assert ".bg-blue-500" in css
    assert "background-color: #3b82f6;" in css

def test_generate_opacity(tw):
    html = '<div class="text-red-500/50"></div>'
    css = tw.generate(html)
    assert ".text-red-500\\/50" in css
    assert "rgba(239, 68, 68, 0.5)" in css

def test_generate_invalid_opacity(tw):
    html = '<div class="text-red-500/xyz"></div>'
    css = tw.generate(html)
    # Should default to 100 opacity (no rgba replacement for hex)
    # text-red-500 is #ef4444
    # Note: Depending on how splitting happens, the class name might be sanitized differently
    # or the split logic might fail to produce "text-red-500" cleanly if "/" logic was botched.
    # The expected behavior after fix:
    # i = "text-red-500". j matches "text-red-500".
    # css generated for ".text-red-500\/xyz" (ori_i).
    print(f"DEBUG CSS: {css}")
    assert ".text-red-500\\/xyz" in css
    assert "#ef4444" in css
    assert "rgba" not in css

def test_generate_variants(tw):
    html = '<div class="hover:text-red-500 sm:bg-white dark:text-white"></div>'
    css = tw.generate(html)
    assert ".hover\\:text-red-500:hover" in css
    assert "@media (min-width: 640px) {.sm\\:bg-white" in css
    assert "@media (prefers-color-scheme: dark) {.dark\\:text-white" in css

def test_generate_arbitrary_values(tw):
    html = '<div class="w-[100px] bg-[#123456]"></div>'
    css = tw.generate(html)
    assert ".w-\\[100px\\]" in css
    assert "width: 100px;" in css
    assert ".bg-\\[\\#123456\\]" in css
    assert "background-color: #123456;" in css

def test_generate_multi_requirement(tw):
    # px-4 -> padding-left, padding-right
    # In classes.py, paddingLeftRight -> paddingRight in MULTI_REQUIREMENT
    html = '<div class="px-4"></div>'
    css = tw.generate(html)
    assert ".px-4" in css
    assert "padding-left" in css
    assert "padding-right" in css

def test_generate_gradients(tw):
    # from-red-500 via-blue-500 to-green-500
    html = '<div class="from-red-500 via-blue-500 to-green-500 bg-gradient-to-r"></div>'
    css = tw.generate(html)
    assert ".from-red-500" in css
    assert "--tw-gradient-from: #ef4444" in css
    assert ".via-blue-500" in css
    assert ".to-green-500" in css

    # Check if they are appended at the end (generate method logic puts them at end)
    # We can't strictly check order in string easily without regex or index search,
    # but the method `generate` explicitly reorders them.
    # Just checking existence is enough for coverage of the branches.

def test_generate_filter(tw):
    # blur-sm -> filter: blur(4px)
    # 'filter' is added if gp == 'filter' and 'filter' not in j
    html = '<div class="blur-sm"></div>'
    css = tw.generate(html)
    assert ".blur-sm" in css
    # classes.py: filter -> blur -> sm
    # In generate: if len(j) == 2. gp="filter". j=["blur", "sm"]. "filter" not in j.
    # Inserts filter. j becomes ["filter", "blur", "sm"].
    # Then len(j) == 3 logic picks it up?
    # Wait, the code says:
    # if len(j) == 2:
    #    if gp == "filter": ... j.insert(0, "filter")
    #    res = self.classes[gp].get(j[1], "")
    #    ...
    # If j is modified to length 3, does it fall through to len(j)==3 block?
    # No, it's `if len(j) == 2`, then next `if len(j) == 3`.
    # So if j becomes len 3, it will trigger the next block.

    assert "blur(4px)" in css

def test_generate_dynamic_multi(tw):
    # Dynamic value that is in MULTI_REQUIREMENT
    # e.g. mx-[10px] -> margin-left: 10px; margin-right: 10px;
    html = '<div class="mx-[10px]"></div>'
    css = tw.generate(html)
    assert ".mx-\\[10px\\]" in css
    # Generated CSS: .mx-\[10px\] {margin-left: 10px;margin-right:10px;;}
    assert "margin-left: 10px;" in css
    assert "margin-right:10px;" in css

def test_unknown_class(tw):
    html = '<div class="unknown-class"></div>'
    css = tw.generate(html)
    assert "unknown-class" not in css

def test_class_with_colon_no_processor(tw):
    # "foo:bar" where "foo" is not a processor.
    # code: k = j[0].split(":"). processors = k. k.pop(). j[0] = k[-1] (which is "bar"?)
    # Wait: k=["foo", "bar"]. j[0]="bar". k.pop() -> removes "bar". processors=["foo"].
    # "foo" is not in ordered_processors_list. process_result_value will return "".
    html = '<div class="foo:text-red-500"></div>'
    css = tw.generate(html)
    # Should not generate CSS because processor "foo" is unknown/invalid
    assert "foo\\:text-red-500" not in css

def test_deep_nested_class(tw):
    # We need to test len(j) == 4 case in generate
    # Mock classes to have 3 levels of nesting
    tw.classes["mockGroup"] = {"level1": {"level2": {"level3": "mockValue"}}}
    tw.to_tailwind_name["mockGroup"] = "mockGroup" # map a class to this group

    # We need merge_first_term to produce 4 items.
    # Input: mockGroup-level1-level2-level3
    # merge_first_term will match "mockGroup" (if we add it to to_tailwind_name)

    # We need to hack TO_TAILWIND_NAME as well, which is imported in __init__
    # But tw.to_tailwind_name is instance variable.
    tw.to_tailwind_name["mockGroup"] = "mockGroup"

    html = '<div class="mockGroup-level1-level2-level3"></div>'
    css = tw.generate(html)
    assert "mockValue" in css

def test_container_arbitrary(tw):
    # container-[100px] -> matches container group.
    # container is in CLASSES but not DYNAMIC_VALUE.
    # Should fall through to else branch in len(j)==2 logic.
    html = '<div class="container-[100px]"></div>'
    css = tw.generate(html)
    assert ".container-\\[100px\\]" in css
    assert "container: 100px;" in css

def test_empty_class_attribute(tw):
    html = '<div class=""></div>'
    css = tw.generate(html)
    assert css == ""

def test_multiple_same_class(tw):
    html = '<div class="p-4 p-4"></div>'
    css = tw.generate(html)
    # Should generate only once
    assert css.count(".p-4") == 1

def test_class_with_newline(tw):
    html = '<div class="p-4\nm-4"></div>'
    css = tw.generate(html)
    assert ".p-4" in css
    assert ".m-4" in css

def test_variants_with_opacity(tw):
    # hover:bg-red-500/50
    html = '<div class="hover:bg-red-500/50"></div>'
    css = tw.generate(html)
    # Selector: .hover\:bg-red-500\/50:hover
    assert ".hover\\:bg-red-500\\/50:hover" in css
    # RGBA check
    assert "rgba(239, 68, 68, 0.5)" in css

def test_missing_property_in_dict(tw):
    # Coverage for "if not res: res = ... DEFAULT" logic
    # Need a group where j[1] is found but it's a dict and doesn't have DEFAULT?
    # Or res is empty.
    # But most classes in CLASSES have DEFAULT.
    pass

def test_no_classes_found(tw):
    html = '<div></div>'
    css = tw.generate(html)
    assert css == ""

def test_hex_shorthand_opacity(tw):
    # #f00 -> #ff0000. Opacity 50% -> 0.5.
    html = '<div class="bg-[#f00]/50"></div>'
    css = tw.generate(html)
    assert "rgba(255, 0, 0, 0.5)" in css

def test_hex_alpha_opacity(tw):
    # #ff0000ff. Alpha is 1.0. Opacity 50% -> 0.5.
    html = '<div class="bg-[#ff0000ff]/50"></div>'
    css = tw.generate(html)
    assert "rgba(255, 0, 0, 0.5)" in css

    # #ff000080. Alpha is 0.5. Opacity 50% -> 0.5 (code logic: if rgba[3] == 1: apply opacity).
    # So it should remain 0.5 from the color itself.
    html = '<div class="bg-[#ff000080]/50"></div>'
    css = tw.generate(html)
    # 0x80 = 128. 128/255 ~= 0.50196.
    # The code prints string(i).
    assert "rgba(255, 0, 0, 0.50196" in css

def test_process_opacity_multiple_colors(tw):
    # Two colors in one property (e.g. gradient or shadow).
    # shadow-[#f00_#00f]/50. Arbitrary value with spaces might be tricky with sanitization.
    # Use spaces as underscores in arbitrary values is a Tailwind convention, logic: replace("_", " ").
    # Does pytailwind support _ replacement?
    # Not explicitly seen in generate.
    # But let's try manual hexes in a string processed by process_opacity directly.
    # Note: process_opacity regex requires space/quote before #.
    css = "background: linear-gradient( #f00, #00f);"
    processed = tw.process_opacity(css, 50)
    # #f00 -> rgba(255, 0, 0, 0.5)
    # #00f -> rgba(0, 0, 255, 0.5)
    assert "rgba(255, 0, 0, 0.5)" in processed
    assert "rgba(0, 0, 255, 0.5)" in processed

def test_border_x_0(tw):
    # border-x-0 maps to borderWidth -> x -> 0, which returns a list containing a dict.
    # This covers normalize_property_value branch for list[dict].
    html = '<div class="border-x-0"></div>'
    css = tw.generate(html)
    assert "border-left-width:0px;" in css
    assert "border-right-width:0px;" in css

def test_media_query_max(tw):
    html = '<div class="max-sm:hidden"></div>'
    css = tw.generate(html)
    print(f"DEBUG MAX: {css}")
    assert "@media (max-width: 640px)" in css
    assert "display: none;" in css
