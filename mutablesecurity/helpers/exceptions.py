"""Module defining exception."""

import typing


class MutableSecurityException(Exception):
    """Class defining a generic MutableSecurity exception."""

    EXCEPTIONS_SUFFIX = "Exception"

    def __init_subclass__(
        cls: typing.Type["MutableSecurityException"],
    ) -> None:
        """Verify if the child name has a standard suffix.

        Raises:
            MutableSecurityException: The name does not ends with the standard
                suffix.
        """
        super().__init_subclass__()

        if not cls.__name__.endswith(cls.EXCEPTIONS_SUFFIX):
            raise MutableSecurityException(
                message=(
                    "The exception name needs to end with the suffix"
                    f' "{cls.EXCEPTIONS_SUFFIX}".'
                )
            )

    def __init__(self, message: str = None) -> None:
        """Initialize the MutableSecurityException instance.

        The message is implicitly taken from class' docstring.

        Args:
            message (str): Alternative way to specify the message
        """
        if self.__doc__ and self.__doc__ != MutableSecurityException.__doc__:
            message = self.__doc__
        elif message is None:
            return

        message = message.replace("\n", "")
        super().__init__(message)


class StoppedMutableSecurityException(MutableSecurityException):
    """MutableSecurity has been stopped."""


class UnexpectedBehaviorException(MutableSecurityException):
    """The codebase behaves strangely."""


class MandatoryAspectLeftUnsetException(MutableSecurityException):
    """A mandatory aspect of the default configuration was left unset."""


class ParserException(MutableSecurityException):
    """The parsing process failed."""


class InvalidConnectionStringException(ParserException):
    """The provided connection string is invalid."""


class DataTypeException(MutableSecurityException):
    """The data type handling process failed."""


class EnumTypeNotSetException(DataTypeException):
    """The child type was not set in the information using enumerations."""


class InvalidDataValueToConvertException(DataTypeException):
    """The provided value is not a stringified version of the set type."""


class NoDataTypeWithAnnotationException(DataTypeException):
    """There is no data type with the provided annotation."""


class InvalidBooleanValueException(DataTypeException):
    """The value does not correspond to any boolean value."""


class PlainYAMLException(MutableSecurityException):
    """The plain YAML handling failed."""


class YAMLFileNotExistsException(PlainYAMLException):
    """The provided YAML file does not exists."""


class YAMLKeyMissingException(PlainYAMLException):
    """A required key is missing from the provided YAML file."""


class NotPlainDictionaryException(PlainYAMLException):
    """The dictionary is not a plain YAML representation."""


class LocalConfigException(MutableSecurityException):
    """An error occurred when processing the user-defined configuration."""


class NoKeyInLocalConfigException(LocalConfigException):
    """The accesses key was not found in the local configuration."""


class InvalidStructureOfLocalConfigException(LocalConfigException):
    """The structure of the local configuration file needs to be single-level.\
"""


class InvalidValueInLocalConfigException(LocalConfigException):
    """A key in the local configuration is invalid."""


class InvalidValueToSetInLocalConfigException(LocalConfigException):
    """The value to set in the local configuration is invalid."""


class FilesException(MutableSecurityException):
    """An error occurred when processing a file."""


class FileNotExistsException(FilesException):
    """The provided file does not exists."""


class ImproperPermissionsException(FilesException):
    """The permissions are not elevated enough(t) to manipulate the file."""


class GitHubException(MutableSecurityException):
    """An error occurred when communicating with GitHub API."""


class GitHubAPIException(GitHubException):
    """The result from GitHub API is not successful."""


class NoIdentifiedAssetException(GitHubException):
    """No release was matched using the provided identifier."""


class CLIException(MutableSecurityException):
    """An error occurred in the CLI module."""


class UnsupportedPythonVersionException(CLIException):
    """This version if Python is not supported."""


class BadArgumentException(CLIException):
    """MutableSecurity received a bad argument. Verify the help and re-run."""


class BadValueException(CLIException):
    """The value provided as a CLI is invalid."""


class HostsOrchestrationException(MutableSecurityException):
    """An error occurred in the module connecting to target hosts."""


class ConnectionExportMethodNotImplementedException(
    HostsOrchestrationException
):
    """The connection export method is not implemented."""


class InvalidConnectionDetailsException(HostsOrchestrationException):
    """The connections details are invalid."""


class InvalidConnectionStringsFileException(HostsOrchestrationException):
    """The provided connection strings file is invalid."""


class UnknownConnectionTypeException(HostsOrchestrationException):
    """The type of the connection could not be deduced."""


class FailedConnectionToHostsException(HostsOrchestrationException):
    """The connection to a remote host failed."""


class FailedExecutionException(HostsOrchestrationException):
    """An error occurred while executing the given operation."""


class MainModuleException(MutableSecurityException):
    """An error occurred in the main module."""


class SolutionsManagerException(MutableSecurityException):
    """An error occurred in the solutions manager module."""


class UnacceptedSolutionMaturityLevelsException(SolutionsManagerException):
    """The maturity of the solution is not accepted by your user profile."""


class SolutionNotPresentException(SolutionsManagerException):
    """The given solution is not present locally."""


class OperationNotImplementedException(SolutionsManagerException):
    """The operation is not implemented in the selected solution."""


class SolutionException(MutableSecurityException):
    """An error occurred inside the automation of a security solution."""


class InvalidMetaException(SolutionException):
    """The meta of the package containing the solution is invalid."""


class NoSolutionConfigurationFileException(SolutionException):
    """No local configuration file for the given solution was found. Maybe \
you should initialize it first."""


class RequirementsNotMetException(SolutionException):
    """The system requirements of the solution are not met."""


class FailedSolutionTestException(SolutionException):
    """One test executed against the installed solution failed."""


class SolutionObjectNotFoundException(SolutionException):
    """The selected object of the solution could not be found."""


class SolutionInformationNotFoundException(SolutionException):
    """The selected information does not exist in solution's context."""


class NonWritableInformationException(SolutionException):
    """The information is not writable."""


class SolutionTestNotFoundException(SolutionException):
    """The selected test does not exist in solution's context."""


class SolutionLogNotFoundException(SolutionException):
    """The selected log source does not exist in solution's context."""


class SolutionLogIdentifierNotSpecifiedException(SolutionException):
    """No identifier was provided for the log source to be retrieved."""


class SolutionActionNotFoundException(SolutionException):
    """The selected action does not exist in solution's context."""


class InvalidNumberOfActionArgumentsException(SolutionException):
    """The number of arguments provided for executing the action is invalid."""


class ActionArgumentNotPresentException(SolutionException):
    """A mandatory argument of the action was not provided."""


class InvalidValueForActionArgumentException(SolutionException):
    """One of the provided arguments could not be converted to its real type.\
"""


class InvalidInformationValueException(SolutionException):
    """The set value for the information is invalid."""


class SolutionAlreadyInstalledException(SolutionException):
    """The solution is already installed."""


class SolutionNotInstalledException(SolutionException):
    """The solution is not installed at the moment."""
