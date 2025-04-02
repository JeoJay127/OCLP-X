from opencore_legacy_patcher.sys_patch.patchsets.hardware.networking.modern_wireless import ModernWireless
from opencore_legacy_patcher.custom.intel_wireless import IntelWireless
from opencore_legacy_patcher.datasets import pci_data
from opencore_legacy_patcher.detections import device_probe


CUSTOM_REPO = "JeoJay127/OCLP-X"

CUSTOM_REPO_LATEST_RELEASE_URL = f"https://api.github.com/repos/{CUSTOM_REPO}/releases/latest"

def patch_patcher_version():
    from opencore_legacy_patcher import constants
    Constants = constants.Constants
    original_init = Constants.__init__

    def modified_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.copyright_date = "Copyright © 2020-2025 Dortania(Modified by JeoJay)"
        self.patcher_name = "OCLP(Modified by JeoJay)"

    Constants.__init__ = modified_init
    print("Patcher version dynamically set to:", Constants().patcher_version)

def patch_commit_info():

    from opencore_legacy_patcher.support.commit_info import ParseCommitInfo
    original_generate_commit_info = ParseCommitInfo.generate_commit_info
    def custom_generate_commit_info(self) -> tuple:
        result = original_generate_commit_info(self)
        return ("refs/tags", result[1], result[2])

    ParseCommitInfo.generate_commit_info = custom_generate_commit_info
    print("generate_commit_info method has been patched.")

def patch_modern_wireless():

    def name(self) -> str:
        """
        Display name for end users
        """     
        if isinstance(self._computer.wifi, IntelWireless):
            return f"{self.hardware_variant()}: Intel Wi-Fi"
       
        elif isinstance(self._computer.wifi, device_probe.Broadcom):
            return f"{self.hardware_variant()}: Broadcom Wi-Fi"
        else:
            return f"{self.hardware_variant()}: Modern Wi-Fi"
    def patched_present(self) -> bool:
        
        supported_chipsets = {
            device_probe.Broadcom.Chipsets.AirPortBrcm4360,
            device_probe.Broadcom.Chipsets.AirportBrcmNIC,
            device_probe.Broadcom.Chipsets.AirPortBrcmNICThirdParty,
            IntelWireless.Chipsets.IntelWirelessIDs 
        }

        wifi = self._computer.wifi 
        
        return isinstance(wifi, (device_probe.Broadcom, IntelWireless)) and wifi.chipset in supported_chipsets

    ModernWireless.name = name 
    ModernWireless.present = patched_present
    print("ModernWireless class has been patched successfully.")

def patch_atheros_ids():

    atheros_ids = pci_data.atheros_ids
    new_atheros_wifi_ids = [
        # AirPortAtheros40 IDs
        0x002A,  # AR928X
        0x002B,  # AR9285
        0x002E,  # AR9287
        0x001C,  # AR242x / AR542x
        0x0023,  # AR5416 - never used by Apple
        0x0024,  # AR5418
        0x0030,  # AR93xx/AR9380
        0x0032,  # AR9485
        0x0033,  # AR958x
        0x0034,  # AR9462
        0x0036,  # AR9565
        0x0037,  # AR9485
    ]
    
    atheros_ids.AtherosWifi = new_atheros_wifi_ids
    
    print("AtherosWifi have been patched successfully.")

def patch_broadcom_ids():

    broadcom_ids = pci_data.broadcom_ids
    
    new_brcm_nic_ids = [
        # AirPortBrcmNIC IDs
        0x43BA,  # BCM43602
        0x43A3,  # BCM4350
        0x43A0,  # BCM4360
        0x43B1,  # BCM4352
        0x43B2,  # BCM4352 (2.4 GHz)
        0x4357,  # BCM43225
    ]
    
    broadcom_ids.AirPortBrcmNIC = new_brcm_nic_ids
    
    print("AirPortBrcmNIC have been patched successfully.")

    
def patch_update_url():
    from opencore_legacy_patcher.support import updates
    
    original_check_binary_updates = updates.CheckBinaryUpdates.check_binary_updates

    def custom_check_binary_updates(self):
        
        updates.REPO_LATEST_RELEASE_URL = CUSTOM_REPO_LATEST_RELEASE_URL

        result = original_check_binary_updates(self)

        if result:
            
            result["Github Link"] = result["Github Link"].replace("dortania/OpenCore-Legacy-Patcher", CUSTOM_REPO)
        return result

    updates.CheckBinaryUpdates.check_binary_updates = custom_check_binary_updates
    print("Update URL has been permanently patched to:", CUSTOM_REPO_LATEST_RELEASE_URL)

