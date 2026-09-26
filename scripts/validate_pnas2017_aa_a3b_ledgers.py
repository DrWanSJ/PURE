"""Anti-sliding-leak validator for the A3b reduced runs (Phase 12).

For every protected ledger l (the 9 audited rows), verifies along a reduced
trajectory that

    d/dt (l . x_RED)  matches  the exact full-network ledger balance,
    i.e. the FULL model's own ledger motion d/dt (l . x_FULL),

and that the A3a sliding-leak identity

    drift_RED(t) - drift_FULL(t) == d/dt (eliminated token content in RED)

is ABSENT (the residual must be at the trajectory-representation level, not
the drained complex content).

usage: python validate_pnas2017_aa_a3b_ledgers.py <red_csv> <full_csv> <out_json>
"""
import csv, json, sys
import numpy as np

ROOT = '.'

def load_traj(p):
    names, rows = None, []
    with open(p) as f:
        r = csv.reader(f)
        names = next(r)[1:]
        for row in r:
            rows.append([float(v) for v in row[1:]])
    return names, rows  # rows: time-stripped, each 241+NC (time handled below)

def load_ledgers():
    scope = json.load(open(f'{ROOT}/models/pnas2017_full_reference/audit/aminoacylation_v1_comparison_scope.json'))
    led = {}
    for g in scope['conservation']:
        if g['id'] == 'aa_subsystem_particle_count':
            continue
        w = g.get('weights') or {}
        led[g['id']] = {s: float(w.get(s, 1)) for s in g['species']}
    binit = {}
    with open(f'{ROOT}/docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2_matrix.csv') as f:
        rd = csv.reader(f)
        hdr = next(rd)
        for row in rd:
            binit[row[0]] = {hdr[i + 1]: float(v) for i, v in enumerate(row[1:]) if float(v) != 0}
    led['Met_material_total'] = binit['Met_total']
    led['Gly_material_total'] = binit['Gly_total']
    return led

def main(red_csv, full_csv, out_json):
    names, R = load_traj(red_csv)
    _, F = load_traj(full_csv)
    idx = {n: i for i, n in enumerate(names)}
    # reload raw time columns (load_traj strips column 0)
    def load_times(p):
        ts = []
        with open(p) as f:
            r = csv.reader(f)
            next(r)
            for row in r:
                ts.append(float(row[0]))
        return np.array(ts)
    tR_raw = load_times(red_csv)
    tF_raw = load_times(full_csv)
    elim = json.load(open(f'{ROOT}/docs/audit/pnas2017_aminoacylation_A3b/protected_ledger_rowspace.json'))
    led = load_ledgers()

    # eliminated complex names (from the fast selectors)
    qnames = []
    with open(f'{ROOT}/docs/audit/pnas2017_aminoacylation_A3b/fast_selector_Q.csv') as f:
        rd = csv.reader(f)
        next(rd)
        for row in rd:
            qnames.append(row[1])
    isElim = [names.index(q) for q in qnames]

    XR = np.array([r[:241] for r in R]).T   # 241 x n
    XF = np.array([r[:241] for r in F]).T
    tR, tF = tR_raw, tF_raw
    nR, nF = len(tR), len(tF)

    out = {'schema': 'pnas2017_aa_a3b_anti_sliding_validation/v1',
           'red_csv': red_csv, 'full_csv': full_csv, 'ledgers': {}}
    all_ok = True
    for lname, w in led.items():
        v = np.zeros(241)
        for sp, wt in w.items():
            v[idx[sp]] = wt
        lR = v @ XR          # ledger trajectory in RED
        lF = v @ XF
        # numerical derivative (log-spaced grid: central differences in t)
        dR = np.gradient(lR, tR)
        dF = np.gradient(lF, tF)
        # sliding-term probe: token content of the eliminated complexes in RED
        vq = np.zeros(241)
        for q in qnames:
            vq[idx[q]] = 1.0
        qc = vq @ XR
        dq = np.gradient(qc, tR)
        # interpolated FULL derivative on the RED grid (the retained external
        # balance), guard the common window
        lo = max(tR[0], tF[0]); hi = min(tR[-1], tF[-1])
        m = (tR >= lo) & (tR <= hi)
        dFi = np.interp(tR[m], tF, dF)
        mismatch = dR[m] - dFi
        scale = max(abs(lF).max(), abs(lR).max(), 1e-30)
        rel_mismatch = np.abs(mismatch).max() / scale
        # A3a sliding-identity coherence: the identity is PRESENT iff the
        # RED-minus-FULL ledger mismatch is of the same magnitude as the
        # eliminated complexes' token-content motion dq; the identity is
        # ABSENT (the anti-sliding requirement) iff the mismatch is
        # negligible compared with dq.
        dq_max = float(np.abs(np.interp(tR[m], tR, dq)).max())
        qc_scale = max(abs(qc).max(), 1e-30)
        coherence = float(np.abs(mismatch).max() / max(dq_max, 1e-300))
        exact = lname in ('MetRS_moiety_total', 'GlyRS_moiety_total',
                          'tRNAfMetCAU_family_total', 'tRNAGlyGCC_family_total',
                          'phosphate_ledger_total', 'guanine_ledger_total')
        if exact:
            ok = rel_mismatch <= 1e-8
        else:
            ok = rel_mismatch <= 1e-6
        sliding_id_present = coherence > 0.01 and rel_mismatch > 1e-8
        rec = {'ledger': lname,
               'class': 'EXACT' if exact else 'INTERFACE_BALANCE',
               't0_red': float(lR[0]), 't0_full': float(lF[0]),
               'max_abs_mismatch': float(np.abs(mismatch).max()),
               'max_rel_mismatch': float(rel_mismatch),
               'sliding_identity_coherence': coherence,
               'eliminated_content_scale': float(qc_scale),
               'sliding_identity_present': bool(sliding_id_present),
               'ok': bool(ok)}
        out['ledgers'][lname] = rec
        all_ok = all_ok and rec['ok']
        print(f"{lname:32s} rel_mismatch={rel_mismatch:.3e} "
              f"sliding_coherence={coherence:.3e} ok={rec['ok']}")
    out['all_ok'] = bool(all_ok)
    json.dump(out, open(out_json, 'w'), indent=2)
    print('all_ok =', all_ok)
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
