"""Module defining an abstract information."""


import typing
from abc import ABC, abstractmethod
from enum import Enum

from pyinfra.api import FactBase

Operation = typing.Annotated[typing.Callable, "pyinfra Operation"]


class InformationType(Enum):
    """Enumeration for possible types for an information."""

    INTEGER = 0
    STRING = 1
    ENUM = 2
    LIST = 3


class InformationProperties(Enum):
    """Enumeration for possible properties of an information."""

    __TYPE_BASE = 0
    CONFIGURATION = __TYPE_BASE + 1
    METRIC = __TYPE_BASE + 2

    __OPTIONALITY_BASE = 10
    MANDATORY = __OPTIONALITY_BASE + 1
    OPTIONAL = __OPTIONALITY_BASE + 2
    NEEDED_AT_INSTALL = __OPTIONALITY_BASE + 3

    __MISC_BASE = 100
    AUTO_GENERATED = __MISC_BASE + 1


class BaseInformation(ABC):
    """Abstract class modeling an information related to the solution."""

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
    def default_value(self) -> typing.Any:
        """Declare the default value getter."""

    @property
    @abstractmethod
    def actual_value(self) -> typing.Any:
        """Declare the actual value getter."""

    @property
    @abstractmethod
    def info_type(self) -> InformationType:
        """Declare the infomation type's getter."""

    @property
    @abstractmethod
    def properties(self) -> typing.List[InformationProperties]:
        """Declare the getter of the properties describing the information."""

    @property
    @abstractmethod
    def getter(self) -> FactBase:
        """Declare the getter of the retrieving fact."""

    @abstractmethod
    def setter(self) -> Operation:
        """Declare the getter of the setting operation."""

    @abstractmethod
    def validate_value(self, value: typing.Any) -> bool:
        """Validate if the information's value is valid.

        Args:
            value (typing.Any): Value of the information

        Returns:
            bool: Boolean indicating if the information is valid
        """
