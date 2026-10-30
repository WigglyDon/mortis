# Mortis handoff

## Immediate assignment

Take over this project and start investigating our own wireless Android Auto for Mortis. Read `README.md`, `docs/vehicle.md`, `docs/roadmap.md`, and `docs/research/sync3.md` first, then act on the first useful technical step.

Mortis is the owner's 2020 Ford Transit Connect XLT. He has SYNC 3, software version 3.3, displayed build `19052_PRODUCT`. The repository covers the whole van; wireless projection is the first project.

## Desired experience

The owner uses the van for DoorDash and repeatedly gets out and back in. The USB cable and unreliable Android Auto startup are frustrating. When the phone reconnects to the van over Bluetooth, Android Auto should start wirelessly on the existing screen with minimal intervention. Reconnection must work through repeated delivery stops and ignition cycles.

The owner sometimes calls this CarPlay, but the immediate target is **wireless Android Auto for an Android phone**. Bluetooth can be the discovery/setup trigger; the projection session needs a suitable data transport such as Wi-Fi. Bluetooth audio autoconnect already happens and the owner reports difficulty disabling it. Investigate that behavior rather than treating it as a confirmed platform restriction.

## Engineering approach

The owner explicitly wants original engineering and reverse engineering where required. An existing community mod is not a prerequisite. Prefer investigating a native implementation inside SYNC using its existing radios. Evaluate an external bridge if evidence shows it is necessary or useful for experimentation; do not silently replace the goal with buying a commercial adapter.

The user-facing goal is reasonable and wireless-to-USB bridges already demonstrate the general function. Native execution entirely inside this exact SYNC unit remains an open feasibility question. Identify the drivers and receiver interfaces before promising a software-only conversion. SYNC runs QNX Neutrino; the exact QNX release, APIM hardware, radio, and accessible interfaces remain unverified.

The owner explicitly authorized firmware updates and use/modification of his devices during the October 30 takeover session. Do not ask again for general permission already granted. Choose changes from module-specific evidence and establish recovery before persistent access changes.

## Current state

- **Current handover:** the owner is cloning `WigglyDon/mortis` from GitHub into a fresh session on the Linux ThinkPad. The USB-A flash drive is already plugged into that computer (owner report; not yet inspected). Read `docs/thinkpad.md` and proceed with device identification and logger preparation. The Mac paths below describe previous work, not files available in a fresh clone.
- Local checkout: `/Users/mradmin/mortis`.
- Public remote: https://github.com/WigglyDon/mortis, branch `main`.
- Repositories belong directly under `/Users/mradmin`, not `Developer`.
- The old `/Users/mradmin/Developer` folder was moved to Trash at the owner's request; do not restore it as part of this project.
- A direct Mac-to-van USB connection was attempted. Mac enumeration exposed no SYNC device, serial console, or disk. This did not provide access to SYNC internals. A separate connected Pixel was visible; no phone inspection was performed.
- No custom program has run on SYNC and no firmware has been changed by this project.
- The initial research and its sources are in `docs/research/sync3.md`.
- The SYNC 3.3 logger has been downloaded from Ford, matched to CyanLabs' MD5, inspected and staged at `private/usb/interrogator-sync33/`. See `docs/experiments/001-apim-inventory.md` for hashes and use. No USB flash drive was connected during preparation.
- The Mac has no USB-A port; the owner's only available stick is USB-A. The ThinkPad runs Linux and now has the stick connected. Its contents/filesystem remain unknown. Local transfer archives on the Mac are optional; the selected handover uses GitHub. Ignored packages, extracts, reports, virtual environments and staged USB files do not follow a clone. The tools and documented hashes allow regeneration on Linux.
- `tools/prepare_interrogator.py` reproduces staging; it refuses existing output directories. `tools/summarize_interrogator.py` emits allowlisted part numbers and storage from returned XML. Six offline tests cover identifier exclusion, malformed input, package rejection and preservation of existing files.
- `docs/research/wireless-native.md` records the reviewed Bluetooth bootstrap and TCP/USB transport boundaries, source references, candidate access method and the first native experiment.
- The stock `4U5T-14G381-AN` application package, listed as 3.3.19052, was downloaded from Ford and matched to its published MD5. Private offline files are under `private/research/sync33/`; the application filesystem is QNX6. Inventory DID `8033` must still confirm Mortis's installed package.
- **Receiver located offline:** `MM_GalService` defines `Transport`/`UsbTransport` vtables and imports `aoa_bulk_rx/tx` from `/usr/lib/libaoa.so.1`. `NET_WifiConnectionMgr` contains TI18xx/P2P supplicant paths. `libBtStack_API.so` exports SPP setup and UUID connection functions. See `docs/experiments/002-stock-image-inspection.md` for evidence, hashes and exact next targets. No callable wireless interface has been demonstrated yet.
- `tools/inspect_sync_image.py` reproduces QNX6 inventory and selected-file ELF inspection using the private venv and `tools/research-requirements.txt`. The tested run found all 19 selected files among 67,894 entries. Detailed captures are in `private/research/sync33/inspection-complete/`. Stock proprietary software is kept out of the public repository.

## Start here

1. On the Linux ThinkPad, inspect the checkout and connected USB stick using `lsblk -f` and mounted-volume information. Identify the actual removable device, filesystem, mount point and contents; preserve existing files before writing. The owner already authorized this work.
2. In a fresh clone, run `python3 tools/prepare_interrogator.py` to download, verify and stage the information-gathering USB logger for SYNC 3.3 (`GB5T-14G386-AB`). The previous Mac staging directory is not present on Linux. Prepare the identified stick following Experiment 001; preserve old installation manifests and captures, and do not format blindly. Physical insertion into Mortis and return of the stick require the owner.
3. Collect the APIM hardware inventory and publish a summary. Raw logs can contain VINs and device identifiers: keep them in ignored `private/` or `raw/` folders.
4. Investigate a native QNX development/access path and the installed Wi-Fi/Bluetooth drivers and Android Auto transport boundary. The initial inventory logger alone does not provide a shell or process listing.
5. Define a small experiment that resolves the first native implementation uncertainty. Record the result and next step in the repository.

While the physical inventory is pending, continue the next targets from Experiment 002: recover the AOA connection/buffer/callback contracts, map the transport virtual functions, determine whether the SPP API supports AA Wireless service registration, and inspect the IFS images for radio drivers and exact OS metadata. Existing findings and hashes are public documentation; redownloading and extracting the stock package on Linux is necessary if the optional private archive is not transferred. Follow `docs/thinkpad.md` rather than restarting the research.

Check the actual module before considering old reformat/update instructions; MY20 incompatibilities are documented in the research. An inventory request is not a reason to reflash the system.

Success should eventually be demonstrated by automatic startup, usable maps/audio/calls/controls, and reliable recovery across repeated stops. Begin with inventory and a testable access path, and keep the owner informed without making them design the investigation.
