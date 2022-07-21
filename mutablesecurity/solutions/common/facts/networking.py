"""Module with common facts for networking."""
import json
import typing

from pyinfra.api import FactBase


class DefaultInterface(FactBase):
    """Fact for getting the default interface."""

    command = "ip -p -j route show default"

    @staticmethod
    def process(
        output: typing.List[str],
    ) -> str:
        interfaces = json.loads("\n".join(output))

        return interfaces[0]["dev"]


class InternetConnection(FactBase):
    """Fact for testing the Internet connection."""

    command = "ping -c 1 8.8.8.8 | grep -c '100% packet loss' || true"

    @staticmethod
    def process(
        output: typing.List[str],
    ) -> bool:
        return int(output[0]) == 0
