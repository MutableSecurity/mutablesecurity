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
    MutableSecurityException,
    RequirementsNotMetException,
    SolutionNotInstalledException,
    YAMLKeyMissingException,
)
from mutablesecurity.helpers.plain_yaml import dump_to_file, load_from_file
from mutablesecurity.leader import Leader
from mutablesecurity.main import ResponseTypes, SecurityDeploymentResult
from mutablesecurity.solutions.base.action import ActionsManager, BaseAction
from mutablesecurity.solutions.base.information import (
    BaseInformation,
    InformationManager,
    InformationProperties,
)
from mutablesecurity.solutions.base.log import BaseLog, LogsManager
from mutablesecurity.solutions.base.test import (
    BaseTest,
    TestResult,
    TestsManager,
    TestType,
)


def exported_functionality(function: typing.Callable) -> typing.Callable:
    """Decorate an exported solution method.

    It includes:
    - Catching and reraising MutableSecurityException exceptions
    - Passing required keyword arguments.

    Args:
        function (typing.Callable): Function to decorate

    Returns:
        typing.Callable: Decorator
    """

    def inner(*args: tuple, **kwargs: typing.Any) -> None:
        """Catch MutableSecurityException exceptions.

        Args:
            args (tuple): Decorated function positional arguments
            kwargs (typing.Any): Decorated function keyword arguments
        """
        # Extract only the keyword parameters needed by the function
        signature = inspect.signature(function.__func__)  # type: ignore
        parameters = signature.parameters
        required_kwargs = {}
        if len(parameters) > 1:
            for key, _ in parameters.items():
                if key == "self" or key == "cls":
                    continue

                required_kwargs[key] = kwargs[key]

        try:
            raw_result = function.__func__(  # type: ignore
                *args, **required_kwargs
            )

            # Store the result into the leader module
            result = SecurityDeploymentResult(
                str(host), ResponseTypes.SUCCESS, "Success", raw_result
            )
            Leader().publish_result(result)
        except MutableSecurityException as exception:
            # Store the result into the leader module
            result = SecurityDeploymentResult(
                str(host), ResponseTypes.ERROR, str(exception)
            )
            Leader().publish_result(result)

    return inner


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

    # By now, disable the unused arguments warnings as they are required for
    # the interface with pyinfra.
    # pylint: disable=unused-argument

    def __new__(  # type: ignore
        cls: typing.Type["BaseSolution"], *args: tuple, **kwargs: typing.Any
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
        configuration = load_from_file(cls.__get_configuration_filename())
        cls.INFORMATION_MANAGER.set_all_from_dict(configuration)

    @classmethod
    def __save_current_configuration_as_file(
        cls: typing.Type["BaseSolution"],
    ) -> None:
        """Save the current configuration as a file."""
        configuration = cls.INFORMATION_MANAGER.get_all_as_dict(
            InformationProperties.CONFIGURATION
        )
        dump_to_file(configuration, cls.__get_configuration_filename())

    @classmethod
    @deploy
    def _get_information_from_remote(
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
        cls._ensure_installed()

        return cls.INFORMATION_MANAGER.get(identifier)

    @staticmethod
    @abstractmethod
    def _install() -> None:
        """Install the solution."""

    @classmethod
    @deploy
    def _ensure_installed(cls: typing.Type["BaseSolution"]) -> None:
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
    @deploy
    def _uninstall() -> None:
        """Uninstall the already-installed solution."""

    @staticmethod
    @abstractmethod
    @deploy
    def _update() -> None:
        """Update the already-installed solution."""

    @exported_functionality
    @classmethod
    @deploy
    def init(cls: typing.Type["BaseSolution"]) -> None:
        """Initialize the security solution lifecycle."""
        cls.INFORMATION_MANAGER.set_default_values()
        cls.__save_current_configuration_as_file()

    @exported_functionality
    @classmethod
    @deploy
    def install(cls: typing.Type["BaseSolution"]) -> None:
        """Install the security solution.

        Raises:
            RequirementsNotMetException: The requirements are not met.
        """
        cls.INFORMATION_MANAGER.validate()

        # Ensure that the requirements are met
        try:
            cls.TESTS_MANAGER.test(None, TestType.PRESENCE)
        except FailedSolutionTestException as exception:
            raise RequirementsNotMetException() from exception

        cls._install()

    @exported_functionality
    @classmethod
    @deploy
    def get_information(
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
        cls._ensure_installed()

        return cls.INFORMATION_MANAGER.get(identifier)

    @exported_functionality
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
        cls._ensure_installed()
        cls._get_information_from_remote()

        cls.INFORMATION_MANAGER.set(identifier, value)

        cls.__save_current_configuration_as_file()

    @exported_functionality
    @classmethod
    @deploy
    def test(
        cls: typing.Type["BaseSolution"],
        identifier: typing.Optional[str] = None,
    ) -> typing.List[TestResult]:
        """Run a test against a security solution.

        Args:
            identifier (str, optional): Key identifying the test. Defaults to
                None.

        Returns:
            typing.List[str]: List of results
        """
        cls._ensure_installed()
        cls._get_information_from_remote()

        result = cls.TESTS_MANAGER.test(identifier, only_check=True)

        return result

    @exported_functionality
    @classmethod
    @deploy
    def get_logs(
        cls: typing.Type["BaseSolution"],
        identifier: typing.Optional[str] = None,
    ) -> typing.Any:
        """Get logs from a target host.

        Args:
            identifier (str, optional): Key identifying the log source.
                Defaults to None.

        Returns:
            typing.Any: Logs
        """
        cls._ensure_installed()

        return cls.LOGS_MANAGER.get_content(identifier)

    @exported_functionality
    @classmethod
    @deploy
    def update(cls: typing.Type["BaseSolution"]) -> None:
        """Update the security solution."""
        cls._ensure_installed()
        cls._get_information_from_remote()

        cls._update()

    @exported_functionality
    @classmethod
    @deploy
    def uninstall(cls: typing.Type["BaseSolution"]) -> None:
        """Uninstall a security solution."""
        cls._ensure_installed()
        cls._get_information_from_remote()

        cls._uninstall()

    @exported_functionality
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
        cls._ensure_installed()
        cls._get_information_from_remote()

        cls.ACTIONS_MANAGER.execute(identifier, args)
