"""Measured scientific figures; no generated conceptual artwork."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/energy_cycles_v1'

def save(fig,name):
    dest=OUT/'figures';dest.mkdir(exist_ok=True)
    fig.savefig(dest/(name+'.png'),dpi=180,bbox_inches='tight')
    p=dest/(name+'.svg');fig.savefig(p,bbox_inches='tight');p.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    plt.close(fig)

def plots(d,ms,summary):
    names=['CK','NDK','MK','PPiase'];fig,ax=plt.subplots(figsize=(8,4.4));x=np.arange(4)
    initial=[100*summary['units'][n]['initial_layer_maxima']['max_scaled_free'] for n in names]
    long=[100*max(summary['units'][n]['long_maxima']['max_scaled_free'],summary['units'][n]['long_maxima']['max_scaled_retained']) for n in names]
    ax.bar(x-.18,initial,.36,label='0–0.05: free forms');ax.bar(x+.18,long,.36,label='1–1000: free/total forms')
    ax.set_xticks(x,names);ax.set_ylabel('Maximum scaled error (%)');ax.axhline(5,color='black',ls='--',lw=1,label='Long-window target 5%')
    ax.set_title('Feasible completed comparisons: transient and long error');ax.legend(fontsize=9);ax.spines[['top','right']].set_visible(False)
    fig.text(.01,-.01,'Domain stops excluded from numerical maxima and reported explicitly; no subsystem is approved.',fontsize=9)
    save(fig,'transient_and_long_errors')
    fig,axs=plt.subplots(2,2,figsize=(10,7.4));selected={'CK':('POSITIVE_CHALLENGE','ADP'),'NDK':('POSITIVE_CHALLENGE','GDP'),'MK':('COUPLED_RESOURCE_LIMITATION','ADP'),'PPiase':('LOW_FUEL','PO4')}
    for ax,n in zip(axs.flat,names):
        cond,s=selected[n];m=next((m for m in ms if m['id']==n+'__'+cond and m['initial_mode']=='ORIGINAL_NONEQUILIBRIUM'),None)
        if m is None:
            ax.text(.5,.5,'No completed comparison',ha='center',va='center');continue
        z=np.load(ROOT/m['trajectory']['path']);i=list(z['species']).index(s);t=z['time']
        ax.plot(t,z['microscopic'][:,i],label='Source microscopic',lw=1.5);ax.plot(t,z['reduced'][:,i],label='Stationary-total candidate',ls='--',lw=1.3)
        ax.set_xscale('symlog',linthresh=1e-7);ax.set_title(n+' / '+cond.replace('_',' ').lower());ax.set_xlabel('Author numerical time');ax.set_ylabel(s+' (source numerical concentration)')
        ax.ticklabel_format(axis='y',useOffset=False)
        ax.axvline(.05,color='#888',lw=.7);ax.axvline(1,color='#888',lw=.7);ax.spines[['top','right']].set_visible(False)
    axs[0,0].legend(fontsize=8);fig.suptitle('Isolated modules: original nonequilibrium initial states',fontsize=13);fig.tight_layout();save(fig,'measured_resource_trajectories')
