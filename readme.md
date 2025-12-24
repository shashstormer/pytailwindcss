# pyTailwindCSS

post v0.0.3 a lot of features have been added and i have used AI extensively to speed up development. Please report any issues you find.

* This is a module written to support generating basic TailwindCss using python only.
* This module was written as a subset of the [xtracto](https://github.com/shashstormer/xtracto) library then made into a seperate module to simplify contribution and development.
* You may fork and make a PR to [this repo]() to contribute to the development of this module.


# installation

```bash
pip install pytailwind
```

# USAGE 

```py
from pytailwind import Tailwind
tailwind = Tailwind()
page = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Simple Tailwind CSS Page</title>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
  <div class="text-center p-8 bg-white rounded shadow-lg">
    <h1 class="text-3xl font-bold text-blue-600 mb-4">Hello, Tailwind CSS!</h1>
    <p class="text-lg text-gray-700 mb-4">This is a simple example using Tailwind CSS.</p>
    <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700">Click Me</button>
  </div>
</body>
</html>

"""
tailwind_css_for_page = tailwind.generate(page)
print(tailwind_css_for_page)

# OPTION 1: generate css on the fly (recommended during development)
# OPTIONA 2: Save the css to a file (recommended for production environments)
with open("page.css", "wt") as f:
    f.write(tailwind_css_for_page)
```

# Features

**pyTailwindCSS** now supports a comprehensive set of **Tailwind CSS v4.1** features:

- **Core Utilities**: Full support for Layout, Flexbox, Grid, Spacing, Sizing, Typography, Backgrounds, Borders, Effects, Filters, Tables, Transitions, and Transforms.
- **Modern Theme System**: Complete implementation of v4 theme variables for colors, fonts, shadows, radii, and more.
- **Arbitrary Values**: Support for JIT-style arbitrary values (e.g., `w-[123px]`, `bg-[#bada55]`) and properties (e.g., `[mask-type:luminance]`).
- **Directives & Functions**: Support for `@apply`, `theme()`, and `--spacing()` via the Python API.
- **Variants**: extensive support for responsive variants (`sm:`, `lg:`), pseudo-classes (`hover:`, `focus:`), and dark mode.
- **Class Detection**: Intelligent extraction of classes from HTML, JSX, and template strings, including handling of complex whitespaces.
- **Preflight**: Includes Tailwind's base reset styles (Preflight) by default.

> **Note**: This is a high-level overview. For detailed usage, specific API references, and comprehensive examples, please refer to the **pytailwind v4.1 docs**.

# Features to implement
1. Config and extension of the default classes with .py config file.
2. Watch files and generate css file.
3. Add support for human-readable output and minified output (through config or/and CLI Options).
