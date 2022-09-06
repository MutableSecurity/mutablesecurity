"""Module collecting system and usage information."""
import platform
import sys
import time
import typing

from mutablesecurity import VERSION, config


class DataCollector:
    """Class getting all the available information."""

    METRICS: typing.List[typing.Type] = []

    @classmethod
    def add_metric(
        cls: typing.Type["DataCollector"], metric_class: typing.Type
    ) -> None:
        """Add a metric to be collected.

        Args:
            metric_class (typing.Type): Class implementing a metric
        """
        cls.METRICS.append(metric_class)

    def get_all(self) -> dict:
        """Get all available metrics.

        Returns:
            dict: Dictionary containing all the collected information
        """
        return {
            m.IDENTIFIER: m._get()  # pylint: disable=protected-access
            for m in self.METRICS
        }


class Metric:
    """Base metric."""

    IDENTIFIER = "metric"

    @classmethod
    def __init_subclass__(cls: typing.Type["Metric"]) -> None:
        """Register a subclass as a metric."""
        super().__init_subclass__()

        DataCollector.add_metric(cls)

    @staticmethod
    def _get() -> str:
        raise NotImplementedError()


class OperatingSystem(Metric):
    """Operating system."""

    IDENTIFIER = "os"

    @staticmethod
    def _get() -> str:
        return platform.version()


class PythonVersion(Metric):
    """Python version."""

    IDENTIFIER = "py_version"

    @staticmethod
    def _get() -> str:
        python_info = sys.version_info

        return f"{python_info.major}.{python_info.minor}.{python_info.micro}"


class PackageVersion(Metric):
    """MutableSecurity version."""

    IDENTIFIER = "package_version"

    @staticmethod
    def _get() -> str:
        return VERSION


class IsDeveloper(Metric):
    """Metric indicating if the user is a developer."""

    IDENTIFIER = "is_dev"

    @staticmethod
    def _get() -> str:
        return str(config.developer_mode)


class CommandLine(Metric):
    """Command line, based on argv."""

    IDENTIFIER = "command"

    @staticmethod
    def _get() -> str:
        return " ".join(sys.argv)


class Timezone(Metric):
    """Timezone."""

    IDENTIFIER = "timezone"

    @staticmethod
    def _get() -> str:
        return time.tzname[0]
