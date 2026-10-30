#!/usr/bin/env python3
"""Inventory a stock QNX6 apps.img and inspect selected files without executing them."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import re

from dissect.qnxfs.qnx6 import QNX6
from elftools.elf.elffile import ELFFile


SELECTED = (
    "/Version.inf",
    "/apps/MM_GalService",
    "/apps/MM_ProjectionService",
    "/apps/NET_WifiConnectionMgr",
    "/apps/NET_BT_Service",
    "/apps/CORAL_BT.exe",
    "/apps/usr/lib/libMM_ProjectionClient.so",
    "/apps/usr/lib/libBtStack_API.so",
    "/apps/usr/lib/libBT_Service_API.so",
    "/usr/lib/libaoa.so.1",
    "/etc/system/config/ss_launch_config.cfg",
    "/etc/wifi_config.conf",
    "/etc/net_bt_cfg.xml",
    "/etc/usblauncher/rules.lua",
    "/etc/usblauncher/rules_otg.lua",
    "/scripts/startup_gf.sh",
    "/scripts/startup_script_functions.sh",
    "/sql/projection.cfg",
    "/sql/projection.sql",
)
SYMBOLS = re.compile(r"Transport|aoa_|P2P|^socket$|QnxDeviceManager.*onConnect|rfcomm|sdp|spp", re.IGNORECASE)


def digest_file(handle):
    digest = hashlib.sha256()
    handle.seek(0)
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def inventory(node, path="", seen=None):
    if seen is None:
        seen = set()
    if node.inum in seen:
        return
    seen.add(node.inum)
    for name, child in node.iterdir():
        if name in (".", ".."):
            continue
        full = path + "/" + name
        row = {
            "path": full, "size": child.size, "inode": child.inum,
            "type": "directory" if child.is_dir() else "symlink" if child.is_symlink() else "file",
        }
        if child.is_symlink():
            row["target"] = child.link
        yield row
        if child.is_dir():
            yield from inventory(child, full, seen)


def elf_info(data):
    elf = ELFFile(io.BytesIO(data))
    dynamic = elf.get_section_by_name(".dynamic")
    symbols = elf.get_section_by_name(".dynsym")
    return {
        "machine": elf["e_machine"],
        "class_bits": elf.elfclass,
        "little_endian": elf.little_endian,
        "needed": [tag.needed for tag in dynamic.iter_tags() if tag.entry.d_tag == "DT_NEEDED"] if dynamic else [],
        "selected_symbols": [
            {
                "name": symbol.name, "address": hex(symbol.entry.st_value),
                "size": symbol.entry.st_size,
                "defined": symbol.entry.st_shndx != "SHN_UNDEF",
            }
            for symbol in symbols.iter_symbols() if SYMBOLS.search(symbol.name)
        ] if symbols else [],
    }


def inspect(image, output):
    # All extraction destinations below come from our fixed SELECTED paths.
    # The image is opened read-only; extracted binaries are never executed.
    output.mkdir(parents=True, exist_ok=False)
    with image.open("rb") as handle:
        image_hash = digest_file(handle)
        fs = QNX6(handle)
        rows = list(inventory(fs.root))
        (output / "file-inventory.json").write_text(json.dumps(rows, indent=2) + "\n")
        available = {row["path"]: row for row in rows}
        selected = []
        for path in SELECTED:
            if path not in available or available[path]["type"] != "file":
                continue
            data = fs.get(path).open().read()
            target = output / "extracted" / path.lstrip("/")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            row = {"path": path, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            if data.startswith(b"\x7fELF"):
                row["elf"] = elf_info(data)
            selected.append(row)
        report = {
            "image_sha256": image_hash,
            "filesystem": "QNX6", "block_size": fs.block_size,
            "entry_count": len(rows), "selected_files": selected,
            "selected_files_absent": [path for path in SELECTED if path not in available],
        }
        (output / "inspection.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="New private output directory.")
    args = parser.parse_args()
    if args.output.exists():
        parser.exit(1, "Output already exists; refusing to overwrite it.\n")
    report = inspect(args.image, args.output)
    print("Inventoried " + str(report["entry_count"]) + " entries; inspected " + str(len(report["selected_files"])) + " files.")
    print("Reports and private extracts: " + str(args.output))


if __name__ == "__main__":
    main()
