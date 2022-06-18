"""Module containing data validation and parser functions."""

import pathlib
import re
import typing

from ..leader import ConnectionDetails
from .exceptions import MutableSecurityException


def parse_connection_string(user_input: str) -> ConnectionDetails:
    """Parse a connection string in the <username>@<hostname>:<port> format.

    Args:
        user_input (str): Input

    Raises:
        InvalidConnectionStringException: The input is not valid.

    Returns:
        ConnectionDetails: Connection details
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

    return ConnectionDetails(hostname, port, username, None, None)


def parse_file_with_connection_strings(
    path: pathlib.Path,
) -> typing.List[ConnectionDetails]:
    """Parse a file containing connection strings.

    See the function parse_connection_string for format information.

    Args:
        path (pathlib.Path): File with connection string

    Raises:
        InvalidConnectionStringsFileException: The provided file is invalid.

    Returns:
        typing.List[ConnectionDetails]: List of connections details
    """
    result = []
    with open(path, "r", encoding="utf-8") as remote_hosts:
        for line in remote_hosts.readlines():
            line = line.strip()
            if not line:
                continue

            try:
                result.append(parse_connection_string(line))
            except InvalidConnectionStringException as exception:
                raise InvalidConnectionStringsFileException() from exception

    return result


class ParserException(MutableSecurityException):
    """The parsing process failed."""


class InvalidConnectionStringException(ParserException):
    """The provided connection string is invalid."""


class InvalidConnectionStringsFileException(ParserException):
    """The file containing connection strings is invalid."""
