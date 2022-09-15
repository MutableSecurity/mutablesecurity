"""Module integrating Suricata."""

# pylint: disable=missing-class-docstring
# pylint: disable=unused-argument
# pylint: disable=unexpected-keyword-arg

import os
import typing
from datetime import datetime

from pyinfra.api.deploy import deploy
from pyinfra.api.facts import FactBase
from pyinfra.operations import apt, files, server

from mutablesecurity.helpers.data_type import (
    BooleanDataType,
    IntegerDataType,
    StringDataType,
)
from mutablesecurity.solutions.base import (
    BaseAction,
    BaseInformation,
    BaseLog,
    BaseSolution,
    BaseTest,
    InformationProperties,
    TestType,
)
from mutablesecurity.solutions.common.facts.bash import PresentCommand
from mutablesecurity.solutions.common.facts.networking import (
    InternetConnection,
)


class StartService(BaseAction):
    @staticmethod
    @deploy
    def start_service() -> None:
        server.service(
            "suricata", running=True, name="Starts the Suricata service."
        )

    IDENTIFIER = "start_service"
    DESCRIPTION = "Starts the Suricata service."
    ACT = start_service


class StopService(BaseAction):
    @staticmethod
    @deploy
    def stop_service() -> None:
        server.service(
            "suricata", running=False, name="Stops the Suricata service."
        )

    IDENTIFIER = "stop_service"
    DESCRIPTION = "Stops the Suricata service."
    ACT = stop_service


class Interface(BaseInformation):
    @staticmethod
    @deploy
    def set_configuration(
        old_value: typing.Any, new_value: typing.Any
    ) -> None:
        _save_current_configuration()

    class ProcessCommandFact(FactBase):
        command =("ls -1 /sys/class/net")

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return (output[0])

    IDENTIFIER = "interface"
    DESCRIPTION = "Interface on which Suricata listens"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.WRITABLE,
        InformationProperties.MANDATORY,
    ]
    DEFAULT_VALUE = None
    GETTER = ProcessCommandFact
    SETTER = set_configuration


class AutomaticUpdate(BaseInformation):
    @staticmethod
    @deploy
    def set_configuration(
        old_value: typing.Any, new_value: typing.Any
    ) -> None:
        _save_current_configuration()

    IDENTIFIER = "automatic_update"
    DESCRIPTION = "State of the automatic daily updates"
    INFO_TYPE = BooleanDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = False
    GETTER = None
    SETTER = set_configuration


class AlertsCount(BaseInformation):
    class AlertsCountFact(FactBase):
        @staticmethod
        def command() -> str:
            return "cat /var/log/suricata/fast.log | wc -l"

        @staticmethod
        def process(output: typing.List[str]) -> int:
            return int(output[0])

    IDENTIFIER = "total_alerts"
    DESCRIPTION = "Total number of alerts"
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
        current_date = datetime.today().strftime("%m/%d/%Y")
        command = (
            f"cat /var/log/suricata/fast.log| grep '{current_date}' | wc -l"
        )

        @staticmethod
        def process(output: typing.List[str]) -> int:
            return int(output[0])

    IDENTIFIER = "total_alerts"
    DESCRIPTION = "Total number of alerts"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = DailyAlertsCountFact
    SETTER = None


class Uptime(BaseInformation):
    class UptimeFact(FactBase):
        command = (
            "suricatasc -c uptime | jq '.message'"
        )

        @staticmethod
        def process(output: typing.List[str]) -> int:
            return int(output[0])

    IDENTIFIER = "uptime"
    DESCRIPTION = "uptime"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = UptimeFact
    SETTER = None


class Version(BaseInformation):
    class VersionFact(FactBase):
        command = "suricata -V version | egrep -o '([0-9].)+'   "

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return output[0]

    IDENTIFIER = "version"
    DESCRIPTION = "Current installed version"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.AUTO_GENERATED_AFTER_INSTALL,
        InformationProperties.READ_ONLY,

    ]
    DEFAULT_VALUE = None
    GETTER = VersionFact
    SETTER = None


class TextAlerts(BaseLog):
    class TextAlertsFact(FactBase):
        command = "cat /var/log/suricata/fast.log"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return "".join(output)

    IDENTIFIER = "text_alerts"
    DESCRIPTION = "Generated alerts in plaintext format"
    FACT = TextAlertsFact


