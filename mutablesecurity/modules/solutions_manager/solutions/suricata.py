from datetime import datetime
from enum import Enum

from humanfriendly import format_timespan
from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, files, python, server

from ..deployments.managed_stats import ManagedStats
from ..deployments.managed_yaml_backed_config import ManagedYAMLBackedConfig
from ..facts.networking import DefaultInterface
from . import AbstractSolution


class AutomaticUpdates(Enum):
    ENABLED = True
    DISABLED = False

    def __str__(self):
        return self.name

    @classmethod
    def from_str(cls, name):
        return cls[name]


class AlertsCount(FactBase):
    command = "cat /var/log/suricata/fast.log | wc -l"

    def process(self, output):
        return int(output[0])


class TestAlertsCount(FactBase):
    def command(self):
        current_date = datetime.today().strftime("%m/%d/%Y-%H:%M")

        return f"tail -n 1 /var/log/suricata/fast.log | grep '{current_date}' | grep -c '1:2100498:7' || true"

    def process(self, output):
        return int(output[0])


class DailyAlertsCount(FactBase):
    def command(self):
        current_date = datetime.today().strftime("%m/%d/%Y")

        return f"cat /var/log/suricata/fast.log | grep '{current_date}' | wc -l"

    def process(self, output):
        return int(output[0])


class Uptime(FactBase):
    command = "suricatasc -c uptime | jq '.message'"

    def process(self, output):
        return format_timespan(int(output[0]))


class Version(FactBase):
    command = "suricatasc -c version | jq -r '.message'"

    def process(self, output):
        return output[0]


class Logs(FactBase):
    command = "cat /var/log/suricata/fast.log"

    def process(self, output):
        return output


