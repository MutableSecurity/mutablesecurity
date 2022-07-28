"""pytest package configuration."""
import pytest
import yaml

ORIGINAL_YAML_SAFELOAD = yaml.safe_load


def __mock_dummy_password(message: str, password: bool) -> str:
    # pylint: disable=unused-argument
    return "password"


def __mock_yaml_safeload(stream: str) -> dict:
    if "current_user" in stream:
        return {"current_user": "username"}
    else:
        return ORIGINAL_YAML_SAFELOAD(stream)


@pytest.fixture(autouse=True)
def __monkeypatch_functions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "rich.prompt.Prompt.ask",
        __mock_dummy_password,
    )
    monkeypatch.setattr(
        "yaml.safe_load",
        __mock_yaml_safeload,
    )
