"""Module for testing the feedback form."""

import typing

import pytest
from rich.console import Console

from mutablesecurity.cli.feedback_form import (
    FeedbackForm,
    FeedbackNotSentException,
)


class GoodResponse:
    """Class mimiking a good response."""

    status_code = 200


class BadResponse:
    """Class mimiking a bad response with a server error."""

    status_code = 501


def __mock_good_request(args: tuple, **kwargs: typing.Any) -> GoodResponse:
    # pylint: disable=unused-argument
    """Return a good response.

    Args:
        args (tuple): Unused
        kwargs (typing.Any): Unused

    Returns:
        GoodResponse: Response
    """
    return GoodResponse()


def __mock_bad_request(args: tuple, **kwargs: typing.Any) -> BadResponse:
    # pylint: disable=unused-argument
    """Return a bad response.

    Args:
        args (tuple): Unused
        kwargs (typing.Any): Unused

    Returns:
        BadResponse: Response
    """
    return BadResponse()


def __mock_ask(message: str, password: bool) -> str:
    # pylint: disable=unused-argument
    """Mock the ask for an user input.

    Args:
        message (str): Unused
        password (bool): Unused

    Returns:
        str: Constant string
    """
    return "hello@mutablesecurity.io"


def test_multiple_launches(
    capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    # pylint: disable=unused-argument
    """Tests if the form is shown properly when launched multiple times.

    Args:
        capsys (pytest.CaptureFixture): Ignored fixture
        monkeypatch (pytest.MonkeyPatch): Object used for monkey patching
    """
    monkeypatch.setattr("rich.prompt.Prompt.ask", __mock_ask)
    monkeypatch.setattr("requests.post", __mock_good_request)

    console = Console()
    for i in range(2):
        with console.capture() as capture:
            form = FeedbackForm(console)

            form.launch()

        if i == 1:
            assert (
                len(capture.get()) == 0
            ), "The feedback form was shown twice."


def test_networking_issues(
    capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    # pylint: disable=unused-argument
    """Tests if there is raised an exception when a networking error occurs.

    Args:
        capsys (pytest.CaptureFixture): Ignored fixture
        monkeypatch (pytest.MonkeyPatch): Object used for monkey patching
    """
    monkeypatch.setattr("rich.prompt.Prompt.ask", __mock_ask)
    monkeypatch.setattr("requests.post", __mock_bad_request)

    console = Console()
    form = FeedbackForm(console)

    with pytest.raises(FeedbackNotSentException) as execution:
        form.launch()

    exception_raised = execution.value
    assert (
        exception_raised
    ), "Exception not raised when networking issues occures."
