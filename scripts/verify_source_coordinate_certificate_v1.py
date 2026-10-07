#!/usr/bin/env python3
"""Independently verify the source-general 241-to-214 and 241-to-224 certificates."""
from __future__ import annotations

import hashlib
import json

import sympy as sp

from verify_reduction_audit_v0 import OUT, SOURCE, columns, rows, source_network


def rational(value):
    return sp.Rational(str(value))


def check_certificate(cert, species, stoich, initial, law_by_id):
    assert cert["canonical_sbml_sha256"] == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert cert["conservation_laws_sha256"] == hashlib.sha256((OUT / "conservation_laws_v0.csv").read_bytes()).hexdigest()
    assert cert["species_contract_sha256"] == hashlib.sha256((OUT / "species_information_contract_detailed.md").read_bytes()).hexdigest()
    eliminated = cert["eliminated_species"]
    retained = cert["retained_species"]
    assert len(eliminated) == len(set(eliminated)) == len(cert["law_ids"])
    assert len(retained) == len(set(retained)) and set(eliminated).isdisjoint(retained)
    assert set(eliminated) | set(retained) == set(species)
    assert retained == [name for name in species if name not in eliminated]
    laws = [law_by_id[law_id] for law_id in cert["law_ids"]]
    assert all(law["scope"] == "SOURCE_GENERAL" for law in laws)
    coefficients = [json.loads(law["species_coefficients_json"]) for law in laws]
    L_E = sp.Matrix([[rational(co.get(name, 0)) for name in eliminated] for co in coefficients])
    L_R = sp.Matrix([[rational(co.get(name, 0)) for name in retained] for co in coefficients])
    A = sp.Matrix([[rational(value) for value in row] for row in cert["A_rows"]])
    B = sp.Matrix([[rational(row.get(name, 0)) for name in retained] for row in cert["B_sparse_rows"]])
    assert L_E.shape == A.shape == (len(laws), len(laws))
    assert B.shape == (len(eliminated), len(retained))
    assert L_E.det() != 0 and L_E * A == sp.eye(len(laws))
    assert L_E * B + L_R == sp.zeros(len(laws), len(retained))
    expected_b = sp.Matrix([sum(rational(co.get(name, 0)) * rational(initial[name]) for name in species)
                            for co in coefficients])
    assert [str(value) for value in expected_b] == cert["author_initial_b"]
    x_E = sp.Matrix([rational(initial[name]) for name in eliminated])
    x_R = sp.Matrix([rational(initial[name]) for name in retained])
    assert A * expected_b + B * x_R == x_E
    index = {name: i for i, name in enumerate(species)}
    for col in stoich:
        s_E = sp.Matrix([rational(col.get(index[name], 0)) for name in eliminated])
        s_R = sp.Matrix([rational(col.get(index[name], 0)) for name in retained])
        assert L_E * s_E + L_R * s_R == sp.zeros(len(laws), 1)
        assert B * s_R == s_E
    return True


def main():
    species, reactions, initial = source_network()
    stoich = columns(species, reactions)
    laws = rows(OUT / "conservation_laws_v0.csv")
    law_by_id = {law["conservation_id"]: law for law in laws}
    assert len(law_by_id) == len(laws)
    for name, expected in (("source_coordinate_certificate_17_v1.json", (17, 224)),
                           ("source_coordinate_certificate_v1.json", (27, 214)),
                           ("source_coordinate_certificate_v2.json", (27, 214)),
                           ("source_coordinate_certificate_v3.json", (27, 214)),
                           ("source_coordinate_certificate_v4.json", (27, 214)),
                           ("source_coordinate_certificate_v5.json", (27, 214)),
                           ("source_coordinate_certificate_v6.json", (27, 214)),
                           ("source_coordinate_certificate_v7.json", (27, 214))):
        cert = json.loads((OUT / name).read_text(encoding="utf-8"))
        assert (cert["eliminated_count"], cert["retained_count"]) == expected
        if name.endswith(("_v2.json", "_v3.json")):
            assert {"CK_degraded", "GlyAMP", "MetAMP"} <= set(cert["retained_species"])
        if name.endswith("_v4.json"):
            assert {"CK_degraded", "NDK_degraded", "GlyAMP", "MetAMP"} <= set(cert["retained_species"])
        if name.endswith("_v5.json"):
            assert {"CK_CP", "CK_degraded", "NDK_degraded", "GlyAMP", "MetAMP"} <= set(cert["retained_species"])
        if name.endswith(("_v6.json", "_v7.json")):
            assert {"CK_CP", "CK_degraded", "NDK_degraded", "GlyAMP", "MetAMP"} <= set(cert["retained_species"])
        check_certificate(cert, species, stoich, initial, law_by_id)
        print(f"PASS: {name}: exact affine map and 968 lifted columns")


if __name__ == "__main__":
    main()
