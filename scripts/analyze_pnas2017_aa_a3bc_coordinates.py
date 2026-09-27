"""A3b/A3c coordinate analysis (Phases 2-4, 6A, 7).

Builds the protected ledger basis L_protected mechanically from the audited
scope/binit rows, classifies every row against the full 968-reaction
stoichiometry, designs the A3b total-coordinate transformation T=[A;Q],
verifies rank(T)=241 and rowspace membership, runs the closure
affinity (q-degree) test, and builds the A3c eligibility table.

usage: python analyze_a3bc.py <ROOT> <OUT>
"""
import csv, json, sys, os
import numpy as np

ROOT = sys.argv[1] if len(sys.argv) > 1 else '../..'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'out'
CAND = sys.argv[3] if len(sys.argv) > 3 else 'a3b21'   # a3b21 | a3br12
OUTDIR = 'pnas2017_aminoacylation_A3b' if CAND == 'a3b21' else 'pnas2017_aminoacylation_A3b_r12'

# ---------------------------------------------------------------- inputs
def load_species():
    with open(f'{ROOT}/models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_initial_values.csv') as f:
        rows = list(csv.reader(f))
    names = [r[1] for r in rows[1:]]
    x0 = np.array([float(r[2]) for r in rows[1:]])
    assert len(names) == 241
    return names, x0

def load_params():
    with open(f'{ROOT}/models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv') as f:
        return {r[0]: float(r[1]) for r in list(csv.reader(f))[1:]}

def load_stoich(idx):
    S = np.zeros((241, 968), dtype=object)
    meta = {}
    with open(f'{ROOT}/models/pnas2017_full_reference/audit/reactions.csv') as f:
        for row in csv.DictReader(f):
            j = int(row['id'][2:]) - 1
            for side, sign in (('reactants', -1), ('products', +1)):
                if row[side]:
                    for term in row[side].split('|'):
                        sp, st = term.rsplit(':', 1)
                        S[idx[sp], j] += sign * int(st)
            meta[j] = {'subsystem': row['subsystem_files'],
                       'reactants': row['reactants'], 'products': row['products'],
                       'rate_law': row['rate_law']}
    return S, meta

names, x0 = load_species()
idx = {n: i for i, n in enumerate(names)}
params = load_params()
k1 = np.array([params[f're{i:010d}_k1'] for i in range(1, 969)])
active = k1 != 0
S, rmeta = load_stoich(idx)
print(f'active reactions (k1 != 0): {int(active.sum())} / 968', flush=True)

# ------------------------------------------------- protected ledger rows
scope = json.load(open(f'{ROOT}/models/pnas2017_full_reference/audit/aminoacylation_v1_comparison_scope.json'))
scope_cons = {g['id']: g for g in scope['conservation']}

binit_rows = {}
with open(f'{ROOT}/docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2_matrix.csv') as f:
    rd = csv.reader(f)
    hdr = next(rd)
    for row in rd:
        binit_rows[row[0]] = {hdr[i + 1]: int(float(v)) for i, v in enumerate(row[1:]) if float(v) != 0}

LEDGERS = {}
LEDGERS['MetRS_total'] = dict(weights={s: 1 for s in scope_cons['MetRS_moiety_total']['species']},
                              source='scope:MetRS_moiety_total')
LEDGERS['GlyRS_total'] = dict(weights={s: 1 for s in scope_cons['GlyRS_moiety_total']['species']},
                              source='scope:GlyRS_moiety_total')
LEDGERS['tRNAfMetCAU_total'] = dict(weights={s: 1 for s in scope_cons['tRNAfMetCAU_family_total']['species']},
                                    source='scope:tRNAfMetCAU_family_total')
LEDGERS['tRNAGlyGCC_total'] = dict(weights={s: 1 for s in scope_cons['tRNAGlyGCC_family_total']['species']},
                                   source='scope:tRNAGlyGCC_family_total')
aw = dict(scope_cons['adenine_ledger_total'].get('weights') or {})
for s in scope_cons['adenine_ledger_total']['species']:
    aw.setdefault(s, 1)
