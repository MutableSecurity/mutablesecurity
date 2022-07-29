"""Module for testing a solution lifecycle."""


from mutablesecurity.helpers.pytest import run_bad_command, run_good_command


def test_valid_init_install() -> None:
    """Set up the solution to be used in the following tests.

    This is modeled as a test (and not a fixture or setup_module function)
    because a password is requested on execution, functionality that is mocked
    via a fixture automatically applied to all tests in this package.
    """
    run_good_command("-o INIT")
    run_good_command("-o INSTALL")


def test_invalid_test_id() -> None:
    """Test the execution with an invalid test identifier."""
    run_bad_command("-o TEST -i pretty_sure_not_exists")


def test_invalid_information_id_on_get() -> None:
    """Test the retrieval of an information with an invalid identifier."""
    run_bad_command("-o GET_INFORMATION -i get_me_if_u_can")


def test_invalid_information_id_on_set() -> None:
    """Test the set of an information with an invalid identifier."""
    run_bad_command("-o SET_INFORMATION -i get_me_if_u_can -v dummy")


def test_invalid_logs_id() -> None:
    """Test the retrieval of a log source with an invalid identifier."""
    run_bad_command("-o GET_LOGS -i logs")


def test_invalid_action_id() -> None:
    """Test the execution with an invalid action identifier."""
    run_bad_command("-o EXECUTE -i action_to_do_nothing -a content=dummy")


def test_surplus_argument_on_execute() -> None:
    """Test the execution with a surplus parameter for an action."""
    run_bad_command(
        "-o EXECUTE -i append_to_file -a content=a -a number=1 -a surplus=a"
    )


def test_missing_argument_on_execute() -> None:
    """Test the execution with a missing parameter for an action."""
    run_bad_command("-o EXECUTE -i append_to_file -a content=a")


def test_bad_argument_type_on_execute() -> None:
    """Test the execution with an invalid parameter for an action."""
    run_bad_command("-o EXECUTE -i append_to_file -a content=a -a number=a")


def test_valid_uninstallation() -> None:
    """Uninstall the solution used in the previous tests.

    This is modeled as a test (and not a fixture or setup_module function)
    because a password is requested on execution, functionality that is mocked
    via a fixture automatically applied to all tests in this package.
    """
    run_good_command("-o UNINSTALL")
