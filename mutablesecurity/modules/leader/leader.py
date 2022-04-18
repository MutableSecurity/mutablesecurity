from pyinfra.api import Config, Inventory, State
from pyinfra.api.connect import connect_all


class Leader:
    @staticmethod
    def _make_inventory(hosts=(), **kwargs):
        return Inventory((hosts, {}), **kwargs)

    @staticmethod
    def connect_to_local(password):
        # Create the local connection with pyinfra
        inventory = Leader._make_inventory(hosts=("@local",))
        state = State(inventory, Config())
        connect_all(state)

        state.config.SUDO = True
        state.config.USE_SUDO_PASSWORD = password

        return state

    @staticmethod
    def connect_to_ssh_with_password(host, ssh_port, ssh_user, ssh_password):
        # Create the inventory with the specified host
        inventory = Leader._make_inventory(
            hosts=(
                (
                    host,
                    {
                        "ssh_port": ssh_port,
                        "ssh_user": ssh_user,
                        "ssh_password": ssh_password,
                        "allow_agent": False,
                        "look_for_keys": False,
                    },
                ),
            )
        )

        # Create the state with its callback
        state = State(inventory, Config())

        # Connect
        connect_all(state)

        return state
