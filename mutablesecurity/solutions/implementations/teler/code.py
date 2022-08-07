"""Module integrating teler."""

# pylint: disable=protected-access
# pylint: disable=missing-class-docstring
# pylint: disable=unused-argument
# pylint: disable=unexpected-keyword-arg

import json
import os
import typing
from datetime import datetime

from packaging import version
from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, files, server

from mutablesecurity.helpers.data_type import (
    BooleanDataType,
    IntegerDataType,
    StringDataType,
    StringListDataType,
)
from mutablesecurity.helpers.github import (
    get_asset_from_latest_release,
    get_latest_release_name,
)
from mutablesecurity.solutions.base import (
    BaseAction,
    BaseInformation,
    BaseLog,
    BaseSolution,
    BaseSolutionException,
    BaseTest,
    InformationProperties,
    TestType,
)
from mutablesecurity.solutions.common.facts.files import FilePresenceTest
from mutablesecurity.solutions.common.facts.networking import (
    InternetConnection,
)
from mutablesecurity.solutions.common.facts.process import ProcessRunning
from mutablesecurity.solutions.common.facts.service import ActiveService
from mutablesecurity.solutions.common.operations.crontab import (
    remove_crontabs_by_part,
)
from mutablesecurity.solutions.implementations.fail2ban.code import (
    Fail2ban,
    ReloadJails,
)

REPOSITORY_DETAILS = ("kitabisa", "teler")


class TelerAlreadyUpdatedException(BaseSolutionException):
    """teler is already at its newest version."""


class IncompatibleArchitectureException(BaseSolutionException):
    """Your architecture does not support any teler build."""


class WebServerPort(BaseInformation):
    IDENTIFIER = "port"
    DESCRIPTION = "Port on which the web server runs"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = 80
    GETTER = None
    SETTER = None


class WebServerLogFormat(BaseInformation):
    @staticmethod
    @deploy
    def set_log_format(old_value: typing.Any, new_value: typing.Any) -> None:
        StopProcess.execute()

        template_path = os.path.join(
            os.path.dirname(__file__), "files/teler.conf.j2"
        )
        j2_values = {"log_format": WebServerLogFormat.get()}
        files.template(
            src=template_path,
            dest="/opt/mutablesecurity/teler/teler.conf",
            configuration=j2_values,
            name="Copy the generated configuration into teler's folder.",
        )

        StartProcess.execute()

    IDENTIFIER = "log_format"
    DESCRIPTION = "Format in which the messages are logged"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = (
        "$remote_addr $remote_user - [$time_local]"
        ' "$request_method $request_uri $request_protocol" $status'
        ' $body_bytes_sent "$http_referer" "$http_user_agent"'
    )
    GETTER = None
    SETTER = set_log_format


class WebServerLogLocation(BaseInformation):
    @staticmethod
    @deploy
    def set_log_location(old_value: typing.Any, new_value: typing.Any) -> None:
        StopProcess.execute()

        remove_crontabs_by_part(
            unique_part="/opt/mutablesecurity/teler/teler",
            name="Removes the crontab containing the old log location",
        )
        server.crontab(
            command=ProcessCommand.get(),
            special_time="@reboot",
            present=True,
            name="Adds a new crontab, with the new log location.",
        )

        StartProcess.execute()

    IDENTIFIER = "log_location"
    DESCRIPTION = "Location in which nginx logs messages"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "/var/log/nginx/access.log"
    GETTER = None
    SETTER = set_log_location


class ProcessCommand(BaseInformation):
    class ProcessCommandFact(FactBase):
        command = "echo 'hi'"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return (
                f"tail -f {WebServerLogLocation.get()} |"
                " /opt/mutablesecurity/teler/teler -c"
                " /opt/mutablesecurity/teler/teler.conf  2>&1 |  sed -u -r"
                r' "s/\\x1B\[([0-9]{1,3}(;[0-9]{1,2})?)?[mGK]//g" | tee'
                " --append /var/log/teler.text.log"
            )

    IDENTIFIER = "command"
    DESCRIPTION = "Command used to create teler's process and crontab"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.READ_ONLY,
        InformationProperties.AUTO_GENERATED_BEFORE_INSTALL,
    ]
    DEFAULT_VALUE = None
    GETTER = ProcessCommandFact
    SETTER = None


