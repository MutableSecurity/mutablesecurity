"""Module with common facts for operating systems."""

import typing

from pyinfra.api import FactBase


class CheckIfUbuntu(FactBase):
    """Fact for checking if an operating system is Ubuntu."""

    command = "awk -F '=' '/PRETTY_NAME/ { print $2 }' /etc/os-release"

    @staticmethod
    def process(output: typing.List[str]) -> bool:
        return "ubuntu" in output[0].lower()
