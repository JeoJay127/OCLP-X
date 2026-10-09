"""
platform_probe.py: Host platform identification with vendor fallbacks
"""

from typing import Optional, Union

from ..constants import Constants
from ..detections import ioreg


APPLE_VENDORS = ("apple", "apple inc.", "apple computer, inc.")


def _normalize_vendor(value: Union[str, bytes, None]) -> Optional[str]:
    if isinstance(value, bytes):
        value = value.replace(b"\0", b"").decode("utf-8", errors="ignore")
    if isinstance(value, str):
        return value.replace("\0", "").strip() or None
    return None


def _read_vendor(path: bytes, property_name: str) -> Optional[str]:
    entry = ioreg.IORegistryEntryFromPath(ioreg.kIOMasterPortDefault, path)
    if not entry:
        return None

    try:
        value = ioreg.corefoundation_to_native(ioreg.IORegistryEntryCreateCFProperty(
            entry, property_name, ioreg.kCFAllocatorDefault, ioreg.kNilOptions
        ))
        return _normalize_vendor(value)
    finally:
        ioreg.IOObjectRelease(entry)


def is_hackintosh(global_constants: Constants) -> Optional[bool]:
    """
    Reuse official host detection when firmware information is available.
    Otherwise, read firmware and platform vendors without relying on SMBIOS model IDs.
    """
    if _normalize_vendor(global_constants.computer.firmware_vendor):
        return global_constants.host_is_hackintosh

    for path, property_name in (
        (b"IODeviceTree:/efi", "firmware-vendor"),
        (b"IODeviceTree:/", "manufacturer"),
    ):
        vendor = _read_vendor(path, property_name)
        if vendor:
            return vendor.casefold() not in APPLE_VENDORS

    return None
