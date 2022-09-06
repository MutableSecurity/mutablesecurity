"""Module initializing Sentry for crash reporting and sending usage data."""
import typing

import requests
import sentry_sdk

from mutablesecurity import config
from mutablesecurity.monitoring.data_collection import DataCollector

SENTRY_DSN = (
    "https://fdb09fcb0cd14638a3f583bab7a6c822@o1397044.ingest.sentry.io/"
    "6721995"
)
CLOUD_FUNCTION_URL = (
    "https://europe-central2-mutablesecurity.cloudfunctions.net/"
    "store_monitoring_data"
)


class Monitor:
    """Class wrapping Sentry and our custom Google Cloud Function."""

    enabled: bool

    def __init__(self) -> None:
        """Initialize the instance."""
        self.enabled = self.__is_monitoring_enabled()

        if self.enabled:
            self.__init_sentry()

    @staticmethod
    def __is_monitoring_enabled() -> bool:
        return config.application_monitoring and not config.developer_mode

    @staticmethod
    def __init_sentry() -> None:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=1.0,
        )

    def report(
        self,
        module: typing.Optional[str] = None,
        operation: typing.Optional[str] = None,
    ) -> None:
        """Report data.

        Args:
            module (str): Used module
            operation (str): Used operation
        """
        if not self.enabled:
            return

        data = Monitor.__get_enhanced_data(module, operation)
        headers = {
            "Content-Type": "application/json",
        }

        requests.post(
            CLOUD_FUNCTION_URL,
            json=data,
            headers=headers,
        )

    @staticmethod
    def __get_enhanced_data(
        module: typing.Optional[str], operation: typing.Optional[str]
    ) -> dict:
        data = DataCollector().get_all()

        data["module"] = module
        data["operation"] = operation

        return data
