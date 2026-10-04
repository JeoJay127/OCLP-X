<div align="center">
             <img src="docs/images/OC-Patcher.png" alt="OpenCore Patcher Logo" width="256" />
             <h1>OpenCore Legacy Patcher</h1>
</div>

- **English**
- [简体中文](./README_CN.md)

An officially modified version of a Python-based project revolving around [Acidanthera's OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) and [Lilu](https://github.com/acidanthera/Lilu) for both running and unlocking features in macOS on supported and unsupported Macs.

Our project's main goal is to breathe new life into Macs no longer supported by Apple, allowing for the installation and usage of macOS Big Sur and newer on machines as old as 2007.

----------

Noteworthy features of OpenCore Legacy Patcher:

* Support for macOS Big Sur, Monterey, Ventura, Sonoma, and Sequoia
* Native Over the Air (OTA) System Updates
* Supports Penryn and newer Macs
* Full support for WPA Wi-Fi and Personal Hotspot on BCM943224 and newer wireless chipsets
* System Integrity Protection, FileVault 2, .im4m Secure Boot and Vaulting
* Recovery OS, Safe Mode and Single-user Mode booting on non-native OSes
* Unlocks features such as Sidecar and AirPlay to Mac even on native Macs
* Enables enhanced SATA and NVMe power management on non-Apple storage devices
* Zero firmware patching required (ie. APFS ROM patching)
* Graphics acceleration for both Metal and non-Metal GPUs
* **Enhanced support for IntelWireless Cards on macOS Sequoia and macOS Tahoe 26(modified version supported)**  
* **Added support for Atheros WiFi cards and some legacy Broadcom WiFi card IDs(modified version supported)**
* **Added AppleHDA audio support (required by AppleALC) for macOS Tahoe 26 Beta 2 (26.0-25A5295e) and later.**

----------

# How to Make Intel WiFi Work on macOS?

Thanks to [zxystd](https://github.com/zxystd) for his contribution! You need the Intel WiFi driver, which can be downloaded from his repository: [AirportItlwm](https://github.com/OpenIntelWireless/itlwm/releases).

Note 2: Currently, OpenCore Legacy Patcher officially supports patching to run macOS Big Sur through Tahoe installs. For older OSes, OpenCore may function; however, support is currently not provided from Dortania.

**Note:** You can only choose **one** of the two driver methods below, **they cannot be used simultaneously!**

### Method 1: Using [AirportItlwm](https://github.com/OpenIntelWireless/itlwm/releases)

1. **Ensure that all related drivers and patches from Method 2 have been completely removed.**

2. **For macOS High Sierra 10.13 ~ macOS Catalina 10.15**, in addition to using the AirportItlwm driver corresponding to your macOS version, you also need a Force patch.

   Add the following patch in **Kernel - Force**:

   | Identifier                           | BundlePath                                     | Comment                         | Enabled | ExecutablePath                  | PlistPath                  | MinKernel | MaxKernel | Arch |
   |--------------------------------------|----------------------------------------------|---------------------------------|---------|---------------------------------|--------------------------------|-----------|-----------|------|
   | com.apple.iokit.IO80211Family        | System/Library/Extensions/IO80211Family.kext | Force IO80211Family to load | true    | Contents/MacOS/IO80211Family | Contents/Info.plist          | 17.0.0    | 19.99.99  | Any  |

3. **For macOS Big Sur 11.0 ~ macOS Sonoma 14.x**, simply use the AirportItlwm driver corresponding to your macOS version.

   **Note:**  
   - If your system is macOS Sonoma 14.4 or later, use the **macOS Sonoma 14.4 AirportItlwm driver**.  
   - If your system is macOS Sonoma 14.0 ~ 14.3, use the **macOS Sonoma 14.0 AirportItlwm driver**.

4. **For macOS Sequoia 15**, there is currently no native AirportItlwm driver available (though it may be released in the future). The current solution is to use the **macOS Ventura AirportItlwm driver**.

   You may see **AirportItlwm_Sequoia.kext**, but it is essentially the Ventura driver renamed for better distinction. The following steps outline how to configure this driver for macOS Sequoia 15:

   - **Disable SIP (System Integrity Protection):** Set `csr-active-config` to `03080000` in **NVRAM-Add-7C436110-AB2A-4BBB-A880-FE41995C9F82** (or use `FF0F0000` to completely disable SIP).
   - **Disable AMFI (Apple Mobile File Integrity):** Set `amfi=0x80` in **NVRAM-Add-7C436110-AB2A-4BBB-A880-FE41995C9F82** or use **AMFIPass.kext v1.4.1 or later**.
   - **Set SecureBootModel to Disabled:** Navigate to **Misc -> Security -> SecureBootModel -> Disabled** in OpenCore.
   - **Disable FileVault:** Go to **System Settings > Privacy & Security > FileVault > Turn Off**.
   - **Add NVRAM delete entries**:

     Add the following under **NVRAM-Delete-7C436110-AB2A-4BBB-A880-FE41995C9F82**:
     - `boot-args`
     - `csr-active-config`
   
   - **Restart your Mac once to ensure the above changes take effect.**

   **Required Kext Drivers (Maintain the order as listed below):**

   | BundlePath                        | Comment       | Enabled | ExecutablePath                      | PlistPath                  | MinKernel | MaxKernel | Arch |
   |-----------------------------------|--------------|---------|--------------------------------------|----------------------------|-----------|-----------|------|
   | IOSkywalkFamily.kext              | V1.0         | true    | Contents/MacOS/IOSkywalkFamily      | Contents/Info.plist        | 24.0.0    | 24.99.99  | Any  |
   | IO80211FamilyLegacy.kext          | V1200.12.2b1 | true    | Contents/MacOS/IO80211FamilyLegacy  | Contents/Info.plist        | 24.0.0    | 24.99.99  | Any  |
   | AirportItlwm_Sequoia.kext         | V2.3.0       | true    | Contents/MacOS/AirportItlwm         | Contents/Info.plist        | 24.0.0    | 24.99.99  | Any  |


## Note:

   1. **AirportItlwm_Sequoia.kext** is just the **Ventura** version of the **AirportItlwm** driver with a renamed file! 
   
   2. The mentioned **IOSkywalkFamily.kext** and **IO80211FamilyLegacy.kext** can be obtained from the repository [IOSkywalkFamily & IO80211FamilyLegacy](https://github.com/JeoJay127/OCLP-X/tree/main/payloads/Kexts/Wifi).


   **Add the following patch in Kernel - Block:**

   | Identifier                           | Comment                 | Enabled | Strategy | MinKernel | MaxKernel | Arch |
   |--------------------------------------|-------------------------|---------|----------|-----------|-----------|------|
   | com.apple.iokit.IOSkywalkFamily      |                         | true    | Exclude  | 24.0.0    |           | Any  |

   **Finally, download this modified version of OpenCore Legacy Patcher, run it, and apply Root Patching:**
   - Click **Post-Install Root Patch** -> **Start Root Patching**, then restart your Mac.

---

### Method 2: Using [HeliPort](https://github.com/OpenIntelWireless/HeliPort/releases) + [Itlwm](https://github.com/OpenIntelWireless/itlwm/releases)

1. **Ensure that all related drivers and patches from Method 1 have been completely removed.**

2. **Add the Itlwm driver and install the HeliPort client.**

   **Note:** The unrestricted version of **HeliPort + Itlwm** supports **macOS High Sierra 10.13 ~ macOS Sequoia 15**.

---

## Intel Bluetooth on macOS Ventura and newer

### Recommendations:
- **Ensure your USB ports are properly mapped.**
- **Modify NVRAM settings** by adding the following entries in **NVRAM-Add-7C436110-AB2A-4BBB-A880-FE41995C9F82**:

   | Key                              | Type  | Value                          |
   |----------------------------------|------|--------------------------------|
   | bluetoothExternalDongleFailed   | Data | 00                             |
   | bluetoothInternalControllerInfo | Data | 0000000000000000000000000000   |

   **Alternative (e.g., for Intel AX201, AX200 wireless cards):**

   | Key                              | Type  | Value                          |
   |----------------------------------|------|--------------------------------|
   | bluetoothExternalDongleFailed   | Data | 00                             |
   | bluetoothInternalControllerInfo | Data | 000000000000000089653A552EFD   |

### Required Kext Drivers:

| BundlePath                        | Comment      | Enabled | ExecutablePath                         | PlistPath                    | MinKernel | MaxKernel | Arch |
|-----------------------------------|-------------|---------|-----------------------------------------|------------------------------|-----------|-----------|------|
| BlueToolFixup.kext                | V2.6.9      | true    | Contents/MacOS/BlueToolFixup           | Contents/Info.plist          | 21.0.0    |           | Any  |
| IntelBTPatcher.kext               | V2.5.0      | true    | Contents/MacOS/IntelBTPatcher          | Contents/Info.plist          | 21.0.0    |           | Any  |
| IntelBluetoothFirmware.kext       | V2.5.0      | true    | Contents/MacOS/IntelBluetoothFirmware  | Contents/Info.plist          |           |           | Any  |

You can download these kexts from:

- [BlueToolFixup.kext](https://github.com/acidanthera/BrcmPatchRAM/releases)

- [IntelBTPatcher.kext](https://github.com/OpenIntelWireless/IntelBluetoothFirmware/releases)

- [IntelBluetoothFirmware.kext](https://github.com/OpenIntelWireless/IntelBluetoothFirmware/releases)


## Running from source

To run the project from source, see here: [Build and run from source](./SOURCE.md)

## Credits

* [Dortania](https://github.com/dortania)
  * Original author, created and maintained the OpenCore Legacy Patcher project

* [Acidanthera](https://github.com/Acidanthera)
  * OpenCorePkg, as well as many of the core kexts and tools
* [DhinakG](https://github.com/DhinakG)
  * Main co-author
* [Khronokernel](https://github.com/Khronokernel)
  * Main co-author
* [Ausdauersportler](https://github.com/Ausdauersportler)
  * iMacs Metal GPUs Upgrade Patch set and documentation
  * Great amounts of help with debugging, and code suggestions
* [vit9696](https://github.com/vit9696)
  * Endless amount of help troubleshooting, determining fixes and writing patches
* [EduCovas](https://github.com/covasedu)
  * macOS Tahoe patch set
  * [non-Metal patch set](https://github.com/moraea/non-metal-frameworks) for nVidia Tesla/Fermi/Maxwell/Pascal, AMD TeraScale 1/2, and Intel Core 1st/2nd Generation GPUs
  * [3802 Metal patch set](https://github.com/moraea/misc-patches/tree/main/3802-Metal-15) and [MetallibSupportPkg](https://github.com/dortania/MetallibSupportPkg) for nVidia Kepler and Intel Core 3rd/4th Generation GPUs
  * Metal bundle patches and shims for [nVidia Kepler](https://github.com/moraea/misc-patches/tree/main/Kepler%2013%2B), [AMD GCN 1 - 4](https://github.com/moraea/misc-patches/tree/main/GCN%2013%2B), and [AMD GCN 5 (Vega)](https://github.com/moraea/misc-patches/tree/main/vega%2013%2B)
  * [IOSurface offset patches](https://github.com/moraea/misc-patches/tree/main/Sonoma%2014.4%20IOSurface) for nVidia Kepler, AMD GCN 1 - 5, and Intel Core 3rd - 6th Generation GPUs
  * [legacy Wi-Fi patch set](https://github.com/moraea/unsupported-wifi-patches) restores functionality for Wi-Fi cards in all 2007 - 2017 models
  * [T1 patch set](https://github.com/moraea/misc-patches/tree/main/T1-Patch) restores Touch ID, Apple Pay, and other secure functionality in 2016 - 2017 models
  * AppleGVA downgrade for accelerated video decoding on 2012 - 2016 models
  * OpenCL and OpenGL downgrade for AMD GCN
  * [USB 1 patch](https://github.com/moraea/misc-patches/tree/main/IOUSBHostFamily-14.4)
* [ASentientHedgehog](https://github.com/moosethegoose2213)
  * [non-Metal patch set](https://github.com/moraea/non-metal-frameworks) for nVidia Tesla/Fermi/Maxwell/Pascal, AMD TeraScale 1/2, and Intel Core 1st/2nd Generation GPUs
* [ASentientBot](https://github.com/ASentientBot)
  * macOS Tahoe patch set
  * 3802 MTLCompiler, 31001 MTLCompiler, T1, WiFi patch sets
  * [dsce](https://github.com/moraea/dsce) and [shared code](https://github.com/moraea/moraea-common) used by some other patches
* [cdf](https://github.com/cdf)
  * Mac Pro on OpenCore Patch set and documentation
  * [Innie](https://github.com/cdf/Innie) and [NightShiftEnabler](https://github.com/cdf/NightShiftEnabler)
* [Syncretic](https://forums.macrumors.com/members/syncretic.1173816/)
  * [AAAMouSSE](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/), [telemetrap](https://forums.macrumors.com/threads/mp3-1-others-sse-4-2-emulation-to-enable-amd-metal-driver.2206682/post-28447707) and [SurPlus](https://github.com/reenigneorcim/SurPlus)
* [dosdude1](https://github.com/dosdude1)
  * Main author of the [original GUI](https://github.com/dortania/OCLP-GUI)
  * Development of previous patchers, laying out much of what needs to be patched
* [parrotgeek1](https://github.com/parrotgeek1)
  * [VMM Patch Set](https://github.com/dortania/OpenCore-Legacy-Patcher/blob/4a8f61a01da72b38a4b2250386cc4b497a31a839/payloads/Config/config.plist#L1222-L1281)
* [BarryKN](https://github.com/BarryKN)
  * Development of previous patchers, laying out much of what needs to be patched
* [mario_bros_tech](https://github.com/mariobrostech) and the rest of the Unsupported Mac Discord
  * Catalyst that started OpenCore Legacy Patcher
* [arter97](https://github.com/arter97/)
  * [SimpleMSR](https://github.com/arter97/SimpleMSR/) to disable firmware throttling in Nehalem+ MacBooks without batteries
* [Mr.Macintosh](https://mrmacintosh.com)
  * Endless hours helping architect and troubleshoot many portions of the project
* [flagers](https://github.com/flagersgit)
  * Aid with Nvidia Web Driver research and development
  * [non-Metal patch set](https://github.com/moraea/non-metal-frameworks) for nVidia Tesla/Fermi/Maxwell/Pascal, AMD TeraScale 1/2, and Intel Core 1st/2nd Generation GPUs
  * [Metal bundle interposer](https://github.com/moraea/misc-patches/tree/main/sequoia%2031001%20interposer) for AMD GCN 1 - 5 and Intel Core 5th/6th Generation GPUs
  * LegacyRVPL, SnapshotIsKill, etc. to aid in rapid testing and development
* [joevt](https://github.com/joevt)
  * [FixPCIeLinkrate](https://github.com/joevt/joevtApps)
* [Jazzzny](https://github.com/Jazzzny)
  * Research and various contributions to the project
  * UEFI Legacy XHCI research and development
  * NVIDIA OpenCL research and development
  * `MacBook5,2` research and development
    * LegacyKeyboardInjector
  * Pre-Ivy Bridge Aquantia Ethernet Patch
  * Non-Metal Photo Booth Patch for Monterey+
  * GUI and Backend Development
    * Updater UI
    * macOS Downloader UI
    * Downloader UI
    * USB Top Case probing
    * Developer root patching
  * Vaulting implementation
  * macOS 15 3802 Helios Research
  * UEFI bootx64.efi research
  * universal2 build research
  * Various documentation contributions
* [crystall1nedev](https://github.com/crystall1nedev)
  * Various patcher and PatcherSupportPkg contributions
* Amazing users who've graciously donate hardware:
  * [JohnD](https://forums.macrumors.com/members/johnd.53633/) - 2013 Mac Pro
  * [SpiGAndromeda](https://github.com/SpiGAndromeda) - AMD Vega 64
  * [turbomacs](https://github.com/turbomacs) - 2014 5k iMac
  * [vinaypundith](https://forums.macrumors.com/members/vinaypundith.1212357/) - MacBook7,1
   * [ThatStella7922](https://github.com/ThatStella7922) - 2017 13" MacBook Pro (A1708)
  * zephar - 2008 Mac Pro
  * jazo97 - 2011 15" MacBook Pro
  * And others (reach out if we forgot you!)
* MacRumors and Unsupported Mac Communities
  * Endless testing and reporting issues
* Apple
  * for macOS and many of the kexts, frameworks and other binaries we reimplemented into newer OSes
