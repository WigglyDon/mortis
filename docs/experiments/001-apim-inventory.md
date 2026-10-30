# Experiment 001: APIM inventory

Date: October 30, 2026. Status: **prepared locally; not run on Mortis**.

Identify the actual APIM and installed software before choosing native access or radio experiments. The owner's displayed version is SYNC 3.3, build `19052_PRODUCT`.

## Prepared files

The verified USB layout is staged at `private/usb/interrogator-sync33/`:

```text
autoinstall.lst
DONTINDX.MSA
SyncMyRide/
  GB5T-14G386-AB_134244.tar.gz
```

Preparation is reproducible with Python 3 and its standard library:

```sh
python3 tools/prepare_interrogator.py
```

It downloads the pinned Ford package, checks its size, SHA-256, published MD5, archive member names and sizes, then creates a new staging directory. It refuses to overwrite an existing directory. The archive stays compressed on the USB. The preparation tool does not execute its contents.

## Using the ThinkPad for the USB step

The Mac has no USB-A port and the available flash drive is USB-A. The owner chose to continue the project on the Linux ThinkPad using a fresh GitHub clone and reports that the stick is plugged into it. The drive's filesystem/contents have not yet been checked. Run `python3 tools/prepare_interrogator.py` in the clone to regenerate the local staging files; previous Mac `private/` files are not in GitHub. See [ThinkPad handover](../thinkpad.md).

A transfer archive has been prepared and checked at `private/transfers/mortis-interrogator-sync33.zip` (44,573 bytes). It contains exactly the three files in the layout above, with no enclosing folder. ZIP SHA-256: `6e7efb2a87c814f4ba04bbb30169116ef6749565cbbb525746805e8d4239fab6`.

On the ThinkPad, inspect the drive and preserve existing contents first. Extract the archive so `autoinstall.lst`, `DONTINDX.MSA` and `SyncMyRide/` sit at the USB root. Eject the drive, run the logger in Mortis as described below, then retrieve the XML using the ThinkPad. Transfer the raw capture into an ignored `private/` directory for analysis. The archive remains local and is not available through a fresh Git clone.

The ThinkPad does not connect directly to the van for this procedure. SYNC reads the drive, runs the packaged information-gathering utility and writes the report onto the drive. This gives us inventory, not an interactive shell.

## Package provenance and inspection

The [Interrogator guide](https://community.cyanlabs.net/t/apim-interrogator-utility-create-interrogator-log/1856) specifies `GB5T-14G386-AB` for SYNC 3.2/3.3. Its [software database](https://cyanlabs.net/fhub/sync3/sw-db/) loads records from [CyanLabs' IVSU API](https://api.cyanlabs.net/ford/sync3/ivsus). Record 938 returned the following on October 30:

| Check | Observed value |
| --- | --- |
| Published size | 44,159 bytes |
| Published and measured MD5 | `10d7ec51673a87a15c72627c2b3c838b` |
| Measured SHA-256 | `bfe7c0b31772b2299282ca842a07e0fdcd0a08a0b5a423203901d70c2832b96e` |
| Download destination after redirect | [Ford's package server](https://ivsu.binaries.ford.com/swparts/GB5T-14G386-AB_134244.tar.gz) |

Locally inspected members:

| Member | Bytes | Observation |
| --- | ---: | --- |
| `Decoded_ODL.xml` | 9,478 | APIM diagnostic identifiers requested by the logger |
| `GB5T-14G386-AB.sh` | 2,231 | Calls `utloggingutility interlog` and validates the XML |
| `utloggingutility` | 85,628 | 32-bit little-endian ARM EABI5 ELF; loader `/usr/lib/ldqnx.so.2` |
| `Version.der` | 2,401 | Package metadata; no independent signature validation performed |

The reviewed script performs cache/log housekeeping, including copying the DID list into the IVSU cache when absent and normalizing the USB XML. It contains no reformat or firmware replacement command. This is inventory collection with incidental writes, rather than a strictly read-only operation. The proprietary utility itself has not been audited. The binary's architecture describes the package target, not a measurement of Mortis's processor or QNX release.

## Physical execution

No external physical disk was reported by `diskutil` and no removable volume was mounted during preparation. Nothing has been copied to a drive or run in the van.

1. Connect a spare USB flash drive. Identify its volume, filesystem and contents before writing. Use an exFAT drive; preserve existing files and any old installation manifests before preparing it. Do not merge active installation manifests from another update.
2. Copy the three staged root items above to the drive's root, then verify the package hash and `Open1` path on the drive. Eject it cleanly.
3. With Mortis parked and SYNC powered, insert the drive and wait for the completion message. Remove it after completion. If an error appears, record it; do not substitute an upgrade/reformat package.
4. Return the drive to the ThinkPad or another computer that accepts it. Copy its returned XML into `private/captures/`, keeping the original filename and raw contents private. Transfer it to the research machine if needed.
5. Summarize locally, substituting the actual log path:

```sh
python3 tools/summarize_interrogator.py private/captures/ACTUAL_LOG.xml > private/apim-summary.json
```

The parser emits only recognized part numbers, installed package numbers, and known partition capacities. It excludes VIN, serial and MAC DIDs, direct configuration, timestamps, filenames and unrecognized text. Review the result before adding a dated public hardware summary.

## Result and next decision

Local download, package inspection and staging succeeded. The hardware result is **pending physical execution**. No APIM, Wi-Fi chipset or QNX version has been identified from Mortis.

Use the returned assembly and application numbers to select the stock software image and a compatible development access method. This logger does not establish a shell, enumerate processes, identify radio modes, or prove that wireless projection can run natively.
