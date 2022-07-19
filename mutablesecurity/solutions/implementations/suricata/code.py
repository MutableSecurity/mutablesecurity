"""Module integrating Suricata."""

# pylint: disable=missing-class-docstring,unused-argument

from pyinfra.api.deploy import deploy

from mutablesecurity.solutions.base import BaseSolution


class Suricata(BaseSolution):
    INFORMATION = []  # type: ignore[list-item, var-annotated]
    TESTS = []  # type: ignore[list-item, var-annotated]
    LOGS = []  # type: ignore[list-item, var-annotated]
    ACTIONS = []  # type: ignore[list-item, var-annotated]

    @staticmethod
    @deploy
    def _install() -> None:
        pass

    @staticmethod
    @deploy
    def _uninstall() -> None:
        pass

    @staticmethod
    @deploy
    def _update() -> None:
        pass
