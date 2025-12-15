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

# We can mock watchdog to test watch mode logic without actually running forever
def test_cli_watch_logic(tmp_path):
    input_file = tmp_path / "index.html"
    input_file.write_text('<div class="text-blue-500"></div>')
    output_file = tmp_path / "output.css"

    # Mock Observer and Handler
    mock_observer_class = MagicMock()
    mock_observer_instance = mock_observer_class.return_value

    # We need to interrupt the loop.
    # The loop is:
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()

    # We need to patch where it is imported. In __main__.py:
    # from watchdog.observers import Observer

    # Since we are running main(), the import happens inside main().
    # But imports are cached in sys.modules.
    # If watchdog is installed, it will import the real one.
    # We want to mock it.

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
