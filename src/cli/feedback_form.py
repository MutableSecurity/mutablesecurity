"""Module for a feedback form shown in the CLI."""

import os
from typing import Optional

import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from .cli import CLIException


class FeedbackForm:
    """Class for showing and processing a feedback form."""

    TITLE = "[bold][blue]We'd Love To Hear From You "
    BODY = """
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
    THANKS = (
        "\n  [bold]Many thanks! One of our staff members will contact you as"
        " soon as possible."
    )
    FILENAME = ".feedback"
    EMAIL_REQUEST = "\n  [bold][blue]Your Email Address"

    console: Console

    def __init__(self, console: Console) -> None:
        """Initialize the object.

        Args:
            console (Console): Console to print in
        """
        self.console = console

    def __check_or_mark_shown_feedback(self) -> bool:
        """Check if the feedback form was shown. If not, it marks as shown.

        Returns:
            bool: Boolean indicating if the feedback form was already shown
        """
        if not (exists := os.path.isfile(self.FILENAME)):
            open(self.FILENAME, "w", encoding="utf-8").close()

        return exists

    def __send_feedback_form(self, email_address: str) -> None:
        """Send the feedback form to a Google Cloud Function.

        Args:
            email_address (str): User's email address

        Raises:
            FeedbackNotSentException: Feedback could no be sent
        """
        data = {"email": email_address, "message": "Want to help!"}
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        }

        result = requests.post(
            "https://europe-central2-mutablesecurity.cloudfunctions.net/"
            "add_to_waiting_list",
            json=data,
            headers=headers,
        )

        if result.status_code != 200:
            raise FeedbackNotSentException()

    def launch(self, no_check: Optional[bool] = False) -> None:
        """Launch the feedback form.

        By default, it is only shown only once. After that, the no_check
        parameter needs to be explicitely set.

        Args:
            no_check (bool, optional): Boolean indicating if the form needs to
                be shown anytime. Defaults to False.

        Raises:
            FeedbackNotSentException: Feedback could no be sent
        """
        # Check if the feedback was already shown
        if not no_check and self.__check_or_mark_shown_feedback():
            return

        # Print the text and the prompt
        self.console.print(
            Panel(
                self.BODY,
                title=self.TITLE,
                box=box.HORIZONTALS,
            )
        )
        email = Prompt.ask(self.EMAIL_REQUEST)

        # Process the email
        if email:
            try:
                self.__send_feedback_form(email_address=email)

                self.console.print(self.THANKS + "\n")

            except FeedbackNotSentException as exception:
                raise exception


class FeedbackNotSentException(CLIException):
    """The feedback could not be sent. Please try again to send the form."""
