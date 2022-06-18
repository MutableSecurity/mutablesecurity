#!/usr/bin/env python3

"""Module for implementing the CLI.

Raises:
    UnsupportedPythonVersion: The current Python version is unsupported
"""

import sys
import typing

import click
from rich.console import Console

from ..helpers.exceptions import UnsupportedPythonVersion
from ..helpers.parsers import (
    parse_connection_string,
    parse_file_with_connection_strings,
)
from ..leader import ConnectionDetails
from ..logger.logger import _setup_logging
from ..main import Main
from ..solutions_manager import SolutionsManager
from ..solutions_manager.solutions import AbstractSolution
from .feedback_form import FeedbackForm
from .printer import Printer

MIN_PYTHON_VERSION = (3, 9)

console = Console()


def __click_callback(callback: typing.Callable) -> typing.Callable:
    """Convert a function into a click lambda function.

    Args:
        callback (typing.Callable): Callback function

    Returns:
        typing.Callable: Corresponding click lambda function
    """
    return lambda _, __, value: callback(value)


class CommandWithBanner(click.Command):
    """Class for attaching the banner to solution's help."""

    def format_usage(
        self, ctx: click.Context, formatter: click.formatting.HelpFormatter
    ) -> None:
        """Format the help message to use the banner.

        Args:
            ctx (click.Context): click's context
            formatter (click.formatting.HelpFormatter): click's formatter
        """
        Printer(console).print_banner()

        super().format_usage(ctx, formatter)


@click.command(cls=CommandWithBanner)
@click.option(
    "-r",
    "--remote",
    type=str,
    help=(
        "Connect to remote in the USERNAME@HOSTNAME:PORT format. If ommited"
        " (besides the remote list parameter), the operations are executed"
        " locally."
    ),
    callback=__click_callback(parse_connection_string),
)
@click.option(
    "-l",
    "--remote-list",
    type=click.Path(exists=True, dir_okay=False),
    help=(
        "Connect to a series of remote hosts specified in a file, in the"
        " USERNAME@HOSTNAME:PORT format. If ommited (besides the remote host"
        " parameter), the operations are executed locally."
    ),
    callback=__click_callback(parse_file_with_connection_strings),
)
@click.option(
    "-k",
    "--key",
    type=click.Path(exists=True, dir_okay=False),
    help="SSH key to use when connecting to the remote host",
)
@click.option(
    "-s",
    "--solution",
    type=click.Choice(Main.get_available_solutions(), case_sensitive=True),
    help="Solution to manage",
    callback=__click_callback(SolutionsManager.get_solution_by_name),
)
@click.option(
    "-o",
    "--operation",
    type=click.Choice(Main.get_available_operations(), case_sensitive=True),
    help="Operation to perform",
)
@click.option(
    "-a",
    "--aspect",
    type=str,
    help=(
        "Configuration's aspect to modify. Available only with a value"
        " (--value)"
    ),
)
@click.option(
    "-v",
    "--value",
    type=str,
    help=(
        "New value of the configuration's aspect. Available only with an"
        " aspect (--aspect)."
    ),
)
@click.option("--verbose", is_flag=True, help="Increase in the logging volume")
@click.option("--feedback", is_flag=True, help="Show feedback form")
@click.option(
    "-h",
    "--help",
    is_flag=True,
    is_eager=False,
    help="Useful information for using MutableSecurity or about a solution",
)
@click.pass_context
def run_command(
    ctx: click.Context,
    remote: ConnectionDetails,
    remote_list: typing.List[ConnectionDetails],
    key: click.Path,
    solution: AbstractSolution,
    operation: str,
    aspect: str,
    value: str,
    verbose: bool,
    feedback: bool,
    help: bool,  # pylint: disable=redefined-builtin
) -> None:
    """Run the CLI based on the provided arguments.

    Args:
        ctx (click.Context): click's context
        remote (ConnectionDetails): Remote host to connect to
        remote_list (typing.List[ConnectionDetails]): File containing remote
            hosts to connect to
        key (click.Path): File containing the SSH key used for host connections
        solution (AbstractSolution): Selected solution
        operation (str): Selected operation
        aspect (str): Solution aspect
        value (str): New value for solution aspect
        verbose (bool): Boolean indicating if the logging is verbose
        feedback (bool): Boolean indicating if the feedback needs to be shown
        help (bool): Boolean indicating if the help needs to be shown
    """
    # TODO: Convert operation to a proper type
    # TODO: Convert aspect to a proper type

    FeedbackForm(console).launch(no_check=feedback)

    printer = Printer(console)

    if solution is None or help:
        printer.print_click_help(ctx)

        return

    if operation is None or help:
        printer.print_solution_help(solution)

        return

    # Attach the password and key to each connection
    password = printer.ask_for_connection_password()
    connection_details = [remote] if remote else remote_list
    for details in connection_details:
        if key:
            details.key = key

        details.password = password

    # Here the solution and the operation must be set.
    additional_arguments = {
        "aspect": aspect,
        "value": value,
    }

    # Run
    _setup_logging(verbose)
    responses = Main.run(
        connection_details, solution, operation, additional_arguments
    )
    printer.print_responses(responses)


def __check_python_version() -> None:
    """Check if the Python version is compatible.

    Raises:
        UnsupportedPythonVersion: The version is not compatible.
    """
    # Check Python version
    if sys.version_info < MIN_PYTHON_VERSION:
        Printer(console=console).print_version_error()

        raise UnsupportedPythonVersion()


def main() -> None:
    """Run the program."""
    run_command()  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    main()
