"""Module defining a dummy security solution, for testing purposes."""

# pylint: disable=protected-access
# pylint: disable=missing-class-docstring
# pylint: disable=unused-argument
# pylint: disable=unexpected-keyword-arg

import typing

from pyinfra.api.deploy import deploy
from pyinfra.api.facts import FactBase
from pyinfra.operations.server import shell

from mutablesecurity.solutions.base import (
    BaseAction,
    BaseInformation,
    BaseLog,
    BaseSolution,
    BaseTest,
    InformationProperties,
    IntegerDataType,
    StringDataType,
    TestType,
)
from mutablesecurity.solutions.common.facts.os import CheckIfUbuntu

# Actions classes definitions


class AppendToFileAction(BaseAction):
    @staticmethod
    @deploy
    def append_to_file(content: str, number: int) -> None:
        shell(
            [f"echo '{content}' >> /tmp/dummy.{number}"],
            name="Creates a new file.",
        )

    IDENTIFIER = "append_to_file"
    DESCRIPTION = "Appends a text to a file."
    ACT = append_to_file


# Information classes definitions


class FileSizeInformation(BaseInformation):
    class GetFileSize(FactBase):
        command = "stat -c '%s' /tmp/dummy"

        @staticmethod
        def process(output: typing.List[str]) -> int:
            return int(output[0])

    IDENTIFIER = "file_size"
    DESCRIPTION = "File size"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = GetFileSize


class MachineIDInformation(BaseInformation):
    class GetMachineID(FactBase):
        command = "cat /etc/machine-id"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return output[0]

    IDENTIFIER = "machine_id"
    DESCRIPTION = "Machine ID"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = GetMachineID


class CurrentUserInformation(BaseInformation):
    class GetCurrentUser(FactBase):
        command = "whoami"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return output[0]

    @staticmethod
    @deploy
    def set_user(old_value: str, new_value: str) -> None:
        shell(["echo {old_username} {new_username}"])

    IDENTIFIER = "current_user"
    DESCRIPTION = "User under which the automation is ran"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = None
    GETTER = GetCurrentUser
    SETTER = set_user


# Logs classes definitions


class ContentLogs(BaseLog):
    class GetContent(FactBase):
        command = "cat /tmp/dummy"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return "".join(output)

    IDENTIFIER = "file_content"
    DESCRIPTION = "Gets the file content."
    FACT = GetContent


# Tests classes definitions


class UbuntuRequirement(BaseTest):
    IDENTIFIER = "ubuntu"
    DESCRIPTION = "Checks if the operating system is Ubuntu."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = CheckIfUbuntu


class FilePresenceTest(BaseTest):
    class CheckIfPresent(FactBase):
        command = "if [ -e /tmp/dummy ] ; then echo '1'; else echo '0' ; fi"

        @staticmethod
        def process(output: typing.List[str]) -> bool:
            return int(output[0]) == 1

    IDENTIFIER = "presence"
    DESCRIPTION = "Checks if a file is present."
    TEST_TYPE = TestType.PRESENCE
    FACT = CheckIfPresent


# Solution class definition


class Dummy(BaseSolution):
    INFORMATION = [
        FileSizeInformation,  # type: ignore[list-item]
        CurrentUserInformation,  # type: ignore[list-item]
        MachineIDInformation,  # type: ignore[list-item]
    ]
    TESTS = [
        UbuntuRequirement,  # type: ignore[list-item]
        FilePresenceTest,  # type: ignore[list-item]
    ]
    LOGS = [
        ContentLogs,  # type: ignore[list-item]
    ]
    ACTIONS = [
        AppendToFileAction,  # type: ignore[list-item]
    ]

    @staticmethod
    @deploy
    def _install() -> None:
        shell(["touch /tmp/dummy"])

    @staticmethod
    @deploy
    def _uninstall() -> None:
        shell(["rm /tmp/dummy"])

    @staticmethod
    @deploy
    def _update() -> None:
        shell(["touch /tmp/dummy"])
