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
    IntegerDataType,
    StringListDataType,
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
from mutablesecurity.solutions.common.facts.os import CheckIfUbuntu
from mutablesecurity.solutions.common.facts.service import ActiveService
from mutablesecurity.solutions.common.operations.files import (
    append_line_to_file,
)


@deploy
def place_ssh_jail_configuration_as_setter(
    old_value: typing.Any, new_value: typing.Any
) -> None:
    template_path = os.path.join(
        os.path.dirname(__file__), "files/sshd.conf.j2"
    )
    j2_values = {
        "ssh_port": SSHPort.get(),
        "max_retries": MaxAttackerRetries.get(),
        "ban_time": BanSeconds.get(),
        "ignored_ips": IgnoredIPs.get(),
    }
    files.template(
        src=template_path,
        dest="/etc/fail2ban/jail.d/sshd.conf",
        configuration=j2_values,
        name="Copy the generated configuration into Fail2ban's folder.",
    )

    ReloadJails.execute()


@deploy
def place_ssh_jail_configuration() -> None:
    place_ssh_jail_configuration_as_setter(None, None)


class SSHPort(BaseInformation):
    IDENTIFIER = "ssh_port"
    DESCRIPTION = "Port on which the SSH server runs"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = 22
    GETTER = None
    SETTER = place_ssh_jail_configuration_as_setter


class MaxAttackerRetries(BaseInformation):
    IDENTIFIER = "max_retries"
    DESCRIPTION = "Login attempts limit above which a user is banned"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = 3
    GETTER = None
    SETTER = place_ssh_jail_configuration_as_setter


class BanSeconds(BaseInformation):
    IDENTIFIER = "ban_seconds"
    DESCRIPTION = "Ban duration in seconds"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = 3600
    GETTER = None
    SETTER = place_ssh_jail_configuration_as_setter


class IgnoredIPs(BaseInformation):
    IDENTIFIER = "ignored_ips"
    DESCRIPTION = (
        "IPs to ignore. Can identify machines like the pentest-related one or"
        " controlled strictly by your cloud provider."
    )
    INFO_TYPE = StringListDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "127.0.0.1"
    GETTER = None
    SETTER = place_ssh_jail_configuration_as_setter


class JailsCount(BaseInformation):
    class JailCountFact(FactBase):
        command = (
            "sqlite3 /var/lib/fail2ban/fail2ban.sqlite3 'select count(name)"
            " from jails where enabled=1'"
        )

        @staticmethod
        def process(output: typing.List[str]) -> int:
            return int(output[0]) - 1

    IDENTIFIER = "jails_count"
    DESCRIPTION = "Number of set jails"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = JailCountFact
    SETTER = None


class ActiveJails(BaseInformation):
    class ActiveJailsFact(FactBase):
        command = (
            "sqlite3 /var/lib/fail2ban/fail2ban.sqlite3 'select name from"
            " jails where enabled=1'"
        )

        @staticmethod
        def process(output: typing.List[str]) -> typing.List[str]:
            output.remove("healthcheck")

            return output

    IDENTIFIER = "active_jails"
    DESCRIPTION = "Active jails"
    INFO_TYPE = StringListDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = ActiveJailsFact
    SETTER = None


class BannedIPs(BaseInformation):
    class BannedIPsFact(FactBase):
        command = (
            "sqlite3 /var/lib/fail2ban/fail2ban.sqlite3 'select ip, jail from"
            ' bips where jail != "healthcheck"\''
        )

        @staticmethod
        def process(output: typing.List[str]) -> typing.List[str]:
            return [
                f'- {ip} from jail "{jail}"'
                for ip, jail in [line.split("|") for line in output]
            ]

    IDENTIFIER = "banned_ips"
    DESCRIPTION = "Banned IPs from all jails"
    INFO_TYPE = StringListDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = BannedIPsFact
    SETTER = None


class UbuntuRequirement(BaseTest):
    IDENTIFIER = "ubuntu"
    DESCRIPTION = "Checks if the operating system is Ubuntu."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = CheckIfUbuntu


class ActiveFail2ban(BaseTest):
    IDENTIFIER = "active_service"
    DESCRIPTION = "Checks if the Fail2ban service is active."
    TEST_TYPE = TestType.OPERATIONAL
    FACT = ActiveService
    FACT_ARGS = ("fail2ban",)


class ClientCommandPresent(BaseTest):
    IDENTIFIER = "command"
    DESCRIPTION = "Checks if the Fail2ban client is registered as a command."
    TEST_TYPE = TestType.PRESENCE
    FACT = PresentCommand
    FACT_ARGS = ("fail2ban-client --help",)


class HealthCheck(BaseTest):
    @staticmethod
    @deploy
    def place_logs() -> None:
        ban_line = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        ban_line += " 8.8.8.8"

        for _ in range(3):
            append_line_to_file("/var/log/fail2ban-healthcheck.log", ban_line)

    class HealthCheckFact(FactBase):
        command = "fail2ban-client set healthcheck unbanip 8.8.8.8"

        @staticmethod
        def process(output: typing.List) -> bool:
            return int(output[0]) == 1

    IDENTIFIER = "healthcheck"
    DESCRIPTION = (
        "Checks if Fail2ban blocks an IP when identifying multiple logs"
        " generated by it."
    )
    TEST_TYPE = TestType.SECURITY
    TRIGGER = place_logs
    FACT = HealthCheckFact


