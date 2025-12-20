import os

import pytest

from pytailwind import Tailwind


@pytest.fixture
def tw():
    return Tailwind()

def test_filter_auto_insert(tw):
    pass

def test_blur_sm_generation(tw):
    # Verify what blur-sm actually produces
    css = tw.generate('<div class="blur-sm"></div>')
    assert "blur(4px)" in css

def test_arbitrary_value_nested_len_3(tw):
    # len(j) == 3. j matches classes[gp][j[1]][j[2]].
    # arbitrary value logic:
    # if j[-1].startswith("["): if not res: res = j[-1]...
    # Need a case where len(j)=3, last is arbitrary, and standard lookup fails.
    # text-red-[123px].
    # classes["textColor"]["red"] exists.
    # But 123px is invalid color.
    # With improved validation, this should NOT generate anything invalid.
    html = '<div class="text-red-[123px]"></div>'
    css = tw.generate(html)
    # Expect empty because 123px is not a valid color for textColor
    assert "color: 123px" not in css
    # Also verify it doesn't generate fontSize
    assert "font-size" not in css

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
    res = tw.process_result_value(".foo {}", ["first-letter"])
    # Should print and return ""
    assert res == ""

def test_merge_first_term_no_match(tw):
    # merge_first_term with list that has no match
    res = tw.merge_first_term(["unknown", "class"])
    # Should return empty list?
    assert res == []

def test_drop_shadow_sm(tw):
    # drop-shadow-sm -> filter: drop-shadow(...)
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
    os.remove(input_file)
    os.remove("output.css")
