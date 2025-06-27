from opencore_legacy_patcher.datasets import pci_data
from opencore_legacy_patcher.detections import device_probe



CUSTOM_REPO = "JeoJay127/OCLP-X"

CUSTOM_REPO_LATEST_RELEASE_URL = f"https://api.github.com/repos/{CUSTOM_REPO}/releases/latest"


def patch_patcher_version():
    import requests
    from opencore_legacy_patcher import constants
    from opencore_legacy_patcher.datasets import os_data
    Constants = constants.Constants
    orig_init = Constants.__init__
    def modified_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        self.copyright_date = "Copyright © 2020-2025 Dortania(Modified by JeoJay)"
        self.patcher_name = "OCLP(Modified by JeoJay)"
        self.legacy_accel_support = [
            os_data.os_data.big_sur,
            os_data.os_data.monterey,
            os_data.os_data.ventura,
            os_data.os_data.sonoma,
            os_data.os_data.sequoia,
            os_data.os_data.tahoe,
        ]
        try:
            response = requests.get(f'https://raw.githubusercontent.com/{CUSTOM_REPO}/main/CHANGELOG.md')
            response.raise_for_status()
            lines = response.text.splitlines()
            new_version = None
            for line in lines:
                if line.startswith('## '):
                    new_version = line.split(' ')[1]
                    break

            if new_version:
                def version_to_tuple(version):
                    return tuple(map(int, version.split('.')))

                current_version_tuple = version_to_tuple(self.patcher_version)
                new_version_tuple = version_to_tuple(new_version)

                if new_version_tuple > current_version_tuple:
                    self.patcher_version = new_version

        except Exception as e:
            print(f"Failed to fetch the latest version number: {e}")
            pass

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
    from opencore_legacy_patcher.sys_patch.patchsets.hardware.networking.modern_wireless import ModernWireless
    from opencore_legacy_patcher.custom.intel_wireless import IntelWireless
    from opencore_legacy_patcher.datasets.os_data import os_data
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
        if self._xnu_major >= os_data.tahoe.value:
            return False
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

def patch_legacy_wireless():
    from opencore_legacy_patcher.sys_patch.patchsets.hardware.networking.legacy_wireless import LegacyWireless
    from opencore_legacy_patcher.datasets.os_data import os_data
    def name(self) -> str:
        """
        Display name for end users
        """     
        if (
            isinstance(self._computer.wifi, device_probe.Broadcom)
            and self._computer.wifi.chipset in [device_probe.Broadcom.Chipsets.AirPortBrcm4331, device_probe.Broadcom.Chipsets.AirPortBrcm43224]
        ):
            return f"{self.hardware_variant()}: Legacy Broadcom Wi-Fi"
        elif (
            isinstance(self._computer.wifi, device_probe.Atheros)
            and self._computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40
        ):
            return f"{self.hardware_variant()}: Legacy Atheros Wi-Fi"
        else:
            return f"{self.hardware_variant()}: Legacy Wi-Fi"
   
    def present(self) -> bool:
        """
        Targeting Legacy Wireless
        """
        if self._xnu_major >= os_data.tahoe.value:
            return False
        if (
            isinstance(self._computer.wifi, device_probe.Broadcom)
            and self._computer.wifi.chipset in [device_probe.Broadcom.Chipsets.AirPortBrcm4331, device_probe.Broadcom.Chipsets.AirPortBrcm43224]
        ):
            return True

        if (
            isinstance(self._computer.wifi, device_probe.Atheros)
            and self._computer.wifi.chipset == device_probe.Atheros.Chipsets.AirPortAtheros40
        ):
            return True

        return False
    LegacyWireless.name = name 
    LegacyWireless.present = present
    print("LegacyWireless has been patched successfully.")

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
    
    print("Atheros WiFi have been patched successfully.")

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

def patch_os_data_with_tahoe():
    from opencore_legacy_patcher.datasets.os_data import os_data
    if not hasattr(os_data, 'tahoe'):
        new_member = int.__new__(os_data, 25)
        new_member._name_ = 'tahoe'
        new_member._value_ = 25
        setattr(os_data, 'tahoe', new_member)
        os_data._member_map_['tahoe'] = new_member
        os_data._value2member_map_[25] = new_member
        os_data._member_names_.append('tahoe')
    
    print("os_data has been patched successfully.")