class Version(BaseInformation):
    class VersionFact(FactBase):
        # Teler returns the major version as an exit code
        command = "/opt/mutablesecurity/teler/teler -v || true"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return output[0].split()[1]

    IDENTIFIER = "version"
    DESCRIPTION = "Installed version"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.METRIC,
    ]
    DEFAULT_VALUE = None
    GETTER = VersionFact
    SETTER = None


class Fail2banIntegration(BaseInformation):
    @staticmethod
    @deploy
    def integrate_fail2ban(
        old_value: typing.Any, new_value: typing.Any
    ) -> None:
        Fail2ban._ensure_installation_state(installed=True)

        filter_path = os.path.join(
            os.path.dirname(__file__), "files/filter.conf"
        )
        files.put(
            src=filter_path,
            dest="/etc/fail2ban/filter.d/teler.conf",
            name="Uploads the Fail2ban filter configuration for teler.",
        )

        jail_path = os.path.join(os.path.dirname(__file__), "files/jail.conf")
        files.put(
            src=jail_path,
            dest="/etc/fail2ban/jail.d/teler.conf",
            name="Uploads the Fail2ban jail configuration for teler.",
        )

        ReloadJails.execute()

    IDENTIFIER = "fail2ban_integration"
    DESCRIPTION = "Whether the integration with Fail2ban is activated"
    INFO_TYPE = BooleanDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = False
    GETTER = FilePresenceTest
    GETTER_ARGS = ("/etc/fail2ban/jail.d/teler.conf",)
    SETTER = integrate_fail2ban


class BinaryArchitectureFact(FactBase):
    command = "dpkg --print-architecture"

    @staticmethod
    def process(output: typing.List[str]) -> str:
        architecture = output[0]

        if architecture in ["386", "amd64", "arm64", "armv6"]:
            return architecture
        else:
            raise IncompatibleArchitectureException()


class BinaryArchitecture(BaseInformation):
    IDENTIFIER = "architecture"
    DESCRIPTION = "Binary's architecture"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.READ_ONLY,
        InformationProperties.AUTO_GENERATED_BEFORE_INSTALL,
    ]
    DEFAULT_VALUE = None
    GETTER = BinaryArchitectureFact
    SETTER = None


class AlertsCount(BaseInformation):
    class AlertsCountFact(FactBase):
        command = "cat /var/log/teler.json.log | egrep '^{' | wc -l"

        @staticmethod
        def process(output: typing.List[str]) -> int:
            return int(output[0])

    IDENTIFIER = "alerts_count"
    DESCRIPTION = "Total number of generated alerts"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = AlertsCountFact
    SETTER = None


class DailyAlertsCount(BaseInformation):
    class DailyAlertsCountFact(FactBase):
        @staticmethod
        def command() -> str:
            current_date = datetime.today().strftime("%d/%b/%Y")

            return (
                f"cat /var/log/teler.json.log | grep '{current_date}' | wc -l"
            )

        @staticmethod
        def process(output: typing.List[str]) -> int:
            return int(output[0])

    IDENTIFIER = "daily_alerts_count"
    DESCRIPTION = "Total number of alerts generated today"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = DailyAlertsCountFact
    SETTER = None


class TopAttacksTypes(BaseInformation):
    class TopAttacksTypesFact(FactBase):
        command = (
            "cat /var/log/teler.json.log | jq -s '.' | jq  'group_by"
            " (.category)[] | {type: .[0].category, occurances: length}' | jq"
            " -s | jq -S . | jq 'sort_by(.occurances) | reverse | .[0:3]'"
        )

        @staticmethod
        def process(output: typing.List[str]) -> typing.List[str]:
            attacks_types = json.loads("".join(output))

            return [
                f"{attacks_type['type']} ({attacks_type['occurances']})"
                for attacks_type in attacks_types
            ]

    IDENTIFIER = "top_attacks_types"
    DESCRIPTION = "Top 3 types of web attacks"
    INFO_TYPE = StringListDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = TopAttacksTypesFact
    SETTER = None


