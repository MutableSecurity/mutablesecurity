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


class InvalidConnectionStringsFileException(ParserException):
    """The file containing connection strings is invalid."""


class CLIException(MutableSecurityException):
    """An error occured in the CLI module."""


class UnsupportedPythonVersion(CLIException):
    """This version if Python is not supported."""
