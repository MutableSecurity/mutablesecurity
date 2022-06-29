"""Module with common facts for networking."""
import json
import typing

from pyinfra.api import FactBase


class DefaultInterface(FactBase):
    """Fact for getting the default interface."""

    command = "ip -p -j route show default"

    def process(  # pylint:  disable=arguments-differ
        self, output: typing.List[str]
    ) -> str:
        """Get the default interface from the JSON output.

        Args:
            output (typing.List[str]): List of lines

        Returns:
            str: Name of default interface
        """
        interfaces = json.loads("\n".join(output))

        return interfaces[0]["dev"]
