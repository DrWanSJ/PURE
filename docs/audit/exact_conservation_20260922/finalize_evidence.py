"""Extract machine-readable results from native stdout; verify original sources.

Run from any directory with Python's standard library. Never runs MATLAB or
changes acceptance criteria. Refuses to finalize incomplete or failed evidence.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    raw = (AUDIT / "matlab_stdout.txt").read_bytes()
    for stem in ("matlab_stdout", "matlab_checkcode_stdout"):
        path = AUDIT / (stem + ".txt")
        if path.exists():
            native = path.read_bytes()
            decoded = native.decode("gb18030")
            assert decoded.encode("gb18030") == native
            (AUDIT / (stem + ".utf8.txt")).write_bytes(decoded.encode("utf-8"))
    # MATLAB's Windows console table glyphs can use the system codepage;
    # all structured markers and their JSON payloads are ASCII.
    stdout = raw.decode("ascii", errors="replace")

    def records(marker):
        return [json.loads(match) for match in re.findall(re.escape(marker) + r" (.+)", stdout)]

    cases = records("EXACT_REDUCTION_CASE")
    physicality = records("EXACT_REDUCTION_PHYSICALITY")
    summary, = records("EXACT_REDUCTION_TEST_SUMMARY")
    structure, = records("EXACT_REDUCTION_STRUCTURE")
    initial, = records("EXACT_REDUCTION_INITIAL")
    derivative = re.search(r"EXACT_REDUCTION_DERIVATIVE max_abs=(\S+) points=(\d+)", stdout)
    assert (AUDIT / "matlab_exitcode.txt").read_text(encoding="utf-8-sig").strip() == "0"
    assert not (AUDIT / "matlab_stderr.txt").read_bytes()
    assert len(cases) == len(physicality) == 3 and derivative
    assert [case["DNA_uM"] for case in cases] == [0.00034, 0.0017, 0.0068]
    assert summary["allPassed"] and all(case["trajectory_pass"] for case in cases)
    assert all(s["failed"] == s["incomplete"] == 0 for s in summary["suites"])
    assert all(case["output_points"] == 1441 for case in cases)
    for case in cases:
        for quantity in ("states", "rates", "mRNA", "protein"):
            assert case[quantity]["max_normalized"] <= 1e-6
    preregistration = read_json(AUDIT / "preregistration.json")
    assert sha(AUDIT / "acceptance_criteria.json") == preregistration["criteria_sha256"]
    for item in preregistration["implementation"]:
        assert sha(Path(item["path"])) == item["sha256"], item["path"]
    before = read_json(AUDIT / "source_inventory_before.json")
    missing = [x["path"] for x in before["files"] if not (ROOT / x["path"]).is_file()]
    changed = [x["path"] for x in before["files"]
               if (ROOT / x["path"]).is_file() and sha(ROOT / x["path"]) != x["sha256"]]
    integrity = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
                 "source_commit": before["head"], "original_tracked_files_checked": len(before["files"]),
                 "changed_original_files": changed, "missing_original_files": missing,
                 "all_original_tracked_files_byte_identical": not changed and not missing,
                 "preregistration_and_tested_implementation_unchanged": True}
    write_json(AUDIT / "integrity_after.json", integrity)
    assert not changed and not missing, "Original files changed; inspect integrity_after.json."
    result = {"scope": "D6 exact conservation reduction, not complete D6 or experimental validation",
              "source_commit": before["head"], "stdout_sha256": sha(AUDIT / "matlab_stdout.txt"),
              "criteria_sha256": preregistration["criteria_sha256"], "summary": summary,
              "initial_reconstruction": initial, "structure": structure,
              "derivative_max_abs_uM_per_s": float(derivative[1]),
              "derivative_points": int(derivative[2]), "cases": cases, "physicality": physicality}
    write_json(AUDIT / "validation_results.json", result)
    print(json.dumps({"allPassed": True, "original_files_unchanged": len(before["files"]),
                      "suites": summary["suites"]}, indent=2))


if __name__ == "__main__":
    main()
