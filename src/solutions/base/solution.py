"""Module modeling the interface and common functionality for solutions."""

import os
import typing
from abc import ABC, abstractmethod
from enum import Enum

from pyinfra.api import Host, State
from pyinfra.api.deploy import deploy

from src.helpers.exceptions import (
    FailedSolutionTestException,
    InstallRequiredInformationNotSetException,
    InvalidInformationValueException,
    InvalidMetaException,
    MutableSecurityException,
    RequirementsNotMetException,
    SolutionActionNotFoundException,
    SolutionInformationNotFoundException,
    SolutionTestNotFoundException,
    YAMLKeyMissingException,
)
from src.helpers.plain_yaml import dump_to_file, load_from_file
from src.solutions.base.action import BaseAction
from src.solutions.base.information import (
    BaseInformation,
    InformationProperties,
)
from src.solutions.base.log import BaseLog
from src.solutions.base.requirement import BaseRequirement
from src.solutions.base.test import BaseTest


def exported_functionality(function: typing.Callable) -> typing.Callable:
    """Decorate by catching and reraising MutableSecurityException exceptions.

    It is useful for not repeating the same try-except logic in each function.

    Args:
        function (typing.Callable): Function to decorate

    Returns:
        typing.Callable: Decorator
    """

    def inner(*args: tuple, **kwargs: dict) -> None:
        """Catch MutableSecurityException exceptions.

        Args:
            args (tuple): Dectorated function positional arguments
            kwargs (dict): Decorated function keywork arguments

        Raises:
            MutableSecurityException: [description]
        """
        try:
            function(*args, **kwargs)
        except MutableSecurityException as exception:
            raise exception

    return inner


