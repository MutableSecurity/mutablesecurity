"""Module defining a dummy security solution, for testing purposes."""

# pylint: disable=missing-class-docstring,unused-argument

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
    IntegerInformationType,
    StringInformationType,
    TestType,
)


class AppendToFileAction(BaseAction):
    @staticmethod
    @deploy
    def append_to_file(content: str) -> None:
        shell([f"echo '{content}' >> /tmp/dummy"])

    IDENTIFIER = "append_to_file"
    DESCRIPTION = "Append a text to a file."
    ACT = append_to_file


class FileSizeInformation(BaseInformation):
    class GetFileSize(FactBase):
        command = "stat -c '%s' /tmp/dummy"

        @staticmethod
        def process(output: typing.List[str]) -> int:
            return int(output[0])

    IDENTIFIER = "file_size"
    DESCRIPTION = "Get the file size."
    INFO_TYPE = IntegerInformationType
    PROPERTIES = [InformationProperties.METRIC]
    DEFAULT_VALUE = None
    GETTER = GetFileSize


class CurrentUserInformation(BaseInformation):
    class GetCurrentUser(FactBase):
        command = "whoami"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return output[0]

    @staticmethod
    def set_user(username: str) -> None:
        shell(["echo {username}"])

    IDENTIFIER = "current_user"
    DESCRIPTION = "Get the user under which the automation is ran."
    INFO_TYPE = StringInformationType
    PROPERTIES = [InformationProperties.CONFIGURATION]
    DEFAULT_VALUE = None
    GETTER = GetCurrentUser
    SETTER = set_user

    @staticmethod
    def validate_value(value: typing.Any) -> bool:
        return isinstance(value, str)


class UbuntuRequirement(BaseTest):
    class CheckIfUbuntu(FactBase):
        command = "uname -a"

        @staticmethod
        def process(output: typing.List[str]) -> bool:
            return "ubuntu" in "".join(output).lower()

    IDENTIFIER = "ubuntu"
    DESCRIPTION = "Check if the operating system is Ubuntu."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = CheckIfUbuntu


class PresenceTest(BaseTest):
    class CheckIfPresent(FactBase):
        command = "if [ -e /tmp/dummy ] ; then echo '1'; else echo '0' ; fi"

        @staticmethod
        def process(output: typing.List[str]) -> bool:
            return int(output[0]) == 1

    IDENTIFIER = "presence"
    DESCRIPTION = "Check if a file is present."
    TEST_TYPE = TestType.PRESENCE
    FACT = CheckIfPresent


class ContentLogs(BaseLog):
    class GetContent(FactBase):
        command = "cat /tmp/dummy"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return "".join(output)

    IDENTIFIER = "file_content"
    DESCRIPTION = "Get the file content."
    FACT = GetContent


class Dummy(BaseSolution):
    INFORMATION = [FileSizeInformation, CurrentUserInformation]  # type: ignore
    TESTS = [UbuntuRequirement, PresenceTest]  # type: ignore
    LOGS = [ContentLogs]  # type: ignore
    ACTIONS = [AppendToFileAction]  # type: ignore

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
