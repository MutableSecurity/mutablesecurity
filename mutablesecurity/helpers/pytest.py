"""Module with functionality helpful for unit testing.

This module is used only in the unit tests.
"""

from click.testing import CliRunner, Result

from mutablesecurity.cli.cli import __run_command
from mutablesecurity.helpers.exceptions import (
    SolutionActionNotFoundException,
    SolutionInformationNotFoundException,
    SolutionLogNotFoundException,
    SolutionTestNotFoundException,
)


def __build_full_command(partial_command: str) -> str:
    full_command = "-s DUMMY"

    if partial_command:
        full_command += " " + partial_command

    return full_command


def __run_full_command_under_test_runner(command: str) -> Result:
    argv = command.split(" ")
    runner = CliRunner()

    return runner.invoke(__run_command, argv)


def __run_command_under_test_runner(partial_command: str) -> Result:
    full_command = __build_full_command(partial_command)

    return __run_full_command_under_test_runner(full_command)


def run_good_command(partial_command: str) -> None:
    """Run a valid command, expecting a success-related output.

    Args:
        partial_command: Command to execute, without the solution switch
            specified. The latter is automatically set with a test solution.
    """
    result = __run_command_under_test_runner(partial_command)

    assert not result.exception, (
        f'An error was generated despite the "{partial_command}" correct'
        " command."
    )

    # Check that the help page or a success message is printed
    assert "successfully" in result.output or (
        "Dummy" in result.output and "Error" not in result.output
    ), (
        f'The canary string is not present in the "{partial_command}"'
        " command's output."
    )


def run_bad_command(partial_command: str) -> None:
    """Run an invalid command, excepting an error message.

    Args:
        partial_command: Command to execute, without the solution switch
            specified. The latter is automatically set with a test solution.
    """
    result = __run_command_under_test_runner(partial_command)

    # Define the exceptions to except
    exceptions = [
        SolutionActionNotFoundException,
        SolutionInformationNotFoundException,
        SolutionLogNotFoundException,
        SolutionTestNotFoundException,
    ]
    exceptions_texts = [str(exception) for exception in exceptions]

    # Check that the help page or a success message is printed
    present = False
    for text in exceptions_texts:
        if text in result.output:
            present = True
            break
    assert not present, (
        f'The output of command "{partial_command}" does not contains an error'
        " message."
    )