LEDGERS['adenine_ledger_total'] = dict(weights=aw, source='scope:adenine_ledger_total')
pw = dict(scope_cons['phosphate_ledger_total']['weights'])
for s in scope_cons['phosphate_ledger_total']['species']:
    pw.setdefault(s, 1)
LEDGERS['phosphate_ledger_total'] = dict(weights=pw, source='scope:phosphate_ledger_total')
LEDGERS['guanine_ledger_total'] = dict(weights={s: 1 for s in scope_cons['guanine_ledger_total']['species']},
                                       source='scope:guanine_ledger_total')
LEDGERS['Met_material_total'] = dict(weights=dict(binit_rows['Met_total']), source='binit:Met_total')
LEDGERS['Gly_material_total'] = dict(weights=dict(binit_rows['Gly_total']), source='binit:Gly_total')

# sanity: binit vs scope agreement for the family rows
for fam in ('tRNAfMetCAU', 'tRNAGlyGCC'):
    assert binit_rows[f'{fam}_total'] == {s: 1 for s in scope_cons[f'{fam}_family_total']['species']}

# ------------------------------------------------------------ Phase 3
def classify(name, weights):
    v = np.zeros(241, dtype=object)
    for sp, w in weights.items():
        v[idx[sp]] += w
    lv = v @ S
    viol_all = [j for j in range(968) if lv[j] != 0]
    viol_act = [j for j in viol_all if active[j]]
    vf = np.zeros(241)
    for sp, w in weights.items():
        vf[idx[sp]] = float(w)
    v0 = float(vf @ x0)
    return v, viol_all, viol_act, v0

classification = {}
for name, d in LEDGERS.items():
    v, va, vac, v0 = classify(name, d['weights'])
    if not va:
        cls = 'EXACT_GLOBAL_INVARIANT'
    elif not vac:
        cls = 'EXACT_ACTIVE_NETWORK_INVARIANT'
    elif name == 'adenine_ledger_total':
        cls = 'INTERFACE_BALANCE'   # violations confined to MK complex binding scope
    else:
        cls = 'RESOURCE_ACCOUNTING_ONLY'
    classification[name] = {
        'class': cls, 'nonzero_species': len(d['weights']),
        'violations_all': len(va), 'violations_active': len(vac),
        'violating_reactions_active': [f're{j+1:010d}' for j in vac],
        't0_value_uM': v0, 'source': d['source'],
    }
    print(f"{name:32s} {cls:35s} viol_all={len(va):3d} viol_active={len(vac):2d} t0={v0:.6g}", flush=True)

# ------------------------------------------- A3b candidate (Phase 4)
ELIM_21 = [
    "GlyRS_AMP_GlytRNAGlyGCC", "GlyRS_ATP", "GlyRS_ATP_tRNAGlyGCC", "GlyRS_Gly",
    "GlyRS_GlyAMP_PPi", "GlyRS_Gly_ATP", "GlyRS_Gly_ATP_tRNAGlyGCC",
    "GlyRS_Gly_tRNAGlyGCC", "GlyRS_tRNAGlyGCC", "MetRS_AMP",
    "MetRS_AMP_MettRNAfMetCAU", "MetRS_ATP", "MetRS_ATP_tRNAfMetCAU", "MetRS_Met",
    "MetRS_MetAMP_PPi", "MetRS_MetAMP_PPi_tRNAfMetCAU", "MetRS_MetAMP_tRNAfMetCAU",
    "MetRS_Met_ATP", "MetRS_Met_ATP_tRNAfMetCAU", "MetRS_Met_tRNAfMetCAU",
    "MetRS_tRNAfMetCAU",
]
assert all(e in idx for e in ELIM_21)

tRNA_bearing = [s_ for s_ in ELIM_21 if 'tRNA' in s_]

if CAND == 'a3b21':
    FAST_SET = list(ELIM_21)
    A3B_TOTAL_ROWS = [
        ('MetRS_total', 'MetRS'),
        ('GlyRS_total', 'GlyRS'),
        ('tRNAfMetCAU_total', 'tRNAfMetCAU'),
        ('tRNAGlyGCC_total', 'tRNAGlyGCC'),
        ('adenine_ledger_total', 'ATP'),
        ('phosphate_ledger_total', 'PPi'),
        ('Met_material_total', 'Met'),
        ('Gly_material_total', 'Gly'),
    ]
