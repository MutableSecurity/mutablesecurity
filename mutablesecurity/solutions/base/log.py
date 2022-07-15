"""Module defining an abstract log source."""
import typing

from pyinfra import host
from pyinfra.api import FactBase

from mutablesecurity.helpers.exceptions import (
    SolutionLogNotFoundException, SolutionObjectNotFoundException)
from mutablesecurity.solutions.base.object import BaseManager, BaseObject


class BaseLog(BaseObject):
    """Abstract class modeling a log source of the solution."""

    FACT: FactBase


class LogsManager(BaseManager):
    """Class managing the logs of a solution."""

    def __init__(self, logs: typing.Sequence[BaseLog]) -> None:
        """Initialize the instance.

        Args:
            logs (typing.Sequence[BaseLog]): List of logs to be added
        """
        super().__init__(logs)

    def get_content(self, identifier: typing.Optional[str]) -> typing.Any:
        """Execute a specific action, with the given arguments.

        Args:
            identifier (str, optional): Log source identifier. Defaults to
                None in case all the information will be retrieved.

        Raises:
            SolutionLogNotFoundException: The identifier does not correspond
                to any log source.

        Returns:
            typing.Any: If identifier, log source content. Else dictionary with
                keys - log source content
        """
        if identifier:
            try:
                log: BaseLog = self.get_object_by_identifier(
                    identifier
                )  # type: ignore
            except SolutionObjectNotFoundException as exception:
                raise SolutionLogNotFoundException() from exception

            return host.get_fact(log.FACT)

        else:
            return {
                log.IDENTIFIER: host.get_fact(log.FACT)  # type: ignore
                for log in self.objects.values()
            }
