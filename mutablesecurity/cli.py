#!/usr/bin/env python3

import logging
import re
import time
from enum import Enum

import click
from rich.console import Console
from rich.emoji import Emoji
from rich.logging import RichHandler
from rich.table import Table
from rich.text import Text

from .modules.main import Main
from .modules.solutions_manager import SolutionsManager

BANNER_FORMAT = """
              _        _     _      __                      _ _         
  /\/\  _   _| |_ __ _| |__ | | ___/ _\ ___  ___ _   _ _ __(_| |_ _   _ 
 /    \| | | | __/ _` | '_ \| |/ _ \ \ / _ \/ __| | | | '__| | __| | | |
/ /\/\ | |_| | || (_| | |_) | |  ___\ |  __| (__| |_| | |  | | |_| |_| |
\/    \/\__,_|\__\__,_|_.__/|_|\___\__/\___|\___|\__,_|_|  |_|\__|\__, |
     {} |___/ 
"""
MOTTO = "Seamless deployment and management of cybersecurity solutions"
SLEEP_SECONDS_BEFORE_LOGS = 2

console = Console()


class CommandWithBanner(click.Command):
    def format_usage(self, ctx, formatter):
        console.print(_create_banner())

        super().format_usage(ctx, formatter)


def _create_banner():
    parts = BANNER_FORMAT.split("{}")

    banner = Text()
    banner.append(parts[0], style="json.key")
    banner.append(MOTTO)
    banner.append(parts[1], style="json.key")

    return banner


def _prepare_long_text(text):
    wrapped_text = Text(text, justify="full")

    return wrapped_text


def _print_help(ctx, param, value):
    if value is False:
        return
    console.print(ctx.get_help())

    # Exit
    ctx.exit()


def _print_module_help(ctx, solution):
    # Get the metadata
    solution_class = SolutionsManager.get_solution_by_name(solution)
    meta = solution_class.meta

    # Create the table with the configurable aspects
    table = Table()
    table.add_column("Aspect", justify="left", style="bold")
    table.add_column("Type", justify="left")
    table.add_column("Possible Values", justify="center")
    table.add_column("Description", justify="left")

    # Fill the table with data
    meta_configuration = meta["configuration"]
    for key in meta_configuration.keys():
        details = meta_configuration[key]

        possible_values = "*"
        required_type = details["type"].__name__
        if issubclass(details["type"], Enum):
            possible_values = ", ".join([value.name for value in details["type"]])
            required_type = "str"

        table.add_row(key, required_type, possible_values, details["help"])

    # Create the text
    help_text = Text()
    help_text.append(_create_banner())
    help_text.append("\n")
    help_text.append("Full name: ", style="bold")
    help_text.append(
        meta["full_name"],
    )
    help_text.append("\n\n")
    help_text.append("Description:", style="bold")
    help_text.append("\n")
    help_text.append(_prepare_long_text(meta["description"]))
    help_text.append("\n\n")
    help_text.append("References:\n", style="bold")
    for reference in meta["references"]:
        help_text.append(f"- {reference}\n")
    help_text.append("\n")
    help_text.append("Configuration:", style="bold")

    # Print the text and the table
    console.print(help_text)
    console.print(table)

    # Exit
    ctx.exit()


def _validate_connection_string(connection_string):
    regex = r"^[a-z][-a-z0-9]*@(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}:((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))$"

    if re.match(regex, connection_string):
        return True

    return False


def _setup_logging(verbose):
    # Enable rich logging
    FORMAT = "%(message)s"
    logging.basicConfig(
        level=logging.DEBUG,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[
            RichHandler(console=Console(file=open("/tmp/mutablesecurity.log", "w")))
        ],
    )

    # Set the logging level according to the options
    if verbose:
        logging.getLogger("mutablesecurity").setLevel(logging.INFO)
    else:
        logging.getLogger("mutablesecurity").setLevel(logging.DEBUG)


def _print_response(response):
    text = Text()

    # Check the success status
    if response["success"]:
        emoji = "white_check_mark"
    else:
        emoji = "stop_sign"
    text.append(str(Emoji(emoji)))

    # Plug the message and the addition sent data
    text.append(" " + response["message"])

    # Print the message
    console.print(text)

    # If there are additional data, print it (only dicts by now)
    additonal_data = response["raw_result"]
    if additonal_data:
        if isinstance(additonal_data, list):
            time.sleep(SLEEP_SECONDS_BEFORE_LOGS)

            with console.pager():
                for line in additonal_data:
                    console.print(line)
        elif isinstance(additonal_data, dict):
            # Create the table
            table = Table()
            table.add_column("Attribute", justify="left", style="bold")
            table.add_column("Value", justify="left")

            # Iterate through dict
            for key, value in additonal_data.items():
                table.add_row(key, str(value))

            console.print("")
            console.print(table)


@click.command(cls=CommandWithBanner)
@click.option(
    "-r",
    "--remote",
    type=str,
    help="Connect to remote in the USERNAME@HOSTNAME:PORT format. If ommited, the operations are executed locally.",
)
@click.option(
    "-s",
    "--solution",
    type=click.Choice(Main.get_available_solutions(), case_sensitive=True),
    help="Solution to manage",
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
    help="Configuration's aspect to modify. Available only with a value (--value)",
)
@click.option(
    "-v",
    "--value",
    type=str,
    help="New value of the configuration's aspect. Available only with an aspect (--aspect).",
)
@click.option("--verbose", is_flag=True, help="Increase in the logging volume")
@click.option(
    "-h",
    "--help",
    is_flag=True,
    is_eager=False,
    help="Useful information for using MutableSecurity or about a solution",
)
@click.pass_context
def run_command(ctx, remote, solution, operation, aspect, value, verbose, help):
    # Print the generic help. Includes the -h presence and an invalid host to
    # connect to
    if solution is None or (remote and not _validate_connection_string(remote)):
        _print_help(ctx, None, value=True)

        ctx.exit()

    # Print the module-specific help. Here the solution must be set.
    if operation is None or help:
        _print_module_help(ctx, solution)

    # Process (and get) the required connection details
    hostname = None
    port = None
    username = None
    connection_details = None
    connection_location_string = remote if remote else "localhost"
    password = click.prompt(
        Text.from_markup(
            f":locked_with_key: Password for {connection_location_string}"
        ),
        hide_input=True,
        type=str,
    )
    if remote:
        remote = remote.split("@")
        username = remote[0]
        remote = remote[1].split(":")
        hostname = remote[0]
        port = int(remote[1])
    connection_details = (hostname, port, username, password)

    # Here the solution and the operation must be set.
    additional_arguments = {"aspect": aspect, "value": value}

    # Set up the logging
    _setup_logging(verbose)

    # Run
    response = Main.run(connection_details, solution, operation, additional_arguments)
    _print_response(response)


def main():
    run_command()


if __name__ == "__main__":
    main()
