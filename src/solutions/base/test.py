"""Module defining an abstract action."""
from abc import ABC, abstractmethod
from enum import Enum

from pyinfra.api import FactBase


class TestType(Enum):
    """Enumeration for types of tests."""

    OPERATIONAL = 0
    SECURITY = 1
    INTEGRATION = 2


class BaseTest(ABC):
    """Abstract class modeling an atomic step for testing the solution."""

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
    def test_type(self) -> TestType:
        """Declare the test type's getter."""

    @property
    @abstractmethod
    def fact(self) -> FactBase:
        """Declare the getter of the fact used to execute the test.

        The fact shoud return a boolean indicating it the test is successful.
        """
