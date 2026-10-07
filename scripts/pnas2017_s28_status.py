"""Publisher-file integrity/readability only; no trajectory comparison."""
import hashlib
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

S28 = "references/PNAS2017_Matsuura/raw/pnas.1615351114.sd28.xlsx"
S28_SHA = "8297f2348f5ebdfc3c14083577f2c5f276f35a7ee8ab30f8a37fd8431ef565ec"


def dataset_s28_status(root: Path) -> dict:
    result = {
        "dataset_s28_acquisition_status": "NOT_ACQUIRED",
        "dataset_s28_readability_status": "NOT_CHECKED",
        "dataset_s28_pointwise_comparison_status": "NOT_RUN",
    }
    path = root / S28
    if not path.is_file():
        return result
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != S28_SHA:
        raise ValueError("Dataset S28 differs from the registered publisher SHA-256")
    with zipfile.ZipFile(path) as archive:
        # Read and parse every workbook XML part, including all worksheet cells.
        # OOXML readability does not establish scientific agreement.
        for name in archive.namelist():
            if name.endswith(".xml") or name.endswith(".rels"):
                ET.fromstring(archive.read(name))
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = workbook.findall("{*}sheets/{*}sheet")
        if len(sheets) != 7:
            raise ValueError("Dataset S28 must contain the seven registered sheets")
    result.update(dataset_s28_acquisition_status="ACQUIRED",
                  dataset_s28_readability_status="READABLE",
                  dataset_s28_sha256=digest,
                  dataset_s28_sheet_names=[sheet.attrib["name"] for sheet in sheets])
    return result
