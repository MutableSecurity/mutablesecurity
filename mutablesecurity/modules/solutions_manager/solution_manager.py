import abc
import importlib
from enum import Enum


class AvailableSolution(Enum):
    SURICATA = ("suricata", "Suricata")


class AbstractSolution(abc.ABC):
    configuration_meta = None
    _configuration = None

    @abc.abstractstaticmethod
    def get_configuration(state=None, host=None):
        raise NotImplemented()

    @abc.abstractstaticmethod
    def _verify_new_configuration(aspect=None, value=None):
        raise NotImplemented()

    @abc.abstractstaticmethod
    def set_configuration(state=None, host=None, aspect=None, value=None):
        raise NotImplemented()

    @abc.abstractstaticmethod
    def _put_configuration(state=None, host=None):
        raise NotImplemented()

    @abc.abstractstaticmethod
    def update(state=None, host=None):
        raise NotImplemented()

    @abc.abstractstaticmethod
    def install(state=None, host=None):
        raise NotImplemented()

    @abc.abstractstaticmethod
    def test(state=None, host=None):
        raise NotImplemented()

    @abc.abstractstaticmethod
    def get_stats(state=None, host=None):
        raise NotImplemented()

    @abc.abstractstaticmethod
    def get_logs(state=None, host=None):
        raise NotImplemented()

    @abc.abstractstaticmethod
    def uninstall(state=None, host=None):
        raise NotImplemented()


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
