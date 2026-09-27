#!/usr/bin/env python3
"""Extract the author's 968 per-reaction rate expressions verbatim.

The author MATLAB file (models/pnas2017_full_reference/original/simulate/
Simulate_fMGG_synthesis/fMGG_synthesis.m) assembles every derivative from a
local vector `react(1:968)`, where each line is a pure monomial
`param(i) * state(a) * state(b) ...` and comment blocks map
`react(i) -> reXXXXXXXX`, `param(i) -> reXXXXXXXX_k1`, `state(k) -> name`.

This script copies those lines VERBATIM into a standalone function
`pnas2017_aa_v1_rates.m` so the formal runner can integrate cumulative
reaction extents WITHOUT any reimplementation of the science, and verifies
the extraction against the independent SBML-derived audit CSVs:

  * react(i) id mapping is monotone re0000000001..re0000000968;
  * every line uses exactly param(i) (its own k1) as coefficient;
  * the multiset of state(k) factors equals the reactant multiset of that
    reaction in audit/reactions.csv (via state-name mapping);
  * the rate_law string in audit/reactions.csv is the same monomial.

It never writes to the original file. Outputs:
  scripts/pnas2017_aa_v1_rates.m                       (generated, verbatim)
  models/pnas2017_full_reference/audit/
      aminoacylation_v1_rates_manifest.json            (extraction evidence)
"""
import csv
import hashlib
import json
import os
import re
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "models", "pnas2017_full_reference", "original",
                   "simulate", "Simulate_fMGG_synthesis", "fMGG_synthesis.m")
AUDIT = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")
OUT_M = os.path.join(ROOT, "scripts", "pnas2017_aa_v1_rates.m")
OUT_MANIFEST = os.path.join(AUDIT, "aminoacylation_v1_rates_manifest.json")

LINE_RE = re.compile(r"^react\((\d+)\) = ([^;]+);$")
MONO_RE = re.compile(r"^param\((\d+)\)((?: \* state\(\d+\))*)$")
STATE_CMT = re.compile(r"^% state\((\d+)\): (.+)$")
REACT_CMT = re.compile(r"^% react\((\d+)\): (re\d+)$")
PARAM_CMT = re.compile(r"^% param\((\d+)\): (\S+)$")


def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_side(s):
    out = []
    for tok in (s or "").split("|"):
        tok = tok.strip()
        if not tok:
            continue
        spec, stoich = tok.rsplit(":", 1)
        out.extend([spec] * int(float(stoich)))
    return sorted(out)


