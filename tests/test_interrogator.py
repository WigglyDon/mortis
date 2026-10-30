"""Offline checks for package staging and the public inventory boundary."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools import prepare_interrogator as prepare
from tools.summarize_interrogator import summarize


def did(number, value):
    return '<m:DID didValue="' + number + '"><m:Response>' + value + '</m:Response></m:DID>'


def xml(contents):
    return ('<Log xmlns:m="urn:test">' + contents + '</Log>').encode()


class SummaryTests(unittest.TestCase):
    def test_namespaced_inventory_excludes_identifiers_and_configuration(self):
        package = b"4U5T-14G381-AN\0\0GB5T-14G386-AB\0".hex()
        data = xml(
            '<VIN>TESTVIN12345678901</VIN>'
            + did("F111", "5U5T-14G380-AA")
            + did("F113", b"5U5T-14G371-ABC\0".hex())
            + did("F18C", "PRIVATE-SERIAL")
            + did("F141", "PRIVATE-RADIO-SERIAL")
            + did("F1D0", "123456789abc")
            + did("F1D1", "12:34:56:78:9a:bd")
            + did("DE00", "PRIVATE-CONFIG")
            + did("8060", package) + did("8061", "00" * 384)
            + '<m:PartitionHealth type="/fs/rwdata/" total="1.2G" available="500M"/>'
            + '<m:PartitionHealth type="/private/identifier" total="1G" available="0"/>'
        )
        result = summarize(data)
        self.assertEqual(result["part_numbers"]["F111"]["part_numbers"], ["5U5T-14G380-AA"])
        self.assertEqual(result["part_numbers"]["F113"]["part_numbers"], ["5U5T-14G371-ABC"])
        self.assertEqual(result["installed_packages"], ["4U5T-14G381-AN", "GB5T-14G386-AB"])
        self.assertEqual(result["storage"], [{"partition": "/fs/rwdata/", "total": "1.2G", "available": "500M"}])
        public = json.dumps(result)
        for secret in ["TESTVIN", "PRIVATE", "123456789abc", "12:34:56", "identifier", "DE00", "F18C", "F141"]:
            self.assertNotIn(secret, public)

    def test_unknown_or_malformed_values_never_pass_through(self):
        data = xml(did("F111", "PRIVATE-SERIAL") + did("F188", "not hex") + did("8060", "abc"))
        with self.assertRaisesRegex(ValueError, "No supported"):
            summarize(data)

    def test_rejects_entity_declarations(self):
        with self.assertRaisesRegex(ValueError, "DTD/entity"):
            summarize(b'<!DOCTYPE Log [<!ENTITY secret "private">]><Log/>')

    def test_parser_errors_do_not_echo_private_filenames_or_values(self):
        with tempfile.TemporaryDirectory() as temporary:
            log = Path(temporary) / "TESTVIN12345678901.xml"
            log.write_bytes(b'<Log>PRIVATE-SERIAL<broken')
            result = subprocess.run(
                [sys.executable, "tools/summarize_interrogator.py", str(log)],
                capture_output=True, text=True,
                cwd=Path(__file__).resolve().parents[1],
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertNotIn("TESTVIN", result.stderr)
            self.assertNotIn("PRIVATE-SERIAL", result.stderr)


class PreparationTests(unittest.TestCase):
    def test_changed_package_is_rejected_before_creating_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "usb"
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                prepare.prepare(b"unreviewed package", output)
            self.assertFalse(output.exists())

    def test_cli_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "existing-capture.xml"
            marker.write_bytes(b"preserve this capture")
            result = subprocess.run(
                [sys.executable, "tools/prepare_interrogator.py", "--output", temporary],
                capture_output=True, text=True,
                cwd=Path(__file__).resolve().parents[1],
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("refusing to overwrite", result.stderr)
            self.assertEqual(marker.read_bytes(), b"preserve this capture")
            self.assertEqual(list(Path(temporary).iterdir()), [marker])


if __name__ == "__main__":
    unittest.main()
