
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
                 raise ValueError("Could not find configuration object in JS file. Please use JSON format for complex configurations.")

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
            raise ValueError(f"Could not parse JS config file. Please ensure it is valid JSON syntax or use a .json file. Error: {e}")

    else:
        raise ValueError("Unsupported config file extension. Use .json or .js")