class TopAttackers(BaseInformation):
    class TopAttackersFact(FactBase):
        command = (
            "cat /var/log/teler.json.log | jq -s '.' | jq  'group_by"
            " (.remote_addr)[] | {attacker: .[0].remote_addr, occurances:"
            " length}' | jq -s | jq -S . | jq 'sort_by(.occurances) | reverse"
            " | .[0:3]'"
        )

        @staticmethod
        def process(output: typing.List[str]) -> typing.List[str]:
            attackers = json.loads("".join(output))

            return [
                f"{attacker['attacker']} ({attacker['occurances']})"
                for attacker in attackers
            ]

    IDENTIFIER = "top_attackers"
    DESCRIPTION = "Top 3 attackers"
    INFO_TYPE = StringListDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = TopAttackersFact
    SETTER = None


class StartProcess(BaseAction):
    @staticmethod
    @deploy
    def start_process() -> None:
        server.shell(
            commands=[f"tmux new -d '{ProcessCommand.get()}'"],
            name=(
                "Run the binary now, without a restart to trigger the crontab."
            ),
        )

    IDENTIFIER = "start_process"
    DESCRIPTION = "Start teler's process"
    ACT = start_process


class StopProcess(BaseAction):
    @staticmethod
    @deploy
    def stop_process() -> None:
        server.shell(
            commands=["killall -9 /opt/mutablesecurity/teler/teler || true"],
            name="Kills the teler process.",
        )

    IDENTIFIER = "stop_process"
    DESCRIPTION = "Stop teler's process"
    ACT = stop_process


class BadUserAgentDetection(BaseTest):
    @staticmethod
    @deploy
    def make_request() -> None:
        url = "http://localhost:" + str(WebServerPort.get())
        wget_command = (
            "wget --header 'User-Agent: curl x MutableSecurity' -O"
            " /tmp/index.html "
            + url
        )
        server.shell(
            commands=[wget_command],
            name="Requests the website with a bad user agent.",
            success_exit_codes=[0, 4],
        )

    class BadUserAgentDetectionFact(FactBase):
        @staticmethod
        def command() -> str:
            current_date = datetime.today().strftime("%d/%b/%Y:%H:%M")

            check_command = (
                "cat /var/log/teler.json.log | jq 'select((.http_user_agent"
                ' == "curl x MutableSecurity") and (.time_local |'
                f' startswith("{current_date}")))\' | wc -l'
            )

            return check_command

        @staticmethod
        def process(output: typing.List[str]) -> bool:
            return int(output[0]) != 0

    IDENTIFIER = "bad_user_agent_detection"
    DESCRIPTION = "Checks if teler detects a request with a bad user agent."
    TEST_TYPE = TestType.SECURITY
    TRIGGER = make_request
    FACT = BadUserAgentDetectionFact


class InternetAccess(BaseTest):
    IDENTIFIER = "internet_access"
    DESCRIPTION = "Checks if host has Internet access."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = InternetConnection


class ProcessUpAndRunning(BaseTest):
    IDENTIFIER = "process_running"
    DESCRIPTION = "Checks if teler's process is running."
    TEST_TYPE = TestType.OPERATIONAL
    FACT = ProcessRunning
    FACT_ARGS = ("/opt/mutablesecurity/teler/teler",)


class ActiveNginx(BaseTest):
    IDENTIFIER = "nginx_active"
    DESCRIPTION = "Checks if nginx is installed and the service is active."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = ActiveService
    FACT_ARGS = ("nginx",)


class SupportedArchitecture(BaseTest):
    class SupportedArchitectureFact(BinaryArchitectureFact):
        @staticmethod
        def process(  # type: ignore[override]
            output: typing.List[str],
        ) -> bool:
            architecture = BinaryArchitectureFact.process(output)

            return architecture is not None

    IDENTIFIER = "supported_architecture"
    DESCRIPTION = "Checks if there is any build for this architecture."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = SupportedArchitectureFact


class BinaryPresenceTest(BaseTest):
    IDENTIFIER = "presence"
    DESCRIPTION = "Checks if a file is present."
    TEST_TYPE = TestType.PRESENCE
    FACT = FilePresenceTest
    FACT_ARGS = ("/opt/mutablesecurity/teler/teler",)


class JsonAlerts(BaseLog):
    class JsonAlertsFact(FactBase):
        command = "cat /var/log/teler.json.log"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return "".join(output)

    IDENTIFIER = "json_alerts"
    DESCRIPTION = "Generated alerts in JSON format"
    FACT = JsonAlertsFact


