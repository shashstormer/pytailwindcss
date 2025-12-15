
import pytest
import json
import os
from pytailwind import Tailwind
from pytailwind.utils import load_config

def test_default_generation():
    tw = Tailwind()
    html_content = '<div class="text-red-500 m-4"></div>'
    css = tw.generate(html_content)
    assert ".text-red-500 {color: #ef4444;}" in css
    assert ".m-4 {margin: 1rem;}" in css

def test_unknown_class_no_generation():
    tw = Tailwind()
    html_content = '<div class="text-brand-500"></div>'
    css = tw.generate(html_content)
    assert "brand" not in css
    assert "#123456" not in css

def test_config_extend_colors():
    config = {
        "theme": {
            "extend": {
                "colors": {
                    "brand": {
                        "500": "#123456"
                    }
                }
            }
        }
    }
    tw = Tailwind(config=config)
    html_content = '<div class="text-brand-500 bg-brand-500 border-brand-500"></div>'
    css = tw.generate(html_content)

    assert ".text-brand-500 {color: #123456;}" in css
    assert ".bg-brand-500 {background-color: #123456;}" in css
    assert ".border-brand-500 {border-color: #123456;}" in css

    # Check that defaults still exist
    html_content_default = '<div class="text-red-500"></div>'
    css_default = tw.generate(html_content_default)
    assert ".text-red-500 {color: #ef4444;}" in css_default

def test_config_override_colors():
    config = {
        "theme": {
            "colors": {
                "brand": {
                    "500": "#123456"
                }
            }
        }
    }
    tw = Tailwind(config=config)

    # Brand should exist
    html_content = '<div class="text-brand-500"></div>'
    css = tw.generate(html_content)
    assert ".text-brand-500 {color: #123456;}" in css

    # Defaults should NOT exist (since we didn't extend, we replaced)
    html_content_default = '<div class="text-red-500"></div>'
    css_default = tw.generate(html_content_default)
    # Depending on implementation, it might generate nothing or fail to find color
    # My implementation clears self.colors if theme.colors is present.
    # So text-red-500 should produce nothing.
    assert "color: #ef4444" not in css_default

def test_config_spacing():
    config = {
        "theme": {
            "extend": {
                "spacing": {
                    "128": "32rem"
                }
            }
        }
    }
    tw = Tailwind(config=config)
    html_content = '<div class="m-128 p-128 w-128 h-128"></div>'
    css = tw.generate(html_content)

    assert ".m-128 {margin: 32rem;}" in css
    assert ".p-128 {padding: 32rem;}" in css
    assert ".w-128 {width: 32rem;}" in css
    assert ".h-128 {height: 32rem;}" in css

def test_config_screens():
    config = {
        "theme": {
            "extend": {
                "screens": {
                    "3xl": "1600px"
                }
            }
        }
    }
    tw = Tailwind(config=config)
    html_content = '<div class="3xl:text-center"></div>'
    css = tw.generate(html_content)

    assert "@media (min-width: 1600px) {.3xl\\:text-center {text-align: center;}}" in css

def test_load_config_json(tmp_path):
    config_data = {
        "theme": {
            "extend": {
                "colors": {"custom": "#aabbcc"}
            }
        }
    }
    config_file = tmp_path / "tailwind.config.json"
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    loaded_config = load_config(str(config_file))
    assert loaded_config == config_data

def test_load_config_js_simple(tmp_path):
    js_content = """
    module.exports = {
        "theme": {
            "extend": {
                "colors": {
                    "custom": "#aabbcc"
                }
            }
        }
    }
    """
    config_file = tmp_path / "tailwind.config.js"
    with open(config_file, "w") as f:
        f.write(js_content)

    loaded_config = load_config(str(config_file))
    assert loaded_config["theme"]["extend"]["colors"]["custom"] == "#aabbcc"

def test_load_config_js_unquoted_keys(tmp_path):
    js_content = """
    module.exports = {
        theme: {
            extend: {
                colors: {
                    custom: "#aabbcc"
                }
            }
        }
    }
    """
    config_file = tmp_path / "tailwind.config.js"
    with open(config_file, "w") as f:
        f.write(js_content)

    loaded_config = load_config(str(config_file))
    assert loaded_config["theme"]["extend"]["colors"]["custom"] == "#aabbcc"
