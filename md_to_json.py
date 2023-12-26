"""File to create the dataset."""
import json
import os

import markdown_to_json


def flatten(
    json_file_path: str,
    current_dict: dict[str],
    parent_key: str,
    flattened_dict: dict[str],
) -> dict[str]:
    """Recursively flattens a nested dictionary"""
    for key, value in current_dict.items():
        new_key = f"{parent_key} - {key}".replace("**", "").strip(" -")
        if isinstance(value, dict):
            flatten(json_file_path, value, new_key, flattened_dict)
        else:
            flattened_dict[f"{json_file_path} - {new_key}"] = value


def flatten_json(json_file_path: str, json_obj: dict[str]) -> dict[str]:
    """Flattens a JSON object into a single-level dictionary."""
    try:
        flattened = {}
        flatten(json_file_path, json_obj, "", flattened)
        return flattened
    except Exception as e:
        print(f"Error: {e}")
        return {}


def write_json_file(json_data: dict[str], json_file_path: str) -> None:
    """Write the .json file."""
    try:
        json_string = json.dumps(json_data, ensure_ascii=False, indent=4)
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json_file.write(json_string)
    except Exception as e:
        print(f"Error: {e}")


def convert_md_to_json(md_file_path: str) -> dict[str]:
    """Convert .md file to .json."""
    try:
        with open(md_file_path, "r", encoding="utf-8") as md_file:
            md_content = md_file.read()

        if not md_content:
            print(f"Warning: {md_file_path} is empty.")
            return {}

        return markdown_to_json.dictify(md_content)

    except Exception as e:
        print(f"Error: {e}")


def get_script_dir() -> str:
    """Get the directory containing the script."""
    script_path = os.path.abspath(__file__)
    return os.path.dirname(script_path)


def get_md_files(path: str) -> list[str]:
    """Traverse subdirectories and get .md files."""
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(path)
        for file in files
        if file.endswith(".md")
    ]


if __name__ == "__main__":
    # Get the directory containing the script
    script_dir = get_script_dir()

    # Construct the full path to the zip file
    file = "pages"
    path = os.path.join(script_dir, file)

    # Traverse subdirectories and convert files
    md_files = get_md_files(path)
    for md_file_path in md_files:
        json_file_path = md_file_path.replace(".md", ".json")
        json_data = convert_md_to_json(md_file_path)

        relative_path = os.path.relpath(md_file_path, script_dir)
        flattened_json = flatten_json(relative_path, json_data)
        write_json_file(flattened_json, json_file_path)
