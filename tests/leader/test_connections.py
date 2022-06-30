"""Module for testing the creation of connections."""
import tempfile
from pathlib import Path

import pytest

from src.helpers.exceptions import InvalidConnectionDetailsException
from src.leader.connections import ConnectionFactory


def test_create_connections() -> None:
    """Test the creation of connections."""
    password = "password"
    hostname = "1.1.1.1"
    username = "administrator"
    port = 10022
    key = "/root/ssh.key"
    connection_string = f"{username}@{hostname}:{port}"

    factory = ConnectionFactory()

    # Local connection
    connection = factory.create_connection(password, None)
    exported_connection = connection.export()
    assert connection.password == password, (
        "The password on local connection is not correct:"
        f" {connection.password} != {password}"
    )
    assert (
        "local" in exported_connection
    ), f"The exported local connection is not correct: {exported_connection}."

    # Remote password-based connection
    connection = factory.create_connection(password, connection_string)
    exported_connection = connection.export()
    ssh_details = exported_connection[1]
    assert connection.password == password, (
        "The password on remote password-based connection is not correct:"
        f" {connection.password} != {password}"
    )
    assert (
        exported_connection[0] == hostname
        and ssh_details["ssh_port"] == port
        and ssh_details["ssh_user"] == username
    ), (
        "The exported remote password-based connection is not correct:"
        f" {exported_connection}."
    )

    # Remote key-based connection
    connection = factory.create_connection(
        password, connection_string, Path(key), password
    )
    exported_connection = connection.export()
    ssh_details = exported_connection[1]
    assert connection.password == password, (
        "The password on remote key-based connection is not correct:"
        f" {connection.password} != {password}"
    )
    assert (
        exported_connection[0] == hostname
        and ssh_details["ssh_port"] == port
        and ssh_details["ssh_user"] == username
        and ssh_details["ssh_key"] == key
        and ssh_details["ssh_key_password"] == password
    ), (
        "The exported remote key-based connection is not correct:"
        f" {exported_connection}."
    )


def test_create_connections_from_file() -> None:
    """Tests the creation of connection based on a file."""
    connection_strings = [
        "administrator@8.8.8.8:22",
        "dns-master@1.1.1.1:13377",
    ]
    password = "password"

    file_content = "\n".join(connection_strings)
    temp_file = tempfile.NamedTemporaryFile("w")
    temp_file.write(file_content)
    temp_file.flush()

    factory = ConnectionFactory()
    connections = factory.create_connections_from_file(
        Path(temp_file.name), password
    )
    assert len(connections) == len(
        connection_strings
    ), "Invalid number of returned connections"


def test_create_invalid_connection() -> None:
    """Test if an exception is raised when passing an invalid string."""
    factory = ConnectionFactory()

    with pytest.raises(InvalidConnectionDetailsException) as execution:
        factory.create_connection(
            "password",
            "dns-master@dns-server",
            Path("/tmp/ssh.key"),
            "password_again",
        )

    exception_raised = execution.value
    assert (
        exception_raised
    ), "An exception was not raised when creating an invalid connection"
