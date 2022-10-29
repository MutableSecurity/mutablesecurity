import re
from datetime import datetime
from enum import Enum

from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, files, python, server, systemd

from ...exceptions import OperationNotSupported
from ..deployments.managed_stats import ManagedStats
from ..deployments.managed_yaml_backed_config import ManagedYAMLBackedConfig
from ..facts.services import ServiceRunning
from . import AbstractSolution


class AgentRegistrationWithPassword(Enum):
    ENABLED = True
    DISABLED = False

    def __str__(self):
        return self.name

    @classmethod
    def from_str(cls, name):
        return cls[name]


class AgentsCount(FactBase):
    # Except the agent with the ID 000 as it is installed on Manager.
    command = "sudo /var/ossec/bin/agent_control -l | grep 'ID: ' | grep -c -v 'ID: 000' || true"

    def process(self, output):
        return int(output[0])


class AlertsCount(FactBase):
    command = "sudo cat /var/ossec/logs/alerts/alerts.json | wc -l"

    def process(self, output):
        return int(output[0])


class DailyAlertsCount(FactBase):
    def command(self):
        current_date = datetime.today().strftime("%Y-%m-%d")

        return f"cat /var/ossec/logs/alerts/alerts.json | grep '{current_date}' | wc -l"

    def process(self, output):
        return int(output[0])


class Version(FactBase):
    command = "sudo /var/ossec/bin/wazuh-control -j info | jq -r .data[0].WAZUH_VERSION"

    def process(self, output):
        return output[0]


class Logs(FactBase):
    command = "cat /var/ossec/logs/ossec.log"

    def process(self, output):
        return output


class InstalationDetails(FactBase):
    command = "cat /tmp/wazuh.txt | grep 'You can access the web interface' -A 2"

    def process(self, output):
        output = "\n".join(output)
        username = re.search("User: ([a-zA-Z0-9]+)", output).group(1)
        password = re.search("Password: ([a-zA-Z0-9]+)", output).group(1)

        return (username, password)


class AgentRegistrationPassword(FactBase):
    command = "cat /var/ossec/logs/ossec.log | grep 'Random password chosen for agent authentication'"

    def process(self, output):
        output = "\n".join(output)
        password = re.search("agent authentication: ([a-zA-Z0-9]+)", output).group(1)

        return password


