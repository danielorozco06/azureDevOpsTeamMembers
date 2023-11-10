"""
This module contains functions to retrieve users from a given Azure DevOps project and write them to a file.
"""

import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()


def get_teams(
    organization_url: str, project_name: str, headers: dict[str, str]
) -> list[str]:
    """
    Function to get all teams for a given project
    """
    api_version = "7.2-preview.3"
    url = f"{organization_url}/_apis/projects/{project_name}/teams?api-version={api_version}&$top=2000"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["value"]


def get_team_members(
    organization_url: str, project_name: str, team_id: str, headers: dict[str, str]
) -> list[str]:
    """
    Function to get all members of a given team
    """
    try:
        api_version = "7.2-preview.2"
        url = (
            f"{organization_url}/_apis/projects/{project_name}/teams/{team_id}/"
            f"members?api-version={api_version}&$top=999"
        )
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["value"]
    except Exception as err:
        print(f"An error occurred: {err}")
    return []


def get_active_teams(
    organization_url: str, project_name: str, headers: dict[str, str]
) -> list[str]:
    """
    Function to get all active teams for a given project
    """
    teams = get_teams(organization_url, project_name, headers)
    active_teams = [
        team
        for team in teams
        if not any(
            word in team["name"].lower() for word in ["inactiva", "nactiva", "inactivo"]
        )
    ]
    return active_teams


def filter_members(members: list[str]) -> list[str]:
    """
    Function to filter out members based on certain conditions
    """
    EXCLUDED_STRINGS = ["vstfs", "nequi"]
    return [
        member
        for member in members
        if not any(
            excluded_string in member["identity"]["uniqueName"]
            for excluded_string in EXCLUDED_STRINGS
        )
    ]


def write_to_file(team: list[str], members: list[str]) -> None:
    """
    Function to write team details and member names to a file
    """
    FILENAME = "team_members.txt"
    filtered_members = filter_members(members)

    with open(FILENAME, "a") as f:
        f.write(f"\nTeam_name:{team['name']}\tTeam_id:{team['id']}\n")
        for member in filtered_members:
            f.write(f"{member['identity']['uniqueName']}\n")


def main() -> None:
    """
    Function main
    """
    organization_url = os.getenv("AZURE_ORGANIZATION_URL")
    project_name = os.getenv("AZURE_PROJECT_NAME")
    pat = os.getenv("AZURE_PAT")

    authorization = str(base64.b64encode(bytes(":" + pat, "ascii")), "ascii")
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic " + authorization,
    }

    active_teams = get_active_teams(organization_url, project_name, headers)
    for team in active_teams:
        members = get_team_members(organization_url, project_name, team["id"], headers)
        write_to_file(team, members)


if __name__ == "__main__":
    main()