class Suricata(AbstractSolution):
    meta = {
        "id": "suricata",
        "full_name": "Suricata Intrusion Detection and Prevention System",
        "description": "Suricata is the leading independent open source threat detection engine. By combining intrusion detection (IDS), intrusion prevention (IPS), network security monitoring (NSM) and PCAP processing, Suricata can quickly identify, stop, and assess even the most sophisticated attacks.",
        "references": ["https://suricata.io", "https://github.com/OISF/suricata"],
        "configuration": {
            "interface": {
                "type": str,
                "help": "Interface on which Suricata listens",
                "default": "eth0",
            },
            "automatic_updates": {
                "type": AutomaticUpdates,
                "help": "State of the automatic daily updates",
                "default": AutomaticUpdates.DISABLED,
            },
        },
        "metrics": {
            "total_alerts": {
                "description": "Total number of alerts",
                "fact": AlertsCount,
            },
            "today_alerts": {
                "description": "Total number of alerts generated today",
                "fact": DailyAlertsCount,
            },
            "uptime": {"description": "Uptime", "fact": Uptime},
            "version": {"description": "Current installed version", "fact": Version},
        },
        "messages": {
            "GET_CONFIGURATION": (
                "The configuration of Suricata was retrieved.",
                "The configuration of Suricata could not be retrieved.",
            ),
            "SET_CONFIGURATION": (
                "The configuration of Suricata was set.",
                "The configuration of Suricata could not be set. Check the provided aspect and value to be valid.",
            ),
            "INSTALL": (
                "Suricata is now installed on this machine.",
                "There was an error on Suricata's installation.",
            ),
            "TEST": (
                "Suricata works as expected.",
                "Suricata does not work as expected.",
            ),
            "GET_LOGS": (
                "The logs of Suricata were retrieved.",
                "The logs of Suricata could not be retrieved.",
            ),
            "GET_STATS": (
                "The stats of Suricata were retrieved.",
                "The stats of Suricata could not be retrieved.",
            ),
            "UPDATE": (
                "Suricata is now at its newest version.",
                "There was an error on Suricata's update.",
            ),
            "UNINSTALL": (
                "Suricata is no longer installed on this machine.",
                "There was an error on Suricata's uninstallation.",
            ),
        },
    }
    result = {}

    @deploy
    def get_configuration(state, host):
        ManagedYAMLBackedConfig.get_configuration(
            state=state, host=host, solution_class=Suricata
        )

    @deploy
    def _set_default_configuration(state, host):
        ManagedYAMLBackedConfig._set_default_configuration(
            state=state, host=host, solution_class=Suricata
        )

    @deploy
    def _verify_new_configuration(state, host, aspect, value):
        ManagedYAMLBackedConfig._verify_new_configuration(
            state=state, host=host, solution_class=Suricata, aspect=aspect, value=value
        )

    @deploy
    def set_configuration(state, host, aspect=None, value=None):
        ManagedYAMLBackedConfig.set_configuration(
            state=state, host=host, solution_class=Suricata, aspect=aspect, value=value
        )

    @deploy
    def _set_configuration_callback(
        state, host, aspect=None, old_value=None, new_value=None
    ):
        # Perform post-setting operations, based on the set configuration
        if aspect == "automatic_updates":
            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Adds a crontab to automatically update the Suricata's rules",
                command="suricata-update",
                present=Suricata._configuration["automatic_updates"],
                hour=0,
                minute=0,
            )
        elif aspect == "interface":
            files.replace(
                state=state,
                host=host,
                sudo=True,
                name="Replaces the default interface in the Suricata's configuration file",
                path="/etc/suricata/suricata.yaml",
                match=r"  - interface: [\"a-zA-Z0-9]*$",
                replace=f"  - interface: {Suricata._configuration['interface']}",
            )

            server.shell(
                state=state,
                host=host,
                sudo=True,
                name="Starts the Suricata service",
                commands=["service suricata restart"],
            )

    @deploy
    def _put_configuration(state, host):
        ManagedYAMLBackedConfig._put_configuration(
            state=state, host=host, solution_class=Suricata
        )

    @deploy
    def install(state, host):
        Suricata._set_default_configuration(state=state, host=host)

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
            name="Installs the requirements",
            packages=["software-properties-common", "jq", "tmux", "moreutils"],
            latest=True,
        )

        apt.ppa(
            state=state,
            host=host,
            sudo=True,
            name="Adds the Suricata's repository",
            src="ppa:oisf/suricata-stable",
        )

        apt.update(
            state=state,
            host=host,
            sudo=True,
            name="Updates the apt reporisoties",
            cache_time=3600,
            success_exit_codes=[0, 100],
        )

        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Installs Suricata",
            packages=["suricata"],
            latest=True,
            success_exit_codes=[0, 100],
        )

        Suricata._configuration["interface"] = host.get_fact(DefaultInterface)

        files.replace(
            state=state,
            host=host,
            sudo=True,
            name="Replaces the default interface in the Suricata's configuration file",
            path="/etc/suricata/suricata.yaml",
            match=r"  - interface: [\"a-zA-Z0-9]*$",
            replace=f"  - interface: {Suricata._configuration['interface']}",
        )

        files.replace(
            state=state,
            host=host,
            sudo=True,
            name="Replaces the default rules location in the Suricata's configuration file",
            path="/etc/suricata/suricata.yaml",
            match=r"^default-rule-path: /etc/suricata/rules$",
            replace="default-rule-path: /var/lib/suricata/rules",
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Updates the Suricata's rules",
            commands=["suricata-update"],
        )

        # Restart the Suricata service as it starts at install but fails if the
        # default interface is not eth0.
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Restart the Suricata service",
            commands=["service suricata restart"],
        )

        Suricata._put_configuration(state=state, host=host)

        Suricata.result[host.name] = True

    @deploy
    def test(state, host):
        Suricata.get_configuration(state=state, host=host)

        curl_command = "wget -O /tmp/index.html http://testmynids.org/uid/index.html"
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Requests a malicious-marked URL",
            commands=[curl_command],
        )

        def stage(state, host):
            # This verification will check if the last alert is one related to the
            # request above.
            alerts = host.get_fact(TestAlertsCount)

            Suricata.result[host.name] = alerts != 0

        python.call(state=state, host=host, sudo=True, function=stage)

    @deploy
    def get_stats(state, host):
        ManagedStats.get_stats(state=state, host=host, solution_class=Suricata)

    @deploy
    def get_logs(state, host):
        Suricata.get_configuration(state=state, host=host)

        Suricata.result[host.name] = host.get_fact(Logs)

    @deploy
    def update(state, host):
        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Updates Suricata",
            packages=["suricata"],
            latest=True,
            present=True,
        )

        Suricata.result[host.name] = True

    @deploy
    def uninstall(state, host):
        Suricata.get_configuration(state=state, host=host)

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Uninstalls Suricata",
            commands=["tmux new -d 'apt -y remove suricata'"],
        )

        Suricata.result[host.name] = True
