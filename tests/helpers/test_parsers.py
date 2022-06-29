"""Module for testing parsers."""


import pytest

from src.helpers.exceptions import InvalidConnectionStringException
from src.helpers.parsers import parse_connection_string


def test_parse_connection_string_correct() -> None:
    """Test parsing of a correct connection string."""
    username = "administrator"
    hostname = "1.1.1.1"
    port = 10022
    string = f"{username}@{hostname}:{port}"

    details = parse_connection_string(string)
    assert details[0] == username, "Parsed username is incorrect in {string}."
    assert details[1] == hostname, "Parsed hostname is incorrect in {string}."
    assert details[2] == port, "Parsed port is incorrect in {string}."


def test_parse_connection_string_incorrect() -> None:
    """Test parsing of an invalid connection string."""
    usernames = ["administrator", "_root", "0"]
    hostnames = ["1.1.1.1", "dns-server", "localhost"]
    ports = [10022, 99999, -1]
    for username_index, username in enumerate(usernames):
        for hostname_index, hostname in enumerate(hostnames):
            for port_index, port in enumerate(ports):
                # Check that the correct pair is skipped
                if username_index == hostname_index == port_index == 0:
                    continue

                string = f"{username}@{hostname}:{port}"

                with pytest.raises(
                    InvalidConnectionStringException
                ) as execution:
                    parse_connection_string(string)

                exception_raised = execution.value
                assert exception_raised, (
                    "Exception was not raised for invalid connection string."
                    f" {string}"
                )
