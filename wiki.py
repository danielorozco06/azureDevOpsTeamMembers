"""File"""
import base64
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def get_azure_headers() -> dict[str, str]:
    """Generate the authorization headers for Azure DevOps API."""
    pat = os.getenv("AZURE_PAT")
    encoded_pat = base64.b64encode(bytes(f":{pat}", "ascii")).decode("ascii")
    return {
        "Accept": "application/json",
        "Authorization": f"Basic {encoded_pat}",
    }


def list_wikis(
    org_url: str, project: str, headers: dict[str, str]
) -> list[dict[str, str]]:
    """List all azure wikis"""
    url = f"{org_url}/{project}/_apis/wiki/wikis?api-version=7.2-preview.2"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["value"]


def get_wiki(org_url: str, project: str, headers: dict[str, str]) -> dict[str, str]:
    """Get azure wiki"""
    wiki_id = "10978e98-31dc-4fe7-9a40-7854c9591ef1"
    url = f"{org_url}/{project}/_apis/wiki/wikis/{wiki_id}?api-version=7.2-preview.2"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_pages_batch(org_url: str, project: str, headers: dict[str, str]) -> None:
    """Returns pageable list of Wiki Pages"""
    # The maximum number of pages to return in a page is 100
    top = 100

    # The maximum number of days to retrieve page views data for is 30 days
    page_views_for_days = 30

    wiki_id = "10978e98-31dc-4fe7-9a40-7854c9591ef1"
    body = {"pageViewsForDays": page_views_for_days, "top": top}
    url = f"{org_url}/{project}/_apis/wiki/wikis/{wiki_id}/pagesbatch?api-version=7.2-preview.1"
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    pages = response.json()["value"]

    path_file = "data.json"
    remove_file(path_file)

    while pages:
        create_json_file(path_file, pages)
        body = {
            "continuationToken": response.headers.get("X-MS-ContinuationToken"),
            "pageViewsForDays": page_views_for_days,
            "top": top,
        }
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        pages = response.json()["value"]


def create_json_file(path_file: str, data: list[dict[str, str]]) -> None:
    """Create a json file"""
    with open(path_file, "a", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def remove_file(path_file: str) -> None:
    """Remove a file if it exists"""
    if os.path.isfile(path_file):
        os.remove(path_file)


if __name__ == "__main__":
    org_url = os.getenv("AZURE_ORGANIZATION_URL")
    project_name = os.getenv("AZURE_PROJECT_NAME")
    headers = get_azure_headers()

    try:
        wikis = list_wikis(org_url, project_name, headers)
        wiki = get_wiki(org_url, project_name, headers)
        get_pages_batch(org_url, project_name, headers)
        print("Finish")
    except Exception as error:
        print(error)
