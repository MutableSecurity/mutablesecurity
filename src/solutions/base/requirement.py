"""Module defining an abstract system requirement."""
from abc import ABC, abstractmethod

from pyinfra.api import FactBase


class BaseRequirement(ABC):
    """Abstract class modeling a system requirement."""

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
    def fact(self) -> FactBase:
        """Declare the getter of the fact used to check the requirement."""
