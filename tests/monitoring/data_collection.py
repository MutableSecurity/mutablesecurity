"""Module testing the data collection."""

from mutablesecurity.monitoring.data_collection import DataCollector


def test_collection() -> None:
    """Tests if all data is collected."""
    collector = DataCollector()

    data = collector.get_all()

    assert len(data.keys()) == len(
        collector.METRICS
    ), "Some metrics were not collected."

    for key, value in data.items():
        assert value is not None, f"The key '{key}' is null"
