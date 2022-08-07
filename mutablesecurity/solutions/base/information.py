"""Module defining an abstract information."""

import typing
from enum import Enum

from pyinfra import host
from pyinfra.api import FactBase

from mutablesecurity.helpers.data_type import DataType
from mutablesecurity.helpers.exceptions import (
    InvalidInformationValueException,
    MandatoryAspectLeftUnsetException,
    NonWritableInformationException,
    SolutionInformationNotFoundException,
    SolutionObjectNotFoundException,
)
from mutablesecurity.helpers.type_hints import PyinfraOperation
from mutablesecurity.solutions.base.object import BaseManager, BaseObject
from mutablesecurity.solutions.base.result import (
    BaseConcreteResultObjects,
    BaseGenericObjectsDescriptions,
    KeysDescriptions,
)


class InformationProperties(Enum):
    """Enumeration for possible properties of an information."""

    # Base for information's type
    __TYPE_BASE = 1

    # Description:  Information required to make a solution operable
    # Example:      Quarantine folder for an antivirus
    CONFIGURATION = __TYPE_BASE + 1

    # Description:  Read-only information that is exposed by the solution,
    #               describing its functioning
    # Requirements: READ_ONLY
    # Example:      Number of blocked malware by an antivirus
    METRIC = __TYPE_BASE + 2

    # Base for configuration's optionality
    __CONFIGURATION_OPTIONALITY_BASE = 10

    # Description:  Required to be set during the whole functioning of the
    #               solution
    # Requirements: CONFIGURATION
    # Example:      Email where an XDR sends its critical alerts
    MANDATORY = __CONFIGURATION_OPTIONALITY_BASE + 1

    # Description:  Optional to set
    # Requirements: CONFIGURATION
    # Example:      Additional threat hunting sources for an IDS
    OPTIONAL = __CONFIGURATION_OPTIONALITY_BASE + 2

    # Base for configuration's generation mechanism
    _CONFIGURATION_VALUE_BASE = 20

    # Description:  With a default (recommended) value. If it is not specified
    #               in the local configuration file of the solution, this value
    #               is used.
    # Requirements: CONFIGURATION
    # Example:      Default 443 port for a HTTPS web server
    WITH_DEFAULT_VALUE = _CONFIGURATION_VALUE_BASE + 1

    # Description:  With a value that is not deductible from querying the host.
    #               The only way  MutableSecurity finds its value is by
    #               inspecting the local configuration file of the solution.
    # Requirements: CONFIGURATION, MANDATORY
    # Example:      Port on which a web server that needs to be protected
    #               listens
    NON_DEDUCTIBLE = _CONFIGURATION_VALUE_BASE + 2

    # Description:  With a value auto-generated before installation
    # Requirements: CONFIGURATION, READ_ONLY
    # Example:      A random password, generated after installing Wazuh
    AUTO_GENERATED_BEFORE_INSTALL = _CONFIGURATION_VALUE_BASE + 3

    # Description:  With a value auto-generated after installation
    # Requirements: CONFIGURATION, READ_ONLY
    # Example:      A random password, generated after installing Wazuh
    AUTO_GENERATED_AFTER_INSTALL = _CONFIGURATION_VALUE_BASE + 4

    # Base for writability
    _WRITABILITY_BASE = 30

    # Description:  The value could not be written, only read
    # Example:      Any metric
    READ_ONLY = _WRITABILITY_BASE + 1

    # Description:  The value could be written and read
    # Example:      A server on which an agent reports
    WRITABLE = _WRITABILITY_BASE + 2

    def __str__(self) -> str:
        """Stringify the object.

        Returns:
            str: String representation
        """
        return self.name

    def __repr__(self) -> str:
        """Represent the object.

        Returns:
            str: String representation
        """
        return self.name


