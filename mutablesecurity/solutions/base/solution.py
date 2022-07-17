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

from pyinfra import host
from pyinfra.api.deploy import deploy

from mutablesecurity.helpers.exceptions import (
    FailedSolutionTestException,
    InvalidMetaException,
    NoLocalConfigurationFileException,
    RequirementsNotMetException,
    SolutionNotInstalledException,
    YAMLFileNotExistsException,
    YAMLKeyMissingException,
)
from mutablesecurity.helpers.plain_yaml import dump_to_file, load_from_file
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


class BaseSolution(ABC):
    """Abstract class wrapping a security solution."""

    # Class members deduced from meta.yaml
    IDENTIFIER: str = ""
    FULL_NAME: str
    DESCRIPTION: str
    REFERENCES: typing.List[str]

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

    def __new__(  # type: ignore
        cls: typing.Type["BaseSolution"],  # pylint: disable=unused-argument
        *args: tuple,
        **kwargs: typing.Any,
    ) -> "BaseSolution":
        """Initialize the class after definition.

        Args:
            args (tuple): Positional arguments
            kwargs (typing.Any): Keyword arguments

        Returns:
            BaseSolution: Class
        """
        cls.__load_meta()

        cls.IDENTIFIER = cls.__module__.split(".")[-2]

        # Attach the actions
        cls.INFORMATION_MANAGER = InformationManager(cls.INFORMATION)
        cls.TESTS_MANAGER = TestsManager(cls.TESTS)
        cls.LOGS_MANAGER = LogsManager(cls.LOGS)
        cls.ACTIONS_MANAGER = ActionsManager(cls.ACTIONS)

        instance: "BaseSolution" = super(BaseSolution, cls).__new__(cls)

        return instance

    @classmethod
    def __build_manager_result(
        cls: typing.Type["BaseSolution"],
        manager: BaseManager,
        concrete_results: BaseConcreteResultObjects,
    ) -> ConcreteObjectsResult:
        return ConcreteObjectsResult(
            manager.KEYS_DESCRIPTIONS,
            manager.objects_descriptions,
            concrete_results,
        )

    @classmethod
    def __load_meta(cls: typing.Type["BaseSolution"]) -> None:
        """Load the meta YAML file containing the solution details.

        Raises:
            InvalidMetaException: Invalid meta YAML file
        """
        # Load the meta YAML file
        module = inspect.getmodule(cls)
        if module is None or not module.__file__:
            raise InvalidMetaException()
        module_path = os.path.dirname(module.__file__)
        meta_filename = os.path.join(module_path, "meta.yaml")
        mandatory_keys = [key.value for key in cls.MetaKeys]
        try:
            meta = load_from_file(meta_filename, mandatory_keys)
        except YAMLKeyMissingException as exception:
            raise InvalidMetaException() from exception

        # Save the values into the class' members
        cls.FULL_NAME = meta[cls.MetaKeys.FULL_NAME.value]
        cls.DESCRIPTION = meta[cls.MetaKeys.DESCRIPTION.value]
        cls.REFERENCES = meta[cls.MetaKeys.REFERENCES.value]

    @classmethod
    def __get_configuration_filename(cls: typing.Type["BaseSolution"]) -> str:
        return f"{host}_{cls.IDENTIFIER}.yaml"

    @classmethod
    def __load_current_configuration_from_file(
        cls: typing.Type["BaseSolution"],
    ) -> None:
        try:
            configuration = load_from_file(cls.__get_configuration_filename())
        except YAMLFileNotExistsException as exception:
            raise NoLocalConfigurationFileException() from exception

        cls.INFORMATION_MANAGER.set_all_from_dict_locally(configuration)

    @classmethod
    def __save_current_configuration_as_file(
        cls: typing.Type["BaseSolution"],
    ) -> None:
        """Save the current configuration as a file."""
        configuration = cls.INFORMATION_MANAGER.represent_as_dict(
            filter_property=InformationProperties.CONFIGURATION
        )
        dump_to_file(configuration, cls.__get_configuration_filename())

    @classmethod
    @deploy
    def __get_information_from_remote(
        cls: typing.Type["BaseSolution"],
        identifier: typing.Optional[str] = None,
    ) -> typing.Any:
        """Get an information from a target host.

        Args:
            identifier (str, optional): Key identifying the information.
                Defaults to None.

        Returns:
            typing.Any: Information value
        """
        return cls.INFORMATION_MANAGER.get(identifier)

    @classmethod
    @deploy
    def __ensure_installed(cls: typing.Type["BaseSolution"]) -> None:
        """Ensure that the solution is installed.

        Mandatory executed when performing actions against an already-installed
        solution.

        Raises:
            SolutionNotInstalledException: The solution is not installed on the
                system.
        """
        cls.__load_current_configuration_from_file()

        try:
            cls.TESTS_MANAGER.test(None, TestType.PRESENCE)
        except FailedSolutionTestException as exception:
            raise SolutionNotInstalledException() from exception

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
        """Install the security solution.

        Raises:
            RequirementsNotMetException: The requirements are not met.
        """
        cls.__load_current_configuration_from_file()

        # Ensure that the requirements are met
        try:
            cls.TESTS_MANAGER.test(None, TestType.REQUIREMENT)
        except FailedSolutionTestException as exception:
            raise RequirementsNotMetException() from exception

        cls._install()

    @classmethod
    @deploy
    def get_information(
        cls: typing.Type["BaseSolution"],
        identifier: typing.Optional[str] = None,
    ) -> ConcreteObjectsResult:
        """Get an information from a target host.

        Args:
            identifier (str, optional): Key identifying the information.
                Defaults to None.

        Returns:
            ConcreteObjectsResult: Response with the requested information
        """
        cls.__ensure_installed()

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
        cls.__ensure_installed()
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
            identifier (str, optional): Key identifying the test. Defaults to
                None.

        Returns:
            ConcreteObjectsResult: Result with tests results
        """
        cls.__ensure_installed()
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
            identifier (str, optional): Key identifying the log source.
                Defaults to None.

        Returns:
            ConcreteObjectsResult: Result with the requested logs
        """
        cls.__ensure_installed()
        cls.__get_information_from_remote()

        results = cls.LOGS_MANAGER.get_content(identifier)

        return cls.__build_manager_result(cls.LOGS_MANAGER, results)

    @classmethod
    @deploy
    def update(cls: typing.Type["BaseSolution"]) -> None:
        """Update the security solution."""
        cls.__ensure_installed()
        cls.__get_information_from_remote()

        cls._update()

    @classmethod
    @deploy
    def uninstall(cls: typing.Type["BaseSolution"]) -> None:
        """Uninstall a security solution."""
        cls.__ensure_installed()
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
                of the action. Defaults to None.
        """
        cls.__ensure_installed()
        cls.__get_information_from_remote()

        cls.ACTIONS_MANAGER.execute(identifier, args)
