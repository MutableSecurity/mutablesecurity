"""Module integrating ClamAV."""

# pylint: disable=missing-class-docstring
# pylint: disable=unused-argument
# pylint: disable=unexpected-keyword-arg
# pylint: disable=anomalous-backslash-in-string

import typing
from datetime import datetime

from pyinfra import host
from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, files, server

from mutablesecurity.helpers.data_type import IntegerDataType, StringDataType
from mutablesecurity.solutions.base import (BaseAction, BaseInformation,
                                            BaseLog, BaseSolution,
                                            BaseSolutionException, BaseTest,
                                            InformationProperties, TestType)
from mutablesecurity.solutions.common.facts.networking import \
    InternetConnection
from mutablesecurity.solutions.common.facts.os import CheckIfUbuntu
from mutablesecurity.solutions.common.facts.service import ActiveService
from mutablesecurity.solutions.common.operations.crontab import \
    remove_crontabs_by_part


class ClamAVAlreadyUpdatedException(BaseSolutionException):
    """ClamAV is already at its newest version."""


def run_crontab() -> None:
    server.crontab(
        sudo=True,
        name="Adds a crontab to automatically scan the system recursively",
        command=(
            "clamscan --recursive"
            f" --log={ScanLogLocation.get()}"
            f" --move={QuarantineLocation.get()} {ScanLocation.get()}"
        ),
        present=True,
        minute=f"{ScanMinute.get()}",
        hour=f"{ScanHour.get()}",
        month=f"{ScanMonth.get()}",
        day_of_week=f"{ScanDayOfTheWeek.get()}",
        day_of_month=f"{ScanDayOfTheMonth.get()}",
    )


def change_scan_logs_location(
    old_value: typing.Any, new_value: typing.Any
) -> None:
    remove_crontabs_by_part(
        unique_part="clamscan --recursive",
        name="Removes the crontab containing the old scan log location",
    )

    server.crontab(
        sudo=True,
        name="Adds a crontab to automatically scan the system recursively",
        command=(
            "clamscan --recursive"
            f" --log={ScanLogLocation.get()}"
            f" --move={QuarantineLocation.get()} {ScanLocation.get()}"
        ),
        present=True,
        minute=f"{ScanMinute.get()}",
        hour=f"{ScanHour.get()}",
        month=f"{ScanMonth.get()}",
        day_of_week=f"{ScanDayOfTheWeek.get()}",
        day_of_month=f"{ScanDayOfTheMonth.get()}",
    )

    files.file(
        sudo=True,
        name=(
            "Creating the new logs file and directory with the 400 permissions"
        ),
        path=f"{new_value}",
        present=True,
        mode="400",
        create_remote_dir=True,
    )

    server.shell(
        sudo=True,
        name=(
            "Adding all the old logs data into the new location while deleting"
            " the old ones."
        ),
        commands=f"mv -f {old_value} {new_value}",
    )


def change_quarantine_location(
    old_value: typing.Any, new_value: typing.Any
) -> None:
    remove_crontabs_by_part(
        unique_part="clamscan --recursive",
        name="Removing the crontab containing the old quarantine location",
    )

    server.crontab(
        sudo=True,
        name="Adds a crontab to automatically scan the system recursively",
        command=(
            "clamscan --recursive"
            f" --log={ScanLogLocation.get()}"
            f" --move={QuarantineLocation.get()} {ScanLocation.get()}"
        ),
        present=True,
        minute=f"{ScanMinute.get()}",
        hour=f"{ScanHour.get()}",
        month=f"{ScanMonth.get()}",
        day_of_week=f"{ScanDayOfTheWeek.get()}",
        day_of_month=f"{ScanDayOfTheMonth.get()}",
    )

    files.directory(
        sudo=True,
        name="Creating the new quarantine directory",
        path=f"{QuarantineLocation.get()}",
        present=True,
    )

    server.shell(
        sudo=True,
        name="Adding all the old quarantine data to the new location .",
        commands=f"mv -f {old_value} {new_value}",
    )


def change_scan_location_or_crontab(
    old_value: typing.Any, new_value: typing.Any
) -> None:
    remove_crontabs_by_part(
        unique_part="clamscan --recursive",
        name="Removes the crontab containing the old scan location/crontab",
    )

    server.crontab(
        sudo=True,
        name="Adds a crontab to automatically scan the system recursively",
        command=(
            "clamscan --recursive"
            f" --log={ScanLogLocation.get()}"
            f" --move={QuarantineLocation.get()} {ScanLocation.get()}"
        ),
        present=True,
        minute=f"{ScanMinute.get()}",
        hour=f"{ScanHour.get()}",
        month=f"{ScanMonth.get()}",
        day_of_week=f"{ScanDayOfTheWeek.get()}",
        day_of_month=f"{ScanDayOfTheMonth.get()}",
    )


