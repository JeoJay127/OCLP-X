import platform
from . import monkey_patch

def apply_patch_version():
    monkey_patch.patch_patcher_version()

def apply_commit_info_patch():
    monkey_patch.patch_commit_info()
def kernel_major() -> int:
    """
    major kernel version
    """

    release_version = platform.uname().release
    major_version = release_version.split('.')[0]

    return int(major_version)

def apply_intel_wifi_patch(): 
    # 24.0.0 (macOS Sequoia)
    if kernel_major() >= 24:
        monkey_patch.patch_modern_wireless()
        print("Intel Wi-Fi patch applied for macOS Sequoia or newer.")
    else:
        print("Intel Wi-Fi patch skipped, macOS version is older than Sequoia.")

def apply_atheros_patch():
    monkey_patch.patch_atheros_ids()

def apply_brcm_patch():
    monkey_patch.patch_broadcom_ids()

def apply_update_patch():
    monkey_patch.patch_start_auto_patch_url()
    monkey_patch.patch_on_update()
    monkey_patch.patch_update_url()
     
def apply_patch():
    apply_commit_info_patch()
    apply_patch_version()
    apply_intel_wifi_patch()
    apply_atheros_patch()
    apply_brcm_patch()
    apply_update_patch()

print("Monkey patching beginning.")
apply_patch()
print("Monkey patching finished.")
