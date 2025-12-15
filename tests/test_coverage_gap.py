import pytest
from pytailwind import Tailwind
from pytailwind.defaults import COLORS, SPACING

@pytest.fixture
def tw():
    return Tailwind()

# ... existing tests ...
# I will append new tests to coverage gaps

def test_filter_auto_insert(tw):
    # Test len(j)==2, gp="filter", "filter" not in j
    # input: blur-sm. j=["blur", "sm"].
    # gp for "blur" is "filter".
    # "filter" not in ["blur", "sm"].
    # Inserts filter -> ["filter", "blur", "sm"].
    # Then loop continues? No, j is modified in place?
    # Loop over jz (j2, j3). j is created anew: j = [j2] + j3.
    # j is modified locally in the loop.
    # So next iteration of jz loop? No, inside `for gp in gps`.
    # j is modified.
    # Then `res = self.classes[gp].get(j[1], "")`.
    # j[1] is "blur". classes["filter"]["blur"] is dict.
    # res is dict.
    # `if isinstance(res, dict): res = res.get("DEFAULT", "")`.
    # classes["filter"]["blur"]["DEFAULT"] is "blur(8px)".
    # So `blur` (without sm) works?
    # `blur` -> `j=["blur"]`. `merge_first_term` -> `[["blur", []]]`. `j=["blur"]`.
    # `len(j)==1`. `classes["filter"]["blur"]` is dict. `res`=dict.
    # `if not res: ...`. `res` is dict (truthy).
    # `gp_res` set to "filter".
    # `normalize` a dict? `normalize_property_value({"sm":...})`.
    # `result += ...`.
    # It might produce garbage CSS if not handled carefully.

    # But `blur-sm`. `j=["blur", "sm"]`.
    # `gp`="filter".
    # `j` becomes `["filter", "blur", "sm"]`.
    # `res = classes["filter"].get("blur")` -> dict.
    # `res` becomes `res.get("DEFAULT")` -> "blur(8px)".
    # `gp_res`="filter".
    # Result: `.blur-sm {filter: blur(8px);}`?
    # Wait, `blur-sm` should map to `blur(4px)` (from `sm` key).
    # `classes["filter"]["blur"]["sm"]` is `blur(4px)`.
    # If `res` takes `DEFAULT`, it ignores `sm`.
    # This logic seems buggy for `blur-sm`.
    # Let's verify what `blur-sm` produces.
    pass

def test_blur_sm_generation(tw):
    # Verify what blur-sm actually produces
    css = tw.generate('<div class="blur-sm"></div>')
    # classes["filter"]["blur"] has "sm": "blur(4px)".
    # If generate logic takes DEFAULT, it gets "blur(8px)".
    # If it falls through to len(j)==3?
    # If j becomes ["filter", "blur", "sm"]. len(j) is 3.
    # It enters `if len(j) == 3`.
    # `res = classes["filter"]["blur"]["sm"]`. "blur(4px)".
    # So it relies on falling through to next if block?
    # `if len(j) == 2:` block executes.
    # Then `if len(j) == 3:` block executes.
    # If both execute, `res` is overwritten?
    # `res` is initialized inside `for gp in gps`.
    # `if len(j) == 2`. `res` set.
    # `if len(j) == 3`. `res` set (overwriting previous).
    # So `blur-sm` works because `len(j)==3` block runs and finds correct value.
    assert "blur(4px)" in css

def test_arbitrary_value_nested_len_3(tw):
    # len(j) == 3. j matches classes[gp][j[1]][j[2]].
    # arbitrary value logic:
    # if j[-1].startswith("["): if not res: res = j[-1]...
    # Need a case where len(j)=3, last is arbitrary, and standard lookup fails.
    # e.g. text-red-[123px]?
    # text-red-500 is len=3. ["text", "red", "500"].
    # text-red-[123px]. ["text", "red", "[123px]"].
    # classes["textColor"]["red"] has no "[123px]". `res` is empty.
    # `if not res: res = "123px"`.
    # `gp_res` = "textColor".
    # CSS: .text-red-\[123px\] {color: 123px;}
    html = '<div class="text-red-[123px]"></div>'
    css = tw.generate(html)
    assert "color: 123px" in css

def test_arbitrary_value_nested_len_4(tw):
    # len(j) == 4.
    # Mock classes to have 3 levels.
    tw.classes["mock"] = {"a": {"b": {"c": "val"}}}
    tw.to_tailwind_name["mock"] = "mock"
    # standard lookup
    html = '<div class="mock-a-b-c"></div>'
    css = tw.generate(html)
    assert "val" in css

    # arbitrary lookup
    # mock-a-b-[custom]
    html2 = '<div class="mock-a-b-[custom]"></div>'
    css2 = tw.generate(html2)
    assert "custom" in css2

def test_undefined_processor(tw):
    # Explicitly call process_result_value with processor not in list
    # (actually it's filtered out before loop, so loop doesn't run)
    # But if we modify filtered list...
    # The only way to hit "UNDEFINED PROCESSOR" print is if processor IS in ordered_list
    # but NOT handled in if/elif chain.
    # "first-letter" is such a case.
    res = tw.process_result_value(".foo {}", ["first-letter"])
    # Should print and return ""
    assert res == ""

def test_merge_first_term_no_match(tw):
    # merge_first_term with list that has no match
    res = tw.merge_first_term(["unknown", "class"])
    # Should return empty list?
    # Logic: while list: join. check. pop.
    # "unknown-class" -> no.
    # "unknown" -> no.
    # Returns []
    assert res == []

def test_drop_shadow_sm(tw):
    # drop-shadow-sm -> filter: drop-shadow(...)
    # Covers line 90 logic for filter auto-insert if j len 2
    # drop-shadow is in filter list but doesn't map to itself directly.
    # merge_first_term should find it via filter list?
    # No, merge_first_term checks if j matches gp (key) OR j in gp (list value).
    # "filter" key has list ["blur", ..., "drop-shadow"].
    # "drop-shadow" IS in that list.
    # So merge_first_term returns [["drop-shadow", ["sm"]]] associated with "filter".
    # j becomes ["drop-shadow", "sm"].
    # gp="filter".
    # len(j)=2.
    # if gp=="filter": True.
    # if "filter" not in j: True.
    # j.insert(0, "filter") -> ["filter", "drop-shadow", "sm"].
    # This hits line 90.
    html = '<div class="drop-shadow-sm"></div>'
    css = tw.generate(html)
    assert "drop-shadow" in css

def test_undefined_processor_print(tw, capsys):
    res = tw.process_result_value(".foo {}", ["first-letter"])
    captured = capsys.readouterr()
    assert "UNDEFINED PROCESSSOR" in captured.out
    assert res == ""

def test_main_cli_import_error(monkeypatch, capsys, tmp_path):
    # Test ImportError in main when watch is True
    # We need to simulate ImportError for watchdog
    import sys

    input_file = tmp_path / "input.html"
    input_file.write_text("<div></div>")

    with pytest.raises(SystemExit) as excinfo:
        # We need to ensure args.watch is True
        # And simulate ImportError
        with pytest.MonkeyPatch.context() as m:
            m.setattr(sys, 'argv', ['pytailwind', str(input_file), '-w'])
            # Mock modules to raise ImportError
            m.setitem(sys.modules, 'watchdog', None)
            m.setitem(sys.modules, 'watchdog.observers', None)

            from pytailwind.__main__ import main
            main()

    assert excinfo.value.code == 1
    # Check output
    captured = capsys.readouterr()
    assert "watchdog module not found" in captured.out
