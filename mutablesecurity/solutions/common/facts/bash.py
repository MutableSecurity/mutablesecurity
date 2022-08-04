"""Module with common facts for interacting with Bash."""

import typing

from pyinfra.api import FactBase


class PresentCommand(FactBase):
    """Fact for checking if a command is recognized by Bash."""

    @staticmethod
    def command(command_with_zero_exit_code: str) -> str:
        return f"{command_with_zero_exit_code}; echo $?"

    @staticmethod
    def process(
        output: typing.List[str],
    ) -> bool:
        return int(output[-1]) == 0
