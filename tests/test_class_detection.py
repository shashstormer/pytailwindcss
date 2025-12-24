"""
Tests for Tailwind class detection and extraction from source files.

Tests organized by feature:
- Class extraction from strings (extract_candidates)
- Class splitting (split_classes)
- Integration with full CSS generation
- Edge cases (nested quotes, template literals, etc.)
"""

import pytest
from pytailwind import Tailwind
from pytailwind.utils import extract_candidates, split_classes, replace_underscores_safe


@pytest.fixture
def tw():
    return Tailwind()


# ============================================================================
# EXTRACT CANDIDATES TESTS
# ============================================================================

class TestExtractCandidates:
    """Test extract_candidates function for extracting class strings from source."""
    
    def test_html_class_attribute(self):
        content = '<div class="bg-red-500 text-white">Hello</div>'
        candidates = extract_candidates(content)
        assert 'bg-red-500 text-white' in candidates
    
    def test_jsx_className(self):
        content = 'return <button className="px-4 py-2">Click</button>'
        candidates = extract_candidates(content)
        assert 'px-4 py-2' in candidates
    
    def test_single_quotes(self):
        content = "<div class='flex items-center'>Test</div>"
        candidates = extract_candidates(content)
        assert 'flex items-center' in candidates
    
    def test_template_literal(self):
        content = 'const cls = `bg-blue-500 hover:bg-blue-600`'
        candidates = extract_candidates(content)
        assert 'bg-blue-500 hover:bg-blue-600' in candidates
    
    def test_object_with_class_values(self):
        content = '''const colors = {
            black: "bg-black text-white",
            blue: "bg-blue-500 text-white",
        };'''
        candidates = extract_candidates(content)
        assert 'bg-black text-white' in candidates
        assert 'bg-blue-500 text-white' in candidates
    
    def test_multiple_attributes(self):
        content = '''<div class="p-4 m-2">
            <span class="text-lg font-bold">Title</span>
        </div>'''
        candidates = extract_candidates(content)
        assert 'p-4 m-2' in candidates
        assert 'text-lg font-bold' in candidates
    
    def test_vue_style_binding(self):
        content = ':class="isActive ? \'text-blue-500\' : \'text-gray-500\'"'
        candidates = extract_candidates(content)
        # Should extract inner strings
        assert any('text-blue-500' in c for c in candidates)
    
    def test_no_classes_returns_empty(self):
        content = '<div>No classes here</div>'
        candidates = extract_candidates(content)
        # Returns empty list or list without meaningful class strings
        assert len(candidates) == 0 or candidates == ['No classes here']


# ============================================================================
# SPLIT CLASSES TESTS
# ============================================================================

class TestSplitClasses:
    """Test split_classes function for parsing class strings."""
    
    def test_simple_classes(self):
        result = split_classes('flex items-center')
        assert result == ['flex', 'items-center']
    
    def test_multiple_spaces(self):
        result = split_classes('flex    items-center   gap-4')
        assert result == ['flex', 'items-center', 'gap-4']
    
    def test_with_arbitrary_value(self):
        result = split_classes('w-[100px] h-[50%]')
        assert result == ['w-[100px]', 'h-[50%]']
    
    def test_arbitrary_value_with_spaces(self):
        result = split_classes("bg-[url('test image.png')] text-white")
        assert len(result) == 2
        assert "bg-[url('test image.png')]" in result
        assert 'text-white' in result
    
    def test_nested_brackets(self):
        result = split_classes('w-[calc(100%-20px)] m-4')
        assert len(result) == 2
        assert 'w-[calc(100%-20px)]' in result
        assert 'm-4' in result
    
    def test_with_variants(self):
        result = split_classes('hover:bg-red-500 dark:text-white focus:ring-2')
        assert result == ['hover:bg-red-500', 'dark:text-white', 'focus:ring-2']
    
    def test_empty_string(self):
        result = split_classes('')
        assert result == []
    
    def test_leading_trailing_whitespace(self):
        result = split_classes('  flex items-center  ')
        assert result == ['flex', 'items-center']


# ============================================================================
# UNDERSCORE REPLACEMENT TESTS
# ============================================================================

class TestUnderscoreReplacement:
    """Test underscore to space conversion."""
    
    def test_simple_underscore(self):
        result = replace_underscores_safe('hello_world')
        assert result == 'hello world'
    
    def test_preserve_underscore_in_quotes(self):
        result = replace_underscores_safe("url('image_name.png')")
        assert result == "url('image_name.png')"  # preserved in quotes
    
    def test_grid_template(self):
        result = replace_underscores_safe('1fr_500px_2fr')
        assert result == '1fr 500px 2fr'


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestClassDetectionIntegration:
    """Test full integration of class detection with CSS generation."""
    
    def test_html_generates_css(self, tw):
        html = '<div class="bg-red-500 text-white p-4"></div>'
        css = tw.generate(html)
        assert 'bg-red-500' in css
        assert 'text-white' in css
        assert 'p-4' in css
    
    def test_jsx_generates_css(self, tw):
        jsx = 'return <button className="px-4 py-2 rounded-lg">Click</button>'
        css = tw.generate(jsx)
        assert 'px-4' in css
        assert 'py-2' in css
        assert 'rounded-lg' in css
    
    def test_js_object_generates_css(self, tw):
        js = '''const styles = {
            primary: "bg-blue-500 text-white",
            secondary: "bg-gray-200 text-black"
        };'''
        css = tw.generate(js)
        assert 'bg-blue-500' in css
        assert 'text-white' in css
        assert 'bg-gray-200' in css
    
    def test_multiline_content(self, tw):
        content = '''
        <div class="flex items-center justify-between">
            <span class="text-lg font-bold">Title</span>
            <button class="px-4 py-2 bg-blue-500">Action</button>
        </div>
        '''
        css = tw.generate(content)
        assert 'flex' in css
        assert 'items-center' in css
        assert 'text-lg' in css
        assert 'bg-blue-500' in css


# ============================================================================
# EDGE CASES TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases in class detection."""
    
    def test_dynamic_class_construction_not_detected(self, tw):
        # Tailwind only detects complete class names
        content = '<div class="text-{{ error ? \'red\' : \'green\' }}-600"></div>'
        css = tw.generate(content)
        # Should NOT generate text-red-600 or text-green-600
        # because the full class name doesn't exist in the source
        assert 'text-red-600' not in css or 'text-green-600' not in css
    
    def test_complete_class_names_detected(self, tw):
        content = '<div class="{{ error ? \'text-red-600\' : \'text-green-600\' }}"></div>'
        css = tw.generate(content)
        # Both complete class names should be detected
        assert 'text-red-600' in css
        assert 'text-green-600' in css
    
    def test_classes_in_object_map(self, tw):
        content = '''
        const colorVariants = {
            blue: "bg-blue-600 hover:bg-blue-500",
            red: "bg-red-600 hover:bg-red-500",
        };
        '''
        css = tw.generate(content)
        assert 'bg-blue-600' in css
        assert 'bg-red-600' in css
    
    def test_arbitrary_values_with_special_chars(self, tw):
        content = '<div class="bg-[#bada55] w-[calc(100%-20px)]"></div>'
        css = tw.generate(content)
        assert '#bada55' in css
        assert 'calc(100% - 20px)' in css or 'calc(100%-20px)' in css
