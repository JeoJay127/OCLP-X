from dataclasses import dataclass, field
from typing import ClassVar
import enum

from opencore_legacy_patcher.detections.device_probe import WirelessCard
from .intel_wireless_ids import intel_wireless_ids

@dataclass
class IntelWireless(WirelessCard):
    # Intel Vendor ID
    VENDOR_ID: ClassVar[int] = 0x8086  
    class Chipsets(enum.Enum):
        IntelWirelessIDs = "IntelWireless supported"
        Unknown = "Unknown"

    chipset: Chipsets = field(init=False)
    def detect_chipset(self):
        """
        Detect whether it is an Intel wireless network card based on the PCI device ID.
        """
        if self.device_id in intel_wireless_ids.IntelWirelessCardIDs:
            self.chipset = IntelWireless.Chipsets.IntelWirelessIDs
        else:
            self.chipset = IntelWireless.Chipsets.Unknown
