from pytailwind import Tailwind

def test_text_decoration_style():
    tw = Tailwind()
    css = tw.generate('<div class="decoration-solid"></div>', include_preflight=False)
    assert '.decoration-solid {text-decoration-style: solid;}' in css
    assert '@layer utilities' in css

    css = tw.generate('<div class="decoration-double"></div>', include_preflight=False)
    assert '.decoration-double {text-decoration-style: double;}' in css

    css = tw.generate('<div class="decoration-dotted"></div>', include_preflight=False)
    assert '.decoration-dotted {text-decoration-style: dotted;}' in css

    css = tw.generate('<div class="decoration-dashed"></div>', include_preflight=False)
    assert '.decoration-dashed {text-decoration-style: dashed;}' in css

    css = tw.generate('<div class="decoration-wavy"></div>', include_preflight=False)
    assert '.decoration-wavy {text-decoration-style: wavy;}' in css

def test_text_decoration_thickness():
    tw = Tailwind()
    css = tw.generate('<div class="decoration-auto"></div>', include_preflight=False)
    assert '.decoration-auto {text-decoration-thickness: auto;}' in css

    css = tw.generate('<div class="decoration-from-font"></div>', include_preflight=False)
    assert '.decoration-from-font {text-decoration-thickness: from-font;}' in css

    css = tw.generate('<div class="decoration-0"></div>', include_preflight=False)
    assert '.decoration-0 {text-decoration-thickness: 0px;}' in css

    css = tw.generate('<div class="decoration-1"></div>', include_preflight=False)
    assert '.decoration-1 {text-decoration-thickness: 1px;}' in css

    # Arbitrary
    css = tw.generate('<div class="decoration-[3px]"></div>', include_preflight=False)
    assert r'.decoration-\[3px\] {text-decoration-thickness: 3px;}' in css

def test_text_decoration_color():
    tw = Tailwind()
    # Assuming default config has red-500 = #ef4444
    css = tw.generate('<div class="decoration-red-500"></div>', include_preflight=False)
    assert '.decoration-red-500 {text-decoration-color: #ef4444;}' in css

    css = tw.generate('<div class="decoration-[#aabbcc]"></div>', include_preflight=False)
    assert r'.decoration-\[\#aabbcc\] {text-decoration-color: #aabbcc;}' in css

def test_text_underline_offset():
    tw = Tailwind()
    css = tw.generate('<div class="underline-offset-auto"></div>', include_preflight=False)
    assert '.underline-offset-auto {text-underline-offset: auto;}' in css

    css = tw.generate('<div class="underline-offset-0"></div>', include_preflight=False)
    assert '.underline-offset-0 {text-underline-offset: 0px;}' in css

    # Arbitrary
    css = tw.generate('<div class="underline-offset-[3px]"></div>', include_preflight=False)
    assert r'.underline-offset-\[3px\] {text-underline-offset: 3px;}' in css

def test_content():
    tw = Tailwind()
    css = tw.generate('<div class="content-none"></div>', include_preflight=False)
    assert '.content-none {content: none;}' in css

    # Arbitrary content often needs quotes in the value
    css = tw.generate('<div class="content-[\'hello\']"></div>', include_preflight=False)
    assert r".content-\[\'hello\'\] {content: 'hello';}" in css

def test_hyphens():
    tw = Tailwind()
    css = tw.generate('<div class="hyphens-none"></div>', include_preflight=False)
    assert '.hyphens-none {hyphens: none;}' in css

    css = tw.generate('<div class="hyphens-manual"></div>', include_preflight=False)
    assert '.hyphens-manual {hyphens: manual;}' in css

    css = tw.generate('<div class="hyphens-auto"></div>', include_preflight=False)
    assert '.hyphens-auto {hyphens: auto;}' in css

def test_text_wrap():
    tw = Tailwind()
    css = tw.generate('<div class="text-wrap"></div>', include_preflight=False)
    assert '.text-wrap {text-wrap: wrap;}' in css

    css = tw.generate('<div class="text-nowrap"></div>', include_preflight=False)
    assert '.text-nowrap {text-wrap: nowrap;}' in css

