"""Module for connecting to taget hosts."""

import typing

from pyinfra.api import Config, Inventory, State
from pyinfra.api.connect import connect_all

from .connections import Connection


class Leader:
    """Class managing connections to target hosts."""

    hosts: list
    inventory: Inventory
    state: State
    unique_password: str  # TODO 1: Remove after having passwords for each host

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

    def attach_host(self, host: Connection) -> None:
        """Attach a host to leader.

        Args:
            host (Connection): Details about the connection
        """
        self.hosts.append(host.export())

        # TODO: Remove after the TODO above
        self.unique_password = host.password

    def connect(self) -> None:
        """Connect to target hosts."""
        self.inventory = self.__make_inventory(hosts=tuple(self.hosts))
        self.state = State(self.inventory, Config())

        self.state.config.SUDO = True
        self.state.config.USE_SUDO_PASSWORD = self.unique_password

        connect_all(self.state)
