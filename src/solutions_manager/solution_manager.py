import importlib

from ..solutions_manager import AbstractSolution, AvailableSolution
from .solutions import AvailableSolution


class SolutionsManager:
    def get_solution_by_name(self, solution_name):
        if not solution_name:
            return False

        module = getattr(AvailableSolution, solution_name)

        # Get the values stored into the tuple
        module_name = module.value[0]
        class_name = module.value[1]

        # Import the module and the class (that is stored)
        try:
            module = importlib.import_module(
                f".solutions.{module_name}", package=__package__
            )

            return getattr(module, class_name)
        except (ImportError, AttributeError):
            return None

    def get_available_solutions_names(self):
        # TODO: Refactor after finishing the SolutionManager module
        solutions = [element.name for element in AvailableSolution]

        return solutions

    def get_available_operations_for_solution(self):
        # TODO: Refactor after finishing the SolutionManager module
        members = dir(AbstractSolution)
        methods = [
            member.upper()
            for member in members
            if member[0] != "_" and callable(getattr(AbstractSolution, member))
        ]

        return methods