def patch_unsupported_host_os() -> bool:
    from opencore_legacy_patcher.datasets.os_data import os_data
    from opencore_legacy_patcher.sys_patch.patchsets import HardwarePatchsetDetection
    def _validation_check_unsupported_host_os(self) -> bool:
        """
        Determine if host OS is unsupported
        """
        _min_os = os_data.big_sur.value
        _max_os = os_data.tahoe.value
        if self._dortania_internal_check() is True:
            return False
        if self._xnu_major < _min_os or self._xnu_major > _max_os:
            return True
        return False

    HardwarePatchsetDetection._validation_check_unsupported_host_os = _validation_check_unsupported_host_os
    print("Unsupported host OS has been patched successfully.")
    
def patch_modern_audio():
    from opencore_legacy_patcher import constants
    from opencore_legacy_patcher.sys_patch.patchsets import detect
    from opencore_legacy_patcher.custom.modern_audio import ModernAudio
    HardwarePatchsetDetection = detect.HardwarePatchsetDetection
    origin_init = HardwarePatchsetDetection.__init__
    origin_detect = HardwarePatchsetDetection._detect
    def __init__(self, constants: constants.Constants,
                 xnu_major: int = None, xnu_minor:  int = None,
                 os_build:  str = None, os_version: str = None,
                 validation: bool = False
                 ) -> None:
        origin_init(self,constants, xnu_major, xnu_minor, os_build, os_version, validation)
        if ModernAudio not in self._hardware_variants:
            self._hardware_variants.append(ModernAudio)
        origin_detect(self)

    HardwarePatchsetDetection.__init__ = __init__
    print("ModernAudio has been patched successfully.")

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
    from opencore_legacy_patcher.sys_patch.auto_patcher.start import StartAutomaticPatching
    from opencore_legacy_patcher.support import updates
    import logging
    import wx
    import requests
    import markdown2
    from opencore_legacy_patcher.datasets import css_data
    from opencore_legacy_patcher.wx_gui import gui_support, gui_entry
    import webbrowser
    import subprocess
    from opencore_legacy_patcher.sys_patch.patchsets import HardwarePatchsetDetection, HardwarePatchsetValidation
    from opencore_legacy_patcher.support import utilities, network_handler

    original_start_auto_patch = StartAutomaticPatching.start_auto_patch

    def custom_start_auto_patch(self):
        logging.info("- Starting Automatic Patching")
        if self.constants.wxpython_variant is False:
            logging.info("- Auto Patch option is not supported on TUI, please use GUI")
            return

        dict = updates.CheckBinaryUpdates(self.constants).check_binary_updates()
        if dict:
            version = dict["Version"]
            logging.info(f"- Found new version: {version}")

            app = wx.App()
            mainframe = wx.Frame(None, -1, "OpenCore Legacy Patcher")

            ID_GITHUB = wx.NewId()
            ID_UPDATE = wx.NewId()

            url = CUSTOM_REPO_LATEST_RELEASE_URL
            response = requests.get(url).json()
            try:
                changelog = response["body"].split("## Asset Information")[0]
            except:  
                changelog = """## Unable to fetch changelog

Please check the Github page for more information about this release."""

            html_markdown = markdown2.markdown(changelog, extras=["tables"])
            html_css = css_data.updater_css
            frame = wx.Dialog(None, -1, title="", size=(650, 500))
            frame.SetMinSize((650, 500))
            frame.SetWindowStyle(wx.STAY_ON_TOP)
            panel = wx.Panel(frame)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.AddSpacer(10)
            self.title_text = wx.StaticText(panel, label="A new version of OpenCore Legacy Patcher is available!")
            self.description = wx.StaticText(panel, label=f"OpenCore Legacy Patcher {version}(Modified by JeoJay) is now available! \n You have {self.constants.patcher_version}. Would you like to update?")
            self.title_text.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
            self.description.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
            self.web_view = wx.html2.WebView.New(panel, style=wx.BORDER_SUNKEN)
            html_code = f'''
<html>
    <head>
        <style>
            {html_css}
        </style>
    </head>
    <body class="markdown-body">
        {html_markdown.replace("<a href=", "<a target='_blank' href=")}
    </body>
</html>
'''
            self.web_view.SetPage(html_code, "")
            self.web_view.Bind(wx.html2.EVT_WEBVIEW_NEWWINDOW, self._onWebviewNav)
            self.web_view.EnableContextMenu(False)
            self.close_button = wx.Button(panel, label="Ignore")
            self.close_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(wx.ID_CANCEL))
            self.view_button = wx.Button(panel, ID_GITHUB, label="View on GitHub")
            self.view_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(ID_GITHUB))
            self.install_button = wx.Button(panel, label="Download and Install")
            self.install_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(ID_UPDATE))
            self.install_button.SetDefault()

            buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
            buttonsizer.Add(self.close_button, 0, wx.ALIGN_CENTRE | wx.RIGHT, 5)
            buttonsizer.Add(self.view_button, 0, wx.ALIGN_CENTRE | wx.LEFT|wx.RIGHT, 5)
            buttonsizer.Add(self.install_button, 0, wx.ALIGN_CENTRE | wx.LEFT, 5)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.title_text, 0, wx.ALIGN_CENTRE | wx.TOP, 20)
            sizer.Add(self.description, 0, wx.ALIGN_CENTRE | wx.BOTTOM, 20)
            sizer.Add(self.web_view, 1, wx.EXPAND | wx.LEFT|wx.RIGHT, 10)
            sizer.Add(buttonsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 20)
            panel.SetSizer(sizer)
            frame.Centre()

            result = frame.ShowModal()

            if result == ID_GITHUB:
                webbrowser.open(dict["Github Link"])
            elif result == ID_UPDATE:
                gui_entry.EntryPoint(self.constants).start(entry=gui_entry.SupportedEntryPoints.UPDATE_APP)

            return

        if utilities.check_seal() is True:
            logging.info("- Detected Snapshot seal intact, detecting patches")
            patches = HardwarePatchsetDetection(self.constants).device_properties
            if not any(not patch.startswith("Settings") and not patch.startswith("Validation") and patches[patch] is True for patch in patches):
                patches = {}
            if patches:
                logging.info("- Detected applicable patches, determining whether possible to patch")
                if patches[HardwarePatchsetValidation.PATCHING_NOT_POSSIBLE] is True:
                    logging.info("- Cannot run patching")
                    return

                logging.info("- Determined patching is possible, checking for OCLP updates")
                patch_string = ""
                for patch in patches:
                    if patches[patch] is True and not patch.startswith("Settings") and not patch.startswith("Validation"):
                        patch_string += f"- {patch}\n"

                logging.info("- No new binaries found on Github, proceeding with patching")

                warning_str = ""
                if network_handler.NetworkUtilities(CUSTOM_REPO_LATEST_RELEASE_URL).verify_network_connection() is False:
                    warning_str = f"""\n\nWARNING: We're unable to verify whether there are any new releases of OpenCore Legacy Patcher on Github. Be aware that you may be using an outdated version for this OS. If you're unsure, verify on Github that OpenCore Legacy Patcher {self.constants.patcher_version} is the latest official release"""

                args = [
                    "/usr/bin/osascript",
                    "-e",
                    f"""display dialog "OpenCore Legacy Patcher has detected you're running without Root Patches, and would like to install them.\n\nmacOS wipes all root patches during OS installs and updates, so they need to be reinstalled.\n\nFollowing Patches have been detected for your system: \n{patch_string}\nWould you like to apply these patches?{warning_str}" """
                    f'with icon POSIX file "{self.constants.app_icon_path}"',
                ]
                output = subprocess.run(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                if output.returncode == 0:
                    gui_entry.EntryPoint(self.constants).start(entry=gui_entry.SupportedEntryPoints.SYS_PATCH, start_patching=True)
                return

            else:
                logging.info("- No patches detected")
        else:
            logging.info("- Detected Snapshot seal not intact, skipping")

        if self._determine_if_versions_match():
            self._determine_if_boot_matches()

    StartAutomaticPatching.start_auto_patch = custom_start_auto_patch
    print("start_auto_patch method has been patched.")

def patch_on_update():
    import requests
    import markdown2
    from opencore_legacy_patcher.datasets import css_data
    from opencore_legacy_patcher.wx_gui import gui_support, gui_update
    import wx
    import webbrowser
    from opencore_legacy_patcher.wx_gui.gui_main_menu import MainFrame
    original_on_update = MainFrame.on_update

    def custom_on_update(self, oclp_url: str, oclp_version: str, oclp_github_url: str):
        custom_url = CUSTOM_REPO_LATEST_RELEASE_URL

        ID_GITHUB = wx.NewId()
        ID_UPDATE = wx.NewId()

        response = requests.get(custom_url).json()
        try:
            changelog = response["body"].split("## Asset Information")[0]
        except:
            changelog = """## Unable to fetch changelog

Please check the Github page for more information about this release."""

        html_markdown = markdown2.markdown(changelog, extras=["tables"])
        html_css = css_data.updater_css
        frame = wx.Dialog(None, -1, title="", size=(650, 500))
        frame.SetMinSize((650, 500))
        frame.SetWindowStyle(wx.STAY_ON_TOP)
        panel = wx.Panel(frame)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(10)
        title_text = wx.StaticText(panel, label="A new version of OpenCore Legacy Patcher is available!")
        description = wx.StaticText(panel, label=f"OpenCore Legacy Patcher {oclp_version}(Modified by JeoJay) is now available! \n You have {self.constants.patcher_version}. Would you like to update?")
        title_text.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))
        description.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        web_view = wx.html2.WebView.New(panel, style=wx.BORDER_SUNKEN)
        html_code = f'''
<html>
    <head>
        <style>
            {html_css}
        </style>
    </head>
    <body class="markdown-body">
        {html_markdown.replace("<a href=", "<a target='_blank' href=")}
    </body>
</html>
'''
        web_view.SetPage(html_code, "")
        web_view.Bind(wx.html2.EVT_WEBVIEW_NEWWINDOW, self._onWebviewNav)
        web_view.EnableContextMenu(False)
        close_button = wx.Button(panel, label="Dismiss")
        close_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(wx.ID_CANCEL))
        view_button = wx.Button(panel, ID_GITHUB, label="View on GitHub")
        view_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(ID_GITHUB))
        install_button = wx.Button(panel, label="Download and Install")
        install_button.Bind(wx.EVT_BUTTON, lambda event: frame.EndModal(ID_UPDATE))
        install_button.SetDefault()

        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsizer.Add(close_button, 0, wx.ALIGN_CENTRE | wx.RIGHT, 5)
        buttonsizer.Add(view_button, 0, wx.ALIGN_CENTRE | wx.LEFT|wx.RIGHT, 5)
        buttonsizer.Add(install_button, 0, wx.ALIGN_CENTRE | wx.LEFT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(title_text, 0, wx.ALIGN_CENTRE | wx.TOP, 20)
        sizer.Add(description, 0, wx.ALIGN_CENTRE | wx.BOTTOM, 20)
        sizer.Add(web_view, 1, wx.EXPAND | wx.LEFT|wx.RIGHT, 10)
        sizer.Add(buttonsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 20)
        panel.SetSizer(sizer)
        frame.Centre()

        result = frame.ShowModal()

        if result == ID_GITHUB:
            webbrowser.open(oclp_github_url)
        elif result == ID_UPDATE:
            gui_update.UpdateFrame(
                parent=self,
                title=self.title,
                global_constants=self.constants,
                screen_location=self.GetPosition(),
                url= f"https://github.com/{CUSTOM_REPO}/releases/download/{oclp_version}/OpenCore-Patcher.pkg",
                version_label=oclp_version
            )

        frame.Destroy()

    MainFrame.on_update = custom_on_update
    print("on_update method has been patched.")
