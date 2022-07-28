"""Module modeling the interface and common functionality for solutions.

All the functions in this module may raise MutableSecurityException exceptions
that are not defined explicitly in docstrings. The reasons are:
- The protected methods are used only in the public ones.
- The public methods use a decorator that catches and converts to an error
result.
"""

import inspect
import os
import typing
from abc import ABC, abstractmethod
from enum import Enum

from pyinfra.api.deploy import deploy

from mutablesecurity.helpers.exceptions import (
    InvalidMetaException,
    NoSolutionConfigurationFileException,
    RequirementsNotMetException,
    SolutionAlreadyInstalledException,
    SolutionNotInstalledException,
    YAMLFileNotExistsException,
    YAMLKeyMissingException,
)
from mutablesecurity.helpers.plain_yaml import dump_to_file, load_from_file
from mutablesecurity.leader import get_connection_for_host
from mutablesecurity.solutions.base.action import ActionsManager, BaseAction
from mutablesecurity.solutions.base.information import (
    BaseInformation,
    InformationManager,
    InformationProperties,
)
from mutablesecurity.solutions.base.log import BaseLog, LogsManager
from mutablesecurity.solutions.base.object import BaseManager
from mutablesecurity.solutions.base.result import (
    BaseConcreteResultObjects,
    ConcreteObjectsResult,
)
from mutablesecurity.solutions.base.test import (
    BaseTest,
    TestsManager,
    TestType,
)


class SolutionCategories(Enum):
    """Enumeration for defining categories of security solutions."""

    WEB_IDS = "Web Intrusion Detection System"
    NETWORK_IDPS = "Network Detection and Prevention System"
    WEB_ENCRYPTION = "Encryption for Web Applications"
    NONE = "No Security"

    def __str__(self) -> str:
        """Stringify a category.

        Returns:
            str: Stringified category
        """
        return self.value


class SolutionMaturity(Enum):
    """Enumeration for defining the solution's maturity level."""

    PRODUCTION = "Production"
    REFACTORING = "Under refactoring, but integrated in older versions"
    UNDER_DEVELOPMENT = "Under development"
    DEV_ONLY = "Only for development and testing purposes"

    def __str__(self) -> str:
        """Stringify the maturity level.

        Returns:
            str: Stringified maturity level
        """
        return self.value


