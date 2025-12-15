
import pytest
from pytailwind import Tailwind

def test_config_screens_replace():
    config = {
        "theme": {
            "screens": {
                "mobile": "400px",
                "desktop": "1000px"
            }
        }
    }
    tw = Tailwind(config=config)

    # Old screens should NOT exist
    assert "sm" not in tw.media_queries
    assert "md" not in tw.media_queries

    # New screens should exist
    assert "mobile" in tw.media_queries
    assert "desktop" in tw.media_queries

    # Generated CSS should use new screens
    html_content = '<div class="mobile:text-center desktop:text-left sm:text-right"></div>'
    css = tw.generate(html_content)

    # mobile and desktop should be processed
    assert "@media (min-width: 400px)" in css
    assert "@media (min-width: 1000px)" in css

    # sm should NOT be processed as a media query (or at least not the default one)
    # Since 'sm' is not in media_queries, generate() logs "UNDEFINED PROCESSSOR : sm" and returns "" for that part.
    # So we expect "sm:text-right" to produce nothing.
    assert "text-align: right" not in css

def test_config_screens_order():
    # Define screens in non-ascending order
    config = {
        "theme": {
            "screens": {
                "lg": "1000px",
                "sm": "500px"
            }
        }
    }
    tw = Tailwind(config=config)

    # Check processor order
    processors = tw.media_query_processors
    # Should be sorted by width: sm (500), lg (1000)
    # Note: 'max-sm' and 'max-lg' are also generated and added.
    # 'max-sm' width is 500. 'max-lg' width is 1000.
    # Stable sort might keep them relative to their pairs?
    # get_width_value extracts 500 for both sm and max-sm.

    sm_index = processors.index("sm")
    lg_index = processors.index("lg")

    assert sm_index < lg_index
