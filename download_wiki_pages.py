"""Downloads the wiki pages"""
import base64
import json
import os
import shutil

import requests


def get_azure_headers() -> dict[str, str]:
    """Generate the authorization headers for Azure DevOps API."""
    pat = os.getenv("AZURE_PAT")
    encoded_pat = base64.b64encode(bytes(f":{pat}", "ascii")).decode("ascii")
    return {
        "Accept": "application/json",
        "Authorization": f"Basic {encoded_pat}",
    }


def read_and_convert_to_json_list(file_path: str) -> list[dict[str, str]]:
    """Reads a file and converts it to a JSON list."""
    with open(file_path, "r") as file:
        return json.load(file)


def get_path_files(
    content: list[dict[str, str]], limit: int | None = None
) -> list[str]:
    """Gets the path files from the content list with a limit"""
    if limit is not None:
        return [page["path"] for page in content[:limit]]
    else:
        return [page["path"] for page in content]


def get_page(org_url: str, project: str, headers: dict[str, str], path: str) -> str:
    """List all azure wikis"""
    params = {"path": path, "includeContent": "True"}
    wiki_id = "10978e98-31dc-4fe7-9a40-7854c9591ef1"
    url = f"{org_url}/{project}/_apis/wiki/wikis/{wiki_id}/pages?api-version=7.2-preview.1"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["content"]


def create_file(path: str, content: str) -> None:
    """Creates a file and writes the content."""
    with open(path, "w") as file:
        file.write(content)


def create_path(path: str) -> None:
    """Creates a directory and any necessary intermediate directories"""
    os.makedirs(path, exist_ok=True)


def remove_path(path: str) -> None:
    """Removes a directory and all its contents."""
    if os.path.exists(path):
        shutil.rmtree(path)


if __name__ == "__main__":
    org_url = os.getenv("AZURE_ORGANIZATION_URL")
    project_name = os.getenv("AZURE_PROJECT_NAME")
    headers = get_azure_headers()

    try:
        content = read_and_convert_to_json_list("data2.json")
        path_files = get_path_files(content, limit=10)
        base_path = "pages"
        remove_path(base_path)

        for path_file in path_files:
            content_page = get_page(org_url, project_name, headers, path_file)
            if content_page:
                path = os.path.dirname(path_file)
                create_path(f"{base_path}/{path}")
                create_file(f"{base_path}/{path_file}.md", content_page)

        print("Finish")
    except Exception as error:
        print(error)
