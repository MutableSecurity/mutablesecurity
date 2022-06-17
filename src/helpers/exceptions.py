class MutableSecurityException(Exception):
    """Generic MutableSecurity exception"""

    def __init__(self) -> None:
        """Initializes the MutableSecurityException instance."""
        super().__init__(self.__doc__)


class MandatoryAspectLeftUnsetException(MutableSecurityException):
    """A mandatory aspect of the default configuration was left unset."""


class SameSetConfigurationValue(MutableSecurityException):
    """The value set in the configuration is the same with the old one."""
