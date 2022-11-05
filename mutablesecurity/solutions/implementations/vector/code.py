"""Module integrating vector."""

# pylint: disable=protected-access
# pylint: disable=missing-class-docstring
# pylint: disable=unused-argument
# pylint: disable=unexpected-keyword-arg

import os
import typing

from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, files, server

from mutablesecurity.helpers.data_type import (
    StringDataType,
    StringListDataType,
)
from mutablesecurity.solutions.base import (
    BaseAction,
    BaseInformation,
    BaseLog,
    BaseSolution,
    BaseTest,
    InformationProperties,
    LogFormat,
    TestType,
)
from mutablesecurity.solutions.common.facts.bash import PresentCommand
from mutablesecurity.solutions.common.facts.networking import (
    InternetConnection,
)
from mutablesecurity.solutions.common.facts.process import ProcessRunning
from mutablesecurity.solutions.common.facts.service import ActiveService
from mutablesecurity.solutions_manager import SolutionsManager


class LokiEndpoint(BaseInformation):
    IDENTIFIER = "loki_endpoint"
    DESCRIPTION = "Endpoint where Loki listens"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = None
    GETTER = None
    SETTER = None


class LokiUser(BaseInformation):
    IDENTIFIER = "loki_user"
    DESCRIPTION = "User to authenticate to Loki"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = None
    GETTER = None
    SETTER = None


class LokiToken(BaseInformation):
    IDENTIFIER = "loki_token"
    DESCRIPTION = "Token to authenticate to Loki"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = None
    GETTER = None
    SETTER = None


@deploy
def upload_new_configuration_file(
    old_value: typing.Any, new_value: typing.Any
) -> None:
    StopService.execute()

    template_path = os.path.join(
        os.path.dirname(__file__), "files/vector.yaml.j2"
    )

    # Generate the values to populate the Jinja template
    j2_values = {
        "loki": {
            "endpoint": LokiEndpoint.get(),
            "user": LokiUser.get(),
            "token": LokiToken.get(),
        },
        "sources": {},
    }

    for solution_id in new_value:
        solution = SolutionsManager().get_solution_class_by_id(solution_id)

        for source in solution.LOGS:
            source_id = solution_id + "_" + source.IDENTIFIER
            j2_values["sources"][source_id] = {
                "location": source.get_log_location_as_string(),
                "format": source.FORMAT.value,
            }

    files.template(
        src=template_path,
        dest="/etc/vector/vector.yaml",
        configuration=j2_values,
        user="vector",
        group="vector",
        name="Copy the generated configuration into vector's folder.",
    )

    StartService.execute()


class EnabledSolutions(BaseInformation):
    IDENTIFIER = "enabled_solutions"
    DESCRIPTION = "Solution whose logs are processed"
    INFO_TYPE = StringListDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = None
    GETTER = None
    SETTER = upload_new_configuration_file


class Version(BaseInformation):
    class VersionFact(FactBase):
        command = "vector --version"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return output[0].split()[1]

    IDENTIFIER = "version"
    DESCRIPTION = "Installed version"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = VersionFact
    SETTER = None


class InternetAccess(BaseTest):
    IDENTIFIER = "internet_access"
    DESCRIPTION = (
        "Checks if host has Internet access, which is required to download the"
        " package and, eventually, connect to Loki."
    )
    TEST_TYPE = TestType.REQUIREMENT
    FACT = InternetConnection


class ExistingSolution(BaseTest):
    IDENTIFIER = "present_command"
    DESCRIPTION = "Checks if Vector is present as a command."
    TEST_TYPE = TestType.PRESENCE
    FACT = PresentCommand
    FACT_ARGS = ("vector -h",)


