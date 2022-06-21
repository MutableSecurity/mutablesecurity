"""Package for managing connection with target hosts."""
from .connections import (
    KeySSHRemoteConnection,
    LocalPasswordConnection,
    PasswordSSHRemoteConnection,
)
from .leader import Leader
