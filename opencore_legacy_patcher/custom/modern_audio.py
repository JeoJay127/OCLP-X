"""
modern_audio.py: Modern Audio detection
"""

from ..sys_patch.patchsets.hardware.base import BaseHardware, HardwareVariant

from ..sys_patch.patchsets.base import PatchType

from ..constants import Constants

from ..datasets.os_data import os_data


class ModernAudio(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Modern Audio"


    def present(self) -> bool:
        """
        Targeting Modern Audio
        """
        return self._xnu_major >= os_data.tahoe.value

    def native_os(self) -> bool:
        """
        - Apple has dropped support for Modern Audio on macOS Tahoe 26 Beta 2
        """

        return self._xnu_major < os_data.tahoe.value

    def requires_kernel_debug_kit(self):
        """
        - Apple has dropped support for Modern Audio on macOS Tahoe 26 Beta 2
        - This requires a kernel debug kit
        """
        
        return True
    
    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.AUDIO

    def patches(self) -> dict:
        """
        Patches for Modern Audio
        """
        return {
            "Modern Audio": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleHDA.kext":      "26.0 Beta 1",
                    },
                },
            },
        }