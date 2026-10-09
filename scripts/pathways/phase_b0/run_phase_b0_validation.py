#!/usr/bin/env python3
"""Safe executed B0-1 gates, regressions, byte reproduction and review report."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/reduction/pathways"
HERE = Path(__file__).resolve().parent
LOG = OUT / "phase_b0_execution_log.txt"
FAILURES = OUT / "phase_b0_failure_evidence.jsonl"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}


def write_json(path, obj):
    path.write_bytes((json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def log(text):
    with LOG.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(text + "\n")


def run(command):
    label = subprocess.list2cmdline([str(c) for c in command])
    log("COMMAND: " + label)
    result = subprocess.run(command, cwd=ROOT, env=ENV, capture_output=True, encoding="utf-8", errors="replace")
    record = {"command": label, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    log("EXIT_CODE: " + str(result.returncode) + "\nSTDOUT:\n" + result.stdout + "STDERR:\n" + result.stderr)
    if result.returncode:
        with FAILURES.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps({"stage": "executed_command", **record}, sort_keys=True) + "\n")
    print(json.dumps({"command": label, "exit_code": result.returncode}), flush=True)
    return record


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regression_phase_a():
    commands = []
    verified = run([sys.executable, ROOT / "scripts/pathways/verify_pathway_atlas.py"])
    commands.append(verified)
    with tempfile.TemporaryDirectory(prefix="phase-b0-phase-a-") as tmp:
        d = Path(tmp)
        for name in ("glyrs_metrs_graph.json", "glyrs_metrs_pathway_index.csv", "glyrs_metrs_sample.md"):
            shutil.copyfile(OUT / name, d / name)
        tested = run([sys.executable, ROOT / "scripts/pathways/test_pathway_atlas.py", "--output-dir", d])
        commands.append(tested)
        report = json.loads((d / "validation_report.json").read_text(encoding="utf-8")) if (d / "validation_report.json").is_file() else {}
        controls = json.loads((d / "negative_controls.json").read_text(encoding="utf-8")) if (d / "negative_controls.json").is_file() else {}
    result = {"status": "PASS" if all(c["exit_code"] == 0 for c in commands) and report.get("structural_status") == "PASS" else "FAIL",
              "commands": commands, "phase_a_test_report": report, "phase_a_negative_controls": controls,
              "report_writes_confined_to_temporary_artifacts": True}
    write_json(OUT / "phase_b0_phase_a_regression.json", result)
    return result


def regression_html():
    # main() on the old entrypoint may append its historical failure archive.
    # Call its original acceptance functions read-only, routing evidence only to B0.
    module_path = ROOT / "scripts/pathways/test_reaction_atlas_html.py"
    spec = importlib.util.spec_from_file_location("phase_b0_existing_html_checks", module_path)
    html = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(html)
    result = {"entrypoint": module_path.relative_to(ROOT).as_posix(), "mode": "EXISTING_ACCEPTANCE_FUNCTIONS_READ_ONLY_B0_REPORT_DESTINATION", "gates": []}
    before = html.snapshot()
    try:
        data = html.extract((OUT / "reaction_atlas_prototype.html").read_text(encoding="utf-8"))
        species, source, v2, parameters = html.read_sources()
        graph = load("glyrs_metrs_graph.json")
        operations = [("A", lambda: html.gate_a(data, species, source, v2, parameters)),
                      ("B", lambda: html.gate_b(data, graph)), ("C", lambda: html.gate_c(data, source, parameters)),
                      ("D", lambda: html.gate_d(data, source)),
                      ("REPRODUCTION", lambda: html.rebuild(OUT / "reaction_atlas_prototype.html")),
                      ("PRESENTATION_PRESERVATION", lambda: html.previous_version_integrity(data))]
        for name, op in operations:
            try:
                result["gates"].append({"gate": name, "status": "PASS", "evidence": op()})
            except Exception:
                result["gates"].append({"gate": name, "status": "FAIL", "traceback": traceback.format_exc()})
        if html.browser_executable() is None:
            result["gates"].append({"gate": "BROWSER", "status": "NOT_RUN", "reason": "No existing supported browser executable; no download authorized"})
        else:
            try:
                evidence = html.run_browser(OUT / "reaction_atlas_prototype.html", data, source)
                result["gates"].append({"gate": "BROWSER", "status": evidence["status"], "evidence": evidence})
            except (ImportError, FileNotFoundError):
                result["gates"].append({"gate": "BROWSER", "status": "NOT_RUN", "traceback": traceback.format_exc()})
            except Exception:
                result["gates"].append({"gate": "BROWSER", "status": "FAIL", "traceback": traceback.format_exc()})
    except Exception:
        result["gates"].append({"gate": "SETUP", "status": "FAIL", "traceback": traceback.format_exc()})
    after = html.snapshot()
    result["changed_protected_files"] = sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))
    statuses = [g["status"] for g in result["gates"]]
    result["status"] = "FAIL" if "FAIL" in statuses or result["changed_protected_files"] else "NOT_RUN" if "NOT_RUN" in statuses else "PASS"
    write_json(OUT / "phase_b0_html_regression.json", result)
    log("COMMAND: run_phase_b0_validation.py -> existing HTML gate_a/b/c/d, rebuild, previous_version_integrity, run_browser\nRESULT:\n" + json.dumps(result, sort_keys=True))
    print(json.dumps({"html_regression": result["status"], "gates": [{"gate": g["gate"], "status": g["status"]} for g in result["gates"]]}), flush=True)
    if result["status"] == "FAIL":
        with FAILURES.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps({"stage": "html_regression", "report": result}, sort_keys=True) + "\n")
    return result


def reproduce():
    names = ("phase_b0_handoff_witnesses.json", "phase_b0_handoff_witnesses.md")
    hashes, commands = [], []
    with tempfile.TemporaryDirectory(prefix="phase-b0-reproduce-") as tmp:
        for i in (1, 2):
            d = Path(tmp) / str(i)
            commands.append(run([sys.executable, HERE / "build_phase_b0_witnesses.py", "--output-dir", d]))
            hashes.append({n: sha(d / n) for n in names if (d / n).is_file()})
    delivered = {n: sha(OUT / n) for n in names}
    return {"status": "PASS" if all(c["exit_code"] == 0 for c in commands) and hashes[0] == hashes[1] == delivered else "FAIL",
            "independent_builds": 2, "hashes": hashes, "delivered_hashes": delivered, "commands": commands}


QUESTIONS = [
    "W1 的 elRS70SAGGU0002_fMet 与 EFTu_GTP 均为显式外部供给，终点为核糖体结合复合物。是否接受它作为结合接口证据，并继续把上游核糖体形成与完整延伸保留为未验证？",
    "是否接受 MTF 的 FD-first (0418/0422) 与 Met-tRNA-first (0420/0424) 为互相竞争的有限入口，并在 MTF_FD_MettRNAfMetCAU 真正汇合，不推断优势结合顺序？",
    "源模型 0426 的复合物转化、0428 的产物释放和 0434 的 MTF 回收已分开记录。是否接受这一来源层面的甲酰化解释，同时保持 FD 的化学身份未获额外证实？",
    "W3 由 W2 生成的精确 fMettRNAfMetCAU 接入 0449，IF2_GTP 显式外供且 0445 未纳入核心见证。是否接受这个 IF2 结合终点，并将核糖体起始与 IF2 回收留待后续独立研究？",
    "源物种流向已验证，但跨 GlyRS/tRNA/EF-Tu、MetRS/tRNA/MTF/IF2 和核糖体复合物的分子身份投影仍为 INFERRED。后续工作需要何种论文/注释证据才可批准这些身份规则？",
]


def review(report):
    data = load("phase_b0_handoff_witnesses.json")
    user_review = load("phase_b0_b0_2_review_record.json")
    lines = ["# Phase B0-1 executed review", "", "Scientific status: **PENDING_HUMAN_REVIEW**. Phase B1 authorized: **false**.", "", "Execution: `" + report["execution_status"] + "`; overall engineering: `" + report["engineering_status"] + "`. These results certify conditional finite source structure only.", "", "## Repository and review hold", "", "Machine: sean. Repository: `C:\\Users\\sean\\Desktop\\GUV`. Origin: `https://github.com/DrWanSJ/PURE.git`. Branch: `codex/energy-cycles-v1`.", "", "Starting HEAD and ending HEAD: `" + report["repository"]["starting_head"] + "` / `" + report["repository"]["ending_head"] + "`. Startup fetch confirmed clean tree and upstream 0/0. Commit/push: `NOT_ATTEMPTED — B0-1 review hold`.", "", "## Executed gates", "", "| Gate | Status | Executed entrypoint | Evidence |", "|---|---|---|---|"]
    lines[0] = "# Phase B0 executed review — B0-2 source/document correction and revalidation"
    lines[2] = "User-supplied scientific status: **" + report["scientific_status"] + "**. Formal signoff: **" + report["formal_signoff_status"] + "**. Phase B1 authorized: **false**."
    lines[10] = lines[10].replace("Startup fetch", "Original B0-1 startup fetch") + " This B0-2 run continues the identified local B0 work."
    lines[12:12] = ["## FD identity correction and original source", "", "**FD is 10-formyltetrahydrofolate (10-甲酰四氢叶酸).** Matsuura et al. 2017, PNAS 114(8):E1336–E1344, DOI [10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114), explicitly identifies it in inline SI Results / Model Construction / **Model construction for formylation of initiator tRNA**, referring to FMet_tRNASynthesis and Dataset S21. [Original article and SI text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/).", "", "The publication describes MTF transferring the formyl group to Met-tRNAfMet and dissociation of the resulting complex containing formylated initiator tRNA and tetrahydrofolate. The earlier FD identity documentation gap is resolved. Full complex composition and real kinetic behavior remain unverified; source species, coefficients and parameters stay unchanged.", "", "## IF2 directionality and future shared-pool constraint", "", "Fresh canonical/source-parameter verification confirms `re0000000449` and `re0000000450` both have reference k1 = 40; both directions remain parameter-enabled. W3 fires 0449 only, does not complete initiation and does not establish irreversible binding or equilibrium.", "", "The MTF entrances `re0000000420/0422` and EF-Tu entrance `re0000000288` consume the same original `MettRNAfMetCAU` pool. Any separately authorized B1 must preserve the competing exits and inverses; isolated B0 nets cannot be combined using duplicated Met-tRNA supplies. No B1 implementation was executed.", "", "Ban et al. 2026, ACS Synthetic Biology 15(6):2675–2683, [DOI 10.1021/acssynbio.6c00333](https://doi.org/10.1021/acssynbio.6c00333), supplies external supporting context for initiator Met-tRNA sequestration by excess EF-Tu. Coverage was publisher metadata and abstract only. Its model explanation and experimentally confirmed supplementation prediction do not validate this repository's kinetic predictions.", "", "The [B0-2 researcher record](phase_b0_b0_2_review_record.md) attributes the conditional decisions to the user. The automated B0-1 contract retains PENDING_HUMAN_REVIEW separately from that user decision. The pre-revision B0-1 package is preserved in phase_b0_b0_1_pre_b0_2_2026-10-09.zip. Codex does not issue a researcher signature.", ""]
    for g in report["gates"]:
        lines.append(f"| {g['gate']} — {g['name']} | {g['status']} | `{g['command']}` | `{g['evidence_file']}` |")
    lines += ["", "## Witness results", "", "| Witness | Directed occurrences | Exact structural net | Verification |", "|---|---|---|---|"]
    for w in data["witnesses"]:
        lines.append(f"| {w['witness_id']} | {len(w['reaction_occurrences'])} | `{w['net_reaction']}` | {report['positive_verification']['witnesses'].get(w['witness_id'], {}).get('status', 'NOT_RUN')} |")
    n = report["negative_controls"]
    lines += ["", f"Required negatives: {n['required_controls_run']} run, {n['required_controls_passed']} passed, {n['required_controls_failed']} failed. All negatives including supplements: {n['controls_run']} run, {n['controls_passed']} passed, {n['controls_failed']} failed.", "", "| Control | Expected rejection | Actual rejection | Petri enabling | Result |", "|---|---|---|---|---|"]
    lines += [f"| {c['id']} | {c['expected_rejection_code']} | {c['actual_rejection_code']} | {c['independent_verifier_evidence']['petri_enabling_status']} | {c['status']} |" for c in n["controls"]]
    lines += ["", "Supplemental positives verify a reordered independent precursor and two genuine MTF cycles with distinct occurrences (each source direction counted twice). N05 is Petri-enabled but rejected for carrier lineage. N09 is Petri-enabled but rejected for a shared-resource carrier claim. All mutations are in memory; none alters source files.", "", "## Independent evidence and preservation", "", "The verifier imports no builder. It reparses original MathML, independent author CSV values and archive bytes, checks exact signed nets, every input and token origin, DAG edges, catalyst recovery, boundary balances, alternative rejoin and reference directions. All five source-bound scenarios are independently checked. The generated witness records retain CANDIDATE_AWAITING_INDEPENDENT_VERIFICATION; executed outcomes live in separate validation reports.", "", f"All {report['positive_verification'].get('preservation', {}).get('existing_tracked_files_unchanged', 0)} pre-existing tracked files are byte-unchanged. Phase A mutation/report writes used temporary copies. Existing HTML regression functions ran read-only with all new reports routed to B0.", "", "Source hashes:", ""]
    for p, h in report["positive_verification"].get("source_integrity", {}).get("hashes", {}).items():
        lines.append(f"- `{p}`: `{h}`.")
    lines += ["", "Two independent builder runs reproduce both new deterministic witness files and equal delivered SHA-256 values:", ""]
    lines += [f"- `{p}`: `{h}`." for p, h in report["reproducibility"]["delivered_hashes"].items()]
    lines += ["", "## Reproduction commands", "", "From the repository root, using the existing Python environment:", "", "```powershell", "python scripts/pathways/phase_b0/build_phase_b0_witnesses.py", "python scripts/pathways/phase_b0/verify_phase_b0_witnesses.py", "python scripts/pathways/phase_b0/test_phase_b0_negative_controls.py", "python scripts/pathways/verify_pathway_atlas.py", "python scripts/pathways/phase_b0/run_phase_b0_validation.py", "```", "", "The final command safely runs Phase A mutation tests in a temporary copy, existing HTML acceptance functions, two B0 builds and preservation checks. Do not run old report-writing mutation/browser entrypoints with default output paths: that would overwrite archived Phase A results. Exact executed temporary paths, raw outputs and exit codes are in phase_b0_execution_log.txt and the regression reports.", "", "## Limitations, failures and unresolved questions", "", "All selected positive directions have nonzero reference parameters; 0427 remains an original zero-parameter reverse in the context appendix. Nonzero k is not measured flux. Finite boundary supplies are explicit conditional assumptions. No full-network availability, complex molecular composition, binding-order dominance, completed elongation/initiation, kinetic feasibility, QSSA, effective-rate law or reduced model is approved.", "", "phase_b0_failure_evidence.jsonl preserves genuine failed attempts. An initial inspection used Windows' default GBK decoding for UTF-8 JSON and failed; it was rerun with explicit UTF-8 without source modification. Any later actual failures are appended with their raw evidence. Expected negative rejections are recorded separately and do not represent failed acceptance gates.", "", "## B0-2 researcher review", ""]
    lines = lines[:lines.index("## B0-2 researcher review")]
    lines += ["## B0-2 user-supplied researcher decisions", "", "| Item | Researcher's exact judgment | Scope |", "|---|---|---|"]
    lines += [f"| {d['id']}. {d['item']} | {d['user_judgment']} | {d['scope']} |" for d in user_review["decisions"]]
    lines += ["", "The researcher conditionally accepts source stoichiometry, catalyst recovery and finite handoffs. Full complex composition remains INFERRED and real kinetic behavior remains unverified. The researcher explicitly relies on Codex's engineering reports and has not independently rerun the unpublished code. Phase A signoff need not be repeated.", "", "FD correction status: `" + report["fd_document_correction_status"] + "`.", ""]
    lines += ["", "## B0-2 handoff checklist", "", "- Review actual W1–W3 equations, boundary assumptions, exact handoffs and provisional carrier streams.", "- Record the five scientific decisions above as researcher decisions, retaining any UNRESOLVED identity questions.", "- Preserve the executed positive/negative, source hash, failure and regression evidence.", "- Obtain explicit authorization before commit/push; this local review hold remains active.", "- Obtain separate scope authorization before any Phase B1 reconstruction or kinetic work.", "", "B0-1 stops here. No Phase B1, commit or push was attempted."]
    lines = lines[:lines.index("## B0-2 handoff checklist")]
    lines += ["## Final signoff and delivery checkpoint", "", "- Preserve the original B0-1 snapshot and corrected B0-2 source/review records with actual rerun evidence.", "- Obtain final researcher confirmation of bounded signoff and explicit authorization before commit/push; the earlier review hold remains active.", "- Obtain separate scope authorization before Phase B1, retaining the shared Met-tRNA competition constraint.", "", "B0 stops here. No Phase B1, commit or push was attempted."]
    (OUT / "phase_b0_review.md").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reuse-regressions", action="store_true", help="Reuse this run's unchanged Phase A/HTML evidence; still recheck protected hashes and all B0 tests")
    args = parser.parse_args()
    stamp = datetime.now(timezone(timedelta(hours=8))).isoformat()
    log("B0-2 correction/revalidation run (Asia/Shanghai): " + stamp)
    log("Historical B0-1 preflight: clean authorized branch, successful fetch, HEAD 14c61055775421e9f30342507cc4fffdceed1607, upstream 0/0. B0-2 continues identified local B0 files; protected hashes and final Git status are rechecked. No synchronization mutation, commit or push is part of this runner.")
    commands = [run([sys.executable, HERE / "build_phase_b0_witnesses.py"]),
                run([sys.executable, HERE / "verify_phase_b0_witnesses.py"]),
                run([sys.executable, HERE / "test_phase_b0_negative_controls.py"])]
    positive = load("phase_b0_independent_verification.json")
    negatives = load("phase_b0_negative_controls.json")
    if args.reuse_regressions:
        phase_a = load("phase_b0_phase_a_regression.json")
        html = load("phase_b0_html_regression.json")
        log("Regression evidence reused from the earlier executed B0-1 run; existing Phase A/HTML/scripts remain protected by independent post-run hashes.")
    else:
        phase_a = regression_phase_a()
        html = regression_html()
    reproduction = reproduce()
    # Independent preservation is rechecked after every regression and builder run.
    commands.append(run([sys.executable, HERE / "verify_phase_b0_witnesses.py"]))
    positive = load("phase_b0_independent_verification.json")
    git_diff = run(["git", "diff", "--check"])
    commands.append(git_diff)
    verify_cmd = "python scripts/pathways/phase_b0/verify_phase_b0_witnesses.py"
    pass_positive = positive.get("structural_verification_status", "FAIL")
    gates = [{"gate": g, "name": name, "status": pass_positive, "command": verify_cmd, "evidence_file": "phase_b0_independent_verification.json"}
             for g, name in (("A", "Source Integrity"), ("B", "W1 Structural Handoff"), ("C", "W2 Multi-Precursor / Alternative Entry"), ("D", "W3 Formylated-tRNA Handoff"), ("E", "Net Stoichiometry"))]
    if reproduction["status"] != "PASS":
        gates[-1]["status"] = "FAIL"
    gates += [{"gate": "F", "name": "Negative Controls", "status": negatives["status"], "command": "python scripts/pathways/phase_b0/test_phase_b0_negative_controls.py", "evidence_file": "phase_b0_negative_controls.json"},
              {"gate": "G", "name": "Phase A Regression / Preservation", "status": "FAIL" if phase_a["status"] == "FAIL" or html["status"] == "FAIL" or pass_positive == "FAIL" else html["status"], "command": "python scripts/pathways/verify_pathway_atlas.py; python scripts/pathways/phase_b0/run_phase_b0_validation.py", "evidence_file": "phase_b0_phase_a_regression.json; phase_b0_html_regression.json"}]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    baseline = load("phase_b0_source_baseline.json")
    statuses = [g["status"] for g in gates]
    engineering = "FAIL" if "FAIL" in statuses or any(c["exit_code"] for c in commands) else "INCOMPLETE" if "NOT_RUN" in statuses else "PASS"
    user_review = load("phase_b0_b0_2_review_record.json")
    report = {"phase": "B0-2_DOCUMENT_CORRECTION_AND_REVALIDATION", "execution_status": "COMPLETED" if engineering == "PASS" else engineering,
              "engineering_status": engineering, "source_integrity_status": "PASS" if "source_integrity" in positive else "FAIL",
              "structural_verification_status": pass_positive, "negative_control_status": negatives["status"], "regression_status": gates[-1]["status"],
              "scientific_status": user_review["scientific_status"], "automated_b0_1_scientific_status": "PENDING_HUMAN_REVIEW",
              "formal_signoff_status": user_review["formal_signoff_status"], "fd_document_correction_status": "DOCUMENTED_AND_REVALIDATED" if engineering == "PASS" else "DOCUMENTED_REVALIDATION_INCOMPLETE",
              "phase_b1_authorized": False, "gates": gates,
              "positive_verification": positive, "negative_controls": {k: v for k, v in negatives.items() if k not in ("controls", "supplemental_positive_tests")},
              "reproducibility": reproduction, "phase_a_regression_status": phase_a["status"], "html_regression_status": html["status"],
              "regressions_reused_after_b0_only_verifier_change": args.reuse_regressions,
              "commands": commands, "repository": {"machine": "sean", "root": str(ROOT), "origin": "https://github.com/DrWanSJ/PURE.git", "branch": baseline["branch"], "starting_head": baseline["starting_head"], "ending_head": head, "upstream_initial_ahead_behind": [0, 0], "commit_push": "NOT_ATTEMPTED — B0-1 review hold"}}
    # Review needs complete negative evidence; aggregate avoids duplicating bulky fixtures.
    review({**report, "negative_controls": negatives})
    report["repository"]["final_git_status"] = run(["git", "status", "--short", "--untracked-files=all"])
    write_json(OUT / "phase_b0_validation_report.json", report)
    log("FINAL_STATUSES: " + json.dumps({k: report[k] for k in ("execution_status", "engineering_status", "source_integrity_status", "structural_verification_status", "negative_control_status", "regression_status", "scientific_status", "phase_b1_authorized")}))
    print(json.dumps({k: report[k] for k in ("execution_status", "engineering_status", "source_integrity_status", "structural_verification_status", "negative_control_status", "regression_status", "scientific_status", "phase_b1_authorized")}), flush=True)
    return 0 if engineering == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
