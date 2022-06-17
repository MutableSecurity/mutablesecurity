import importlib

from .solutions import AvailableSolution


class SolutionsManager:
    @staticmethod
    def get_solution_by_name(solution_name):
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
