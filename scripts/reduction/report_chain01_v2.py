"""Produce evidence-bound R1 or final R2 reports from saved V2 arrays/scores."""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path

from prepare_chain01_v2 import ROOT,OUT,CONFIG,digest,dump,check_integrity


def load(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def latest(phase):
    index=load(OUT/(phase+'_latest.json')); summary=load(ROOT/index['summary']); directory=(ROOT/index['summary']).parent
    return summary,load(directory/'verification_report.json'),load(directory/'independent_verification.json'),directory
def number(v): return f'{v:.9g}'
def link(path): return '../../'+str(Path(path).relative_to(ROOT)).replace('\\','/')


def table(lines,headers,rows):
    lines+=['','| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']
    lines+=['| '+' | '.join(map(str,row))+' |' for row in rows]
    lines+=['']


def maximum(summary,config,name,metrics):
    values=[(rec[name]['metrics'][w][metric]['max_normalized'],testid,w,metric)
        for testid,rec in summary['tests'].items() if config['tests'][testid]['domain']=='IN_DOMAIN'
        for w in config['tests'][testid]['gate_windows'] for metric in metrics]
    return max(values)


def make(final=False):
    integrity=check_integrity(); config=load(CONFIG); source=load(OUT/'source_manifest.json'); cert=load(OUT/'mathematical_certificate.json')
    base,bv,bi,bd=latest('base'); boundary,rv,ri,rd=latest('boundary') if final else (None,None,None,None)
    for verification in [bv,bi]+([rv,ri] if final else []):
        if verification['status']!='PASS': raise ValueError('Numerical/independent checks unresolved; do not publish a supported recommendation')
    lines=['# CHAIN_01 V2 resource-preserving staged-chain validation','',
           'Date: 2026-10-08 (Asia/Shanghai). Branch: `codex/pnas-topology-first`.',
           'Final local scientific comparison.' if final else 'R1 local base-boundary comparison; R2 competition experiment remains pending.','']
    if final:
        eligible=[name for name in ('Direct','Two-stage','Three-stage') if all(s['decisions'][name][key]==value
                  for s in (base,boundary) for key,value in [('product','PRODUCT_OUTPUT_SUPPORTED'),('resources','RESOURCE_LEDGER_SUPPORTED'),('macro','LONG_TIME_MACRO_SUPPORTED')])
                  and boundary['decisions'][name]['boundary']=='LOCAL_BOUNDARY_SUPPORTED']
        selected=min(eligible,key=lambda name:len(config['models'][name]['rates_exact'])) if eligible else 'Full'
        lines+=['**Recommendation: retain '+selected+' for the tested local domain.** '+
          ('It is the smallest candidate satisfying the registered long-time product, resource and source re21 competition constraints.' if eligible else 'No candidate satisfies every registered constraint.'),
          'This is local observable support, not global VALIDATED status, reduced-core approval, or authorization to run the 968-reaction replacement.','']
    else:
        selected=None
        lines+=['Base numerical and independent analytic checks: **PASS**. The comparison preserves both the original coarse-grid unresolved attempt and the converged numerical successor.','']
    lines+=['## Sources, exact mapping and equations','',
       'Canonical SBML and author CSVs were reread and cross-checked, including all 968 topology reaction rows and all 241 net species coordinates. '+
       'Placeholder SBML k1=1 was not used. Raw source SHA-256 is `'+source['sources'][0]['sha256']+'`.',
       'Source time units are retained; no conversion to seconds is made. The old three-step A/X1/X2/B map to V2 S1/S2/S3/S4.',
       'S4 is the ribosome-bound Pept0002 local extension state. It is a local production proxy, not free final Pept0003 or full PURE protein output.','']
    descriptions=['EF-Tu.GTP loaded complex before hydrolysis','GDP/Pi bound after hydrolysis','Pi released; EF-Tu.GDP bound','EF-Tu released before extension','Pept0002 formed; ribosome still bound']
    table(lines,['Alias','Exact SBML species ID','Chemical meaning'],[[a,'`'+sid+'`',descriptions[int(a[1])]] for a,sid in source['species_aliases'].items()])
    table(lines,['Source reaction','Author k','Products'],[[r['reaction_id'],r['author_parameters'][0]['author_value_exact'],', '.join(r['products_exact'])] for r in source['chain_reactions']])
    lines+=['Full: S0→S1→S2+Pi→S3+EF-Tu.GDP→S4, with rates 260,1000,7,1000.',
            'Direct: S0→S4+Pi+EF-Tu.GDP, ke=1/tau.',
            'Two-stage: S0→S2+Pi, then S2→S4+EF-Tu.GDP, with ka=1/(1/260+1/1000) and kb=1/(1/7+1/1000).',
            'Three-stage: retain S0→S1 and S1→S2+Pi at source rates; S2→S4+EF-Tu.GDP uses kb.',
            'For every model: z0′=u−J0, zi′=J(i−1)−Ji, S4′=Jlast, xi_i′=Ji with Ji=ki zi. '+
            'Pi/GDP currents and extents are read from the designated release stages. All candidate columns equal their exact sums of source columns; all net differences are exactly zero.',
            'When re21 is restored, subtract c*z0 from z0′ and add it independently to both exact source products and xi21. c=0.23; no sink or invented chemical product is used.','']
    table(lines,['Model','Chain reactions','Chemical states including S4','Transient states','Extent counters','Mean wait','Variance'],[
        [name,r['reaction_count'],r['chemical_state_count'],r['transient_state_count'],r['extent_counter_count'],number(float(F(r['mean_residence_exact']))),number(float(F(r['variance_exact'])))] for name,r in cert['models'].items()])
    lines+=['Free Pi/GDP are read from extents. R2 adds two explicit source product amounts and one re21 extent to every model. '+
            'The input and its integral are experiment-driver coordinates, not intrinsic reaction states. These accounting dimensions are not hidden in the reaction/state reduction claim.',
            'All mean-dwell matches are approximate Markov candidates. Waiting variances differ; equal steady current or final cohort yield alone does not establish dynamic equivalence.','',
            '## Frozen experiments and budgets','',
            'Protocol SHA-256: `'+digest(CONFIG)+'`. The R0 freeze predates all V2 trajectories and was pushed before R1 began.',
            'Unit S0 pulse runs through 100tau; constant u=1 through 10000tau; u=exp(-t/T) at T/tau=20,100,1000 through ten supply-decay times. '+
            'The V1 rectangular inputs and nonzero initial inventory [0,.25,.5,.25,0] are retained as prospectively excluded negative controls.',
            'Required long-time windows are [5,10]tau and [10,end]tau. Early [0,10], V1 transient/post and long subwindows are all retained. '+
            'Maxima are original registered sampled-grid values. Numerical midpoint refinements check convergence without changing scoring nodes. '+
            'The first base attempt remains archived with native NUMERICALLY_UNRESOLVED sampling records; the successor meets the unchanged 1e-4 refinement-change budget.',
            'Gate 2: product current and integrated formation extent each ≤1% of predeclared fixed scales. Gate 3: Pi/GDP current, extent, bound Pi/GDP, '+
            'bound GTP precursor, total chain-bound Tu, unreleased phosphate equivalents and unfinished ribosome inventory each ≤1%. '+
            'Amount scale is initial cohort 1 or u0*tau; current scale is cohort/tau or u0. Growing cumulative totals never set an acceptance denominator.',
            'R2 additionally requires ≤1% relative error in both success and escape probabilities and in final cohort yield. '+
            'The small escape pathway carries intact GTP-loaded carrier, so its allocation is checked separately.',
            'Production integral means integral of formation current, equal to directed product extent. Window integrals and checkpoint cumulative-relative errors are saved separately.','',
            '## Numerical and independent verification','']
    rows=[]
    for phase,v,ind in [('base',bv,bi)]+([('boundary',rv,ri)] if final else []):
        rows.append([phase,v['status'],ind['status'],number(max(r['primary_vs_expm'] for t in v['checks'].values() for r in t.values())),
                     number(max(r['current_vs_expm'] for t in v['checks'].values() for r in t.values())),
                     number(max(r['ledger_max'] for t in v['checks'].values() for r in t.values())),number(ind['largest_checkpoint_state_extent_error'])])
    table(lines,['Phase','Numerical','Independent','Max state/extent vs expm','Max current vs expm','Max fate residual','Max 70-digit checkpoint error'],rows)
    lines+=['Primary Radau (1e-10,1e-12), tighter Radau (1e-12,1e-14), augmented dense expm and independent source-rebuilt exact rational Laplace residues at 70 digits are compared. '+
            'Repeated rate-1000 poles are treated explicitly. All-grid currents and fate identities, required-window scores, exact candidate source-column sums, waiting-time resolvent moments and artifact hashes are checked.',
            'No negative clipping, state projection or parameter fitting was used. '+str(integrity['protected_file_count'])+' preexisting tracked files retain their raw byte fingerprints. V1 remains LOCAL_CANDIDATE_FAILED_REGISTERED_SCREEN.','',
            '## Long-time product and resource scores','']
    for phase,s in [('base',base)]+([('boundary',boundary)] if final else []):
        lines+=['### '+phase,'']
        rows=[]
        for name,rec in s['decisions'].items():
            p=maximum(s,config,name,config['gates']['product']['metrics']); r=maximum(s,config,name,config['gates']['resources']['metrics'])
            rows.append([name,rec['product'],rec['resources'],rec['boundary'],number(p[0]),f'{p[1]}/{p[2]}/{p[3]}',number(r[0]),f'{r[1]}/{r[2]}/{r[3]}'])
        table(lines,['Model','Product','Ledger','Boundary','Worst product / fixed scale','Where','Worst resource / fixed scale','Where'],rows)
        rows=[]
        for testid,test in config['tests'].items():
            if test['domain']!='IN_DOMAIN': continue
            for name in ('Direct','Two-stage','Three-stage'):
                values=s['tests'][testid][name]['metrics']
                rows.append([testid,name]+[number(max(values[w][m]['max_normalized'] for w in test['gate_windows'])) for m in ('product_extent','product_current','pi_extent','pi_current','gdp_extent','gdp_current','bound_pi','bound_gdp','unfinished')])
        table(lines,['Test','Model','S4 extent','S4 current','Pi extent','Pi current','GDP extent','GDP current','Bound Pi','Bound GDP','Unfinished'],rows)
    lines+=['## Stable input: persistent absolute offsets','',
            'For base constant input, each stage current tends to u; each transient stage tends to u/k. S4 continues to increase. '+
            'The eventual current equality follows for any completing irreversible chain and is not a parameter validation. '+
            'xi_R=u(t-d_R)+o(1), where d_R is the mean delay through the resource-release stage.','']
    rows=[]
    for name,r in cert['models'].items():
        endpoint=next(rec for rec in base['tests']['B_constant'][name]['endpoints'] if rec['t_over_tau']==10000)
        rows.append([name]+[number(float(F(r['cumulative_asymptotic_offsets_vs_full_exact'][m]))) for m in ('product','pi','gdp')]+[
             number(endpoint['pi_extent']['signed_absolute']),number(endpoint['pi_extent']['fixed_scale_signed']),number(endpoint['pi_extent']['relative_absolute']),
             number(endpoint['bound_gdp']['signed_absolute'])])
    table(lines,['Model','Analytic S4 offset','Analytic Pi offset','Analytic GDP offset','Pi offset at 10000tau','Pi / fixed scale','Pi cumulative-relative','Bound GDP offset'],rows)
    lines+=['Direct has a persistent Pi deficit despite a shrinking cumulative percentage. Two-stage preserves the mean Pi-release delay but reallocates bound Pi to a longer GTP precursor residence. '+
            'Three-stage preserves hydrolysis and Pi release exactly in these local tests; combining EF-Tu departure with extension delays free GDP and adds bound GDP by approximately u/1000. '+
            'Both coarse multi-stage models have a nonzero free-GDP deficit; it is measured against the fixed resource scale.','',
            '## Applicability and failure mechanisms','']
    if final:
        rows=[]
        for name in ('Full','Direct','Two-stage','Three-stage'):
            alloc=boundary['tests']['A_pulse'][name]['allocation']
            endpoint=next(e for e in boundary['tests']['B_constant'][name]['endpoints'] if e['t_over_tau']==10000)
            rows.append([name,number(alloc['completion_probability']),number(alloc['escape_probability']),number(alloc['completion_relative_error']),number(alloc['escape_relative_error']),
                         number(endpoint['product_extent']['fixed_scale_signed']),number(endpoint['product_extent']['relative_absolute']),alloc['status']])
        table(lines,['Model','Success p','Escape q','p relative error','q relative error','10000tau S4 error / fixed scale','10000tau S4 cumulative-relative','Allocation support'],rows)
        lines+=['re21 produces `EFTu_GTP_GlytRNAGlyGCC` and `elRS70SAGGU0002_fMet`. Both are explicit local output reservoirs; neither is called a bare sink or a free ribosome. '+
                'The escaped loaded carrier retains its GTP, Tu and Gly-tRNA cargo. Source re13 rebinding is not restored in this open boundary test.',
                'p=k_in/(k_in+c), q=c/(k_in+c). Two-stage changes k_in from 260 to ka, hence the race with undocking; the small instantaneous yield-rate bias accumulates during sustained input. '+
                'Three-stage retains the original S0 competition rate and exact allocation. The author c=.23 is the only numerical competition parameter tested.',
                'Analytically, relative Two-stage escape bias is (260-ka)/(ka+c); relative success bias is c*(260-ka)/(260*(ka+c)). '+
                'These formulas describe sensitivity for c≥0, not empirical validation of an untested parameter range.','']
    rows=[]
    for testid in ('D_fast','D_inventory'):
        for name in ('Direct','Two-stage','Three-stage'):
            rec=base['tests'][testid][name]; end=rec['endpoints'][-1]
            rows.append([testid,name,rec['domain'],number(rec['metrics']['early_0_10']['product_current']['max_normalized']),
                number(rec['metrics']['early_0_10']['pi_current']['max_normalized']),number(end['gdp_extent']['signed_absolute']),str(rec['initial_resource_mapping_difference'])])
    table(lines,['Control','Model','Prospective domain','Early product-current error','Early Pi-current error','Final GDP extent difference','Initial ledger projection difference'],rows)
    lines+=['Fast rectangular inputs remain negative controls even when some late measures pass. Arbitrary initial internal mixtures cannot be reconstructed from the retained coordinates. '+
            'In the initial-inventory control, Three-stage adds 0.25 bound GDP equivalents by assigning initially Tu-free S3 to a GDP-bound reservoir; the subsequent free-GDP extent differs by 0.25. '+
            'This excludes a general nonzero-internal-inventory claim.',
            'Supported input evidence is confined to the declared pulse late windows, steady supply, and the three tested slow supply ratios. All source rates and internal zero side paths are fixed. '+
            'There is no full ATP/GTP shared-pool concentration validation or demonstration of safe arbitrary upstream/downstream coupling.','']
    if final:
        lines+=['A separate prospective full-coupled pilot of Three-stage is recommended for consideration, with shared Tu/GTP/Pi and ribosome inventories, source units, '+
                'downstream consumption, internal initial mixtures and reactivated side paths explicitly audited. That pilot is **not started or approved here**. '+
                'PURE_reduced_core and historical scientific decision records are unchanged.','']
    lines+=['## Reproduction, files and delivery','',
        'Commands actually used: `python scripts/reduction/prepare_chain01_v2.py`; `python scripts/tests/test_chain01_v2.py`; '+
        '`python scripts/reduction/validate_chain01_v2.py`; `python scripts/tests/verify_chain01_v2.py`'+
        ('; `python scripts/reduction/validate_chain01_v2.py --boundary`; `python scripts/tests/verify_chain01_v2.py --boundary`.' if final else '.'),
        'Each completed round runs diff checks, commit, explicit push and live `git ls-remote` confirmation. Exact payload SHA receipts and verification times are in '+
        '[git_delivery_manifest.json](../../results/reduction/chain01_v2/git_delivery_manifest.json). The receipt is committed subsequently to avoid a circular self hash.','']
    for title,path in [('Frozen protocol',CONFIG),('Source manifest',OUT/'source_manifest.json'),('Exact mathematics',OUT/'mathematical_certificate.json'),('Base summary',bd/'validation_summary.json'),('Base independent checks',bd/'independent_verification.json')]+(
                  [('Boundary summary',rd/'validation_summary.json'),('Boundary independent checks',rd/'independent_verification.json')] if final else []):
        lines+=['- ['+title+']('+link(path)+')']
    lines+=['','Raw compressed CSVs include primary, tighter and expm states/extents, currents, both input limits, fate residuals and original scoring-grid membership. '+
            'Error CSVs include signed, fixed-scale and relative errors without denominator clipping. Every phase has the nine requested PNG figures and a data-source map. '+
            'Numerical attempts, frozen fingerprints, independent verification and derived provenance navigation are subordinate to the canonical sources and original arrays.','']
    phase='boundary' if final else 'base'
    idx=load(OUT/(phase+'_latest.json'))
    figs=ROOT/idx['figures'] if 'figures' in idx else OUT/'figures'/phase/(rd.name if final else bd.name)
    lines+=['### Figure index','']
    for image in sorted(figs.glob('*.png')):
        lines+=['- ['+image.stem+']('+link(image)+')']
    target=ROOT/'docs/reduction'/('chain01_v2_validation_report.md' if final else 'chain01_v2_base_validation_report.md')
    target.write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    summary={'protocol_id':config['protocol_id'],'config_sha256':digest(CONFIG),'base_decisions':base['decisions'],'boundary_decisions':boundary['decisions'] if final else None,
             'selected_local_model':selected,'condition_domain':config['gates']['domain'],'full_coupled_validation':'NOT_STARTED','PURE_reduced_core':'UNCHANGED; no promotion',
             'source_semantics':'S4 local Pept0002 formation proxy','historical_integrity':integrity,'report':str(target.relative_to(ROOT)).replace('\\','/')}
    dump(OUT/'validation_summary.json',summary)
    dump(OUT/'verification_report.json',{'status':'PASS','base_numerical':bv['status'],'base_independent':bi['status'],
           'boundary_numerical':rv['status'] if final else 'NOT_STARTED','boundary_independent':ri['status'] if final else 'NOT_STARTED','historical_integrity':integrity})
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--final',action='store_true'); args=ap.parse_args(); make(args.final)
