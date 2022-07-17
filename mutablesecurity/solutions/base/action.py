"""Module defining an abstract action."""
import inspect
import typing

from mutablesecurity.helpers.exceptions import (
    SolutionActionNotFoundException,
    SolutionObjectNotFoundException,
)
from mutablesecurity.solutions.base.object import BaseManager, BaseObject
from mutablesecurity.solutions.base.result import (
    BaseGenericObjectsDescriptions,
    KeysDescriptions,
)

Operation = typing.Annotated[typing.Callable, "pyinfra Operation"]


class BaseAction(BaseObject):
    """Abstract class modeling a possible action performed by the solution.

    This class is stateless.
    """

    ACT: Operation

    @classmethod
    @property
    def PARAMETERS_KEYS(  # noqa: N802 # pylint: disable=invalid-name
        cls: typing.Type["BaseAction"],
    ) -> str:
        """Get the keys of the required parameters.

        Returns:
            str: Parameters keys
        """
        names = inspect.signature(cls.ACT).parameters.keys()

        return ", ".join(names)


class ActionsManager(BaseManager):
    """Class managing the actions of a solution."""

    objects_descriptions: BaseGenericObjectsDescriptions
    KEYS_DESCRIPTIONS: KeysDescriptions = {
        "identifier": "Identifier",
        "description": "Description",
        "parameters_keys": "Expected Parameters Keys",
    }

    def __init__(self, actions: typing.Sequence[BaseAction]) -> None:
        """Initialize the instance.

        Args:
            actions (typing.Sequence[BaseAction]): List of actions to be added
        """
        super().__init__(actions)

        self.objects_descriptions = [
            {
                "identifier": action.IDENTIFIER,
                "description": action.DESCRIPTION,
                "parameters_keys": action.PARAMETERS_KEYS,
            }
            for action in actions
        ]

    def execute(self, identifier: str, args: dict) -> None:
        """Execute a specific action, with the given arguments.

        Args:
            identifier (str): Action identifier
            args (dict): Action's arguments

        Raises:
            SolutionActionNotFoundException: The identifier does not correspond
                to any action.
        """
        try:
            action: BaseAction = self.get_object_by_identifier(
                identifier
            )  # type: ignore[assignment]
        except SolutionObjectNotFoundException as exception:
            raise SolutionActionNotFoundException() from exception

        action.ACT(**args)