def patch_start_auto_patch_url():
    import importlib
    from opencore_legacy_patcher.sys_patch.auto_patcher.start import StartAutomaticPatching
    
    original_start_auto_patch = StartAutomaticPatching.start_auto_patch

    def custom_start_auto_patch(self):
        
        custom_url = CUSTOM_REPO_LATEST_RELEASE_URL
    
        import inspect
        source_lines = inspect.getsource(original_start_auto_patch).splitlines()
        new_source_lines = []
        for line in source_lines:
            if "url = " in line:
                
                indent = line[:len(line) - len(line.lstrip())]
                
                new_line = f"{indent}url = '{custom_url}'"
                new_source_lines.append(new_line)
            else:
                new_source_lines.append(line)
       
        new_source = '\n'.join(new_source_lines).strip() + '\n'
        
        new_code = compile(new_source, '<string>', 'exec')
    
        namespace = globals().copy()
    
        required_modules = [
            'wx', 'wx.html2', 'logging', 'plistlib', 'requests', 'markdown2',
            'subprocess', 'webbrowser', '...constants', '...datasets.css_data',
            '...wx_gui.gui_entry', '...wx_gui.gui_support',
            '...support.utilities', '...support.updates',
            '...support.global_settings', '...support.network_handler',
            '..patchsets.HardwarePatchsetDetection', '..patchsets.HardwarePatchsetValidation'
        ]
    
        for module_name in required_modules:
            try:
                if module_name.startswith('..'):
                    
                    module = importlib.import_module(module_name, package=__package__)
                else:
                    
                    module = __import__(module_name)
                
                namespace[module_name.split('.')[-1]] = module
            except ImportError:
                print(f"Warning: Module {module_name} could not be imported.")
    
        exec(new_code, namespace)
    
        new_function = namespace['start_auto_patch']
        
        return new_function(self)

    
    StartAutomaticPatching.start_auto_patch = custom_start_auto_patch
    print("start_auto_patch method's url has been patched.")

def patch_on_update():
    import importlib
    from opencore_legacy_patcher.wx_gui.gui_main_menu import MainFrame
    
    original_on_update = MainFrame.on_update

    def custom_on_update(self, oclp_url: str, oclp_version: str, oclp_github_url: str):
        
        custom_url = CUSTOM_REPO_LATEST_RELEASE_URL

        if "/releases/" in oclp_github_url:
                parts = oclp_github_url.rsplit('/', 1)
                if len(parts) == 2 and not parts[1].startswith('v'):
                    oclp_github_url = f"{parts[0]}/v{parts[1]}"
        
        import inspect
        source_lines = inspect.getsource(original_on_update).splitlines()
        new_source_lines = []
        for line in source_lines:
            if "url = " in line:
               
                indent = line[:len(line) - len(line.lstrip())]
                
                new_line = f"{indent}url = '{custom_url}'"
                new_source_lines.append(new_line)
            else:
                new_source_lines.append(line)
        
        new_source = '\n'.join(new_source_lines).strip() + '\n'
     
        new_code = compile(new_source, '<string>', 'exec')
     
        namespace = globals().copy()
     
        required_modules = [
            'wx', 'wx.html2', 'sys', 'logging', 'requests', 'markdown2',
            'threading', 'webbrowser', '..constants', '..support.global_settings',
            '..support.updates', '..datasets.os_data', '..datasets.css_data',
            '..wx_gui.gui_build', '..wx_gui.gui_macos_installer_download',
            '..wx_gui.gui_support', '..wx_gui.gui_help', '..wx_gui.gui_settings',
            '..wx_gui.gui_sys_patch_display', '..wx_gui.gui_update'
        ]
    
        for module_name in required_modules:
            try:
                if module_name.startswith('..'):
                    
                    module = importlib.import_module(module_name, package=__package__)
                else:
                    
                    module = __import__(module_name)
                
                namespace[module_name.split('.')[-1]] = module
            except ImportError:
                print(f"Warning: Module {module_name} could not be imported.")
    
        exec(new_code, namespace)
       
        new_function = namespace['on_update']
    
        return new_function(self, oclp_url, oclp_version, oclp_github_url)

    MainFrame.on_update = custom_on_update
    print("on_update method has been patched.")