class BaseInformation(BaseObject):
    """Abstract class modeling an information related to the solution.

    As the information is the only part of a solution that is stateful (can be
    useful for the effective operations), the actual value is stored inside the
    host data.
    """

    DEFAULT_VALUE: typing.Any
    INFO_TYPE: typing.Type[DataType]
    PROPERTIES: typing.List[InformationProperties]
    GETTER: FactBase
    GETTER_ARGS: tuple
    SETTER: typing.Optional[PyinfraOperation]

    @staticmethod
    def __ensure_exists_on_host() -> None:
        if "mutablesecurity" not in host.host_data:
            host.host_data["mutablesecurity"] = {}

    @classmethod
    def get(cls: typing.Type["BaseInformation"]) -> typing.Any:
        """Get the actual value of the property, as stored in the host data.

        Returns:
            typing.Any: Value
        """
        cls.__ensure_exists_on_host()

        try:
            return host.host_data["mutablesecurity"][cls.IDENTIFIER]
        except KeyError:
            return None

    @classmethod
    def set_actual_value(
        cls: typing.Type["BaseInformation"], value: typing.Any
    ) -> None:
        """Set a value as the actual one, in the host data.

        Args:
            value (typing.Any): Value to set
        """
        cls.__ensure_exists_on_host()

        host.host_data["mutablesecurity"][cls.IDENTIFIER] = value

    @staticmethod
    def validate_value(
        value: typing.Any,  # pylint: disable=unused-argument
    ) -> bool:
        """Validate if the information's value is valid.

        Args:
            value (typing.Any): Value of the information

        Returns:
            bool: Boolean indicating if the information is valid
        """
        return True


