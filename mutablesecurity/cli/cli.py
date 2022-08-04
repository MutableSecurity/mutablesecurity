#!/usr/bin/env python3

"""Module for implementing the CLI."""

import os
import pathlib
import sys
import typing

import click
import gevent.hub
from rich.console import Console
from rich.traceback import install

from mutablesecurity.cli.feedback_form import FeedbackForm
from mutablesecurity.cli.printer import Printer
from mutablesecurity.cli.solutions_manager_adapter import (
    SolutionsManagerAdapter,
)
from mutablesecurity.helpers.exceptions import (
    BadArgumentException,
    BadValueException,
    MutableSecurityException,
    StoppedMutableSecurityException,
    UnexpectedBehaviorException,
    UnsupportedPythonVersionException,
)
from mutablesecurity.leader import ConnectionFactory
from mutablesecurity.main import Main

MIN_PYTHON_VERSION = (3, 9)


console = Console()
adapter = SolutionsManagerAdapter()


def __click_callback(callback: typing.Callable) -> typing.Callable:
    return lambda _, __, value: callback(value)


def __lower_str_callback(argument: str) -> typing.Optional[str]:
    if argument:
        return argument.lower()

    return None


def __split_arguments(arguments: typing.Tuple[str]) -> typing.Dict[str, str]:
    result = {}
    for argument in arguments:
        argument_split = argument.split("=")

        if len(argument_split) != 2:
            raise BadValueException()

        result[argument_split[0]] = argument_split[1]

    return result


def __ask_for_password_when_not_root(
    remote: str, remote_list: pathlib.Path
) -> typing.Optional[str]:
    if remote is None and remote_list is None and os.geteuid() == 0:
        return None
    else:
        return Printer(console).ask_for_connection_password()


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
)
@click.option(
    "-l",
    "--remote-list",
    type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
    help=(
        "Connect to a series of remote hosts specified in a file, in the"
        " USERNAME@HOSTNAME:PORT format. If ommited (besides the remote host"
        " parameter), the operations are executed locally."
    ),
)
@click.option(
    "-k",
    "--key",
    type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
    help="SSH key to use when connecting to the remote host",
)
@click.option(
    "-s",
    "--solution",
    type=click.Choice(
        SolutionsManagerAdapter().get_solutions_ids(),
        case_sensitive=True,
    ),
    callback=__click_callback(__lower_str_callback),
    help="Solution to manage",
)
@click.option(
    "-o",
    "--operation",
    type=click.Choice(
        SolutionsManagerAdapter().get_operations_ids(),
        case_sensitive=True,
    ),
    callback=__click_callback(__lower_str_callback),
    help="Operation to perform",
)
@click.option(
    "-i",
    "--identifier",
    type=str,
    help="Information to modify. Available only with a value (--value)",
)
@click.option(
    "-v",
    "--value",
    type=str,
    help=(
        "New value of the information. Available only with an identifier"
        " (--identifier)."
    ),
)
@click.option(
    "-a",
    "--arguments",
    type=str,
    multiple=True,
    callback=__click_callback(__split_arguments),
    help='Arguments to be passed to an action, in the "key=value" format',
)
@click.option("--verbose", is_flag=True, help="Increase in the logging volume")
@click.option("--feedback", is_flag=True, help="Show feedback form")
@click.option("--dev", is_flag=True, help="Run in developer mode", hidden=True)
@click.option(
    "-h",
    "--help",
    is_flag=True,
    is_eager=False,
    help="Useful information for using MutableSecurity or about a solution",
)
@click.pass_context
def __run_command(
    ctx: click.Context,
    remote: str,
    remote_list: pathlib.Path,
    key: pathlib.Path,
    solution: str,
    operation: str,
    identifier: str,
    value: str,
    arguments: dict,
    verbose: bool,
    feedback: bool,
    dev: bool,
    help: bool,  # pylint: disable=redefined-builtin
) -> None:
    # No docstring here, please check the arguments descriptions to get more
    # context about their meaning

    FeedbackForm(console).launch(no_check=feedback)

    printer = Printer(console)

    if solution is None or help:
        printer.print_click_help(ctx)

        return

    if operation is None or help:
        printer.print_solution_help(solution)

        return

    # Attach the password and key to each connection
    password = __ask_for_password_when_not_root(remote, remote_list)
    if remote_list:
        if password is None:
            raise UnexpectedBehaviorException()

        connections = ConnectionFactory().create_connections_from_file(
            remote_list, password, key, None
        )
    else:
        connection = ConnectionFactory().create_connection(
            password, remote, key, password
        )
        connections = [connection]

    # Here the solution and the operation must be set.
    additional_arguments = {
        "identifier": identifier,
        "value": value,
        "args": arguments,
    }

    # Run
    main_module = Main(verbose, dev)
    responses = main_module.run(
        connections, solution, operation, additional_arguments
    )
    printer.print_responses(responses)


def __check_python_version() -> None:
    # Check Python version
    if sys.version_info < MIN_PYTHON_VERSION:
        Printer(console=console).print_version_error(MIN_PYTHON_VERSION)

        raise UnsupportedPythonVersionException()


def __setup_pretty_traceback() -> None:
    install(show_locals=True)


def __patch_gevent() -> None:
    gevent.hub.Hub.NOT_ERROR = (Exception, KeyboardInterrupt)


def main() -> None:
    """Run the program."""
    __setup_pretty_traceback()
    __check_python_version()
    __patch_gevent()

    try:
        __run_command(  # pylint: disable=no-value-for-parameter
            standalone_mode=False
        )
    except MutableSecurityException as exception:
        Printer(console=console).print_exception(exception)
    except click.Abort:
        Printer(console=console).print_exception(
            StoppedMutableSecurityException()
        )
    except click.BadParameter:
        Printer(console=console).print_exception(BadArgumentException())
    else:
        return

    try:
        sys.exit(1)
    except SystemExit:
        os._exit(1)  # pylint: disable=protected-access


if __name__ == "__main__":
    main()
