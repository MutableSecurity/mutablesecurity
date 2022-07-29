"""Package dealing with logging information.

The logged messages are sent to syslog.

On Linux, the messages can be found with the command below:
    tail -f /var/log/syslog | grep mutablesecurity
"""

import logging

from mutablesecurity.logger.logger import Logger


def get_logger() -> logging.Logger:
    """Get the default logger.

    Returns:
        logging.Logger: Logger
    """
    return Logger().native_logger
