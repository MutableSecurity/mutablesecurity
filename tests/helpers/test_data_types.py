"""Module for testing the data types."""

import pytest

from mutablesecurity.helpers.data_type import DataType, DataTypeFactory
from mutablesecurity.helpers.exceptions import (
    NoDataTypeWithAnnotationException,
)


class InvalidClassUsedForAnnotation:
    """Dummy class used for annotations."""


def test_valid_type_creation() -> None:
    """Test if a data type is returned when providing a valid annotation."""
    returned_type = DataTypeFactory().create_from_annotation(int)
    assert issubclass(
        returned_type, DataType
    ), "The returned data type is incorrect for an integer annotation."


def test_invalid_type_creation() -> None:
    """Tests if an exception is raised when providing an invalid annotation."""
    with pytest.raises(NoDataTypeWithAnnotationException) as execution:
        DataTypeFactory().create_from_annotation(InvalidClassUsedForAnnotation)

    exception_raised = execution.value
    assert (
        exception_raised
    ), "Exception not raised when using an invalid annotation."