class ScanLogLocation(BaseInformation):
    IDENTIFIER = "scan_log_location"
    DESCRIPTION = (
        "The location of the generated logs after the on-demand/crontab scans."
        "Chose a file in which the logs will be stored if you would"
        " like to change."
    )
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.MANDATORY,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.CONFIGURATION,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "/opt/mutablesecurity/clamav/logs/logs.txt"
    GETTER = None
    SETTER = change_scan_logs_location


class QuarantineLocation(BaseInformation):
    IDENTIFIER = "quarantine_location"
    DESCRIPTION = (
        "The location where the infected files will be moved to after the"
        " on-demand/crontab scans. Select a directory in which the"
        " quarantine will take place if you would like to change."
    )
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.MANDATORY,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.CONFIGURATION,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "/opt/mutablesecurity/clamav/quarantine/"
    GETTER = None
    SETTER = change_quarantine_location


class ScanLocation(BaseInformation):
    IDENTIFIER = "scan_location"
    DESCRIPTION = (
        "The location where the on-demand/crontab scans will take place."
        "Select a different directory if you would like to change."
    )
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.MANDATORY,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.CONFIGURATION,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "/"
    GETTER = None
    SETTER = change_scan_location_or_crontab


class ScanMinute(BaseInformation):
    IDENTIFIER = "scan_minute"
    DESCRIPTION = (
        "The minute (0-59, or * for any) when the crontab scan will take place"
    )
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.CONFIGURATION,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "0"
    GETTER = None
    SETTER = change_scan_location_or_crontab


class ScanHour(BaseInformation):
    IDENTIFIER = "scan_hour"
    DESCRIPTION = (
        "The hour (0-23, or * for any) when the crontab scan will take place"
    )
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.CONFIGURATION,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "0"
    GETTER = None
    SETTER = change_scan_location_or_crontab


class ScanMonth(BaseInformation):
    IDENTIFIER = "scan_month"
    DESCRIPTION = (
        "The month (1-12, JAN-DEC, or * for any) when the crontab scan will"
        " take place"
    )
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.CONFIGURATION,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "*"
    GETTER = None
    SETTER = change_scan_location_or_crontab


class ScanDayOfTheWeek(BaseInformation):
    IDENTIFIER = "scan_day_of_week"
    DESCRIPTION = (
        "The day (0-6, SUN-SAT, 7 for Sunday or * for any) of the week when"
        " the crontab scan will take place"
    )
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.CONFIGURATION,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "MON"
    GETTER = None
    SETTER = change_scan_location_or_crontab


class ScanDayOfTheMonth(BaseInformation):
    IDENTIFIER = "scan_day_of_month"
    DESCRIPTION = (
        "The day (1-31, or * for any) of the month when the crontab scan will"
        " take place"
    )
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.CONFIGURATION,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "*"
    GETTER = None
    SETTER = change_scan_location_or_crontab


class InstalledVersion(BaseInformation):
    class InstalledVersionFact(FactBase):
        command = (
            "apt-cache policy clamav | grep -i Installed | cut -d ' ' -f 4"
        )

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return output[0]

    IDENTIFIER = "version"
    DESCRIPTION = "Installed version"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = InstalledVersionFact
    SETTER = None


class TotalInfectedFiles(BaseInformation):
    class TotalInfectedFilesFact(FactBase):
        @staticmethod
        def command() -> str:
            return (
                f"cat {ScanLogLocation.get()}| grep -oP 'Infected"
                " files:\s+\K\w+' | awk '{T+= $NF} END"  # noqa: W605
                " { print T }'"
            )

        @staticmethod
        def process(output: typing.List[str]) -> int:
            return int(output[0])

    IDENTIFIER = "total_infected_files_detected"
    DESCRIPTION = "Total number of infected files detected overall"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = TotalInfectedFilesFact
    SETTER = None


class DailyInfectedFiles(BaseInformation):
    class DailyInfectedFilesCountFact(FactBase):
        @staticmethod
        def command() -> str:
            current_date = datetime.today().strftime("%Y:%m:%d")

            return (
                f"cat {ScanLogLocation.get()}| grep -B 6 'Start Date:"
                f" {current_date}' | grep 'Infected files' | egrep -o '[0-9]+'"
            )

        @staticmethod
        def process(output: typing.List[str]) -> int:
            temp = [int(elem) for elem in output]
            return sum(temp)

    IDENTIFIER = "daily_infected_files_detected"
    DESCRIPTION = "Total number of infected files detected today"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = DailyInfectedFilesCountFact
    SETTER = None