class InformationManager(BaseManager):
    """Class managing the information of a solution."""

    objects_descriptions: BaseGenericObjectsDescriptions
    KEYS_DESCRIPTIONS: KeysDescriptions = {
        "identifier": "Identifier",
        "description": "Description",
        "type": "Type",
        "properties": "Properties",
        "default_value": "Default Value",
    }

    def __init__(self, information: typing.Sequence[BaseInformation]) -> None:
        """Initialize the instance.

        Args:
            information (typing.Sequence[BaseInformation]): List of information
                to be added
        """
        super().__init__(information)

        self.objects_descriptions = [
            {
                "identifier": info.IDENTIFIER,
                "description": info.DESCRIPTION,
                "type": info.INFO_TYPE,
                "properties": info.PROPERTIES,
                "default_value": info.DEFAULT_VALUE,
            }
            for info in information
        ]

    def get(
        self, identifier: typing.Optional[str] = None
    ) -> BaseConcreteResultObjects:
        """Get a specific information or all of them.

        Args:
            identifier (str): Information identifier. Defaults to None in case
                all the information will be retrieved.

        Raises:
            SolutionInformationNotFoundException: The identifier does not
                correspond to any information.

        Returns:
            BaseConcreteResultObjects: Result containing the requested
                information
        """
        # Get the information list
        if identifier:
            try:
                info: BaseInformation = self.get_object_by_identifier(
                    identifier
                )  # type: ignore[assignment]
            except SolutionObjectNotFoundException as exception:
                raise SolutionInformationNotFoundException() from exception

            info_list = [info]

        else:
            info_list = list(self.objects.values())  # type: ignore[arg-type]

        # Get the concrete values
        for info in info_list:
            if InformationProperties.NON_DEDUCTIBLE not in info.PROPERTIES:
                args = getattr(info, "GETTER_ARGS", ())
                info.set_actual_value(host.get_fact(info.GETTER, *args))

        return self.represent_as_dict(identifier=identifier)

    def set(
        self,
        identifier: str,
        value: typing.Any,
        only_local: bool = False,
    ) -> None:
        """Set an information value.

        Args:
            identifier (str): Information identifier
            value (typing.Any): New value
            only_local (bool): Boolean indicating if the changes are
                local-only. Defaults to False, indicating the fact that the
                remote host is involved in the process.

        Raises:
            SolutionInformationNotFoundException: The information identified
                by the provided key was not found.
            InvalidInformationValueException: The new value is incorrect.
            NonWritableInformationException: The information is not writable.
        """
        try:
            info: BaseInformation = self.get_object_by_identifier(
                identifier
            )  # type: ignore[assignment]
        except SolutionObjectNotFoundException as exception:
            raise SolutionInformationNotFoundException() from exception

        if InformationProperties.CONFIGURATION not in info.PROPERTIES:
            raise NonWritableInformationException()

        old_value = info.get()
        new_value = value

        if not info.validate_value(new_value):
            new_value = info.INFO_TYPE.convert_string(value)
            if not info.validate_value(new_value):
                raise InvalidInformationValueException()

        info.set_actual_value(new_value)

        if not only_local and info.SETTER:
            info.SETTER(old_value, new_value)

    def set_default_values_locally(self) -> None:
        """Set the default values in the local configuration."""
        for raw_info in self.objects.values():
            info: BaseInformation = raw_info  # type: ignore[assignment]

            if InformationProperties.WITH_DEFAULT_VALUE in info.PROPERTIES:
                info.set_actual_value(info.DEFAULT_VALUE)

            if (
                InformationProperties.AUTO_GENERATED_BEFORE_INSTALL
                in info.PROPERTIES
            ):
                args = getattr(info, "GETTER_ARGS", ())
                info.set_actual_value(host.get_fact(info.GETTER, *args))

    def populate(self, export: dict, post_installation: bool = True) -> None:
        """Set all the local values from an export dictionary.

        Args:
            export (dict): Previously exported dictionary
            post_installation (bool): Boolean indicating if the installation
                was already done
        """
        # Populate from passed dictionary
        for key, value in export.items():
            self.set(key, value, only_local=True)

        # Get the auto-generated values
        for key, raw_info in self.objects.items():
            info: BaseInformation = raw_info  # type: ignore[assignment]

            if (
                InformationProperties.AUTO_GENERATED_BEFORE_INSTALL
                in info.PROPERTIES
                or (
                    post_installation
                    and InformationProperties.AUTO_GENERATED_BEFORE_INSTALL
                    in info.PROPERTIES
                )
            ):
                args = getattr(info, "GETTER_ARGS", ())
                value = host.get_fact(info.GETTER, *args)
                self.set(key, value, only_local=True)

        self.validate_all()

    def validate_all(
        self, filter_property: typing.Optional[InformationProperties] = None
    ) -> None:
        """Validate if the stored information is set accordingly as a whole.

        The value is not validated as an exception is already raised on setting
        methods.

        Args:
            filter_property (InformationProperties): Filter for information
                stored in the manager. Defaults to None.

        Raises:
            MandatoryAspectLeftUnsetException: One mandatory aspect is left
                unset.
        """
        for raw_info in self.objects.values():
            info: BaseInformation = raw_info  # type: ignore[assignment]

            if filter_property and filter_property not in info.PROPERTIES:
                continue

            if (
                InformationProperties.MANDATORY in info.PROPERTIES
                and info.get() is None
            ):
                raise MandatoryAspectLeftUnsetException()

    def represent_as_dict(
        self,
        identifier: str = None,
        filter_properties: typing.Optional[
            typing.List[InformationProperties]
        ] = None,
    ) -> BaseConcreteResultObjects:
        """Get the (filtered) information as a dictionary.

        Args:
            filter_properties (typing.List[InformationProperties]): Mandatory
                properties for the information returned. Defaults to None.
            identifier (str): Identifier of the single information to represent
                in the string. Defaults to None.

        Returns:
            BaseConcreteResultObjects: Resulted dictionary
        """
        result = {}
        for key, current_info in self.objects.items():
            info: BaseInformation = current_info  # type: ignore[assignment]

            if identifier and info.IDENTIFIER != identifier:
                continue

            if filter_properties and not set(filter_properties).issubset(
                info.PROPERTIES
            ):
                continue

            result[key] = info.get()

        return result
