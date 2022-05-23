from pyinfra.api import Config, Inventory, State
from pyinfra.api.connect import connect_all


class ConnectionDetails(dict):
    def __init__(self, hostname, port, username, key, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.key = key
        self.password = password


class Leader:
    @staticmethod
    def _make_inventory(hosts=(), **kwargs):
        return Inventory((hosts, {}), **kwargs)

    @staticmethod
    def connect_to_local(details):
        # Create the local connection with pyinfra
        inventory = Leader._make_inventory(hosts=("@local",))
        state = State(inventory, Config())
        connect_all(state)

        state.config.SUDO = True
        state.config.USE_SUDO_PASSWORD = details.password

        return state

    @staticmethod
    def _connect_to_ssh_with_params(details, additional_pyinfra_params):
        # Create the inventory with the specified host
        ssh_connection_details = {
            "ssh_port": details.port,
            "ssh_user": details.username,
            "allow_agent": False,
        }
        ssh_connection_details |= additional_pyinfra_params
        inventory = Leader._make_inventory(
            hosts=(
                (
                    details.hostname,
                    ssh_connection_details,
                ),
            )
        )

        # Create the state with its callback
        state = State(inventory, Config())

        # Connect
        connect_all(state)

        state.config.SUDO = True
        state.config.USE_SUDO_PASSWORD = details.password

        return state

    @staticmethod
    def connect_to_ssh_with_password(details):
        params = {
            "ssh_password": details.password,
            "look_for_keys": False,
        }

        return Leader._connect_to_ssh_with_params(details, params)

    @staticmethod
    def connect_to_ssh_with_key(details):
        params = {
            "ssh_key": details.key,
            "ssh_key_password": details.password,
        }

        return Leader._connect_to_ssh_with_params(details, params)
