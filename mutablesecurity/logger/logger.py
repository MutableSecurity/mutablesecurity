"""Module implementing a logger."""
import logging
import logging.handlers
import re
import typing

from pypattyrn.creational.singleton import Singleton


class Logger(metaclass=Singleton):
    """Class modeling a logger."""

    PASSWORD_REPLACEMENT_STRING = "REDACTED"  # noqa: S105
    native_logger: logging.Logger
    old_factory: typing.Any

    @staticmethod
    def remove_pyinfra_password(
        *args: tuple, **kwargs: typing.Any
    ) -> logging.LogRecord:
        """Remove the passwords embedded in logs by pyinfra.

        Args:
            args (tuple): Unused
            kwargs (typing.Any): Unused

        Returns:
            logging.LogRecord: Modified logs
        """
        record = Logger().old_factory(*args, **kwargs)
        record.msg = re.sub(
            r"'use_sudo_password': '.*', ",
            f"'use_sudo_password': '{Logger.PASSWORD_REPLACEMENT_STRING}', ",
            record.msg,
        )

        return record

    def __init__(self) -> None:
        """Initialize the object."""
        # Create a syslog handler and a logger
        handler = logging.handlers.SysLogHandler(address="/dev/log")
        logging.basicConfig(
            level=logging.INFO,
            format=(
                "mutablesecurity: %(process)d: %(pathname)s: %(lineno)d: "
                " %(levelname)s: %(message)s"
            ),
            datefmt="[%X]",
            handlers=[handler],
        )

        # Get the MutableSecurity logger
        self.native_logger = logging.getLogger()

        # Log a message
        logging.debug("The logger was initialized.")

        # Remove the embedded password
        self.old_factory = logging.getLogRecordFactory()
        logging.setLogRecordFactory(self.remove_pyinfra_password)

    def set_verbosity(self, verbose: bool) -> None:
        """Set the logger to be verbose.

        Args:
            verbose (bool): Boolean indicating if the logging is verbose
        """
        if verbose:
            self.native_logger.setLevel(logging.INFO)
        else:
            self.native_logger.setLevel(logging.DEBUG)
