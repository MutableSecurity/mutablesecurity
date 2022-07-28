"""Module for implementing the solution manager logic."""

import importlib
import os
import re
import typing

from mutablesecurity import config
from mutablesecurity.helpers.exceptions import (
    OperationNotImplementedException,
    SolutionNotPresentException,
    UnacceptedSolutionMaturityException,
)
from mutablesecurity.helpers.python import find_public_methods
from mutablesecurity.solutions.base import BaseSolution, SolutionMaturity


class SolutionsManager:
    """Class for managing solutions automations."""

    def __translate_solution_module_to_id(
        self, solution_module_name: str
    ) -> str:
        return solution_module_name.upper()

    def __translate_solution_id_to_class_name(self, solution_id: str) -> str:
        solution_id = solution_id.lower().capitalize()

        def convert_to_upper(match: re.Match) -> str:
            return match.group()[1].upper()

        return re.sub(r"_[a-z]", convert_to_upper, solution_id.capitalize())

    def __translate_solution_id_to_module_name(self, solution_id: str) -> str:
        return solution_id.lower()

    def __translate_operation_name_to_id(self, operation_name: str) -> str:
        return operation_name.upper()

    def __translate_operation_id_to_name(self, operation_id: str) -> str:
        return operation_id.lower()

    def __get_all_solutions_modules(self) -> typing.Generator[str, None, None]:
        solutions_folder = os.path.join(
            os.path.dirname(__file__), "../solutions/implementations"
        )

        for entry in os.scandir(solutions_folder):
            if entry.is_dir() and not entry.name.startswith("_"):
                yield self.__translate_solution_module_to_id(entry.name)

    def get_available_solutions_ids(self) -> typing.List[str]:
        """Get the locally available solutions.

        Returns:
            typing.List[str]: List of solutions identifiers
        """
        solutions = []
        for solution_module in self.__get_all_solutions_modules():
            solution_id = self.__translate_solution_module_to_id(
                solution_module
            )

            try:
                self.get_solution_by_id(solution_id)
            except UnacceptedSolutionMaturityException:
                continue

            solutions.append(
                self.__translate_solution_module_to_id(solution_module)
            )

        return solutions

    def get_solution_by_id(
        self, solution_id: str, maturity_check: bool = True
    ) -> typing.Type[BaseSolution]:
        """Get a solution class by its identifier.

        Args:
            solution_id (str): Solution's identifier
            maturity_check (bool): Boolean indicating if a maturity check is
                executed. This is useful for developers, as this will be
                bypassed. Defaults to True.

        Raises:
            SolutionNotPresentException: The selected solution is not present
                locally.
            UnacceptedSolutionMaturityException: The maturity of the solution
                does not correspond to user's profile.

        Returns:
            BaseSolution: Implementation class
        """
        module_name = self.__translate_solution_id_to_module_name(solution_id)
        class_name = self.__translate_solution_id_to_class_name(solution_id)

        try:
            module = importlib.import_module(
                f"mutablesecurity.solutions.implementations.{module_name}.code"
            )

            returned_class = getattr(module, class_name)
        except (ImportError, AttributeError) as exception:
            raise SolutionNotPresentException() from exception

        if (
            maturity_check
            and not config.developer_mode
            and returned_class.MATURITY is not SolutionMaturity.PRODUCTION
        ):
            raise UnacceptedSolutionMaturityException()

        return returned_class

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
