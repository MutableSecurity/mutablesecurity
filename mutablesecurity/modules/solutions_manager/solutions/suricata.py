import os
from enum import Enum

import yaml
from pyinfra import config
from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, files, server

from .. import AbstractSolution
from ..facts import DefaultInterface


class FunctioningModes(Enum):
    IDS = "ids"
    IPS = "ips"

    def __str__(self):
        return self.name


class AutomaticUpdates(Enum):
    ENABLED = True
    DISABLED = False

    def __str__(self):
        return self.name


class AlertsCount(FactBase):
    command = "cat /var/log/suricata/eve.json | jq 'select(.event_type==\"alert\")' | grep -c '^{$' || true"

    def process(self, output):
        return int(output[0])


class Alerts(FactBase):
    command = "cat /var/log/suricata/eve.json"

    def process(self, output):
        return output.split()


class ConfigurationState(FactBase):
    command = "cat /opt/mutablesecurity/suricata/suricata.conf"

    def process(self, output):
        # Join the returned lines
        output = "\n".join(output)

        # Load the YAML
        config = yaml.safe_load(output)

        # Convert the fields into enumerations
        config["mode"] = FunctioningModes(config["mode"])
        config["automatic_updates"] = AutomaticUpdates(config["automatic_updates"])

        return config


