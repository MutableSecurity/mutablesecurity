"""Module with common facts for networking."""

import typing

from pyinfra.api import FactBase


class FilePresenceTest(FactBase):
    """Fact for checking if a file is present on the system."""

    @staticmethod
    def command(path: str) -> str:
        return f"if [ -e {path} ] ; then echo '1'; else echo '0' ; fi"

    @staticmethod
    def process(output: typing.List[str]) -> bool:
        return int(output[0]) == 1
