"""Forward output must separate source acquisition from scientific comparison."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import compare_pnas2017_engines as comparison
import pnas2017_s28_status as status
import run_pnas2017_reference as reference

ROOT = Path(__file__).resolve().parents[1]


class S28StatusTests(unittest.TestCase):
    def test_acquired_readable_does_not_mean_compared(self):
        result = status.dataset_s28_status(ROOT)
        self.assertEqual(result["dataset_s28_acquisition_status"], "ACQUIRED")
        self.assertEqual(result["dataset_s28_readability_status"], "READABLE")
        self.assertEqual(result["dataset_s28_pointwise_comparison_status"], "NOT_RUN")
        self.assertEqual(len(result["dataset_s28_sheet_names"]), 7)
        self.assertNotIn("dataset_s28_comparison", result)

    def test_missing_is_separate_from_not_run(self):
        with tempfile.TemporaryDirectory() as directory:
            result = status.dataset_s28_status(Path(directory))
        self.assertEqual(result["dataset_s28_acquisition_status"], "NOT_ACQUIRED")
        self.assertEqual(result["dataset_s28_readability_status"], "NOT_CHECKED")
        self.assertEqual(result["dataset_s28_pointwise_comparison_status"], "NOT_RUN")

    def test_unregistered_or_unreadable_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / status.S28
            path.parent.mkdir(parents=True)
            path.write_bytes(b"not a workbook")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                status.dataset_s28_status(root)
            with patch.object(status, "S28_SHA", hashlib.sha256(path.read_bytes()).hexdigest()):
                with self.assertRaises(status.zipfile.BadZipFile):
                    status.dataset_s28_status(root)

    def test_fresh_comparison_output_and_preserved_history(self):
        frozen = comparison.RUN / "engine_comparison.json"
        before = frozen.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "comparison.json"
            comparison.main(output)
            result = json.loads(output.read_text())
            self.assertEqual(result["dataset_s28_acquisition_status"], "ACQUIRED")
            self.assertEqual(result["dataset_s28_readability_status"], "READABLE")
            self.assertEqual(result["dataset_s28_pointwise_comparison_status"], "NOT_RUN")
            self.assertFalse(any("unavailable" in v for v in result["limitations"]))
            with self.assertRaises(FileExistsError):
                comparison.main(output)
        self.assertEqual(before, frozen.read_bytes())

    def test_reference_refuses_existing_frozen_run_before_writes(self):
        with patch.dict(sys.modules, {"libsbml": object()}):
            with self.assertRaises(FileExistsError):
                reference.run("rr_cvode_author_csv_20260924", True)


if __name__ == "__main__":
    unittest.main()
