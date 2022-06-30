"""Module for testing the server connection functionality."""
from pyinfra.api.deploy import deploy
from pyinfra.operations import server

from src.leader import ConnectionFactory, Leader


@deploy
def say_hi() -> None:
    """Deployment to say hi."""
    server.shell("echo 'hi!'", _sudo=False)


def test_local_execution() -> None:
    """Test if an operation executes correctly with a local connection."""
    local_connection = ConnectionFactory().create_connection("password")

    leader = Leader()
    leader.attach_connection(local_connection)

    leader.connect()
    leader.run_operation(say_hi)
