# pyTailwindCSS

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

* Supports most [tailwind classes](https://tailwindcss.com/)
* Supports Hover, Focus, and Other States refer [tailwind guidelines](https://tailwindcss.com/docs/hover-focus-and-other-states).
* Most of existing tailwind classes can always be parsed using this library (some clases may be missed out please contact shashstormer or make a PR to this repo).

# Features to implement
1. Config and extension of the default classes with .py config file.
2. Watch files and generate css file.
3. Add support for human-readable output and minified output (through config or/and CLI Options).