class ValidConfiguration(BaseTest):
    class CheckValidationExitCode(FactBase):
        command = "vector validate /etc/vector/vector.yaml; echo $?"

        @staticmethod
        def process(output: typing.List[str]) -> bool:
            return int(output[-1]) == 0

    IDENTIFIER = "valid_configuration"
    DESCRIPTION = (
        "Checks if the generated Vector configuration is valid. It"
        " includes a healthcheck for the connection with Loki."
    )
    TEST_TYPE = TestType.OPERATIONAL
    FACT = CheckValidationExitCode


class RunningService(BaseTest):
    IDENTIFIER = "active_service"
    DESCRIPTION = "Checks if Vector's service is running."
    TEST_TYPE = TestType.OPERATIONAL
    FACT = ActiveService
    FACT_ARGS = ("vector",)


class ProcessUpAndRunning(BaseTest):
    IDENTIFIER = "process_running"
    DESCRIPTION = "Checks if Vector's process is running."
    TEST_TYPE = TestType.OPERATIONAL
    FACT = ProcessRunning
    FACT_ARGS = ("/usr/bin/vector",)


class StartService(BaseAction):
    @staticmethod
    @deploy
    def start_service() -> None:
        server.service(
            "vector", running=True, name="Starts the Vector service."
        )

    IDENTIFIER = "start_service"
    DESCRIPTION = "Starts the Vector service."
    ACT = start_service


class StopService(BaseAction):
    @staticmethod
    @deploy
    def stop_service() -> None:
        server.service(
            "vector", running=False, name="Stops the Vector service."
        )

    IDENTIFIER = "stop_service"
    DESCRIPTION = "Stops the Vector service."
    ACT = stop_service


class JsonLogs(BaseLog):
    IDENTIFIER = "json_alerts"
    DESCRIPTION = "Functional logs in JSON format"
    LOCATION = "/var/log/vector.log"
    FORMAT = LogFormat.JSON


class Vector(BaseSolution):
    INFORMATION = [
        LokiEndpoint,  # type: ignore[list-item]
        EnabledSolutions,  # type: ignore[list-item]
        LokiUser,  # type: ignore[list-item]
        LokiToken,  # type: ignore[list-item]
        Version,  # type: ignore[list-item]
    ]
    TESTS = [
        InternetAccess,  # type: ignore[list-item]
        ExistingSolution,  # type: ignore[list-item]
        RunningService,  # type: ignore[list-item]
        ProcessUpAndRunning,  # type: ignore[list-item]
        ValidConfiguration,  # type: ignore[list-item]
    ]
    LOGS = [
        JsonLogs,  # type: ignore[list-item]
    ]
    ACTIONS = [
        StartService,  # type: ignore[list-item]
        StopService,  # type: ignore[list-item]
    ]

    @staticmethod
    @deploy
    def _install() -> None:
        apt.packages(
            packages=["curl"],
            name="Installs curl",
        )

        server.shell(
            commands=[
                "curl -1sLf"
                " https://repositories.timber.io/public/vector/cfg/setup/"
                "bash.deb.sh | bash"
            ],
            name="Adds the Vector apt repository",
        )

        server.packages(
            packages=["vector"],
            name="Installs Vector via apt",
        )

        env_file = os.path.join(os.path.dirname(__file__), "files/vector.env")
        files.put(
            src=env_file,
            dest="/etc/default/vector",
            name=(
                "Uploads the file with environment variables used by the"
                " service."
            ),
        )

        files.file(
            path="/etc/vector/vector.toml",
            present=False,
            name="Removes the default configuration file.",
        )

        files.file(
            path="/var/log/vector.log",
            present=True,
            user="vector",
            group="vector",
            name="Creates the log file.",
        )

        upload_new_configuration_file(None, EnabledSolutions.get())

    @staticmethod
    @deploy
    def _uninstall(remove_logs: bool = True) -> None:
        apt.packages(
            packages=["vector"],
            present=False,
            extra_uninstall_args="--purge",
            name="Uninstalls Vector via apt.",
        )

    @staticmethod
    @deploy
    def _update() -> None:
        apt.packages(
            packages=["vector"],
            latest=True,
            name="Updates Vector via apt.",
        )
