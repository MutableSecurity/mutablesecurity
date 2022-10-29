import re
from enum import Enum

from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, files, server, systemd

from ...exceptions import MutableSecurityException
from ..deployments.managed_stats import ManagedStats
from ..deployments.managed_yaml_backed_config import ManagedYAMLBackedConfig
from . import AbstractSolution


class AgentRegistrationWithPassword(Enum):
    ENABLED = True
    DISABLED = False

    def __str__(self):
        return self.name

    @classmethod
    def from_str(cls, name):
        return cls[name]


class Version(FactBase):
    command = "/var/ossec/bin/wazuh-control info | grep -oP 'WAZUH_VERSION.*'"

    def process(self, output):
        return re.search('WAZUH_VERSION="(.*)"', output[0]).group(1)


class Logs(FactBase):
    command = "cat /var/ossec/logs/ossec.json"

    def process(self, output):
        return output


class ConnectionWithManager(FactBase):
    def command(self):
        return f"ss -te | grep -c '{WazuhAgent._configuration['manager_ip']}:1514'"

    def process(self, output):
        return bool(output[0])


class WazuhAgent(AbstractSolution):
    meta = {
        "id": "wazuh_agent",
        "full_name": "Wazuh Agent",
        "description": "Wazuh is an unified XDR and SIEM protection for endpoint and cloud workloads. The Wazuh agent run on the monitored endpoints and continuously sends events to the Wazuh server for analysis and threat detection.",
        "references": ["https://wazuh.com", "https://github.com/wazuh/wazuh"],
        "configuration": {
            "name": {
                "type": str,
                "help": "Name identifying the agent",
                "default": None,
            },
            "manager_ip": {
                "type": str,
                "help": "IP Address of Wazuh Manager",
                "default": None,
            },
            "registration_with_password": {
                "type": AgentRegistrationWithPassword,
                "help": "Boolean indicating if the agent needs to register with a password",
                "default": AgentRegistrationWithPassword.ENABLED,
            },
            "registration_password": {
                "type": str,
                "help": "Password for registration",
                "default": None,
            },
        },
        "metrics": {
            "version": {"description": "Current installed version", "fact": Version},
        },
        "messages": {
            "GET_CONFIGURATION": (
                "The configuration of Wazuh was retrieved.",
                "The configuration of Wazuh could not be retrieved.",
            ),
            "SET_CONFIGURATION": (
                "The configuration of Wazuh was set.",
                "The configuration of Wazuh could not be set. Check the provided aspect and value to be valid.",
            ),
            "INSTALL": (
                "Wazuh is now installed on this machine.",
                "There was an error on Wazuh's installation.",
            ),
            "TEST": (
                "Wazuh works as expected.",
                "Wazuh does not work as expected.",
            ),
            "GET_LOGS": (
                "The logs of Wazuh were retrieved.",
                "The logs of Wazuh could not be retrieved.",
            ),
            "GET_STATS": (
                "The stats of Wazuh were retrieved.",
                "The stats of Wazuh could not be retrieved.",
            ),
            "UPDATE": (
                "Wazuh is now at its newest version.",
                "There was an error on Wazuh's update.",
            ),
            "UNINSTALL": (
                "Wazuh is no longer installed on this machine.",
                "There was an error on Wazuh's uninstallation.",
            ),
        },
    }
    result = {}

    @deploy
    def get_configuration(state, host):
        ManagedYAMLBackedConfig.get_configuration(
            state=state, host=host, solution_class=WazuhAgent
        )

    @deploy
    def _set_default_configuration(state, host):
        ManagedYAMLBackedConfig._set_default_configuration(
            state=state, host=host, solution_class=WazuhAgent
        )

    @deploy
    def _verify_new_configuration(state, host, aspect, value):
        ManagedYAMLBackedConfig._verify_new_configuration(
            state=state,
            host=host,
            solution_class=WazuhAgent,
            aspect=aspect,
            value=value,
        )

    @deploy
    def set_configuration(state, host, aspect=None, value=None):
        ManagedYAMLBackedConfig.set_configuration(
            state=state,
            host=host,
            solution_class=WazuhAgent,
            aspect=aspect,
            value=value,
        )

    @deploy
    def _set_configuration_callback(
        state, host, aspect=None, old_value=None, new_value=None
    ):
        # If the registration strategy changes, then the agent has no change as
        # it will be registered after (before installation) or already
        # registered in Manager (after installation).
        if aspect != "registration_with_password":
            try:
                WazuhAgent._check_installation_config(state=state, host=host)

                if aspect == "manager_ip":
                    WazuhAgent.__set_manager_ip_ossec_conf(state=state, host=host)
            except MutableSecurityException:
                pass
            else:
                WazuhAgent.__register_to_manager(state=state, host=host)
                WazuhAgent.__reload_service(state=state, host=host)

    @deploy
    def _put_configuration(state, host):
        ManagedYAMLBackedConfig._put_configuration(
            state=state, host=host, solution_class=WazuhAgent
        )

    @deploy
    def _check_installation_config(state, host):
        ManagedYAMLBackedConfig._check_installation_config(
            state=state, host=host, solution_class=WazuhAgent
        )

    @deploy
    def __set_manager_ip_ossec_conf(state, host):
        files.replace(
            state=state,
            host=host,
            sudo=True,
            name="Replaces the logging format",
            path="/var/ossec/etc/ossec.conf",
            match=r"^      <address>MANAGER_IP</address>$",
            replace=f"      <address>{WazuhAgent._configuration['manager_ip']}</address>",
        )

    @deploy
    def __register_to_manager(state, host):
        registration_command = f"/var/ossec/bin/agent-auth -m {WazuhAgent._configuration['manager_ip']} -A {WazuhAgent._configuration['name']}"
        if WazuhAgent._configuration["registration_with_password"]:
            registration_command += (
                f" -P {WazuhAgent._configuration['registration_password']}"
            )
        registration_command += " || true"
        server.shell(
            state=state,
            host=host,
            name="Register the agent",
            commands=[registration_command],
        )

    @deploy
    def __reload_service(state, host):
        systemd.daemon_reload(
            state=state,
            host=host,
        )
        systemd.service(
            state=state,
            host=host,
            sudo=True,
            service="wazuh-agent",
            running=True,
            restarted=True,
            enabled=True,
        )

    @deploy
    def install(state, host):
        WazuhAgent.get_configuration(state=state, host=host)

        WazuhAgent._check_installation_config(state=state, host=host)

        server.shell(
            state=state,
            host=host,
            name="Installs the GPG key",
            commands=[
                "curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add -"
            ],
        )

        server.shell(
            state=state,
            host=host,
            name="Adds the repository",
            commands=[
                "echo 'deb https://packages.wazuh.com/4.x/apt/ stable main' | tee -a /etc/apt/sources.list.d/wazuh.list"
            ],
        )

        apt.update(
            state=state,
            host=host,
            sudo=True,
            name="Updates the apt repositories",
            cache_time=3600,
            success_exit_codes=[0, 100],
        )

        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Installs Wazuh Agent",
            packages=["wazuh-agent"],
            latest=True,
            success_exit_codes=[0, 100],
        )

        files.replace(
            state=state,
            host=host,
            sudo=True,
            name="Replaces the logging format",
            path="/var/ossec/etc/ossec.conf",
            match=r"^    <log_format>plain</log_format>$",
            replace="    <log_format>json</log_format>",
        )

        WazuhAgent.__set_manager_ip_ossec_conf(state=state, host=host)
        WazuhAgent.__register_to_manager(state=state, host=host)
        WazuhAgent.__reload_service(state=state, host=host)

        WazuhAgent._put_configuration(state=state, host=host)

        WazuhAgent.result[host.name] = True

    @deploy
    def test(state, host):
        WazuhAgent.get_configuration(state=state, host=host)

        WazuhAgent.result[host.name] = host.get_fact(ConnectionWithManager)

    @deploy
    def get_stats(state, host):
        ManagedStats.get_stats(state=state, host=host, solution_class=WazuhAgent)

    @deploy
    def get_logs(state, host):
        WazuhAgent.get_configuration(state=state, host=host)

        WazuhAgent.result[host.name] = host.get_fact(Logs)

    @deploy
    def update(state, host):
        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Updates Wazuh Agent",
            packages=["wazuh-agent"],
            latest=True,
            present=True,
        )

        WazuhAgent.result[host.name] = True

    @deploy
    def uninstall(state, host):
        systemd.service(
            state=state,
            host=host,
            sudo=True,
            service="wazuh-agent",
            enabled=False,
        )
        systemd.daemon_reload(
            state=state,
            host=host,
        )

        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Installs Wazuh Agent",
            packages=["wazuh-agent"],
            present=False,
        )

        WazuhAgent.result[host.name] = True
