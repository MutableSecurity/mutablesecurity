from enum import Enum

from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import server

from .. import AbstractSolution
from ..facts import DefaultInterface


# The script prologue can contain various enumerations and facts that are used
# in the management of the solution.
class State(Enum):
    ENABLED = True
    DISABLED = False


class UserCount(FactBase):
    command = "cat /etc/passwd | wc -l"

    def process(self, output):
        return int(output[0])


# The class containing the functionality to manage the solution
class Dummy(AbstractSolution):
    # Member for storing the configuration as known by MutableSecurity, that
    # needs to be synchronized periodically (via get_configuration calls) with
    # the one from the machine
    _configuration = {
        "state": State.DISABLED,
    }

    # Member for metadata of the solution: full name, description, references to
    # webpages (homepages, documentation, forums), the description of the
    # configuration (with a type and a help message describing the usage of the
    # member of the configuration) and messages to be printed on (un)successful
    # executions of operations
    meta = {
        "full_name": "Dummy Module",
        "description": "This is a dummy module.",
        "references": ["https://dummy.io"],
        "configuration": {"state": {"type": State, "help": "State of the solution"}},
        "messages": {
            "INSTALL": (
                "Message to be printed when the installation is successfully.",
                "Message to be printed when the installation is unsuccessfully.",
            ),
            "UNINSTALL": (
                "Message to be printed when the uninstallation is successfully.",
                "Message to be printed when the uninstallation is unsuccessfully.",
            ),
            "TEST": (
                "Message to be printed when the testing is successfully.",
                "Message to be printed when the testing is unsuccessfully.",
            ),
            "GET_STATS": (
                "Message to be printed when the stat retrieval is successfully.",
                "Message to be printed when the stat retrieval is unsuccessfully.",
            ),
            "GET_CONFIGURATION": (
                "Message to be printed when the configuration retrieval is successfully.",
                "Message to be printed when the configuration retrieval is unsuccessfully.",
            ),
            "SET_CONFIGURATION": (
                "Message to be printed when the configuration setting is successfully.",
                "Message to be printed when the configuration setting is unsuccessfully.",
            ),
        },
    }

    # Member for storing the status of the last executed operation. True
    # indicates a success.
    result = None

    def _verify_new_configuration(aspect=None, value=None):
        # Steps to verify the configuration. This is an example of working with
        # enumerations.
        if aspect != "state" or State[value] is None:
            # Return a boolean indicating if the configuration requested to be
            # set is valid.
            return False

        return True

    @deploy
    def get_configuration(state, host):
        # Steps to get the configuration
        pass

        # Set the result as a boolean indicating the status of the operation
        Suricata.result = True

    @deploy
    def set_configuration(state, host, aspect=None, value=None):
        # Ensure the configuration is synced.
        Suricata.get_configuration(state=state, host=host)

        # Steps to set the configuration. The _put_configuration method needs to
        # be called to ensure the synchronization of the configurations.
        pass

        # Set the result as a boolean indicating the status of the operation
        Suricata.result = True

    @deploy
    def _put_configuration(state, host):
        # Steps to set the configuration
        pass

        # Set the result as a boolean indicating the status of the operation
        Suricata.result = True

    @deploy
    def install(state, host):
        # Steps to install the solution
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Creates a dummy file",
            commands=["touch /tmp/dummy.txt"],
        )
        pass

        # Set the result as a boolean indicating the status of the operation
        Suricata.result = True

    @deploy
    def update(state, host):
        # Steps to update the solution
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Updates a dummy file",
            commands=["touch /tmp/dummy.txt"],
        )
        pass

        # Set the result as a boolean indicating the status of the operation
        Suricata.result = True

    @deploy
    def test(state, host):
        # Ensure the configuration is synced.
        Suricata.get_configuration(state=state, host=host)

        # Steps to verify if the solution is well functioning
        pass

        # Set the result as a boolean indicating the status of the operation
        Suricata.result = True

    @deploy
    def get_stats(state, host):
        # Ensure the configuration is synced.
        Suricata.get_configuration(state=state, host=host)

        # Steps to get the solution's stats
        pass

        # Set the result as a boolean indicating the status of the operation.
        # This is an example of working with facts.
        Suricata.result = {"user": host.get_fact(UserCount)}

    @deploy
    def get_logs(state, host):
        # Ensure the configuration is synced.
        Suricata.get_configuration(state=state, host=host)

        # Steps to get the solution's logs
        pass

        # Set the result as a boolean indicating the status of the operation.
        Suricata.result = True

    @deploy
    def uninstall(state, host):
        # Ensure the configuration is synced.
        Suricata.get_configuration(state=state, host=host)

        # Steps to uninstall the solution
        pass

        # Set the result as a boolean indicating the status of the operation
        Suricata.result = True
