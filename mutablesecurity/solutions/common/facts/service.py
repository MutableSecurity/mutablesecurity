"""Module with common facts for services."""

import typing

from pyinfra.api import FactBase


class ActiveService(FactBase):
    """Fact for checking if a service is active."""

    def command(self, service_name: str) -> str:
        return f"systemctl is-active {service_name} || true"

    @staticmethod
    def process(
        output: typing.List[str],
    ) -> bool:
        return output[0] == "active"
