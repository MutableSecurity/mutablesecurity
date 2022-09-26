"""Module integrating Let's Encrypt."""

# pylint: disable=protected-access
# pylint: disable=missing-class-docstring
# pylint: disable=unused-argument
# pylint: disable=unexpected-keyword-arg

import typing
from datetime import datetime

from pyinfra import host
from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import apt, files, server, systemd

from mutablesecurity.helpers.data_type import IntegerDataType, StringDataType
from mutablesecurity.solutions.base import (BaseAction, BaseInformation,
                                            BaseLog, BaseSolution,
                                            BaseSolutionException, BaseTest,
                                            InformationProperties, TestType)
from mutablesecurity.solutions.common.facts.files import FilePresenceTest
from mutablesecurity.solutions.common.facts.networking import \
    InternetConnection
from mutablesecurity.solutions.common.facts.os import CheckIfUbuntu
from mutablesecurity.solutions.common.facts.service import ActiveService
from mutablesecurity.solutions.common.operations.apt import autoremove


class CertbotAlreadyUpdatedException(BaseSolutionException):
    """Certbot is already at its newest version."""


class CertbotAlreadyInstalledException(BaseSolutionException):
    """Let's Encrypt Nginx file exists and Certbot is already installed."""


@deploy
def revoke_certificate_with_explicit_domain(domain: str = None) -> None:
    if domain is None:
        domain = UserDomain.get()

    server.shell(
        sudo=True,
        name="Revokes the generated certificate",
        commands=[
            f"certbot revoke -n --cert-name {domain} --reason"
            f" {RevokeReason.get()}"
        ],
    )

    server.shell(
        sudo=True,
        name=(
            "Adds all the old configurations back in place inside"
            " sites-enabled"
        ),
        commands=[
            "mv -f /opt/mutablesecurity/lets_encrypt/default"
            " /etc/nginx/sites-enabled/default"
        ],
    )

    files.file(
        sudo=True,
        name="Removes the MutableSecurity traces from /var/log/nginx/",
        path=f"/var/log/nginx/https_{domain}_access.log",
        present=False,
    )


@deploy
def revoke_old_and_generate_new_certificate(domain: str) -> None:
    revoke_certificate_with_explicit_domain(domain)
    GenerateCertificate.execute()


@deploy
def revoke_old_and_generate_new_certificate_when_domain_changed(
    old_value: typing.Any, new_value: typing.Any
) -> None:
    revoke_certificate_with_explicit_domain(old_value)

    server.shell(
        sudo=True,
        name=(
            "Saves the default config file in case the user wants to"
            " remove LetsEncrypt (Certbot)"
        ),
        commands=[
            "cp /etc/nginx/sites-enabled/default"
            " /opt/mutablesecurity/lets_encrypt/"
        ],
    )

    server.shell(
        sudo=True,
        name=(
            "Generates and installs the certificate for the given Nginx domain"
        ),
        commands=[
            "certbot --nginx --noninteractive --agree-tos --cert-name"
            f" {new_value} -d {new_value} -m"
            f" {UserEmail.get()} --redirect"
        ],
    )

    server.shell(
        sudo=True,
        name=(
            "Adds MutableSecurity logs generation command in the"
            " sites-enabled directory of the Nginx configuration"
        ),
        commands=[
            f"sed -i '/server_name {new_value};/a access_log"
            f" /var/log/nginx/https_{new_value}_access.log; # Managed by"
            " MutableSecurity' /etc/nginx/sites-enabled/default"
        ],
    )

    server.shell(
        sudo=True,
        name="Restart the Nginx service",
        commands=["systemctl restart nginx"],
    )


@deploy
def revoke_old_and_generate_new_certificate_when_email_changed(
    old_value: typing.Any, new_value: typing.Any
) -> None:
    revoke_old_and_generate_new_certificate(UserDomain.get())


class UserEmail(BaseInformation):
    IDENTIFIER = "email"
    DESCRIPTION = (
        "The email of the user whom installs Let's Encrypt on the given"
        " domain"
    )
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = None
    GETTER = None
    SETTER = revoke_old_and_generate_new_certificate_when_email_changed


class UserDomain(BaseInformation):
    IDENTIFIER = "domain"
    DESCRIPTION = "The domain on which the user installs Let's Encrypt"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = None
    GETTER = None
    SETTER = revoke_old_and_generate_new_certificate_when_domain_changed


class RevokeReason(BaseInformation):
    IDENTIFIER = "revoke_reason"
    DESCRIPTION = (
        "The reason why Let's Encrypt has been removed. Choose from"
        " 'unspecified', 'keycompromise', 'affiliationchanged', 'superseded',"
        " 'cessationofoperation', if you wish to change the reason."
    )
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "unspecified"
    GETTER = None
    SETTER = None


class LogLocation(BaseInformation):
    class LogLocationFact(FactBase):
        command = "echo 'hi'"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return f"/var/log/nginx/https_{UserDomain.get()}_access.log"

    IDENTIFIER = "log_location"
    DESCRIPTION = "Location where Nginx logs messages"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.READ_ONLY,
        InformationProperties.AUTO_GENERATED_BEFORE_INSTALL,
    ]
    DEFAULT_VALUE = None
    GETTER = LogLocationFact
    SETTER = None


