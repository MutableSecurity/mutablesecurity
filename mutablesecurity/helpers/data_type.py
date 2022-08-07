"""Module for storing wrapped data types.

The module is mainly used when interacting with users. One use-case is to
convert a provided string to a proper Python class.
"""
import typing
from enum import Enum

from mutablesecurity.helpers.exceptions import (
    EnumTypeNotSetException,
    InvalidBooleanValueException,
    InvalidDataValueToConvertException,
    NoDataTypeWithAnnotationException,
)


def str_to_bool(string: str) -> bool:
    """Convert a string into a boolean.

    Args:
        string (str): String

    Raises:
        InvalidBooleanValueException: The specified boolean value is invalid.

    Returns:
        bool: Boolean
    """
    string = string.lower()
    if string == "true":
        return True
    elif string == "false":
        return False
    else:
        raise InvalidBooleanValueException()


class InnerDataType(Enum):
    """Enumeration for possible types for a piece of data."""

    __BASIC_TYPES_BASE = 0
    BOOLEAN = __BASIC_TYPES_BASE + 1
    INTEGER = __BASIC_TYPES_BASE + 2
    STRING = __BASIC_TYPES_BASE + 3
    ENUM = __BASIC_TYPES_BASE + 4

    __LIST_BASE = 10
    LIST_OF_BOOLEANS = __LIST_BASE + 0
    LIST_OF_INTEGERS = __LIST_BASE + 1
    LIST_OF_STRINGS = __LIST_BASE + 2
    LIST_OF_ENUMS = __LIST_BASE + 3


class DataType:
    """Class for wrapping the data types.

    The role of this indirection (with class and back enumeration) is produced
    by the optional base enumeration.
    """

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
        bool,
        int,
        str,
        Enum,
        typing.List[bool],
        typing.List[int],
        typing.List[str],
        typing.List[Enum],
    ]:
        """Convert a string into its original representation.

        Args:
            string (str): Stringified data value

        Raises:
            InvalidDataValueToConvertException: The provided value is invalid.

        Returns:
            typing.Union[bool, int, str, Enum, typing.List[bool],
                typing.List[int], typing.List[str], typing.List[Enum]]:
                Converted value
        """
        if not string or not isinstance(string, str):
            raise InvalidDataValueToConvertException()

        try:
            if cls.INNER_TYPE == InnerDataType.BOOLEAN:
                return str_to_bool(string)
            if cls.INNER_TYPE == InnerDataType.INTEGER:
                return int(string)
            elif cls.INNER_TYPE == InnerDataType.ENUM:
                return cls.BASE_ENUM(string)
            elif cls.INNER_TYPE == InnerDataType.LIST_OF_BOOLEANS:
                bool_list = string.split(",")

                return [str_to_bool(elem) for elem in bool_list]
            elif cls.INNER_TYPE == InnerDataType.LIST_OF_INTEGERS:
                int_list = string.split(",")

                return [int(elem) for elem in int_list]
            elif cls.INNER_TYPE == InnerDataType.LIST_OF_STRINGS:
                return string.split(",")
            elif cls.INNER_TYPE == InnerDataType.LIST_OF_ENUMS:
                enum_list = string.split(",")

                return [cls.BASE_ENUM(elem) for elem in enum_list]

            return string

        except (
            KeyError,
            ValueError,
            InvalidBooleanValueException,
        ) as exception:
            raise InvalidDataValueToConvertException() from exception

    @classmethod
    def validate_data(cls: typing.Type["DataType"], data: typing.Any) -> bool:
        """Validate if a piece of data is of a type.

        Args:
            data (typing.Any): Verified data

        Returns:
            bool: Boolean indicating if the data corresponds to the set type
        """
        return isinstance(data, cls.PYTHON_ANNOTATION)

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


class BooleanDataType(DataType):
    """Data type for boolean."""

    ALIAS = "BOOLEAN"
    INNER_TYPE = InnerDataType.BOOLEAN
    PYTHON_ANNOTATION = bool


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


class BooleanListDataType(DataType):
    """Data type for list of booleans."""

    ALIAS = "LIST_OF_BOOLEANS"
    INNER_TYPE = InnerDataType.LIST_OF_BOOLEANS
    PYTHON_ANNOTATION = typing.List[bool]


class IntegerListDataType(DataType):
    """Data type for list of integers."""

    ALIAS = "LIST_OF_INTEGERS"
    INNER_TYPE = InnerDataType.LIST_OF_INTEGERS
    PYTHON_ANNOTATION = typing.List[int]


class StringListDataType(DataType):
    """Data type for list of strings."""

    ALIAS = "LIST_OF_STRINGS"
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
