import typing
from abc import ABC, abstractmethod

from pyinfra.api import Host, State


class AbstractSolution(ABC):
    """Abstract class wrapping a security solution"""

    FULL_NAME = ""
    DESCRIPTION = ""
    REFERENCES = []

    _configuration: dict
    meta: dict
    result: dict

    def represent_configuration_as_list(self) -> typing.List[typing.List[str]]:
        meta_configuration = meta["configuration"]
        for key in meta_configuration.keys():
            details = meta_configuration[key]

            possible_values = "*"
            required_type = details["type"].__name__
            if issubclass(details["type"], Enum):
                possible_values = ", ".join(
                    [value.name for value in details["type"]]
                )
                required_type = "str"

            table.add_row(key, required_type, possible_values, details["help"])

        table.add_column("Aspect", justify="left", style="bold")
        table.add_column("Type", justify="left")
        table.add_column("Possible Values", justify="center")
        table.add_column("Description", justify="left")

    @staticmethod
    @abstractmethod
    def get_configuration(state: State, host: Host):
        """Retrieves the configuration of the running solution.

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _set_default_configuration(
        state: State, host: Host, aspect: str, value: str
    ):
        """Overwrites the local configuration with the default one.

        It can be called by methods which resets the configuration to its
        default state (for example, install).

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host
            aspect (str): Set aspect
            value (str): Set value

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _verify_new_configuration(state: State, host: Host, aspect, value):
        """Verifies a configuration that needs to be set.

        This method is automatically called by set_configuration.

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host
            aspect (str): Set aspect
            value (str): Set value

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def set_configuration(state: State, host: Host, aspect=None, value=None):
        """Sets an aspect of the configuration.

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host
            aspect (str): Set aspect
            value (str): Set value

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _set_configuration_callback(
        state: State, host: Host, aspect, old_value, new_value
    ):
        """Executes operations after the configuration setting.

        If overwritten, it is called automatically by set_configuration to
        perform post-setting operations.

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host
            aspect (str): Set aspect
            old_value (str): Old value
            new_value (str): New value

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _put_configuration(state: State, host: Host):
        """Uploads the local configuration to the target host.

        This method is automatically called by set_configuration and,
        optionnaly, by methods that modifies the configuration (for example,
        install).

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def install(state: State, host: Host):
        """Installs the solution in the target host.

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def test(state: State, host: Host):
        """Tests the proper functioning of the running solution.

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_logs(state: State, host: Host):
        """Retrieves the logs generated by the solution.

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_stats(state: State, host: Host):
        """Retrieves the stats generated by the solution.

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def update(state: State, host: Host):
        """Updates the solution to its latest version.

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def uninstall(state: State, host: Host):
        """Uninstalls the solution from the target host.

        Args:
            state (State): pyinfra's state
            host (Host): pyinfra's host

        Raises:
            NotImplementedError: Method not implemented
        """
        raise NotImplementedError
