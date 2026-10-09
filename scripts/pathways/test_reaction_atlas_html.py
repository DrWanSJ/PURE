#!/usr/bin/env python3
"""Independent source, algebra, preservation and real file:// browser gates.

The HTML builder is never imported. Canonical SBML, reviewed annotations and
archived author parameters are parsed afresh. Phase A tests run on temporary
copies, so their report-writing behavior cannot overwrite published evidence.
Playwright uses an existing system browser; it never installs a browser.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from functools import reduce
import hashlib
import io
import json
import operator
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
import xml.etree.ElementTree as ET
import zipfile
import csv

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/reduction/pathways"
SOURCE = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
V2 = ROOT / "docs/reduction/reaction_level_annotation_v2.csv"
AUTHOR = ROOT / "references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip"
PRESENTATION_BASELINE = "f2cd0aacf345f029c907b0690d0fabb9e30f8b66"
SB = "{http://www.sbml.org/sbml/level2/version4}"
MM = "{http://www.w3.org/1998/Math/MathML}"
NEW_NAMES = {"reaction_atlas_prototype.html", "reaction_atlas_ui_review.md",
             "reaction_atlas_html_test_report.json", "reaction_atlas_html_failures.jsonl",
             "build_reaction_atlas_html.py", "test_reaction_atlas_html.py"}


def require(condition, explanation):
    if not condition:
        raise AssertionError(explanation)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def math_number(node):
    """Separate constant-MathML implementation, with no default-to-one rule."""
    tag = node.tag.split("}")[-1]
    if tag == "math":
        require(len(node) == 1, "One constant expression required")
        return math_number(node[0])
    if tag == "cn":
        number = Fraction((node.text or "").strip())
        if node.get("type") in {"rational", "e-notation"}:
            require(len(node) == 1 and node[0].tag == MM + "sep", "Invalid cn separator")
            tail = (node[0].tail or "").strip()
            return number / Fraction(tail) if node.get("type") == "rational" else number * Fraction(10) ** int(tail)
        require(not len(node), "Unexpected constant child")
        return number
    if tag == "apply":
        op = node[0].tag.split("}")[-1]
        args = [math_number(child) for child in list(node)[1:]]
        if op == "plus":
            return sum(args, Fraction())
        if op == "times":
            return reduce(operator.mul, args, Fraction(1))
        if op == "minus" and len(args) == 1:
            return -args[0]
        if op == "minus" and len(args) == 2:
            return args[0] - args[1]
        if op == "divide" and len(args) == 2:
            return args[0] / args[1]
        if op == "power" and len(args) == 2 and args[1].denominator == 1:
            return args[0] ** int(args[1])
    raise AssertionError("Unsupported nonconstant MathML: " + tag)


def read_sources():
    model = ET.parse(SOURCE).getroot().find(SB + "model")
    species = {s.attrib["id"]: s.get("name", s.attrib["id"]) for s in model.findall(SB + "listOfSpecies/" + SB + "species")}
    source = {}
    for r in model.findall(SB + "listOfReactions/" + SB + "reaction"):
        rid = r.attrib["id"]
        require(rid not in source, "Duplicate canonical ID " + rid)
        entry = {}
        for side, name in (("reactants", "Reactants"), ("products", "Products")):
            participants = defaultdict(Fraction)
            for ref in r.findall(SB + "listOf" + name + "/" + SB + "speciesReference"):
                math = ref.find(SB + "stoichiometryMath/" + MM + "math")
                value = math_number(math) if math is not None else Fraction(ref.get("stoichiometry", "1"))
                require(value > 0, "Nonpositive source coefficient " + rid)
                participants[ref.attrib["species"]] += value
            entry[side] = dict(participants)
        entry["modifiers"] = tuple(sorted(ref.attrib["species"] for ref in r.findall(SB + "listOfModifiers/" + SB + "modifierSpeciesReference")))
        source[rid] = entry
    v2 = {r["reaction_id"]: r for r in rows(V2)}
    with zipfile.ZipFile(AUTHOR) as archive:
        names = [n for n in archive.namelist() if n.endswith("fMGG_synthesis_parameters.csv")]
        require(len(names) == 1, "Unique author CSV required")
        content = archive.read(names[0]).decode("utf-8-sig").replace("\r\r\n", "\n").replace("\r\n", "\n")
        author = {r["Name"]: Fraction(r["Value"]) for r in csv.DictReader(io.StringIO(content))}
    parameters = {rid: author[v2[rid]["official_parameter_id"]] for rid in source}
    for rid in source:
        require(parameters[rid] == Fraction(v2[rid]["official_parameter_value"]), "Parameter provenance mismatch " + rid)
    return species, source, v2, parameters


def exact(side):
    require(all(isinstance(v, str) for v in side.values()), "Exact coefficient strings required")
    return {s: Fraction(v) for s, v in side.items()}


def parse_equation(equation):
    require(equation.count(" -> ") == 1, "A directed source equation is required")
    sides = []
    for text in equation.split(" -> "):
        side = defaultdict(Fraction)
        if text not in {"∅", "0", ""}:
            for term in text.split(" + "):
                pieces = term.split()
                require(len(pieces) in {1, 2}, "Unrecognized coefficient term " + term)
                side[pieces[-1]] += Fraction(pieces[0]) if len(pieces) == 2 else 1
        sides.append(dict(side))
    return sides


def net(ids, source):
    # A Counter exposes actual occurrence multiplicities independently of JS.
    result = defaultdict(Fraction)
    for rid, multiplicity in Counter(ids).items():
        for s in set(source[rid]["reactants"]) | set(source[rid]["products"]):
            result[s] += multiplicity * (source[rid]["products"].get(s, 0) - source[rid]["reactants"].get(s, 0))
    return {s: str(v) for s, v in sorted(result.items()) if v}


def cycle(path, vector, carriers):
    return bool(path["target_product"] and "PRODUCTIVE_PATH" in path["types"] and
                path["start"] == path["end"] == path["enzyme"] and
                not (set(vector) & carriers) and Fraction(vector.get(path["target_product"], "0")) > 0)


def snapshot():
    completed = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
    names = completed.stdout.decode("utf-8").split("\0")
    return {n: digest(ROOT / n) for n in names if n and (ROOT / n).is_file() and
            Path(n).name not in NEW_NAMES and "scripts/pathways/reaction_atlas_ui/" not in n}


def extract(html):
    match = re.search(r'<script id="atlas-data" type="application/json">(.*?)</script>', html, re.S)
    require(match is not None, "Offline source payload missing")
    return json.loads(match.group(1))


def previous_version_integrity(data):
    """Compare the entire scientific payload with the committed pre-UI version."""
    original = subprocess.check_output(["git", "show", PRESENTATION_BASELINE +
        ":docs/reduction/pathways/reaction_atlas_prototype.html"], cwd=ROOT).decode("utf-8")
    old = extract(original)
    require(data == old, "UI changes must leave the full embedded scientific payload unchanged")
    return {"status": "PASS", "baseline_commit": PRESENTATION_BASELINE,
            "entire_embedded_scientific_payload_identical": True,
            "path_order_and_nets_unchanged": 20,
            "directed_path_step_occurrences": sum(len(p["reaction_ids"]) for p in old["paths"].values()),
            "phase_a_reactions": len(old["phase_a_ids"]),
            "return_witnesses": sum(len(m["return_loops"]) for m in old["modules"].values())}


def gate_a(data, species, source, v2, parameters):
    require(len(species) == 241 and len(source) == 968, "Canonical inventory")
    require(set(data["species"]) == set(species), "241 exact species IDs")
    require({s: d["name"] for s, d in data["species"].items()} == species, "Original species names")
    require(set(data["reactions"]) == set(source), "968 unique source IDs")
    contexts = set()
    nonunit = []
    disabled = []
    signatures = defaultdict(list)
    for rid, r in source.items():
        signatures[(tuple(sorted(r["reactants"].items())), tuple(sorted(r["products"].items())), r["modifiers"])].append(rid)
    for rid, r in source.items():
        ui = data["reactions"][rid]
        for side in ("reactants", "products"):
            require(exact(ui[side]) == r[side], f"Exact {rid} {side}")
            nonunit.extend([{"rid": rid, "side": side, "species": s, "coefficient": str(v)} for s, v in r[side].items() if v != 1])
        require(parse_equation(ui["equation"]) == [r["reactants"], r["products"]], "Displayed source equation " + rid)
        labels = set(filter(None, v2[rid]["level_c_functional_contexts"].split(";")))
        require(set(ui["level_c"]) == labels, "Reviewed multiple classification " + rid)
        require(ui["family"] == v2[rid]["reaction_family_id"], "Reviewed family " + rid)
        require(ui["mechanism"] == v2[rid]["mechanistic_reaction_type"], "Reviewed mechanism " + rid)
        contexts |= labels
        activity = "REFERENCE_DISABLED" if parameters[rid] == 0 else "NONZERO_PARAMETER"
        require(ui["reference_activity"] == activity, "True directional zero parameter " + rid)
        require(Fraction(ui["reference_parameter"]) == parameters[rid], "Original parameter value " + rid)
        require(ui["reference_pair_activity"] == v2[rid]["reference_activity"], "Original pair activity " + rid)
        reversed_ids = signatures[(tuple(sorted(r["products"].items())), tuple(sorted(r["reactants"].items())), r["modifiers"])]
        require(len(reversed_ids) <= 1 and ui["reverse"] == (reversed_ids[0] if reversed_ids else None), "Exact reverse " + rid)
        if activity == "REFERENCE_DISABLED":
            disabled.append(rid)
    require(len(contexts) == 23 and set(data["level_c_contexts"]) == contexts, "23 contexts")
    require(data["reactions"]["re0000000414"]["products"]["PO4"] == "2", "0414 2 PO4")
    flat = [c for g in data["groups"] for c in g["contexts"]]
    require(len(flat) == 23 and {c["id"] for c in flat} == contexts, "Hierarchy preserves 23 contexts")
    for c in flat:
        expected = {rid for rid, r in data["reactions"].items() if c["id"] in r["level_c"]}
        require(set(c["reaction_ids"]) == expected, "Functional set " + c["id"])
        for s in c["substeps"]:
            if c["id"] != "RS_binding":
                require(s["mapping_status"] == "SUBSTEP_MAPPING_NOT_VALIDATED" and set(s["reaction_ids"]) == expected,
                        "Unreviewed subprocess cannot invent a subdivision")
    for record in data["metadata"]["provenance"]:
        require(record["sha256"] == digest(ROOT / record["path"]), "Current source fingerprint " + record["path"])
    require({r["source_sbml_sha256"] for r in v2.values()} == {digest(SOURCE)}, "Reviewed source fingerprint")
    return {"species": 241, "unique_reactions": 968, "contexts": 23,
            "equations_checked": 968, "multi_label_reactions": sum(len(r["level_c"]) > 1 for r in data["reactions"].values()),
            "directional_zero_parameters": len(disabled), "nonunit_coefficients": nonunit,
            "canonical_sbml_sha256": digest(SOURCE), "reviewed_v2_sha256": digest(V2), "author_archive_sha256": digest(AUTHOR)}


def gate_b(data, graph):
    scoped = set(graph["coverage"]["phase_a_reaction_ids"])
    require(len(scoped) == 134 and set(data["phase_a_ids"]) == scoped, "Phase A 134")
    require(set(data["noncarrier_ids"]) == set(graph["noncarrier_reactions"]), "Free channels preserved")
    expected_paths = {p["id"]: p for m in graph["modules"].values() for p in m["paths"]}
    require(len(expected_paths) == 20 and set(expected_paths) == set(data["paths"]), "20 existing paths")
    for pid, p in expected_paths.items():
        ui = data["paths"][pid]
        for key in ("id", "title", "reaction_ids", "states", "start", "end", "types", "target_product", "reference_feasible", "rejoins", "shared_continuations", "evidence_status", "scientific_status"):
            require(ui[key] == p[key], f"Phase A {pid} {key} unchanged")
        require(set(ui["reaction_ids"]) <= scoped, "No foreign pathway additions")
    for e, m in graph["modules"].items():
        require(data["modules"][e]["return_loops"] == m["return_loops"], "Finite loop witnesses preserved")
        require(data["modules"][e]["sccs"] == m["sccs"], "Cyclic SCC evidence preserved")
        require(data["modules"][e]["branches"] == {b["state"]: b["outgoing_reaction_ids"] for b in m["branches"]}, "All competition edges preserved")
        require(data["modules"][e]["rejoins"] == {b["state"]: b["incoming_reaction_ids"] for b in m["rejoins"]}, "All convergence edges preserved")
        for t in m["transitions"]:
            for key in ("carrier_before", "carrier_after", "other_reactants", "other_products", "tracked_carriers", "types"):
                require(data["transitions"][t["reaction_id"]][key] == t[key], "Source transition projection preserved")
    require(data["boundary_links"] == graph["boundary_links"], "Foreign boundary incidence preserved")
    require(len(set(data["reactions"]) - scoped) == data["metadata"]["remaining_pathways"] == 834, "834 not reconstructed")
    for name, value in data["metadata"]["phase_a_inputs"].items():
        require(value == digest(OUT / name), "Phase A input hash unchanged " + name)
    # Ensure all three source-derived binding topic counts come from source.
    binding = next(c for g in data["groups"] for c in g["contexts"] if c["id"] == "RS_binding")
    counts = {}
    for i, s in enumerate(binding["substeps"][:3]):
        expected = set()
        for e, aa, trna in (("GlyRS", "Gly", "tRNAGlyGCC"), ("MetRS", "Met", "tRNAfMetCAU")):
            carriers = set(data["modules"][e]["carrier_states"])
            ligand = (aa, "ATP", trna)[i]
            members = {rid for rid in binding["reaction_ids"] if
                       set(data["reactions"][rid]["reactants"]) & carriers and
                       exact({k: v for k, v in data["reactions"][rid]["reactants"].items() if k not in carriers}) == {ligand: Fraction(1)} and
                       not set(data["reactions"][rid]["products"]) - carriers}
            expected |= members
            require(len(members) == 4, "Four source binding entrances for " + e)
            counts[s["title"] + " / " + e] = len(members)
        require(set(s["reaction_ids"]) == expected, "Source binding grouping identities")
    return {"scoped_reactions": 134, "representative_paths": 20, "outside_phase_a": 834,
            "original_transition_projection_count": len(data["transitions"]),
            "return_witnesses": sum(len(m["return_loops"]) for m in data["modules"].values()), "binding_counts": counts,
            "phase_a_hashes": data["metadata"]["phase_a_inputs"]}


def gate_c(data, source, parameters):
    results = {}
    complete = []
    for pid, p in data["paths"].items():
        vector = net(p["reaction_ids"], source)
        require(vector == p["net_reference"], "Independent S-column sum " + pid)
        certified = cycle(p, vector, set(data["modules"][p["enzyme"]]["carrier_states"]))
        require(certified == p["complete_catalytic_cycle"], "Incomplete path cannot be a cycle " + pid)
        require(p["reference_feasible"] == all(parameters[r] != 0 for r in p["reaction_ids"]), "Disabled reference support " + pid)
        results[pid] = {"net": vector, "cycle": certified, "reference_feasible": p["reference_feasible"]}
        if certified:
            complete.append(pid)
    for e, aa, trna, target in (("GlyRS", "Gly", "tRNAGlyGCC", "GlytRNAGlyGCC"), ("MetRS", "Met", "tRNAfMetCAU", "MettRNAfMetCAU")):
        expected = {aa: "-1", "ATP": "-1", trna: "-1", target: "1", "AMP": "1", "PPi": "1"}
        require(results[e + "-P01"]["net"] == expected, "P01 catalytic stoichiometry")
        # Valid entrance plus existing shared continuation, used as a check
        # only; no new scientific path is written or offered by the UI.
        entrance, main = data["paths"][e + "-P02"], data["paths"][e + "-P01"]
        index = main["states"].index(entrance["end"])
        require(net(entrance["reaction_ids"] + main["reaction_ids"][index:], source) == expected, "Rejoined suffix algebra")
    witnesses = {l["id"]: net(l["reaction_ids"], source) for m in data["modules"].values() for l in m["return_loops"]}
    require(all(not value for value in witnesses.values()), "All exact two-direction return witnesses cancel")
    return {"path_nets": results, "complete_productive_cycles": complete, "incomplete_entries": 20 - len(complete),
            "return_witness_nets": witnesses, "shared_suffix_entrance_checks": 2,
            "algebra_scope": "STOICHIOMETRY_ONLY_NOT_KINETICS_OR_REDUCTION"}


def gate_d(data, source):
    precursor = "GlyRS_Gly_ATP_tRNAGlyGCC"
    expected = {f"re{i:010d}" for i in (197, 206, 196, 194, 214)}
    require(set(data["modules"]["GlyRS"]["branches"][precursor]) == expected, "Five parallel outlets")
    for rid in expected:
        require(source[rid]["reactants"].get(precursor) == 1, "Common real precursor")
    require(data["reactions"]["re0000000214"]["reference_activity"] == "REFERENCE_DISABLED", "0214 inactive")
    require(source["re0000000214"]["products"].get("GlyRS_degraded") == 1, "0214 real sink")
    require(data["paths"]["GlyRS-P02"]["reaction_ids"] == ["re0000000132", "re0000000134"], "Real alternate entrance")
    require(data["paths"]["GlyRS-P02"]["end"] == "GlyRS_Gly_ATP", "Real rejoin")
    for e, m in data["modules"].items():
        for p in [data["paths"][pid] for pid in m["path_ids"]] + m["return_loops"]:
            require(len(p["states"]) == len(p["reaction_ids"]) + 1, "Endpoint sequence length")
            for i, rid in enumerate(p["reaction_ids"]):
                require(source[rid]["reactants"].get(p["states"][i]) == 1 and source[rid]["products"].get(p["states"][i + 1]) == 1,
                        "Real directed carrier continuity")
        require(len(m["rejoins"][e + "_degraded"]) == 15, "All 15 original sink inlets")
    scoped = set(data["phase_a_ids"])
    for b in data["boundary_links"]:
        require(b["reaction_id"] not in scoped and b["interpretation_status"] == "HUMAN_REVIEW_REQUIRED", "External incidence only")
        side = "reactants" if b["role"] == "reactant" else "products"
        require(source[b["reaction_id"]][side][b["species"]] == Fraction(b["stoichiometry"]), "Boundary exact source occurrence")
    return {"parallel_precursor": precursor, "parallel_outlets": sorted(expected), "disabled_sink": "re0000000214",
            "alternate_rejoin": "GlyRS-P01 / re0000000205", "foreign_incidence_records": len(data["boundary_links"]),
            "foreign_status": "PATHWAY_NOT_RECONSTRUCTED / HUMAN_REVIEW_REQUIRED"}


def old_regression():
    with tempfile.TemporaryDirectory(prefix="atlas-phase-a-regression-") as tmp:
        directory = Path(tmp)
        for name in ("glyrs_metrs_graph.json", "glyrs_metrs_pathway_index.csv", "glyrs_metrs_sample.md"):
            shutil.copyfile(OUT / name, directory / name)
        command = [sys.executable, str(ROOT / "scripts/pathways/test_pathway_atlas.py"), "--output-dir", str(directory)]
        run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        require(run.returncode == 0, "Original Phase A regression failed: " + run.stdout + run.stderr)
        report = json.loads((directory / "validation_report.json").read_text(encoding="utf-8"))
        require(report["structural_status"] == "PASS", "Original Phase A gates")
        return {"status": "PASS", "published_reports_untouched": True, "test_report": report,
                "negative_controls": json.loads((directory / "negative_controls.json").read_text(encoding="utf-8"))}


def rebuild(html_path):
    with tempfile.TemporaryDirectory(prefix="atlas-html-reproduction-") as tmp:
        hashes = []
        for i in (1, 2):
            output = Path(tmp) / f"run{i}.html"
            run = subprocess.run([sys.executable, str(ROOT / "scripts/pathways/build_reaction_atlas_html.py"), "--output", str(output)],
                                 cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            require(run.returncode == 0, "HTML rebuild failure: " + run.stdout + run.stderr)
            hashes.append(digest(output))
        require(hashes[0] == hashes[1] == digest(html_path), "Two rebuilt HTML files must equal the deliverable bytes")
        return {"status": "PASS", "independent_runs": 2, "matches_deliverable_bytes": True, "sha256": hashes[0]}


def browser_executable():
    candidates = [os.environ.get("ATLAS_BROWSER_EXECUTABLE", ""),
                  r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                  r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def run_browser(html_path, data, source, screenshot_dir=None):
    from playwright.sync_api import sync_playwright
    checks, errors, console_errors, requests = [], [], [], []
    evidence = {"checks": checks, "page_errors": errors, "console_errors": console_errors,
                "network_requests": requests, "browser_test_mode": "OFFLINE_FILE_URL_REAL_INTERACTION"}
    with sync_playwright() as p:
        executable = browser_executable()
        browser = p.chromium.launch(headless=True, **({"executable_path": executable} if executable else {}))
        evidence.update({"browser_version": browser.version, "executable": executable or "existing_playwright_chromium"})
        context = browser.new_context(offline=True, viewport={"width": 1600, "height": 1000})
        context.grant_permissions(["clipboard-read", "clipboard-write"])
        page = context.new_page()
        page.set_default_timeout(8000)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("request", lambda request: requests.append(request.url) if not request.url.startswith("file:") else None)

        def check(name, condition, details=None):
            require(condition, "Browser check: " + name + (": " + str(details) if details else ""))
            checks.append({"name": name, "status": "PASS", **({"details": details} if details is not None else {})})

        def shot(name):
            if screenshot_dir:
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(screenshot_dir / (name + ".png")))

        def search(text):
            page.locator("#search").fill(text)
            page.wait_for_function("q => Atlas.getState().query === q", arg=text)

        def choose_path(pid):
            search(pid)
            page.locator(f'#content [data-action="path"][data-path="{pid}"]').click()
            require(page.locator("#selected-path-title").inner_text() == pid, "Path selection " + pid)

        def coverage():
            return [page.locator("#" + name).inner_text() for name in ("source-count", "source-coverage", "phase-coverage", "remaining-count")]

        def inspect(rid):
            search(rid)
            page.locator(f'.reaction-list [data-action="reaction"][data-rid="{rid}"]').click()
            require(page.locator("#inspector-rid").inner_text() == rid, "Actual inspector Reaction ID")
            require(page.locator("#inspector-equation").inner_text() == data["reactions"][rid]["equation"], "Actual inspector source equation " + rid)

        def presentation_cards(test_page, path):
            cards = test_page.locator(".path-step").evaluate_all("""xs=>xs.map(e=>({
              rid:e.dataset.rid,number:Number(e.dataset.step),pairStatus:e.dataset.pairStatus,
              displayIds:e.dataset.displayIds.split(','),
              equations:[...e.querySelectorAll('.equation')].map(x=>x.textContent.trim()),
              headerIds:[...e.querySelectorAll('.card-top [data-action="reaction"]')].map(x=>x.dataset.rid),
              tags:[...e.querySelectorAll('.tag.code')].map(x=>x.textContent),
              description:e.querySelector('.mechanism-description')?.textContent,
              direction:e.querySelector('.path-direction')?.textContent,
              activities:[...e.querySelectorAll('[data-direction-rid]')].map(x=>({
                rid:x.dataset.directionRid,label:x.querySelector('.activity-label').textContent,
                disabled:x.classList.contains('disabled-direction')})),
              competition:[...e.querySelectorAll('.competition-button')].map(x=>({
                state:x.dataset.state,count:Number(x.dataset.outgoingCount),label:x.textContent,aria:x.getAttribute('aria-label')})),
              projection:e.querySelectorAll('.carrier-transition,.co-substrates,.card-meta').length,
              text:e.textContent,technical:[...e.querySelectorAll('.step-tools [data-action="reaction"]')].map(x=>x.textContent)
            }))""")
            require(len(cards) == len(path["reaction_ids"]), "One card per actual directed step")
            displayed_ids, paired_cards = set(), 0
            for i, (card, rid) in enumerate(zip(cards, path["reaction_ids"])):
                r = source[rid]
                matches = [other for other, candidate in source.items() if other != rid and
                           r["reactants"] == candidate["products"] and r["products"] == candidate["reactants"]]
                reciprocal = ([other for other, candidate in source.items() if other != matches[0] and
                               source[matches[0]]["reactants"] == candidate["products"] and
                               source[matches[0]]["products"] == candidate["reactants"]] if len(matches) == 1 else [])
                paired = (len(matches) == len(reciprocal) == 1 and data["reactions"][rid]["reverse"] == matches[0]
                          and data["reactions"][matches[0]]["reverse"] == rid)
                ids = sorted([rid, matches[0]]) if paired else [rid]
                displayed_ids.update(ids)
                paired_cards += paired
                require(card["rid"] == rid and card["number"] == i + 1, "Original step identity and number")
                require(card["headerIds"] == card["displayIds"] == ids, "Both original IDs independently linked")
                require(card["pairStatus"] == ("EXACT_UNIQUE_SOURCE_PAIR" if paired else "UNPAIRED"), "Independent exact pair status")
                require(len(card["equations"]) == 1, "Only one equation per step")
                equation = card["equations"][0]
                require(("⇌" in equation) == paired, "No invented bidirectional arrow")
                require(parse_equation(equation.replace("⇌", "->").replace("→", "->")) ==
                        [source[ids[0]]["reactants"], source[ids[0]]["products"]], "Canonical source sides and coefficients")
                require(card["projection"] == 0 and not any(x in card["text"] for x in
                        ("另外必须消耗", "另外释放", "∅", "RFAM")), "No redundant projection or audit fields")
                require(card["tags"] == data["reactions"][rid]["level_c"], "Reviewed current-direction Level-C retained")
                require(card["description"] and card["technical"] == ["技术详情"], "Mechanism explanation and technical action")
                require(card["description"].count("。") == 1, "One concise mechanism sentence per card")
                direction = "→" if rid == ids[0] else "←"
                require(card["direction"] == "当前路径：" + direction + " " + rid, "Actual path direction, independent of pair orientation")
                if paired:
                    require(card["activities"] == [{"rid": id, "label": "REFERENCE_DISABLED" if
                            data["reactions"][id]["reference_activity"] == "REFERENCE_DISABLED" else "REFERENCE_ENABLED",
                            "disabled": data["reactions"][id]["reference_activity"] == "REFERENCE_DISABLED"} for id in ids],
                            "Separate directional reference activity and disabled styling")
                before = path["states"][i]
                # Count from fresh SBML sides within the published carrier module,
                # independently of JS and the parameter filter.
                m = data["modules"][data["transitions"][rid]["enzyme"]]
                outlets = [id for id in m["reaction_ids"] if before in source[id]["reactants"] and
                           set(source[id]["products"]) & set(m["carrier_states"])]
                if len(outlets) > 1:
                    require(len(card["competition"]) == 1 and card["competition"][0]["state"] == before and
                            card["competition"][0]["count"] == len(outlets) and
                            card["competition"][0]["label"] == f"查看竞争出口 ({len(outlets)})" and
                            before in card["competition"][0]["aria"], "Original precursor and outlet count")
                else:
                    require(not card["competition"], "No misleading competition action")
            counts = test_page.locator(".path-counts")
            require(int(counts.get_attribute("data-path-step-count")) == len(cards) and
                    int(counts.get_attribute("data-paired-card-count")) == paired_cards and
                    int(counts.get_attribute("data-displayed-id-count")) == len(displayed_ids), "Three separate UI counts")
            return {"cards": len(cards), "bidirectional_cards": paired_cards, "displayed_original_ids": len(displayed_ids)}

        try:
            page.goto(html_path.resolve().as_uri(), wait_until="load")
            check("offline file:// load", page.url.startswith("file:") and page.locator("#content h2").first.inner_text() == "RS_binding")
            original_coverage = coverage()
            check("default functional summary without a unique net", page.locator('[data-summary-kind="FUNCTIONAL"][data-net-unique="false"]').count() == 1 and page.locator("#net-equation").count() == 0)
            check("23 Level-C navigation entries", page.locator("#hierarchy details[data-context]").count() == 23)
            shot("atlas-functional")
            group = page.locator('details[data-group="RS"]')
            group.locator(":scope > summary").click()
            check("Level A collapses", not group.evaluate("e=>e.open"))
            group.locator(":scope > summary").click()
            binding = page.locator('details[data-context="RS_binding"]')
            binding.locator(":scope > summary").click(position={"x": 4, "y": 10})
            check("Level C collapses", not binding.evaluate("e=>e.open"))
            binding.locator(":scope > summary").click(position={"x": 4, "y": 10})
            topic = page.locator('details[data-substep="RS_binding:0"]')
            topic.locator(":scope > summary").click()
            for e in ("GlyRS", "MetRS"):
                topic.locator(f'[data-action="substep"][data-enzyme="{e}"]').click()
                check("source binding count " + e, page.locator(".reaction-list .reaction-card").count() == 4)
            topic.locator(":scope > summary").click()
            check("subprocess collapses", not topic.evaluate("e=>e.open"))

            # Actual buttons and rendered DOM, all 20 representative paths.
            for pid, path in data["paths"].items():
                choose_path(pid)
                ids = page.locator(".path-step").evaluate_all("xs=>xs.map(e=>e.dataset.rid)")
                check("ordered path " + pid, ids == path["reaction_ids"], {"steps": len(ids)})
                vector = json.loads(page.locator("#net-equation").get_attribute("data-net-vector"))
                check("visible canonical net " + pid, vector == net(ids, source))
                kind = "CATALYTIC_CYCLE" if path["complete_catalytic_cycle"] else "PATH_NET"
                check("summary type " + pid, page.locator(f'[data-summary-kind="{kind}"]').count() == 1)
                check("reference support " + pid, page.locator("[data-reference-supported]").get_attribute("data-reference-supported") == str(path["reference_feasible"]).lower())
                check("single source equation and exact reverse card " + pid, True, presentation_cards(page, path))
            evidence["representative_card_coverage"] = {"paths": 20,
                "actual_directed_step_occurrences": sum(len(p["reaction_ids"]) for p in data["paths"].values()),
                "one_equation_per_step": True, "independent_direction_activity": True,
                "carrier_projection_hidden_only_in_main_cards": True}
            choose_path("GlyRS-P01")
            check("GlyRS-P01 has eight steps", page.locator(".path-step").count() == 8)
            first_step = page.locator(".path-step").first
            check("0126 centered on one reversible source equation", first_step.locator(".equation").inner_text() == "Gly + GlyRS ⇌ GlyRS_Gly" and
                  first_step.locator(".carrier-transition,.co-substrates").count() == 0 and "RS_binding" in first_step.inner_text())
            first_step.locator('.step-tools [data-action="reaction"]').click()
            t = data["transitions"]["re0000000126"]
            check("0126 inspector preserves carrier projection", all(
                json.loads(page.locator("#inspector-carrier-" + side).get_attribute("data-species")) == t["carrier_" + side]
                for side in ("before", "after")))
            check("0126 inspector preserves other participants", page.locator("#inspector-other-reactants li").inner_text().split() == [t["other_reactants"]["Gly"], "Gly"] and
                  page.locator("#inspector-other-products").inner_text() == "无" and not t["other_products"])
            page.locator('#inspector-carrier-before [data-action="state"]').click()
            check("carrier state remains accessible through inspector", page.locator("#state-dialog-title").inner_text() == t["carrier_before"][0])
            page.locator('[data-action="close-state"]').click()
            partner = data["reactions"][data["paths"]["GlyRS-P01"]["reaction_ids"][0]]["reverse"]
            first_step.locator(f'.card-top [data-action="reaction"][data-rid="{partner}"]').click()
            check("reverse partner inspected without changing main chain", page.locator("#inspector-rid").inner_text() == partner and page.locator(".path-step").count() == 8)
            check("0131 has its own original direction and parameter", page.locator("#inspector-equation").inner_text() == data["reactions"][partner]["equation"] and
                  json.loads(page.locator("#inspector-carrier-before").get_attribute("data-species")) == data["transitions"][partner]["carrier_before"])
            page.locator("#source-provenance > summary").click()
            check("inverse original rate remains separate", "原始参数: " + data["reactions"][partner]["reference_parameter"] in page.locator(".provenance").inner_text())
            page.locator('.path-step[data-rid="re0000000197"] [data-action="reaction"]').first.click()
            check("0197 exact inspector", page.locator("#inspector-equation").inner_text() == data["reactions"]["re0000000197"]["equation"])
            check("provenance collapsed", not page.locator("#source-provenance").evaluate("e=>e.open"))
            disabled_row = page.locator('.path-step[data-rid="re0000000197"] [data-direction-rid="re0000000198"]')
            check("0198 disabled direction explicit in bidirectional card", disabled_row.locator(".activity-label").inner_text() == "REFERENCE_DISABLED" and
                  disabled_row.evaluate("e=>e.classList.contains('disabled-direction')") and disabled_row.is_visible())
            page.locator('.path-step[data-rid="re0000000197"] .card-top [data-rid="re0000000198"]').click()
            check("0198 independently opens disabled inverse inspector", page.locator("#inspector-rid").inner_text() == "re0000000198" and
                  page.locator("#inspector-equation").inner_text() == data["reactions"]["re0000000198"]["equation"] and
                  "REFERENCE_DISABLED" in page.locator("#inspector-content").inner_text())
            first_step.scroll_into_view_if_needed()
            page.locator("#reading").evaluate("e=>e.scrollTop+=document.querySelector('.path-steps').getBoundingClientRect().top-e.getBoundingClientRect().top-24")
            shot("atlas-glyrs-p01-new-cards")
            if screenshot_dir:
                box = first_step.bounding_box()
                page.screenshot(path=str(screenshot_dir / "atlas-glyrs-p01-first-card.png"),
                    clip={"x": box["x"] - 40, "y": box["y"], "width": box["width"] + 40, "height": box["height"]})
            shot("atlas-glyrs-p01")
            precursor = "GlyRS_Gly_ATP_tRNAGlyGCC"
            page.locator("#positive-only").check()
            competition = page.locator(f'.path-step[data-rid="re0000000197"] .competition-button[data-state="{precursor}"]')
            check("parameter filter preserves five original precursor exits", competition.inner_text() == "查看竞争出口 (5)")
            competition.click()
            grid = page.locator("#state-dialog .branch-grid")
            actual = grid.locator("[data-outgoing-rid]").evaluate_all("xs=>xs.map(e=>e.dataset.outgoingRid).sort()")
            expected = sorted(f"re{i:010d}" for i in (197, 206, 196, 194, 214))
            check("five parallel outlets", actual == expected and grid.evaluate("e=>getComputedStyle(e).display") == "grid")
            boxes = grid.locator("[data-outgoing-rid]").evaluate_all("xs=>xs.map(e=>({x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y}))")
            check("parallel layout has two columns, not a serial chain", len({round(b["x"]) for b in boxes}) == 2 and boxes[0]["y"] == boxes[1]["y"])
            sink = grid.locator('[data-outgoing-rid="re0000000214"]')
            check("0214 disabled sink default collapsed", "REFERENCE_DISABLED" in sink.inner_text() and not sink.locator("details").evaluate("e=>e.open"))
            shot("atlas-parallel-branches")
            sink.locator("summary").click()
            sink.locator('[data-action="state"][data-state="GlyRS_degraded"]').click()
            check("sink convergence distinguished", page.locator('[data-convergence="SINK_CONVERGENCE"]').count() == 1 and
                  "PRODUCTIVE_REJOIN" not in page.locator("#state-content .tag-row").first.inner_text())
            check("all 15 sink inlets accessible", page.locator("#state-content > .jump-list [data-action='reaction']").count() == 15)
            page.locator('[data-action="close-state"]').click()
            page.locator("#positive-only").uncheck()
            choose_path("GlyRS-P02")
            page.locator('[data-action="rejoin"][data-state="GlyRS_Gly_ATP"]').click()
            check("alternate entrance rejoin focuses next 0205", page.locator("#selected-path-title").inner_text() == "GlyRS-P01" and
                  page.locator(".focused-step").evaluate_all("xs=>xs.map(e=>e.dataset.rid)") == ["re0000000205"])
            choose_path("GlyRS-P07")
            page.locator('[data-action="rejoin"][data-state="GlyRS_GlyAMP_tRNAGlyGCC"]').click()
            check("shared suffix rejoin focuses 0178", page.locator(".focused-step").get_attribute("data-rid") == "re0000000178")

            displays = page.evaluate("() => Object.fromEntries(Object.keys(Atlas.data.reactions).map(rid=>[rid,Atlas.getExactReverseDisplay(rid,Atlas.data)]))")
            paired_ids = []
            for rid, display in displays.items():
                matches = [id for id, r in source.items() if id != rid and source[rid]["reactants"] == r["products"] and
                           source[rid]["products"] == r["reactants"]]
                if display["reverseId"]:
                    a, b = display["forwardId"], display["reverseId"]
                    require(matches == [b if rid == a else a] and a < b, "Every displayed pair uses full exact source sides")
                    require(source[a]["reactants"] == source[b]["products"] and source[a]["products"] == source[b]["reactants"], "No net-only reverse matching")
                    require(exact(display["reactants"]) == source[a]["reactants"] and exact(display["products"]) == source[a]["products"], "Deterministic original orientation")
                    paired_ids.append(rid)
                else:
                    require(not matches, "Unique published exact partners must be displayed")
            check("all 968 reverse display decisions independently checked against SBML", True,
                  {"paired_directed_ids": len(paired_ids), "unique_exact_pairs": len(paired_ids) // 2})
            controls = page.evaluate("""() => {
              const tiny=()=>({reactions:{F:structuredClone(Atlas.data.reactions.re0000000126),
                R:structuredClone(Atlas.data.reactions.re0000000131)}});
              const fixture=()=>{const d=tiny();d.reactions.F.reverse='R';d.reactions.R.reverse='F';return d;};
              const paired=(d,id='F')=>Boolean(Atlas.getExactReverseDisplay(id,d).reverseId);
              const result={},d=fixture();
              const a=Atlas.getExactReverseDisplay('F',d),b=Atlas.getExactReverseDisplay('R',d);
              result.canonicalBothDirections=a.forwardId===b.forwardId && a.reverseId===b.reverseId &&
                a.currentDirection==='→' && b.currentDirection==='←';
              const near=fixture();near.reactions.R.products.Gly='1.00000000000000000001';result.nearCoefficientRejected=!paired(near);
              const netOnly=fixture();netOnly.reactions.R.reactants.Catalyst='1';netOnly.reactions.R.products.Catalyst='1';
              result.netOnlyReverseRejected=!paired(netOnly);
              const amb=fixture();amb.reactions.R2=structuredClone(amb.reactions.R);result.ambiguousReverseRejected=!paired(amb);
              const ambForward=fixture();ambForward.reactions.F2=structuredClone(ambForward.reactions.F);
              result.ambiguousForwardRejected=!paired(ambForward);
              const stale=fixture();stale.reactions.R.reverse=null;result.nonreciprocalPointerRejected=!paired(stale);
              const missing=fixture();missing.reactions.F.reverse=null;result.unreviewedPointerRejected=!paired(missing);
              const absent=fixture();delete absent.reactions.R;result.absentPartnerRejected=!paired(absent);
              const reordered=fixture();reordered.reactions.R.products={GlyRS:'1.0',Gly:'1e0'};
              result.exactRationalAndOrderAccepted=paired(reordered);
              const single=document.createElement('div');single.innerHTML=Atlas.pathStep('re0000000214',
                'GlyRS_Gly_ATP_tRNAGlyGCC','GlyRS_degraded',1);
              result.realUnpairedUsesSingleArrow=single.querySelector('.arrow').textContent.trim()==='→' &&
                single.querySelectorAll('.card-top [data-action="reaction"]').length===1;
              const saved=Atlas.data.transitions;
              try {Atlas.data.transitions={re0000000126:saved.re0000000126};
                const one=document.createElement('div');one.innerHTML=Atlas.pathStep('re0000000126','GlyRS','GlyRS_Gly',1);
                result.singleOutletHasNoCompetition=one.querySelectorAll('.competition-button').length===0;
                result.sinkHasNoOutgoing=Atlas.getCompetingOutlets('GlyRS_degraded','GlyRS',Atlas.data).length===0;
              } finally {Atlas.data.transitions=saved;}
              const foreign=Object.keys(Atlas.data.reactions).filter(rid=>!Atlas.data.phase_a_ids.includes(rid));
              result.noForeignMechanismNarratives=foreign.every(rid=>Atlas.mechanismDescription(rid,Atlas.data,true)==='');
              const descriptions=Object.fromEntries(Object.keys(saved).map(rid=>[rid,Atlas.mechanismDescription(rid,Atlas.data)]));
              result.associationUsesReviewedTemplate=descriptions.re0000000126==='Gly 与游离 GlyRS 结合形成复合物。';
              result.dissociationUsesReviewedTemplate=descriptions.re0000000189==='酶结合态复合物释放 PPi。';
              result.chargingUsesReviewedTemplate=descriptions.re0000000178.includes('aminoacyl-tRNA');
              result.activationUsesReviewedTemplate=descriptions.re0000000197.includes('aminoacyl-AMP / PPi');
              return result;
            }""")
            for name, condition in controls.items():
                check("pair and narrative control " + name, condition)

            # Runtime algebra counterexamples: repeated real cycles and source
            # data perturbation. Changes exist only in this disposable page.
            doubled = data["paths"]["GlyRS-P01"]["reaction_ids"] * 2
            check("executed JS counts repeated occurrences", page.evaluate("ids=>Atlas.netForIds(ids)", doubled) == net(doubled, source))
            check("no hardcoded cycle equation", page.evaluate("""() => {
              const r=Atlas.data.reactions.re0000000126, original=r.reactants.Gly;
              try {r.reactants.Gly='3/2';return Atlas.netForIds(Atlas.data.paths['GlyRS-P01'].reaction_ids).Gly==='-3/2';}
              finally {r.reactants.Gly=original;}
            }"""))
            p01 = data["paths"]["GlyRS-P01"]
            fake = {**p01, "end": "GlyRS_AMP"}
            check("nonclosed cycle rejected by executed JS", not page.evaluate("p=>Atlas.cycleCertificate(p,Atlas.netForIds(p.reaction_ids))", fake))
            no_product = {**p01, "target_product": "GlyRS"}
            check("cycle without actual target production rejected", not page.evaluate("p=>Atlas.cycleCertificate(p,Atlas.netForIds(p.reaction_ids))", no_product))
            for e, m in data["modules"].items():
                choose_path(e + "-P01")
                page.locator("#content > details.chooser > summary").click()
                enzyme = page.locator(f'.enzyme-chooser[data-enzyme="{e}"]')
                if not enzyme.evaluate("el=>el.open"):
                    enzyme.locator(":scope > summary").click()
                loop_details = enzyme.locator(":scope > details")
                loop_details.locator(":scope > summary").click()
                check("all finite return witnesses selectable " + e, loop_details.locator('[data-action="loop"]').count() == 24)
                disabled_loop = next(l for l in m["return_loops"] if not l["reference_feasible"])
                loop_details.locator(f'[data-loop="{disabled_loop["id"]}"]').click()
                check("disabled return not promoted " + e, page.locator('[data-summary-kind="PATH_NET"][data-reference-supported="false"]').count() == 1)
                check("return witness independent net " + e, json.loads(page.locator("#net-equation").get_attribute("data-net-vector")) == net(disabled_loop["reaction_ids"], source))
                check("local return keeps two real directions with one canonical orientation " + e, True,
                      presentation_cards(page, disabled_loop))
            witness_vectors = page.evaluate("() => Object.fromEntries(Object.values(Atlas.data.modules).flatMap(m=>m.return_loops.map(l=>[l.id,Atlas.netForIds(l.reaction_ids)])))")
            check("all 48 executed return nets", witness_vectors == {l["id"]: net(l["reaction_ids"], source) for m in data["modules"].values() for l in m["return_loops"]})

            inspect("re0000000197")
            check("exact Reaction ID search", page.locator(".reaction-list .reaction-card").count() == 1)
            page.locator('[data-action="copy"][data-copy="rid"]').click()
            page.wait_for_function("() => document.getElementById('toast').textContent.length>0")
            clipboard_id = page.evaluate("() => navigator.clipboard.readText()")
            check("copy Reaction ID", clipboard_id == "re0000000197")
            page.locator('[data-action="copy"][data-copy="equation"]').click()
            page.wait_for_function("() => document.getElementById('toast').classList.contains('visible')")
            check("copy full equation", page.evaluate("() => navigator.clipboard.readText()") == data["reactions"]["re0000000197"]["equation"])
            search(precursor)
            expected_incident = sorted(rid for rid, r in source.items() if precursor in r["reactants"] or precursor in r["products"])
            actual_incident = page.locator(".reaction-list .reaction-card").evaluate_all("xs=>xs.map(e=>e.dataset.reactionCard)")
            check("species search returns actual incident source IDs", actual_incident == expected_incident)
            page.locator('[data-action="search-kind"][data-kind="species"]').click()
            check("species tab finds exact species", page.locator('.result-species [data-action="state"]').count() == 1)
            page.locator('[data-action="species-reactions"]').click()
            check("species incidence opens source list", page.locator(".reaction-list .reaction-card").count() == len(expected_incident))
            inspect("re0000000414")
            check("0414 visible 2 PO4", "2 PO4" in page.locator("#inspector-equation").inner_text())
            outside = set(data["reactions"]) - set(data["phase_a_ids"])
            check("outside inspector explicitly pending", "PATHWAY_NOT_RECONSTRUCTED" in page.locator("#inspector-pathway-status").inner_text())
            # Search and inspector independently exercised across every Level C.
            for stage in data["level_c_contexts"]:
                rid = next(rid for rid, r in data["reactions"].items() if stage in r["level_c"])
                inspect(rid)
                check("source inspector across " + stage, stage in page.locator("#inspector-content .tag-row").first.inner_text())
                if rid in outside:
                    require("PATHWAY_NOT_RECONSTRUCTED" in page.locator("#inspector-pathway-status").inner_text(), "Foreign inspector scope")
            family = data["reactions"]["re0000000197"]["family"]
            search(family)
            expected_family = sorted(rid for rid, r in data["reactions"].items() if r["family"] == family)
            check("family search", page.locator(".pager > span").inner_text().endswith("/ " + str(len(expected_family))))
            search("DEG_sink")
            before_filter = page.locator(".pager > span").inner_text()
            page.locator("#positive-only").check()
            check("zero parameter filter changes list", page.locator(".pager > span").inner_text() != before_filter)
            check("filter preserves original coverage", coverage() == original_coverage, original_coverage)
            search("re0000000214")
            check("disabled search hidden under filter", page.locator(".reaction-list .reaction-card").count() == 0)
            page.locator("#positive-only").uncheck()
            inspect("re0000000214")
            check("disabled reaction retained in complete index", "REFERENCE_DISABLED" in page.locator("#inspector-content .tag-row").first.inner_text())
            page.locator('#hierarchy [data-action="context"][data-context="RS_to_INIT_formylation"]').click()
            check("unreconstructed MTF context explicit", page.locator('[data-pathway-status="PATHWAY_NOT_RECONSTRUCTED"]').count() == 1)
            formyl = page.locator('details[data-context="RS_to_INIT_formylation"]')
            formyl.locator('.nav-sub > summary').click()
            formyl.locator('[data-action="substep"]').click()
            check("unreviewed substep visibly marked", page.locator('[data-mapping-status="SUBSTEP_MAPPING_NOT_VALIDATED"]').count() == 1)
            page.locator("#pathway-mode").click()
            check("no new MTF pathway", page.locator('[data-pathway-status="PATHWAY_NOT_RECONSTRUCTED"]').count() == 1 and page.locator(".path-step").count() == 0)
            choose_path("GlyRS-P01")
            handoff = page.locator(".handoff-box")
            handoff.locator(":scope > summary").click()
            check("handoff source incidence scope", "PATHWAY_NOT_RECONSTRUCTED" in handoff.inner_text() and "HUMAN_REVIEW_REQUIRED" in handoff.inner_text())
            handoff.locator('[data-action="boundary"]').click()
            check("foreign handoff has source list, no path", page.locator(".path-step").count() == 0 and page.locator('[data-pathway-status="PATHWAY_NOT_RECONSTRUCTED"]').count() == 1)

            # All 968 IDs through real paginated cards and their click handlers.
            page.locator('[data-action="all-source"]').click()
            seen, page_counts = [], []
            while True:
                cards = page.locator(".reaction-list .reaction-card")
                page_ids = cards.evaluate_all("xs=>xs.map(e=>e.dataset.reactionCard)")
                require(len(page_ids) <= 24, "No eager full-network DOM")
                page_counts.append(len(page_ids))
                for rid in page_ids:
                    cards.locator(f'[data-action="reaction"][data-rid="{rid}"]').click()
                    require(page.locator("#inspector-equation").inner_text() == data["reactions"][rid]["equation"], "All-source inspector equation " + rid)
                    visible = page.locator("#inspector-content .tag-row").first.inner_text()
                    require(all(c in visible for c in data["reactions"][rid]["level_c"]), "All-source inspector labels " + rid)
                    require(("REFERENCE_DISABLED" in visible) == (data["reactions"][rid]["reference_activity"] == "REFERENCE_DISABLED"), "All-source zero activity " + rid)
                    if rid in outside:
                        require("PATHWAY_NOT_RECONSTRUCTED" in page.locator("#inspector-pathway-status").inner_text(), "All-source pending pathway " + rid)
                seen.extend(page_ids)
                next_button = page.locator('.pager [data-delta="1"]')
                if next_button.is_disabled():
                    break
                next_button.click()
            check("all 968 source equations opened by real card clicks", len(seen) == 968 and set(seen) == set(source), {"pages": len(page_counts), "max_cards_per_page": max(page_counts)})
            check("paging coverage invariant", coverage() == original_coverage)
            choose_path("MetRS-P01")
            page.locator('.path-step[data-rid="re0000000239"] [data-action="reaction"]').first.click()
            shot("atlas-metrs-p01")

            # Browser layout at narrow widths.
            page.set_viewport_size({"width": 390, "height": 844})
            check("narrow viewport has no horizontal overflow", page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth"))
            check("narrow step equations retain exact complete sides", True, presentation_cards(page, data["paths"]["MetRS-P01"]))
            check("narrow equations wrap without clipping", page.locator(".path-step .equation").evaluate_all(
                "xs=>xs.every(e=>e.scrollWidth<=e.clientWidth && !['hidden','clip'].includes(getComputedStyle(e).overflowX))"))
            check("narrow source inventory remains visible", page.locator(".compact-source-network").is_visible())
            page.locator('[data-action="toggle-nav"]').click()
            check("narrow navigation opens", page.locator(".navigation").is_visible())
            page.locator('[data-action="toggle-nav"]').click()
            check("narrow navigation closes", not page.locator(".navigation").is_visible())
            shot("atlas-narrow")
            page.locator('.path-step[data-rid="re0000000239"]').scroll_into_view_if_needed()
            shot("atlas-narrow-cards")
            # Native page zoom is changed through Chromium's own Settings in
            # a fresh disposable profile. This never touches the user's profile.
            # CSS zoom is not equivalent: it leaves viewport media queries at
            # their old width and can produce a false overflow failure.
            with tempfile.TemporaryDirectory(prefix="atlas-native-zoom-") as profile:
                zoom_context = p.chromium.launch_persistent_context(profile, headless=True,
                    **({"executable_path": executable} if executable else {}), offline=True,
                    viewport={"width": 1600, "height": 1000})
                try:
                    settings = zoom_context.pages[0]
                    settings.goto("chrome://settings/appearance")
                    settings.locator("select#zoomLevel").select_option("2")
                    zoom_page = zoom_context.new_page()
                    zoom_page.on("pageerror", lambda error: errors.append(str(error)))
                    zoom_page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
                    zoom_page.on("request", lambda request: requests.append(request.url) if not request.url.startswith("file:") else None)
                    zoom_page.goto(html_path.resolve().as_uri())
                    zoom_page.locator("#search").fill("MetRS-P01")
                    zoom_page.wait_for_function("() => Atlas.getState().query === 'MetRS-P01'")
                    zoom_page.locator('[data-action="path"][data-path="MetRS-P01"]').click()
                    metrics = zoom_page.evaluate("({dpr:devicePixelRatio,width:innerWidth,clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,cssZoom:getComputedStyle(document.documentElement).zoom})")
                    check("native browser page zoom is 200 percent", metrics["dpr"] == 2 and metrics["width"] == 800 and metrics["cssZoom"] == "1", metrics)
                    check("200 percent native zoom has no horizontal overflow", metrics["scrollWidth"] <= metrics["clientWidth"])
                    check("200 percent native zoom preserves net and eight steps", zoom_page.locator(".path-step").count() == 8 and
                          json.loads(zoom_page.locator("#net-equation").get_attribute("data-net-vector")) == net(data["paths"]["MetRS-P01"]["reaction_ids"], source))
                    check("200 percent native zoom preserves readable exact cards", True, presentation_cards(zoom_page, data["paths"]["MetRS-P01"]))
                    check("200 percent equations wrap without clipping", zoom_page.locator(".path-step .equation").evaluate_all(
                        "xs=>xs.every(e=>e.scrollWidth<=e.clientWidth && !['hidden','clip'].includes(getComputedStyle(e).overflowX))"))
                    check("native zoom page has no resource requests", zoom_page.evaluate("performance.getEntriesByType('resource').length") == 0)
                    if screenshot_dir:
                        zoom_page.screenshot(path=str(screenshot_dir / "atlas-zoom-200.png"))
                    zoom_page.locator('.path-step[data-rid="re0000000239"]').evaluate("e=>e.scrollIntoView({block:'center',behavior:'instant'})")
                    zoom_page.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
                    visible_box = zoom_page.locator('.path-step[data-rid="re0000000239"]').evaluate("e=>({top:e.getBoundingClientRect().top,bottom:e.getBoundingClientRect().bottom,height:innerHeight})")
                    check("native 200 percent complex card visible in actual viewport", visible_box["top"] >= 0 and
                          visible_box["bottom"] <= visible_box["height"], visible_box)
                    if screenshot_dir:
                        # Playwright's document clipping can return a blank image
                        # after scrolling a natively zoomed page. Capture the real
                        # Chromium surface instead, with no document-coordinate clip.
                        cdp = zoom_context.new_cdp_session(zoom_page)
                        capture = cdp.send("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False, "fromSurface": True})
                        (screenshot_dir / "atlas-zoom-200-cards-native-surface.png").write_bytes(base64.b64decode(capture["data"]))
                        cdp.detach()
                        evidence["native_zoom_card_screenshot_method"] = "Native Chromium surface, captureBeyondViewport=false, no document clip"
                    evidence["native_zoom_metrics"] = metrics
                finally:
                    zoom_context.close()
            check("no external resources or network attempts", not requests and page.evaluate("performance.getEntriesByType('resource').length") == 0)
            # A second existing Chromium distribution: core file:// compatibility
            # on Edge, with all 20 cards/nets and all 968 independent source IDs.
            edge_path = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
            if edge_path.is_file() and str(edge_path) != executable:
                edge = p.chromium.launch(headless=True, executable_path=str(edge_path))
                try:
                    edge_context = edge.new_context(offline=True, viewport={"width": 1600, "height": 1000})
                    edge_page = edge_context.new_page()
                    edge_page.on("pageerror", lambda error: errors.append(str(error)))
                    edge_page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
                    edge_page.on("request", lambda request: requests.append(request.url) if not request.url.startswith("file:") else None)
                    edge_page.goto(html_path.resolve().as_uri())
                    for pid, path in data["paths"].items():
                        edge_page.locator("#search").fill(pid)
                        edge_page.wait_for_function("q=>Atlas.getState().query===q", arg=pid)
                        edge_page.locator(f'[data-action="path"][data-path="{pid}"]').click()
                        require(json.loads(edge_page.locator("#net-equation").get_attribute("data-net-vector")) == net(path["reaction_ids"], source), "Edge net " + pid)
                        presentation_cards(edge_page, path)
                    check("Edge all 20 paths and 94 exact cards offline", True)
                    edge_page.locator("#search").fill("GlyRS-P01")
                    edge_page.wait_for_function("()=>Atlas.getState().query==='GlyRS-P01'")
                    edge_page.locator('[data-action="path"][data-path="GlyRS-P01"]').click()
                    for rid in ("re0000000126", "re0000000131", "re0000000197", "re0000000198"):
                        edge_page.locator(f'.path-step .card-top [data-rid="{rid}"]').click()
                        require(edge_page.locator("#inspector-rid").inner_text() == rid and
                                edge_page.locator("#inspector-equation").inner_text() == data["reactions"][rid]["equation"], "Edge independent direction inspector " + rid)
                    check("Edge independent direction inspector links", True)
                    edge_page.locator("#positive-only").check()
                    edge_page.locator('.path-step[data-rid="re0000000197"] .competition-button').click()
                    check("Edge five parallel exits including disabled 0214", edge_page.locator(".branch-outlet").count() == 5 and
                          "REFERENCE_DISABLED" in edge_page.locator('[data-outgoing-rid="re0000000214"]').inner_text())
                    edge_page.locator('[data-action="close-state"]').click()
                    edge_page.locator("#positive-only").uncheck()
                    edge_page.locator('[data-action="all-source"]').click()
                    edge_ids = []
                    while True:
                        ids = edge_page.locator(".reaction-list .reaction-card").evaluate_all("xs=>xs.map(e=>e.dataset.reactionCard)")
                        for rid in ids:
                            edge_page.locator(f'.reaction-list [data-rid="{rid}"]').click()
                            require(edge_page.locator("#inspector-equation").inner_text() == data["reactions"][rid]["equation"], "Edge source equation " + rid)
                        edge_ids.extend(ids)
                        button = edge_page.locator('.pager [data-delta="1"]')
                        if button.is_disabled():
                            break
                        button.click()
                    check("Edge all 968 original directed reactions independently accessible", len(edge_ids) == 968 and set(edge_ids) == set(source))
                    check("Edge offline has no resource requests", edge_page.evaluate("performance.getEntriesByType('resource').length") == 0)
                    evidence["edge_compatibility"] = {"status": "PASS", "browser_version": edge.version,
                        "executable": str(edge_path), "paths": 20, "step_cards": 94, "source_inspector_clicks": 968,
                        "scope": "Core file URL, cards, nets, direction links, branches, filtering and full source index"}
                finally:
                    edge.close()
            else:
                evidence["edge_compatibility"] = {"status": "NOT_RUN", "reason": "No second Edge binary available"}
            check("no blocking browser console exceptions", not errors and not console_errors, {"page_errors": errors, "console_errors": console_errors})
            evidence["resource_entries"] = page.evaluate("performance.getEntriesByType('resource').length")
            evidence["screenshot_directory"] = str(screenshot_dir) if screenshot_dir else None
            evidence["unexecuted_required_browser_checks"] = []
            evidence["zoom_method"] = "Native Chromium Settings / Page zoom / 200%, disposable profile"
            evidence["status"] = "PASS"
        except Exception:
            evidence["failure_traceback"] = traceback.format_exc()
            evidence["status"] = "FAIL"
            if screenshot_dir:
                shot("atlas-failed-browser-check")
        finally:
            browser.close()
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=OUT / "reaction_atlas_prototype.html")
    parser.add_argument("--report", type=Path, default=OUT / "reaction_atlas_html_test_report.json")
    parser.add_argument("--screenshot-dir", type=Path)
    args = parser.parse_args()
    before = snapshot()
    report = {"schema_version": 1, "scope": "PHASE_A_PATHWAYS_ONLY", "phase_b": "PHASE_B_NOT_AUTHORIZED", "gates": []}
    data = extract(args.html.read_text(encoding="utf-8"))
    species, source, v2, parameters = read_sources()
    graph = json.loads((OUT / "glyrs_metrs_graph.json").read_text(encoding="utf-8"))
    for name, operation in (("A", lambda: gate_a(data, species, source, v2, parameters)),
                            ("B", lambda: gate_b(data, graph)), ("C", lambda: gate_c(data, source, parameters)),
                            ("D", lambda: gate_d(data, source))):
        try:
            report["gates"].append({"gate": name, "status": "PASS", "evidence": operation()})
        except Exception:
            report["gates"].append({"gate": name, "status": "FAIL", "traceback": traceback.format_exc()})
    for name, operation in (("phase_a_regression", old_regression), ("reproducibility", lambda: rebuild(args.html)),
                            ("presentation_data_integrity", lambda: previous_version_integrity(data))):
        try:
            report[name] = operation()
        except Exception:
            report[name] = {"status": "FAIL", "traceback": traceback.format_exc()}
    try:
        evidence = run_browser(args.html, data, source, args.screenshot_dir)
        report["gates"].append({"gate": "E", "status": evidence["status"], "evidence": evidence,
                                **({"traceback": evidence["failure_traceback"]} if evidence["status"] == "FAIL" else {})})
    except (ImportError, FileNotFoundError):
        report["gates"].append({"gate": "E", "status": "NOT_RUN", "traceback": traceback.format_exc()})
    except Exception:
        report["gates"].append({"gate": "E", "status": "FAIL", "traceback": traceback.format_exc()})
    after = snapshot()
    changed = sorted(n for n in set(before) | set(after) if before.get(n) != after.get(n))
    report["preservation"] = {"status": "PASS" if not changed else "FAIL", "protected_tracked_files": len(before), "changed_files": changed,
                              "phase_a_inputs_byte_unchanged": all(before.get("docs/reduction/pathways/" + n) == v for n, v in data["metadata"]["phase_a_inputs"].items())}
    passed = all(g["status"] == "PASS" for g in report["gates"]) and all(report[n]["status"] == "PASS" for n in ("phase_a_regression", "reproducibility", "preservation", "presentation_data_integrity"))
    report["acceptance_status"] = "PASS" if passed else "FAIL"
    report["scientific_status"] = "HTML_PROTOTYPE_READY_FOR_HUMAN_REVIEW" if passed else "HTML_PROTOTYPE_NOT_ACCEPTED"
    args.report.write_bytes((json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    if not passed:
        failure = {"recorded_at_utc": datetime.now(timezone.utc).isoformat(), "report": report}
        with (OUT / "reaction_atlas_html_failures.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(failure, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps({"acceptance_status": report["acceptance_status"], "gates": [{"gate": g["gate"], "status": g["status"], **({"traceback": g["traceback"]} if "traceback" in g else {})} for g in report["gates"]],
                      "phase_a_regression": report["phase_a_regression"]["status"], "reproducibility": report["reproducibility"], "preservation": report["preservation"]}, indent=2, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
