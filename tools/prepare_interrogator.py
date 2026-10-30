#!/usr/bin/env python3
"""Verify and stage Ford's SYNC 3.2/3.3 inventory logger locally."""

import argparse
import hashlib
import io
from pathlib import Path
import tarfile
import urllib.request


PACKAGE = "GB5T-14G386-AB_134244.tar.gz"
URL = "https://ivsu.binaries.ford.com/swparts/" + PACKAGE
SIZE = 44159
# MD5 published by CyanLabs; SHA-256 measured from Ford's download on 2026-10-30.
MD5 = "10d7ec51673a87a15c72627c2b3c838b"
SHA256 = "bfe7c0b31772b2299282ca842a07e0fdcd0a08a0b5a423203901d70c2832b96e"
MEMBERS = {
    "Decoded_ODL.xml": 9478,
    "GB5T-14G386-AB.sh": 2231,
    "utloggingutility": 85628,
    "Version.der": 2401,
}
AUTOINSTALL = (
    "[SYNCGen3.0_ALL]\r\n"
    "Item1 = GB5T-14G386-AB\r\n"
    "Open1 = SyncMyRide\\" + PACKAGE + "\r\n"
    "Options = Delay,Include,Transaction\r\n"
).encode("ascii")


def verify(data):
    """Check pinned bytes and archive contents without extracting or executing."""
    if len(data) != SIZE or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("Package does not match the reviewed Ford download (SHA-256/size).")
    if hashlib.md5(data).hexdigest() != MD5:
        raise ValueError("Package does not match the published CyanLabs MD5.")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = archive.getmembers()
        if len(members) != len(MEMBERS) or {
            member.name: member.size for member in members
        } != MEMBERS or not all(member.isfile() for member in members):
            raise ValueError("Unexpected logger archive contents.")


def prepare(data, output):
    verify(data)
    # Never overwrite a drive, previous staging directory, or returned captures.
    output.mkdir(parents=True, exist_ok=False)
    (output / "SyncMyRide").mkdir()
    (output / "SyncMyRide" / PACKAGE).write_bytes(data)
    (output / "autoinstall.lst").write_bytes(AUTOINSTALL)
    (output / "DONTINDX.MSA").write_bytes(b"")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, help="Use a previously downloaded package.")
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parents[1] / "private/usb/interrogator-sync33",
        help="New local staging directory; must not already exist.",
    )
    args = parser.parse_args()
    if args.output.exists():
        parser.exit(1, "Output already exists; refusing to overwrite it.\n")
    try:
        if args.package:
            data = args.package.read_bytes()
        else:
            with urllib.request.urlopen(URL, timeout=30) as response:
                data = response.read(SIZE + 1)
        prepare(data, args.output)
    except (OSError, ValueError, tarfile.TarError) as error:
        parser.exit(1, "Preparation failed: " + str(error) + "\n")
    print("Verified and staged: " + str(args.output))
    print("SHA-256: " + SHA256)
    print("No device was accessed. See docs/experiments/001-apim-inventory.md before use.")


if __name__ == "__main__":
    main()
