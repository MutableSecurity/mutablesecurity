"""Module for testing a solution lifecycle."""


from mutablesecurity.helpers.pytest import run_good_command
from mutablesecurity.solutions.implementations.dummy.code import (
    AppendToFileAction,
    ContentLogs,
    CurrentUserInformation,
    FilePresenceTest,
    FileSizeInformation,
)


def test_solution_help() -> None:
    """Test the print of the solution's help."""
    run_good_command("")


def test_valid_init() -> None:
    """Test a valid solution initialization."""
    run_good_command("-o INIT")


def test_valid_install() -> None:
    """Test a valid installation."""
    run_good_command("-o INSTALL")


def test_valid_test() -> None:
    """Test a valid test."""
    run_good_command("-o TEST")


def test_valid_specific_test() -> None:
    """Test a valid test wit an identifier."""
    run_good_command(f"-o TEST -i {FilePresenceTest.IDENTIFIER}")


def test_valid_get_information() -> None:
    """Test the retrieval of all information."""
    run_good_command("-o GET_INFORMATION")


def test_valid_get_specific_information() -> None:
    """Test the retrieval of specific information."""
    run_good_command(
        f"-o GET_INFORMATION -i {CurrentUserInformation.IDENTIFIER}"
    )
    run_good_command(f"-o GET_INFORMATION -i {FileSizeInformation.IDENTIFIER}")


def test_valid_set_information() -> None:
    """Test the setting of an information."""
    run_good_command(
        f"-o SET_INFORMATION -i {CurrentUserInformation.IDENTIFIER} -v user"
    )


def test_valid_get_logs() -> None:
    """Test ."""
    run_good_command(f"-o GET_LOGS -i {ContentLogs.IDENTIFIER}")


def test_valid_action_execution() -> None:
    """Test a valid action execution."""
    run_good_command(
        f"-o EXECUTE -i {AppendToFileAction.IDENTIFIER} -a content=dummy -a"
        " number=1"
    )


def test_valid_uninstallation() -> None:
    """Test a valid uninstallation."""
    run_good_command("-o UNINSTALL")
