"""Module defining a dummy security solution, for testing purposes."""

# pylint: disable=protected-access
# pylint: disable=missing-class-docstring
# pylint: disable=unused-argument
# pylint: disable=unexpected-keyword-arg

import os
import typing
import uuid

from pyinfra.api.deploy import deploy
from pyinfra.api.facts import FactBase
from pyinfra.operations import apt, files, server

from mutablesecurity.helpers.data_type import (
    StringDataType,
    StringListDataType,
)
from mutablesecurity.solutions.base import (
    BaseAction,
    BaseInformation,
    BaseLog,
    BaseSolution,
    BaseSolutionException,
    BaseTest,
    InformationProperties,
    TestType,
)
from mutablesecurity.solutions.common.facts.bash import PresentCommand


class IncompatibleArchitectureException(BaseSolutionException):
    """Your architecture does not support any Duplicati build."""


# Actions classes definitions


class LocalBackup(BaseAction):
    @staticmethod
    @deploy
    def local_backup(source_file: str, backup_location: str) -> None:
        command = _make_local_backup(source_file, backup_location)
        server.shell(
            commands=[command],
            name="Backup files on localhost.",
        )

    IDENTIFIER = "local_backup"
    DESCRIPTION = "Save files local"
    ACT = local_backup


class RestoreLocalBackup(BaseAction):
    @staticmethod
    @deploy
    def restore_local_backup(
        backup_location: str, restore_location: str
    ) -> None:
        command = _make_local_backup(
            backup_location, restore_location, reverse=True
        )
        server.shell(
            commands=[command],
            name="Restore backup files on localhost.",
        )

    IDENTIFIER = "restore_local_backup"
    DESCRIPTION = "Restore backup files on localhost"
    ACT = restore_local_backup


class SshBackup(BaseAction):
    @staticmethod
    @deploy
    def ssh_backup(
        source_file: str,
        server_ip: str,
        username: str,
        password: str,
        ssh_fingerprint: str,
    ) -> None:
        command = _make_ssh_backup(
            source_file, server_ip, username, password, ssh_fingerprint
        )
        server.shell(
            commands=[command],
            name="Save file over SSH",
        )

    IDENTIFIER = "ssh_backup"
    DESCRIPTION = "Save files on remote computer via SSH"
    ACT = ssh_backup


class RestoreSshBackup(BaseAction):
    @staticmethod
    @deploy
    def restore_ssh_backup(
        restore_location: str,
        server_ip: str,
        username: str,
        password: str,
        ssh_fingerprint: str,
    ) -> None:
        command = _make_ssh_backup(
            restore_location,
            server_ip,
            username,
            password,
            ssh_fingerprint,
            reverse=True,
        )
        server.shell(
            commands=[command],
            name="Restore backup file over SSH",
        )

    IDENTIFIER = "restore_ssh_backup"
    DESCRIPTION = "Restore files on localhost from remote computer over SSH"
    ACT = restore_ssh_backup


class GoogleDriveBackup(BaseAction):
    @staticmethod
    @deploy
    def google_drive_backup(
        source_file: str, backup_location: str, oauth_token: str
    ) -> None:
        command = _make_googledrive_backup(
            source_file, backup_location, oauth_token
        )
        server.shell(
            commands=[command],
            name="Save file to Google Drive",
        )

    IDENTIFIER = "google_drive_backup"
    DESCRIPTION = "Save files to Google Drive"
    ACT = google_drive_backup


class RestoreGoogleDriveBackup(BaseAction):
    @staticmethod
    @deploy
    def restore_google_drive_backup(
        restore_location: str, backup_location: str, oauth_token: str
    ) -> None:
        command = _make_googledrive_backup(
            restore_location, backup_location, oauth_token, reverse=True
        )
        server.shell(
            commands=[command],
            name="Get backup file from Google Drive",
        )

    IDENTIFIER = "restore_google_drive_backup"
    DESCRIPTION = "Get backup file from Google Drive"
    ACT = restore_google_drive_backup


