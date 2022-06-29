"""Module for testing the one communicating with GitHub API."""

import pytest

from src.helpers.exceptions import GitHubAPIError, NoIdentifiedAssetException
from src.helpers.github import (
    get_asset_from_latest_release,
    get_latest_release_name,
)


def test_get_latest_release_name() -> None:
    """Test the retrieval of the latest release name."""
    name = get_latest_release_name("kitabisa", "teler")

    assert name[0] == "v", "The release name is invalid."


def test_get_latest_release_name_for_invalid_repository() -> None:
    """Test if an exception is raised when passing an invalid repository."""
    with pytest.raises(GitHubAPIError) as execution:
        get_latest_release_name("mutablesecurity", "mutablesecurity-gui")

    exception_raised = execution.value
    assert exception_raised, "The inexistent repository was not detected."


def test_get_asset_from_latest_release() -> None:
    """Test the retrieval of an asset."""
    url = get_asset_from_latest_release("kitabisa", "teler", "linux")

    assert "https://" in url, "The release URL was not returned."


def test_get_asset_from_latest_release_for_inexistent_keyword() -> None:
    """Test if an exception is raised when passing an inexistent keyword."""
    with pytest.raises(NoIdentifiedAssetException) as execution:
        get_asset_from_latest_release("kitabisa", "teler", "dosbox")

    exception_raised = execution.value
    assert (
        exception_raised
    ), "Despite the invalid keyword, an asset URL was returned."
