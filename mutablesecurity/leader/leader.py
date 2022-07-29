"""Module for connecting to target hosts."""

import typing

from pyinfra.api import Config, Inventory, State
from pyinfra.api.connect import connect_all
from pyinfra.api.deploy import add_deploy
from pyinfra.api.exceptions import PyinfraError
from pyinfra.api.operations import run_ops
from pypattyrn.creational.singleton import Singleton

from mutablesecurity.helpers.exceptions import (
    FailedConnectionToHostsException,
    FailedExecutionException,
)
from mutablesecurity.leader.connections import Connection

if typing.TYPE_CHECKING:
    from mutablesecurity.main import SecurityDeploymentResult


class Leader(object, metaclass=Singleton):
    """Class managing target hosts."""

    hosts: list
    inventory: Inventory
    state: State
    unique_password: typing.Optional[
        str
    ]  # TODO: Remove after having passwords for each host
    results: typing.List["SecurityDeploymentResult"]

    def __init__(self) -> None:
        """Initialize the object."""
        self.hosts = []
        self.results = []

    def __make_inventory(
        self, hosts: tuple, **kwargs: typing.Any
    ) -> Inventory:
        return Inventory((hosts, {}), **kwargs)

    def attach_connection(self, host: Connection) -> None:
        """Attach a host to leader.

        Args:
            host (Connection): Details about the connection
        """
        self.hosts.append(host.export())

        # TODO: Remove after the above one
        self.unique_password = host.password

    def connect(self) -> None:
        """Connect to target hosts.

        Raises:
            FailedConnectionToHostsException: Could not connect to host.
        """
        self.inventory = self.__make_inventory(hosts=tuple(self.hosts))
        self.state = State(self.inventory, Config())

        self.state.config.SUDO = True
        self.state.config.USE_SUDO_PASSWORD = self.unique_password

        try:
            connect_all(self.state)
        except PyinfraError as exception:
            raise FailedConnectionToHostsException() from exception

    def run_operation(
        self, operation: typing.Callable, **kwargs: typing.Any
    ) -> None:
        """Execute an operation.

        Args:
            operation (typing.Callable): Operation to execute
            kwargs (typing.Any): Additional operation parameters

        Raises:
            FailedExecutionException: Could not execute the given operation.
        """
        try:
            add_deploy(self.state, operation, **kwargs)

            run_ops(self.state)
        except PyinfraError as exception:
            raise FailedExecutionException() from exception

    def publish_result(self, result: "SecurityDeploymentResult") -> None:
        """Publish a deployment result.

        Args:
            result (SecurityDeploymentResult): Deployment result
        """
        self.results.append(result)
