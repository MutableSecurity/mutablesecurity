"""Module for printing the command line interface."""

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from .cli import CLIException


class Printer:
    """Class for printing the user interface."""

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
    FEEDBACK_EMAIL_REQUEST = "\n  [bold][blue]Your Email Address"

    console: Console

    def __init__(self, console: Console) -> None:
        """Initialize the object.

        Args:
            console (Console): Console to print in
        """
        self.console = console

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

        email = Prompt.ask(self.FEEDBACK_EMAIL_REQUEST)

        if not email:
            raise NoEmailProvidedException()

        return email

    def thanks_for_feedback(self) -> None:
        """Print thanks message if the user provided an email address."""
        self.console.print(self.FEEDBACK_THANKS + "\n")


class NoEmailProvidedException(CLIException):
    """The user does not provide any email address."""