class InstalledVersion(BaseInformation):
    class InstalledVersionFact(FactBase):
        command = (
            "apt-cache policy certbot | grep -i Installed | cut -d ' ' -f 4"
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


class SecuredRequests(BaseInformation):
    class SecuredRequestsFact(FactBase):
        @staticmethod
        def command() -> str:
            return f"cat {LogLocation.get()}| wc -l "

        @staticmethod
        def process(output: typing.List[str]) -> int:
            return int(output[0])

    IDENTIFIER = "secured_requests"
    DESCRIPTION = "Total number of secured requests"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = SecuredRequestsFact
    SETTER = None


class SecuredRequestsToday(BaseInformation):
    class SecuredRequestsTodayFact(FactBase):
        @staticmethod
        def command() -> str:
            current_date = datetime.today().strftime("%d/%b/%Y")

            return (
                f"sudo cat {LogLocation.get()} | grep '{current_date}' | wc -l"
            )

        @staticmethod
        def process(output: typing.List[str]) -> int:
            return int(output[0])

    IDENTIFIER = "secured_requests_today"
    DESCRIPTION = "Total number of secured requests today"
    INFO_TYPE = IntegerDataType
    PROPERTIES = [
        InformationProperties.METRIC,
        InformationProperties.READ_ONLY,
    ]
    DEFAULT_VALUE = None
    GETTER = SecuredRequestsTodayFact
    SETTER = None


class FilePresenceRequirement(BaseTest):
    IDENTIFIER = "configuration_file_presence"
    DESCRIPTION = (
        "Checks if the old Nginx configuration file is saved in"
        " /opt/mutablesecurity/lets_encrypt."
    )
    TEST_TYPE = TestType.PRESENCE
    FACT = FilePresenceTest
    FACT_ARGS = ("/opt/mutablesecurity/lets_encrypt/default", True)


class UbuntuRequirement(BaseTest):
    IDENTIFIER = "ubuntu"
    DESCRIPTION = "Checks if the operating system is Ubuntu."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = CheckIfUbuntu


class TestRequest(BaseTest):
    @staticmethod
    @deploy
    def make_request() -> None:
        curl_command = f"curl https://{UserDomain.get()}"
        server.shell(
            commands=[curl_command],
            name="Checks if the HTTPS connection is made.",
        )

    class TestRequestFact(FactBase):
        @staticmethod
        def command() -> str:
            current_date = datetime.today().strftime("%d/%b/%Y:%H:%M")

            check_command = (
                f"sudo cat {LogLocation.get()} | grep '{current_date}' | wc -l"
            )

            return check_command

        @staticmethod
        def process(output: typing.List[str]) -> bool:
            return int(output[0]) != 0

    IDENTIFIER = "request_via_https"
    DESCRIPTION = "Checks if the site is secured with Let's Encrypt."
    TEST_TYPE = TestType.SECURITY
    TRIGGER = make_request
    FACT = TestRequestFact


class InternetAccess(BaseTest):
    IDENTIFIER = "internet_access"
    DESCRIPTION = "Checks if host has Internet access."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = InternetConnection


class ActiveNginx(BaseTest):
    IDENTIFIER = "nginx_active"
    DESCRIPTION = "Checks if Nginx is installed and the service is active."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = ActiveService
    FACT_ARGS = ("nginx",)


class TestDomainRequest(BaseTest):
    class TestDomainRequestFact(FactBase):
        @staticmethod
        def command() -> str:
            check_command = (
                "curl -o /dev/null -s -w '%{{http_code}}\n' -H 'Host:"
                f" {UserDomain.get()}' http://localhost/"
            )

            return check_command

        @staticmethod
        def process(output: typing.List[str]) -> bool:
            return output[0] != "000"

    IDENTIFIER = "domain_request"
    DESCRIPTION = (
        "Checks if the site exists before trying to generate certificate."
    )
    TEST_TYPE = TestType.REQUIREMENT
    FACT = TestDomainRequestFact
    FACT_ARGS = ()


class TextLogs(BaseLog):
    class GeneratedLogsFact(FactBase):
        @staticmethod
        def command() -> str:
            return f"cat {LogLocation.get()}"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return "\n".join(output)

    IDENTIFIER = "logs"
    DESCRIPTION = (
        "The logs generated by Let's Encrypt x Certbot for the given domain"
    )
    INFO_TYPE = IntegerDataType
    FACT = GeneratedLogsFact


class GenerateCertificate(BaseAction):
    @staticmethod
    @deploy
    def generate_certificate() -> None:
        server.shell(
            sudo=True,
            name=(
                "Saves the default config file in case the user wants to"
                " remove LetsEncrypt (Certbot)"
            ),
            commands=[
                "cp /etc/nginx/sites-enabled/default"
                " /opt/mutablesecurity/lets_encrypt/"
            ],
        )

        server.shell(
            sudo=True,
            name=(
                "Generates and installs the certificate for the given Nginx"
                " domain"
            ),
            commands=[
                "certbot --nginx --noninteractive --agree-tos --cert-name"
                f" {UserDomain.get()} -d {UserDomain.get()} -m"
                f" {UserEmail.get()} --redirect"
            ],
        )

        server.shell(
            sudo=True,
            name=(
                "Adds MutableSecurity logs generation command in the"
                " sites-enabled directory of the Nginx configuration"
            ),
            commands=[
                f"sed -i '/server_name {UserDomain.get()};/a access_log"
                f" {LogLocation.get()}; # Managed by MutableSecurity'"
                " /etc/nginx/sites-enabled/default"
            ],
        )

        server.shell(
            sudo=True,
            name="Restart the Nginx service",
            commands=["systemctl restart nginx"],
        )

    IDENTIFIER = "generate_certificate"
    DESCRIPTION = (
        "Generates a certificate for a given domain and email. Used mostly"
        " when there are multiple domains for which Let's Encrypt HTTPS"
        " encryption is required."
    )
    ACT = generate_certificate


class RevokeCurrentCertificate(BaseAction):
    @staticmethod
    @deploy
    def revoke_certificate() -> None:
        revoke_certificate_with_explicit_domain()

    IDENTIFIER = "revoke_certificate"
    DESCRIPTION = "Revokes the certificate for the current email and domain."
    ACT = revoke_certificate


class LetsEncrypt(BaseSolution):
    INFORMATION = [
        RevokeReason,  # type: ignore[list-item]
        UserEmail,  # type: ignore[list-item]
        UserDomain,  # type: ignore[list-item]
        LogLocation,  # type: ignore[list-item]
        SecuredRequests,  # type: ignore[list-item]
        SecuredRequestsToday,  # type: ignore[list-item]
        InstalledVersion,  # type: ignore[list-item]
    ]
    TESTS = [
        UbuntuRequirement,  # type: ignore[list-item]
        InternetAccess,  # type: ignore[list-item]
        TestRequest,  # type: ignore[list-item]
        ActiveNginx,  # type: ignore[list-item]
        FilePresenceRequirement,  # type: ignore[list-item]
        TestDomainRequest,  # type: ignore[list-item]
    ]
    LOGS = [
        TextLogs,  # type: ignore[list-item]
    ]
    ACTIONS = []

    @staticmethod
    @deploy
    def _install() -> None:
        files.directory(
            sudo=True,
            path="/opt/mutablesecurity/lets_encrypt",
            present=True,
            name="Creates the folder that will store Let's Encrypt.",
        )

        apt.update(
            sudo=True,
            name="Updates the apt reporisoties",
            env={"LC_TIME": "en_US.UTF-8"},
            cache_time=3600,
            success_exit_codes=[0, 100],
        )

        apt.packages(
            sudo=True,
            name="Installs the requirements",
            packages=["python3-certbot-nginx", "curl"],
            latest=True,
        )
        GenerateCertificate.execute()

    @staticmethod
    @deploy
    def _uninstall(remove_logs: bool = True) -> None:
        RevokeCurrentCertificate.execute()

        apt.packages(
            sudo=True,
            update=True,
            name="Removes Let's Encrypt x Certbot",
            packages=["letsencrypt", "certbot"],
            present=False,
        )

        files.directory(
            sudo=True,
            name="Removes Let's Encrypt from /etc",
            path="/etc/letsencrypt",
            present=False,
        )

        files.directory(
            sudo=True,
            name="Removes Let's Encrypt from /root/.local/share/",
            path="/root/.local/share/letsencrypt/",
            present=False,
        )

        files.directory(
            sudo=True,
            name="Removes Certbot from /opt/eff.org/",
            path="/opt/eff.org/certbot/",
            present=False,
        )

        files.directory(
            sudo=True,
            name="Removes Let's Encrypt from /var/lib/",
            path="/var/lib/letsencrypt/",
            present=False,
        )

        files.directory(
            sudo=True,
            name="Removes Let's Encrypt from /var/log/",
            path="/var/log/letsencrypt/",
            present=False,
        )

        autoremove(
            name=(
                "Removes all residual data correlated to Let's Encrypt x"
                " Certbot"
            )
        )

        systemd.service(
            name="Restarts the Nginx service to apply changes",
            service="nginx.service",
            running=True,
            restarted=True,
            enabled=True,
        )

        files.directory(
            sudo=True,
            name=(
                "Removes the Certbot traces from"
                " opt/mutablesecurity/lets_encrypt/"
            ),
            path="/opt/mutablesecurity/lets_encrypt/",
            present=False,
        )

    @staticmethod
    @deploy
    def _update() -> None:
        class LatestVersionFact(FactBase):
            command = (
                "apt-cache policy certbot | grep -i Candidate | cut -d ' '"
                " -f 4"
            )

            @staticmethod
            def process(output: typing.List[str]) -> str:
                return output[0]

        if host.get_fact(LatestVersionFact) == InstalledVersion.get():
            raise CertbotAlreadyUpdatedException()

        apt.packages(
            sudo=True,
            update=True,
            packages=["certbot"],
            latest=True,
            name="Updates Certbot via apt.",
        )
