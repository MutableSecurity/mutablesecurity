"""Module adapting the solutions manager's output to be used in the CLI."""
import typing

from pypattyrn.creational.singleton import Singleton

from mutablesecurity.solutions_manager import SolutionsManager


class SolutionsManagerAdapter(metaclass=Singleton):
    """Class adapting the solutions manager's output to be used in CLI."""

    manager = SolutionsManager()

    def get_solutions_ids(self) -> typing.List[str]:
        """Get the solutions identifiers.

        Returns:
            typing.List[str]: Solutions identifiers
        """
        solutions = self.manager.get_production_solutions()

        return [solution.IDENTIFIER.upper() for solution in solutions]

    def get_operations_ids(self) -> typing.List[str]:
        """Get the operations identifiers.

        Returns:
            typing.List[str]: Operations identifiers
        """
        operations = self.manager.get_available_operations_ids()

        return [operation.upper() for operation in operations]
