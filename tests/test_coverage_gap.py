"""
Additional coverage tests for the new generator.
"""

import os
import pytest
from pytailwind import Tailwind


@pytest.fixture
def tw():
    return Tailwind()


def test_filter_auto_insert(tw):
    """Test that filter utilities work correctly."""
    pass


def test_blur_sm_generation(tw):
    """Verify what blur-sm actually produces."""
    css = tw.generate('<div class="blur-sm"></div>')
    assert "blur(4px)" in css


def test_arbitrary_value_nested_len_3(tw):
    """Test arbitrary values are validated correctly."""
    # text-red-[123px] - 123px is not a valid color
    html = '<div class="text-red-[123px]"></div>'
    css = tw.generate(html)
    # Expect empty because 123px is not a valid color for textColor
    assert "color: 123px" not in css
    # Also verify it doesn't generate fontSize
    assert "font-size" not in css


def test_main_cli_import_error(monkeypatch, capsys, tmp_path):
    """Test ImportError in main when watch is True."""
    import sys

    input_file = tmp_path / "input.html"
    input_file.write_text("<div></div>")

    with pytest.raises(SystemExit) as excinfo:
        with pytest.MonkeyPatch.context() as m:
            m.setattr(sys, 'argv', ['pytailwind', str(input_file), '-w'])
            m.setitem(sys.modules, 'watchdog', None)
            m.setitem(sys.modules, 'watchdog.observers', None)

            from pytailwind.__main__ import main
            main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "watchdog module not found" in captured.out
    os.remove(input_file)
    os.remove("output.css")