class MaliciousURL(BaseTest):
    class MaliciousURLFact(FactBase):
        @staticmethod
        def command() -> str:
            current_date = datetime.today().strftime("%m/%d/%Y-%H:%M")
            curl_command = (
                "wget -O /tmp/index.html http://testmynids.org/uid/index.html"
                "&& tail -n 1 /var/log/suricata/fast.log | "
                f"grep '{current_date}' | grep -c '1:2100498:7' || true"
            )

            return curl_command

        @staticmethod
        def process(output: typing.List[str]) -> bool:
            return int(output[0]) != 0

    IDENTIFIER = "malicious_url"
    DESCRIPTION = " Requests a malicious-marked URL"
    TEST_TYPE = TestType.SECURITY
    FACT = MaliciousURLFact


class ProcessUpAndRunning(BaseTest):
    class ProcessRunning1(FactBase):
        """Fact for checking if a process is running."""

        def command(self, executable: str) -> str:
            return f"systemctl status {executable}| egrep ' active' | wc -l"

        @staticmethod
        def process(
            output: typing.List[str],
        ) -> bool:
            return int(output[0]) != 0
    IDENTIFIER = "process_running"
    DESCRIPTION = "Checks if suricata's process is running."
    TEST_TYPE = TestType.OPERATIONAL
    FACT = ProcessRunning1
    FACT_ARGS = ("suricata",)


class ExistingSolution(BaseTest):
    IDENTIFIER = "present_commnad"
    DESCRIPTION = "Checks if suricata's command is present."
    TEST_TYPE = TestType.PRESENCE
    FACT = PresentCommand
    FACT_ARGS = ("suricata -V",)


class InternetAccess(BaseTest):
    IDENTIFIER = "internet_access"
    DESCRIPTION = "Checks if host has Internet access."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = InternetConnection


class Suricata(BaseSolution):
    INFORMATION = [
        Interface,  # type: ignore[list-item]
        AlertsCount,  # type: ignore[list-item]
        AutomaticUpdate,  # type: ignore[list-item]
        DailyAlertsCount,  # type: ignore[list-item]
        Uptime,  # type: ignore[list-item]
        Version,  # type: ignore[list-item]
    ]  # type: ignore[list-item, var-annotated]

    TESTS = [
        MaliciousURL,  # type: ignore[list-item, var-annotated]
        InternetAccess,  # type: ignore[list-item, var-annotated]
        ProcessUpAndRunning,  # type: ignore[list-item, var-annotated]
        ExistingSolution,  # type: ignore[list-item, var-annotated]
    ]  # type: ignore[list-item, var-annotated]
    LOGS = [
        TextAlerts,  # type: ignore[list-item, var-annotated]
    ]
    ACTIONS = [
        StartService,  # type: ignore[list-item, var-annotated]
        StopService,  # type: ignore[list-item, var-annotated]
    ]  # type: ignore[list-item, var-annotated]

    @staticmethod
    @deploy
    def _install() -> None:
        apt.packages(
            packages=["software-properties-common", "jq", "tmux", "moreutils"],
            name="Installs the required packages",
        )

        apt.packages(
            name="Installs Suricata",
            packages=["suricata"],
        )

        _save_current_configuration()

        files.replace(
            name=(
                "Replaces the default rules location in the Suricata's"
                " configuration file"
            ),
            path="/etc/suricata/suricata.yaml",
            match=r"^default-rule-path: /etc/suricata/rules$",
            replace="default-rule-path: /var/lib/suricata/rules",
        )

        server.shell(
            name="Updates the Suricata's rules",
            commands=["suricata-update"],
        )

        # Restart the Suricata service as it starts at install but fails if the
        # default interface is not eth0.
        server.shell(
            name="Restart the Suricata service",
            commands=["service suricata restart"],
        )

    @staticmethod
    @deploy
    def _uninstall() -> None:
        apt.packages(
            packages=["suricata"],
            present=False,
            extra_uninstall_args="--purge",
            name="Uninstalls Suricata via apt.",
        )

    @staticmethod
    @deploy
    def _update() -> None:
        apt.packages(
            packages=["suricata"],
            latest=True,
            name="Updates Suricata",
        )


def _save_current_configuration() -> None:
    template_path = os.path.join(
        os.path.dirname(__file__), "files/suricata.conf.j2"
    )
    j2_values = {
        "interface": Interface().get(),
        "automatic_update": AutomaticUpdate.get(),
    }
    files.template(
        src=template_path,
        dest="/opt/mutablesecurity/suricata/suricata.conf",
        configuration=j2_values,
        name="Copy the generated configuration into Suricata's folder.",
    )
