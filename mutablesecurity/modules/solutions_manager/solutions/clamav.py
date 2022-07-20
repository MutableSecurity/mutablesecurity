from datetime import datetime

from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, files, python, server

from ..deployments.managed_stats import ManagedStats
from ..deployments.managed_yaml_backed_config import ManagedYAMLBackedConfig
from . import AbstractSolution


class InfectedFilesCount(FactBase):
    def command(self):
        return (
            f"cat {ClamAV._configuration['logs']}"
            "| grep -oP 'Infected files:\s+\K\w+' | awk '{T+= $NF} END { print T }'"
        )

    def process(self, output):
        return int(output[0])


class TestInfectedFiles(FactBase):
    def command(self):
        current_date = datetime.today().strftime("%Y:%m:%d")

        return f"cat {ClamAV._configuration['logs']} | grep -c '{current_date}' || true"

    def process(self, output):
        return int(output[0])


class DailyInfectedFilesCount(FactBase):
    def command(self):
        current_date = datetime.today().strftime("%Y:%m:%d")
        return f"cat {ClamAV._configuration['logs']}| grep -B 6 'Start Date: {current_date}' | grep 'Infected files' | egrep -o '[0-9]+'"

    def process(self, output):
        temp = [int(elem) for elem in output]
        return sum(temp)


class Version(FactBase):
    command = "clamscan --version"

    def process(self, output):
        return output[0]


class Logs(FactBase):
    def command(self):
        return f"cat /var/log/clamav/freshclam.log  /var/log/clamav/clamav.log {ClamAV._configuration['logs']}"

    def process(self, output):
        return output


