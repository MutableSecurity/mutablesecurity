"""Module for a feedback form shown in the CLI."""

import os
from typing import Optional

import requests
from rich.console import Console

from mutablesecurity.cli.printer import NoEmailProvidedException, Printer
from mutablesecurity.helpers.exceptions import CLIException


class FeedbackForm:
    """Class for managing the feedback form."""

    FILENAME = ".feedback"

    console: Console

    def __init__(self, console: Console) -> None:
        """Initialize the object.

        Args:
            console (Console): Console to print in
        """
        self.console = console

    def __check_or_mark_shown_feedback(self) -> bool:
        if not (exists := os.path.isfile(self.FILENAME)):
            open(self.FILENAME, "w", encoding="utf-8").close()

        return exists

    def __send_feedback_form(self, email_address: str) -> None:
        data = {"email": email_address, "message": "Want to help!"}
        headers = {
            "Content-Type": "application/json",
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
        parameter needs to be explicitly set.

        Args:
            no_check (bool): Boolean indicating if the form needs to be shown
                anytime. Defaults to False.

        Raises:
            FeedbackNotSentException: Feedback could no be sent
        """
        # Check if the feedback was already shown
        if not no_check and self.__check_or_mark_shown_feedback():
            return

        # Print the text and the prompt
        printer = Printer(self.console)
        try:
            email = printer.print_feedback_and_ask()
        except NoEmailProvidedException:
            return

        # Process the email
        try:
            self.__send_feedback_form(email_address=email)
        except FeedbackNotSentException as exception:
            raise exception
        else:
            printer.thanks_for_feedback()


class FeedbackNotSentException(CLIException):
    """The feedback could not be sent. Please try again to send the form."""
