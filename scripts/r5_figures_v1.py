"""Static scientific figures from recorded CSV evidence."""
from r5_common_v1 import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def main():
 dest=OUT/'figures';dest.mkdir(exist_ok=True)
 scan=list(csv.DictReader((OUT/'ck/singular_eta_scan.csv').open()));gly=list(csv.DictReader((OUT/'glyrs/condition_predictor_comparison.csv').open()));bal=json.loads((OUT/'balance/balance_decomposition_summary.json').read_text())
 fig,ax=plt.subplots(1,3,figsize=(16,5));fig.subplots_adjust(bottom=.30,top=.85,wspace=.40)
 eta=np.array([float(v['eta']) for v in scan]);ax[0].loglog(eta,[float(v['outer_post_layer_slow_max_scaled']) for v in scan],'o-',label='Outer, after own layer');ax[0].loglog(eta,[float(v['hybrid_post_common_layer_slow_max_scaled']) for v in scan],'s-',label='Hybrid, common window');ax[0].invert_xaxis();ax[0].set(xlabel='eta (smaller to right)',ylabel='Max normalized slow error',title='CK baseline singular family');ax[0].legend(fontsize=8);ax[0].grid(alpha=.2)
 ratios=np.array([float(v['new_over_old_error']) for v in gly]);labels=[v['condition'].replace('R3_','') for v in gly];ax[1].bar(np.arange(len(gly)),ratios,color=['#c45145' if x>1 else '#387e9d' for x in ratios]);ax[1].axhline(1,color='black',ls='--',lw=1);ax[1].set_xticks(np.arange(len(gly)),labels,rotation=70,ha='right',fontsize=8);ax[1].set(ylabel='New / old post-layer error',title='GlyRS feedback predictor');ax[1].text(.03,.95,'Below 1 = improvement',transform=ax[1].transAxes,va='top',fontsize=9)
 values=[bal['max_exact_law_drift'],bal['max_postprocessing_summation_change'],bal['max_primary_source_ledger_residual'],bal['max_reduced_slow_ledger_residual'],bal['max_same_trajectory_tight_extent_change']];labels=['Exact-law drift','Summation only','Source ledger','Reduced slow ledger','Tight-ledger change'];ax[2].bar(range(5),values,color=['#387e9d','#93b7c9','#c49145','#c49145','#c45145']);ax[2].set_yscale('log');ax[2].set_xticks(range(5),labels,rotation=60,ha='right',fontsize=8);ax[2].set(ylabel='Absolute reference concentration',title='Balance components (different tests)');ax[2].grid(axis='y',alpha=.2)
 fig.suptitle('R5 descriptive evidence — no candidate promotion',fontsize=16)
 fig.text(.01,.025,'Source: singular_eta_scan.csv; condition_predictor_comparison.csv; balance_decomposition_summary.json.\nWindows/scales differ between panels. Balance values are component maxima, not an additive causal decomposition.',fontsize=9)
 fig.savefig(dest/'r5_evidence_overview.png',dpi=150);fig.savefig(dest/'r5_evidence_overview.svg');plt.close(fig)
 print('Scientific overview figure written')
if __name__=='__main__':main()
