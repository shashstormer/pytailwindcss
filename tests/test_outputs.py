from pytailwind import Tailwind
import os


def test_outputs():
    tw = Tailwind()

    all_classes = []

    # 1. Generate all values for each class
    # Iterate over mapping to find prefixes
    for group_name, prefix_data in tw.to_tailwind_name.items():
        if isinstance(prefix_data, list):
            prefixes = prefix_data
        else:
            prefixes = [prefix_data]

        for prefix in prefixes:
            # Skip if prefix is likely a value itself (e.g. "block" in display group)
            # Actually to_tailwind_name for display is ["block", "inline", ...]
            # For these, the class name IS the prefix.

            # Check if group exists in classes
            if group_name not in tw.classes:
                continue

            class_values = tw.classes[group_name]

            if isinstance(class_values, dict):
                # If prefix is a key in the values (like 'block' in display), it's a standalone class
                # But to_tailwind_name mapping is messy.
                # Let's rely on reversing: for a group, we have values.
                # If to_tailwind_name entry is a list of strings that matches keys in classes[group], then class is just that string.

                # Heuristic:
                # If prefix matches a key in class_values, it's likely a standalone class.
                if prefix in class_values:
                    all_classes.append(prefix)
                    continue

                # Otherwise, it's a prefix-value structure (e.g. bg-red-500)
                for key, val in class_values.items():
                    if key == "DEFAULT":
                        all_classes.append(prefix)
                        continue

                    # Recursive check for nested dicts (like colors: red: {500: ...})
                    if isinstance(val, dict):
                        for sub_key in val:
                            if sub_key == "DEFAULT":
                                all_classes.append(f"{prefix}-{key}")
                            else:
                                all_classes.append(f"{prefix}-{key}-{sub_key}")
                    else:
                        all_classes.append(f"{prefix}-{key}")
            else:
                # Value is likely directly mapped or handled strangely?
                pass

    # Deduplicate
    all_classes = sorted(list(set(all_classes)))

    # 2. Generate state variants
    # States: pseudo_class_processors, media_query_processors, pseudo_element_processors
    states = []
    states.extend(tw.pseudo_class_processors)
    states.extend(tw.media_query_processors)
    states.extend(tw.pseudo_element_processors)

    # 3 representative classes
    # Use simple, robust ones
    sample_classes = ["text-center", "bg-red-500", "p-4"]

    state_classes = []
    for state in states:
        for cls in sample_classes:
            state_classes.append(f"{state}:{cls}")

    # Combine everything
    full_list = all_classes + state_classes

    # Create HTML
    html_content = ""
    for cls in full_list:
        html_content += f'<div class="{cls}"></div>\n'

    # Generate CSS
    css_output = tw.generate(html_content)

    with open("test_outputs.css", "w") as f:
        f.write(css_output)

    print(f"Generated {len(full_list)} classes into test_outputs.css")
    os.remove("test_outputs.css")


if __name__ == "__main__":
    test_outputs()