elif CAND == 'a3br12':
    # evidence-driven restricted fast set (Phase 6): the A3b-21 smoke
    # closure loses feasibility at t ~ 2.5 s (the v1r3 failure era); the
    # 12 tRNA-bearing complexes return to the dynamic state vector and
    # only the tRNA-free binding/adenylation complexes stay algebraic.
    FAST_SET = [s_ for s_ in ELIM_21 if s_ not in tRNA_bearing]
    A3B_TOTAL_ROWS = [
        ('MetRS_total', 'MetRS'),
        ('GlyRS_total', 'GlyRS'),
        ('adenine_ledger_total', 'ATP'),
        ('phosphate_ledger_total', 'PPi'),
        ('Met_material_total', 'Met'),
        ('Gly_material_total', 'Gly'),
    ]
else:
    raise SystemExit(f'unknown candidate {CAND}')

def build_A_Q(elim, total_rows):
    qset = set(elim)
    repl = {r for _, r in total_rows}
    keep = [nm for nm in names if nm not in qset and nm not in repl]
    A = np.zeros((len(keep) + len(total_rows), 241), dtype=np.int64)
    rowmeta = []
    for i, nm in enumerate(keep):
        A[i, idx[nm]] = 1
        rowmeta.append({'kind': 'identity', 'species': nm})
    for k, (lname, replaced) in enumerate(total_rows):
        for sp, wt in LEDGERS[lname]['weights'].items():
            A[len(keep) + k, idx[sp]] += int(wt)
        rowmeta.append({'kind': 'ledger_total', 'ledger': lname, 'replaces': replaced})
    Q = np.zeros((len(elim), 241), dtype=np.int64)
    for k, e in enumerate(elim):
        Q[k, idx[e]] = 1
    return A, Q, keep, rowmeta

A, Q, keep, rowmeta = build_A_Q(FAST_SET, A3B_TOTAL_ROWS)
n = 241
assert A.shape[0] + Q.shape[0] == n, (A.shape, Q.shape)
T = np.vstack([A, Q])

def mod_rank(Mint, p):
    M = [[int(x) % p for x in row] for row in Mint]
    m = len(M)
    ncols = len(M[0]) if m else 0
    r = 0
    for c in range(ncols):
        piv = None
        for i in range(r, m):
            if M[i][c] % p:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pr = pow(M[r][c], p - 2, p)
        for i in range(r + 1, m):
            f = M[i][c]
            if f:
                inv = f * pr % p
                row_i, row_r = M[i], M[r]
                for cc in range(c, ncols):
                    row_i[cc] = (row_i[cc] - inv * row_r[cc]) % p
        r += 1
        if r == m:
            break
    return r

P1, P2 = 1000000007, 998244353
Tlist = [list(map(int, row)) for row in T]
rankT, rankT2 = mod_rank(Tlist, P1), mod_rank(Tlist, P2)
rankT_num = int(np.linalg.matrix_rank(T.astype(float)))
condT = float(np.linalg.cond(T.astype(float)))
print(f'rank(T): mod p1={rankT} mod p2={rankT2} numeric={rankT_num} (n={n}); cond={condT:.4e}', flush=True)
assert rankT == rankT2 == rankT_num == n

Aint = [list(map(int, r)) for r in A]
rankA_p1 = mod_rank(Aint, P1)
rowspace = {}
for lname, d in LEDGERS.items():
    lv = np.zeros(241, dtype=np.int64)
    for sp, w in d['weights'].items():
        lv[idx[sp]] += int(w)
    rs1 = mod_rank(Aint + [list(map(int, lv))], P1)
    ok1 = (rs1 == rankA_p1)
    rs2 = mod_rank(Aint + [list(map(int, lv))], P2)
    ok = ok1 and (rs2 == mod_rank(Aint, P2))
    cf, *_ = np.linalg.lstsq(A.astype(float).T, lv.astype(float), rcond=None)
    resid = float(np.abs(A.astype(float).T @ cf - lv.astype(float)).max())
    rowspace[lname] = {'in_rowspace_A': bool(ok), 'numeric_ls_residual': resid,
                       'classification': classification[lname]['class']}
    print(f"rowspace(A): {lname:30s} in={ok} ls_resid={resid:.2e}", flush=True)

