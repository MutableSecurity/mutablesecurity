import logging

from rich.console import Console
from rich.logging import RichHandler


class Logger:
    def __init__(self, verbose):
        # Enable rich logging
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(
                    console=Console(file=open("/tmp/mutablesecurity.log", "w"))
                )
            ],
        )

        # Set the logging level according to the options
        if verbose:
            logging.getLogger("mutablesecurity").setLevel(logging.INFO)
        else:
            logging.getLogger("mutablesecurity").setLevel(logging.DEBUG)
