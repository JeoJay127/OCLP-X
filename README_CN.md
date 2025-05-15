<div align="center">
             <img src="docs/images/OC-Patcher.png" alt="OpenCore Patcher Logo" width="256" />
             <h1>OpenCore Legacy Patcher</h1>
</div>

- **简体中文**
- [English](./README.md)

一个官方修改版的 Python 项目，围绕 [Acidanthera 的 OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) 和 [Lilu](https://github.com/acidanthera/Lilu) 开发，旨在在受支持和不受支持的 Mac 上运行 macOS 并解锁其功能。

我们的主要目标是让苹果官方不再支持的 Mac 焕发新生，使 2007 年及更新的设备能够安装和使用 macOS Big Sur 及更新版本。

----------

## OpenCore Legacy Patcher 的重要功能：

* 支持 macOS Big Sur、Monterey、Ventura、Sonoma 和 Sequoia
* 原生支持 OTA（在线）系统更新
* 兼容 Penryn 及更新的 Mac 机型
* 完全支持 WPA Wi-Fi 及个人热点，适用于 BCM943224 及更新的无线芯片组
* 支持系统完整性保护（SIP）、FileVault 2、.im4m 安全启动和 Vaulting
* 在非原生操作系统上支持恢复模式（Recovery OS）、安全模式（Safe Mode）和单用户模式（Single-user Mode）启动
* 解锁原生 Mac 设备上的 Sidecar 和 AirPlay to Mac 等功能
* 在非 Apple 存储设备上启用增强的 SATA 和 NVMe 电源管理
* 无需固件补丁（即 APFS ROM 补丁）
* 支持 Metal 和非 Metal GPU 的图形加速
* **增强对 macOS Sequoia 上 Intel 无线网卡的支持(修改版支持)** 
* **新增对 Atheros WiFi 网卡及部分旧款 Broadcom WiFi 网卡 ID 的支持(修改版支持)**

----------

## 如何使Intel WiFi 在macOS 工作？

感谢[zxystd](https://github.com/zxystd) 的贡献！需要Intel WiFi驱动,可以去他的仓库[AirportItlwm](https://github.com/OpenIntelWireless/itlwm/releases)下载。

### Intel WiFi驱动方法

注意：驱动方式一和驱动方式二只能选择其中一个,不能同时使用！！！

#### 驱动方式一：使用[AirportItlwm](https://github.com/OpenIntelWireless/itlwm/releases)驱动

- 1.确保驱动方式二中所有相关驱动及补丁都已经删除干净。

- 2.对于macOS High Serrira 10.13 ~ macOS Catalina 10.15系统,除了使用对应系统版本的AirportItlwm驱动外，还需要一个Force补丁。

Kernel - Force中新增补丁：

|Identifier | BundlePath                       | Comment                | Enabled | ExecutablePath                     | PlistPath               | MinKernel | MaxKernel | Arch |
|-----------|----------------------------------|--------------------------------------------|---------|-------------------------------------|----------------------------------|-----------|-----------|------|
| com.apple.iokit.IO80211Family         | System/Library/Extensions/IO80211Family.kext | Force IO80211Family to load        | true    | Contents/MacOS/IO80211Family    | Contents/Info.plist              | 17.0.0    | 19.99.99  | Any  |

- 3.对于macOS Big Sur 11.0 ~ macOS Sonoma 14.x,使用对应系统版本的AirportItlwm驱动即可。

  需要注意的是，如果你是macOS Sonoma 14.4以上的系统，需要使用macOS Sonoma 14.4的AirportItlwm驱动，如果是macOS Sonoma 14.0 ～ 14.3系统，需要使用macOS Sonoma 14.0的AirportItlwm驱动。

- 4.对于macOS Sequoia 15系统,由于目前还没有对应系统的原生AirportItlwm驱动(后续可能会有)，目前做法是使用macOS Ventura系统对应的AirportItlwm驱动(所以有些时候，你会看到AirportItlwm_Sequoia.kext,其实很可能就是Ventura系统对应的AirportItlwm驱动改名而已，为了很好区分，以下内容也会采用这种做法)，但是需要添加一些驱动和补丁。

对于macOS Sequoia 15系统，建议按照以下步骤进行操作(打开你的config)：

   - 禁用SIP(System Integrity Protection),  在 NVRAM-Add-7C436110-AB2A-4BBB-A880-FE41995C9F82 中设置csr-active-config为03080000(也可以使用FF0F0000彻底禁用)
   - 禁用AMFI(Apple Mobile File Integrity), 在 NVRAM-Add-7C436110-AB2A-4BBB-A880-FE41995C9F82 中设置amfi=0x80或者使用v1.4.1版或更新版本的AMFIPass.kext。(如果不考虑安全原因，可以使用amfi_get_out_of_my_way=0x1来彻底禁用AMFI)
   - SecureBootModel 设置为Disabled，具体操作：Misc -> Security ->SecureBootModel -> Disabled
   - 关闭“文件保险箱”功能：系统设置 > 隐私与安全性 > 文件保险箱 > 关闭
   - 添加NVRAM删除（主要是为了避免重启Reset NVRAM这一步操作），在 NVRAM-Delete-7C436110-AB2A-4BBB-A880-FE41995C9F82 中添加以下值：
   
     - boot-args
     - csr-active-config

   - 重启一次电脑，确保以上操作生效。

需要的kext驱动(注意保持如下顺序)：

| BundlePath                       | Comment       | Enabled | ExecutablePath                     | PlistPath               | MinKernel | MaxKernel | Arch |
|----------------------------------|--------------|---------|-------------------------------------|----------------------------------|-----------|-----------|------|
| IOSkywalkFamily.kext             | V1.0         | true    | Contents/MacOS/IOSkywalkFamily     | Contents/Info.plist              | 24.0.0    | 24.99.99  | Any  |
| IO80211FamilyLegacy.kext         | V1200.12.2b1 | true    | Contents/MacOS/IO80211FamilyLegacy | Contents/Info.plist              | 24.0.0    | 24.99.99  | Any  |
| AirportItlwm_Sequoia.kext        | V2.3.0       | true    | Contents/MacOS/AirportItlwm        | Contents/Info.plist              | 24.0.0    | 24.99.99  | Any  |


注：
  1. AirportItlwm_Sequoia.kext 就是Ventura系统对应的AirportItlwm驱动改名而已！！！
  2. 上述 IOSkywalkFamily.kext和IO80211FamilyLegacy.kext可以到仓库 [IOSkywalkFamily&IO80211FamilyLegacy](https://github.com/JeoJay127/OCLP-X/tree/main/payloads/Kexts/Wifi)获取




Kernel - Block 中新增补丁：
| Identifier                           | Comment                | Enabled | Strategy | MinKernel | MaxKernel | Arch |
|--------------------------------------|------------------------|---------|----------|-----------|-----------|------|
| com.apple.iokit.IOSkywalkFamily      |                        | true    | Exclude  | 24.0.0    |           | Any  |


下载此修改版本OpenCore Legacy Patcher,安装运行它，点击Post-Install Root Patch -> Start Root Patching，完成后重启即可。


#### 驱动方式二：使用[HeliPort](https://github.com/OpenIntelWireless/HeliPort/releases) + [Itlwm](https://github.com/OpenIntelWireless/itlwm/releases) 驱动

- 1.确保驱动方式一中所有相关驱动及补丁都已经删除干净。

- 2.添加Itlwm驱动，然后安装HeliPort客户端。

 注：对于intel无线网卡，可以使用HeliPort + Itlwm无限制版本(支持macOS High Serrira 10.13 ~ macOS Sequoia 15)


## macOS Ventura 及更新版本的 Intel 蓝牙驱动

•	建议定制好USB

•	NVRAM 设置：在 NVRAM-Add-7C436110-AB2A-4BBB-A880-FE41995C9F82 中，新增以下两个条目：


| Key                              | Type  | Value                          |
|----------------------------------|------|--------------------------------|
| bluetoothExternalDongleFailed   | Data | 00                             |
| bluetoothInternalControllerInfo | Data | 0000000000000000000000000000   |

 备用(例如：Intel AX201，AX200无线网卡)：

| Key                              | Type  | Value                          |
|----------------------------------|------|--------------------------------|
| bluetoothExternalDongleFailed   | Data | 00                             |
| bluetoothInternalControllerInfo | Data | 000000000000000089653A552EFD |

需要的kext驱动：

| BundlePath                       | Comment      | Enabled | ExecutablePath                        | PlistPath               | MinKernel | MaxKernel | Arch |
|----------------------------------|--------------|---------|-------------------------------------  |------------------------|-----------|-----------|------|
| BlueToolFixup.kext               | V2.6.9       | true    | Contents/MacOS/BlueToolFixup          | Contents/Info.plist       | 21.0.0    |           | Any  |
| IntelBTPatcher.kext              | V2.5.0       | true    | Contents/MacOS/IntelBTPatcher         | Contents/Info.plist     | 21.0.0    |           | Any  |
| IntelBluetoothFirmware.kext      | V2.5.0       | true    | Contents/MacOS/IntelBluetoothFirmware | Contents/Info.plist     |           |           | Any  |

可以从以下仓库下载以上最新kext驱动：

[BlueToolFixup.kext](https://github.com/acidanthera/BrcmPatchRAM/releases)

[IntelBTPatcher.kext](https://github.com/OpenIntelWireless/IntelBluetoothFirmware/releases)

[IntelBluetoothFirmware.kext](https://github.com/OpenIntelWireless/IntelBluetoothFirmware/releases)

----------

## 从源码运行

要从源码运行本项目，请参考：[从源码构建和运行](./SOURCE.md)

## 鸣谢

* [Dortania](https://github.com/dortania)  
  * 项目原作者，创建并维护了 OpenCore Legacy Patcher 项目

* [Acidanthera](https://github.com/Acidanthera)  
  * 提供 OpenCorePkg 以及许多核心 kext 和工具

* [zxystd](https://github.com/zxystd)  
  * macOS Intel Wi-Fi 适配器内核扩展的开发者

* Apple  
  * 提供 macOS 及我们在新系统中重新实现的众多 kext、框架和其他二进制文件