class BaseSolution(ABC):
    """Abstract class wrapping a security solution."""

    # Class members deduced from meta.yaml
    IDENTIFIER: str = ""
    FULL_NAME: str
    DESCRIPTION: str
    REFERENCES: typing.List[str]
    MATURITY: SolutionMaturity
    CATEGORIES: typing.List[SolutionCategories]

    # Class members declared explicitly in the child class
    INFORMATION: typing.List[BaseInformation]
    TESTS: typing.List[BaseTest]
    LOGS: typing.List[BaseLog]
    ACTIONS: typing.List[BaseAction]

    # Class members automatically computed from the ones from the above section
    INFORMATION_MANAGER: InformationManager
    TESTS_MANAGER: TestsManager
    LOGS_MANAGER: LogsManager
    ACTIONS_MANAGER: ActionsManager

    class MetaKeys(Enum):
        """Class containing the mandatory key of a meta YAML file."""

        FULL_NAME = "full_name"
        DESCRIPTION = "description"
        REFERENCES = "references"
        MATURITY = "maturity"
        CATEGORIES = "categories"

    def __init_subclass__(cls: typing.Type["BaseSolution"]) -> None:
        """Initialize a subclass after definition."""
        super().__init_subclass__()

        cls.__load_meta()

        cls.IDENTIFIER = cls.__module__.split(".")[-2]

        # Attach the actions
        cls.INFORMATION_MANAGER = InformationManager(cls.INFORMATION)
        cls.TESTS_MANAGER = TestsManager(cls.TESTS)
        cls.LOGS_MANAGER = LogsManager(cls.LOGS)
        cls.ACTIONS_MANAGER = ActionsManager(cls.ACTIONS)

    @classmethod
    def __build_manager_result(
        cls: typing.Type["BaseSolution"],
        manager: BaseManager,
        concrete_results: BaseConcreteResultObjects,
        is_long_output: bool = False,
    ) -> ConcreteObjectsResult:
        return ConcreteObjectsResult(
            manager.KEYS_DESCRIPTIONS,
            manager.objects_descriptions,
            concrete_results,
            is_long_output,
        )

    @classmethod
    def __load_meta(cls: typing.Type["BaseSolution"]) -> None:
        # Load the meta YAML file
        module = inspect.getmodule(cls)
        if module is None or not module.__file__:
            raise InvalidMetaException()
        module_path = os.path.dirname(module.__file__)
        meta_filename = os.path.join(module_path, "meta.yaml")
        mandatory_keys = [key.value for key in cls.MetaKeys]
        try:
            meta = load_from_file(meta_filename, mandatory_keys=mandatory_keys)
        except YAMLKeyMissingException as exception:
            raise InvalidMetaException() from exception

        # Save the values into the class' members
        cls.FULL_NAME = meta[cls.MetaKeys.FULL_NAME.value]
        cls.DESCRIPTION = meta[cls.MetaKeys.DESCRIPTION.value]
        cls.REFERENCES = meta[cls.MetaKeys.REFERENCES.value]
        try:
            cls.MATURITY = SolutionMaturity[meta[cls.MetaKeys.MATURITY.value]]
            cls.CATEGORIES = [
                SolutionCategories[cat]
                for cat in meta[cls.MetaKeys.CATEGORIES.value]
            ]
        except KeyError as exception:
            raise InvalidMetaException() from exception

    @classmethod
    def __get_configuration_filename(cls: typing.Type["BaseSolution"]) -> str:
        host_id = get_connection_for_host()

        return f"{host_id}_{cls.IDENTIFIER}.yaml"

    @classmethod
    def __load_current_configuration_from_file(
        cls: typing.Type["BaseSolution"], post_installation: bool
    ) -> None:
        try:
            configuration = load_from_file(cls.__get_configuration_filename())
        except YAMLFileNotExistsException as exception:
            raise NoSolutionConfigurationFileException() from exception

        cls.INFORMATION_MANAGER.populate(configuration, post_installation)

    @classmethod
    def __save_current_configuration_as_file(
        cls: typing.Type["BaseSolution"],
    ) -> None:
        configuration = cls.INFORMATION_MANAGER.represent_as_dict(
            filter_properties=[
                InformationProperties.CONFIGURATION,
                InformationProperties.WRITABLE,
            ]
        )
        dump_to_file(configuration, cls.__get_configuration_filename())

    @classmethod
    @deploy
    def __get_information_from_remote(
        cls: typing.Type["BaseSolution"],
        identifier: typing.Optional[str] = None,
    ) -> typing.Any:
        return cls.INFORMATION_MANAGER.get(identifier)

    @classmethod
    @deploy
    def __ensure_installation_state(
        cls: typing.Type["BaseSolution"], installed: bool
    ) -> None:
        cls.__load_current_configuration_from_file(True)

        raised_exception = (
            SolutionNotInstalledException
            if installed
            else SolutionAlreadyInstalledException
        )
        cls.TESTS_MANAGER.test(
            None,
            TestType.PRESENCE,
            expected_value=installed,
            exception_when_fail=raised_exception,
        )

    @staticmethod
    @abstractmethod
    def _install() -> None:
        """Install the solution."""

    @staticmethod
    @abstractmethod
    @deploy
    def _uninstall() -> None:
        """Uninstall the already-installed solution."""

    @staticmethod
    @abstractmethod
    @deploy
    def _update() -> None:
        """Update the already-installed solution."""

    @classmethod
    @deploy
    def init(cls: typing.Type["BaseSolution"]) -> None:
        """Initialize the security solution lifecycle."""
        cls.INFORMATION_MANAGER.set_default_values_locally()
        cls.__save_current_configuration_as_file()

    @classmethod
    @deploy
    def install(cls: typing.Type["BaseSolution"]) -> None:
        """Install the security solution."""
        cls.__load_current_configuration_from_file(False)

        cls.__ensure_installation_state(False)

        # Ensure that the requirements are met
        cls.TESTS_MANAGER.test(
            None,
            TestType.REQUIREMENT,
            exception_when_fail=RequirementsNotMetException,
        )

        cls._install()

    @classmethod
    @deploy
    def get_information(
        cls: typing.Type["BaseSolution"],
        identifier: typing.Optional[str] = None,
    ) -> ConcreteObjectsResult:
        """Get an information from a target host.

        Args:
            identifier (str): Key identifying the information. Defaults to None
                if all the information needs to be retrieved.

        Returns:
            ConcreteObjectsResult: Response with the requested information
        """
        cls.__ensure_installation_state(True)

        results = cls.INFORMATION_MANAGER.get(identifier)
        cls.__save_current_configuration_as_file()

        return cls.__build_manager_result(cls.INFORMATION_MANAGER, results)

    @classmethod
    @deploy
    def set_information(
        cls: typing.Type["BaseSolution"],
        identifier: str,
        value: typing.Any,
    ) -> None:
        """Set an information to a target host.

        Args:
            identifier (str):  Key identifying the information
            value (typing.Any): New value of the information
        """
        cls.__ensure_installation_state(True)
        cls.__get_information_from_remote()

        cls.INFORMATION_MANAGER.set(identifier, value)

        cls.__save_current_configuration_as_file()

    @classmethod
    @deploy
    def test(
        cls: typing.Type["BaseSolution"],
        identifier: typing.Optional[str] = None,
    ) -> ConcreteObjectsResult:
        """Run a test against a security solution.

        Args:
            identifier (str): Key identifying the test. Defaults to None if all
                the tests needs to be executed.

        Returns:
            ConcreteObjectsResult: Result with tests results
        """
        cls.__ensure_installation_state(True)
        cls.__get_information_from_remote()

        results = cls.TESTS_MANAGER.test(identifier, only_check=True)

        return cls.__build_manager_result(cls.TESTS_MANAGER, results)

    @classmethod
    @deploy
    def get_logs(
        cls: typing.Type["BaseSolution"],
        identifier: typing.Optional[str] = None,
    ) -> ConcreteObjectsResult:
        """Get logs from a target host.

        Args:
            identifier (str): Key identifying the log source. Defaults to None
                if all the logs needs to be retrieved.

        Returns:
            ConcreteObjectsResult: Result with the requested logs
        """
        cls.__ensure_installation_state(True)
        cls.__get_information_from_remote()

        results = cls.LOGS_MANAGER.get_content(identifier)

        return cls.__build_manager_result(cls.LOGS_MANAGER, results, True)

    @classmethod
    @deploy
    def update(cls: typing.Type["BaseSolution"]) -> None:
        """Update the security solution."""
        cls.__ensure_installation_state(True)
        cls.__get_information_from_remote()

        cls._update()

    @classmethod
    @deploy
    def uninstall(cls: typing.Type["BaseSolution"]) -> None:
        """Uninstall a security solution."""
        cls.__ensure_installation_state(True)
        cls.__get_information_from_remote()

        cls._uninstall()

    @classmethod
    @deploy
    def execute(
        cls: typing.Type["BaseSolution"],
        identifier: str,
        args: typing.Dict[str, str],
    ) -> None:
        """Delegate the security solution to perform a specific action.

        Args:
            identifier (str): Key identifying the action
            args (typing.Dict[str, str]): Dictionary containing the arguments
                of the action. Defaults to None if all actions needs to be
                executed.
        """
        cls.__ensure_installation_state(True)
        cls.__get_information_from_remote()

        cls.ACTIONS_MANAGER.execute(identifier, args)
