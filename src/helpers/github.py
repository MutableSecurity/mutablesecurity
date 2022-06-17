import json

import requests


class GitHub:
    def get_latest_release_name(username, repository):
        connection = requests.get(
            f"https://api.github.com/repos/{username}/{repository}/releases/latest"
        )
        content = connection.content
        name = json.loads(content)["name"]

        return name

    @staticmethod
    def get_asset_from_latest_release(username, repository, unique_name_part):
        connection = requests.get(
            f"https://api.github.com/repos/{username}/{repository}/releases/latest"
        )
        content = connection.content
        assets = json.loads(content)["assets"]

        for asset in assets:
            if unique_name_part in asset["name"]:
                return asset["browser_download_url"]
