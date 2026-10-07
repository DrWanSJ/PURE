"""Repair an entry-point import without mutating the frozen R7 verifier body.

The original NameError is retained in verification_attempt_001.json. No equations,
numerical arrays, registration hashes, scoring rules, or gates are changed.
"""
from pathlib import Path
import traceback
import verify_r7_ck_first_order_v1 as frozen
from r7_ck_h1_v1 import ROOT, OUT, sha, load, write_json, stamp

def main():
    frozen.Path=Path
    try:
        frozen.verify()
        report=load(OUT/'verification.json')
        supplement=load(OUT/'canonical_structure_verification.json')
        assert supplement['status']=='PASS_INDEPENDENT_CANONICAL_STRUCTURE'
        report['checks'].append(dict(check='CANONICAL_RATE_JACOBIAN_GQ_H1_RESIDUAL_AND_OFF_GRAPH_ETA_FAMILY',
            status='PASS',receipt_sha256=sha(OUT/'canonical_structure_verification.json'),maxima=supplement['maxima']))
        report['entry_repair']=dict(scope='IMPORT_ONLY_PATH_NAME',frozen_verifier_body_unchanged=True,
            frozen_verifier_sha256=sha(ROOT/'scripts/verify_r7_ck_first_order_v1.py'),entry_sha256=sha(Path(__file__)),
            original_failure_receipt_sha256=sha(OUT/'verification_attempt_001.json'))
        report['diagnostic_labels']=dict(nonlinear_flow_consistency_evaluation='RESUMMED_SUBSTITUTION_DIAGNOSTIC',
            resummed_trajectory_solves=0,formal_model='F0_PLUS_Fq_H1_TAYLOR_TRUNCATION')
        write_json(OUT/'verification.json',report)
    except Exception as exc:
        write_json(OUT/'verification_attempt_002.json',dict(stage='INDEPENDENT_FINAL_VERIFIER',status='FAIL',
            error=str(exc),traceback=traceback.format_exc(),recorded_at_utc=stamp(),scientific_gates_changed=False))
        raise

if __name__=='__main__':main()
