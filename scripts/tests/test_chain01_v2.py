"""Prospective structural tests; --verify later independently audits saved data."""
from pathlib import Path
from fractions import Fraction as F
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/reduction'))
from prepare_chain01_v2 import OUT, CONFIG, model_specs, coefficients, check_integrity


class StructuralChecks(unittest.TestCase):
    def test_frozen_sources_and_history(self):
        self.assertEqual(check_integrity()['status'],'PASS')

    def test_column_identity_and_waiting_moments(self):
        cert=json.loads((OUT/'mathematical_certificate.json').read_text())
        manifest=json.loads((OUT/'source_manifest.json').read_text())
        for spec in model_specs(manifest).values():
            self.assertEqual(sum((1/F(x) for x in spec['rates_exact']),F(0)),F(manifest['tau_exact']))
        for rec in cert['models'].values():
            self.assertEqual(set(rec['net_per_species_difference_exact'].values()),{'0'})
            self.assertEqual(len(rec['net_per_species_difference_exact']),241)

    def test_boundary_products_and_exact_probabilities(self):
        cert=json.loads((OUT/'mathematical_certificate.json').read_text())
        manifest=json.loads((OUT/'source_manifest.json').read_text())
        self.assertEqual(manifest['boundary_reaction']['products_exact'],{'EFTu_GTP_GlytRNAGlyGCC':'1','elRS70SAGGU0002_fMet':'1'})
        for rec in cert['models'].values():
            c=rec['competition']
            self.assertEqual(F(c['completion_probability_exact'])+F(c['escape_probability_exact']),1)

    def test_ledger_composition(self):
        props=coefficients(['S0','S1','S2','S3','S4'])
        self.assertEqual(props['bound_pi'],[0,1,0,0,0])
        self.assertEqual(props['bound_gdp'],[0,1,1,0,0])
        self.assertEqual(props['phosphate_unreleased'],[1,1,0,0,0])

    def test_negative_controls_do_not_promote_domain(self):
        config=json.loads(CONFIG.read_text())
        for name in ('D_fast','D_inventory'):
            self.assertEqual(config['tests'][name]['gate_windows'],[])
            self.assertNotEqual(config['tests'][name]['domain'],'IN_DOMAIN')
        self.assertEqual(config['tests']['B_constant']['end_tau'],10000)
        self.assertEqual(config['gates']['resources']['max_fixed_scale_error'],.01)

    def test_implemented_free_bound_fate_vectors(self):
        # This tests independently stated conservation vectors, including both
        # material re21 products, rather than mirroring the RHS calculation.
        import numpy as np
        from validate_chain01_v2 import matrix
        config=json.loads(CONFIG.read_text())
        for name,spec in config['models'].items():
            for c in (0.,.23):
                m,labels,rates=matrix(spec,c,1/(20*.1487032967032967))
                n=len(spec['states'])
                vectors=[]
                rib=np.zeros(len(labels)); rib[:n]=1; rib[-2]=-1
                if c: rib[labels.index('undocked_ribosome')]=1
                vectors.append(rib)
                for states,positive_extent,negative_extent,escape,inlet in [
                    (['S0'],0,None,True,True),
                    (['S1'],spec['pi_stage'],0,False,False),
                    (['S1','S2'],spec['gdp_stage'],0,False,False),
                    (['S0','S1','S2'],spec['gdp_stage'],None,True,True),
                ]:
                    v=np.zeros(len(labels))
                    for i,state in enumerate(spec['states']): v[i]=int(state in states)
                    v[n+positive_extent]+=1
                    if negative_extent is not None: v[n+negative_extent]-=1
                    if c and escape: v[labels.index('undocked_intact_gtp_carrier')]+=1
                    if inlet: v[-2]-=1
                    vectors.append(v)
                for vector in vectors:
                    self.assertLessEqual(float(np.max(abs(vector@m))),1e-12,(name,c))


if __name__=='__main__':
    if '--verify' in sys.argv:
        from verify_chain01_v2 import verify
        verify()
    else:
        unittest.main()