# Information classes definitions


class BinaryArchitectureFact(FactBase):
    command = "dpkg --print-architecture"

    @staticmethod
    def process(output: typing.List[str]) -> str:
        architecture = output[0]

        if architecture in ["386", "amd64", "arm64", "armv6"]:
            return architecture


class BinaryArchitecture(BaseInformation):
    IDENTIFIER = "architecture"
    DESCRIPTION = "Binary's architecture"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.READ_ONLY,
        InformationProperties.AUTO_GENERATED_BEFORE_INSTALL,
    ]
    DEFAULT_VALUE = None
    GETTER = BinaryArchitectureFact
    SETTER = None


class EncryptionModule(BaseInformation):
    @staticmethod
    @deploy
    def set_configuration(
        old_value: typing.Any, new_value: typing.Any
    ) -> None:
        _save_current_configuration()

    @staticmethod
    @deploy
    class EncryptionModuleValue(FactBase):
        command = (
            "cat /opt/mutablesecurity/duplicati/duplicati.conf             |  "
            "    grep 'encryption_module' | cut -d : -f 2"
        )

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return int(output[0])

    IDENTIFIER = "encryption_module"
    DESCRIPTION = "Algorithm used for encrytion"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "aes"
    GETTER = EncryptionModuleValue
    SETTER = set_configuration


class CompressionModule(BaseInformation):
    @staticmethod
    @deploy
    def set_configuration(
        old_value: typing.Any, new_value: typing.Any
    ) -> None:
        _save_current_configuration()

    @staticmethod
    @deploy
    class CompressionModuleValue(FactBase):
        command = "echo 'hi'"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return (
                "cat /opt/mutablesecurity/duplicati/duplicati.conf | grep     "
                "            'compression_module' | cut -d : -f 2"
            )

    IDENTIFIER = "compression_module"
    DESCRIPTION = "Algorithm used from compression"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "zip"
    GETTER = CompressionModuleValue
    SETTER = set_configuration


class SkipFilesLarger(BaseInformation):
    @staticmethod
    @deploy
    def set_configuration(
        old_value: typing.Any, new_value: typing.Any
    ) -> None:
        _save_current_configuration()

    @staticmethod
    @deploy
    class SkipLargerFilesValue(FactBase):
        command = "echo 'hi'"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return (
                "cat /opt/mutablesecurity/duplicati/duplicati.conf | grep     "
                "            'skip_files_larger_than' | cut -d : -f 2"
            )

    IDENTIFIER = "skip_files_larger_than"
    DESCRIPTION = (
        "Don't backup files which heve size larger than corresponding value"
    )
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "2GB"
    GETTER = SkipLargerFilesValue
    SETTER = set_configuration


class ExcludeFilesAttributes(BaseInformation):
    @staticmethod
    @deploy
    def set_configuration(
        old_value: typing.Any, new_value: typing.Any
    ) -> None:
        _save_current_configuration()

    @staticmethod
    @deploy
    class ExcludeFilesValue(FactBase):
        command = "echo 'hi'"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return (
                "cat /opt/mutablesecurity/duplicati/duplicati.conf | grep     "
                "            'exclude_files_attributes' | cut -d : -f 2"
            )

    IDENTIFIER = "exclude_files_attributes"
    DESCRIPTION = "Don't backup files which have this attribute"
    INFO_TYPE = StringListDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.OPTIONAL,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = "Temporary"
    GETTER = ExcludeFilesValue
    SETTER = set_configuration


class Passphrase(BaseInformation):
    @staticmethod
    @deploy
    def set_configuration(
        old_value: typing.Any, new_value: typing.Any
    ) -> None:
        _save_current_configuration()

    @staticmethod
    @deploy
    class PassphraseValue(FactBase):
        command = (
            "cat /opt/mutablesecurity/duplicati/duplicati.conf |              "
            "       grep 'passphrase' | cut -d : -f 2"
        )

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return "asdsa"

    IDENTIFIER = "passphrase"
    DESCRIPTION = "This value represents the value by encryption key"
    INFO_TYPE = StringDataType
    PROPERTIES = [
        InformationProperties.CONFIGURATION,
        InformationProperties.MANDATORY,
        InformationProperties.WITH_DEFAULT_VALUE,
        InformationProperties.NON_DEDUCTIBLE,
        InformationProperties.WRITABLE,
    ]
    DEFAULT_VALUE = None
    GETTER = PassphraseValue
    SETTER = set_configuration


