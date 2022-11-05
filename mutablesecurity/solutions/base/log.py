"""Module defining an abstract log source."""
import typing
from enum import Enum

from pyinfra import host
from pyinfra.api import FactBase

from mutablesecurity.helpers.exceptions import (
    InvalidSolutionLocationTypeException,
    SolutionLogIdentifierNotSpecifiedException,
    SolutionLogNotFoundException,
    SolutionObjectNotFoundException,
)
from mutablesecurity.solutions.base.information import BaseInformation
from mutablesecurity.solutions.base.object import BaseManager, BaseObject
from mutablesecurity.solutions.base.result import (
    BaseConcreteResultObjects,
    BaseGenericObjectsDescriptions,
    KeysDescriptions,
)


class LogFormat(Enum):
    """Enumeration defining possible format for log locations."""

    TEXT = "text"
    JSON = "json"

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
    LOCATION: typing.Union[str, BaseInformation]

    @classmethod
    def get_log_location_as_string(
        cls: typing.Type["BaseLog"], abstract: bool = False
    ) -> str:
        """Get the location as a string.

        Args:
             abstract (bool): Boolean indicating if the operations are
                performed over an installed solution

        Raises:
            InvalidSolutionLocationTypeException: The log type is invalid.

        Returns:
            str: Location as a string
        """
        if isinstance(cls.LOCATION, str):
            return cls.LOCATION
        elif issubclass(
            cls.LOCATION, BaseInformation  # type: ignore[arg-type]
        ):
            return (
                f"{cls.LOCATION.__name__}"  # type: ignore[attr-defined]
                "-dependent"  # type: ignore[attr-defined]
                if abstract
                else cls.LOCATION.get()
            )
        else:
            raise InvalidSolutionLocationTypeException()


class LogsManager(BaseManager):
    """Class managing the logs of a solution."""

    class DefaultGetterFact(FactBase):
        """Class to get the content of the file."""

        @staticmethod
        def command(location: str) -> str:
            """Generate the command to retrieve the content of the file.

            Args:
                location (str): String location

            Returns:
                str: Command
            """
            return f"cat {location} || true"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            """Process the file content.

            Args:
                output (typing.List[str]): Raw content

            Returns:
                str: Processed content
            """
            return "\n".join(output)

    objects_descriptions: BaseGenericObjectsDescriptions
    KEYS_DESCRIPTIONS: KeysDescriptions = {
        "identifier": "Identifier",
        "description": "Description",
        "location": "Location",
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
                "location": log.get_log_location_as_string(abstract=True),
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

        return {
            log.IDENTIFIER: host.get_fact(
                self.DefaultGetterFact, log.get_log_location_as_string()
            )
            for log in log_list
        }