# ------------------------------------------ Phase 6A: closure q-degree test
qdep_a3b = set(FAST_SET) | {r for _, r in A3B_TOTAL_ROWS}
maxdeg, offenders = 0, []
for j in range(968):
    terms = [t.rsplit(':', 1)[0] for t in rmeta[j]['reactants'].split('|') if t]
    deg = sum(1 for t in terms if t in qdep_a3b)
    if deg > maxdeg:
        maxdeg, offenders = deg, []
    if deg == maxdeg and deg > 1:
        offenders.append({'reaction': f're{j+1:010d}', 'reactants': terms,
                          'subsystem': rmeta[j]['subsystem']})
qdep_a3a = set(ELIM_21) | {'MetRS', 'GlyRS'}
maxdeg_a3a = 0
for j in range(968):
    terms = [t.rsplit(':', 1)[0] for t in rmeta[j]['reactants'].split('|') if t]
    maxdeg_a3a = max(maxdeg_a3a, sum(1 for t in terms if t in qdep_a3a))
print(f'closure max degree in q: A3b={maxdeg} (offenders {len(offenders)}), A3a-coords={maxdeg_a3a}', flush=True)

# ------------------------------------------ Phase 4C: interface flux report
def interface_report(lname):
    w = LEDGERS[lname]['weights']
    v = np.zeros(241, dtype=object)
    for sp, wt in w.items():
        v[idx[sp]] += int(wt)
    lv = v @ S
    out = {}
    for j in range(968):
        if lv[j] != 0 and active[j]:
            sub = rmeta[j]['subsystem'] or 'UNSPECIFIED'
            out.setdefault(sub, []).append(f're{j+1:010d}')
    return {k: sorted(vv) for k, vv in sorted(out.items())}

iface = {lname: interface_report(lname) for lname, _ in A3B_TOTAL_ROWS}

# ------------------------------------------ Phase 7: A3c eligibility table
A3C_PROTECTED = ['tRNAfMetCAU_total', 'tRNAGlyGCC_total', 'phosphate_ledger_total',
                 'adenine_ledger_total', 'Met_material_total', 'Gly_material_total']
elig = []
for e in ELIM_21:
    contrib, why = {}, []
    for lname in A3C_PROTECTED:
        c = int(LEDGERS[lname]['weights'].get(e, 0))
        if c:
            contrib[lname] = c
            why.append(lname)
    cls = 'ELIGIBLE_FOR_RESTRICTED_QSSA' if not why else 'KEEP_EXPLICIT_PROTECTED_LEDGER'
    elig.append({'state': e, 'protected_content': contrib,
                 'classification': cls, 'blocking_rows': why})
n_elig = sum(1 for e in elig if e['classification'] == 'ELIGIBLE_FOR_RESTRICTED_QSSA')
print(f'A3c strict-eligible states: {n_elig} / 21', flush=True)

# ------------------------------------------ runner-facing artifacts
# ledger_dot_S: exact per-reaction balance rows (w^T S) for the 8 A3b ledger
# coordinates — the reduced ledger-row dynamics is (w^T S) v, cancellation-free
ledS = {}
for lname, _ in A3B_TOTAL_ROWS:
    v = np.zeros(241, dtype=object)
    for sp, wt in LEDGERS[lname]['weights'].items():
        v[idx[sp]] += int(wt)
    lv = v @ S
    ledS[lname] = {f're{j+1:010d}': int(lv[j]) for j in range(968) if lv[j] != 0}
os.makedirs(f'{OUT}/{OUTDIR}', exist_ok=True)
with open(f'{OUT}/{OUTDIR}/ledger_dot_S.json', 'w') as f:
    json.dump(ledS, f, indent=1)