# Logs classes definitions
class DefaultLogs(BaseLog):
    class DefaultLogsFact(FactBase):
        command = "cat /var/log/duplicati.log"

        @staticmethod
        def process(output: typing.List[str]) -> str:
            return "\n".join(output)

    IDENTIFIER = "logs"
    DESCRIPTION = "Default log location"
    FACT = DefaultLogsFact


# Tests
class SupportedArchitecture(BaseTest):
    class SupportedArchitectureFact(BinaryArchitectureFact):
        @staticmethod
        def process(  # type: ignore[override]
            output: typing.List[str],
        ) -> bool:
            architecture = BinaryArchitectureFact.process(output)

            return architecture is not None

    IDENTIFIER = "supported_architecture"
    DESCRIPTION = "Checks if there is any build for this architecture."
    TEST_TYPE = TestType.REQUIREMENT
    FACT = SupportedArchitectureFact


class ClientCommandPresence(BaseTest):
    IDENTIFIER = "command"
    DESCRIPTION = "Checks if the Duplicati cli is registered as a command."
    TEST_TYPE = TestType.PRESENCE
    FACT = PresentCommand
    FACT_ARGS = ("duplicati-cli --help",)


class ClientEncryption(BaseTest):
    class LocalEncryptionTest(FactBase):
        @staticmethod
        def command() -> list:
            backup_path = "/tmp/backup" + uuid.uuid4().hex
            file_test = "/tmp/file.txt"
            local_backup = _make_local_backup(file_test, backup_path)
            execute_command = [
                "echo 'Hi' >> f{file_test}",
                local_backup,
                f" && dir {backup_path} |grep '*.f{EncryptionModule.get()}'",
                f"rm -r {backup_path}",
            ]
            return execute_command

        @staticmethod
        def process(output: typing.List[str]) -> bool:
            return int(output[0]) != 0

    IDENTIFIER = "local_encrypted_backup"
    DESCRIPTION = "Checks if the Duplicati local encryption works"
    TEST_TYPE = TestType.SECURITY
    FACT = LocalEncryptionTest


# Solution class definition


class Duplicati(BaseSolution):
    INFORMATION = [
        BinaryArchitecture,  # type: ignore[list-item]
        CompressionModule,  # type: ignore[list-item]
        EncryptionModule,
        ExcludeFilesAttributes,  # type: ignore[list-item]
        SkipFilesLarger,  # type: ignore[list-item]
        Passphrase,  # type: ignore[list-item]
    ]
    TESTS = [
        ClientEncryption,  # type: ignore[list-item]
        SupportedArchitecture,  # type: ignore[list-item]
        ClientCommandPresence,  # type: ignore[list-item]
    ]
    LOGS = [
        DefaultLogs,  # type: ignore[list-item]
    ]
    ACTIONS = [
        LocalBackup,  # type: ignore[list-item]
        RestoreLocalBackup,  # type: ignore[list-item]
        SshBackup,  # type: ignore[list-item]
        RestoreSshBackup,  # type: ignore[list-item]
        GoogleDriveBackup,  # type: ignore[list-item]
        RestoreGoogleDriveBackup,  # type: ignore[list-item]
    ]

    @staticmethod
    @deploy
    def _install() -> None:
        architecture = BinaryArchitecture.get()
        if not architecture:
            raise IncompatibleArchitectureException()

        release_url = (
            "https://updates.duplicati.com/beta/duplicati_2.0.6.3-1_all.deb"
        )
        apt.deb(
            name="Install Duplicati via deb",
            src=release_url,
        )

        _save_current_configuration()

    @staticmethod
    @deploy
    def _uninstall(remove_logs: bool = True) -> None:
        apt.packages(
            packages=["duplicati"],
            present=False,
            extra_uninstall_args="--purge",
            name="Uninstalls Duplicati via apt.",
        )
        files.directory(
            name="Remove duplicati executable and configuration.",
            path="/opt/mutablesecurity/duplicati",
            present=False,
        )
        files.directory(
            name="Remove duplicati log file.",
            path="/var/log/duplicati.log",
            present=False,
            force=True,
        )

    @staticmethod
    @deploy
    def _update() -> None:
        apt.packages(
            packages=["duplicati"],
            latest=True,
            name="Update duplicati via apt.",
        )


