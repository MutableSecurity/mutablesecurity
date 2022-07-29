"""Module for modeling connection with target hosts."""
import abc
import pathlib
import typing

from pyinfra import host

from mutablesecurity.helpers.exceptions import (
    ConnectionExportMethodNotImplementedException,
    InvalidConnectionDetailsException,
    InvalidConnectionStringException,
    InvalidConnectionStringsFileException,
    UnexpectedBehaviorException,
    UnknownConnectionTypeException,
)
from mutablesecurity.helpers.files import read_file_lines
from mutablesecurity.helpers.parsers import parse_connection_string
from mutablesecurity.helpers.type_hints import PyinfraConnectionDump

CONNECTION_KEY_IN_HOST_DATA = "connection"


class Connection:
    """Base class for connection types."""

    password: typing.Optional[str]

    def __init__(self, password: typing.Optional[str]) -> None:
        """Initialize a connection.

        Args:
            password (str): Local user password. Can be None if the deployment
                is done as root.
        """
        self.password = password

    @abc.abstractmethod
    def export(self) -> PyinfraConnectionDump:
        """Export the host details as a tuple.

        Raises:
            ConnectionExportMethodNotImplementedException: Method is not
                implemented.
        """
        raise ConnectionExportMethodNotImplementedException()


class LocalPasswordConnection(Connection):
    """Class for managing a connection to the local host."""

    def export(self) -> PyinfraConnectionDump:
        """Export the host details as a tuple.

        Returns:
            PyinfraConnectionDump: Host details
        """
        return (
            "@local",
            {
                CONNECTION_KEY_IN_HOST_DATA: self,
            },
        )

    def __str__(self) -> str:
        """Stringify the connection.

        Returns:
            str: Stringified connection
        """
        return "root@localhost"


class RemoteConnection(Connection):  # pylint: disable=abstract-method
    """Class for managing a connection to a target host managed via SSH."""

    hostname: str
    port: int
    username: str
    additional_parameters: dict

    def __init__(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str,
        additional_parameters: dict,
    ) -> None:
        """Create a connection to a remote host.

        Args:
            hostname (str): Hostname
            port (int): Port
            username (str): Username
            password (str): Password
            additional_parameters (dict): Additional parameters for connecting
                with pyinfra
        """
        super().__init__(password)

        self.hostname = hostname
        self.port = port
        self.username = username
        self.additional_parameters = additional_parameters

    def export(self) -> PyinfraConnectionDump:
        """Export the host details as a tuple.

        Returns:
            PyinfraConnectionDump: Host details
        """
        ssh_connection_details = {
            "ssh_port": self.port,
            "ssh_user": self.username,
            "allow_agent": False,
            CONNECTION_KEY_IN_HOST_DATA: self,
        }
        ssh_connection_details |= self.additional_parameters

        return (
            self.hostname,
            ssh_connection_details,
        )

    def __str__(self) -> str:
        """Stringify the connection.

        Returns:
            str: Stringified connection
        """
        return f"{self.username}@{self.hostname}:{self.port}"


class PasswordSSHRemoteConnection(RemoteConnection):
    """Class for modeling a password-based, SSH connection."""

    ssh_password: str

    def __init__(
        self, hostname: str, port: int, username: str, user_password: str
    ) -> None:
        """Create a connection via password-based SSH.

        Args:
            hostname (str): Host
            port (int): Port where SSH listens
            username (str): Username
            user_password (str): Password for user (for both SSH connection and
                local sudo)
        """
        super().__init__(
            hostname,
            port,
            username,
            user_password,
            {
                "ssh_password": user_password,
                "ssh_look_for_keys": False,
            },
        )


class KeySSHRemoteConnection(RemoteConnection):
    """Class for modeling a key-based, SSH connection."""

    key: pathlib.Path
    key_password: str

    def __init__(
        self,
        hostname: str,
        port: int,
        username: str,
        user_password: str,
        key: pathlib.Path,
        key_password: str,
    ) -> None:
        """Create a connection via key-based SSH.

        Args:
            hostname (str): Host
            port (int): Port where SSH listens
            username (str): Username
            user_password (str): Password for user (for both SSH connection and
                local sudo)
            key (pathlib.Path): Path to SSH key
            key_password (str): Password for SSH key
        """
        super().__init__(
            hostname,
            port,
            username,
            user_password,
            {
                "ssh_key": str(key),
                "ssh_key_password": key_password,
            },
        )


class ConnectionFactory:
    """Class for creating connections."""

    def create_connection(
        self,
        user_password: typing.Optional[str] = None,
        connection_string: typing.Optional[str] = None,
        key: typing.Optional[pathlib.Path] = None,
        key_password: typing.Optional[str] = None,
    ) -> Connection:
        """Create a single connection.

        Args:
            user_password (str): Password of user's account. Defaults to None
                if the connection is local and the tool is ran with sudo.
            connection_string (str): Connection string. Defaults to None.
            key (pathlib.Path): Path to SSH key. Defaults to None.
            key_password (str): Password for SSH key. Defaults to None.

        Raises:
            InvalidConnectionDetailsException: The connection string could not
                be parsed.
            UnknownConnectionTypeException: The type of the connection could
                not be established.
            UnexpectedBehaviorException: A password that must be set is not
                set.

        Returns:
            Connection: Resulted connection
        """
        if connection_string is None:
            return LocalPasswordConnection(user_password)

        try:
            username, hostname, port = parse_connection_string(
                connection_string
            )
        except InvalidConnectionStringException as exception:
            raise InvalidConnectionDetailsException() from exception
        else:
            if user_password is None:
                raise UnexpectedBehaviorException()

            if key is None:
                return PasswordSSHRemoteConnection(
                    hostname,
                    port,
                    username,
                    user_password,
                )
            elif key_password:
                return KeySSHRemoteConnection(
                    hostname,
                    port,
                    username,
                    user_password,
                    key,
                    key_password,
                )

        raise UnknownConnectionTypeException()

    def create_connections_from_file(
        self,
        connection_strings_file: pathlib.Path,
        user_password: str,
        key: typing.Optional[pathlib.Path] = None,
        key_password: typing.Optional[str] = None,
    ) -> typing.List[Connection]:
        """Create connections from a file with connection string.

        Args:
            connection_strings_file (pathlib.Path): Path to file with
                connection strings
            user_password (str): Password of user's account
            key (pathlib.Path): Path to SSH key. Defaults to None.
            key_password (str): Password for SSH key. Defaults to None.

        Raises:
            InvalidConnectionStringsFileException: The provided file with
                connection strings is invalid.
            UnknownConnectionTypeException: The type of the connection could
                not be established.

        Returns:
            typing.List[Connection]: List of connections
        """
        connections = []
        for connection_string in read_file_lines(connection_strings_file):
            try:
                connection = self.create_connection(
                    user_password, connection_string, key, key_password
                )
            except InvalidConnectionDetailsException as exception:
                raise InvalidConnectionStringsFileException() from exception
            except UnknownConnectionTypeException as exception:
                raise exception
            else:
                connections.append(connection)

        return connections


def get_connection_for_host() -> Connection:
    """Get the connection used to create the pyinfra host.

    Returns:
        Connection: Connection
    """
    return host.host_data[CONNECTION_KEY_IN_HOST_DATA]
