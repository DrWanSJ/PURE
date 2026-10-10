"""Focused safety checks for the release wrapper; no scientific evidence edits."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).with_name("release.py")
spec = importlib.util.spec_from_file_location("phase_c_release", SCRIPT)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseSafety(unittest.TestCase):
    def test_path_traversal_is_refused_before_output(self):
        done = subprocess.run([sys.executable, str(SCRIPT), "verify", "--run-id", "../unsafe"],
                              capture_output=True, text=True)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("Unsafe run-id", done.stderr)

    def test_existing_run_refused_without_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            run = base / "already_exists"
            run.mkdir()
            marker = run / "original.bin"
            marker.write_bytes(b"immutable-original")
            with patch.object(release, "BASE", base), patch.object(sys, "argv", [str(SCRIPT), "verify", "--run-id", "already_exists"]):
                with self.assertRaises(FileExistsError):
                    release.main()
            self.assertEqual(marker.read_bytes(), b"immutable-original")
            self.assertEqual(list(run.iterdir()), [marker])

    def test_runtime_cannot_read_reference_trajectory(self):
        with tempfile.TemporaryDirectory() as directory:
            audit = release.AccessAudit(Path(directory))
            with audit.phase("R3_CHAIN12_RECYCLE.simulate"):
                with self.assertRaisesRegex(RuntimeError, "trajectory read"):
                    audit.hook("open", (str(Path(directory) / "reference.npz"), "r", os.O_RDONLY))
            self.assertEqual(len(audit.forbidden_attempts), 1)

    def test_write_outside_fresh_output_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            audit = release.AccessAudit(base / "run")
            audit.hook("open", (str(base / "run" / "new.json"), "w", os.O_WRONLY | os.O_CREAT))
            with self.assertRaisesRegex(RuntimeError, "outside fresh run"):
                audit.hook("open", (str(base / "old_evidence.json"), "w", os.O_WRONLY | os.O_CREAT))

    def test_changed_scientific_evidence_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            evidence = base / "science.json"
            evidence.write_bytes(b"original")
            inventory = {"science.json": release.sha(evidence)}
            evidence.write_bytes(b"changed")
            with patch.object(release, "ROOT", base):
                with self.assertRaisesRegex(RuntimeError, "PROTECTED_SCIENTIFIC_EVIDENCE_CHANGED"):
                    release.check_protection(inventory)


if __name__ == "__main__":
    unittest.main()