class BaseSolution(ABC):
    """Abstract class wrapping a security solution."""

    identifier: str
    config_filename: str
    full_name: str
    description: str
    references: typing.List[str]
    requirements: typing.Dict[str, BaseRequirement]
    information: typing.Dict[str, BaseInformation]
    tests: typing.Dict[str, BaseTest]
    logs: typing.Dict[str, BaseLog]
    actions: typing.Dict[str, BaseAction]

    class MetaKeys(Enum):
        """Class containing the mandatory key of a meta YAML file."""

        FULL_NAME = "full_name"
        DESCRIPTION = "description"
        REFERENCES = "references"

    # By now, disable the unused arguments warnings as they are required for
    # the interface with pyinfra.
    # pylint: disable=unused-argument

    def __init__(self, hostname: str) -> None:
        """Initialize the object.

        Args:
            hostname (str): Name of the host on which the solution is managed
        """
        self.__load_meta()

        self.identifier = self.__class__.__module__
        self.config_filename = f"{hostname}_{self.identifier}.yaml"

    def __load_meta(self) -> None:
        """Load the meta YAML file containing the solution details.

        Raises:
            InvalidMetaException: Invalid meta YAML file
        """
        # Load the meta YAML file
        meta_filename = os.path.join(
            ".".join(__name__.split(".")[:-1]), "meta.yaml"
        )
        mandatory_keys = [key.value for key in self.MetaKeys]
        try:
            meta = load_from_file(meta_filename, mandatory_keys)
        except YAMLKeyMissingException as exception:
            raise InvalidMetaException() from exception

        # Save the values into the class' members
        self.full_name = meta[self.MetaKeys.FULL_NAME.value]
        self.description = meta[self.MetaKeys.DESCRIPTION.value]
        self.references = meta[self.MetaKeys.REFERENCES.value]

    def __get_information_as_dict(
        self, filter_property: typing.Optional[InformationProperties] = None
    ) -> dict:
        """Get the (filtered) information as a dictionary.

        Args:
            filter_property (InformationProperties, optional): Mandatory
                properties for the information returned. Defaults to None.

        Returns:
            dict: Resulted dictionary
        """
        result = {}
        for key, info in self.information.items():
            if filter_property in info.properties:
                result[key] = info.actual_value

        return result

    def __save_current_configuration_as_file(self) -> None:
        """Save the current configuration as a file."""
        configuration = self.__get_information_as_dict(
            InformationProperties.CONFIGURATION
        )
        dump_to_file(configuration, self.config_filename)

    @deploy
    def __set_default_information(self) -> None:
        """Set the default values to configuration."""
        for info in self.information.values():
            info.actual_value = info.default_value  # type: ignore

    @deploy
    def __check_required_information_for_install(self) -> bool:
        """Check if all the information required for installation is present.

        Returns:
            bool: Boolean indicating if the required information is present
        """
        for info in self.information.values():
            if (
                InformationProperties.NEEDED_AT_INSTALL in info.properties
                and info.actual_value is None
            ):
                return False

        return True

    @deploy
    def __check_requirements(self, state: State, host: Host) -> bool:
        """Check the system requirements for the solution to be installed.

        Args:
            state (State): State
            host (Host): Host

        Returns:
            bool: Boolean indicating if the system is compatible
        """
        for requirement in self.requirements.values():
            if not host.get_fact(requirement.fact):
                return False

        return True

    @deploy
    def _get_information(
        self,
        state: State,
        host: Host,
        identifier: typing.Optional[str] = None,
    ) -> typing.Any:
        """Get a specific information or all of them.

        Args:
            state (State): State
            host (Host): Host
            identifier (str, optional): Information identifier. Defaults to
                None in case all the information will be retrieved.

        Raises:
            SolutionInformationNotFoundException: [description]

        Returns:
            typing.Any: Information value
        """
        if identifier:
            try:
                info: BaseInformation = getattr(self.information, identifier)
            except KeyError as exception:
                raise SolutionInformationNotFoundException() from exception

            info.actual_value = host.get_fact(info.getter)  # type: ignore

            return_value = info.actual_value
        else:
            info_list = list(self.information.values())
            for info in info_list:
                info.actual_value = host.get_fact(info.getter)  # type: ignore

            return_value = self.__get_information_as_dict()

        self.__save_current_configuration_as_file()

        return return_value

    @deploy
    def _set_information(
        self, state: State, host: Host, identifier: str, value: typing.Any
    ) -> None:
        """Set an information value.

        Args:
            state (State): State
            host (Host): Host
            identifier (str): Information identifier
            value (typing.Any): New value

        Raises:
            SolutionInformationNotFoundException: The information identified
                by the provided key was not found.
        """
        try:
            info = getattr(self.information, identifier)
        except KeyError as exception:
            raise SolutionInformationNotFoundException() from exception

        info.setter(value)
        info.actual_value = value

        self.__save_current_configuration_as_file()

    def _check_information_value(
        self, identifier: str, value: typing.Any
    ) -> bool:
        """Validate a value for an information.

        Args:
            identifier (str): Information identifier
            value (typing.Any): Value to be set

        Raises:
            SolutionInformationNotFoundException: Information not found

        Returns:
            bool: Boolean indicating if the value is valid
        """
        try:
            information = getattr(self.information, identifier)
        except KeyError as exception:
            raise SolutionInformationNotFoundException() from exception

        return information.validate_value(value)

    @deploy
    def _make_test(
        self,
        state: State,
        host: Host,
        identifier: typing.Optional[str] = None,
    ) -> None:
        """Make a test or all the testsuite.

        Args:
            state (State): State
            host (Host): Host
            identifier (typing.Optional[str, optional): Test identifier.
                Defaults to None if all the testsuite is executed.

        Raises:
            SolutionTestNotFoundException: Invalid test identifier
            FailedSolutionTestException: A test failed.
        """
        if identifier:
            try:
                test: BaseTest = getattr(self.tests, identifier)
            except KeyError as exception:
                raise SolutionTestNotFoundException() from exception

            tests_list = [test]
        else:
            tests_list = list(self.tests.values())

        for test in tests_list:
            if not host.get_fact(test.fact):
                raise FailedSolutionTestException()

    def represent_information_as_matrix(
        self,
    ) -> typing.List[typing.List[str]]:
        """Represent the information as a matrix.

        Returns:
            typing.List[typing.List[str]]: Matrix with details about the
                solution's information.
        """
        result = [
            [
                "Identifier",
                "Description",
                "Type",
                "Properties",
                "Default Value",
                "Actual Value",
            ]
        ]
        for key, info in self.information.items():
            properties = ", ".join([prop.name for prop in info.properties])

            result.append(
                [
                    key,
                    info.description,
                    info.info_type.name,
                    properties,
                    str(info.default_value),
                    str(info.actual_value),
                ]
            )

        return result

    def represent_log_sources_as_matrix(self) -> typing.List[typing.List[str]]:
        """Represent the log sources as a matrix.

        Returns:
            typing.List[typing.List[str]]: Matrix with information about log
                sources
        """
        result = [["Identifier", "Description"]]

        for key, log in self.logs.items():
            result.append([key, log.description])

        return result

    @abstractmethod
    @deploy
    def _install(self, state: State, host: Host) -> None:
        """Install the solution.

        Args:
            state (State): State
            host (Host): Host
        """

    @abstractmethod
    @deploy
    def _ensure_installed(self, state: State, host: Host) -> None:
        """Ensure that the solution is installed.

        Mandatory executed when performing actions against an already-installed
        solution.

        Args:
            state (State): State
            host (Host): Host
        """

    @abstractmethod
    @deploy
    def _uninstall(self, state: State, host: Host) -> None:
        """Uninstall the already-installed solution.

        Args:
            state (State): State
            host (Host): Host
        """

    @abstractmethod
    @deploy
    def _update(self, state: State, host: Host) -> None:
        """Update the already-installed solution.

        Args:
            state (State): State
            host (Host): Host
        """

    @exported_functionality
    @deploy
    def init(self) -> None:
        """Initialize the security solution lifecycle."""
        self.__set_default_information()
        self.__save_current_configuration_as_file()

    @exported_functionality
    @deploy
    def install(self, state: State, host: Host) -> None:
        """Install the security solution.

        Args:
            state (State): State
            host (Host): Host

        Raises:
            InstallRequiredInformationNotSetException: The information required
                for installation is no set.
            RequirementsNotMetException: The system's requirements are not met.
        """
        if not self.__check_required_information_for_install():
            raise InstallRequiredInformationNotSetException()
        if not self.__check_requirements(state, host):
            raise RequirementsNotMetException()
        self._install(state, host)

    @exported_functionality
    @deploy
    def get_information(
        self, state: State, host: Host, identifier: typing.Optional[str] = None
    ) -> typing.Any:
        """Get an information from a target host.

        Args:
            state (State): State
            host (Host): Host
            identifier (str, optional): Key identifying the information.
                Defaults to None.

        Returns:
            typing.Any: [description]
        """
        self._ensure_installed(state, host)

        return self._get_information(state, host, identifier)

    @exported_functionality
    @deploy
    def set_information(
        self, state: State, host: Host, identifier: str, value: typing.Any
    ) -> None:
        """Set an information to a target host.

        Args:
            state (State): State
            host (Host): Host
            identifier (str):  Key identifying the information
            value (typing.Any): New value of the information

        Raises:
            InvalidInformationValueException: The given value is invalid.
        """
        self._ensure_installed(state, host)
        self._get_information(state, host)

        if self._check_information_value(identifier, value):
            self._set_information(state, host, identifier, value)
        else:
            raise InvalidInformationValueException()

    @exported_functionality
    @deploy
    def test(
        self, state: State, host: Host, identifier: typing.Optional[str] = None
    ) -> typing.List[str]:
        """Run a test against a security solution.

        Args:
            state (State): State
            host (Host): Host
            identifier (str, optional): Key identifying the test. Defaults to
                None.

        Returns:
            typing.List[str]: [description]
        """
        self._ensure_installed(state, host)
        self._get_information(state, host)

        return self._make_test(state, host, identifier)

    @exported_functionality
    @deploy
    def update(self, state: State, host: Host) -> None:
        """Update the security solution.

        Args:
            state (State): State
            host (Host): Host
        """
        self._ensure_installed(state, host)
        self._get_information(state, host)

        self._update(state, host)

    @exported_functionality
    @deploy
    def uninstall(self, state: State, host: Host) -> None:
        """Uninstall a security solution.

        Args:
            state (State): State
            host (Host): Host
        """
        self._ensure_installed(state, host)
        self._get_information(state, host)

        self._uninstall(state, host)

    @exported_functionality
    @deploy
    def exec(
        self,
        state: State,
        host: Host,
        identifier: str,
        args: typing.Optional[dict] = None,
    ) -> None:
        """Delegate the security solution to perform a specific action.

        Args:
            state (State): State
            host (Host): Description
            identifier (str): Key identifying the action
            args (dict, optional): Dictionary containing the arguments of the
                action. Defaults to None.

        Raises:
            SolutionActionNotFoundException: The given identifier is invalid.
        """
        self._ensure_installed(state, host)
        self._get_information(state, host)

        try:
            action = getattr(self.actions, identifier)
        except KeyError as exception:
            raise SolutionActionNotFoundException() from exception

        action.act(**args)
