"""Module defining an abstract action."""
import typing

from mutablesecurity.helpers.exceptions import (
    SolutionActionNotFoundException,
    SolutionObjectNotFoundException,
)
from mutablesecurity.solutions.base.object import BaseManager, BaseObject

Operation = typing.Annotated[typing.Callable, "pyinfra Operation"]


class BaseAction(BaseObject):
    """Abstract class modeling a possible action performed by the solution.

    This class is stateless.
    """

    ACT: Operation


class ActionsManager(BaseManager):
    """Class managing the actions of a solution."""

    def __init__(self, actions: typing.Sequence[BaseAction]) -> None:
        """Initialize the instance.

        Args:
            actions (typing.Sequence[BaseAction]): List of actions to be added
        """
        super().__init__(actions)

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
            )  # type: ignore
        except SolutionObjectNotFoundException as exception:
            raise SolutionActionNotFoundException() from exception

        action.ACT(**args)
