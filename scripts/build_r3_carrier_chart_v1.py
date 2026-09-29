#!/usr/bin/env python3
"""Certify an exact six-carrier coordinate transform for the R3 fast set."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction

import sympy as sp

from verify_reduction_audit_v0 import OUT, ROOT, SOURCE, rows, source_network

PARTITION = ROOT / "docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition.json"
R1_CHART = OUT / "source_coordinate_certificate_v4.json"
OUTPUT = OUT / "r3_carrier_chart_v1.json"
CARRIERS = ["GlyRS", "MetRS", "tRNAGlyGCC", "tRNAfMetCAU", "Gly", "Met"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational(value):
    return sp.Rational(str(value))


def build():
    species, _, initial = source_network()
    index = {name: i for i, name in enumerate(species)}
    historical = json.loads(PARTITION.read_text(encoding="utf-8"))
    fast = historical["eliminated_complexes"]
    assert len(fast) == 21 and len(CARRIERS) == 6
    assert not set(fast) & set(CARRIERS)
    r1 = json.loads(R1_CHART.read_text(encoding="utf-8"))
    assert set(fast + CARRIERS) <= set(r1["retained_species"])
    source_laws = [law for law in rows(OUT / "conservation_laws_v0.csv")
                   if law["scope"] == "SOURCE_GENERAL"]
    assert len(source_laws) == 27
    coefficients = [json.loads(law["species_coefficients_json"]) for law in source_laws]
    carrier_matrix = sp.Matrix([[rational(law.get(name, 0)) for name in CARRIERS]
                                for law in coefficients])
    fast_matrix = sp.Matrix([[rational(law.get(name, 0)) for name in fast]
                             for law in coefficients])
    assert carrier_matrix.rank() == fast_matrix.rank() == 6
    assert carrier_matrix.row_join(fast_matrix).rank() == 6
    pivot_rows = list(carrier_matrix.T.rref()[1])
    assert len(pivot_rows) == 6
    chart = carrier_matrix[pivot_rows, :].inv() * -fast_matrix[pivot_rows, :]
    assert carrier_matrix * chart + fast_matrix == sp.zeros(27, 21)

    # At fixed transformed slow carriers z_c = x_c - C*q, an arbitrary
    # feasible q change is compensated by delta_x_c = C*delta_q.
    delta_q = sp.Matrix([sp.Rational(1, 100000) for _ in fast])
    delta_c = chart * delta_q
    assert carrier_matrix * delta_c + fast_matrix * delta_q == sp.zeros(27, 1)
    perturbed = {name: rational(initial[name]) + delta_c[i] for i, name in enumerate(CARRIERS)}
    assert all(value >= 0 for value in perturbed.values())

    # The same adjustment lies within the exact R1 retained-coordinate
    # tangent space. Therefore its 27 eliminated source coordinates do not
    # change, and the generic affine chart remains the exact base.
    delta_retained = {name: delta_c[i] for i, name in enumerate(CARRIERS)}
    delta_retained.update({name: delta_q[j] for j, name in enumerate(fast)})
    for row in r1["B_sparse_rows"]:
        assert sum((rational(value) * delta_retained.get(name, 0)
                    for name, value in row.items()), sp.Rational(0)) == 0
    certificate = {
        "schema_version": "1.0", "status": "EXACT_CARRIER_COORDINATE_CERTIFICATE_NOT_QSSA_VALIDATION",
        "canonical_sbml_sha256": sha(SOURCE),
        "conservation_laws_sha256": sha(OUT / "conservation_laws_v0.csv"),
        "r1_source_chart_sha256": sha(R1_CHART),
        "historical_candidate_partition_sha256": sha(PARTITION),
        "source_general_law_ids": [law["conservation_id"] for law in source_laws],
        "carrier_species": CARRIERS, "candidate_fast_species": fast,
        "carrier_law_rank": int(carrier_matrix.rank()),
        "fast_law_rank": int(fast_matrix.rank()),
        "joint_law_rank": int(carrier_matrix.row_join(fast_matrix).rank()),
        "pivot_law_ids": [source_laws[i]["conservation_id"] for i in pivot_rows],
        "carrier_delta_per_fast_delta_rows": [
            {name: str(chart[i, j]) for j, name in enumerate(fast) if chart[i, j] != 0}
            for i in range(len(CARRIERS))],
        "slow_coordinate_definition": "z_carrier = x_carrier - C*q; x_carrier = z_carrier + C*q",
        "exact_identity": "L_carrier*C + L_fast = 0 over all 27 SOURCE_GENERAL laws",
        "r1_eliminated_delta_for_test": "0 for every eliminated source coordinate",
        "rational_test_delta_q": "1/100000 for every candidate fast species",
        "rational_test_carrier_values": {name: str(value) for name, value in perturbed.items()},
        "physical_test": "All 21 perturbed complexes and all six adjusted carriers remain nonnegative at author initial state; no clipping.",
        "scope": "Exact linear coordinate transform; fast algebraic closure and coupled numerical validity remain untested.",
    }
    return certificate


def main():
    certificate = build()
    OUTPUT.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("PASS: rank(L_q)=rank(L_carrier)=6; exact L_carrier*C+L_q=0 for 27 source-general laws")
    print("PASS: 21 candidate q and six carriers retained by R1 chart; exact eliminated-coordinate delta zero")
    print("PASS: rational small positive q perturbation preserves all source laws and physical carrier domain")


if __name__ == "__main__":
    main()
