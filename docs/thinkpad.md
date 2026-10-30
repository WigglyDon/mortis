# Continue on the Linux ThinkPad

The owner chose the Linux ThinkPad as the working machine. It accepts the available USB-A flash drive and is a suitable host for the next embedded development work. Continue from the existing findings; do not restart the investigation.

## Selected handover: clone from GitHub

The owner chose a fresh GitHub clone and a fresh agent session on the Linux ThinkPad. The USB-A stick is already connected there. Clone `https://github.com/WigglyDon/mortis.git`, open the checkout, and read `HANDOFF.md`. The current tools, research findings and handoff are committed to `main`.

Ignored `private/` files are not in GitHub. Regenerate the logger immediately with:

```sh
python3 tools/prepare_interrogator.py
```

This downloads and verifies the small Ford logger package into local staging. Then inspect the connected stick and proceed with the hardware step below. No private archive is required for inventory collection.

## Optional transfer of existing private research

The Mac has a prepared archive at `private/transfers/mortis-thinkpad.zip`. It contains Git history, the current working files including uncommitted changes, the verified logger, the downloaded stock Ford package, and the completed inspection reports and selected extracts. Proprietary software stays under ignored `private/` paths.

Copy that archive to the ThinkPad using an available network/file-transfer method. Extract it into a temporary directory, enter its `mortis-transfer` directory, and run:

```sh
bash restore.sh "$HOME/mortis"
```

The restore script requires Git, refuses an existing destination, creates the checkout from the included Git bundle and overlays the current working files. It sets the existing GitHub origin without pushing anything. No Mac virtual environment or installed tools are copied.

This archive predates the final GitHub handover and preserves an earlier uncommitted snapshot. Prefer the fresh clone. If reusing private files from the archive, copy only its `workspace/private/` research inputs into the clone and keep the current GitHub documentation and tools.

## Research environment

Use Python 3.9 or newer. Create a new Linux virtual environment:

```sh
python3 -m venv private/research/venv
private/research/venv/bin/python -m pip install -r tools/research-requirements.txt
python3 -m unittest discover -s tests -v
```

The optional transfer includes the original compressed Ford package. In a fresh clone, retrieve it from Ford when continuing static analysis:

```sh
mkdir -p private/research
curl --fail --location --output private/research/4U5T-14G381-AN.tar.gz \
  https://ivsu.binaries.ford.com/swparts/4U5T-14G381-AN_1552583626000.TAR.GZ
```

Preserve an existing package instead of overwriting it. Recreate `apps.img` when needed, verifying the package first:

```sh
private/research/venv/bin/python - <<'PY'
import hashlib, shutil, tarfile
from pathlib import Path
package = Path('private/research/4U5T-14G381-AN.tar.gz')
digest = hashlib.sha256()
with package.open('rb') as source:
    for chunk in iter(lambda: source.read(1024 * 1024), b''):
        digest.update(chunk)
assert digest.hexdigest() == 'b2958f001f2efb76e7edb64aa5814babccb5e97d283716b15e555300f2d7bdb9'
target = Path('private/research/sync33/apps.img')
assert not target.exists(), 'Preserve existing image; no extraction needed.'
target.parent.mkdir(parents=True, exist_ok=True)
with tarfile.open(package, 'r:gz') as outer:
    with tarfile.open(fileobj=outer.extractfile('apps.tar.gz'), mode='r|gz') as inner:
        for member in inner:
            if member.name == 'apps.img':
                with target.open('xb') as output:
                    shutil.copyfileobj(inner.extractfile(member), output)
                break
        else:
            raise RuntimeError('apps.img absent from package')
PY
```

If the private inspection results were transferred, use them immediately. Otherwise, the findings are recorded in [Experiment 002](experiments/002-stock-image-inspection.md), and `tools/inspect_sync_image.py` can regenerate detailed reports from the extracted image. This is reconstruction of local research artifacts, not a new investigation.

## First hardware step

The USB-A stick is already plugged into the ThinkPad according to the owner. Inspect it with `lsblk -f` and mounted-volume information. Identify its mount point, filesystem and existing contents before writing. After running the preparation tool, the ready-to-copy files are under `private/usb/interrogator-sync33/`. Follow [Experiment 001](experiments/001-apim-inventory.md), preserving existing contents and previous installation manifests. Formatting has not been found necessary; do not erase the drive as a default preparation step.

The laptop prepares the stick; SYNC runs the logger from it and returns XML. Shell/native-code access to Mortis remains an open investigation. Firmware and device changes are already authorized, subject to selecting compatible procedures and a recovery path.
