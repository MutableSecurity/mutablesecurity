"""Module for implementing the solution manager logic."""

import importlib
import os
import re
import typing

from src.helpers.exceptions import (
    OperationNotImplementedException,
    SolutionNotPresentException,
)
from src.helpers.python import find_decorated_methods
from src.solutions.base import BaseSolution, exported_functionality


class SolutionsManager:
    """Class for managing solutions automations."""

    def __translate_solution_id_to_class_name(self, solution_id: str) -> str:
        """Translate the identifier of a solution into its class name.

        Args:
            solution_id (str): Solution's identifier

        Returns:
            str: Implementation class
        """
        solution_id = solution_id.capitalize()

        def convert_to_upper(match: re.Match) -> str:
            """Convert a Regex match into its corresponding uppercase version.

            Args:
                match (re.Match): Regex match

            Returns:
                str: Uppercased result
            """
            return match.group()[1].upper()

        return re.sub(r"_[a-z]", convert_to_upper, solution_id.capitalize())

    def __translate_operation_name_to_id(self, operation_name: str) -> str:
        """Translate an operation name to an identifier.

        It only uppercases all the letters.

        Args:
            operation_name (str): Operation's name

        Returns:
            str: Operation's identifier
        """
        return operation_name.upper()

    def __translate_operation_id_to_name(self, operation_id: str) -> str:
        """Translate an operation identifier to a name.

        It only lowercases all the letters.

        Args:
            operation_id (str): Operation's identifier

        Returns:
            str: Operation's name
        """
        return operation_id.lower()

    def get_available_solutions_ids(self) -> typing.List[str]:
        """Get the locally available solutions.

        Returns:
            typing.List[str]: List of solutions identifiers
        """
        solutions_folder = os.path.join(
            os.path.dirname(__file__), "../solutions/implementations"
        )
        solutions = [
            entry.name
            for entry in os.scandir(solutions_folder)
            if entry.is_dir() and not entry.name.startswith("_")
        ]

        return solutions

    def get_solution_by_id(self, solution_id: str) -> BaseSolution:
        """Get a solution class by its identifier.

        Args:
            solution_id (str): Solution's identifier

        Raises:
            SolutionNotPresentException: The selected solution is not present
                locally.

        Returns:
            BaseSolution: Implementation class
        """
        class_name = self.__translate_solution_id_to_class_name(solution_id)

        try:
            module = importlib.import_module(
                f"src.solutions.implementations.{solution_id}.deployments"
            )

            return getattr(module, class_name)
        except (ImportError, AttributeError) as exception:
            raise SolutionNotPresentException() from exception

    def get_available_operations_ids(self) -> typing.List[str]:
        """Get the operations implemented for a solution.

        Returns:
            typing.List[str]: List of operations' names
        """
        exported_methods = find_decorated_methods(
            BaseSolution, exported_functionality
        )
        operations = [
            self.__translate_operation_name_to_id(method)
            for method in exported_methods
        ]

        return operations

    def get_operation_by_id(
        self, solution: BaseSolution, operation_id: str
    ) -> typing.Callable:
        """Retrieve an operation by its name.

        Args:
            solution (BaseSolution): Solution
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