class ClamAV(AbstractSolution):
    meta = {
        "id": "clamav",
        "full_name": "Clam AntiVirus (ClamAV)",
        "description": "ClamAV is an open source (GPLv2) anti-virus toolkit, designed especially for e-mail scanning on mail gateways. It provides a number of utilities including a flexible and scalable multi-threaded daemon, a command line scanner and advanced tool for automatic database updates. The core of the package is an anti-virus engine available in a form of shared library.",
        "references": [
            "https://www.clamav.net/",
            "https://github.com/Cisco-Talos/clamav",
            "https://docs.clamav.net/Introduction.html",
        ],
        "configuration": {
            "logs": {
                "type": str,
                "help": "The location of the generated logs after the on-demand/crontab scans. Please chose a file in which the logs will be stored if you wish to change.",
                "default": "/opt/mutablesecurity/clamav/logs/logs.txt",
            },
            "quarantine": {
                "type": str,
                "help": "The location where the infected files will be moved to after the on-demand/crontab scans. Please select a directory in which the quarantine will take place if you wish to change.",
                "default": "/opt/mutablesecurity/clamav/quarantine/",
            },
            "scan_location": {
                "type": str,
                "help": "The location where the on-demand/crontab scans will take place. Please select a directory you wish to scan if you wish to change it.",
                "default": "/home",
            },
            "scan_minute": {
                "type": str,
                "help": "The minute when the crontab scan will take place. (0-59, or * for any)",
                "default": "0",
            },
            "scan_hour": {
                "type": str,
                "help": "The hour when the crontab scan will take place. (0-23, or * for any)",
                "default": "5",
            },
            "scan_month": {
                "type": str,
                "help": "The month when the crontab scan will take place. (1-12, JAN-DEC, or * for any)",
                "default": "*",
            },
            "scan_day_of_week": {
                "type": str,
                "help": "The day of the week when the crontab scan will take place. (0-6, SUN-SAT, 7 for sunday or * for any)",
                "default": "*",
            },
            "scan_day_of_month": {
                "type": str,
                "help": "The day of the month when the crontab scan will take place. (1-31, or * for any)",
                "default": "*",
            },
        },
        "metrics": {
            "total_infected_files": {
                "description": "Total number of infected files detected and deleted/quarantined",
                "fact": InfectedFilesCount,
            },
            "today_infected_files": {
                "description": "Total number of infected files detected today and deleted/quarantined",
                "fact": DailyInfectedFilesCount,
            },
            "version": {"description": "Current installed version", "fact": Version},
        },
        "messages": {
            "GET_CONFIGURATION": (
                "The configuration of ClamAV was retrieved.",
                "The configuration of ClamAV could not be retrieved.",
            ),
            "SET_CONFIGURATION": (
                "The configuration of ClamAV was set.",
                "The configuration of ClamAV could not be set. Check the provided aspect and value to be valid.",
            ),
            "INSTALL": (
                "ClamAV is now installed on this machine.",
                "There was an error on ClamAV's installation.",
            ),
            "TEST": (
                "ClamAV works as expected.",
                "ClamAV does not work as expected.",
            ),
            "GET_LOGS": (
                "The logs of ClamAV were retrieved.",
                "The logs of ClamAV could not be retrieved.",
            ),
            "GET_STATS": (
                "The stats of ClamAV were retrieved.",
                "The stats of ClamAV could not be retrieved.",
            ),
            "UPDATE": (
                "ClamAV is now at its newest version.",
                "There was an error on ClamAV's update.",
            ),
            "UNINSTALL": (
                "ClamAV is no longer installed on this machine.",
                "There was an error on ClamAV's uninstallation.",
            ),
        },
    }
    result = {}

    @deploy
    def get_configuration(state, host):
        ManagedYAMLBackedConfig.get_configuration(
            state=state, host=host, solution_class=ClamAV
        )

    @deploy
    def _set_default_configuration(state, host):
        ManagedYAMLBackedConfig._set_default_configuration(
            state=state, host=host, solution_class=ClamAV
        )

    @deploy
    def _verify_new_configuration(state, host, aspect, value):
        ManagedYAMLBackedConfig._verify_new_configuration(
            state=state, host=host, solution_class=ClamAV, aspect=aspect, value=value
        )

    @deploy
    def set_configuration(state, host, aspect=None, value=None):
        ManagedYAMLBackedConfig.set_configuration(
            state=state, host=host, solution_class=ClamAV, aspect=aspect, value=value
        )

    @deploy
    def _set_configuration_callback(
        state, host, aspect=None, old_value=None, new_value=None
    ):
        # Perform post-setting operations, based on the set configuration
        if aspect == "logs":
            temp = old_value

            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Removing the old crontab with the old logs location",
                command=f"clamscan --recursive --log={temp} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=False,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )
            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Adding the new crontab with the new logs location",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=True,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )

            files.file(
                state=state,
                host=host,
                sudo=True,
                name="Creating the new logs file and directory with the 400 permissions",
                path=f"{ClamAV._configuration['logs']}",
                present=True,
                mode="400",
                create_remote_dir=True,
            )

        elif aspect == "quarantine":

            temp = old_value

            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Removing the old crontab with the old quarantine location",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={temp} {ClamAV._configuration['scan_location']}",
                present=False,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )
            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Adding the new crontab with the new quarantine location",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=True,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )

            files.directory(
                state=state,
                host=host,
                sudo=True,
                name="Creating the new quarantine directory",
                path=f"{ClamAV._configuration['quarantine']}",
                present=True,
            )

        elif aspect == "scan_location":
            temp = old_value

            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Removing the old crontab with the old scan location",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {temp}",
                present=False,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )
            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Adding the new crontab with the new scan location",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=True,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )

        elif aspect == "scan_minute":
            temp = old_value

            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Removing the old crontab with the old scan minute",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=False,
                minute=f"{temp}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )
            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Adding the new crontab with the new scan minute",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=True,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )
        elif aspect == "scan_hour":
            temp = old_value

            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Removing the old crontab with the old scan hour",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=False,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{temp}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )
            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Adding the new crontab with the new scan hour",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=True,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )
        elif aspect == "scan_month":
            temp = old_value

            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Removing the old crontab with the old scan month",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=False,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{temp}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )
            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Adding the new crontab with the new scan month",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=True,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )
        elif aspect == "scan_day_of_week":
            temp = old_value

            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Removing the old crontab with the old scan day of the week",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=False,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{temp}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )
            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Adding the new crontab with the new scan day of the week",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=True,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )
        elif aspect == "scan_day_of_month":
            temp = old_value

            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Removing the old crontab with the old scan day of the month",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=False,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{temp}",
            )
            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Adding the new crontab with the new scan day of the month",
                command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
                present=True,
                minute=f"{ClamAV._configuration['scan_minute']}",
                hour=f"{ClamAV._configuration['scan_hour']}",
                month=f"{ClamAV._configuration['scan_month']}",
                day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
                day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
            )

    @deploy
    def _put_configuration(state, host):
        ManagedYAMLBackedConfig._put_configuration(
            state=state, host=host, solution_class=ClamAV
        )

    @deploy
    def install(state, host):
        ClamAV._set_default_configuration(state=state, host=host)
        ClamAV._put_configuration(state=state, host=host)

        apt.update(
            state=state,
            host=host,
            sudo=True,
            name="Updates the apt reporisoties",
            env={"LC_TIME": "en_US.UTF-8"},
            cache_time=3600,
            success_exit_codes=[0, 100],
        )

        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Installs ClamAV",
            packages=["clamav", "clamav-daemon"],
            latest=True,
            success_exit_codes=[0, 100],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Stopping the service to renew the signature database",
            commands=["systemctl stop clamav-freshclam"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Renewing the signature database",
            commands=["freshclam"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Starting the service to renew the signature database",
            commands=["systemctl start clamav-freshclam"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Enabling the clamav-daemon",
            commands=["systemctl enable clamav-daemon"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Starting the clamav-daemon",
            commands=["systemctl start clamav-daemon"],
        )

        files.directory(
            state=state,
            host=host,
            sudo=True,
            name="Creating the default quarantine directory",
            path=f"{ClamAV._configuration['quarantine']}",
            present=True,
        )

        files.file(
            state=state,
            host=host,
            sudo=True,
            name="Creating the logs file and directory with the 400 permissions",
            path=f"{ClamAV._configuration['logs']}",
            present=True,
            mode="400",
            create_remote_dir=True,
        )

        server.crontab(
            state=state,
            host=host,
            sudo=True,
            name="Adds a crontab to automatically scan the /home directory recursively each day at 5 am",
            command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
            present=True,
            minute=f"{ClamAV._configuration['scan_minute']}",
            hour=f"{ClamAV._configuration['scan_hour']}",
            month=f"{ClamAV._configuration['scan_month']}",
            day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
            day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
        )

        ClamAV._put_configuration(state=state, host=host)

        ClamAV.result[host.name] = True

    @deploy
    def test(state, host):
        ClamAV.get_configuration(state=state, host=host)

        files.directory(
            state=state,
            host=host,
            sudo=True,
            name="Creating the test directory in /tmp",
            path="/tmp/clamav_test",
            present=True,
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Creating the file on which we'll test ClamAV",
            commands=[
                "echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > /tmp/clamav_test/test.txt"
            ],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Running the ClamAV scan with the remove option on the given directory created",
            commands=[
                f"clamscan --remove --log={ClamAV._configuration['logs']} /tmp/clamav_test"
            ],
            success_exit_codes=[1],
        )

        files.directory(
            state=state,
            host=host,
            sudo=True,
            name="Removing the test directory in /tmp",
            path="/tmp/clamav_test",
            present=False,
        )

        def stage(state, host):
            # This verification will check if the last alert is one related to the
            # request above.
            infected_files = host.get_fact(TestInfectedFiles)

            ClamAV.result[host.name] = infected_files != 0

        python.call(state=state, host=host, sudo=True, function=stage)

    @deploy
    def get_stats(state, host):
        ManagedStats.get_stats(state=state, host=host, solution_class=ClamAV)

    @deploy
    def get_logs(state, host):
        ClamAV.get_configuration(state=state, host=host)

        ClamAV.result[host.name] = host.get_fact(Logs)

    @deploy
    def update(state, host):
        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Updates ClamAV",
            packages=["clamav", "clamav-daemon"],
            latest=True,
            present=True,
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Stopping the service to renew the signature database",
            commands=["systemctl stop clamav-freshclam"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Renewing the signature database",
            commands=["freshclam"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Starting the service to renew the signature database",
            commands=["systemctl start clamav-freshclam"],
        )

        ClamAV.result[host.name] = True

    @deploy
    def uninstall(state, host):
        ClamAV.get_configuration(state=state, host=host)

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Uninstalls ClamAV",
            commands=["apt-get --purge remove -y clamav clamav-daemon"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Running autoremove to clean all leftover files",
            commands=["apt-get -y autoremove"],
        )

        files.file(
            state=state,
            host=host,
            sudo=True,
            name="Removing the configuration file",
            path="/opt/mutablesecurity/clamav/clamav.conf",
            present=False,
        )

        files.directory(
            state=state,
            host=host,
            sudo=True,
            name="Removing the /opt/mutablesecurity/clamav directory",
            path="/opt/mutablesecurity/clamav/",
            present=False,
        )

        files.directory(
            state=state,
            host=host,
            sudo=True,
            name="Removing the /var/log/clamav/ directory",
            path="/var/log/clamav/",
            present=False,
        )

        server.crontab(
            state=state,
            host=host,
            sudo=True,
            name="Removing the created crontab",
            command=f"clamscan --recursive --log={ClamAV._configuration['logs']} --move={ClamAV._configuration['quarantine']} {ClamAV._configuration['scan_location']}",
            present=False,
            minute=f"{ClamAV._configuration['scan_minute']}",
            hour=f"{ClamAV._configuration['scan_hour']}",
            month=f"{ClamAV._configuration['scan_month']}",
            day_of_week=f"{ClamAV._configuration['scan_day_of_week']}",
            day_of_month=f"{ClamAV._configuration['scan_day_of_month']}",
        )

        ClamAV.result[host.name] = True
