import os
import sys
import argparse
from unittest.mock import patch, MagicMock
import pytest
from pytailwind.__main__ import main
import watchdog

def test_cli_no_args(capsys):
    # Running without args should fail/exit because 'input' is required
    with patch.object(sys, 'argv', ['pytailwind']):
        try:
            main()
        except SystemExit:
            pass
    captured = capsys.readouterr()
    assert "error" in captured.err
    if os.path.exists("output.css"):
        os.remove("output.css")

def test_cli_generate_file(tmp_path):
    input_file = tmp_path / "index.html"
    input_file.write_text('<div class="text-red-500"></div>')
    output_file = tmp_path / "output.css"

    with patch.object(sys, 'argv', ['pytailwind', str(input_file), '-o', str(output_file)]):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    assert ".text-red-500" in content
    assert "color: #ef4444;" in content
    os.remove(output_file)

def test_cli_generate_folder(tmp_path):
    input_dir = tmp_path / "src"
    input_dir.mkdir()
    (input_dir / "page1.html").write_text('<div class="p-4"></div>')
    (input_dir / "page2.html").write_text('<div class="m-4"></div>')
    (input_dir / "ignored.txt").write_text('<div class="hidden"></div>')
    output_file = tmp_path / "style.css"

    with patch.object(sys, 'argv', ['pytailwind', str(input_dir), '-o', str(output_file)]):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    assert ".p-4" in content
    assert ".m-4" in content
    assert ".hidden" not in content # .txt files should be ignored
    os.remove(output_file)

def test_cli_watch_missing_watchdog(tmp_path, capsys):
    input_file = tmp_path / "index.html"
    input_file.write_text("")

    # Mock sys.modules to simulate missing watchdog
    with patch.dict(sys.modules, {'watchdog': None, 'watchdog.observers': None, 'watchdog.events': None}):
        with patch.object(sys, 'argv', ['pytailwind', str(input_file), '-w']):
             with pytest.raises(SystemExit):
                main()

    captured = capsys.readouterr()
    assert "watchdog module not found" in captured.out
    os.remove("output.css")
    os.remove(input_file)

# We can mock watchdog to test watch mode logic without actually running forever
def test_cli_watch_logic(tmp_path):
    input_file = tmp_path / "index.html"
    input_file.write_text('<div class="text-blue-500"></div>')
    output_file = tmp_path / "output.css"
    mock_observer_class = MagicMock()
    mock_observer_instance = mock_observer_class.return_value
    with patch.object(sys, 'argv', ['pytailwind', str(input_file), '-w', '-o', str(output_file)]):
        with patch('watchdog.observers.Observer', mock_observer_class):
            with patch('time.sleep', side_effect=KeyboardInterrupt):
                main()

    mock_observer_instance.schedule.assert_called()
    mock_observer_instance.start.assert_called()
    mock_observer_instance.stop.assert_called()

    # Check if CSS was generated initially
    assert output_file.exists()
    assert ".text-blue-500" in output_file.read_text()
    os.remove(output_file)