def main():
    txt = open(SRC, encoding="utf-8", errors="replace").read()
    lines = txt.splitlines()
    src_sha = hashlib.sha256(open(SRC, "rb").read()).hexdigest()

    state_names, react_ids, param_names = {}, {}, {}
    for ln in lines:
        m = STATE_CMT.match(ln)
        if m:
            state_names[int(m.group(1))] = m.group(2).strip()
            continue
        m = REACT_CMT.match(ln)
        if m:
            react_ids[int(m.group(1))] = m.group(2)
            continue
        m = PARAM_CMT.match(ln)
        if m:
            param_names[int(m.group(1))] = m.group(2)

    react_lines = []
    for i, ln in enumerate(lines, 1):
        m = LINE_RE.match(ln.strip())
        if m:
            react_lines.append((i, ln.rstrip()))
    problems = []
    if len(react_lines) != 968:
        problems.append("found %d react assignment lines, expected 968" % len(react_lines))

    # independent SBML-derived source
    reactions = {r["id"]: r for r in load_rows(os.path.join(AUDIT, "reactions.csv"))}

    extracted = []
    for lineno, ln in react_lines:
        body = ln.strip()
        m = LINE_RE.match(body)
        idx = int(m.group(1))
        expr = m.group(2).strip()
        mm = MONO_RE.match(expr)
        rid = react_ids.get(idx)
        if not mm:
            problems.append("react(%d) not a pure param*state monomial: %r" % (idx, expr))
            continue
        pidx = int(mm.group(1))
        sidx = [int(s) for s in re.findall(r"state\((\d+)\)", mm.group(2))]
        states = [state_names.get(k, "?%d" % k) for k in sidx]
        if pidx != idx:
            problems.append("react(%d) uses param(%d)" % (idx, pidx))
        pname = param_names.get(pidx, "")
        if pname != rid + "_k1":
            problems.append("param(%d)=%s does not match react id %s" % (pidx, pname, rid))
        r = reactions.get(rid)
        if r is None:
            problems.append("reaction %s absent from audit/reactions.csv" % rid)
            continue
        sbml_reactants = parse_side(r["reactants"])
        if sorted(states) != sbml_reactants:
            problems.append("react(%d)=%s states %s != SBML reactants %s"
                            % (idx, rid, states, sbml_reactants))
        expected_law = sorted(["k1"] + sbml_reactants)
        law = sorted(r["rate_law"].replace(" ", "").split("*"))
        if law != expected_law:
            problems.append("rate_law %s: %r != constructed %r" % (rid, law, expected_law))
        extracted.append(dict(index=idx, reaction_id=rid, states=states,
                              line=body, source_line=lineno))

    check("extraction_verified_against_sbml_audit", not problems, problems[:5])
    check("state_count", len(state_names) == 241)
    check("param_count", len([k for k, v in param_names.items() if v.endswith("_k1")]) == 968)

    # write the verbatim .m function
    span = (extracted[0]["source_line"], extracted[-1]["source_line"])
    with open(OUT_M, "w", newline="\n") as f:
        f.write("function [react] = pnas2017_aa_v1_rates(state, param)\n")
        f.write("%% GENERATED by scripts/generate_pnas2017_aa_v1_rates.py -- DO NOT EDIT.\n")
        f.write("%% Verbatim extract of the react(1:968) monomial block (source lines %d-%d)\n" % span)
        f.write("%% of models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/\n")
        f.write("%%   fMGG_synthesis.m (SHA-256 %s).\n" % src_sha)
        f.write("%% Each line is character-identical to the author source; indices map\n")
        f.write("%% react(i) -> reaction id per models/pnas2017_full_reference/audit/\n")
        f.write("%%   aminoacylation_v1_rates_manifest.json.\n")
        f.write("%%\n%% react index -> reaction id mapping (comments, from the author file):\n")
        for e in extracted:
            f.write("%% react(%d): %s\n" % (e["index"], e["reaction_id"]))
        f.write("\n")
        f.write("    react = zeros(968,1);\n")
        for e in extracted:
            f.write("    %s\n" % e["line"])
        f.write("end\n")

    manifest = OrderedDict([
        ("schema", "pnas2017_aa_v1_rates_manifest/v1"),
        ("source_file", os.path.relpath(SRC, ROOT).replace("\\", "/")),
        ("source_sha256", src_sha),
        ("react_block_source_lines", list(span)),
        ("n_reactions_extracted", len(extracted)),
        ("verification", OrderedDict([
            ("against", "models/pnas2017_full_reference/audit/reactions.csv (SBML-derived)"),
            ("checks", ["monomial form param(i)*prod(state)", "param(i)==react_id_k1",
                        "state multiset == SBML reactants", "rate_law string == k1*reactants"]),
            ("all_passed", not problems),
        ])),
        ("reaction_id_by_index", OrderedDict((str(e["index"]), e["reaction_id"]) for e in extracted)),
        ("state_index_to_species", OrderedDict((str(k), v) for k, v in sorted(state_names.items()))),
    ])
    with open(OUT_MANIFEST, "w", newline="\n") as f:
        json.dump(manifest, f, indent=2)
    print("wrote %s (%d lines) and manifest" % (os.path.relpath(OUT_M, ROOT), len(extracted) + 3))
    return 1 if problems else 0


fails = []


def check(name, cond, detail=""):
    if cond:
        print("PASS  %s %s" % (name, ""))
    else:
        fails.append(name)
        print("FAIL  %s %s" % (name, detail))


if __name__ == "__main__":
    import sys
    rc = main()
    sys.exit(1 if (rc or fails) else 0)
