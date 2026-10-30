# Mortis

Mortis is my **2020 Ford Transit Connect XLT**. This is the project home for everything about him: maintenance, repairs, upgrades, software, and experiments.

The aim is to understand the van, improve the things that are frustrating, and build our own solutions where useful. Original development and reverse engineering are part of the project; an existing community solution is a starting point when it helps.

## Start here

- [Current handoff](HANDOFF.md) — the immediate wireless Android Auto assignment and project context.
- [Linux ThinkPad transfer](docs/thinkpad.md) — resume the existing work on the chosen development machine.
- [Vehicle profile](docs/vehicle.md) — what we know about Mortis.
- [Roadmap](docs/roadmap.md) — the next steps and longer-term interests.
- [SYNC 3 investigation](docs/research/sync3.md) — findings, sources, and open technical questions.
- [Native wireless architecture](docs/research/wireless-native.md) — protocol boundaries, access research, and the first native experiment.
- [APIM inventory experiment](docs/experiments/001-apim-inventory.md) — verified logger package, staged USB layout, and capture procedure.
- [Stock receiver inspection](docs/experiments/002-stock-image-inspection.md) — Android Auto transport, Wi-Fi and Bluetooth evidence from the matching stock image.

## First project

Investigate wireless Android Auto using Mortis's existing SYNC 3 system. The immediate milestone is a hardware inventory and a usable inspection method. Running our own wireless receiver inside SYNC is a hypothesis to test.

The desired experience is automatic wireless startup when the phone reconnects to the van, with reliable recovery across repeated DoorDash delivery stops.

Other work can grow alongside this: maintenance records, electrical systems, interior changes, and our own vehicle software.

## Project status

Started on October 30, 2026. The SYNC 3.3 inventory logger is verified and staged locally. Offline inspection of the matching stock image identified the Android Auto receiver and candidate USB, Wi-Fi and Bluetooth interfaces. Python tools reproduce inspection and summarize returned inventory logs without exporting vehicle or device identifiers. Native execution on Mortis remains unverified; no firmware has been changed as part of this project.

## Working notes

Record observations separately from assumptions, and attach evidence to technical conclusions. Keep raw diagnostic captures in the ignored `private/` or `raw/` directories; publish reviewed summaries with vehicle and device identifiers removed.

Run the local tool checks with `python3 -m unittest discover -s tests -v`.