class StartService(BaseAction):
    @staticmethod
    @deploy
    def start_service() -> None:
        server.service(
            "fail2ban", running=True, name="Starts the Fail2ban service."
        )

    IDENTIFIER = "start_service"
    DESCRIPTION = "Starts the Fail2ban service."
    ACT = start_service


class StopService(BaseAction):
    @staticmethod
    @deploy
    def stop_service() -> None:
        server.service(
            "fail2ban", running=False, name="Stops the Fail2ban service."
        )

    IDENTIFIER = "stop_service"
    DESCRIPTION = "Stops the Fail2ban service."
    ACT = stop_service


class RestartService(BaseAction):
    @staticmethod
    @deploy
    def restart_service() -> None:
        server.service(
            "fail2ban", restarted=True, name="Restarts the Fail2ban service."
        )

    IDENTIFIER = "restart_service"
    DESCRIPTION = "Restarts the Fail2ban service."
    ACT = restart_service


class ReloadJails(BaseAction):
    @staticmethod
    @deploy
    def reload_jails() -> None:
        server.shell(commands=["service fail2ban restart"])

    IDENTIFIER = "reload_jails"
    DESCRIPTION = "Reload the jail."
    ACT = reload_jails


class Unban(BaseAction):
    @staticmethod
    @deploy
    def unban(jail_name: str, ip: str) -> None:  # pylint: disable=invalid-name
        server.shell(
            commands=[f"fail2ban-client set {jail_name} unbanip {ip}"],
            name=f"Unbans {ip} from jail {jail_name}.",
        )

    IDENTIFIER = "unban"
    DESCRIPTION = "Unbans an IP address from a jail."
    ACT = unban


class DefaultLogs(BaseLog):
    class DefaultLogsFact(FactBase):
        command = "cat /var/log/fail2ban.log"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return "\n".join(output)

    IDENTIFIER = "logs"
    DESCRIPTION = "Default log location"
    FACT = DefaultLogsFact


class Fail2ban(BaseSolution):
    INFORMATION = [
        SSHPort,  # type: ignore[list-item, var-annotated]
        MaxAttackerRetries,  # type: ignore[list-item, var-annotated]
        BanSeconds,  # type: ignore[list-item, var-annotated]
        IgnoredIPs,  # type: ignore[list-item, var-annotated]
        JailsCount,  # type: ignore[list-item, var-annotated]
        ActiveJails,  # type: ignore[list-item, var-annotated]
        BannedIPs,  # type: ignore[list-item, var-annotated]
    ]
    TESTS = [
        UbuntuRequirement,  # type: ignore[list-item, var-annotated]
        ActiveFail2ban,  # type: ignore[list-item, var-annotated]
        ClientCommandPresent,  # type: ignore[list-item, var-annotated]
        HealthCheck,  # type: ignore[list-item, var-annotated]
    ]
    LOGS = [DefaultLogs]  # type: ignore[list-item, var-annotated]
    ACTIONS = [
        StartService,  # type: ignore[list-item, var-annotated]
        StopService,  # type: ignore[list-item, var-annotated]
        RestartService,  # type: ignore[list-item, var-annotated]
        ReloadJails,  # type: ignore[list-item, var-annotated]
        Unban,  # type: ignore[list-item, var-annotated]
    ]

    @staticmethod
    @deploy
    def _install() -> None:
        apt.packages(
            packages=["sqlite3", "fail2ban"],
            name="Installs Fail2ban and SQLite via apt.",
        )

        place_ssh_jail_configuration()

        filter_path = os.path.join(
            os.path.dirname(__file__), "files/healthcheck/filter.conf"
        )
        files.put(
            src=filter_path,
            dest="/etc/fail2ban/filter.d/healthcheck.conf",
            name="Copy the healthcheck filter configuration.",
        )

        jail_path = os.path.join(
            os.path.dirname(__file__), "files/healthcheck/jail.conf"
        )
        files.put(
            src=jail_path,
            dest="/etc/fail2ban/jail.d/healthcheck.conf",
            name="Copy the healthcheck jail configuration.",
        )

        files.file(
            path="/var/log/fail2ban-healthcheck.log",
            present=True,
            name="Create the healthcheck log file.",
        )

        ReloadJails.execute()

    @staticmethod
    @deploy
    def _uninstall() -> None:
        apt.packages(
            packages=["fail2ban"],
            present=False,
            extra_uninstall_args="--purge",
            name="Uninstalls Fail2ban via apt.",
        )

        files.file(
            path="/var/log/fail2ban-healthcheck.log",
            present=False,
            name="Remove the healthcheck log file.",
        )

    @staticmethod
    @deploy
    def _update() -> None:
        apt.packages(
            packages=["fail2ban"],
            latest=True,
            name="Uninstalls Fail2ban via apt.",
        )
