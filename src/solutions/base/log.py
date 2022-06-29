"""Module defining an abstract log source."""
from abc import ABC, abstractmethod

from pyinfra.api import FactBase


class BaseLog(ABC):
    """Abstract class modeling a log source of the solution."""

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
        """Declare the fact used to retrieve the logs."""