class Suricata(AbstractSolution):
    _configuration = {
        "mode": FunctioningModes.IDS,
        "interface": None,
        "automatic_updates": AutomaticUpdates.DISABLED,
    }
    meta = {
        "full_name": "Suricata Intrusion Detection and Prevention System",
        "description": "Suricata is the leading independent open source threat detection engine. By combining intrusion detection (IDS), intrusion prevention (IPS), network security monitoring (NSM) and PCAP processing, Suricata can quickly identify, stop, and assess even the most sophisticated attacks.",
        "references": ["https://suricata.io", "https://github.com/OISF/suricata"],
        "configuration": {
            "mode": {"type": FunctioningModes, "help": "Mode in which Suricata works"},
            "interface": {"type": str, "help": "Interface on which Suricata listens"},
            "automatic_updates": {
                "type": AutomaticUpdates,
                "help": "State of the automatic daily updates",
            },
        },
        "messages": {
            "INSTALL": (
                "Suricata is now installed on this machine.",
                "There was an error on Suricata's installation.",
            ),
            "UNINSTALL": (
                "Suricata is no longer installed on this machine.",
                "There was an error on Suricata's uninstallation.",
            ),
            "TEST": (
                "Suricata works as expected.",
                "Suricata does not work as expected.",
            ),
            "GET_STATS": (
                "The stats of Suricata were retrieved.",
                "The stats of Suricata could not be retrieved.",
            ),
            "GET_CONFIGURATION": (
                "The configuration of Suricata was retrieved.",
                "The configuration of Suricata could not be retrieved.",
            ),
            "SET_CONFIGURATION": (
                "The configuration of Suricata was set.",
                "The configuration of Suricata could not be set. Check the provided aspect and value to be valid.",
            ),
        },
    }
    result = None

    @deploy
    def get_configuration(state, host):
        Suricata._configuration = host.get_fact(ConfigurationState)

        Suricata.result = Suricata._configuration

    def _verify_new_configuration(aspect=None, value=None):
        real_value = None
        if aspect == "mode":
            real_value = FunctioningModes[value]
        elif aspect == "automatic_updates":
            real_value = AutomaticUpdates[value]
        elif aspect == "interface":
            real_value = value

        return real_value is not None

    @deploy
    def set_configuration(state, host, aspect=None, value=None):
        if not Suricata._verify_new_configuration(aspect, value):
            Suricata.result = False

            return

        Suricata.get_configuration(state=state, host=host)

        if aspect == "mode":
            value = FunctioningModes[value]

            update_command = "suricata-update"
            if (
                value == FunctioningModes.IPS
                and Suricata._configuration["mode"] == FunctioningModes.IDS
            ):
                files.put(
                    state=state,
                    host=host,
                    sudo=True,
                    name="Creates the Suricata's configuration file to modify the downloaded rules",
                    src=os.path.dirname(__file__) + "/suricata/suricata-modify.conf",
                    dest="/opt/mutablesecurity/suricata/suricata-modify.conf",
                )

                update_command += (
                    " --modify-conf /opt/mutablesecurity/suricata/suricata-modify.conf"
                )

                Suricata._configuration["mode"] = FunctioningModes.IPS
            elif (
                FunctioningModes.IDS
                and Suricata._configuration["mode"] == FunctioningModes.IPS
            ):
                Suricata._configuration["mode"] = FunctioningModes.IDS

            server.shell(
                state=state,
                host=host,
                sudo=True,
                name="Updates the Suricata's rules, optionally with the corresponding modifications",
                commands=[update_command, "suricatasc -c reload-rules"],
            )
        elif aspect == "automatic_updates":
            value = AutomaticUpdates[value]

            files.put(
                state=state,
                host=host,
                sudo=True,
                name="Puts the script that deals with the updates",
                src=os.path.dirname(__file__) + "/suricata/suricata-update.sh",
                dest="/opt/mutablesecurity/suricata/suricata-update.sh",
            )

            if (
                value == AutomaticUpdates.DISABLED
                and Suricata._configuration["automatic_updates"]
                == AutomaticUpdates.ENABLED
            ):
                Suricata._configuration["automatic_updates"] = AutomaticUpdates.DISABLED
            elif (
                value == AutomaticUpdates.ENABLED
                and Suricata._configuration["automatic_updates"]
                == AutomaticUpdates.DISABLED
            ):
                Suricata._configuration["automatic_updates"] = AutomaticUpdates.ENABLED

            server.crontab(
                state=state,
                host=host,
                sudo=True,
                name="Adds a crontab to automatically update the Suricata's rules",
                command="/opt/mutablesecurity/suricata/suricata-update.sh",
                present=Suricata._configuration["automatic_updates"].value,
                hour=0,
                minute=0,
            )

        Suricata._put_configuration(state=state, host=host)

        Suricata.result = True

    @deploy
    def _put_configuration(state, host):
        configuration = Suricata._configuration
        for key, value in configuration.items():
            if isinstance(value, Enum):
                configuration[key] = value.value

        files.template(
            state=state,
            host=host,
            sudo=True,
            name="Dumps the Suricata's configuration file",
            src=os.path.dirname(__file__) + "/suricata/suricata.conf.j2",
            dest="/opt/mutablesecurity/suricata/suricata.conf",
            configuration=Suricata._configuration,
        )

        Suricata.result = True

    @deploy
    def install(state, host):
        apt.update(
            state=state,
            host=host,
            sudo=True,
            name="Updates the apt reporisoties",
            env={"LC_TIME": "en_US.UTF-8"},
            cache_time=3600,
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
        )

        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Installs Suricata, jq and ufw",
            packages=["suricata", "jq", "ufw", "tmux", "moreutils"],
            latest=True,
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

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Enables ufw",
            commands=["ufw --force enable"],
        )

        paths = ["/etc/ufw/before.rules", "/etc/ufw/before6.rules"]
        for path in paths:
            files.replace(
                state=state,
                host=host,
                sudo=True,
                name="Adds the ufw rules required to proxy the traffic",
                path=path,
                match=r"# End required lines",
                replace=f"# End required lines\\n\\n# Suricata\\n-I INPUT -j NFQUEUE\\n-I OUTPUT -j NFQUEUE\\n\\n",
            )

        files.replace(
            state=state,
            host=host,
            sudo=True,
            name="Modifies the listening mode of Suricata",
            path="/etc/default/suricata",
            match=r"LISTENMODE=.*",
            replace=f"LISTENMODE=nfqueue",
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Updates the Suricata's rules",
            commands=["suricata-update"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Starts the Suricata service",
            commands=["service suricata start"],
        )

        files.directory(
            state=state,
            host=host,
            sudo=True,
            name="Creates the MutableSecurity directory",
            path="/opt/mutablesecurity/suricata/",
        )

        Suricata._put_configuration(state=state, host=host)

        Suricata.result = True

    @deploy
    def update(state, host):
        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Updates Suricata, jq and ufw",
            packages=["suricata"],
            latest=True,
            present=True,
        )

        Suricata.result = True

    @deploy
    def test(state, host):
        Suricata.get_configuration(state=state, host=host)

        curl_command = "curl --max-time 3 http://testmynids.org/uid/index.html"
        if Suricata._configuration["mode"] == FunctioningModes.IPS:
            curl_command += " || true"
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Updates the Suricata's rules",
            commands=[curl_command],
        )

        # This verification will return a non-zero exit code if the error was
        # not found.
        result = True
        try:
            server.shell(
                state=state,
                host=host,
                sudo=True,
                name="Verifies the Suricata's alerts file",
                commands=[
                    "tail -n 100 /var/log/suricata/fast.log | grep -c '1:2100498:7'"
                ],
            )
        except:
            result = False

        Suricata.result = result

    @deploy
    def get_stats(state, host):
        Suricata.get_configuration(state=state, host=host)

        Suricata.result = {"alerts_count": host.get_fact(AlertsCount)}

    @deploy
    def get_logs(state, host):
        Suricata.get_configuration(state=state, host=host)

        Suricata.result = host.get_fact(Alerts)

    @deploy
    def uninstall(state, host):
        Suricata.get_configuration(state=state, host=host)

        paths = ["/etc/ufw/before.rules", "/etc/ufw/before6.rules"]
        for path in paths:
            server.shell(
                state=state,
                host=host,
                sudo=True,
                name="Removes the ufw rules required to proxy the traffic",
                commands=[
                    f"cat {path} | tr '\\n' '\\r' | sed 's/# End required lines\\r\\r# Suricata\\r-I INPUT -j NFQUEUE\\r-I OUTPUT -j NFQUEUE\\r\\r/# End required lines/' | tr '\\r' '\\n' | sponge {path}"
                ],
            )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Reloads ufw",
            commands=["ufw reload"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Uninstalls Suricata",
            commands=["tmux new -d 'apt -y remove suricata'"],
        )

        Suricata.result = True
