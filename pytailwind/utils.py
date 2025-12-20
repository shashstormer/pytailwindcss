import json
import os
import re


def load_config(config_path):
    """
    Loads Tailwind configuration from a file.
    Supports JSON files directly.
    Attempts to parse JS files that export a simple object.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    if config_path.endswith(".json"):
        with open(config_path, "r") as f:
            return json.load(f)
    elif config_path.endswith(".js"):
        # Basic parsing for JS config files
        # Expects: module.exports = { ... }
        # Or just { ... }
        with open(config_path, "r") as f:
            content = f.read()

        # Remove comments
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        # Try to find the object
        match = re.search(r'module\.exports\s*=\s*({.*})', content, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Maybe it's just the object?
            json_str = content.strip()
            if not (json_str.startswith("{") and json_str.endswith("}")):
                raise ValueError(
                    "Could not find configuration object in JS file. Please use JSON format for complex configurations.")

        # Naive conversion to JSON:
        # Quote keys if not quoted
        # This is very fragile.
        # Ideally user should use JSON.
        # But let's try to handle simple cases.

        # Remove trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        # Quote keys: key: value -> "key": value
        # This regex is tricky.
        # matches key without quotes followed by :
        # But exclude inside strings.
        # For now, let's just use strict JSON parsing and tell user to provide valid JSON in the JS object structure
        # (which is mostly compatible except for quotes on keys and trailing commas).

        # Actually, let's try using `ast.literal_eval` if it looks like Python dict? No, JS uses true/false/null.

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to fix keys
            # Replace unquoted keys with quoted keys
            # (\w+)\s*: -> "$1":
            # But be careful about http://...
            pass

        try:
            # Very simple regex replace for unquoted keys
            fixed_json = re.sub(r'(?<!")(\b[a-zA-Z0-9_]+\b)(?!")\s*:', r'"\1":', json_str)
            return json.loads(fixed_json)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Could not parse JS config file. Please ensure it is valid JSON syntax or use a .json file. Error: {e}")

    else:
        raise ValueError("Unsupported config file extension. Use .json or .js")


def extract_candidates(content):
    """
    Extracts potential class strings from content.
    Looks for:
    1. Strings inside quotes: "...", '...', `...`
    2. Strings inside class=... attributes (if unquoted, though rare)
    """
    candidates = []
    # Match strings inside quotes.
    # Group 1: Quote char
    # Group 2: Content
    # We allow escaped quotes inside via (?:\\. | [^...])*
    # But for simplicity and speed, we use non-greedy matching which works for valid code usually.
    # r'(["\'`])((?:\\\1|.)*?)\1'
    pattern = re.compile(r'(["\'`])((?:\\\1|.)*?)\1', re.DOTALL)

    for match in pattern.finditer(content):
        inner = match.group(2)
        candidates.append(inner)
        # Recurse: if the content contains quotes, it might be nested (e.g. JS template literal)
        if any(q in inner for q in ["'", '"', "`"]):
            candidates.extend(extract_candidates(inner))

    return candidates


def split_classes(class_string):
    """
    Splits a string of classes by whitespace, respecting brackets [].
    "w-full bg-[url('...')] hover:bg-red-500" -> ["w-full", "bg-[url('...')]", "hover:bg-red-500"]
    """
    classes = []
    current = []
    bracket_depth = 0
    quote = None

    for char in class_string:
        if quote:
            current.append(char)
            if char == quote:
                # Check if previous char was backslash?
                # For simplicity, assume simple quoting.
                # If we want to handle escaped quotes inside arbitrary values:
                # But typically arbitrary values are like [url('...')] or [theme('...')]
                quote = None
        elif char in ["'", '"']:
            quote = char
            current.append(char)
        elif char == '[':
            bracket_depth += 1
            current.append(char)
        elif char == ']':
            if bracket_depth > 0:
                bracket_depth -= 1
            current.append(char)
        elif char.isspace() and bracket_depth == 0 and quote is None:
            if current:
                classes.append("".join(current))
                current = []
        else:
            current.append(char)

    if current:
        classes.append("".join(current))

    return classes


def split_by_hyphen(text):
    """
    Splits a string by hyphen '-', respecting brackets [].
    "w-[calc(100%-20px)]" -> ["w", "[calc(100%-20px)]"]
    "bg-red-500" -> ["bg", "red", "500"]
    """
    parts = []
    current = []
    bracket_depth = 0

    for char in text:
        if char == '[':
            bracket_depth += 1
            current.append(char)
        elif char == ']':
            if bracket_depth > 0:
                bracket_depth -= 1
            current.append(char)
        elif char == '-' and bracket_depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)

    parts.append("".join(current))
    return parts


def replace_underscores_safe(value):
    """
    Replace _ with space, but not inside quotes ' " ` or url(...).
    Tailwind treats _ as space in arbitrary values unless quoted/escaped.
    """
    res = []
    quote = None
    i = 0
    while i < len(value):
        char = value[i]

        # Check for escaped char (basic handling)
        if char == '\\' and i + 1 < len(value):
            res.append(char)
            res.append(value[i + 1])
            i += 2
            continue

        if quote:
            res.append(char)
            if char == quote:
                quote = None
        elif char in ["'", '"', "`"]:
            quote = char
            res.append(char)
        elif char == "_":
            res.append(" ")
        else:
            res.append(char)
        i += 1
    return "".join(res)
