"""Quirk for the unvgwjvxa1dgmzjz smart litter box.

The cloud definition omits the device status, the daily visit counter and a
RAW payload containing the latest cat weight and visit duration. It also
labels dpId 7 as the daily counter although that datapoint reports deltas.

See https://github.com/home-assistant/core/pull/193823.
"""

from tuya_device_handlers import TUYA_QUIRKS_REGISTRY
from tuya_device_handlers.builder import DeviceQuirk
from tuya_device_handlers.const import DPMode

(
    DeviceQuirk()
    .applies_to(product_id="unvgwjvxa1dgmzjz")
    .remove_dpid(dpid=7, dpcode="excretion_times_day")
    .add_dpid_integer(
        dpid=7,
        dpcode="excretion_times_total",
        dpmode=DPMode.READ,
        unit="times",
        min=0,
        max=2147483647,
        scale=0,
        step=1,
        report_type="sum",
    )
    .add_dpid_enum(
        dpid=24,
        dpcode="status",
        dpmode=DPMode.READ,
        enum_range=[
            "IDLE",
            "CAT_ENTER",
            "CAT_LEAVE",
            "CLEANING",
            "CLEAN_STOP",
            "APPEASING",
            "APPEASE_STOP",
        ],
    )
    .add_dpid_integer(
        dpid=106,
        dpcode="excretion_times_day",
        dpmode=DPMode.READ,
        unit="times",
        min=0,
        max=60,
        scale=0,
        step=1,
    )
    .add_dpid_raw(
        dpid=113,
        dpcode="cat_data",
        dpmode=DPMode.READ,
    )
    .register(TUYA_QUIRKS_REGISTRY)
)
