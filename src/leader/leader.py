"""Module for connecting to taget hosts."""

import typing

from pyinfra.api import Config, Inventory, State
from pyinfra.api.connect import connect_all
from pyinfra.api.deploy import add_deploy
from pyinfra.api.exceptions import PyinfraError
from pyinfra.api.operations import run_ops

from ..helpers.exceptions import (
    FailedConnectionToHostsException,
    FailedExecutionException,
)
from .connections import Connection


class Leader:
    """Class managing target hosts."""

    hosts: list
    inventory: Inventory
    state: State
    unique_password: str  # TODO: Remove after having passwords for each host

    def __make_inventory(
        self,
        hosts: typing.Optional[tuple] = (),
        **kwargs: typing.Optional[dict]
    ) -> Inventory:
        """Create a pyinfra inventory.

        To be used only by children.

        Args:
            hosts (tuple, optional): Hosts to connect to. Defaults to ().
            kwargs (dict. optional): Additional named arguments

        Returns:
            Inventory: pyinfra inventory
        """
        return Inventory((hosts, {}), **kwargs)

    def attach_connection(self, host: Connection) -> None:
        """Attach a host to leader.

        Args:
            host (Connection): Details about the connection
        """
        self.hosts.append(host.export())

        # TODO: Remove after the TODO above
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
        self, operation: typing.Callable, **kwargs: typing.Optional[dict]
    ) -> None:
        """Execute an operation.

        Args:
            operation (typing.Callable): Operation to execute
            kwargs (dict. optional): Additional operation parameters

        Raises:
            FailedExecutionException: Could not execute the given operation.
        """
        try:
            add_deploy(self.state, operation, **kwargs)

            run_ops(self.state)
        except PyinfraError as exception:
            raise FailedExecutionException() from exception
