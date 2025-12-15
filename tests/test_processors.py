import pytest
from pytailwind import Tailwind

@pytest.fixture
def tw():
    return Tailwind()

@pytest.mark.parametrize("processor,expected_part", [
    ("hover", ":hover {"),
    ("focus", ":focus {"),
    ("active", ":active {"),
    ("visited", ":visited {"),
    ("first", ":first-child {"),
    ("last", ":last-child {"),
    ("odd", ":nth-child(odd) {"),
    ("even", ":nth-child(even) {"),
    ("disabled", ":disabled {"),
    ("group-hover", ".group:hover "),
    ("focus-within", ":focus-within {"),
    ("focus-visible", ":focus-visible {"),
    ("checked", ":checked {"),
    ("required", ":required {"),
    ("invalid", ":invalid {"),
    ("before", "::before {"),
    ("after", "::after {"),
    ("first-of-type", ":first-of-type {"),
    ("last-of-type", ":last-of-type {"),
    ("only-child", ":only-child {"),
    ("only-of-type", ":only-of-type {"),
    ("empty", ":empty {"),
    ("read-only", ":read-only {"),
    ("placeholder-shown", ":placeholder-shown {"),
    ("not-first", ":not(:first-child) {"),
    ("not-last", ":not(:last-child) {"),
    ("not-disabled", ":not(:disabled) {"),
    ("not-checked", ":not(:checked) {"),
    ("not-odd", ":not(:nth-child(odd)) {"),
    ("not-even", ":not(:nth-child(even)) {"),
    ("peer-hover", ".peer:hover ~ "),
    ("peer-focus", ".peer:focus ~ "),
    ("peer-active", ".peer:active ~ "),
    ("peer-checked", ".peer:checked ~ "),
    ("peer-required", ".peer:required ~ "),
    ("peer-invalid", ".peer:invalid ~ "),
    ("peer-placeholder-shown", ".peer:placeholder-shown ~ "),
    ("sm", "@media (min-width: 640px)"),
    ("md", "@media (min-width: 768px)"),
    ("lg", "@media (min-width: 1024px)"),
    ("xl", "@media (min-width: 1280px)"),
    ("2xl", "@media (min-width: 1536px)"),
    ("print", "@media print"),
    ("dark", "@media (prefers-color-scheme: dark)"),
    ("light", "@media (prefers-color-scheme: light)"),
    ("motion-safe", "@media (prefers-reduced-motion: no-preference)"),
    ("motion-reduce", "@media (prefers-reduced-motion: reduce)"),
    ("max-sm", "@media (max-width: 640px)"),
    ("max-md", "@media (max-width: 768px)"),
    ("max-lg", "@media (max-width: 1024px)"),
    ("max-xl", "@media (max-width: 1280px)"),
    ("max-2xl", "@media (max-width: 1536px)"),
    # Pseudo-elements in ordered list but check if logic supports them
    ("first-letter", "UNDEFINED PROCESSSOR"), # Wait, logic doesn't support first-letter explicitly in if/elif chain?
    ("first-line", "UNDEFINED PROCESSSOR"),
    ("marker", "UNDEFINED PROCESSSOR"),
    ("selection", "UNDEFINED PROCESSSOR"),
    ("backdrop", "UNDEFINED PROCESSSOR"),
    ("placeholder", "UNDEFINED PROCESSSOR"),
])
def test_all_processors(tw, processor, expected_part):
    # Some pseudo-elements are in ordered_processors_list but NOT in the if/elif chain
    # They will hit "UNDEFINED PROCESSSOR" branch and return empty string

    # Let's verify which ones are actually implemented in the loop
    # Code review of __init__.py shows:
    # before, after -> implemented
    # first-letter -> NOT implemented in loop?
    # first-line -> NOT implemented
    # marker -> NOT implemented
    # selection -> NOT implemented
    # backdrop -> NOT implemented
    # placeholder -> NOT implemented

    # So for these, result will be empty.

    css = ".foo {color: red;}"
    res = tw.process_result_value(css, [processor])

    if expected_part == "UNDEFINED PROCESSSOR":
        assert res == ""
    else:
        assert expected_part in res

def test_processor_combinations(tw):
    # Test combination like hover + sm
    res = tw.process_result_value(".foo {color: red;}", ["hover", "sm"])
    assert "@media (min-width: 640px)" in res
    assert ":hover" in res
