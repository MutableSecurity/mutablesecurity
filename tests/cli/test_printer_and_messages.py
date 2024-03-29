"""Module for testing the printing module, besides the custom messages."""

import inspect

import pytest
from click import Context
from rich.console import Console

from mutablesecurity.cli.cli import __run_command
from mutablesecurity.cli.printer import NoEmailProvidedException, Printer
from mutablesecurity.main import ResponseTypes, SecurityDeploymentResult


def __mock_ask_with_no_input(message: str, password: bool) -> str:
    # pylint: disable=unused-argument
    return ""


def test_no_feedback_email(
    capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    # pylint: disable=unused-argument
    """Tests if an exception is raised when no email is provided.

    Args:
        capsys (pytest.CaptureFixture): Ignored fixture
        monkeypatch (pytest.MonkeyPatch): Object used for monkey patching
    """
    monkeypatch.setattr("rich.prompt.Prompt.ask", __mock_ask_with_no_input)

    console = Console()
    printer = Printer(console)
    with pytest.raises(NoEmailProvidedException) as execution:
        printer.print_feedback_and_ask()
    assert execution.value, "Exception not raised when providing no email."


def test_simple_prints() -> None:
    """Test all the simple print methods from class."""
    console = Console()

    methods = inspect.getmembers(Printer, predicate=inspect.isfunction)
    for name, method in methods:
        signature = inspect.signature(method)
        if len(signature.parameters) != 1 or signature.return_annotation:
            continue

        with console.capture() as capture:
            printer = Printer(console)
            getattr(printer, name)()

        assert (
            len(capture.get()) != 0
        ), f"No message printed for method {name}."


def test_help() -> None:
    """Test the print of help."""
    console = Console()

    with console.capture() as capture:
        printer = Printer(console)
        printer.print_click_help(Context(command=__run_command))

    assert len(capture.get()) != 0, "No message printed when calling help."


def test_print_solution_help() -> None:
    """Test the print of a solution help."""
    console = Console()

    with console.capture() as capture:
        printer = Printer(console)
        printer.print_solution_help("dummy")

    assert (
        len(capture.get()) != 0
    ), "No message printed when calling help for a solution."


def test_print_result() -> None:
    """Test the print of deployments results."""
    responses = [
        SecurityDeploymentResult(
            "local", ResponseTypes.SUCCESS, "Success", None
        )
    ]

    console = Console()

    with console.capture() as capture:
        printer = Printer(console)
        printer.print_responses(responses)

    assert (
        len(capture.get()) != 0
    ), "No message printed when showing deployments results."
