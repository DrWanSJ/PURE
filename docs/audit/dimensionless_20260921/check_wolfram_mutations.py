"""Small fault-injection checks; all mutated sources stay in ignored scratch."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).resolve().parent
scratch = root / "results/runs/dimensionless_audit_20260921/mutations"
scratch.mkdir(parents=True, exist_ok=True)
path = "models/literature_reference/dimensionless/verify_wolfram_v2.wl"
fixed = (root/path).read_text(encoding="utf-8")
original = subprocess.check_output(["git", "show", "1aed082:"+path], cwd=root).decode("utf-8")


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


cases = [
    ("original_wrong_TL_stoichiometry", replace_once(original,
        "-vtx - vrs - 2 vtl + ven,", "-vtx - vrs - vtl + ven,"), 0, "T1 ALL PASS: False"),
    ("fixed_wrong_TL_stoichiometry", replace_once(fixed,
        "-vtx - vrs - 2 vtl + ven,", "-vtx - vrs - vtl + ven,"), 1, "AUDIT ALL PASS: False"),
    ("fixed_wrong_accounting_mappings", replace_once(fixed,
        "Dnt -> y11 nN cN, DTL -> y12 cL", "Dnt -> y1 nN cN, DTL -> y10 cL"), 1,
        "STATE MAPPING (12): False"),
    ("fixed_wrong_rhoT", replace_once(fixed,
        "rhoT -> (nN cN)/(nT cT)", "rhoT -> (nN cN)/(nA cA)"), 1,
        "AUDIT ALL PASS: False"),
    ("fixed_contaminated_global_context",
        'Global`y1 = 0; Global`rhoA = Global`rhoT; $Assumptions = False;\n' + fixed, 0,
        "AUDIT ALL PASS: True"),
]


def run_case(case):
    name, content, expected_exit, marker = case
    script = scratch/(name+".wl")
    script.write_text(content, encoding="utf-8")
    cmd = ["wolframscript", "-script", str(script)]
    proc = subprocess.run(cmd, capture_output=True, timeout=180)
    (evidence/(name+".stdout.txt")).write_bytes(proc.stdout)
    (evidence/(name+".stderr.txt")).write_bytes(proc.stderr)
    text = proc.stdout.decode("utf-8", errors="replace")
    result = {"case": name, "exit_code": proc.returncode, "expected_exit": expected_exit,
              "expected_marker": marker, "pass": proc.returncode == expected_exit and marker in text}
    print(json.dumps(result), flush=True)
    return result


with ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(run_case, cases))
(evidence/"mutation_results.json").write_text(json.dumps(results, indent=2)+"\n", encoding="utf-8")
assert all(row["pass"] for row in results), results
print("MUTATION / CONTEXT CHECKS: ALL PASS")
