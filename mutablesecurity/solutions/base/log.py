"""Module defining an abstract log source."""
import typing
from enum import Enum

from pyinfra import host
from pyinfra.api import FactBase

from mutablesecurity.helpers.exceptions import (
    SolutionLogIdentifierNotSpecifiedException,
    SolutionLogNotFoundException,
    SolutionObjectNotFoundException,
)
from mutablesecurity.solutions.base.object import BaseManager, BaseObject
from mutablesecurity.solutions.base.result import (
    BaseConcreteResultObjects,
    BaseGenericObjectsDescriptions,
    KeysDescriptions,
)


class LogFormat(Enum):
    """Enumeration defining possible format for log locations."""

    TEXT = 0
    JSON = 1

    def __str__(self) -> str:
        """Stringify the object.

        Returns:
            str: String representation
        """
        return self.name

    def __repr__(self) -> str:
        """Represent the object.

        Returns:
            str: String representation
        """
        return self.name


class BaseLog(BaseObject):
    """Abstract class modeling a log source of the solution.

    This class is stateless.
    """

    FORMAT: LogFormat
    FACT: FactBase


class LogsManager(BaseManager):
    """Class managing the logs of a solution."""

    objects_descriptions: BaseGenericObjectsDescriptions
    KEYS_DESCRIPTIONS: KeysDescriptions = {
        "identifier": "Identifier",
        "description": "Description",
        "format": "Format",
    }

    def __init__(self, logs: typing.Sequence[BaseLog]) -> None:
        """Initialize the instance.

        Args:
            logs (typing.Sequence[BaseLog]): List of log sources to be added
        """
        super().__init__(logs)

        self.objects_descriptions = [
            {
                "identifier": log.IDENTIFIER,
                "description": log.DESCRIPTION,
                "format": log.FORMAT,
            }
            for log in logs
        ]

    def get_content(
        self, identifier: typing.Optional[str] = None
    ) -> BaseConcreteResultObjects:
        """Execute a specific action, with the given arguments.

        Args:
            identifier (str): Log source identifier. Defaults to None in case
                all the information will be retrieved.

        Raises:
            SolutionLogNotFoundException: The identifier does not correspond
                to any log source.
            SolutionLogIdentifierNotSpecifiedException: No identifier was
                provided.

        Returns:
            BaseConcreteResultObjects: Content of log sources
        """
        if not identifier:
            raise SolutionLogIdentifierNotSpecifiedException()

        log_list = []
        try:
            log: BaseLog = self.get_object_by_identifier(
                identifier
            )  # type: ignore[assignment]
        except SolutionObjectNotFoundException as exception:
            raise SolutionLogNotFoundException() from exception

        log_list = [log]

        return {log.IDENTIFIER: host.get_fact(log.FACT) for log in log_list}