class UbuntuRequirement(BaseTest):
    IDENTIFIER = "ubuntu"
    DESCRIPTION = "Checks if the operating system is Ubuntu."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = CheckIfUbuntu


class ActiveClamAVDatabase(BaseTest):
    IDENTIFIER = "active_database"
    DESCRIPTION = "Checks if the ClamAV virus database service is active."
    TEST_TYPE = TestType.OPERATIONAL
    FACT = ActiveService
    FACT_ARGS = ("clamav-freshclam",)


class InternetAccess(BaseTest):
    IDENTIFIER = "internet_access"
    DESCRIPTION = "Checks if host has Internet access."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = InternetConnection


class TestScan(BaseTest):
    @staticmethod
    @deploy
    def create_test() -> None:
        files.directory(
            sudo=True,
            name="Creating the test directory in /tmp",
            path="/tmp/clamav_test",  # noqa: S108
            present=True,
        )

        server.shell(
            sudo=True,
            name="Creating the file on which we'll test ClamAV",
            commands=[
                "echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-"  # noqa: W605
                "STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'"
                " > /tmp/clamav_test/test.txt"
            ],
        )

        server.shell(
            sudo=True,
            name=(
                "Running the ClamAV scan with the remove option on the given"
                " directory created"
            ),
            commands=[
                "clamscan --remove"
                f" --log={ScanLogLocation.get()} /tmp/clamav_test"
            ],
            success_exit_codes=[1],
        )

        files.directory(
            sudo=True,
            name="Removing the test directory in /tmp",
            path="/tmp/clamav_test",  # noqa: S108
            present=False,
        )

    class TestScanFact(FactBase):
        @staticmethod
        def command() -> str:
            current_date = datetime.today().strftime("%Y:%m:%d")

            check_command = (
                f"cat {ScanLogLocation.get()} | grep -c '{current_date}' ||"
                " true"
            )

            return check_command

        @staticmethod
        def process(output: typing.List[str]) -> bool:
            return int(output[0]) != 0

    IDENTIFIER = "eicar_detection"
    DESCRIPTION = (
        "Creates a EICAR-STANDARD-ANTIVIRUS-TEST-FILE and checks if ClamAV is"
        " able to detect it."
    )
    TEST_TYPE = TestType.SECURITY
    TRIGGER = create_test
    FACT = TestScanFact


class TextLogs(BaseLog):
    class GeneratedLogsFact(FactBase):
        @staticmethod
        def command() -> str:
            return (
                "cat /var/log/clamav/freshclam.log "
                f" /var/log/clamav/clamav.log {ScanLogLocation.get()} || true"
            )

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return "\n".join(output)

    IDENTIFIER = "logs"
    DESCRIPTION = "The logs generated by ClamAV and FreshClam"
    INFO_TYPE = IntegerDataType
    FACT = GeneratedLogsFact


class StartScan(BaseAction):
    @staticmethod
    @deploy
    def scan_device(scan_location: str) -> None:
        server.shell(
            sudo=True,
            name="Starts the scan with the predifined scan options.",
            commands=[
                "clamscan --recursive"
                f" --log={ScanLogLocation.get()}"
                f" --move={QuarantineLocation.get()} {scan_location}"
            ],
            success_exit_codes=[0, 1],
        )

    IDENTIFIER = "start_scan"
    DESCRIPTION = (
        "Starts the scan containing the predifined scan options: Quarantine"
        " Location and Scan Log Location. Also, it requires the input of Scan"
        " Location."
    )
    ACT = scan_device


