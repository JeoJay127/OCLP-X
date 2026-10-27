from opencore_legacy_patcher.datasets import pci_data
from opencore_legacy_patcher.detections import device_probe



CUSTOM_REPO = "JeoJay127/OCLP-X"

CUSTOM_REPO_LATEST_RELEASE_URL = f"https://api.github.com/repos/{CUSTOM_REPO}/releases/latest"


def _release_tag(branch):
    return branch[len("refs/tags/"):] if branch.startswith("refs/tags/") else None


def patch_fork_metadata():
    import sys
    from opencore_legacy_patcher import constants
    from opencore_legacy_patcher.support import commit_info
    Constants = constants.Constants
    origin_init = Constants.__init__
    def modified_init(self, *args, **kwargs):
        origin_init(self, *args, **kwargs)
        self.patcher_name = "OCLP(Modified by JeoJay)"
        self.repo_link = f"https://github.com/{CUSTOM_REPO}"
        branch = commit_info.ParseCommitInfo(sys.executable).generate_commit_info()[0]
        self.installer_pkg_url = f"{self.repo_link}/releases/download/{_release_tag(branch) or self.patcher_version}/AutoPkg-Assets.pkg"
        self.installer_pkg_url_nightly = f"http://nightly.link/{CUSTOM_REPO}/workflows/build-app-wxpython/main/AutoPkg-Assets.pkg.zip"

    Constants.__init__ = modified_init

def patch_modern_audio():
    from opencore_legacy_patcher.sys_patch.patchsets.hardware.misc.modern_audio import ModernAudio
    from opencore_legacy_patcher.custom.platform_probe import is_hackintosh
    from opencore_legacy_patcher.datasets.os_data import os_data

    origin_present = ModernAudio.present

    def present(self) -> bool:
        """
        Extend official audio detection to Hackintosh hosts on Tahoe Beta 2 and later
        """
        if (
            self._xnu_major == os_data.tahoe.value
            and self.native_os() is False
            and is_hackintosh(self._constants) is True
        ):
            return True
        return origin_present(self)

    ModernAudio.present = present
    print("ModernAudio class has been patched successfully.")

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
        # if self._xnu_major >= os_data.tahoe.value:
        #     return False
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
        # if self._xnu_major >= os_data.tahoe.value:
        #     return False
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

def patch_update_url():
    from opencore_legacy_patcher.support import updates
    from packaging import version
    
    original_check_binary_updates = updates.CheckBinaryUpdates.check_binary_updates

    def custom_check_binary_updates(self):
        updates.REPO_LATEST_RELEASE_URL = CUSTOM_REPO_LATEST_RELEASE_URL
        release_tag = _release_tag(self.constants.commit_info[0])
        if release_tag:
            try:
                release_version = version.parse(release_tag)
                if release_version.base_version == self.binary_version.base_version:
                    self.binary_version = release_version
            except version.InvalidVersion:
                pass

        result = original_check_binary_updates(self)

        if result:
            release_tag = result["Link"].split("/releases/download/", 1)[1].split("/", 1)[0]
            result["Version"] = release_tag
            result["Github Link"] = f"https://github.com/{CUSTOM_REPO}/releases/tag/{release_tag}"
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
                url=oclp_url,
                version_label=oclp_version
            )

        frame.Destroy()

    MainFrame.on_update = custom_on_update
    print("on_update method has been patched.")
