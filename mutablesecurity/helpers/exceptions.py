"""Module defining exception."""


class MutableSecurityException(Exception):
    """Class defining a generic MutableSecurity exception."""

    def __init__(self) -> None:
        """Initialize the MutableSecurityException instance."""
        super().__init__(self.__doc__)


class MandatoryAspectLeftUnsetException(MutableSecurityException):
    """A mandatory aspect of the default configuration was left unset."""


class SameSetConfigurationValue(MutableSecurityException):
    """The value set in the configuration is the same with the old one."""


class ParserException(MutableSecurityException):
    """The parsing process failed."""


class InvalidConnectionStringException(ParserException):
    """The provided connection string is invalid."""


class PlainYAMLException(MutableSecurityException):
    """The plain YAML handling failed."""


class YAMLFileNotExistsException(PlainYAMLException):
    """The provided YAML file does not exists."""


class YAMLKeyMissingException(PlainYAMLException):
    """A required key is missing from the provided YAML file."""


class NotPlainDictionaryException(PlainYAMLException):
    """The dictionary is not a plain YAML representation."""


class FilesException(MutableSecurityException):
    """An error occurred when processing a file."""


class FileNotExists(FilesException):
    """The provided file does not exists."""


class ImproperPermissionsException(FilesException):
    """The permissions are not elevated enough(t) to manipulate the file."""


class GitHubException(MutableSecurityException):
    """An error occurred when communicating with GitHub API."""


class GitHubAPIError(GitHubException):
    """The result from GitHub API is not successful."""


class NoIdentifiedAssetException(GitHubException):
    """No release was matched using the provided identifier."""


class CLIException(MutableSecurityException):
    """An error occurred in the CLI module."""


class UnsupportedPythonVersion(CLIException):
    """This version if Python is not supported."""


class HostsOrchestrationException(MutableSecurityException):
    """An error occurred in the module connecting to target hosts."""


class ConnectionExportMethodNotImplemented(HostsOrchestrationException):
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


class SolutionNotPresentException(SolutionsManagerException):
    """The given solution is not present locally."""


class OperationNotImplementedException(SolutionsManagerException):
    """The operation is not implemented in the selected solution."""


class SolutionException(MutableSecurityException):
    """An error occurred inside the automation of a security solution."""


class InvalidMetaException(SolutionException):
    """The meta of the package containing the solution is invalid."""


class RequirementsNotMetException(SolutionException):
    """The system requirements of the solution are not met."""


class FailedSolutionTestException(SolutionException):
    """One test executed against the installed solution failed."""


class SolutionObjectNotFoundException(SolutionException):
    """The selected object of the solution could not be found."""


class SolutionInformationNotFoundException(SolutionException):
    """The selected information does not exist in solution's context."""


class EnumTypeNotSetException(SolutionException):
    """The child type was not set in the information using enumerations."""


class InvalidInformationValueToConvert(SolutionException):
    """The provided value is not a stringified version of the set type."""


class NonWritableInformationException(SolutionException):
    """The information is not writable."""


class SolutionTestNotFoundException(SolutionException):
    """The selected test does not exist in solution's context."""


class SolutionLogNotFoundException(SolutionException):
    """The selected log source does not exist in solution's context."""


class SolutionActionNotFoundException(SolutionException):
    """The selected action does not exist in solution's context."""


class InvalidInformationValueException(SolutionException):
    """The set value for the information is invalid."""


class SolutionAlreadyInstalledException(SolutionException):
    """The solution is already installed."""


class SolutionNotInstalledException(SolutionException):
    """The solution is not installed at the moment."""
