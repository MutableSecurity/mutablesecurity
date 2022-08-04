"""Module for filtering solutions based on different criteria."""
from mutablesecurity import config
from mutablesecurity.solutions.base import SolutionMaturityLevels
from mutablesecurity.solutions_manager.types import (
    SolutionsGenerator,
    SolutionsList,
)


class SolutionsFilter:
    """Class for filtering lists of security solutions."""

    solutions: SolutionsList

    def __init__(self, solutions: SolutionsList) -> None:
        """Initialize the instance.

        Args:
            solutions (SolutionsList): List of security solutions, that is
                filtered by every public method
        """
        self.solutions = solutions

    def is_usable_in_production(self) -> SolutionsGenerator:
        """Get the solutions that are usable in production.

        The filtering is based on the current configuration. A developer will
        retrieve here all the solutions.

        Yields:
            SolutionsGenerator: Solutions generator
        """
        for solution in self.solutions:
            if (
                config.developer_mode
                or solution.MATURITY is SolutionMaturityLevels.PRODUCTION
            ):
                yield solution

    def had_not_maturity_level(
        self, maturity: SolutionMaturityLevels
    ) -> SolutionsGenerator:
        """Get the solutions that don't have a maturity level set.

        Args:
            maturity (SolutionMaturityLevels): Maturity level

        Yields:
            Iterator[SolutionsGenerator]: Solutions generator
        """
        for solution in self.solutions:
            if solution.MATURITY != maturity:
                yield solution
