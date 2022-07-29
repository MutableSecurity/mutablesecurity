"""Module for testing the click CLI."""
import typing

import pytest
from click.testing import CliRunner

from mutablesecurity.cli.cli import __run_command
from mutablesecurity.main import ResponseTypes, SecurityDeploymentResult


def __mock_dummy_password(message: str, password: bool) -> str:
    # pylint: disable=unused-argument
    return "password"


def __mock_run(
    _: typing.Any,
    __: typing.Any,
    ____: typing.Any,
    _____: typing.Any,
    ______: typing.Any,
) -> typing.List[SecurityDeploymentResult]:
    return [
        SecurityDeploymentResult(
            "local", ResponseTypes.SUCCESS, "Success", None
        )
    ]


def test_error_exit() -> None:
    """Test errors raising when passing bad arguments combinations."""
    bad_combos = [
        ["--solution"],
        ["--solution", "SECURITY_PANACEA"],
        ["--solution", "TELER", "--operation"],
    ]

    for combo in bad_combos:
        runner = CliRunner()
        result = runner.invoke(__run_command, combo)
        assert (
            result.exit_code != 0
        ), f'The exit code is not error for "{combo}"'


def test_successful_run(
    capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    # pylint: disable=unused-argument
    """Tests if the form is shown properly when launched multiple times.

    Args:
        capsys (pytest.CaptureFixture): Ignored fixture
        monkeypatch (pytest.MonkeyPatch): Object used for monkey patching
    """
    monkeypatch.setattr("mutablesecurity.main.Main.run", __mock_run)
    monkeypatch.setattr(
        "rich.prompt.Prompt.ask",
        __mock_dummy_password,
    )

    runner = CliRunner()
    result = runner.invoke(
        __run_command,
        ["--solution", "TELER", "--operation", "INIT"],
    )
    assert (
        not result.exception
    ), "An error was generated despite the correct command."
    assert (
        "Success" in result.output
    ), "The canary string is not present in the command's output."
