"""Module for sorting security solutions based on different properties."""
from functools import cmp_to_key

from mutablesecurity.solutions.base import BaseSolutionType
from mutablesecurity.solutions_manager.types import SolutionsList


class SolutionsSorter:
    """Class for sorting arrays of security solutions."""

    solutions: SolutionsList

    def __init__(self, solutions: SolutionsList) -> None:
        """Initialize the instance.

        Args:
            solutions (SolutionsList): List of security solutions, that will be
                sorted by every public method
        """
        self.solutions = solutions

    def by_maturity(self, ascending: bool = True) -> SolutionsList:
        """Get all non-development solutions, ordered by maturity.

        Args:
            ascending (bool): Boolean indicating if the ordering should be
                ascending. Defaults to True.

        Returns:
            SolutionsList: Maturity-ordered solutions
        """

        def maturity_compare(
            first: BaseSolutionType, second: BaseSolutionType
        ) -> int:
            return int(first.MATURITY) - int(second.MATURITY)

        solutions = list(self.solutions)
        solutions.sort(key=cmp_to_key(maturity_compare))

        if not ascending:
            solutions.reverse()

        return solutions
