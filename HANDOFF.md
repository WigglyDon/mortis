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

## Current state

- Local checkout: `/Users/mradmin/mortis`.
- Public remote: https://github.com/WigglyDon/mortis, branch `main`.
- Repositories belong directly under `/Users/mradmin`, not `Developer`.
- The old `/Users/mradmin/Developer` folder was moved to Trash at the owner's request; do not restore it as part of this project.
- A direct Mac-to-van USB connection was attempted. Mac enumeration exposed no SYNC device, serial console, or disk. This did not provide access to SYNC internals. A separate connected Pixel was visible; no phone inspection was performed.
- No custom program has run on SYNC and no firmware has been changed by this project.
- The initial research and its sources are in `docs/research/sync3.md`.

## Start here

1. Inspect the current checkout and device connections. Keep conclusions tied to what is actually observed.
2. Prepare the information-gathering USB logger for SYNC 3.3 (`GB5T-14G386-AB`, subject to checking the source and package). Prepare and verify the files locally; physical execution needs a USB flash drive and the owner. If a suitable drive is already available, identify it before writing to it and preserve existing contents.
3. Collect the APIM hardware inventory and publish a summary. Raw logs can contain VINs and device identifiers: keep them in ignored `private/` or `raw/` folders.
4. Investigate a native QNX development/access path and the installed Wi-Fi/Bluetooth drivers and Android Auto transport boundary. The initial inventory logger alone does not provide a shell or process listing.
5. Define a small experiment that resolves the first native implementation uncertainty. Record the result and next step in the repository.

Check the actual module before considering old reformat/update instructions; MY20 incompatibilities are documented in the research. An inventory request is not a reason to reflash the system.

Success should eventually be demonstrated by automatic startup, usable maps/audio/calls/controls, and reliable recovery across repeated stops. Begin with inventory and a testable access path, and keep the owner informed without making them design the investigation.
