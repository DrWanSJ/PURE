#!/usr/bin/env python3
"""Inventory the PNAS 2017 (Matsuura et al.) combined SBML reference model.

This is a STRUCTURAL audit only: it reads the SBML and the authors' simulation
export CSVs and writes machine-readable inventories WITHOUT modifying the
scientific model or interpreting it. It does not run libSBML's consistency
checker (libSBML is not installed in this environment); see
docs/pnas2017/sbml_audit.md for what was and was not validated.

Inputs (immutable originals):
  models/pnas2017_full_reference/original/fMGG_synthesis.xml            (combined SBML)
  models/pnas2017_full_reference/original/subsystems/*.xml             (26 subsystem SBMLs)
  models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/*.csv

Outputs:
  models/pnas2017_full_reference/audit/{species,reactions,parameters,modules}.csv
  models/pnas2017_full_reference/audit/inventory_summary.json
"""
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict, Counter

SBML_NS = "http://www.sbml.org/sbml/level2/version4"
MATH_NS = "http://www.w3.org/1998/Math/MathML"
NS = {"s": SBML_NS, "m": MATH_NS}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(ROOT, "models", "pnas2017_full_reference", "original")
COMBINED = os.path.join(ORIG, "fMGG_synthesis.xml")
SUBSYS_DIR = os.path.join(ORIG, "subsystems")
SIMDAT = os.path.join(ORIG, "simulate", "Simulate_fMGG_synthesis", "dat")
AUDIT = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")


