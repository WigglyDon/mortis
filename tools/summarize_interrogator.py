#!/usr/bin/env python3
"""Extract allowlisted part numbers and storage from a private APIM XML log."""

import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


PART_DIDS = {
    "8033": "SYNC application",
    "F110": "Diagnostic database",
    "F111": "APIM core assembly",
    "F113": "APIM delivery assembly",
    "F124": "APIM calibration",
    "F188": "APIM strategy",
}
PACKAGE_DIDS = {"8060", "8061"}
PART = re.compile(r"(?:DS-)?[A-Z0-9]{4}-[A-Z0-9]{6}-[A-Z0-9]{1,5}")
PARTITIONS = {"/fs/Nuance/", "/fs/rwdata/", "/fs/mp/", "/fs/images/"}
CAPACITY = re.compile(r"[0-9]+(?:\.[0-9]+)?[KMGT]?")


def local_name(name):
    return name.rsplit("}", 1)[-1].lower()


def decode_parts(response):
    text = response.strip().strip("\x00")
    if PART.fullmatch(text):
        return [text]
    compact = "".join(text.split())
    if not compact or len(compact) % 2 or not re.fullmatch(r"[0-9a-fA-F]+", compact):
        return []
    decoded = bytes.fromhex(compact).decode("ascii", errors="replace")
    # Packeted responses are NUL-padded part-number slots. Never pass raw text on.
    return [slot.strip() for slot in decoded.split("\x00") if PART.fullmatch(slot.strip())]


def summarize(data):
    if len(data) > 5 * 1024 * 1024:
        raise ValueError("XML exceeds the 5 MiB inventory limit.")
    text = data.decode("utf-8-sig")
    if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
        raise ValueError("DTD/entity declarations are not supported.")
    root = ET.fromstring(text)
    parts = {}
    packages = set()
    storage = []
    for element in root.iter():
        attrs = {local_name(key): value for key, value in element.attrib.items()}
        if local_name(element.tag) == "did":
            did = attrs.get("didvalue", "").upper()
            if did not in PART_DIDS and did not in PACKAGE_DIDS:
                continue
            responses = [child for child in element if local_name(child.tag) == "response"]
            values = sorted({
                part for response in responses
                for part in decode_parts("".join(response.itertext()))
            })
            if did in PACKAGE_DIDS:
                packages.update(values)
            elif values:
                parts[did] = {"label": PART_DIDS[did], "part_numbers": values}
        elif local_name(element.tag) == "partitionhealth":
            path = attrs.get("type", "")
            total, available = attrs.get("total", ""), attrs.get("available", "")
            if path in PARTITIONS and CAPACITY.fullmatch(total) and CAPACITY.fullmatch(available):
                storage.append({"partition": path, "total": total, "available": available})
    if not parts and not packages and not storage:
        raise ValueError("No supported APIM inventory fields found.")
    return {
        "part_numbers": parts,
        "installed_packages": sorted(packages),
        "storage": storage,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    args = parser.parse_args()
    try:
        result = summarize(args.log.read_bytes())
    except (OSError, ValueError, ET.ParseError):
        # Do not echo source filenames, raw values, or decoder errors containing data.
        parser.exit(1, "Cannot summarize this log; inspect it locally in private/.\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
