"""Module defining an abstract log source."""
import typing

from pyinfra import host
from pyinfra.api import FactBase

from mutablesecurity.helpers.exceptions import (
    SolutionLogNotFoundException,
    SolutionObjectNotFoundException,
)
from mutablesecurity.solutions.base.object import BaseManager, BaseObject
from mutablesecurity.solutions.base.result import BaseConcreteResultObjects


class BaseLog(BaseObject):
    """Abstract class modeling a log source of the solution.

    This class is stateless.
    """

    FACT: FactBase


class LogsManager(BaseManager):
    """Class managing the logs of a solution."""

    def __init__(self, logs: typing.Sequence[BaseLog]) -> None:
        """Initialize the instance.

        Args:
            logs (typing.Sequence[BaseLog]): List of logs to be added
        """
        super().__init__(logs)

    def get_content(
        self, identifier: typing.Optional[str]
    ) -> BaseConcreteResultObjects:
        """Execute a specific action, with the given arguments.

        Args:
            identifier (str, optional): Log source identifier. Defaults to
                None in case all the information will be retrieved.

        Raises:
            SolutionLogNotFoundException: The identifier does not correspond
                to any log source.

        Returns:
            BaseConcreteResultObjects: Content of log sources
        """
        log_list = []
        if identifier:
            try:
                log: BaseLog = self.get_object_by_identifier(
                    identifier
                )  # type: ignore
            except SolutionObjectNotFoundException as exception:
                raise SolutionLogNotFoundException() from exception

            log_list = [log]
        else:
            log_list = list(self.objects.values())  # type: ignore

        return {log.IDENTIFIER: host.get_fact(log.FACT) for log in log_list}
