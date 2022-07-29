"""Module with common facts for processes."""

import typing

from pyinfra.api import FactBase


class ProcessRunning(FactBase):
    """Fact for checking if a process is running."""

    def command(self, executable: str) -> str:
        return f"ps -axo cmd | egrep '^{executable}' | wc -l"

    @staticmethod
    def process(
        output: typing.List[str],
    ) -> bool:
        return int(output[0]) != 0
