"""Module for testing the management of solutions."""


import pytest

from src.helpers.exceptions import (
    OperationNotImplementedException,
    SolutionNotPresentException,
)
from src.solutions_manager import SolutionsManager


def test_valid_solutions_operations() -> None:
    """Test valid solutions and operations retrievals."""
    manager = SolutionsManager()

    # Get all the available solutions
    solutions = manager.get_available_solutions_ids()
    assert len(solutions) != 0, "No solution was retrieved."

    # Get a reference to the first solution
    solution_id = solutions[0]
    solution = manager.get_solution_by_id(solution_id)
    assert (
        solution is not None
    ), 'Solution with ID "{solution_id}" was not returned'
    assert isinstance(
        solution, object
    ), 'Solution with ID "{solution_id}" is not a class.'

    # Get all the operations
    operations = manager.get_available_operations_ids()
    assert len(operations) != 0, "No operation was retrieved."

    # Get an operation in the above solution
    operation_id = operations[0]
    operation = manager.get_operation_by_id(solution, operation_id)
    assert operation is not None, (
        'Operation with ID "{solution_id}" from solution with ID'
        ' "{operation_id}" was not returned.'
    )
    assert callable(operation), (
        'Operation with ID "{solution_id}" from solution with ID'
        ' "{operation_id}" is not a function.'
    )


def test_get_solution_by_invalid_id() -> None:
    """Test if an error is raised when passing an invalid solution ID."""
    manager = SolutionsManager()

    with pytest.raises(SolutionNotPresentException) as execution:
        manager.get_solution_by_id("security_panacea_free")

    exception_raised = execution.value
    assert exception_raised, "A security solution panacea was found!"


def test_get_operation_by_invalid_id() -> None:
    """Test if an error is raised when passing an invalid operation ID."""
    manager = SolutionsManager()

    solutions = manager.get_available_solutions_ids()
    solution_id = solutions[0]
    solution = manager.get_solution_by_id(solution_id)

    with pytest.raises(OperationNotImplementedException) as execution:
        manager.get_operation_by_id(solution, "PROTECT_ALL")

    exception_raised = execution.value
    assert exception_raised, (
        "An exception was not raised when retrieving an operation by an"
        " invalid ID!"
    )
