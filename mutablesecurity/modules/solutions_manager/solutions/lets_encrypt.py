from datetime import datetime

from genericpath import exists
from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, python, server

from ..deployments.managed_stats import ManagedStats
from ..deployments.managed_yaml_backed_config import ManagedYAMLBackedConfig
from . import AbstractSolution


class SecuredRequests(FactBase):
    command = "cat /var/log/nginx/https_dev.mutablesecurity.io_access.log | wc -l "

    def process(self, output):
        return int(output[0])


class SecuredRequestsToday(FactBase):
    def command(self):
        current_date = datetime.today().strftime("%d/%B/%Y")

        return f"sudo cat /var/log/nginx/https_dev.mutablesecurity.io_access.log | grep '{current_date}' | wc -l"

    def process(self, output):
        return int(output[0])


class Version(FactBase):
    command = "apt-cache policy certbot | grep -i Installed | cut -d ' ' -f 4"

    def process(self, output):
        return output[0]


class Logs(FactBase):
    command = "cat /var/log/nginx/https_dev.mutablesecurity.io_access.log"

    def process(self, output):
        return output


class LetsEncrypt(AbstractSolution):
    meta = {
        "id": "letsencrypt",
        "full_name": "Let's Encrypt x Certbot",
        "description": "Let's Encrypt is a free, automated, and open certificate authority brought to you by the nonprofit Internet Security Research Group (ISRG). Certbot is made by the Electronic Frontier Foundation (EFF), a 501(c)3 nonprofit based in San Francisco, CA, that defends digital privacy, free speech, and innovation.",
        "references": [
            "https://letsencrypt.org/",
            "https://github.com/letsencrypt",
            "https://certbot.eff.org/",
            "https://github.com/certbot/certbot",
        ],
        "configuration": {
            "email": {
                "type": str,
                "help": "The email provided for security reasons when generating certificates",
                "default": "hello@mutablesecurity.io",
            },
            "domains": {
                "type": list,
                "help": "The domain(s) protected by certificates",
                "default": "staging.mutablesecurity.io",
            },
        },
        "metrics": {
            "SecuredRequests": {
                "description": "Total number Secured Requests",
                "fact": SecuredRequests,
            },
            "SecuredRequestsToday": {
                "description": "Total number of Secured Requests Today",
                "fact": SecuredRequestsToday,
            },
            "version": {"description": "Current installed version", "fact": Version},
        },
        "messages": {
            "GET_CONFIGURATION": (
                "The configuration of Let's Encrypt x Certbot was retrieved.",
                "The configuration of Let's Encrypt x Certbot could not be retrieved.",
            ),
            "SET_CONFIGURATION": (
                "The configuration of Let's Encrypt x Certbot was set.",
                "The configuration of Let's Encrypt x Certbot could not be set. Check the provided aspect and value to be valid.",
            ),
            "INSTALL": (
                "Let's Encrypt x Certbot is now installed on this machine.",
                "There was an error on Let's Encrypt x Certbot's installation.",
            ),
            "TEST": (
                "Let's Encrypt x Certbot works as expected.",
                "Let's Encrypt x Certbot does not work as expected.",
            ),
            "GET_LOGS": (
                "The logs of Let's Encrypt x Certbot were retrieved.",
                "The logs of Let's Encrypt x Certbot could not be retrieved.",
            ),
            "GET_STATS": (
                "The stats of Let's Encrypt x Certbot were retrieved.",
                "The stats of Let's Encrypt x Certbot could not be retrieved.",
            ),
            "UPDATE": (
                "Let's Encrypt x Certbot is now at its newest version.",
                "There was an error on Let's Encrypt x Certbot's update.",
            ),
            "UNINSTALL": (
                "Let's Encrypt x Certbot is no longer installed on this machine.",
                "There was an error on Let's Encrypt x Certbot's uninstallation.",
            ),
        },
    }
    result = None

    @deploy
    def get_configuration(state, host):
        ManagedYAMLBackedConfig.get_configuration(
            state=state, host=host, solution_class=LetsEncrypt
        )

    @deploy
    def _set_default_configuration(state, host):
        ManagedYAMLBackedConfig._set_default_configuration(
            state=state, host=host, solution_class=LetsEncrypt
        )

    @deploy
    def _verify_new_configuration(state, host, aspect, value):
        ManagedYAMLBackedConfig._verify_new_configuration(
            state=state,
            host=host,
            solution_class=LetsEncrypt,
            aspect=aspect,
            value=value,
        )

    @deploy
    def set_configuration(state, host, aspect=None, value=None):
        ManagedYAMLBackedConfig.set_configuration(
            state=state,
            host=host,
            solution_class=LetsEncrypt,
            aspect=aspect,
            value=value,
        )

    @deploy
    def _set_configuration_callback(state, host, aspect=None, value=None):
        # Perform post-setting operations, based on the set configuration
        pass

    @deploy
    def _put_configuration(state, host):
        ManagedYAMLBackedConfig._put_configuration(
            state=state, host=host, solution_class=LetsEncrypt
        )

    @deploy
    def install(state, host):
        LetsEncrypt._set_default_configuration(state=state, host=host)
        LetsEncrypt._put_configuration(state=state, host=host)

        file_path = "/opt/mutablesecurity/letsencrypt/default"
        if not exists(file_path):
            server.shell(
                state=state,
                host=host,
                sudo=True,
                name="Saves the default config file in case the user wants to remove LetsEncrypt(Certbot)",
                commands=[
                    "cp /etc/nginx/sites-enabled/default /opt/mutablesecurity/letsencrypt/"
                ],
            )

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
            packages=["python3-certbot-nginx", "curl"],
            latest=True,
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Generates and installs the certificates for the given nginx domain",
            commands=[
                "certbot --nginx --noninteractive --agree-tos --cert-name staging.mutablesecurity.io -d staging.mutablesecurity.io -m hello@mutablesecurity.io --redirect"
            ],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Adds MutableSecurity logs command in sites-enabled",
            commands=[
                "sed -i '/server_name staging.mutablesecurity.io;/a access_log /var/log/nginx/https_dev.mutablesecurity.io_access.log; # Managed by MutableSecurity' /etc/nginx/sites-enabled/default"
            ],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Restart the Nginx service",
            commands=["systemctl restart nginx"],
        )

        LetsEncrypt.result = True

    @deploy
    def test(state, host):
        LetsEncrypt.get_configuration(state=state, host=host)

        curl_command = "curl https://staging.mutablesecurity.io"
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Requests if the https connection is made",
            commands=[curl_command],
        )

        def stage(state, host):
            connections = host.get_fact(SecuredRequestsToday)

            LetsEncrypt.result = connections != 0

        python.call(state=state, host=host, sudo=True, function=stage)

    @deploy
    def get_stats(state, host):
        ManagedStats.get_stats(state=state, host=host, solution_class=LetsEncrypt)

    @deploy
    def get_logs(state, host):
        LetsEncrypt.get_configuration(state=state, host=host)

        LetsEncrypt.result = host.get_fact(Logs)

    @deploy
    def update(state, host):
        apt.packages(
            state=state,
            host=host,
            sudo=True,
            name="Updates Let's Encrypt x Certbot",
            packages=["certbot"],
            latest=True,
            present=True,
        )

        LetsEncrypt.result = True

    @deploy
    def uninstall(state, host):
        LetsEncrypt.get_configuration(state=state, host=host)

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Revokes the generated certificate",
            commands=["certbot revoke -n --cert-name staging.mutablesecurity.io"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Adds all the old configurations back in place on sites-enabled",
            commands=[
                "cp /opt/mutablesecurity/letsencrypt/default /etc/nginx/sites-enabled/default"
            ],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Purges Let's Encrypt x Certbot",
            commands=["apt purge -y letsencrypt certbot"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Removes all traces of Let's Encrypt x Certbot",
            commands=[
                "rm -rf /etc/letsencrypt /root/.local/share/letsencrypt/ /opt/eff.org/certbot/ /var/lib/letsencrypt/ /var/log/letsencrypt/ /var/log/nginx/https_dev.mutablesecurity.io_access.log /opt/mutablesecurity/letsencrypt/default"
            ],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Removes everything using autoremove",
            commands=["apt -y update && apt -y autoremove"],
        )

        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Restarts the Nginx service to apply changes",
            commands=["systemctl restart nginx"],
        )

        LetsEncrypt.result = True
