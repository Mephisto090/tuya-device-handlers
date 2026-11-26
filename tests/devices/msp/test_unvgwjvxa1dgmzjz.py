"""Tests for the unvgwjvxa1dgmzjz smart litter box quirk."""

from unittest.mock import patch

from tests import create_device
from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.device_wrapper.sensor import (
    CatLitterBoxDurationRawWrapper,
    CatLitterBoxWeightRawWrapper,
    DeltaIntegerWrapper,
)
from tuya_device_handlers.registry import QuirksRegistry
from tuya_device_handlers.type_information import IntegerTypeInformation


def test_quirk_adds_missing_datapoints(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The quirk adds the datapoints omitted by the cloud definition."""
    device = create_device("msp_unvgwjvxa1dgmzjz.json")

    with patch.dict(TUYA_QUIRKS_REGISTRY._quirks, clear=True):
        assert 24 not in device.local_strategy
        assert 106 not in device.local_strategy
        assert 113 not in device.local_strategy

    filled_quirks_registry.initialise_device_quirk(device)

    assert device.local_strategy[24]["status_code"] == "status"
    assert device.local_strategy[106]["status_code"] == "excretion_times_day"
    assert device.local_strategy[113]["status_code"] == "cat_data"
    assert device.status_range["excretion_times_day"].report_type is None
    assert device.status_range["excretion_times_total"].report_type == "sum"


def test_quirk_separates_daily_and_total_counts(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The daily counter is direct while dpId 7 remains a delta total."""
    device = create_device("msp_unvgwjvxa1dgmzjz.json")
    filled_quirks_registry.initialise_device_quirk(device)

    daily_type = IntegerTypeInformation.find_dpcode(
        device, "excretion_times_day"
    )
    assert daily_type is not None
    assert daily_type.report_type is None

    total_type = IntegerTypeInformation.find_dpcode(
        device, "excretion_times_total"
    )
    assert total_type is not None
    total_wrapper = DeltaIntegerWrapper(
        total_type.dpcode,
        total_type,
    )

    device.status["excretion_times_day"] = 2
    assert daily_type.read_device_value(device) == 2

    device.status["excretion_times_total"] = 1
    assert not total_wrapper.skip_update(
        device,
        ["excretion_times_total"],
        {"excretion_times_total": 1},
    )
    assert total_wrapper.read_device_status(device) == 1
    assert not total_wrapper.skip_update(
        device,
        ["excretion_times_total"],
        {"excretion_times_total": 2},
    )
    assert total_wrapper.read_device_status(device) == 2


def test_quirk_decodes_visit_payload(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """Weight and duration are decoded from the shared RAW payload."""
    device = create_device("msp_unvgwjvxa1dgmzjz.json")
    filled_quirks_registry.initialise_device_quirk(device)
    device.status["cat_data"] = "AAAF2ABW"

    weight_wrapper = CatLitterBoxWeightRawWrapper.find_dpcode(
        device, "cat_data"
    )
    duration_wrapper = CatLitterBoxDurationRawWrapper.find_dpcode(
        device, "cat_data"
    )

    assert weight_wrapper is not None
    assert duration_wrapper is not None
    assert weight_wrapper.read_device_status(device) == 1496
    assert duration_wrapper.read_device_status(device) == 86


def test_quirk_maps_status_updates(
    filled_quirks_registry: QuirksRegistry,
) -> None:
    """The previously unknown status datapoint is exposed as an enum."""
    device = create_device("msp_unvgwjvxa1dgmzjz.json")
    filled_quirks_registry.initialise_device_quirk(device)

    assert "CAT_ENTER" in device.status_range["status"].values
    assert "APPEASING" in device.status_range["status"].values
    assert "APPEASE_STOP" in device.status_range["status"].values
    assert "RESET_STOP" in device.status_range["status"].values
    assert device.local_strategy[24]["status_code"] == "status"
