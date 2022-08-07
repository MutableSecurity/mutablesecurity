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

from mutablesecurity import config
from mutablesecurity.cli.messages import MessageFactory, MessageTypes
from mutablesecurity.helpers.exceptions import (
    CLIException,
    MutableSecurityException,
)
from mutablesecurity.main import ResponseTypes, SecurityDeploymentResult
from mutablesecurity.solutions.base.result import ConcreteObjectsResult
from mutablesecurity.solutions_manager import SolutionsManager
from mutablesecurity.visual_proxy import (
    ObjectsDescriberFacade,
    describe_solution_object,
    describe_solution_objects,
)

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

Categories:
{categories}

Description:
{description}

References:
{references}

Actions:
{actions}
Information:
{information}
Log Sources:
{logs}
Tests:
{tests}
"""

    SOLUTION_HELP_DEV_EXTENSION = """Maturity: {maturity}\n"""

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
    FEEDBACK_EMAIL_PROMPT = "[bold][blue]Your Email Address"

    HOST_MESSAGE = "Connection {host}"

    VERSION_ERROR_TEXT = (
        "Please make sure that your Python version is at least"
        " {major}.{minor} before executing MutableSecurity."
    )

    console: Console

    def __init__(self, console: Console) -> None:
        """Initialize the object.

        Args:
            console (Console): Console to print in
        """
        self.console = console

    def __create_banner(self) -> Text:
        parts = self.BANNER_FORMAT.split("{}")

        banner = Text()
        banner.append(parts[0], style="json.key")
        banner.append(self.MOTTO)
        banner.append(parts[1], style="json.key")

        return banner

    def __represent_unordered_list(
        self, unordered_list: typing.List[str]
    ) -> Text:
        result = Text()
        for element in unordered_list:
            result.append(f"- {element}\n")

        return result[:-1]

    def __represent_table(
        self, string_table: PrintableMatrix, full_width: bool = False
    ) -> Table:
        min_width = 1000 if full_width else None
        table = Table(show_lines=True, min_width=min_width)
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
        items = re.split(r"\{|\}", format_string)

        for index, item in enumerate(items):
            if index % 2 == 0:
                self.console.print(item, end="")
            else:
                self.console.print(kwargs[item], end="")

    def __ask(self, message: str, is_sensitive: bool = False) -> str:
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

        message_text = self.VERSION_ERROR_TEXT.format(major=major, minor=minor)
        message = MessageFactory().create_message(
            MessageTypes.ERROR, message_text
        )
        self.console.print(message.to_text())

    def print_exception(self, exception: MutableSecurityException) -> None:
        """Print a MutableSecurity exception to stdout.

        Args:
            exception (MutableSecurityException): Exception to print
        """
        message = MessageFactory().create_message(
            MessageTypes.ERROR, str(exception)
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
        solution_class = SolutionsManager().get_solution_class_by_id(
            solution_id
        )
        solution = solution_class()

        categories = [str(cat) for cat in solution.CATEGORIES]

        facade = ObjectsDescriberFacade(solution)
        information_matrix = facade.describe_information()
        tests_matrix = facade.describe_tests()
        logs_matrix = facade.describe_logs()
        actions_matrix = facade.describe_actions()

        categories_repr = self.__represent_unordered_list(categories)
        references_repr = self.__represent_unordered_list(solution.REFERENCES)
        information_repr = self.__represent_table(information_matrix)
        tests_repr = self.__represent_table(tests_matrix)
        logs_repr = self.__represent_table(logs_matrix)
        actions_repr = self.__represent_table(actions_matrix)

        self.print_banner()
        self.__formatted_print(
            self.SOLUTION_HELP,
            categories=categories_repr,
            full_name=solution.FULL_NAME,
            description=solution.DESCRIPTION,
            references=references_repr,
            tests=tests_repr,
            information=information_repr,
            logs=logs_repr,
            actions=actions_repr,
        )

        if config.developer_mode:
            self.__formatted_print(
                self.SOLUTION_HELP_DEV_EXTENSION,
                maturity=solution.MATURITY,
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
            host_text = self.HOST_MESSAGE.format(host=response.host_id)
            host_message = MessageFactory().create_message(
                MessageTypes.COMPUTER_INFO, host_text
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

            if (
                hasattr(response, "additional_data")
                and response.additional_data is not None
            ):
                result: ConcreteObjectsResult = response.additional_data
                if result.is_long_output:
                    for key, content in result.concrete_objects.items():
                        with self.console.pager():
                            matrix = describe_solution_object(
                                result.keys_descriptions,
                                result.generic_objects_descriptions,
                                key,
                            )
                            self.console.print(
                                self.__represent_table(matrix, full_width=True)
                            )

                            self.console.print("")
                            self.console.print(content)
                else:
                    matrix = describe_solution_objects(
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
