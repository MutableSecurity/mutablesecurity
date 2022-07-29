"""Module containing data validation and parser functions."""

import re
import typing

from mutablesecurity.helpers.exceptions import InvalidConnectionStringException


def parse_connection_string(user_input: str) -> typing.Tuple[str, str, int]:
    """Parse a connection string in the <username>@<hostname>:<port> format.

    Args:
        user_input (str): Input

    Raises:
        InvalidConnectionStringException: The input is not valid.

    Returns:
        typing.Tuple[str, str, int]: Connection details (username, hostname
            and port number)
    """
    regex = (
        r"^[a-z][-a-z0-9]*@(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)"
        "(\.(25[0-5]|"  # noqa: pylint: disable=anomalous-backslash-in-string
        "2[0-4][0-9]|[01]?[0-9][0-9]?)){3}:((6553[0-5])|"
        "(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|"
        "([0-5]{0,5})|([0-9]{1,4}))$"
    )

    if not re.match(regex, user_input):
        raise InvalidConnectionStringException()

    username, hostname, port = re.split("@|:", user_input)
    port = int(port)

    return (username, hostname, port)
