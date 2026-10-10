/* Deterministic evidence-only UI. Data is embedded by the existing generator. */
(function(){
  'use strict';
  const D=PHASE_C, F='R3_CHAIN12_RECYCLE';
  if(!D) throw new Error('Phase C presentation payload missing');
  const $=id=>document.getElementById(id), esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const pct=n=>(n*100).toPrecision(7)+'%', num=n=>Number(n).toPrecision(8), M=Object.fromEntries(D.models.map(m=>[m.model,m]));
  const link=(p,label)=>'<a href="../../'+esc(p)+'">'+esc(label)+'</a>';
  const cert='docs/reduction/rapid_reduction/mathematical_certificate.json', map='docs/reduction/rapid_reduction/candidate_source_map.json';
  const reaction=id=>'<button class="reaction-btn" type="button" data-phase-reaction="'+id+'">'+id+'</button>';
  const rx=ids=>ids.map(x=>reaction('re000000'+x)).join(' ');
  const scope={R0:'规范参考 / 源模型',R1:'SOURCE_GENERAL · 精确守恒消元',R2:'AUTHOR_CONDITION · 精确支持面',R3_CHAIN1:'条件接受 · 一轮 Gly 动力学近似',R3_CHAIN12:'条件接受 · 两轮 Gly 动力学近似',R3_RECYCLE:'条件接受 · 精确观测商系统',R3_CHAIN12_RECYCLE:'条件接受 · 四场景长期近似候选'};
  function node(id,from,kind,body,ids){return '<div class="node '+kind+'"><h4>'+id+'</h4><div class="dims">'+from+' → '+M[id].independent_dimension+'</div><span class="tag">'+scope[id]+'</span><p>'+body+'</p><div>'+rx(ids)+'</div><p>'+link(cert,'数学证书')+' · '+link(map,'源映射')+'</p></div>';}
  function init(){
    const C=D.current_decision;
    $('phase-status').innerHTML='<b>'+esc(C.phase_c.scientific_status)+'</b><br><span class="fine">人工决定：'+esc(C.decision_date)+' · '+esc(C.phase_c.numerical_gate_status)+' 是独立的数值门结果。</span>';
    $('phase-dim').textContent=['R0','R1','R2',F].map(id=>M[id].independent_dimension).join(' → ');
    $('phase-stat').innerHTML=[['原始 species',D.source.species],['规范反应方向',D.source.canonical_directions],['作者正参数方向',D.source.positive_author_directions],['支持面潜在方向',D.source.support_directions]].map(x=>'<div class="stat">'+x[0]+'<strong>'+x[1]+'</strong></div>').join('');
    $('phase-counts').innerHTML='<b>'+M[F].independent_dimension+' 是化学状态维数，不是反应数。</b> 各版本另有 '+M[F].counter_dimension+' 个共同积分计数器；最终实际积分 '+(M[F].independent_dimension+M[F].counter_dimension)+' 个坐标，运行时计算 '+M[F].mass_action_expressions+' 个有效单项式。';
    $('phase-b1').innerHTML='<b>'+esc(C.b1_3.scientific_status)+'</b> · '+Object.entries(C.b1_3.gates).map(([k,v])=>esc(k)+': '+esc(typeof v==='string'?v:JSON.stringify(v))).join(' · ');
    $('phase-source').innerHTML='<b>R0 · '+M.R0.independent_dimension+' 化学维 · 规范参考</b> → R1 → R2。源范围：全部 '+D.source.canonical_directions+' 个规范 Reaction ID，所有原始身份保留。'+link('models/pnas2017_full_reference/original/fMGG_synthesis.xml','规范 SBML')+' · '+link(cert,'证书');
    $('phase-flow-exact').innerHTML=node('R1',M.R0.independent_dimension,'exact','源范围为全部 '+D.source.canonical_directions+' 个规范 Reaction ID；精确有理守恒，允许在声明物理域内重构完整源状态。',[])+node('R2',M.R1.independent_dimension,'exact','仅作者固定零参数和初值支持面。剔除恒零种，再按支持面守恒；不能解释为直接相减。',['0952'])+node('R3_RECYCLE',M.R2.independent_dimension,'quotient','回收尾态投影；保留资源、因子边际与受保护观测，丢失微观路径的唯一逆映射。',['0306','0910','0913','0916','0918']);
    $('phase-flow-chain').innerHTML=node('R3_CHAIN1',M.R2.independent_dimension,'approx','Gly 第一轮合并 slow + fast；保留其他网络、竞争出口与资源库存投影。',['0017','0018'])+node('R3_CHAIN12',M.R3_CHAIN1.independent_dimension,'approx','再加入第二轮 Gly 平均等待时间近似。与右上回收商系统同维，但数学含义不同。',['0078','0079'])+'<div class="node quotient"><h4>两条 '+M.R3_RECYCLE.independent_dimension+' 维支线保持独立</h4><p><b>R3_RECYCLE</b>：回收的精确观测投影。</p><p><b>R3_CHAIN12</b>：两轮 Gly 的近似聚合。</p><p>二者重组才得到最终候选。</p>'+link(map,'查看两个变换的独立源映射')+'</div>';
    $('phase-merged').innerHTML='<b>R3_CHAIN12 '+M.R3_CHAIN12.independent_dimension+' + 回收商系统 → '+F+' '+M[F].independent_dimension+'</b><p>条件接受：四个冻结场景、源时间长期窗口的全耦合数值候选。整体仍为近似，不是普适验证的 PURE 模型。</p>'+link(cert,'数学证书')+' · '+link(map,'逐变换源映射')+' · '+link('docs/reduction/rapid_reduction/phase_c_formal_acceptance_20261010.md','完整接受范围');
    $('phase-equations').innerHTML='<span>S ∈ Q<sup>'+D.source.species+'×'+D.source.canonical_directions+'</sup>；rank S = '+D.mathematics.source_rank+'；dim ker Sᵀ = '+D.mathematics.source_left_nullity+'</span><span>'+D.source.species+' = '+D.mathematics.author_support_species+' + '+D.mathematics.zero_count+'；'+D.mathematics.author_support_species+' − '+D.mathematics.charts.R2.law_rank+' = '+D.mathematics.support_live_rank+'</span><span>P A<sub>tail</sub> = Q P；'+D.quotient.microstates+' → '+D.quotient.observables+'</span>';
    $('phase-scenario').innerHTML=D.scenarios.map(s=>'<option>'+s.id+'</option>').join('');
    $('phase-observable').innerHTML='<optgroup label="源状态及受保护库存">'+D.observable_labels.map(s=>'<option>'+s+'</option>').join('')+'</optgroup><optgroup label="模型侧积分事件量">'+D.counter_names.map(s=>'<option>'+s+'</option>').join('')+'</optgroup>';
    $('phase-window').innerHTML=D.config.windows.map((w,i)=>'<option value="'+i+'">'+w.join('–')+(i===0?' · 初始层（默认）':i===1?' · 过渡层':' · 长期')+'</option>').join('');
    ['phase-scenario','phase-observable','phase-window'].forEach(id=>$(id).addEventListener('change',plot));
    $('phase-local').textContent='局部非零 fast 初值反例：初始层资源误差可达 '+pct(D.local_early_resource_error)+'；不是所有初始层都通过。';
    const max=M[F].maxima_long, rib=Math.max(...Object.values(D.ribosome_long_errors).flatMap(x=>Object.values(x)));
    $('phase-maxima').innerHTML=[['自由 Pept0003',max.peptide_max],['资源 / 因子',max.resource_max],['核糖体库存 / 占用',rib],['累计资源事件量',max.cumulative_max]].map(([k,v])=>'<div class="metric"><span>'+k+'</span><strong>'+pct(v)+'</strong><span>四场景长期最大归一化误差</span></div>').join('');
    const rows=D.scenarios.map(s=>{const c=D.comparisons[s.id][F].comparison,w=c.windows[2];return '<tr><td>'+s.id+'</td><td class="num">'+num(c.reference_endpoint_Pept0003)+'</td><td class="num">'+num(c.reduced_endpoint_Pept0003)+'</td>'+['peptide_max','resource_max','net_flux_rms_max','cumulative_max'].map(k=>'<td class="num">'+pct(w[k])+'</td>').join('')+'<td class="pass">'+esc(D.comparisons[s.id][F].status)+'</td></tr>';});
    $('phase-results').innerHTML=table(['冻结场景','R0 肽终点','171 肽终点','肽误差','资源误差','流量 RMS','累计事件误差','原报告数值状态'],rows);
    $('phase-gates').innerHTML=table(['指标','固定门（归一化比例）','百分数 / 绝对尺度'],Object.entries(D.config.gates).map(([k,v])=>'<tr><td>'+k+'</td><td class="num">'+v+'</td><td>'+(['peptide','resources','net_flux_rms','cumulative'].includes(k)?pct(v):'绝对门 / 数值门')+'</td></tr>'));
    $('phase-scale-rules').textContent=JSON.stringify(D.config.scale_rule,null,2);
    $('phase-runtime').innerHTML=table(['模型 / 化学维数','中位秒数','相对速度 R0 / 模型','初始 / 末端 Jacobian 非零元','有效单项式'],D.models.map(m=>'<tr><td>'+m.model+' / '+m.independent_dimension+'</td><td class="num">'+m.median_seconds.toFixed(4)+'</td><td class="num">'+m.speedup.toFixed(3)+'×</td><td class="num">'+m.Jacobian_nnz_initial+' / '+m.Jacobian_nnz_final+'<div class="mini-bar" style="width:'+(m.Jacobian_nnz_final/Math.max(...D.models.map(x=>x.Jacobian_nnz_final))*140)+'px"></div></td><td>'+m.mass_action_expressions+'</td></tr>'));
    $('phase-runtime-note').textContent='未实现计算提速（No computational speedup yet）。'+D.config.performance_repeats+' 次重复取中位，排除首次编译；均包含共同计数器和相同 dense-output 任务。末端 Jacobian 非零元：'+M.R0.Jacobian_nnz_final+' → '+M[F].Jacobian_nnz_final+'。稀疏坐标重构和 Jacobian 填充是受矩阵结构支持的工程假设，不是唯一因果证明。';
    mechanisms();
    $('phase-evidence-links').innerHTML=[['docs/reduction/pathways/phase_b1_3_formal_acceptance_20261010.md','B1-3 正式接受'],['docs/reduction/rapid_reduction/phase_c_formal_acceptance_20261010.md','Phase C 正式接受'],[cert,'当前 Phase C 数学证书'],[map,'候选源映射'],['docs/reduction/rapid_reduction/release_manifest_v1.json','完整发布清单'],['docs/reduction/rapid_reduction/release_evidence_navigation_v1.json','证据导航'],['results/reduction/rapid_v1/validation_results.json','原始数值报告'],['scripts/reduction/rapid_v1/runtime.py','实际运行实现'],['docs/visualization/phase_c_release_v1.json','本页数据 contract'],['docs/reduction/pathways/reaction_atlas_prototype.html','既有反应路径图谱']].map(x=>link(x[0],x[1])).join('');
    $('phase-inputs').innerHTML=table(['输入（仓库相对路径）','字节数','SHA-256'],D.inputs.map(i=>'<tr><td>'+link(i.path,i.path)+'</td><td>'+i.bytes+'</td><td class="hash">'+i.sha256+'</td></tr>'));
    $('phase-freshness').textContent=D.freshness.status+' · 构建时验证输入字节、冻结配置及全部已保存场景/窗口误差。本页面不声称重新执行 ODE；浏览器离线后不能监控磁盘变化。刷新检查：'+D.freshness.method;
    $('phase-decision-json').textContent=JSON.stringify(C,null,2);
    plot();
  }
  function table(head,rows){return '<table><thead><tr>'+head.map(x=>'<th>'+x+'</th>').join('')+'</tr></thead><tbody>'+rows.join('')+'</tbody></table>';}
  function plot(){
    const sc=$('phase-scenario').value, label=$('phase-observable').value, wi=Number($('phase-window').value), w=D.config.windows[wi], i=D.trajectory_labels.indexOf(label), comp=D.comparisons[sc][F].comparison;
    const indices=D.grid.map((t,j)=>t>=w[0]&&t<=w[1]?j:-1).filter(j=>j>=0), A=D.trajectories[sc].R0[i], B=D.trajectories[sc][F][i], scale=comp.fixed_scales[label]||comp.counter_fixed_scales[label];
    const all=indices.flatMap(j=>[A[j],B[j]]), rawMin=Math.min(...all),rawMax=Math.max(...all),span=rawMax-rawMin||Math.max(1e-20,Math.abs(rawMax)*.05), lo=rawMin-span*.06,hi=rawMax+span*.09;
    const W=1000,H=330,L=95,R=28,T=22,BT=49, x=t=>L+(t-w[0])/(w[1]-w[0])*(W-L-R),y=v=>H-BT-(v-lo)/(hi-lo)*(H-T-BT);
    let svg='<title>'+esc(sc+' '+label+' R0 and '+F+' source-time '+w.join('–'))+'</title><desc>实际保存采样点，无平滑或伪造；横轴源数值时间，纵轴源浓度或源累计事件量。</desc>';
    for(let j=0;j<=4;j++){const v=lo+(hi-lo)*j/4,yy=y(v),t=w[0]+(w[1]-w[0])*j/4,xx=x(t);svg+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+yy+'" y2="'+yy+'" stroke="#e3e7eb"/><text x="'+(L-9)+'" y="'+(yy+4)+'" text-anchor="end">'+v.toExponential(2)+'</text><text x="'+xx+'" y="'+(H-24)+'" text-anchor="middle">'+Number(t.toPrecision(4))+'</text>';}
    function path(V){return indices.map((j,k)=>(k?'L':'M')+x(D.grid[j]).toFixed(3)+','+y(V[j]).toFixed(3)).join(' ');}
    svg+='<path d="'+path(A)+'" fill="none" stroke="#174b70" stroke-width="2.6"/><path d="'+path(B)+'" fill="none" stroke="#c17415" stroke-width="2.1" stroke-dasharray="8 5"/>';
    svg+='<text x="'+L+'" y="13">'+esc(label)+' · '+(i<D.observable_labels.length?'源浓度尺度':'源累计事件量')+'</text><text x="'+((W+L-R)/2)+'" y="'+(H-3)+'" text-anchor="middle">源数值时间（未解释为秒）</text>';
    $('phase-plot').innerHTML=svg;
    let max=0;indices.forEach(j=>{max=Math.max(max,Math.abs(A[j]-B[j])/scale)});
    $('phase-plot-note').textContent='所选窗口最大 |171 − R0_TIGHT| / 固定初值尺度 '+num(scale)+' = '+pct(max)+'；'+indices.length+' 个原始保存点。默认展示初始层；曲线重合不代表数学精确。'+(Math.max(Math.abs(rawMin),Math.abs(rawMax))<D.config.solver.atol?' 此窗口量级低于求解器绝对容差 '+D.config.solver.atol+'；勿把放大的曲线差异解释为精确动力学差异。':'');
    $('phase-scales').textContent=JSON.stringify({scenario:sc,initial_overrides:D.scenarios.find(s=>s.id===sc).initial_overrides,fixed_scales:comp.fixed_scales,counter_fixed_scales:comp.counter_fixed_scales},null,2);
    $('phase-window-results').innerHTML=table(['源时间窗口','肽最大误差','资源/因子最大误差','流量 RMS','累计事件量','最差资源'],comp.windows.map((r,j)=>'<tr><td>'+r.range.join('–')+(j===0?' · 初始层':j===2?' · 门适用长期':'')+'</td>'+['peptide_max','resource_max','net_flux_rms_max','cumulative_max'].map(k=>'<td class="num">'+pct(r[k])+'</td>').join('')+'<td>'+esc(r.worst_resource)+'</td></tr>'));
    $('phase-point-data').innerHTML=table(['源时间','R0','171','归一化绝对误差'],indices.map(j=>'<tr><td class="num">'+num(D.grid[j])+'</td><td class="num">'+num(A[j])+'</td><td class="num">'+num(B[j])+'</td><td class="num">'+pct(Math.abs(A[j]-B[j])/scale)+'</td></tr>'));
  }
  function mechanisms(){
    const cb=D.mathematics.closure_counterexamples,rf=cb.find(c=>c.candidate==='RF1_RF2_SHARED_POST_ENDPOINT_MERGE'), fraction=s=>{const a=s.split('/').map(Number);return a.length===2?a[0]/a[1]:a[0];};
    const content=[
      ['起始接口','源起始网络保持；第一轮 Gly 的上游载体和共享核糖体/因子库存保持。源身份不等于生理时序或完整肽化学认证。',['0001','0016']],
      ['两轮 Gly 聚合','各轮 kᵦ = '+cb[0].approximate_rate+'；平均等待时间 '+cb[0].mean_wait+'。匹配均值，不匹配完整等待时间分布；原系统同投影状态的肽键导数可为 '+cb[0].projected_product_derivative_a+' 与 '+cb[0].projected_product_derivative_b+'，故精确 lumpability 被拒绝。',['0017','0018','0078','0079']],
      ['RF1 / RF2 终止：禁止精确合并','同一 bound-ribosome 总量 '+rf.same_aggregate_bound_ribosome+'，RF1: k = '+fraction(rf.Pept0003_derivative_a)+'；RF2: k = '+fraction(rf.Pept0003_derivative_b)+'。自由 Pept0003 释放导数不同，必须保留竞争入口、活跃逆向和作者禁用方向。',['0796','0797','0798','0811','0812','0813','0810','0823']],
      ['RF3 备选通路','直接释放与 RF3 交换是替代路径；未实验排名主导机制。RF3、核苷酸供应是明确边界条件。',['0799','0814','0847']],
      ['RRF / EF-G 核糖体回收','re0000000910 是 70S splitting。随后的自由组分释放是独立源事件；有限 EF-G–GTP、RRF 供应仍显式保留。',['0902','0910','0911','0913','0916','0918']],
      ['精确 '+D.quotient.microstates+' → '+D.quotient.observables+' 回收观测商系统','P A_tail = Q P。保留 N3、N2、bound-tRNA / RRF / EFG 边际，保留 0306 与 0910 外部输入。两维微观相关性无唯一逆，个别 gross 路径 extent 不可恢复。',['0306','0910','0913','0916','0918']]
    ];
    function side(s){return Object.entries(s).map(([k,v])=>(Number(v)===1?'':v+' ')+k).join(' + ')||'∅';}
    $('phase-mechanisms').innerHTML=content.map(([title,desc,ids])=>'<article class="mechanism"><h4>'+title+'</h4><p>'+desc+'</p>'+rx(ids)+'<p>'+link(map,'完整源映射 / 边界')+' · '+link(cert,'数学证书')+' · '+link('docs/reduction/rapid_reduction/reduction_report.md','历史科学报告')+'</p><details><summary>原始反应方程与作者参数</summary>'+ids.map(x=>{const r=D.reactions['re000000'+x];return '<div class="equation"><b>'+r.id+'</b> · k = '+r.author_k_exact+'<br>'+esc(side(r.reactants))+' → '+esc(side(r.products))+'</div>';}).join('')+'</details></article>').join('');
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
