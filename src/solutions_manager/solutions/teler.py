import json
import os
from datetime import datetime

from packaging import version
from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, files, python, server

from ...helpers.github import GitHub
from ..deployments.managed_stats import ManagedStats
from ..deployments.managed_yaml_backed_config import ManagedYAMLBackedConfig
from . import AbstractSolution


class AlertsCount(FactBase):
    command = "cat /var/log/teler.log | wc -l"

    def process(self, output):
        return int(output[0])


class DailyAlertsCount(FactBase):
    def command(self):
        current_date = datetime.today().strftime("%d/%b/%Y")

        return f"cat /var/log/teler.log | grep '{current_date}' | wc -l"

    def process(self, output):
        return int(output[0])


class TopAttacksTypes(FactBase):
    command = "cat /var/log/teler.log | jq -s '.' | jq  'group_by (.category)[] | {type: .[0].category, occurances: length}' | jq -s | jq -S . | jq 'sort_by(.occurances) | reverse | .[0:3]'"

    def process(self, output):
        attacks_types = json.loads("".join(output))

        return ", ".join(
            [
                f"{attacks_type['type']} ({attacks_type['occurances']})"
                for attacks_type in attacks_types
            ]
        )


class TopAttackers(FactBase):
    command = "cat /var/log/teler.log | jq -s '.' | jq  'group_by (.remote_addr)[] | {attacker: .[0].remote_addr, occurances: length}' | jq -s | jq -S . | jq 'sort_by(.occurances) | reverse | .[0:3]'"

    def process(self, output):
        attackers = json.loads("".join(output))

        return ", ".join(
            [
                f"{attacker['attacker']} ({attacker['occurances']})"
                for attacker in attackers
            ]
        )


class Version(FactBase):
    # Teler returns the major version as an exit code
    command = "/opt/teler/teler -v || true"

    def process(self, output):
        return output[0].split()[1]


class Logs(FactBase):
    command = "cat /var/log/teler.log"

    def process(self, output):
        return output


class TestBadUserAgent(FactBase):
    def command(self):
        current_date = datetime.today().strftime("%d/%b/%Y:%H:%M")

        string = f'cat /var/log/teler.log | jq \'select((.http_user_agent == "curl x MutableSecurity") and (.time_local | startswith("{current_date}")))\' | wc -l'

        return string

    def process(self, output):
        return int(output[0]) != 0


