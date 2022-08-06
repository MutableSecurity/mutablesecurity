"""Module for implementing the solution manager logic.

For each module, there are multiple aspects handled:
- MutableSecurity module ID, embedded in each module's definition, used to
refer to the module (for example, when selecting from CLI the solution to be
installed) and same as the Python module name: dummy
- Class automating the management and deployment of the module: Dummy.
"""

import importlib
import os
import re
import typing

from pypattyrn.creational.singleton import Singleton

from mutablesecurity.helpers.exceptions import (
    OperationNotImplementedException,
    SolutionNotPresentException,
)
from mutablesecurity.helpers.python import find_public_methods
from mutablesecurity.solutions.base import (
    BaseSolution,
    BaseSolutionType,
    SolutionMaturityLevels,
)
from mutablesecurity.solutions_manager.filter import SolutionsFilter
from mutablesecurity.solutions_manager.sorter import SolutionsSorter
from mutablesecurity.solutions_manager.types import (
    SolutionsGenerator,
    SolutionsList,
)


class SolutionsManager(metaclass=Singleton):
    """Class for managing solutions automations."""

    solutions: SolutionsList
    solutions_filter: SolutionsFilter
    solutions_sorter: SolutionsSorter

    def __init__(self) -> None:
        """Initialize the instance."""
        self.solutions = list(self.__get_all_solution_classes())
        self.solutions_filter = SolutionsFilter(self.solutions)

    def __get_all_solutions_py_modules(
        self,
    ) -> typing.Generator[str, None, None]:
        solutions_folder = os.path.join(
            os.path.dirname(__file__), "../solutions/implementations"
        )

        for entry in os.scandir(solutions_folder):
            if entry.is_dir() and not entry.name.startswith("_"):
                yield entry.name

    def __get_all_solution_classes(self) -> SolutionsGenerator:
        for module_id in self.__get_all_solutions_py_modules():
            yield self.get_solution_class_by_id(module_id)

    def __translate_solution_id_to_class_name(self, solution_id: str) -> str:
        solution_id = solution_id.capitalize()

        def convert_to_upper(match: re.Match) -> str:
            return match.group()[1].upper()

        return re.sub(r"_[a-z]", convert_to_upper, solution_id.capitalize())

    def __translate_operation_name_to_id(self, operation_name: str) -> str:
        return operation_name.upper()

    def __translate_operation_id_to_name(self, operation_id: str) -> str:
        return operation_id.lower()

    def get_production_solutions(self) -> SolutionsList:
        """Get the locally available solutions.

        The modules should have the maturity adequate to the current settings.

        Returns:
            SolutionsList: List of solutions identifiers
        """
        return list(self.solutions_filter.is_usable_in_production())

    def get_non_dev_solutions_sorted_desc_by_maturity(
        self,
    ) -> typing.List[BaseSolutionType]:
        """Get the non-development solutions sorted descending by maturity.

        Returns:
            typing.List[BaseSolutionType]: List of solutions
        """
        solutions = SolutionsManager().get_production_solutions()
        non_dev_solutions = list(
            SolutionsFilter(solutions).had_not_maturity_level(
                SolutionMaturityLevels.DEV_ONLY
            )
        )

        return SolutionsSorter(non_dev_solutions).by_maturity(ascending=False)

    def get_solution_class_by_id(self, module_id: str) -> BaseSolutionType:
        """Get a solution class by its identifier.

        Args:
            module_id (str): Solution's identifier

        Raises:
            SolutionNotPresentException: The selected solution is not present
                locally.

        Returns:
            BaseSolutionType: Implementation class
        """
        class_name = self.__translate_solution_id_to_class_name(module_id)

        try:
            module = importlib.import_module(
                f"mutablesecurity.solutions.implementations.{module_id}.code"
            )

            return getattr(module, class_name)
        except (ImportError, AttributeError) as exception:
            raise SolutionNotPresentException() from exception

    def get_available_operations_ids(self) -> typing.List[str]:
        """Get the operations implemented for a solution.

        Returns:
            typing.List[str]: List of operations' names
        """
        exported_methods = find_public_methods(BaseSolution)
        operations = [
            self.__translate_operation_name_to_id(method)
            for method in exported_methods
        ]

        return operations

    def get_operation_by_id(
        self,
        solution: typing.Union[BaseSolution, typing.Type[BaseSolution]],
        operation_id: str,
    ) -> typing.Callable:
        """Retrieve an operation by its name.

        Args:
            solution (typing.Type[BaseSolution]): Solution or solution class
            operation_id (str): Operation's name

        Raises:
            OperationNotImplementedException: The selected operation is not
                implemented.

        Returns:
            typing.Callable: Operation function
        """
        operation_name = self.__translate_operation_id_to_name(operation_id)
        try:
            return getattr(solution, operation_name)
        except AttributeError as exception:
            raise OperationNotImplementedException() from exception
