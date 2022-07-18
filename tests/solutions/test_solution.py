"""Module for testing a solution lifecycle."""

import pytest
import yaml
from click.testing import CliRunner

from mutablesecurity.cli.cli import __run_command
from mutablesecurity.helpers.exceptions import (
    SolutionActionNotFoundException,
    SolutionInformationNotFoundException,
    SolutionLogNotFoundException,
    SolutionTestNotFoundException,
)
from mutablesecurity.solutions.implementations.dummy.code import (
    AppendToFileAction,
    ContentLogs,
    CurrentUserInformation,
    FileSizeInformation,
    PresenceTest,
)

ORIGINAL_YAML_SAFELOAD = yaml.safe_load


def __mock_dummy_password(message: str, password: bool) -> str:
    # pylint: disable=unused-argument
    """Mock a password input.

    Args:
        message (str): Unused
        password (bool): Unused

    Returns:
        str: Dummy password
    """
    return "password"


def __mock_yaml_safeload(stream: str) -> dict:
    # pylint: disable=unused-argument
    """Mock a YAML configuration parsing.

    Args:
        stream (str): Content to process

    Returns:
        dict: Configuration dictionary
    """
    if "current_user" in stream:
        return {"current_user": "username"}
    else:
        return ORIGINAL_YAML_SAFELOAD(stream)


def test_successful_dummy_deploy_and_manage(
    capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    # pylint: disable=unused-argument
    """Tests a valid sequence of commands deploying and managing a solution.

    Args:
        capsys (pytest.CaptureFixture): Ignored fixture
        monkeypatch (pytest.MonkeyPatch): Object used for monkey patching
    """
    monkeypatch.setattr(
        "rich.prompt.Prompt.ask",
        __mock_dummy_password,
    )
    monkeypatch.setattr(
        "yaml.safe_load",
        __mock_yaml_safeload,
    )

    # Create the commands to be ran. The identifiers are retrieved in advance
    # to increase the visibility of the array with commands.
    command_base = "--solution DUMMY"
    user_info_id = CurrentUserInformation.IDENTIFIER
    size_info_id = FileSizeInformation.IDENTIFIER
    action_id = AppendToFileAction.IDENTIFIER
    logs_id = ContentLogs.IDENTIFIER
    commands = [
        "",
        " -o INIT",
        " -o INSTALL",
        " -o TEST",
        f" -o TEST -i {PresenceTest.IDENTIFIER}",
        " -o GET_INFORMATION",
        f" -o GET_INFORMATION -i {user_info_id}",
        f" -o GET_INFORMATION -i {size_info_id}",
        f" -o SET_INFORMATION -i {user_info_id} -v ",
        " -o GET_LOGS",
        f" -o GET_LOGS -i {logs_id}",
        f" -o EXECUTE -i {action_id} -a content=dummy -a number=1",
        " -o UNINSTALL",
    ]
    commands = [command_base + command for command in commands]

    for command in commands:
        runner = CliRunner()

        result = runner.invoke(
            __run_command,
            command.split(" "),
        )

        assert (
            not result.exception
        ), "An error was generated despite the correct command."

        # Check that the help page or a success message is printed
        assert "successfully" in result.output or (
            "Dummy" in result.output and "Error" not in result.output
        ), "The canary string is not present in the command's output."


def test_bad_dummy_deploy_and_manage(
    capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    # pylint: disable=unused-argument
    """Tests invalid sequence of commands deploying and managing a solution.

    Args:
        capsys (pytest.CaptureFixture): Ignored fixture
        monkeypatch (pytest.MonkeyPatch): Object used for monkey patching
    """
    monkeypatch.setattr(
        "rich.prompt.Prompt.ask",
        __mock_dummy_password,
    )
    monkeypatch.setattr(
        "yaml.safe_load",
        __mock_yaml_safeload,
    )

    # Create the commands to be ran. The identifiers are retrieved in advance
    # to increase the visibility of the array with commands.
    command_base = "--solution DUMMY"
    commands = [
        " -o INIT",
        " -o INSTALL",
        " -o TEST -i pretty_sure_not_exists",
        " -o GET_INFORMATION -i get_me_if_u_can",
        " -o SET_INFORMATION -i get_me_if_u_can -v dummy",
        " -o GET_LOGS -i logs",
        " -o EXECUTE -i action_to_do_nothing -a content=dummy",
        " -o EXECUTE -i append_to_file -a content=a -a number=1 -a surplus=a",
        " -o EXECUTE -i append_to_file -a content=a",
        " -o EXECUTE -i append_to_file -a content=a -a number=a",
    ]
    invalid_start_index = 2
    commands = [command_base + command for command in commands]

    # Define the exceptions to except
    exceptions = [
        SolutionActionNotFoundException,
        SolutionInformationNotFoundException,
        SolutionLogNotFoundException,
        SolutionTestNotFoundException,
    ]
    exceptions_texts = [str(exception) for exception in exceptions]

    for index, command in enumerate(commands):
        runner = CliRunner()

        result = runner.invoke(
            __run_command,
            command.split(" "),
        )

        # Check that the help page or a success message is printed
        if index >= invalid_start_index:
            present = False
            for text in exceptions_texts:
                if text in result.output:
                    present = True
                    break

            assert not present, (
                f'The output of command "{command}" does not contains an error'
                " message."
            )