class TextAlerts(BaseLog):
    class TextAlertsFact(FactBase):
        command = "cat /var/log/teler.text.log"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return "".join(output)

    IDENTIFIER = "text_alerts"
    DESCRIPTION = "Generated alerts in plaintext format"
    FACT = TextAlertsFact


class Teler(BaseSolution):
    INFORMATION = [
        WebServerPort,  # type: ignore[list-item]
        WebServerLogFormat,  # type: ignore[list-item]
        WebServerLogLocation,  # type: ignore[list-item]
        ProcessCommand,  # type: ignore[list-item]
        Version,  # type: ignore[list-item]
        BinaryArchitecture,  # type: ignore[list-item]
        AlertsCount,  # type: ignore[list-item]
        DailyAlertsCount,  # type: ignore[list-item]
        TopAttacksTypes,  # type: ignore[list-item]
        TopAttackers,  # type: ignore[list-item]
        Fail2banIntegration,  # type: ignore[list-item]
    ]
    TESTS = [
        BadUserAgentDetection,  # type: ignore[list-item]
        InternetAccess,  # type: ignore[list-item]
        ProcessUpAndRunning,  # type: ignore[list-item]
        BinaryPresenceTest,  # type: ignore[list-item]
        SupportedArchitecture,  # type: ignore[list-item]
        ActiveNginx,  # type: ignore[list-item]
    ]
    LOGS = [
        JsonAlerts,  # type: ignore[list-item]
        TextAlerts,  # type: ignore[list-item]
    ]
    ACTIONS = [
        StartProcess,  # type: ignore[list-item]
        StopProcess,  # type: ignore[list-item]
    ]

    @staticmethod
    @deploy
    def _install() -> None:
        apt.packages(
            packages=["jq", "tmux"],
            name="Installs the required packages",
        )

        architecture = BinaryArchitecture.get()
        if not architecture:
            raise IncompatibleArchitectureException()

        release_url = get_asset_from_latest_release(
            *REPOSITORY_DETAILS, f"linux_{architecture}"
        )
        wget_command = f"wget -O /tmp/teler.tar.gz {release_url}"
        server.shell(
            commands=[wget_command],
            name="Downloads the latest release from GitHub.",
        )

        server.shell(
            commands=["tar -xzf /tmp/teler.tar.gz -C /tmp"],
            name="Unarchives the downloaded release.",
        )

        files.directory(
            path="/opt/teler",
            present=True,
            name="Creates the folder that will store teler.",
        )

        server.shell(
            commands=["cp /tmp/teler /opt/mutablesecurity/teler/teler"],
            name="Moves the binary into the created folder.",
        )

        template_path = os.path.join(
            os.path.dirname(__file__), "files/teler.conf.j2"
        )
        j2_values = {"log_format": WebServerLogFormat.get()}
        files.template(
            src=template_path,
            dest="/opt/mutablesecurity/teler/teler.conf",
            configuration=j2_values,
            name="Copy the generated configuration into teler's folder.",
        )

        files.file(
            "/var/log/teler.json.log",
            present=True,
            name="Creates the log file.",
        )

        server.crontab(
            command=ProcessCommand.get(),
            special_time="@reboot",
            present=True,
            name="Adds a crontab to automatically run the binary, at startup.",
        )

        StartProcess.execute()

    @staticmethod
    @deploy
    def _uninstall(remove_logs: bool = True) -> None:
        StopProcess.execute()

        remove_crontabs_by_part(
            unique_part="/opt/mutablesecurity/teler/teler",
            name="Removes the crontab to automatically run teler.",
        )

        files.directory(
            name="Removes the teler executable and configuration.",
            path="/opt/teler",
            present=False,
        )

        if remove_logs:
            files.file(
                name="Removes teler's JSON log file.",
                path="/var/log/teler.json.log",
                present=False,
            )

            files.file(
                name="Removes teler's text log file.",
                path="/var/log/teler.text.log",
                present=False,
            )

    @staticmethod
    @deploy
    def _update() -> None:
        # Check if the latest release has a greater version than the local
        # software
        local_version = Version.get()
        github_latest_version = get_latest_release_name(*REPOSITORY_DETAILS)
        if version.parse(local_version) == version.parse(
            github_latest_version
        ):
            raise TelerAlreadyUpdatedException()

        Teler._uninstall(remove_logs=False)
        Teler.install()
