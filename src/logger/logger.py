"""Module implementing a logger."""
import logging

from rich.console import Console
from rich.logging import RichHandler


class Logger:
    """Class modeling a logger."""

    def __init__(self, verbose: bool) -> None:
        """Initialize the object.

        Args:
            verbose (bool): Boolean indicating if the logging needs to be
                verbose
        """
        # Enable rich logging
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(
                    console=Console(
                        file=open(
                            "/tmp/mutablesecurity.log", "w", encoding="utf-8"
                        )
                    )
                )
            ],
        )

        # Set the logging level according to the option
        if verbose:
            logging.getLogger("mutablesecurity").setLevel(logging.INFO)
        else:
            logging.getLogger("mutablesecurity").setLevel(logging.DEBUG)