def _load_default_param() -> dict:
    command_params = {
        "encryptionModule": " --encryption-module=" + EncryptionModule.get(),
        "compressionModule": " --compression-module="
        + CompressionModule.get(),
        "skipFilesLrger": " --skip-files-larger-than=" + SkipFilesLarger.get(),
        "excludeFilesAtt": " --exclude-files-attributes="
        + ExcludeFilesAttributes.get(),
        "logFile": " --log-file=/var/log/duplicati.log",
    }

    if EncryptionModule.get() == "none":
        command_params["encryptionModule"] = " "
    if CompressionModule.get() == "none":
        command_params["compressionModule"] = " "

    return command_params


def _make_local_backup(
    source_file: str, backup_location: str, reverse: bool = False
) -> str:
    params = _load_default_param()
    operation = 'backup "'

    if reverse:
        operation = 'restore "'
        restore_location = '" --restore-path="' + backup_location
        backup_location = restore_location

    command = (
        "duplicati-cli "
        + operation
        + backup_location
        + '" "'
        + source_file
        + '" '
        + " --passphrase="
        + Passphrase.get()
        + " ".join(params.values())
    )
    return command


def _make_ssh_backup(
    source_file: str,
    server_ip: str,
    username: str,
    password: str,
    ssh_fingerprint: str,
    reverse: bool = False,
) -> str:
    username = " --auth-username=" + username
    password = " --auth-password=" + password
    server_ip = "ssh://" + server_ip + '" '
    params = _load_default_param()
    operation = 'backup "'

    if reverse:
        operation = "restore "
        location = ' --restore-path="' + server_ip
        server_ip = location

    command = (
        "duplicati-cli "
        + operation
        + server_ip
        + '"'
        + source_file
        + '" '
        + username
        + password
        + " --passphrase="
        + Passphrase.get()
        + ' --ssh-fingerprint="'
        + ssh_fingerprint
        + '"'
        + " ".join(params.values())
    )
    return command


def _make_googledrive_backup(
    source_file: str,
    backup_location: str,
    oauth_token: str,
    reverse: bool = False,
) -> str:
    backup_path = "googledrive://" + backup_location
    authid = " --authid='" + oauth_token+"'"
    params = _load_default_param()
    operation = 'backup "'

    if reverse:
        operation = 'restore '
        restore_location = ' --restore-path="' + source_file
        source_file = restore_location

    command = (
        "duplicati-cli "
        + operation
        + source_file
        + '" "'
        + backup_path
        + '" '
        + authid
        + " --passphrase="
        + Passphrase.get()
        + " ".join(params.values())
    )
    return command


def _save_current_configuration() -> None:
    template_path = os.path.join(
        os.path.dirname(__file__), "files/duplicati.conf.j2"
    )
    j2_values = {
        "encryption_module": EncryptionModule.get(),
        "compression_module": CompressionModule.get(),
        "skip_files_larger_than": SkipFilesLarger.get(),
        "exclude_files_attributes": ExcludeFilesAttributes.get(),
        "passphrase": Passphrase.get(),
    }
    files.template(
        src=template_path,
        dest="/opt/mutablesecurity/duplicati/duplicati.conf",
        configuration=j2_values,
        name="Copy the generated configuration into Duplicati's folder.",
    )
