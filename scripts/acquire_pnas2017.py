"""Freeze the publicly downloadable files linked by the authors' PURE simulator.

This script copies original bytes only. It never rewrites an existing raw file.
Dataset spreadsheets and the paper/SI are registered separately when obtained.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "references" / "PNAS2017_Matsuura" / "raw"
PROVENANCE = ROOT / "references" / "PNAS2017_Matsuura" / "provenance"
ORIGINAL = ROOT / "models" / "pnas2017_full_reference" / "original"
DOI = "10.1073/pnas.1615351114"
ACCESS_DATE = "2026-09-24"
SOURCE_PAGE = "https://sites.google.com/view/puresimulator"
SOURCES = (
    (
        "fMGG_synthesis.xml",
        "17hCxjOpbypq-ri2gOEL-ByTDQNlIit-2",
        "xml",
        True,
    ),
    (
        "SBML_files.zip",
        "1IQ2cBPcF4uBM4lc1Mn7u3ae8XQLNsJij",
        "zip",
        False,
    ),
    (
        "Simulate_fMGG_synthesis.zip",
        "1qnRPhyw2p_8tAy4kNY7Vd1SkEcb6x5xy",
        "zip",
        False,
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_format(path: Path, kind: str) -> None:
    if kind == "zip":
        if not zipfile.is_zipfile(path):
            raise ValueError(f"Expected ZIP content: {path}")
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError(f"Corrupt ZIP member: {bad}")
    elif kind == "xml":
        root = ET.parse(path).getroot()
        if root.tag.split("}")[-1] != "sbml":
            raise ValueError(f"Expected SBML root, got {root.tag}")
    else:
        raise ValueError(kind)


def freeze_download(name: str, file_id: str, kind: str, confirm: bool) -> dict:
    RAW.mkdir(parents=True, exist_ok=True)
    destination = RAW / name
    url = (
        "https://drive.usercontent.google.com/download"
        f"?id={file_id}&export=download"
        + ("&confirm=t" if confirm else "")
    )
    if not destination.exists():
        request = Request(url, headers={"User-Agent": "PURE-source-acquisition/1.0"})
        partial = destination.with_name(destination.name + ".partial")
        with urlopen(request, timeout=120) as response, partial.open("wb") as output:
            shutil.copyfileobj(response, output)
        try:
            validate_format(partial, kind)
            partial.replace(destination)
        finally:
            partial.unlink(missing_ok=True)
    validate_format(destination, kind)
    return {
        "path": destination.relative_to(ROOT).as_posix(),
        "original_filename": name,
        "source_page": SOURCE_PAGE,
        "download_url": url,
        "doi": DOI,
        "access_date": ACCESS_DATE,
        "format_inspected": kind,
        "bytes": destination.stat().st_size,
        "sha256": sha256(destination),
        "license_status": "No explicit reuse license found on the authors' download page; redistribution rights unresolved.",
    }


def copy_original(source: Path, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copyfile(source, destination)
    if sha256(source) != sha256(destination):
        raise ValueError(f"Immutable original differs from source: {destination}")
    return {
        "path": destination.relative_to(ROOT).as_posix(),
        "bytes": destination.stat().st_size,
        "sha256": sha256(destination),
        "source_path": source.relative_to(ROOT).as_posix(),
        "transformation": "byte-identical copy",
    }


def main() -> None:
    entries = [freeze_download(*source) for source in SOURCES]
    copies = [copy_original(RAW / "fMGG_synthesis.xml", ORIGINAL / "fMGG_synthesis.xml")]
    PROVENANCE.mkdir(parents=True, exist_ok=True)
    manifest = {
        "benchmark": "PNAS2017_full_reference",
        "doi": DOI,
        "access_date": ACCESS_DATE,
        "source_files": entries,
        "model_copies": copies,
        "note": "The combined XML was format-inspected as SBML. ZIP contents have not been silently promoted to the canonical model. Publisher Dataset S27 remains unavailable; its listed .xlsx filename does not establish the actual file contents or format.",
    }
    path = PROVENANCE / "sources.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for entry in entries:
        print(entry["path"], entry["bytes"], entry["sha256"])


if __name__ == "__main__":
    main()
