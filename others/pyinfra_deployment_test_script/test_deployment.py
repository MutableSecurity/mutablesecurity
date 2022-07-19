#!/usr/bin/env python3
"""Python 3 script for connecting to a local WinRM instance via pyinfra.

This script requires to be ran with: poetry run <path_to_script>.

For Windows, you need to firstly enable WinRM by using the Powershell script
from the same directory.

If the system's password is not the set one ("password", see the code below),
change it via the USE_SUDO_PASSWORD member of the state.
"""

import os
import typing

from pyinfra import host
from pyinfra.api import Config, Inventory, State
from pyinfra.api.connect import connect_all
from pyinfra.api.deploy import add_deploy, deploy
from pyinfra.api.facts import FactBase
from pyinfra.api.operations import run_ops
from pyinfra.operations.server import shell

HostTuple = typing.Union[typing.Tuple[str, dict], str]
HostTupleList = typing.List[HostTuple]


class DummyFact(FactBase):
    """Dummy fact class.

    Can be replaced/deleted.
    """

    command = "dir"

    @staticmethod
    def process(output: typing.List[str]) -> str:
        """Process the returned lines.

        Args:
            output (typing.List[str]): Returned lines

        Returns:
            str: String containing all concatenated lines
        """
        return "\n".join(output)


def __make_inventory(hosts: HostTupleList) -> Inventory:
    """Create a pyinfra inventory.

    Args:
        hosts (HostTupleList): Hosts information

    Returns:
        Inventory: Created inventory
    """
    return Inventory((hosts, {}))


def make_inventory_cross_platform() -> Inventory:
    """Create an inventory depending on the platform.

    Returns:
        Inventory: Created inventory
    """
    if os.name == "posix":
        return __make_inventory(["@local"])
    elif os.name == "nt":
        return __make_inventory(
            hosts=[
                (
                    "@winrm/127.0.0.1",
                    {
                        "winrm_user": "mutablesecurity",
                        "winrm_password": "password",
                    },
                )
            ]
        )


@deploy
def test() -> None:
    """Test the execution of some operations.

    Can be replaced/deleted.
    """
    # Execute an operation
    shell(
        name="Dummy command",
        commands=["dir"],
    )

    # Get a fact
    host.get_fact(DummyFact)


def main() -> None:
    """Run the main functionality."""
    # Create the inventory
    inventory = make_inventory_cross_platform()
    state = State(inventory, Config())

    # Set the commands to be ran with sudo
    state.config.SUDO = True
    state.config.USE_SUDO_PASSWORD = "password"  # noqa: S105

    # Connect
    connect_all(state)

    # Execute a deployment
    add_deploy(state, test)
    run_ops(state)


if __name__ == "__main__":
    main()
