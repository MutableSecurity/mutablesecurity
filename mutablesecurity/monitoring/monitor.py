"""Module initializing Sentry for crash reporting and sending usage data."""
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

    def __init__(self) -> None:
        """Initialize the instance."""
        if not self.__is_monitoring_enabled():
            return

        self.__send_custom_usage_data()
        self.__init_sentry()

    def __is_monitoring_enabled(self):
        return config.application_monitoring

    def __init_sentry(self) -> None:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=1.0,
        )

    def __send_custom_usage_data(self) -> None:
        data = DataCollector().get_all()
        headers = {
            "Content-Type": "application/json",
        }

        requests.post(
            CLOUD_FUNCTION_URL,
            json=data,
            headers=headers,
        )
