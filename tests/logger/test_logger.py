"""Module for testing the logger."""

import random
import string

from mutablesecurity.logger import get_logger


def test_log_password() -> None:
    """Test if the logger removes a password embedded in the log message."""
    random_password = "".join(
        random.choices(string.printable, k=32)  # noqa: S311
    )

    get_logger().error(
        "Executing with"
        f" {{'use_sudo_password': '{random_password}', sudo: True}}"
    )

    with open("/var/log/syslog", "r", encoding="utf-8") as syslog:
        for line in syslog.readlines():
            assert (
                random_password not in line
            ), "A non-redacted password was found in syslog."