class Clamav(BaseSolution):
    INFORMATION = [
        ScanLogLocation,  # type: ignore[list-item, var-annotated]
        QuarantineLocation,  # type: ignore[list-item, var-annotated]
        ScanLocation,  # type: ignore[list-item, var-annotated]
        ScanMinute,  # type: ignore[list-item, var-annotated]
        ScanHour,  # type: ignore[list-item, var-annotated]
        ScanMonth,  # type: ignore[list-item, var-annotated]
        ScanDayOfTheWeek,  # type: ignore[list-item, var-annotated]
        ScanDayOfTheMonth,  # type: ignore[list-item, var-annotated]
        InstalledVersion,  # type: ignore[list-item, var-annotated]
        TotalInfectedFiles,  # type: ignore[list-item, var-annotated]
        DailyInfectedFiles,  # type: ignore[list-item, var-annotated]
    ]
    TESTS = [
        UbuntuRequirement,  # type: ignore[list-item, var-annotated]
        InternetAccess,  # type: ignore[list-item, var-annotated]
        ActiveClamAVDatabase,  # type: ignore[list-item, var-annotated]
        TestScan,  # type: ignore[list-item, var-annotated]
    ]
    LOGS = [TextLogs]  # type: ignore[list-item, var-annotated]
    ACTIONS = [StartScan]  # type: ignore[list-item, var-annotated]

    @staticmethod
    @deploy
    def _install() -> None:
        apt.update(
            sudo=True,
            name="Updates the apt reporisoties",
            env={"LC_TIME": "en_US.UTF-8"},
            cache_time=3600,
            success_exit_codes=[0, 100],
        )

        apt.packages(
            sudo=True,
            name="Installs ClamAV",
            packages=["clamav"],
            latest=True,
            success_exit_codes=[0, 100],
        )

        server.shell(
            sudo=True,
            name="Stopping the service to renew the signature database",
            commands=["systemctl stop clamav-freshclam"],
        )

        server.shell(
            sudo=True,
            name="Renewing the signature database",
            commands=["freshclam"],
        )

        server.shell(
            sudo=True,
            name="Starting the service to renew the signature database",
            commands=["systemctl start clamav-freshclam"],
        )

        files.directory(
            sudo=True,
            name="Creating the default quarantine directory",
            path=f"{QuarantineLocation.get()}",
            present=True,
        )

        files.file(
            sudo=True,
            name=(
                "Creating the logs file and directory with the 400 permissions"
            ),
            path=f"{ScanLogLocation.get()}",
            present=True,
            mode="400",
            create_remote_dir=True,
        )

        files.directory(
            sudo=True,
            name="Creating the test directory in /tmp",
            path="/tmp/clamav_test",  # noqa: S108
            present=True,
        )

        server.shell(
            sudo=True,
            name="Creating the file on which we'll test ClamAV",
            commands=[
                "echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-"  # noqa: W605
                "STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'"
                " > /tmp/clamav_test/test.txt"  # noqa: S108
            ],
        )

        server.shell(
            sudo=True,
            name=(
                "Running the ClamAV scan with the remove option on the given"
                " directory created"
            ),
            commands=[
                "clamscan --remove"
                f" --log={ScanLogLocation.get()} /tmp/clamav_test"
            ],
            success_exit_codes=[1],
        )

        files.directory(
            sudo=True,
            name="Removing the test directory in /tmp",
            path="/tmp/clamav_test",  # noqa: S108
            present=False,
        )

        run_crontab()

    @staticmethod
    @deploy
    def _uninstall() -> None:
        server.shell(
            sudo=True,
            name="Uninstalls ClamAV",
            commands=["apt-get --purge remove -y clamav"],
        )

        server.shell(
            sudo=True,
            name="Running autoremove to clean all leftover files",
            commands=["apt-get -y autoremove"],
        )

        files.file(
            sudo=True,
            name="Removing the configuration file",
            path="/opt/mutablesecurity/clamav/clamav.conf",
            present=False,
        )

        files.directory(
            sudo=True,
            name="Removing the /opt/mutablesecurity/clamav directory",
            path="/opt/mutablesecurity/clamav/",
            present=False,
        )

        files.directory(
            sudo=True,
            name="Removing the /var/log/clamav/ directory",
            path="/var/log/clamav/",
            present=False,
        )

        remove_crontabs_by_part(
            unique_part="clamscan --recursive",
            name="Removes the crontab from the system.",
        )

    @staticmethod
    @deploy
    def _update() -> None:
        class LatestVersionFact(FactBase):
            command = (
                "apt-cache policy clamav | grep -i Candidate | cut -d ' ' -f 4"
            )

            @staticmethod
            def process(output: typing.List[str]) -> str:
                return output[0]

        if host.get_fact(LatestVersionFact) == InstalledVersion.get():
            raise ClamAVAlreadyUpdatedException()

        apt.packages(
            sudo=True,
            name="Updates ClamAV",
            packages=["clamav"],
            latest=True,
            present=True,
        )

        server.shell(
            sudo=True,
            name="Stopping the service to renew the signature database",
            commands=["systemctl stop clamav-freshclam"],
        )

        server.shell(
            sudo=True,
            name="Renewing the signature database",
            commands=["freshclam"],
        )

        server.shell(
            sudo=True,
            name="Starting the service to renew the signature database",
            commands=["systemctl start clamav-freshclam"],
        )
