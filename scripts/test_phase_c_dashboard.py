#!/usr/bin/env python3
"""Validate the upgraded existing offline atlas against frozen scientific files.

No scientific output is regenerated. The only output is this release's dashboard
validation report, in results/reduction/phase_c_release_v1/dashboard/.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit

import numpy as np
from build_phase_c_dashboard import ROOT, DATA_PATH, build_data, digest, serialize, SCENARIOS, FINAL

HTML = ROOT / "docs/visualization/reduction_reasoning_atlas.html"
REPORT = ROOT / "results/reduction/phase_c_release_v1/dashboard/static_validation.json"
LEGACY_HTML_REF = "7a95c29b6bf80b567863cc70a631859016144924"


class Inventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.external_resources = [], [], []
        self.in_script, self.scripts = False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag in ["script", "link", "img", "iframe"] and (a.get("src") or a.get("href")):
            self.external_resources.append(a.get("src") or a.get("href"))
        if tag == "script":
            self.in_script = True
            self.scripts.append("")

    def handle_data(self, data):
        if self.in_script:
            self.scripts[-1] += data

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False


def payload(text, name):
    start = text.index("const " + name + " = ") + len("const " + name + " = ")
    return json.JSONDecoder().raw_decode(text[start:])[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--allow-pending-package-links", action="store_true", help="Development only; report remains INCOMPLETE")
    args = ap.parse_args()
    text = HTML.read_text(encoding="utf-8")
    d = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    inventory = Inventory()
    inventory.feed(text)
    checks = []

    def checked(name, evidence):
        checks.append({"check": name, "status": "PASS", "evidence": evidence})

    assert DATA_PATH.read_bytes() == serialize(build_data()).encode("utf-8"), "Stale presentation contract"
    assert payload(text, "PHASE_C") == d, "Embedded and portable data contracts differ"
    checked("freshness_and_embedded_contract", {"input_files": len(d["inputs"]), "data_sha256": digest(DATA_PATH)})
    assert len(inventory.ids) == len(set(inventory.ids)), "Duplicate HTML IDs"
    assert all(i in inventory.ids for i in ["s1", "s2", "s3", "s4", "s5", "spSearch", "rxSearch", "scopeSeg", "layerSeg", "drawer", "phase-c", "phase-plot", "phase-inputs"])
    historical = subprocess.check_output(["git", "show", LEGACY_HTML_REF + ":docs/visualization/reduction_reasoning_atlas.html"], cwd=ROOT).decode("utf-8")
    old = Inventory()
    old.feed(historical)
    assert set(old.ids) <= set(inventory.ids), "An existing filter, diagram or section was removed"
    old_data, new_data = payload(historical, "DATA"), payload(text, "DATA")
    for key in old_data:
        if key == "provenance":
            for field in old_data[key]:
                if field not in ["built_at", "source_ref"]:
                    assert new_data[key][field] == old_data[key][field], (key, field)
        else:
            assert new_data[key] == old_data[key], key
    checked("legacy_preserved", {"legacy_html_ref": LEGACY_HTML_REF, "old_ids": len(old.ids), "historical_scientific_payload": "IDENTICAL_VALUES_EXCEPT_BUILD_TIMESTAMP_AND_REF_ALIAS_SAME_COMMIT"})

    assert not inventory.external_resources, inventory.external_resources
    assert not re.search(r"\b(fetch|XMLHttpRequest|WebSocket)\s*\(", "\n".join(inventory.scripts))
    assert "@import" not in text
    assert "SOURCE_NUMERICAL_TIME_UNIT_NOT_INTERPRETED_AS_SECONDS" in text
    assert "历史快照" in text and "初始层（默认）" in text
    checked("offline_structure_and_scope", "No external assets, fetch, CDN, duplicate IDs; legacy scope explicit and early window default")

    model_map = {m["model"]: m for m in d["models"]}
    assert {m: v["independent_dimension"] for m, v in model_map.items()} == {
        "R0": 241, "R1": 214, "R2": 175, "R3_CHAIN1": 174,
        "R3_CHAIN12": 173, "R3_RECYCLE": 173, FINAL: 171}
    assert len(d["counter_names"]) == 20 and all(m["counter_dimension"] == 20 for m in d["models"])
    assert model_map[FINAL]["independent_dimension"] + len(d["counter_names"]) == 191
    assert all(m["speedup"] < 1 for m in d["models"] if m["model"] != "R0")
    assert d["plotted_reference"] == "R0_TIGHT"
    assert d["quotient"]["microstates"] == 7 and d["quotient"]["observables"] == 5
    assert d["reactions"]["re0000000414"]["products"]["PO4"] == "2"
    assert d["reactions"]["re0000000798"]["author_k_exact"] == "1/2"
    assert d["reactions"]["re0000000813"]["author_k_exact"] == "3/2"
    checked("scientific_dimensions_and_boundaries", "Distinct 173 branches, 171+20=191, 7-to-5 quotient, RF 0.5/1.5, 2 PO4 and no speedup")

    curve_checks = 0
    for sc in SCENARIOS:
        for model in ["R0", FINAL]:
            tag = sc + "__" + ("R0_TIGHT" if model == "R0" else model)
            p = ROOT / "results/reduction/rapid_v1/trajectories" / tag
            meta = json.loads(p.with_suffix(".json").read_text())
            with np.load(p.with_suffix(".npz")) as z:
                np.testing.assert_array_equal(d["grid"], z["t"])
                for label in ["Pept0003", "ATP", "GTP", "GDP", "PO4", "PPi", "RS30S", "RS50S", "EFTu", "EFG"]:
                    np.testing.assert_array_equal(d["trajectories"][sc][model][d["trajectory_labels"].index(label)], z["X"][meta["source_species_order"].index(label)])
                    curve_checks += 1
                for label in d["counter_names"]:
                    np.testing.assert_array_equal(d["trajectories"][sc][model][d["trajectory_labels"].index(label)], z["counters"][meta["counter_names"].index(label)])
                    curve_checks += 1
        for row in d["comparisons"][sc][FINAL]["comparison"]["windows"]:
            assert row["range"] in d["config"]["windows"]
    checked("saved_trajectory_identity", {"direct_series_compared": curve_checks, "samples_per_series": len(d["grid"]), "scenarios": SCENARIOS})

    source_links = ["../../" + row["path"] for row in d["inputs"]]
    js = (ROOT / "scripts/phase_c_dashboard.js").read_text(encoding="utf-8")
    dynamic_paths = set(re.findall(r"['\"]((?:docs|results|scripts)/[^'\"]+)['\"]", js))
    all_links = set(inventory.links + source_links + ["../../" + p for p in dynamic_paths])
    missing = []
    for href in all_links:
        url = urlsplit(href)
        if url.scheme or href.startswith("//"):
            continue  # Optional remote citation hyperlinks are not runtime dependencies.
        if not url.path:
            assert not url.fragment or unquote(url.fragment) in inventory.ids, href
        elif not (HTML.parent / unquote(url.path)).resolve().exists():
            missing.append(href)
    if missing and not args.allow_pending_package_links:
        raise AssertionError("Unresolved dashboard links: " + str(missing))
    checks.append({"check": "local_links", "status": "INCOMPLETE" if missing else "PASS", "checked": len(all_links), "missing": missing})

    node = shutil.which("node")
    if node:
        for script in inventory.scripts:
            with tempfile.NamedTemporaryFile(suffix=".js", mode="w", encoding="utf-8", delete=False) as f:
                f.write(script)
                name = f.name
            try:
                subprocess.run([node, "--check", name], check=True, capture_output=True, text=True)
            finally:
                Path(name).unlink()  # Only this test's exact temporary file.
        checked("javascript_syntax", "node --check: all embedded JavaScript")
    else:
        checks.append({"check": "javascript_syntax", "status": "UNAVAILABLE"})
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report = {"status": "PASS" if not missing else "INCOMPLETE", "html": HTML.relative_to(ROOT).as_posix(), "html_sha256": digest(HTML),
              "checks": checks, "browser_visual_verification": "SEPARATE_REPORT_REQUIRED", "fresh_ODE_execution": False}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": len(checks), "report": REPORT.relative_to(ROOT).as_posix(), "missing": missing}, ensure_ascii=False))


if __name__ == "__main__":
    main()
