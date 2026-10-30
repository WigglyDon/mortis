# Roadmap

## First milestone: identify the SYNC hardware

- [x] Record the van's model and displayed SYNC version.
- [x] Check what a direct USB connection exposes to the Mac.
- [ ] Prepare a diagnostic USB flash drive appropriate for SYNC 3.3.
- [ ] Collect the APIM inventory and review the log locally.
- [ ] Record the hardware part number, installed packages, and storage configuration in a public summary.

Done means we can identify the actual module and choose a development access method from evidence.

## Next milestone: establish a development path

- Determine how to inspect the installed software and obtain the required files.
- Identify the exact QNX release, processor architecture, and compatible build tools.
- Investigate how to run a small native diagnostic program.
- Inventory the Wi-Fi and Bluetooth drivers and the Android Auto receiver interfaces.
- Identify a recovery method before making persistent system changes.

Done means we can build and run a small program for this unit and collect the information needed to evaluate wireless projection.

## Wireless Android Auto experiment

Determine whether a native service can establish a wireless session and pass it into SYNC's existing Android Auto receiver. Check the radio and driver modes, connection setup, receiver transport, audio, controls, startup, and reconnection behavior.

An external USB bridge is another available experiment if it helps isolate the protocol or receiver behavior. The preferred architecture will follow the findings.

## Work across the van

Add these as they become useful:

- Maintenance history, repairs, parts, and service intervals.
- Electrical and power improvements.
- Interior and practical upgrades.
- Diagnostics and vehicle data.
- Our own dashboard software and connected tools.

Each new project should begin with the problem, a small first experiment, and an observable result. There are no fixed delivery dates yet.
