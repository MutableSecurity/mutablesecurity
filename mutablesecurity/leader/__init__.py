"""Package for managing connection with target hosts."""
from mutablesecurity.leader.connections import (
    Connection,
    ConnectionFactory,
    get_connection_for_host,
)
from mutablesecurity.leader.leader import Leader
