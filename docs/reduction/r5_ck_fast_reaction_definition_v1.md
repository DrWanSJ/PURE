# CK declared fast reactions

Exactly re0000000332/333: CK+CP ⇌ CK_CP; re0000000336/337: CK_ADP+CP ⇌ CK_CP_ADP. Canonical table, SBML and author CSV agree: k_on=2, k_off=1000 for each pair. K0=K1=500 in reference concentration scale. All 14 other touching reactions are listed in reaction_definition.csv and retained as slow forcing. Original module IDs, rate laws, stoichiometry and hashes are in that table.

Author CSV omits units; docs/pnas2017/chemical_ledger.md supports µM inference from 50mM CP ↔ 50000. docs/pnas2017/sbml_audit.md documents incomplete metadata. Numerical time uses repository seconds convention. These interpretations do not repair the absolute biochemical unit audit.
