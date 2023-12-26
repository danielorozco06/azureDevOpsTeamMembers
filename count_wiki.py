"""File"""

import json


def read_and_convert_to_json_list(file_path: str) -> list[dict[str, str]]:
    """Reads a file and converts it to a JSON list."""
    with open(file_path, "r") as file:
        content = json.load(file)
        return content


def create_json_file(path_file: str, data: list[dict[str, str]]) -> None:
    """Create a json file with the provided data."""
    # Use "w" mode to overwrite existing file
    with open(path_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    try:
        content = read_and_convert_to_json_list("data.json")

        if not content:
            print("No content")
            exit()

        new_content = []
        for page in content:
            path = page["path"]
            if "/Lineamientos Areas Transversales de TI/DevOps/" in path:
                views = len(page["viewStats"]) if page["viewStats"] else 0
                obj = {"path": path, "views": views}
                new_content.append(obj)

        # sort by views
        new_content.sort(key=lambda x: x["views"], reverse=True)
        create_json_file("data2.json", new_content)

        print("Finish")
    except Exception as error:
        print(error)
