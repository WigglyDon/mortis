# Experiment 002: inspect the stock receiver offline

Date: October 30, 2026. Status: **completed initial static inspection**.

Question: can we locate Android Auto and a candidate transport boundary in the software matching the owner's displayed build?

Result: **yes**. The stock image contains an identifiable receiver, USB transport classes, a dynamically linked Android Open Accessory library, Wi-Fi peer-to-peer code and Bluetooth serial-profile entry points. Their suitability for native wireless operation remains untested.

## Reproducible inputs

[CyanLabs' IVSU database API](https://api.cyanlabs.net/ford/sync3/ivsus), record 561, lists `4U5T-14G381-AN` as SYNC 3.3.19052. Its download redirected to [Ford's stock package](https://ivsu.binaries.ford.com/swparts/4U5T-14G381-AN_1552583626000.TAR.GZ).

| Artifact | Bytes | Verification |
| --- | ---: | --- |
| Outer package | 502,997,338 | Published and measured MD5 `0553d1a474fbf9f0db68a9c96fbda7cb` |
| Outer package | 502,997,338 | Measured SHA-256 `b2958f001f2efb76e7edb64aa5814babccb5e97d283716b15e555300f2d7bdb9` |
| `apps.img` | 1,610,612,736 | Measured SHA-256 `a23047744a2065a120aed5521e34e0e0656c226b2da1427d29d00a044bac1edd` |

The outer archive contains `Version.der`, `apps.tar.gz`, `QNX-IFS` and `MLO`. The nested application archive contains `apps.img`. Explicit members were read with Python's `tarfile.extractfile()` and copied locally; no package code was executed. No independent Ford signature verification was performed.

The application image has a QNX6 superblock at `0x2000`, 1,024-byte filesystem blocks, and 67,894 enumerated entries. It was opened read-only using [Dissect's QNX6 reader](https://github.com/fox-it/dissect.qnxfs). No filesystem driver was installed and no volume was mounted. The image's `Version.inf` identifies `4U5T-14G381-AN` and `SYNCGen3.0_3.3.19052_PRODUCT`.

Raw software and extracts remain in ignored `private/research/sync33/`. These are stock-image findings; Mortis's inventory must still confirm its installed package and hardware.

## Receiver and transport evidence

| Artifact in `apps.img` | Observation |
| --- | --- |
| `/etc/system/config/ss_launch_config.cfg` | Launches `/fs/mp/apps/MM_GalService` and `/fs/mp/apps/MM_ProjectionService` as projection services. |
| `/apps/MM_GalService` | ARM EABI5 ELF using `/usr/lib/ldqnx.so.2`; contains Android Auto protocol endpoints, QNX audio/video callbacks, and `QnxDeviceManager::onConnect`. |
| `MM_GalService` dynamic symbols | Defines `Transport` and `UsbTransport` vtables; imports `aoa_init`, `aoa_usbinfo_add/remove`, `aoa_get_protocol`, `aoa_bulk_rx`, `aoa_bulk_tx` and `aoa_shutdown`. |
| `/usr/lib/libaoa.so.1` | Exports the AOA functions above and depends on `libusbdi.so.2`. |
| `/apps/MM_ProjectionService` | Contains Android Auto settings, GAL launch, Bluetooth pairing and device management paths. |

Receiver SHA-256: `c511a2b1171e2c2d0968978137bf1ba09a3e8fd1e200f7032d53715fec5b5ff1`.

AOA library SHA-256: `31ab5a4a9002a45919a58364b41d2b4060634b83a4fdc538375f9d1b0a465451`.

For this receiver ELF, `_ZTV9Transport` is at virtual address `0x23dec0`, `_ZTV12UsbTransport` at `0x23dee0`, and `_ZN16QnxDeviceManager9onConnectEP9aoa_hdl_sPKv` at `0x1730b8` with size 1,012 bytes. These are static analysis coordinates for this file, not addresses measured in a running process.

This narrows the experiment to a transport adapter or AOA compatibility shim while retaining the receiver. Imports and vtables do not establish safe interposition, function signatures or a supported extension API. USB discovery, handles, buffer ownership, control transfers and disconnect/reconnect callbacks also need to work; redirecting two bulk functions alone is insufficient.

No TCP transport was identified in this initial symbol/string inspection. That is a bounded search result, not proof that one cannot be added or exists nowhere else.

## Radio evidence

`NET_WifiConnectionMgr` contains named P2P handlers and supplicant interfaces `tiw_p2pdev0` and `tiw_p2pgrp0`. It includes TI18xx utility command strings and group-owner/client state handling. `wifi_config.conf` also includes P2P group-owner address settings. This is stronger software evidence than radio frequency support alone, but does not verify Mortis's chipset, AP capability, firmware, allowed channels or coexistence behavior. Wi-Fi Direct support is not automatically compatible with the reference implementation's access-point setup.

Wi-Fi manager SHA-256: `033acf5b1363b981118f28dfca9ef8b31d8070cd4619eea543aa9cb0e7935e5b`.

The launcher names `CORAL_BT.exe` and `NET_BT_Service`. `NET_BT_Service` depends on `libBT_Service_API.so` and `libBtStack_API.so`; the inspected integration is different from the reference bridges' BlueZ API. `libBtStack_API.so` exports `BT_SPP_setupSPP`, `BT_SPP_setupSPP_Idx`, `BT_SPP_connectSPP_UUID`, connection and shutdown functions. Serial-profile APIs are a promising route to investigate for RFCOMM setup. Their presence does not show that arbitrary UUID/channel registration or an AA Wireless service is supported.

Bluetooth stack API SHA-256: `8c41179ead72da9ab6da3cb557be9f7903c5048bc184e842bec336daab5ae7ae`.

The stock boot image contains an OMAP5432 board identifier. This describes the package's build target. The exact running QNX release and Mortis's hardware remain unmeasured.

## Tool and validation

`tools/inspect_sync_image.py` inventories the image, extracts 19 fixed paths, computes hashes, and reports ELF dependencies and selected dynamic symbols. Its destination must be a new directory. It does not execute the extracted programs or follow their symlinks into the host filesystem.

Tested locally with Python 3.9.6 and the pinned research dependencies:

```sh
python3 -m venv private/research/venv
private/research/venv/bin/python -m pip install -r tools/research-requirements.txt
private/research/venv/bin/python tools/inspect_sync_image.py \
  private/research/sync33/apps.img \
  --output private/research/sync33/inspection-complete
```

The completed run enumerated 67,894 entries and found all 19 selected files. The receiver's size/hash, ELF architecture, imported AOA functions and version metadata were also checked in a separate manual extraction. Detailed reports are `inspection-complete/file-inventory.json` and `inspection-complete/inspection.json`. The reader dependencies are host research tools; they are not proposed QNX runtime dependencies.

## Next experiment

1. Recover the AOA lifecycle and callback signatures around `QnxDeviceManager::onConnect`, and map the transport virtual functions. Determine how the receiver is told that a device exists and how USB removal is handled.
2. Recover the parameter contracts of `BT_SPP_setupSPP[_Idx]` and `BT_SPP_connectSPP_UUID`, including service registration, channel selection and data delivery. Check whether the API can represent the Android Auto Wireless service.
3. Inspect the boot/secondary IFS files for exact driver names, supplicant build and OS metadata. Neither installed driver capability nor kernel version can be inferred from application filenames alone.
4. Confirm the actual module/application via Experiment 001. Establish native execution and recovery. The first live probe should observe a stock wired session and the identified callbacks before introducing network-backed I/O.

No firmware or persistent setting was changed during this experiment. Firmware changes are authorized by the owner; their necessity and compatibility will follow the module inventory and access findings.
