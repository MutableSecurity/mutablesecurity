"""Module for storing wrapped data types.

The module is mainly used when interacting with users, for actions and
information. One use-case is to convert a provided string to a proper Python
class.
"""
import typing
from enum import Enum

from mutablesecurity.helpers.exceptions import (
    EnumTypeNotSetException,
    InvalidDataValueToConvertException,
    NoDataTypeWithAnnotationException,
)


class InnerDataType(Enum):
    """Enumeration for possible types for an information."""

    __BASIC_TYPES_BASE = 0
    INTEGER = __BASIC_TYPES_BASE + 1
    STRING = __BASIC_TYPES_BASE + 2
    ENUM = __BASIC_TYPES_BASE + 3

    __LIST_BASE = 10
    LIST_OF_INTEGERS = __LIST_BASE + 0
    LIST_OF_STRINGS = __LIST_BASE + 1
    LIST_OF_ENUMS = __LIST_BASE + 2


class DataType:
    """Class for wrapping the data types."""

    ALIAS: str
    INNER_TYPE: InnerDataType
    BASE_ENUM: typing.Type[Enum]
    PYTHON_ANNOTATION: typing.Type
    DEFINED_TYPES: typing.List[typing.Type["DataType"]] = []

    def __init_subclass__(cls: typing.Type["DataType"]) -> None:
        """Initialize the child class after definition.

        It validates and registers its existence.

        Raises:
            EnumTypeNotSetException: The enumeration type is not provided.
        """
        super().__init_subclass__()

        if cls.INNER_TYPE in [
            InnerDataType.ENUM,
            InnerDataType.LIST_OF_ENUMS,
        ] and not getattr(cls, "BASE_ENUM", None):
            raise EnumTypeNotSetException()

        cls.DEFINED_TYPES.append(cls)

    @classmethod
    def name(cls: typing.Type["DataType"]) -> str:
        """Get the name of the underlying type.

        Returns:
            str: Name
        """
        return cls.INNER_TYPE.name

    @classmethod
    def convert_string(
        cls: typing.Type["DataType"],
        string: str,
    ) -> typing.Union[
        int, str, Enum, typing.List[int], typing.List[str], typing.List[Enum]
    ]:
        """Convert a string into its original representation.

        Args:
            string (str): Stringified data value

        Raises:
            InvalidDataValueToConvertException: The provided value is invalid.

        Returns:
            typing.Union[ int, str, Enum, typing.List[int], typing.List[str], \
                typing.List[Enum] ]: Converted value
        """
        try:
            if cls.INNER_TYPE == InnerDataType.INTEGER:
                return int(string)
            elif cls.INNER_TYPE == InnerDataType.ENUM:
                return cls.BASE_ENUM(string)
            elif cls.INNER_TYPE == InnerDataType.LIST_OF_INTEGERS:
                int_list = string.split(",")

                return [int(elem) for elem in int_list]
            elif cls.INNER_TYPE == InnerDataType.LIST_OF_STRINGS:
                return string.split(",")
            elif cls.INNER_TYPE == InnerDataType.LIST_OF_ENUMS:
                enum_list = string.split(",")

                return [cls.BASE_ENUM(elem) for elem in enum_list]

            return string

        except (KeyError, ValueError) as exception:
            raise InvalidDataValueToConvertException() from exception

    def __str__(self) -> str:
        """Stringify the object.

        Returns:
            str: String representation
        """
        return self.INNER_TYPE.name

    def __repr__(self) -> str:
        """Represent the object.

        Returns:
            str: String representation
        """
        return self.INNER_TYPE.name


class IntegerDataType(DataType):
    """Data type for integer."""

    ALIAS = "INTEGER"
    INNER_TYPE = InnerDataType.INTEGER
    PYTHON_ANNOTATION = int


class StringDataType(DataType):
    """Data type for strings."""

    ALIAS = "STRING"
    INNER_TYPE = InnerDataType.STRING
    PYTHON_ANNOTATION = str


class IntegerListDataType(DataType):
    """Data type for list of integers."""

    ALIAS = "LIST OF INTEGERS"
    INNER_TYPE = InnerDataType.LIST_OF_INTEGERS
    PYTHON_ANNOTATION = typing.List[int]


class StringListDataType(DataType):
    """Data type for list of strings."""

    ALIAS = "LIST OF STRINGS"
    INNER_TYPE = InnerDataType.LIST_OF_STRINGS
    PYTHON_ANNOTATION = typing.List[str]


class DataTypeFactory:
    """Factory class to return a DataType class."""

    @staticmethod
    def create_from_annotation(
        annotation: typing.Type,
    ) -> typing.Type[DataType]:
        """Return a DataType class based on a Python type annotation.

        Args:
            annotation (typing.Type): Python annotation to convert

        Raises:
            NoDataTypeWithAnnotationException: No type correspond to the given
                annotation.

        Returns:
            typing.Type[DataType]: Corresponding data type
        """
        for current_type in DataType.DEFINED_TYPES:
            if current_type.PYTHON_ANNOTATION == annotation:
                return current_type

        raise NoDataTypeWithAnnotationException()
