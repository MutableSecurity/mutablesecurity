"""Module defining an abstract action."""
import typing
from abc import ABC, abstractmethod

Operation = typing.Annotated[typing.Callable, "pyinfra Operation"]


class BaseAction(ABC):
    """Abstract class modeling a possible action performed by the solution."""

    @property
    @abstractmethod
    def identifier(self) -> str:
        """Declare the identifier getter."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Declare the description getter."""

    @property
    @abstractmethod
    def act(self) -> Operation:
        """Declare the getter of the operation used to execute the action."""
