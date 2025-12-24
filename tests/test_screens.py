
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

    # sm should NOT be processed as a media query (since 'sm' is not in media_queries)
    # In the new generator, it may still generate the class but not wrapped in media query
    # The key check is that it's NOT wrapped in the default sm breakpoint
    assert "@media (width >= 40rem)" not in css

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
