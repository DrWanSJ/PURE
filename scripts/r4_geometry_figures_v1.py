"""Render completed geometric diagnostics while independent coupled jobs run."""
from r4_fast_block_common_v1 import *
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=OUT/'figures';p.mkdir(exist_ok=True)
def save(n):plt.tight_layout();plt.savefig(p/(n+'.png'),dpi=160);plt.close()
frames=[];lag=[]
for family in ['GlyRS','MetRS']:
 for c in REG['conditions']:
  name=c['condition_id'];base=OUT/(family.lower()+'_only')/name;frame=pd.read_csv(base/'manifold_geometry.csv');frame['candidate']='R4_'+family.upper()+'_ONLY';frames.append(frame[['candidate','condition','time_s','closure_max','defect_max']].rename(columns={'closure_max':'closure','defect_max':'defect'}))
  if name=='R3_BASE':
   f=pd.read_csv(base/'lag.csv');species=['GlyRS_AMP_GlytRNAGlyGCC','GlyRS_Gly_ATP'] if family=='GlyRS' else ['MetRS_AMP_MettRNAfMetCAU','MetRS_Met_ATP'];f=f[f.species.isin(species)];f['candidate']='R4_'+family.upper()+'_ONLY';lag.append(f[['candidate','time_s','species','actual_lag_uM','predicted_lag_uM']].rename(columns={'actual_lag_uM':'actual','predicted_lag_uM':'predicted'}))
hist=pd.read_csv(OUT/'historical_r3_comparison/manifold_geometry.csv');frames.append(hist[['candidate','condition','time_s','closure_max','defect_max']].rename(columns={'closure_max':'closure','defect_max':'defect'}));frame=pd.concat(frames);frame.to_csv(p/'04_closure_vs_defect.csv',index=False);labels=['historical_R3_21','R4_GLYRS_ONLY','R4_METRS_ONLY'];plt.figure(figsize=(8,4.5))
for j,n in enumerate(labels):
 f=frame[frame.candidate==n];plt.scatter(np.full(len(f),j)-.08,np.maximum(f.closure,1e-20),s=2,alpha=.3,label=n+' closure');plt.scatter(np.full(len(f),j)+.08,np.maximum(f.defect,1e-20),s=2,alpha=.3,label=n+' defect')
plt.yscale('log');plt.xticks(range(3),labels);plt.ylabel('max |G| or |G-Dh F| (uM/s)');plt.title('Closure does not establish invariance');plt.legend(fontsize=6,ncol=2);save('04_closure_vs_defect')
frame=pd.concat(lag);frame.to_csv(p/'05_representative_lag.csv',index=False);fig,axes=plt.subplots(2,2,figsize=(11,7))
for col,n in enumerate(labels[1:]):
 species=['GlyRS_Gly_ATP','GlyRS_AMP_GlytRNAGlyGCC'] if col==0 else ['MetRS_Met_ATP','MetRS_AMP_MettRNAfMetCAU']
 for ax,sp in zip(axes[:,col],species):
  f=frame[(frame.candidate==n)&(frame.species==sp)];ax.plot(f.time_s,f.actual,label='Observed q_full-h0');ax.plot(f.time_s,f.predicted,label='Linearized predictor',ls='--');ax.set_xscale('symlog',linthresh=1e-4);ax.set_title(sp,fontsize=10);ax.set_xlabel('Time (s)');ax.set_ylabel('Lag (uM)');ax.legend(fontsize=7)
fig.suptitle('Baseline representative lag; full window retained');save('05_representative_lag')
modes=pd.read_csv(OUT/'mixed_csp_mode_block/m4_geometry.csv');modes.to_csv(p/'06_m4_span_persistence.csv',index=False);fig,axes=plt.subplots(1,2,figsize=(10,4))
for condition,f in modes.groupby('condition'):
 axes[0].plot(f.time_s,f.temporal_angle_deg,label=condition,lw=.8);axes[1].plot(f.time_s,f.baseline_same_time_angle_deg,label=condition,lw=.8)
for ax,title in zip(axes,['Adjacent-time largest principal angle','Same-time angle to baseline']):ax.set_xscale('symlog',linthresh=1e-4);ax.set_ylabel('Degrees');ax.set_xlabel('Time (s)');ax.set_title(title)
axes[1].legend(fontsize=5,ncol=2);fig.suptitle('m4 span persistence: no new scientific threshold');save('06_m4_span_persistence')
sr=pd.read_csv(OUT/'mixed_csp_mode_block/species_ranked_support.csv').head(8);rr=pd.read_csv(OUT/'mixed_csp_mode_block/reaction_ranked_support.csv').head(8);parts=[]
for typ,f,col in [('species',sr,'species'),('reaction',rr,'reaction_id')]:
 for _,row in f.iterrows():parts.append({'support_type':typ,'id':row[col],'mean_participation':row.mean_participation_valid_only,'canonical_equation':row.get('canonical_equation',''),'included_samples':row.number_included_samples})
write_csv(p/'07_m4_participation.csv',parts);fig,axes=plt.subplots(1,2,figsize=(12,5))
for ax,f,col in [(axes[0],sr,'species'),(axes[1],rr,'reaction_id')]:ax.barh(f[col].iloc[::-1],f.mean_participation_valid_only.iloc[::-1]);ax.set_xlabel('Mean participation over qualified samples')
fig.suptitle('m4 chemical support; excluded raw rows retained');save('07_m4_participation');print('Four geometric figures rendered',flush=True)