class WazuhManager(AbstractSolution):
    meta = {
        "id": "wazuh_manager",
        "full_name": "Wazuh Manager",
        "description": "Wazuh is an unified XDR and SIEM protection for endpoint and cloud workloads. The Manager is the central server in the Wazuh architecture. It analyzes the data received from all registered agents and triggers alerts when an event coincides with a rule.",
        "references": ["https://wazuh.com", "https://github.com/wazuh/wazuh"],
        "configuration": {
            "dashboard_username": {
                "type": str,
                "help": "Username for Wazuh Dashboard",
                "default": None,
                "read_only": True,
            },
            "dashboard_password": {
                "type": str,
                "help": "Password for Wazuh Dashboard",
                "default": None,
                "read_only": True,
            },
            "agents_registration_with_password": {
                "type": AgentRegistrationWithPassword,
                "help": "Boolean indicating if the agents needs to register with a password",
                "default": AgentRegistrationWithPassword.ENABLED,
            },
            "agents_password": {
                "type": str,
                "help": "Password for agents registration. Keep this aspect empty to let Wazuh generate a random password.",
                "default": "",
            },
        },
        "metrics": {
            "total_agents": {
                "description": "Total number of registered agents",
                "fact": AgentsCount,
            },
            "total_alerts": {
                "description": "Total number of alerts",
                "fact": AlertsCount,
            },
            "today_alerts": {
                "description": "Total number of alerts generated today",
                "fact": DailyAlertsCount,
            },
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
            state=state, host=host, solution_class=WazuhManager
        )

        # TODO: Remove after upgrading to pyinfra 2.x
        def stage(state, host):
            if (
                password := WazuhManager._configuration.get("dashboard_password", None)
            ) is None:
                (
                    WazuhManager._configuration["dashboard_username"],
                    WazuhManager._configuration["dashboard_password"],
                ) = host.get_fact(InstalationDetails)

                WazuhManager._configuration["agents_password"] = host.get_fact(
                    AgentRegistrationPassword
                )

        python.call(state=state, host=host, function=stage)

    @deploy
    def _set_default_configuration(state, host):
        ManagedYAMLBackedConfig._set_default_configuration(
            state=state, host=host, solution_class=WazuhManager
        )

    @deploy
    def _verify_new_configuration(state, host, aspect, value):
        ManagedYAMLBackedConfig._verify_new_configuration(
            state=state,
            host=host,
            solution_class=WazuhManager,
            aspect=aspect,
            value=value,
        )

    @deploy
    def set_configuration(state, host, aspect=None, value=None):
        ManagedYAMLBackedConfig.set_configuration(
            state=state,
            host=host,
            solution_class=WazuhManager,
            aspect=aspect,
            value=value,
        )

    @deploy
    def _set_configuration_callback(
        state, host, aspect=None, old_value=None, new_value=None
    ):
        password_script_location = f"/opt/mutablesecurity/{WazuhManager.meta['id']}/wazuh-opendistro-passwords-tool.sh"
        if aspect == "agents_registration_with_password":
            WazuhManager.__change_agents_registration(
                state=state, host=host, value=new_value
            )
        elif aspect == "agents_password":
            server.shell(
                state=state,
                host=host,
                name="Places the password in the configuration file and changes its permisions",
                commands=[
                    f"echo '{new_value}' > /var/ossec/etc/authd.pass",
                    "chmod 644 /var/ossec/etc/authd.pass",
                    "chown root:wazuh /var/ossec/etc/authd.pass",
                ],
            )

            systemd.service(
                state=state,
                host=host,
                service="wazuh-manager",
                running=True,
                restarted=True,
                enabled=True,
                sudo=True,
            )

    @deploy
    def _put_configuration(state, host):
        ManagedYAMLBackedConfig._put_configuration(
            state=state, host=host, solution_class=WazuhManager
        )

    @deploy
    def __change_agents_registration(state, host, value):
        if value:
            matched = "no"
            replaced = "yes"
        else:
            matched = "yes"
            replaced = "no"

        files.replace(
            state=state,
            host=host,
            name="Enables password authentication for agents",
            path="/var/ossec/etc/ossec.conf",
            match=f"<use_password>{matched}</use_password>",
            replace=f"<use_password>{replaced}</use_password>",
            sudo=True,
        )

        systemd.service(
            state=state,
            host=host,
            service="wazuh-manager",
            running=True,
            restarted=True,
            enabled=True,
            sudo=True,
        )

    @deploy
    def _check_installation_config(state, host):
        ManagedYAMLBackedConfig._check_installation_config(
            state=state, host=host, solution_class=WazuhManager
        )

    @deploy
    def install(state, host):
        WazuhManager.get_configuration(state=state, host=host)

        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Installs the requirements",
            packages=["jq"],
            latest=True,
        )

        setup_script_location = (
            f"/opt/mutablesecurity/{WazuhManager.meta['id']}/wazuh-setup.sh"
        )
        password_script_location = f"/opt/mutablesecurity/{WazuhManager.meta['id']}/wazuh-opendistro-passwords-tool.sh"

        files.download(
            state=state,
            host=host,
            name="Download the Wazuh setup script",
            src="https://packages.wazuh.com/4.3/wazuh-install.sh",
            dest=setup_script_location,
            sudo=True,
        )

        files.download(
            state=state,
            host=host,
            name="Download the Wazuh passwords script",
            src="https://packages.wazuh.com/4.3/wazuh-opendistro-passwords-tool.sh",
            dest=password_script_location,
            sudo=True,
        )

        server.shell(
            state=state,
            host=host,
            name="Executes the Wazuh Manager installation via management script",
            commands=[
                f"bash {setup_script_location} -a -i -o | tee --append /tmp/wazuh.txt"
            ],
            sudo=True,
        )

        WazuhManager.__change_agents_registration(host=host, state=state, value=True)

        WazuhManager._put_configuration(state=state, host=host)

        WazuhManager.result[host.name] = True

    @deploy
    def test(state, host):
        required_services_name = [
            "wazuh-dashboard.service",
            "wazuh-indexer.service",
            "wazuh-manager.service",
        ]

        is_ok = True
        for service in required_services_name:
            is_ok &= host.get_fact(ServiceRunning, service)

        WazuhManager.result[host.name] = is_ok

    @deploy
    def get_stats(state, host):
        ManagedStats.get_stats(state=state, host=host, solution_class=WazuhManager)

    @deploy
    def get_logs(state, host):
        WazuhManager.get_configuration(state=state, host=host)

        WazuhManager.result[host.name] = host.get_fact(Logs)

    @deploy
    def update(state, host):
        raise OperationNotSupported()

    @deploy
    def uninstall(state, host):
        WazuhManager.get_configuration(state=state, host=host)

        setup_script_location = (
            f"/opt/mutablesecurity/{WazuhManager.meta['id']}/wazuh-setup.sh"
        )

        server.shell(
            state=state,
            host=host,
            name="Executes the Wazuh Manager uninstallation via management script",
            commands=[f"bash {setup_script_location} -u"],
            sudo=True,
        )

        WazuhManager.result[host.name] = True
