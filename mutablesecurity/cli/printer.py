"""Module for printing the command line interface."""

import re
import typing

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from mutablesecurity.cli.messages import MessageFactory, MessageTypes
from mutablesecurity.helpers.exceptions import CLIException
from mutablesecurity.main import ResponseTypes, SecurityDeploymentResult
from mutablesecurity.solutions.base.result import (
    BaseConcreteResultObjects,
    BaseGenericObjectsDescriptions,
    ConcreteObjectsResult,
    KeysDescriptions,
)
from mutablesecurity.solutions_manager import SolutionsManager

PrintableMatrix = typing.List[typing.List[str]]


class Printer:
    """Class for printing the user interface."""

    SECONDS_BEFORE_SHOWING_LOGS = 2

    # pylint: disable=anomalous-backslash-in-string
    BANNER_FORMAT = """
                  _        _     _      __                      _ _
      /\/\  _   _| |_ __ _| |__ | | ___/ _\ ___  ___ _   _ _ __(_| |_ _   _
     /    \| | | | __/ _` | '_ \| |/ _ \ \ / _ \/ __| | | | '__| | __| | | |
    / /\/\ | |_| | || (_| | |_) | |  ___\ |  __| (__| |_| | |  | | |_| |_| |
    \/    \/\__,_|\__\__,_|_.__/|_|\___\__/\___|\___|\__,_|_|  |_|\__|\__, |
         {} |___/
    """  # noqa: W605, pylint: enable=anomalous-backslash-in-string
    MOTTO = "Seamless deployment and management of cybersecurity solutions"

    SOLUTION_HELP = """
Full name: {full_name}

Description:
{description}

References:
{references}

Tests:
{tests}
Information:
{information}
Log Sources:
{logs}
Actions:
{actions}
"""

    PASSWORD_PROMPT = "[bold][blue]Password"  # noqa: S105

    FEEDBACK_TITLE = "[bold][blue]We'd Love To Hear From You "
    FEEDBACK_BODY = """
We're all administrators, just like you. We deploy and manage security \
solutions in our infrastructure, but we're sick of repeating the same \
time-consuming procedures over and over again.

Our goal is to make interacting with security solutions easier. Because \
we're starting from scratch, we'd like to get in touch with as many \
administrators as possible to see how they use our software in their \
daily operations and what features could be added to make their jobs \
easier.

[bold]Please provide us your email address if you want to support us with \
the above.[/bold] If you'd rather send it later, simply press ENTER now \
and run [italic]mutablesecurity feedback[/italic] when you're ready.
    """
    FEEDBACK_THANKS = (
        "\n  [bold]Many thanks! One of our staff members will contact you as"
        " soon as possible."
    )
    FEEDBACK_EMAIL_PROMPT = "\n  [bold][blue]Your Email Address"

    console: Console

    def __init__(self, console: Console) -> None:
        """Initialize the object.

        Args:
            console (Console): Console to print in
        """
        self.console = console

    def __to_str(self, obj: typing.Any) -> str:
        """Stringify an object.

        The classes can be printed either by their implicit name or, if
        defined, by a static member named ALIAS.

        Args:
            obj (typing.Any): Any object

        Returns:
            str: String representation
        """
        if obj is None:
            return ""
        elif isinstance(obj, type):
            if not (name := getattr(obj, "ALIAS", None)):
                name = obj.__name__

            return name
        elif isinstance(obj, list):
            return ", ".join([self.__to_str(elem) for elem in obj])

        return str(obj)

    def __create_banner(self) -> Text:
        """Create the banner based on logo and motto.

        Returns:
            Text: Banner
        """
        parts = self.BANNER_FORMAT.split("{}")

        banner = Text()
        banner.append(parts[0], style="json.key")
        banner.append(self.MOTTO)
        banner.append(parts[1], style="json.key")

        return banner

    def __represent_unordered_list(
        self, unordered_list: typing.List[str]
    ) -> Text:
        """Convert an unordered list into its text representation.

        Args:
            unordered_list (typing.List[str]): List to be converted

        Returns:
            Text: Resulted text representation
        """
        result = Text()
        for element in unordered_list:
            result.append(f"- {element}\n")

        return result[:-1]

    def __create_solution_matrix(
        self,
        keys_descriptions: KeysDescriptions,
        generic_objects_descriptions: BaseGenericObjectsDescriptions,
        concrete_objects: typing.Optional[BaseConcreteResultObjects] = None,
    ) -> PrintableMatrix:
        """Create a matrix based on information specific to a solution.

        Args:
            keys_descriptions (KeysDescriptions): Description of keys present
                in the descriptions
            generic_objects_descriptions (BaseGenericObjectsDescriptions):
                Generic description to each object stored in the solution
            concrete_objects (BaseConcreteResultObjects, optional): If a result
                is printed, then some concrete values of the objects are stored
                here. Defaults to None.

        Returns:
            PrintableMatrix: Matrix representation
        """
        matrix = []

        # Create the header
        headers = list(keys_descriptions.values())
        if concrete_objects:
            headers.append("Value")
        matrix.append(headers)

        # Create the body
        keys_ids = list(keys_descriptions.keys())
        id_key = keys_ids[0]
        if concrete_objects:
            for key, value in concrete_objects.items():
                description = [
                    elem
                    for elem in generic_objects_descriptions
                    if elem[id_key] == key
                ][0]

                row = [self.__to_str(elem) for elem in description.values()]
                row.append(self.__to_str(value))
                matrix.append(row)
        else:
            for current_object in generic_objects_descriptions:
                row = []
                for key in keys_ids:
                    row.append(self.__to_str(current_object[key]))

                matrix.append(row)

        return matrix

    def __represent_table(self, string_table: PrintableMatrix) -> Table:
        """Convert a table into its table representation.

        The first line is considered to be the headers one.

        Args:
            string_table (PrintableMatrix): Table to be converted

        Returns:
            Table: Resulted table representation
        """
        table = Table()
        for line_index, line in enumerate(string_table):
            if line_index == 0:
                for element_index, element in enumerate(line):
                    if element_index == 0:
                        justify = "left"
                        style = "bold"
                    else:
                        justify = "center"
                        style = None

                    table.add_column(
                        element,
                        justify=justify,  # type: ignore[arg-type]
                        style=style,
                    )
            else:
                table.add_row(*line)

        return table

    def __formatted_print(
        self, format_string: str, **kwargs: typing.Any
    ) -> None:
        """Print a string formatted with a series of arguments.

        Args:
            format_string (str): Format string, having inside {} placeholders
            kwargs (typing.Any): Parameters for populating the format string
        """
        items = re.split(r"\{|\}", format_string)

        for index, item in enumerate(items):
            if index % 2 == 0:
                self.console.print(item, end="")
            else:
                self.console.print(kwargs[item], end="")

    def __ask(self, message: str, is_sensitive: bool = False) -> str:
        """Ask for an input.

        Args:
            message (str): Prompt message
            is_sensitive (bool): Boolean indicating if the read string is
                sensitive

        Returns:
            str: Provided password
        """
        decorated_message = (
            MessageFactory()
            .create_message(MessageTypes.QUESTION, message)
            .to_str()
        )

        return Prompt.ask(decorated_message, password=is_sensitive)

    def print_version_error(
        self, min_py_version: typing.Tuple[int, int]
    ) -> None:
        """Print an error message related to Python's version.

        Args:
            min_py_version(typing.Tuple[int, int]): Minimum major and minor
                version numbers of Python
        """
        self.print_banner()

        major, minor = min_py_version

        message = MessageFactory().create_message(
            MessageTypes.ERROR,
            "Please make sure that your Python version is at least"
            f" {major}.{minor} before executing MutableSecurity.",
        )
        self.console.print(message.to_text())

    def print_banner(self) -> None:
        """Print the banner."""
        self.console.print(self.__create_banner())

    def print_click_help(self, ctx: click.Context) -> None:
        """Print the help message generated automatically by click.

        Args:
            ctx (click.Context): click's context
        """
        self.console.print(ctx.get_help())

    def print_solution_help(self, solution_id: str) -> None:
        """Print the help of a solution.

        Args:
            solution_id (str): Selected solution's name
        """
        solution_class = SolutionsManager().get_solution_by_id(solution_id)
        solution = solution_class()

        information_matrix = self.__create_solution_matrix(
            solution.INFORMATION_MANAGER.KEYS_DESCRIPTIONS,
            solution.INFORMATION_MANAGER.objects_descriptions,
        )
        tests_matrix = self.__create_solution_matrix(
            solution.TESTS_MANAGER.KEYS_DESCRIPTIONS,
            solution.TESTS_MANAGER.objects_descriptions,
        )
        logs_matrix = self.__create_solution_matrix(
            solution.LOGS_MANAGER.KEYS_DESCRIPTIONS,
            solution.LOGS_MANAGER.objects_descriptions,
        )
        actions_matrix = self.__create_solution_matrix(
            solution.ACTIONS_MANAGER.KEYS_DESCRIPTIONS,
            solution.ACTIONS_MANAGER.objects_descriptions,
        )

        information_repr = self.__represent_table(information_matrix)
        references_repr = self.__represent_unordered_list(solution.REFERENCES)
        tests_repr = self.__represent_table(tests_matrix)
        logs_repr = self.__represent_table(logs_matrix)
        actions_repr = self.__represent_table(actions_matrix)

        self.print_banner()
        self.__formatted_print(
            self.SOLUTION_HELP,
            full_name=solution.FULL_NAME,
            description=solution.DESCRIPTION,
            references=references_repr,
            tests=tests_repr,
            information=information_repr,
            logs=logs_repr,
            actions=actions_repr,
        )

    def ask_for_connection_password(self) -> str:
        """Asks for a connection password.

        Returns:
            str: Connection password
        """
        return self.__ask(self.PASSWORD_PROMPT, is_sensitive=True)

    def print_responses(
        self, responses: typing.List[SecurityDeploymentResult]
    ) -> None:
        """Print the responses produces by the deployments.

        Args:
            responses (typing.List[SecurityDeploymentResult]): Produced
                responses
        """
        for index, response in enumerate(responses):
            if index != 0:
                self.console.print("")

            # Print host information
            host_message = MessageFactory().create_message(
                MessageTypes.COMPUTER_INFO,
                f"Host {response.host_id}",
            )
            self.console.print(host_message.to_text())

            # Create a message for each result and print it
            if response.response_type == ResponseTypes.SUCCESS:
                message = MessageFactory().create_message(
                    MessageTypes.SUCCESS, response.message
                )
            elif response.response_type == ResponseTypes.ERROR:
                message = MessageFactory().create_message(
                    MessageTypes.ERROR, response.message
                )
            self.console.print(message.to_text())

            if getattr(response, "additional_data", None):
                result: ConcreteObjectsResult = response.additional_data
                matrix = self.__create_solution_matrix(
                    result.keys_descriptions,
                    result.generic_objects_descriptions,
                    result.concrete_objects,
                )

                self.console.print(self.__represent_table(matrix))

    def print_feedback_and_ask(self) -> str:
        """Print the feedback form description and ask for an email address.

        Raises:
            NoEmailProvidedException: No email was provided.

        Returns:
            str: Entered email address
        """
        self.console.print(
            Panel(
                self.FEEDBACK_BODY,
                title=self.FEEDBACK_TITLE,
                box=box.HORIZONTALS,
            )
        )

        email = self.__ask(self.FEEDBACK_EMAIL_PROMPT)

        if not email:
            raise NoEmailProvidedException()

        return email

    def thanks_for_feedback(self) -> None:
        """Print thanks message if the user provided an email address."""
        self.console.print(self.FEEDBACK_THANKS + "\n")


class NoEmailProvidedException(CLIException):
    """The user does not provide any email address."""