class Teler(AbstractSolution):
    meta = {
        "id": "teler",
        "full_name": "teler Real-time HTTP Intrusion Detection",
        "description": "teler is an real-time intrusion detection and threat alert based on web log.",
        "references": ["https://github.com/kitabisa/teler"],
        "configuration": {
            "port": {
                "type": int,
                "help": "Port on which the server listens",
                "default": 80,
            },
            "log_location": {
                "type": str,
                "help": "Location in which the server generates its logs",
                "default": "/var/log/nginx/access.log",
            },
            "log_format": {
                "type": str,
                "help": "Format for parsing the server's log messages",
                "default": '$remote_addr $remote_user - [$time_local] "$request_method $request_uri $request_protocol" $status $body_bytes_sent "$http_referer" "$http_user_agent"',
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
            "top_alerts_types": {
                "description": "Top 3 most common alerts types",
                "fact": TopAttacksTypes,
            },
            "top_attackers": {
                "description": "Top 3 attackers",
                "fact": TopAttackers,
            },
            "version": {"description": "Current installed version", "fact": Version},
        },
        "messages": {
            "GET_CONFIGURATION": (
                "The configuration of teler was retrieved.",
                "The configuration of teler could not be retrieved.",
            ),
            "SET_CONFIGURATION": (
                "The configuration of teler was set.",
                "The configuration of teler could not be set. Check the provided aspect and value to be valid.",
            ),
            "INSTALL": (
                "teler is now installed on this machine.",
                "There was an error on teler's installation.",
            ),
            "TEST": (
                "teler works as expected.",
                "teler does not work as expected.",
            ),
            "GET_LOGS": (
                "The logs of teler were retrieved.",
                "The logs of teler could not be retrieved.",
            ),
            "GET_STATS": (
                "The stats of teler were retrieved.",
                "The stats of teler could not be retrieved.",
            ),
            "UPDATE": (
                "teler is now at its newest version.",
                "There was an error on teler's update.",
            ),
            "UNINSTALL": (
                "teler is no longer installed on this machine.",
                "There was an error on teler's uninstallation.",
            ),
        },
    }
    result = {}

    @deploy
    def get_configuration(state, host):
        ManagedYAMLBackedConfig.get_configuration(
            state=state, host=host, solution_class=Teler
        )

    @deploy
    def _set_default_configuration(state, host):
        ManagedYAMLBackedConfig._set_default_configuration(
            state=state, host=host, solution_class=Teler
        )

    @deploy
    def _verify_new_configuration(state, host, aspect, value):
        ManagedYAMLBackedConfig._verify_new_configuration(
            state=state, host=host, solution_class=Teler, aspect=aspect, value=value
        )

    @deploy
    def set_configuration(state, host, aspect=None, value=None):
        ManagedYAMLBackedConfig.set_configuration(
            state=state, host=host, solution_class=Teler, aspect=aspect, value=value
        )

    @deploy
    def _set_configuration_callback(
        state, host, aspect=None, old_value=None, new_value=None
    ):
        if aspect != "log_location" and aspect != "log_format":
            return

        # Kill the teler instance
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Kills the teler process",
            commands=["killall -9 /opt/teler/teler || true"],
        )

        teler_command = f"tail -f {Teler._configuration['log_location']} | /opt/teler/teler -c /opt/teler/teler.conf"
        if aspect == "log_location":
            # Removes the old crontab
            old_teler_command = (
                f"tail -f {old_value} | /opt/teler/teler -c /opt/teler/teler.conf"
            )
            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Removes the old crontab",
                command=old_teler_command,
                present=False,
                special_time="@reboot",
            )

            # Adds a new crontab
            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Adds a crontab to automatically run teler",
                command=teler_command,
                present=True,
                special_time="@reboot",
            )
        elif aspect == "log_format":
            server.shell(
                state=state,
                host=host,
                sudo=True,
                name="Kills the teler process",
                commands=["killall -9 /opt/teler/teler || true"],
            )

            # Regenerate and upload the new teler configuration
            j2_configuration = {"log_format": Teler._configuration["log_format"]}
            files.template(
                state=state,
                host=host,
                sudo=True,
                name="Copy the regenerated configuration file",
                src=os.path.dirname(__file__) + "/../files/teler/teler.conf.j2",
                dest="/opt/teler/teler.conf",
                configuration=j2_configuration,
            )

        # Restarts teler
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Run teler without restart",
            commands=[f"tmux new -d '{teler_command}'"],
        )

    @deploy
    def _put_configuration(state, host):
        ManagedYAMLBackedConfig._put_configuration(
            state=state, host=host, solution_class=Teler
        )

    @deploy
    def install(state, host):
        Teler._set_default_configuration(state=state, host=host)

        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Installs the requirements",
            packages=["jq", "tmux"],
            latest=True,
        )

        # Get the latest release
        release_url = GitHub.get_asset_from_latest_release(
            "kitabisa", "teler", "linux_amd64"
        )
        wget_command = f"wget -O /tmp/teler.tar.gz {release_url}"
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Downloads the latest release",
            commands=[wget_command],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Unarchives the binaries",
            commands=["tar -xzf /tmp/teler.tar.gz"],
        )

        files.directory(
            state=state,
            host=host,
            sudo=True,
            name="Creates a home for teler",
            path="/opt/teler",
            present=True,
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Moves the binary into teler's home",
            commands=["cp teler /opt/teler/teler"],
        )

        j2_configuration = {"log_format": Teler._configuration["log_format"]}
        files.template(
            state=state,
            host=host,
            sudo=True,
            name="Copy the default configuration file",
            src=os.path.dirname(__file__) + "/../files/teler/teler.conf.j2",
            dest="/opt/teler/teler.conf",
            configuration=j2_configuration,
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Creates the log file",
            commands=["touch /var/log/teler.log"],
        )

        teler_command = f"tail -f {Teler._configuration['log_location']} | /opt/teler/teler -c /opt/teler/teler.conf"
        server.crontab(
            state=state,
            host=host,
            sudo=True,
            name="Adds a crontab to automatically run the binary",
            command=teler_command,
            present=True,
            special_time="@reboot",
        )
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Run the binary now, without a restart to trigger the crontab",
            commands=[f"tmux new -d '{teler_command}'"],
        )

        Teler._put_configuration(state=state, host=host)

        Teler.result[host.name] = True

    @deploy
    def test(state, host):
        Teler.get_configuration(state=state, host=host)

        url = "http://localhost:" + str(Teler._configuration["port"])
        wget_command = (
            "wget --header 'User-Agent: curl x MutableSecurity' -O /tmp/index.html "
            + url
        )
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Requests the website with a bad user agent",
            commands=[wget_command],
        )

        def stage(state, host):
            # This verification will check if the last alert is one related to the
            # request above.
            alerts = host.get_fact(TestBadUserAgent)

            Teler.result[host.name] = alerts != 0
            host.get_fact(Logs)

        python.call(state=state, host=host, sudo=True, function=stage)

    @deploy
    def get_stats(state, host):
        ManagedStats.get_stats(state=state, host=host, solution_class=Teler)

    @deploy
    def get_logs(state, host):
        Teler.get_configuration(state=state, host=host)

        Teler.result[host.name] = host.get_fact(Logs)

    @deploy
    def update(state, host):
        # Check if the latest release has a greater version than the local
        # software
        local_version = host.get_fact(Version)
        github_latest_version = GitHub.get_latest_release_name("kitabisa", "teler")
        if version.parse(local_version) == version.parse(github_latest_version):
            Teler.result[host.name] = True

            return

        # If the version on GitHub is greater, then update the software
        Teler.uninstall(state=state, host=host)
        Teler.install(state=state, host=host)

    @deploy
    def uninstall(state, host):
        Teler.get_configuration(state=state, host=host)

        # Kill the teler instance
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Kills the teler process",
            commands=["killall -9 /opt/teler/teler || true"],
        )

        teler_command = f"tail -f {Teler._configuration['log_location']} | /opt/teler/teler -c /opt/teler/teler.conf"
        server.crontab(
            state=state,
            host=host,
            sudo=True,
            name="Removes the crontab to automatically run teler",
            command=teler_command,
            present=False,
            special_time="@reboot",
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Kills the teler process",
            commands=["killall -9 /opt/teler/teler || true"],
        )

        files.directory(
            state=state,
            host=host,
            sudo=True,
            name="Removes the teler executable and configuration",
            path="/opt/teler",
            present=False,
        )

        files.file(
            state=state,
            host=host,
            sudo=True,
            name="Removes the teler log file",
            path="/var/log/teler.log",
            present=False,
        )

        Teler.result[host.name] = True
