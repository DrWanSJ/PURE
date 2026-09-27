"""Render process-oriented, explicitly undecided reduction review from audit CSVs."""

from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "models/pnas2017_full_reference/audit"
RED = ROOT / "docs/reduction"
DOI = "10.1073/pnas.1615351114"
CARDS = (
    ("Amino-acid activation", ("Aminoacylation_A_Gly", "Aminoacylation_A_Met"),
     "GlyRS or MetRS binds amino acid and ATP and forms an aminoacyl-adenylate; PPi is released through explicit states.",
     "A net activation step could replace reversible binding and adenylate intermediates only with explicit ATP→AMP/PPi bookkeeping and a justified rate law.",
     "Aminoacyl-adenylate and synthetase occupancy, reverse fluxes, and the timing of PPi release would become unobservable without reconstruction."),
    ("tRNA aminoacylation", ("Aminoacylation_B_fMetCAU", "Aminoacylation_B_GlyGCC"),
     "The aminoacyl-adenylate transfers amino acid to a specific tRNA, recycles synthetase, and releases AMP through enzyme-bound intermediates.",
     "Binding and transfer steps might be lumped into a charging reaction that explicitly conserves each tRNA and releases AMP.",
     "Synthetase occupancy, bound tRNA, and free-versus-charged recycling times would be lost unless reconstructed and tested."),
    ("Initiator-tRNA formylation", ("FMet_tRNASynthesis",),
     "MTF transfers a formyl group from the donor system to initiator Met-tRNA, producing fMet-tRNA and donor product states.",
     "An effective formylation step may retain donor/product molecules and initiator-tRNA identity while collapsing MTF binding states.",
     "The MTF occupancy and donor-bound intermediates would no longer be direct observables; donor moiety balance must be resolved first."),
    ("Initiation factor preparation", ("Initiation_A",),
     "IF2 and its GTP/GDP states participate in preparation for 30S/70S initiation.",
     "A conditional factor-cycle aggregate could retain explicit GTP/GDP/Pi and free IF2 pools.",
     "IF2 nucleotide-state occupancy and exchange timing would be lost without a reconstruction rule."),
    ("Ribosome and mRNA initiation assembly", ("Initiation_B1", "Initiation_B2", "Initiation_C"),
     "30S, mRNA, fMet-tRNA, IF1/IF2/IF3 and 50S form successive initiation complexes, including GTP hydrolysis and factor release.",
     "Several binding paths might be represented by a smaller occupancy graph if their factor and nucleotide balances are retained.",
     "Order-of-binding paths, individual IF occupancy, preinitiation residence times, and some free/occupied ribosome fractions would become unrecoverable."),
    ("EF-Tu ternary-complex delivery", ("Elongation_A_Gly", "Elongation_A_Met"),
     "EF-Tu, EF-Ts, GTP/GDP and aminoacyl-tRNA assemble and recycle the ternary delivery complex.",
     "An effective delivery cycle could combine assembly/exchange while retaining GTP/GDP, charged tRNA and free EF-Tu/EF-Ts inventories.",
     "Ternary-complex occupancy, exchange pathway fluxes and delay to ribosome delivery would be lost."),
    ("EF-G nucleotide cycle", ("Elongation_B",),
     "EF-G associates with ribosomal states and GTP/GDP/Pi during the translocation cycle.",
     "Binding/release steps might be lumped around an explicit GTP-consuming translocation event.",
     "EF-G-bound ribosome occupancy and separate hydrolysis/product-release timing would be lost."),
    ("Peptidyl-tRNA and ribosome transitions", ("Elongation_Ca1_fMetCAU", "Elongation_Ca1_GlyGCC", "Elongation_Ca2_pept0002", "Elongation_Ca2_pept0003"),
     "The model advances sequence-specific peptidyl-tRNA and ribosome complexes through Gly addition and translocation toward fMGG.",
     "Some microscopic ribosome steps might be grouped by peptide length and occupancy while retaining amino-acid incorporation, tRNA return and GTP/Pi accounting.",
     "Pre/post-translocation occupancy, intermediate peptide species and individual tRNA release times would become unavailable."),
    ("RF1/RF2 peptide release", ("Termination_A_RF1", "Termination_A_RF2"),
     "Release factors bind the stop-codon complex and hydrolyze peptidyl-tRNA to release the fMGG peptide.",
     "RF1 and RF2 pathways might share a net release step only if branch-specific kinetics and factor usage are preserved or explicitly discarded.",
     "RF1-versus-RF2 occupancy, pathway-specific release kinetics and bound peptide states would be lost."),
    ("RF3-assisted termination", ("Termination_B_RF1", "Termination_B_RF2"),
     "RF3 and GTP/GDP states promote turnover of release-factor-bound posttermination complexes.",
     "An effective RF3 recycling step could preserve nucleotide consumption and factor availability.",
     "RF1/RF2/RF3 complex occupancy and GDP/Pi release timing would be lost."),
    ("Ribosome recycling", ("Termination_C",),
     "RRF and EF-G split/recycle posttermination ribosome and tRNA/mRNA complexes with explicit guanylate states.",
     "A reduced recycling path could retain 30S/50S/70S, free versus occupied pools, tRNA return and GTP→GDP/Pi.",
     "Posttermination residence times and RRF/EF-G occupancy would no longer be direct observables."),
    ("Creatine-kinase energy regeneration", ("EnergyRegeneration_A",),
     "CK exchanges phosphoryl groups between creatine phosphate/creatine and ADP/ATP through bound enzyme states.",
     "A reversible net CP + ADP ↔ Cr + ATP candidate could preserve these four explicit resources if supported by kinetics.",
     "CK occupancy and mechanistic forward/reverse rates would be lost; the ideal-particle effect and proton/Mg chemistry need separate review."),
    ("Nucleotide-diphosphate kinase exchange", ("EnergyRegeneration_B",),
     "NDK couples adenylate and guanylate carriers through nucleotide-bound enzyme states.",
     "A net ATP + GDP ↔ ADP + GTP candidate could retain both carrier pools.",
     "NDK occupancy and exchange intermediates would be lost; charge/Mg and reverse-flow assumptions remain unresolved."),
    ("Adenylate kinase exchange", ("EnergyRegeneration_C",),
     "MK interconverts adenylate carrier states with distinct bound-ADP intermediates.",
     "A net ATP + AMP ↔ 2 ADP candidate could retain the three free adenylate species.",
     "MK occupancy and its two ADP-bound configurations would be lost; adenylate moiety and particle checks are required."),
    ("Pyrophosphate hydrolysis", ("EnergyRegeneration_D",),
     "PPiase binds PPi and releases two `PO4` species; the source MathML coefficient of 2 must be preserved.",
     "A net PPi → 2 Pi step could collapse PPiase binding while keeping PPi/Pi and the +1 ideal-particle event change explicit.",
     "PPiase occupancy and hydrolysis delay would be lost. Any model that hides Pi production fails the resource requirement."),
    ("Shared small-molecule transitions", ("SmallMolecules",),
     "The source subsystem records small-molecule reactions shared with other process modules.",
     "A shared bookkeeping representation might avoid duplicate display edges, but chemical events must retain one unique combined-SBML ID.",
     "Any deletion would risk free-resource, phosphate and particle accounting; shared display membership is not duplicate chemistry."),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ids_for(reactions: list[dict[str, str]], modules: tuple[str, ...]) -> list[str]:
    requested = set(modules)
    return [row["sbml_reaction_id"] for row in reactions if requested.intersection(row["level_b_subsystem_candidates"].split(";"))]


def source_names(modules: list[dict[str, str]]) -> list[str]:
    return [Path(row["source_file"]).stem for row in modules]


def level_from_module(name: str) -> str:
    if name.startswith("Aminoacylation") or name.startswith("FMet"):
        return "aminoacylation"
    if name.startswith("Initiation"):
        return "initiation"
    if name.startswith("Elongation"):
        return "elongation"
    if name.startswith("Termination"):
        return "termination / ribosome recycling"
    if name.startswith("EnergyRegeneration") or name == "SmallMolecules":
        return "energy regeneration"
    return "UNKNOWN"


def main() -> None:
    module_path = AUDIT / "modules.csv"
    decision_path = RED / "reduction_decisions.csv"
    species_path = AUDIT / "species_properties.csv"
    balance_path = AUDIT / "reaction_balance_audit.csv"
    modules = read_csv(module_path)
    decisions = read_csv(decision_path)
    species = read_csv(species_path)
    balance = {row["sbml_reaction_id"]: row for row in read_csv(balance_path)}
    if len(modules) != 26 or len(decisions) != 968 or len(species) != 241 or len(balance) != 968:
        raise ValueError("Audit table cardinality changed")
    module_names = set(source_names(modules))
    if {m for _, mm, *_ in CARDS for m in mm} != module_names:
        raise ValueError("Process cards must cover all 26 original subsystem files exactly")
    by_id = {row["sbml_reaction_id"]: row for row in decisions}
    if len(by_id) != 968:
        raise ValueError("Duplicate combined reaction ID")
    covered = {rid for _, mm, *_ in CARDS for rid in ids_for(decisions, mm)}
    if covered != set(by_id):
        raise ValueError("Some combined reactions lack review-card coverage")
    label_counts = Counter(row["candidate_label"] for row in decisions)
    type_counts = Counter(row["cell_designer_reaction_type"] for row in decisions)
    unique_count = sum(row["module_mapping_status"] == "EXTRACTED_EXACT_STOICHIOMETRY" for row in decisions)
    ambiguous_count = sum(row["module_mapping_status"] == "AMBIGUOUS_MULTIPLE_SUBSYSTEMS" for row in decisions)
    if (unique_count, ambiguous_count) != (884, 84):
        raise ValueError("Combined-to-subsystem mapping changed")

    reduction = [
        "# PNAS 2017 reaction-family reduction map — candidate labels only",
        "",
        f"**Canonical source:** Matsuura et al., DOI `{DOI}`, unchanged combined SBML `fMGG_synthesis.xml`. This map is derived navigation, not a reduced model or a scientific acceptance decision. Every proposed non-KEEP row is `HUMAN_REVIEW_REQUIRED=true` and `decision_status=PENDING` in [`reduction_decisions.csv`](reduction_decisions.csv).",
        "",
        "## Coverage and interpretation",
        "",
        "- Level A: initiation; elongation; aminoacylation (including initiator formylation); termination/ribosome recycling; energy regeneration (including the shared SmallMolecules source card). Cross-process appearances are retained as multiple candidate memberships, not extra reactions.",
        "- Level B: all 26 original SBML subsystem files. They contain 1,098 reaction *entries*; after collapsing exact stoichiometric duplicates across diagrams, 968 unique signatures match all 968 combined-SBML reactions. Exactly 884 combined reactions map to one subsystem and 84 map to more than one. Original subsystem-local IDs are recorded beside the combined IDs in the CSV.",
        "- Level C: biochemical process plus original CellDesigner reaction type. Across the combined model: " + ", ".join(f"{key} {value}" for key, value in sorted(type_counts.items())) + ". Reaction types describe graph structure; they are not evidence of fast equilibrium or QSSA.",
        "- Candidate labels: " + ", ".join(f"{key} {value}" for key, value in sorted(label_counts.items())) + ". `DROP_CANDIDATE` is reserved here for degradation-related reactions whose official fMGG parameter is exactly zero; it is conditional on that reference condition and does not authorize deletion. `LUMP_CANDIDATE` marks nondegradation association/dissociation/state transitions without a direct free-resource delta. Resource/peptide steps are provisionally `KEEP`. No QSSA, fast-equilibrium or chemostat claim is made without time-scale, reconstruction and chemical-ledger evidence.",
        "- The original combined SBML stores one `PO4` product coefficient as MathML 2 in `re0000000414`; inventories use the effective value 2. The exact source mapping is `EnergyRegeneration_D.xml/re13`. Raw RoadRunner/SimBiology imports read it as 1, so use the separately verified compatibility copy for numerical work.",
        "",
        "## Original 26 subsystems",
        "",
        "| Level A | Original subsystem file / model ID | Source entries | Combined IDs in subsystem | Level C reaction types |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for module in modules:
        name = Path(module["source_file"]).stem
        rows = [by_id[rid] for rid in ids_for(decisions, (name,))]
        types = Counter(row["cell_designer_reaction_type"] for row in rows)
        level = level_from_module(name)
        reduction.append(f"| {level} | `{module['source_file']}` / `{module['source_model_id']}` | {module['reaction_entry_count']} | {len(rows)} | " + ", ".join(f"{kind} {count}" for kind, count in sorted(types.items())) + " |")
    reduction += [
        "",
        "## How to evaluate a transformation",
        "",
        "For each original combined reaction, the decision CSV exposes reactant/product IDs and stoichiometry, official author-CSV `k1`, suggested label and assumption, evidence gap, effects on free ATP/GTP/AMP/ADP/GDP, Pi/PPi, tRNA, ideal-particle proxy, unknown ionic contribution and observables that may be lost. The [`reaction_balance_audit.csv`](../../models/pnas2017_full_reference/audit/reaction_balance_audit.csv) retains the full event-level resource deltas. Formula, net charge, protonation and Mg-binding information remain unresolved, so neither elemental balance nor quantitative ionic strength can be certified.",
        "",
        "The candidate label is not a command to change the model. The human researcher must examine the [process review](human_reduction_review.md), supply validation data and approve or reject each scientific transformation. Similar peptide output cannot replace resource, occupancy, particle and moiety checks.",
        "",
    ]

    human = [
        "# Human reduction review — PNAS 2017 translation chemistry",
        "",
        "**All boxes are intentionally empty.** This document organizes the 968 combined-SBML reactions by biochemical process and original source subsystem. A reaction may appear in several process cards because the 26 source diagrams reuse chemistry; the combined model still has 968 unique reaction IDs. Every suggested transformation below is `HUMAN_REVIEW_REQUIRED`. The source SBML, author simulator CSVs, and row-level [`reduction_decisions.csv`](reduction_decisions.csv) are the evidence trail. No choice here is finalized or validated.",
        "",
        "For particle change, the numbers below count stoichiometric changes in the *represented species* per individual event; they are an ideal proxy, not osmotic pressure. Free ATP/GTP/Pi/PPi deltas do not include carrier moieties bound in complexes. Ionic consequences remain unknown because formula/charge/protonation/Mg metadata are absent.",
        "",
    ]
    for title, group_modules, chemistry, proposal, loss in CARDS:
        rows = [by_id[rid] for rid in ids_for(decisions, group_modules)]
        rids = [row["sbml_reaction_id"] for row in rows]
        involved = [row["sbml_id"] for row in species if set(group_modules).intersection(row["level_b_subsystem_candidates"].split(";"))]
        complexes = [row["sbml_id"] for row in species if row["sbml_id"] in involved and row["complex"] == "True"]
        resource_names = ("ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "PO4", "PPi", "CP", "Cr", "Gly", "Met", "fMet", "tRNAGlyGCC", "tRNAfMetCAU", "GlytRNAGlyGCC", "MettRNAfMetCAU", "fMettRNAfMetCAU")
        affected = [key for key in resource_names if any(float(balance[rid]["net_free_" + key]) != 0 for rid in rids)]
        particles = Counter("increase" if float(balance[rid]["net_tracked_particle_count_per_event"]) > 0 else "decrease" if float(balance[rid]["net_tracked_particle_count_per_event"]) < 0 else "unchanged" for rid in rids)
        examples = [row for row in rows if any(float(balance[row["sbml_reaction_id"]]["net_free_" + key]) != 0 for key in resource_names)][:2]
        if not examples:
            examples = rows[:2]
        human += [
            f"## {title}", "",
            f"**Chemical process.** {chemistry}", "",
            f"**Original implementation.** {len(rids)} unique combined reactions map to {', '.join('`' + x + '.xml`' for x in group_modules)}. Exact combined IDs are below; original module-local IDs are in the decision CSV.", "",
            f"**Intermediates.** {len(complexes)} candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.", "",
            f"**Explicit free resources.** Event-level changes occur for: {', '.join('`' + x + '`' for x in affected) if affected else 'none in the selected free-resource list'}. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.", "",
            f"**Particle number.** Among these event stoichiometries, {particles['increase']} increase, {particles['decrease']} decrease and {particles['unchanged']} leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.", "",
            "**Representative original reactions.**", "",
        ]
        for row in examples:
            rid = row["sbml_reaction_id"]
            b = balance[rid]
            left, right = json.loads(b["reactants_json"]), json.loads(b["products_json"])
            def side(items: dict[str, float]) -> str:
                return " + ".join((f"{v:g} " if v != 1 else "") + k for k, v in items.items()) or "∅"
            human.append(f"- `{rid}`: `{side(left)} → {side(right)}`; tracked-particle Δ = {float(b['net_tracked_particle_count_per_event']):g}.")
        human += [
            "", f"**Candidate lumping.** {proposal}", "",
            f"**Information lost if applied.** {loss} Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.", "",
            "**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.", "",
            "**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**", "",
            "- [ ] KEEP", "- [ ] LUMP", "- [ ] QSSA", "- [ ] CHEMOSTAT", "- [ ] DROP", "- [ ] NEED MORE INFORMATION", "",
            "<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>", "",
            "Original combined reaction IDs: " + ", ".join(f"`{rid}`" for rid in rids) + ".", "",
            "Candidate complex/intermediate IDs: " + (", ".join(f"`{sid}`" for sid in complexes) if complexes else "none classified") + ".", "",
            "</details>", "",
        ]
    human += [
        "## Review decision record", "",
        "For every approved transformation, create a versioned decision that cites original combined IDs, source/module IDs, exact equations, assumptions, domain, species/observable reconstruction rules, ATP/GTP/Pi/PPi/AMP/ADP/GDP/tRNA balances, particle and ionic coverage, numerical evidence and researcher/date. Until then `PURE_reduced_core` remains a proposal.", "",
    ]
    RED.mkdir(parents=True, exist_ok=True)
    out_map = RED / "reduction_map.md"
    out_review = RED / "human_reduction_review.md"
    # These reports are fingerprinted below. Write exact LF bytes on Windows
    # too, so Git and a fresh checkout preserve the same SHA-256 values.
    out_map.write_bytes("\n".join(reduction).encode("utf-8"))
    out_review.write_bytes("\n".join(human).encode("utf-8"))
    files = (module_path, decision_path, species_path, balance_path)
    manifest = {
        "status": "DERIVED_NAVIGATION_NOT_SOURCE_AUTHORITY",
        "generated_by": "scripts/render_pnas2017_review.py",
        "inputs_sha256": {p.relative_to(ROOT).as_posix(): digest(p) for p in files},
        "outputs_sha256": {p.relative_to(ROOT).as_posix(): digest(p) for p in (out_map, out_review)},
        "counts": {"original_subsystems": len(modules), "combined_reactions": len(decisions), "single_subsystem": unique_count, "shared_subsystems": ambiguous_count, "process_review_cards": len(CARDS)},
        "freshness_rule": "Regenerate when an input SHA changes; this report cannot replace frozen SBML source evidence.",
    }
    (RED / "review_render_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