def test_font_variant_numeric():
    tw = Tailwind()
    css = tw.generate('<div class="ordinal"></div>', include_preflight=False)
    assert '.ordinal {font-variant-numeric: ordinal;}' in css

    css = tw.generate('<div class="slashed-zero"></div>', include_preflight=False)
    assert '.slashed-zero {font-variant-numeric: slashed-zero;}' in css

def test_line_clamp():
    tw = Tailwind()
    none_css = tw.generate('<div class="line-clamp-none"></div>', include_preflight=False)
    assert 'overflow: visible;' in none_css
    assert '-webkit-line-clamp: none;' in none_css

    clamp2_css = tw.generate('<div class="line-clamp-2"></div>', include_preflight=False)
    assert '-webkit-line-clamp: 2;' in clamp2_css

    # Arbitrary
    clamp_arb = tw.generate('<div class="line-clamp-[7]"></div>', include_preflight=False)
    assert '-webkit-line-clamp: 7;' in clamp_arb

def test_list_style_image():
    tw = Tailwind()
    css = tw.generate('<div class="list-image-none"></div>', include_preflight=False)
    assert '.list-image-none {list-style-image: none;}' in css

    css = tw.generate('<div class="list-image-[url(x.png)]"></div>', include_preflight=False)
    assert r'.list-image-\[url\(x\.png\)\] {list-style-image: url(x.png);}' in css

def test_font_smoothing():
    tw = Tailwind()
    antialiased = tw.generate('<div class="antialiased"></div>', include_preflight=False)
    assert '-webkit-font-smoothing: antialiased;' in antialiased
    assert '-moz-osx-font-smoothing: grayscale;' in antialiased

    subpixel = tw.generate('<div class="subpixel-antialiased"></div>', include_preflight=False)
    assert '-webkit-font-smoothing: auto;' in subpixel
    assert '-moz-osx-font-smoothing: auto;' in subpixel

def test_decoration_conflict():
    tw = Tailwind()
    # decoration-[#000] should only match color, NOT thickness
    css = tw.generate('<div class="decoration-[#000]"></div>', include_preflight=False)
    assert 'text-decoration-color: #000;' in css
    assert 'text-decoration-thickness' not in css

def test_font_stretch():
    tw = Tailwind()
    css = tw.generate('<div class="font-stretch-expanded"></div>', include_preflight=False)
    assert '.font-stretch-expanded {font-stretch: expanded;}' in css

def test_font_family_arbitrary():
    tw = Tailwind()
    # font-[Open_Sans]
    css = tw.generate('<div class="font-[Open_Sans]"></div>', include_preflight=False)
    assert r'.font-\[Open_Sans\] {font-family: Open Sans;}' in css

    # font-(family-name:--my-font)
    css = tw.generate('<div class="font-(family-name:--my-font)"></div>', include_preflight=False)
    assert r'.font-\(family-name\:--my-font\) {font-family: var(--my-font);}' in css

    # font-(--my-font)
    css = tw.generate('<div class="font-(--my-font)"></div>', include_preflight=False)
    assert r'.font-\(--my-font\) {font-family: var(--my-font);}' in css

def test_font_size_extended():
    tw = Tailwind()
    # text-(length:--my-text-size)
    css = tw.generate('<div class="text-(length:--my-text-size)"></div>', include_preflight=False)
    assert r'.text-\(length\:--my-text-size\) {font-size: var(--my-text-size);}' in css

    # text-sm/6 (line-height modifier)
    css = tw.generate('<div class="text-sm/6"></div>', include_preflight=False)
    assert 'font-size: 0.875rem;' in css
    assert 'line-height: 1.5rem;' in css

    # text-lg/loose
    css = tw.generate('<div class="text-lg/loose"></div>', include_preflight=False)
    assert 'font-size: 1.125rem;' in css
    assert 'line-height: 2;' in css

def test_font_weight_extended():
    tw = Tailwind()
    # font-(weight:--my-font-weight)
    css = tw.generate('<div class="font-(weight:--my-font-weight)"></div>', include_preflight=False)
    assert r'.font-\(weight\:--my-font-weight\) {font-weight: var(--my-font-weight);}' in css

def test_font_stretch_extended():
    tw = Tailwind()
    # font-stretch-50%
    css = tw.generate('<div class="font-stretch-50%"></div>', include_preflight=False)
    assert r'.font-stretch-50\% {font-stretch: 50%;}' in css