recon = {
    'schema': 'pnas2017_aa_a3b_reconstruction/v1',
    'order': ['eliminated(q)'] + [r for _, r in A3B_TOTAL_ROWS],
    'carriers': {r: {'total_row': l, 'family_ledger': l,
                     **({'carrier_weight': 2} if r == 'PPi' else {})}
                 for l, r in A3B_TOTAL_ROWS},
    'rule': ('carrier = total(y) - sum_{members != carrier} w_j x_j '
             '(PPi: (total - sum w_j x_j)/w_carrier); members read x from '
             'q (eliminated), y (identity rows), or previously reconstructed carriers'),
}
with open(f'{OUT}/{OUTDIR}/reconstruction.json', 'w') as f:
    json.dump(recon, f, indent=2)

# ------------------------------------------------------------- emit
os.makedirs(f'{OUT}/{OUTDIR}', exist_ok=True)
os.makedirs(f'{OUT}/pnas2017_aminoacylation_A3c', exist_ok=True)

with open(f'{OUT}/{OUTDIR}/coordinate_matrix_A.csv', 'w', newline='') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['row_id', 'kind', 'label'] + names)
    for i, m in enumerate(rowmeta):
        w.writerow([f'A{i}', m['kind'], m.get('species') or m.get('ledger')] + [int(x) for x in A[i]])
with open(f'{OUT}/{OUTDIR}/fast_selector_Q.csv', 'w', newline='') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['row_id', 'species'] + names)
    for k, e in enumerate(FAST_SET):
        w.writerow([f'Q{k}', e] + [int(x) for x in Q[k]])
with open(f'{OUT}/{OUTDIR}/transformation_T.csv', 'w', newline='') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['block', 'row_id', 'label'] + names)
    for i, m in enumerate(rowmeta):
        w.writerow(['A', f'A{i}', m.get('species') or m.get('ledger')] + [int(x) for x in A[i]])
    for k, e in enumerate(FAST_SET):
        w.writerow(['Q', f'Q{k}', e] + [int(x) for x in Q[k]])

led_rowspace_out = {
    'schema': 'pnas2017_aa_a3b_ledger_rowspace/v1',
    'candidate': CAND,
    'n_states': n, 'n_fast_q': len(FAST_SET), 'n_slow_rows_A': int(A.shape[0]), 'candidate': CAND,
    'rank_T_mod_p1': int(rankT), 'rank_T_mod_p2': int(rankT2),
    'rank_T_numeric': rankT_num, 'cond_T_numeric': condT,
    'protected_ledgers': {k: {**classification[k], **rowspace[k]} for k in LEDGERS},
    'a3b_total_rows': [{'ledger': l, 'replaces_free_carrier': r} for l, r in A3B_TOTAL_ROWS],
    'interface_report': iface,
    'closure_structure': {
        'max_degree_in_q': int(maxdeg),
        'affine_in_q': bool(maxdeg <= 1),
        'n_offending_reactions': len(offenders),
        'offending_reactions': offenders[:40],
        'max_degree_in_q_a3a_coordinates': int(maxdeg_a3a),
        'consequence': ('linear solve M(y)q=-b(y)' if maxdeg <= 1 else
                        'nonlinear constrained root solve required (registered Newton discipline)'),
    },
}
with open(f'{OUT}/{OUTDIR}/protected_ledger_rowspace.json', 'w') as f:
    json.dump(led_rowspace_out, f, indent=2)

a3c_out = {
    'schema': 'pnas2017_aa_a3c_eligibility/v1',
    'selection_rule': ('a fast state is eligible only if, after accounting for the exactly '
                       'reconstructed enzyme totals, its algebraic motion creates no unresolved '
                       'contribution to any protected ledger row'),
    'protected_rows_examined': A3C_PROTECTED,
    'states': elig,
    'n_eligible': n_elig,
}
with open(f'{OUT}/pnas2017_aminoacylation_A3c/a3c_eligibility.json', 'w') as f:
    json.dump(a3c_out, f, indent=2)

print('artifacts written to', OUT, flush=True)