def local(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def math_to_text(el):
    """Render a MathML subtree to a flat infix string (best-effort, for audit)."""
    if el is None:
        return ""
    t = local(el.tag)
    if t == "ci":
        return (el.text or "").strip()
    if t == "cn":
        return (el.text or "").strip()
    if t == "apply":
        kids = [c for c in el if local(c.tag) not in ("annotation",)]
        if not kids:
            return ""
        op = local(kids[0].tag)
        args = [math_to_text(k) for k in kids[1:]]
        if op == "times":
            return " * ".join(a for a in args if a != "")
        if op == "plus":
            return " + ".join(a for a in args if a != "")
        if op == "minus":
            return " - ".join(args)
        if op == "divide":
            return " / ".join(args)
        return "%s(%s)" % (op, ", ".join(args))
    kids = [math_to_text(c) for c in el if local(c.tag) in ("apply", "ci", "cn")]
    return kids[0] if len(kids) == 1 else " ".join(kids)


def reaction_signature(rx):
    """Content signature of a reaction: (sorted reactants, sorted products).

    Each entry is (species_id, stoichiometry_string). Used to match subsystem
    reactions (local ids) to combined-model reactions (global ids)."""
    def side(name):
        node = rx.find("s:" + name, NS)
        out = []
        if node is not None:
            for sr in node.findall("s:speciesReference", NS):
                sm = sr.find("s:stoichiometryMath/s:math/*", NS)
                st = (sm.text or "1").strip() if sm is not None \
                    else sr.get("stoichiometry", "1")
                out.append((sr.get("species"), st))
        return tuple(sorted(out))
    return (side("listOfReactants"), side("listOfProducts"))


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main():
    os.makedirs(AUDIT, exist_ok=True)

    tree = ET.parse(COMBINED)
    model = tree.getroot().find("s:model", NS)
    sbml_level = tree.getroot().get("level")
    sbml_version = tree.getroot().get("version")

    # --- compartments ---
    comps = model.find("s:listOfCompartments", NS)
    comp_rows = comps.findall("s:compartment", NS) if comps is not None else []

    # --- species ---
    sp_list = model.find("s:listOfSpecies", NS)
    species = sp_list.findall("s:species", NS)
    # real initial values from authors' export
    init_csv = {}
    ip = os.path.join(SIMDAT, "fMGG_synthesis_initial_values.csv")
    for r in read_csv_rows(ip):
        init_csv[r["Name"]] = r["Value"]

    species_rows = []
    for s in species:
        sid = s.get("id")
        species_rows.append(OrderedDict([
            ("id", sid),
            ("name", s.get("name", "")),
            ("compartment", s.get("compartment", "")),
            ("sbml_initial_concentration", s.get("initialConcentration", "")),
            ("sbml_initial_amount", s.get("initialAmount", "")),
            ("boundary_condition", s.get("boundaryCondition", "false")),
            ("constant", s.get("constant", "false")),
            ("has_annotations", str(s.find("s:annotation", NS) is not None).lower()),
            ("author_export_initial_value", init_csv.get(sid, "")),
        ]))
    species_ids = {s.get("id") for s in species}

    # --- reactions (parse first so subsystems can be mapped by content) ---
    rx_list = model.find("s:listOfReactions", NS)
    reactions = rx_list.findall("s:reaction", NS)

    # --- subsystem module membership (Level B: 26 original subsystems) ---
    # Subsystem files use local reaction ids (re1, re12, ...) that do NOT match
    # the combined model's (re0000000001). Species ids ARE shared, so reactions
    # are matched back to the combined model by (reactants, products) content
    # signature. The combined model's 968 signatures are unique (verified).
    sig_to_combined = defaultdict_set()
    for rx in reactions:
        sig_to_combined[reaction_signature(rx)].add(rx.get("id"))
    reaction_modules = defaultdict_set()
    module_files = {}
    unmatched_subsystem_rx = 0
    for fn in sorted(os.listdir(SUBSYS_DIR)):
        if not fn.endswith(".xml"):
            continue
        m = re.match(r"(.+?)_[A-Za-z0-9]+\.xml$", fn)
        broad = m.group(1) if m else fn
        st = ET.parse(os.path.join(SUBSYS_DIR, fn))
        smodel = st.getroot().find("s:model", NS)
        rl = smodel.find("s:listOfReactions", NS)
        sub_rxs = rl.findall("s:reaction", NS) if rl is not None else []
        combined_ids = set()
        for srx in sub_rxs:
            for cid in sig_to_combined.get(reaction_signature(srx), set()):
                combined_ids.add(cid)
                reaction_modules[cid].add(fn[:-4])
            if not sig_to_combined.get(reaction_signature(srx), set()):
                unmatched_subsystem_rx += 1
        module_files[fn[:-4]] = {
            "broad_module": broad,
            "n_reactions": len(sub_rxs),
            "n_reactions_mapped_to_combined": len(combined_ids),
        }

    param_csv = {}
    pp = os.path.join(SIMDAT, "fMGG_synthesis_parameters.csv")
    for r in read_csv_rows(pp):
        param_csv[r["Name"]] = r["Value"]

    reaction_rows = []
    parameter_rows = []
    rev_counter = Counter()
    for rx in reactions:
        rid = rx.get("id")
        rev = rx.get("reversible", "")
        fast = rx.get("fast", "")
        rev_counter[(rev, fast)] += 1

        def side_items(side):
            out = []
            node = rx.find("s:" + side, NS)
            if node is None:
                return out
            for sr in node.findall("s:speciesReference", NS):
                spec = sr.get("species")
                stoich = ""
                sm = sr.find("s:stoichiometryMath", NS)
                if sm is not None:
                    stoich = math_to_text(sm.find("m:math/*", NS))
                else:
                    stoich = sr.get("stoichiometry", "")
                out.append((spec, stoich.strip()))
            return out

        ritems = side_items("listOfReactants")
        pitems = side_items("listOfProducts")
        kl = rx.find("s:kineticLaw", NS)
        rate = ""
        local_params = []
        if kl is not None:
            rate = math_to_text(kl.find("m:math", NS))
            lp = kl.find("s:listOfParameters", NS)
            if lp is not None:
                for p in lp.findall("s:parameter", NS):
                    pid = p.get("id")
                    sbml_val = p.get("value", "")
                    csv_val = param_csv.get("%s_%s" % (rid, pid), "")
                    local_params.append(pid)
                    parameter_rows.append(OrderedDict([
                        ("reaction_id", rid),
                        ("parameter_id", pid),
                        ("parameter_name", p.get("name", "")),
                        ("sbml_value", sbml_val),
                        ("sbml_units", p.get("units", "")),
                        ("sbml_constant", p.get("constant", "")),
                        ("author_export_value", csv_val),
                        ("value_is_placeholder",
                         str(sbml_val == "1" and csv_val not in ("1", "")).lower()),
                    ]))
        reaction_rows.append(OrderedDict([
            ("id", rid),
            ("name", rx.get("name", "")),
            ("reversible", rev),
            ("fast", fast),
            ("subsystem_files", "|".join(sorted(reaction_modules.get(rid, set())))),
            ("n_reactants", len(ritems)),
            ("n_products", len(pitems)),
            ("reactants", "|".join("%s:%s" % (a, b) for a, b in ritems)),
            ("products", "|".join("%s:%s" % (a, b) for a, b in pitems)),
            ("n_kinetic_params", len(local_params)),
            ("kinetic_param_ids", "|".join(local_params)),
            ("rate_law", rate),
            ("metaid", kl.get("metaid", "") if kl is not None else ""),
        ]))

    # global (model-level) parameters, rules, events, unit defs
    glp = model.find("s:listOfParameters", NS)
    n_global_params = len(glp.findall("s:parameter", NS)) if glp is not None else 0
    n_rules = len(model.find("s:listOfRules", NS).findall("*", NS)) \
        if model.find("s:listOfRules", NS) is not None else 0
    n_events = len(model.find("s:listOfEvents", NS).findall("*", NS)) \
        if model.find("s:listOfEvents", NS) is not None else 0
    n_unitdefs = len(model.find("s:listOfUnitDefinitions", NS).findall("*", NS)) \
        if model.find("s:listOfUnitDefinitions", NS) is not None else 0

    # module-level kinetic families
    fam_counter = Counter()
    for row in reaction_rows:
        fam = classify_family(row)
        fam_counter[fam] += 1

    # --- write CSVs ---
    write_csv(os.path.join(AUDIT, "species.csv"), species_rows)
    write_csv(os.path.join(AUDIT, "reactions.csv"), reaction_rows)
    write_csv(os.path.join(AUDIT, "parameters.csv"), parameter_rows)

    mod_rows = []
    for label in sorted(module_files):
        info = module_files[label]
        mod_rows.append(OrderedDict([
            ("subsystem_id", label),
            ("broad_module", info["broad_module"]),
            ("n_reactions", info["n_reactions"]),
        ]))
    write_csv(os.path.join(AUDIT, "modules.csv"), mod_rows)

    summary = OrderedDict([
        ("source_file", os.path.relpath(COMBINED, ROOT).replace("\\", "/")),
        ("sbml_level", sbml_level),
        ("sbml_version", sbml_version),
        ("model_id", model.get("id", "")),
        ("compartment_count", len(comp_rows)),
        ("species_count", len(species)),
        ("reaction_count", len(reactions)),
        ("reaction_local_parameter_count", len(parameter_rows)),
        ("global_parameter_count", n_global_params),
        ("rule_count", n_rules),
        ("event_count", n_events),
        ("unit_definition_count", n_unitdefs),
        ("subsystem_file_count", len(module_files)),
        ("reversible_fast_attribute_counts",
         {"|".join(k): v for k, v in rev_counter.items()}),
        ("reactions_mapped_to_a_subsystem",
         sum(1 for r in reaction_rows if r["subsystem_files"])),
        ("reactions_not_mapped_to_any_subsystem",
         sum(1 for r in reaction_rows if not r["subsystem_files"])),
        ("subsystem_reactions_unmatched_to_combined", unmatched_subsystem_rx),
        ("sbml_parameter_values_are_placeholders",
         sum(1 for p in parameter_rows if p["value_is_placeholder"] == "true")),
        ("kinetic_family_candidates", dict(fam_counter)),
        ("libsbml_validation", "NOT_RUN: libsbml not installed in environment"),
        ("roadrunner_import", "NOT_RUN: libroadrunner not installed in environment"),
    ])
    with open(os.path.join(AUDIT, "inventory_summary.json"), "w",
              encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print("\nWrote audit CSVs to", AUDIT)


def classify_family(row):
    """Coarse, purely structural rate-law shape classifier (candidate only)."""
    rate = row["rate_law"]
    parts = [p.strip() for p in rate.split("*")] if rate else []
    n_ci_species = sum(1 for p in parts)
    nr, npd = row["n_reactants"], row["n_products"]
    if not rate:
        return "unknown"
    if "*" not in rate:
        return "constant_or_single_term"
    if nr == 1 and len(parts) == 2:
        return "unimolecular_mass_action"
    if nr == 2 and len(parts) == 3:
        return "bimolecular_mass_action"
    if len(parts) >= 4:
        return "higher_order_mass_action"
    return "other"


class defaultdict_set(dict):
    def __missing__(self, key):
        self[key] = s = set()
        return s


def write_csv(path, rows):
    if not rows:
        open(path, "w").close()
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
