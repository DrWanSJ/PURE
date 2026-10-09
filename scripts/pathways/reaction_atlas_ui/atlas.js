"use strict";
(() => {
  const data = JSON.parse(document.getElementById("atlas-data").textContent);
  const PAGE_SIZE = 24;
  const phaseIds = new Set(data.phase_a_ids);
  const contexts = Object.fromEntries(data.groups.flatMap(g => g.contexts.map(c => [c.id, {...c, group: g}])));
  const pathMembership = Object.fromEntries(Object.keys(data.reactions).map(rid => [rid, Object.values(data.paths).filter(p => p.reaction_ids.includes(rid)).map(p => p.id)]));
  const state = {mode: "functional", context: "RS_binding", substep: null, enzyme: null, path: "GlyRS-P01", loop: null,
    page: 0, query: "", searchKind: "reactions", positiveOnly: false, speciesFilter: null, customIds: null, rid: null, focusState: null};
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[c]));
  const sortedUnique = xs => [...new Set(xs)].sort();
  const isSink = sid => sid.endsWith("_degraded");
  const isDisabled = rid => data.reactions[rid].reference_activity === "REFERENCE_DISABLED";
  const tag = (text, cls="") => `<span class="tag ${cls}">${esc(text)}</span>`;
  const ridButton = rid => `<button type="button" class="reaction-link" data-action="reaction" data-rid="${esc(rid)}">${esc(rid)}</button>`;
  const speciesButton = sid => `<button type="button" class="species-token" data-action="state" data-state="${esc(sid)}">${esc(sid)}</button>`;
  const reactionTags = rid => data.reactions[rid].level_c.map(c => tag(c, "code")).join("") + (isDisabled(rid) ? tag("REFERENCE_DISABLED", "disabled") : "");
  const phaseStatus = rid => phaseIds.has(rid) ? (data.noncarrier_ids.includes(rid) ? "PHASE_A_NONCARRIER_CHANNEL · PATHWAY_NOT_RECONSTRUCTED" : "PHASE_A_STRUCTURAL_GRAPH") : "PATHWAY_NOT_RECONSTRUCTED";
  const topologyTypes = t => t.types.map(type => type === "REJOIN" && t.carrier_after.some(isSink) ? "SINK_CONVERGENCE" : type);

  // Exact rational arithmetic. Decimal/scientific source numbers are converted
  // to integer ratios, and a reaction is added once per actual path occurrence.
  const gcd = (a,b) => {a=a<0n?-a:a; b=b<0n?-b:b; while(b){[a,b]=[b,a%b];} return a || 1n;};
  const normalize = (n,d) => {if(!d) throw Error("Zero rational denominator"); if(d<0n){n=-n;d=-d;} const g=gcd(n,d); return [n/g,d/g];};
  function rational(value) {
    const text = String(value).trim();
    if(text.includes("/")){const [a,b]=text.split("/");return normalize(BigInt(a),BigInt(b));}
    const match = /^([+-]?)(\d+)(?:\.(\d*))?(?:[eE]([+-]?\d+))?$/.exec(text);
    if(!match) throw Error("Unsupported exact coefficient: "+text);
    const fraction=match[3]||"", exponent=Number(match[4]||0)-fraction.length;
    let n=BigInt(match[2]+fraction)*(match[1]==="-"?-1n:1n), d=1n;
    if(exponent>=0)n*=10n**BigInt(exponent);else d=10n**BigInt(-exponent);
    return normalize(n,d);
  }
  const addRat=(a,b)=>normalize(a[0]*b[1]+b[0]*a[1],a[1]*b[1]);
  const ratString=([n,d])=>d===1n?String(n):`${n}/${d}`;
  function netForIds(ids) {
    const net={};
    for(const rid of ids){
      const r=data.reactions[rid]; if(!r)throw Error("Unknown original Reaction ID: "+rid);
      for(const [side,sign] of [["reactants",-1n],["products",1n]])for(const [sid,value] of Object.entries(r[side])){
        const [n,d]=rational(value);net[sid]=addRat(net[sid]||[0n,1n],[sign*n,d]);
      }
    }
    return Object.fromEntries(Object.keys(net).sort().filter(s=>net[s][0]!==0n).map(s=>[s,ratString(net[s])]));
  }
  function netSides(net) {
    const consumed={},produced={};
    for(const [sid,value] of Object.entries(net)){const [n,d]=rational(value);if(n<0n)consumed[sid]=ratString([-n,d]);else if(n>0n)produced[sid]=ratString([n,d]);}
    return [consumed,produced];
  }
  function plainSide(side) {return Object.entries(side).map(([s,n])=>(rational(n)[0]===rational(n)[1]?"":n+" ")+s).join(" + ")||"∅";}
  function netEquation(net) {const [a,b]=netSides(net);return plainSide(a)+" -> "+plainSide(b);}
  function htmlSide(side) {return Object.entries(side).map(([s,n])=>(rational(n)[0]===rational(n)[1]?"":esc(n)+" ")+speciesButton(s)).join(" + ")||"∅";}
  const equationHTML = rid => `<span>${htmlSide(data.reactions[rid].reactants)}</span><span class="arrow"> → </span><span>${htmlSide(data.reactions[rid].products)}</span>`;
  function sameExactSide(a,b) {
    const keys=Object.keys(a).sort(),other=Object.keys(b).sort();
    return keys.length===other.length && keys.every((s,i)=>s===other[i] && ratString(rational(a[s]))===ratString(rational(b[s])));
  }
  function getExactReverseDisplay(reactionId,sourceData) {
    const reactions=sourceData.reactions,r=reactions[reactionId];
    if(!r)throw Error("Unknown original Reaction ID: "+reactionId);
    const partners=rid=>Object.keys(reactions).filter(id=>id!==rid &&
      sameExactSide(reactions[rid].reactants,reactions[id].products) &&
      sameExactSide(reactions[rid].products,reactions[id].reactants));
    const matches=partners(reactionId),partner=matches[0];
    // A reviewed pointer alone is insufficient: require complete side swaps,
    // reciprocal pointers and uniqueness on BOTH sides. Never use net vectors.
    const paired=matches.length===1 && r.reverse===partner && reactions[partner].reverse===reactionId &&
      partners(partner).length===1;
    const [forwardId,reverseId]=paired?[reactionId,partner].sort():[reactionId,null];
    const orientation=reactions[forwardId];
    return {forwardId,reverseId,reactants:orientation.reactants,products:orientation.products,
      currentId:reactionId,currentDirection:reactionId===forwardId?"→":"←",
      pairValidationStatus:paired?"EXACT_UNIQUE_SOURCE_PAIR":"UNPAIRED",
      directionalActivity:Object.fromEntries([forwardId,reverseId].filter(Boolean).map(id=>
        [id,reactions[id].reference_activity==="REFERENCE_DISABLED"?"REFERENCE_DISABLED":"REFERENCE_ENABLED"]))};
  }
  function mechanismDescription(reactionId,sourceData,bidirectional=false) {
    const r=sourceData.reactions[reactionId],t=sourceData.transitions[reactionId];
    // Reading templates apply only to the published Phase A enzyme projection
    // and reviewed RS labels. Species names alone never create a mechanism.
    if(!r || !t || !sourceData.phase_a_ids.includes(reactionId) ||
      !r.level_c.some(c=>["RS_binding","RS_activation","RS_charging"].includes(c)))return "";
    const inputs=Object.keys(t.other_reactants),outputs=Object.keys(t.other_products);
    if(r.mechanism==="HETERODIMER_ASSOCIATION" && inputs.length && !outputs.length){
      const carrier=t.carrier_before.length===1 && t.carrier_before[0]===t.enzyme?`游离 ${t.enzyme} `:"酶结合态复合物";
      return `${plainSide(t.other_reactants)} 与${carrier}结合形成复合物。${bidirectional?"逆向通道对应复合物解离。":""}`;
    }
    if(r.mechanism==="DISSOCIATION" && outputs.length && !inputs.length)
      return `酶结合态复合物释放 ${plainSide(t.other_products)}。${bidirectional?"逆向通道对应该组分重新结合。":""}`;
    if(r.mechanism==="STATE_TRANSITION" && r.level_c.includes("RS_activation"))
      return "酶结合态在 ATP 装配状态与 aminoacyl-AMP / PPi 中间体之间转换。";
    if(r.mechanism==="STATE_TRANSITION" && r.level_c.includes("RS_charging"))
      return "酶结合态在 aminoacyl-AMP 与 aminoacyl-tRNA 状态之间转换。";
    return "按原始方程发生载体状态变化。";
  }
  function getCompetingOutlets(before,enzyme,sourceData) {
    return Object.keys(sourceData.transitions).filter(rid=>{
      const t=sourceData.transitions[rid];return t.enzyme===enzyme && t.carrier_before.includes(before);
    }).sort();
  }
  function cycleCertificate(path,net) {
    return Boolean(path.target_product && path.types.includes("PRODUCTIVE_PATH") && path.start===path.end && path.start===path.enzyme &&
      data.modules[path.enzyme].carrier_states.every(s=>!net[s]) && rational(net[path.target_product]||"0")[0]>0n);
  }
  function speciesChips(ids) {
    const first=ids.slice(0,8),rest=ids.slice(8);
    return `<div class="species-chips">${first.map(speciesButton).join("")}</div>`+(rest.length?`<details class="more-species"><summary>另外 ${rest.length} 个物种</summary><div class="species-chips">${rest.map(speciesButton).join("")}</div></details>`:"");
  }
  function reactionCard(rid) {
    const r=data.reactions[rid];
    return `<article class="reaction-card" data-reaction-card="${esc(rid)}"><div class="card-top">${ridButton(rid)}<span class="card-meta">${esc(r.family)}</span></div><div class="equation">${equationHTML(rid)}</div><div class="tag-row">${reactionTags(rid)}</div></article>`;
  }
  function pagedReactionList(ids) {
    const pages=Math.max(1,Math.ceil(ids.length/PAGE_SIZE));state.page=Math.min(state.page,pages-1);
    const shown=ids.slice(state.page*PAGE_SIZE,(state.page+1)*PAGE_SIZE);
    return `<div class="reaction-list" data-visible-reaction-count="${shown.length}">${shown.map(reactionCard).join("")}</div>`+
      `<div class="pager"><span>${ids.length?state.page*PAGE_SIZE+1:0}–${Math.min(ids.length,(state.page+1)*PAGE_SIZE)} / ${ids.length}</span><div><button type="button" data-action="page" data-delta="-1" ${state.page===0?"disabled":""}>上一页</button> <button type="button" data-action="page" data-delta="1" ${state.page===pages-1?"disabled":""}>下一页</button></div></div>`;
  }
  function renderHierarchy() {
    $("hierarchy").innerHTML=data.groups.map(group=>`<details class="nav-group" data-group="${group.id}" ${group.id==="RS"?"open":""}><summary>${esc(group.title)}</summary>`+
      group.contexts.map(c=>`<details class="nav-context" data-context="${c.id}" ${c.id==="RS_binding"?"open":""}><summary class="context-summary"><button type="button" data-action="context" data-context="${c.id}">${esc(c.id)}</button><span class="count">${c.reaction_ids.length}</span></summary>`+
        c.substeps.map(s=>`<details class="nav-sub" data-substep="${s.id}"><summary>${esc(s.title)}</summary>`+
          (s.mapping_status==="SOURCE_DERIVED_UI_GROUPING"?["GlyRS","MetRS"].map(e=>`<button type="button" data-action="substep" data-context="${c.id}" data-substep="${s.id}" data-enzyme="${e}">${e} · ${s.reaction_ids.filter(rid=>data.transitions[rid]?.enzyme===e).length} reactions</button>`).join(""):
            `<button type="button" data-action="substep" data-context="${c.id}" data-substep="${s.id}">Other / 原始 Level-C 集合</button>`)+
          `<span class="mapping-dot">${s.mapping_status==="SOURCE_DERIVED_UI_GROUPING"?"源方程阅读分组 · 待人工确认":"SUBSTEP_MAPPING_NOT_VALIDATED"}</span></details>`).join("")+`</details>`).join("")+`</details>`).join("");
  }
  function selectedIds() {
    let ids=state.customIds|| (state.context?contexts[state.context].reaction_ids:Object.keys(data.reactions));
    if(state.substep)ids=contexts[state.context].substeps.find(s=>s.id===state.substep).reaction_ids;
    if(state.enzyme)ids=ids.filter(rid=>data.transitions[rid]?.enzyme===state.enzyme || Object.keys(data.reactions[rid].reactants).concat(Object.keys(data.reactions[rid].products)).some(s=>s.includes(state.enzyme=== "GlyRS"?"Gly":"Met")));
    if(state.speciesFilter)ids=ids.filter(rid=>data.reactions[rid].reactants[state.speciesFilter]||data.reactions[rid].products[state.speciesFilter]);
    return [...ids].sort();
  }
  function pathChooser() {
    return `<section class="chooser"><h3>沿 GlyRS / MetRS 的连续路径阅读</h3><p class="small">分类负责导航；选择路径后保留跨 Level-C 的完整反应链。</p>`+
      Object.entries(data.modules).map(([enzyme,m])=>`<details class="enzyme-chooser" data-enzyme="${enzyme}" ${enzyme==="GlyRS"?"open":""}><summary>${enzyme} · ${m.path_ids.length} 条代表路径</summary><div class="path-grid">`+
        m.path_ids.map(id=>`<button type="button" class="path-choice" data-action="path" data-path="${id}"><b>${id}</b><span>${esc(data.paths[id].title)}</span></button>`).join("")+`</div><details><summary class="small">逆向与局部返回 · ${m.return_loops.length} 个有限见证</summary><div class="loop-list">`+
        m.return_loops.map(l=>`<button type="button" data-action="loop" data-enzyme="${enzyme}" data-loop="${l.id}">${l.id}${l.reference_feasible?"":" · 禁用边"}</button>`).join("")+`</div></details></details>`).join("")+`</section>`;
  }
  function functionalView() {
    const c=state.context?contexts[state.context]:null,sub=state.substep?c.substeps.find(s=>s.id===state.substep):null;
    const ids=selectedIds(),shown=state.positiveOnly?ids.filter(rid=>!isDisabled(rid)):ids;
    const inputs=sortedUnique(ids.flatMap(rid=>Object.keys(data.reactions[rid].reactants))),outputs=sortedUnique(ids.flatMap(rid=>Object.keys(data.reactions[rid].products)));
    const phaseContext=Boolean(c&&["RS_binding","RS_activation","RS_charging"].includes(c.id));
    const title=state.speciesFilter?state.speciesFilter:state.customIds?"外部 carrier handoff · 源反应":sub?sub.title:c?c.id:"Reaction Source Index";
    const caption=c?c.function:"按原始 Reaction ID 浏览完整源反应；分页显示，全部方程可立即打开。";
    let body=`<div class="section-kicker">${c?esc(c.group.title):"ALL ORIGINAL REACTIONS"}</div><h2>${esc(title)}</h2><p class="subtitle">${esc(caption)}</p>`;
    body+=`<div class="tag-row">${tag(`${ids.length} unique Reaction IDs`)}${tag("ORIGINAL_REACTIONS_AVAILABLE")}${phaseContext?tag("PHASE_A_PATHWAYS_ONLY"):tag("PATHWAY_NOT_RECONSTRUCTED","pending")}${tag("HUMAN_REVIEW_REQUIRED","pending")}</div>`;
    if(sub)body+=`<div class="notice neutral" data-mapping-status="${sub.mapping_status}">${sub.mapping_status==="SOURCE_DERIVED_UI_GROUPING"?"SOURCE_DERIVED_UI_GROUPING：按源方程识别的阅读分组，未改动原始科学标签；待科研人员确认。":"SUBSTEP_MAPPING_NOT_VALIDATED：这是阅读主题。以下展示其父 Level-C 的原始集合，不声称已经完成本子步骤的反应划分。"}</div>`;
    body+=`<section class="summary-box" data-summary-kind="FUNCTIONAL" data-net-unique="false"><div class="summary-kind">TYPE A · FUNCTIONAL SUMMARY</div><h3>这个过程涉及什么？</h3>`;
    if(sub?.mapping_status==="SOURCE_DERIVED_UI_GROUPING")body+=`<p class="small">${["GlyRS","MetRS"].map(e=>`${e}：${ids.filter(rid=>data.transitions[rid]?.enzyme===e).length} 条原始方向`).join(" · ")}</p>`;
    body+=`<div class="io-grid"><div><div class="io-label">涉及输入 · 参与物种集合</div>${speciesChips(inputs)}</div><div><div class="io-label">涉及输出 · 参与物种集合</div>${speciesChips(outputs)}</div></div><p class="net-note" id="functional-net-note">无唯一净反应——本集合包含替代入口、逆向或竞争出口，不对分类内全部反应求和。</p></section>`;
    if(phaseContext)body+=pathChooser();
    else body+=`<div class="notice neutral" data-pathway-status="PATHWAY_NOT_RECONSTRUCTED">本分类可查看原始反应与审核标签。完整 carrier-based pathway 尚未重构：PATHWAY_NOT_RECONSTRUCTED · PHASE_B_NOT_AUTHORIZED。</div>`;
    body+=`<h3>原始反应</h3><p class="source-counter">当前显示 ${shown.length} / ${ids.length} 个分类内 ID。筛选不改变 968 / 968 源网络覆盖。</p>`+pagedReactionList(shown);
    return body;
  }
  function pathStep(rid,before,after,number) {
    const t=data.transitions[rid],display=getExactReverseDisplay(rid,data),paired=Boolean(display.reverseId);
    const outlets=t?getCompetingOutlets(before,t.enzyme,data):[];
    const description=mechanismDescription(display.forwardId,data,paired);
    const pairIds=[display.forwardId,display.reverseId].filter(Boolean);
    return `<article class="path-step ${state.focusState===before?"focused-step":""}" data-step="${number}" data-rid="${rid}" data-before="${esc(before)}" data-after="${esc(after)}" data-pair-status="${display.pairValidationStatus}" data-display-ids="${pairIds.join(",")}"><span class="step-number">${String(number).padStart(2,"0")}</span>`+
      `<div class="card-top">${ridButton(display.forwardId)}${paired?`<span class="pair-link" aria-hidden="true">↔</span>${ridButton(display.reverseId)}`:""}</div>`+
      `<div class="tag-row">${data.reactions[rid].level_c.map(c=>tag(c,"code")).join("")}</div>`+
      `<div class="equation"><span>${htmlSide(display.reactants)}</span><span class="arrow"> ${paired?"⇌":"→"} </span><span>${htmlSide(display.products)}</span></div>`+
      (description?`<p class="mechanism-description">${esc(description)}</p>`:"")+
      `<div class="path-direction">当前路径：<b>${display.currentDirection} ${esc(rid)}</b></div>`+
      (paired?`<div class="directional-activity" aria-label="两个方向的参考参数状态">${pairIds.map((id,i)=>`<div data-direction-rid="${id}" class="${isDisabled(id)?"disabled-direction":""}"><span>${i===0?"→":"←"} ${id}</span><span class="activity-label">${display.directionalActivity[id]}</span></div>`).join("")}</div>`:isDisabled(rid)?`<div class="tag-row">${tag("REFERENCE_DISABLED","disabled")}</div>`:"")+
      `<div class="step-tools">${outlets.length>1?`<button type="button" class="competition-button" data-action="state" data-state="${esc(before)}" data-outgoing-count="${outlets.length}" aria-label="查看 ${esc(before)} 的竞争出口（${outlets.length}）" title="前体状态：${esc(before)}">查看竞争出口 (${outlets.length})</button>`:""}<button type="button" data-action="reaction" data-rid="${rid}">技术详情</button></div></article>`;
  }
  function netSummary(path,net,complete) {
    const [a,b]=netSides(net),supported=path.reaction_ids.every(rid=>!isDisabled(rid));
    return `<section class="summary-box" data-summary-kind="${complete?"CATALYTIC_CYCLE":"PATH_NET"}" data-reference-supported="${supported}"><div class="summary-kind">${complete?"TYPE C · COMPLETE CATALYTIC CYCLE":"TYPE B · PATH NET STOICHIOMETRY"}</div><h3>${complete?"完整催化循环的净反应":"选定路径的净计量变化"}</h3><div class="net-equation" id="net-equation" data-net-vector="${esc(JSON.stringify(net))}">${htmlSide(a)} <span class="arrow">→</span> ${htmlSide(b)}</div><div class="io-grid"><div><div class="io-label">净消耗</div>${speciesChips(Object.keys(a))}</div><div><div class="io-label">净生成</div>${speciesChips(Object.keys(b))}</div></div><p class="net-note">按实际反应出现次数，对原始计量逐项相加。${complete?"起点酶已恢复，内部酶载体状态抵消。":"这是入口 / 返回段的计量变化，不标为完整产物催化循环。"} 不表示实际通量或共同动力学时间尺度。</p>${supported?"":`<p class="net-note">含 REFERENCE_DISABLED：只展示源结构，不表示参考参数支持此路径。</p>`}</section>`;
  }
  function pathwayView() {
    if(state.context && !["RS_binding","RS_activation","RS_charging"].includes(state.context))return `<h2>${esc(state.context)}</h2><div class="notice" data-pathway-status="PATHWAY_NOT_RECONSTRUCTED">PATHWAY_NOT_RECONSTRUCTED · PHASE_B_NOT_AUTHORIZED。本模块本轮仅提供源反应；请切换 Functional View 查看。</div>`;
    let p=state.loop?data.modules[state.loop.enzyme].return_loops.find(l=>l.id===state.loop.id):data.paths[state.path];
    if(!p)return pathChooser();
    if(state.loop)p={...p,title:"有限局部返回见证",enzyme:state.loop.enzyme,start:p.states[0],end:p.states.at(-1),target_product:null,types:["RETURN_LOOP"],rejoins:[],shared_continuations:[]};
    const net=netForIds(p.reaction_ids),complete=cycleCertificate(p,net);
    let body=`<div class="path-header"><div class="section-kicker">${esc(p.enzyme)} · CARRIER-STATE PATHWAY</div><h2 id="selected-path-title">${esc(p.id)}</h2><p class="subtitle">${esc(p.title)}</p><div class="tag-row">${p.types.map(t=>tag(t)).join("")}${tag("PHASE_A_PATHWAYS_ONLY")}${tag("HUMAN_REVIEW_REQUIRED","pending")}</div><div class="endpoints"><div>起点<b>${esc(p.start)}</b></div><span>→</span><div>终点<b>${esc(p.end)}</b></div></div></div>`+netSummary(p,net,complete);
    if(state.positiveOnly)body+=`<p class="small">参数筛选只作用于源反应列表；此处保留所选路径的每个原始步骤。</p>`;
    const displays=p.reaction_ids.map(rid=>getExactReverseDisplay(rid,data));
    const pairedCards=displays.filter(d=>d.reverseId).length,displayIds=sortedUnique(displays.flatMap(d=>[d.forwardId,d.reverseId].filter(Boolean)));
    body+=`<p class="path-counts" data-path-step-count="${p.reaction_ids.length}" data-paired-card-count="${pairedCards}" data-displayed-id-count="${displayIds.length}">${p.reaction_ids.length} 个有向路径步骤 · ${pairedCards} 张双向卡片 · 卡片涉及 ${displayIds.length} 个原始方向</p><p class="pair-note">⇌ 表示源模型存在两个精确相反的通道；不表示平衡、相同速率或两向均启用。REFERENCE_ENABLED 仅表示该方向参考参数非零。</p>`;
    body+=`<div class="path-steps" id="path-steps" data-path-id="${esc(p.id)}">`+p.reaction_ids.map((rid,i)=>pathStep(rid,p.states[i],p.states[i+1],i+1)).join("")+`</div>`;
    for(const link of p.rejoins){
      const target=data.paths[link.path_id],index=target.states.indexOf(link.state),next=target.reaction_ids[index];
      body+=`<button type="button" class="rejoin-link" data-action="rejoin" data-path="${link.path_id}" data-state="${esc(link.state)}"><strong>REJOIN · ${esc(link.state)}</strong><code>继续至 ${link.path_id}${next?" / "+next:""}</code></button>`;
    }
    for(const link of p.shared_continuations)body+=`<button type="button" class="rejoin-link" data-action="rejoin" data-path="${link.path_id}" data-state="${esc(link.state)}"><strong>共享后缀在 ${esc(link.state)} 汇合</strong><code>${link.path_id} / ${link.reaction_ids.map(esc).join(" → ")}</code></button>`;
    body+=`<div class="finish-marker">${p.start===p.end?"↺ 返回起始载体状态：":"本入口抵达真实状态："}<code>${esc(p.end)}</code>${complete?" · 酶恢复，产物已释放":""}</div>`;
    const boundary=data.boundary_links.filter(b=>b.module===p.enzyme);
    body+=`<details class="handoff-box"><summary>外部 carrier handoff 边界 · ${boundary.length} 条源 incidence</summary><p>PATHWAY_NOT_RECONSTRUCTED · HUMAN_REVIEW_REQUIRED。这里只确认完整源反应中的消耗或生成关系，不把 EF-Tu / MTF / ribosome 接口串成新路径。</p><button type="button" data-action="boundary" data-enzyme="${p.enzyme}">查看本酶全部外部接口源反应</button></details>`;
    body+=`<details class="chooser"><summary>其他代表路径、逆向与返回见证</summary>${pathChooser()}</details>`;
    return body;
  }
  function searchResults() {
    const q=state.query.toLowerCase();
    const result={reactions:Object.keys(data.reactions).filter(rid=>{const r=data.reactions[rid];return [rid,r.equation,r.family,...r.level_c].some(x=>x.toLowerCase().includes(q));}).filter(rid=>!state.positiveOnly||!isDisabled(rid)),
      species:Object.keys(data.species).filter(s=>s.toLowerCase().includes(q)||data.species[s].name.toLowerCase().includes(q)),
      paths:Object.keys(data.paths).filter(id=>id.toLowerCase().includes(q)||data.paths[id].title.toLowerCase().includes(q))};
    if(!result[state.searchKind].length&&result.paths.length)state.searchKind="paths";
    let body=`<div class="section-kicker">SOURCE SEARCH · OFFLINE</div><h2>搜索：${esc(state.query)}</h2><p class="small">Reaction ID、物种、RFAM 和路径均来自同一份内嵌源数据。</p><div class="results-tabs">${[["reactions","反应"],["species","Species"],["paths","路径"]].map(([key,label])=>`<button type="button" class="${state.searchKind===key?"active":""}" data-action="search-kind" data-kind="${key}">${label} ${result[key].length}</button>`).join("")}</div>`;
    if(state.searchKind==="reactions")return body+pagedReactionList(result.reactions);
    if(state.searchKind==="paths")return body+`<div class="path-grid">`+result.paths.map(id=>`<button type="button" class="path-choice" data-action="path" data-path="${id}"><b>${id}</b><span>${esc(data.paths[id].title)}</span></button>`).join("")+`</div>`;
    const pages=Math.max(1,Math.ceil(result.species.length/PAGE_SIZE));state.page=Math.min(state.page,pages-1);
    return body+`<div class="reaction-list">`+result.species.slice(state.page*PAGE_SIZE,(state.page+1)*PAGE_SIZE).map(s=>`<div class="result-species"><button type="button" data-action="state" data-state="${esc(s)}">${esc(s)}</button><button type="button" class="quiet" data-action="species-reactions" data-state="${esc(s)}">关联源反应</button></div>`).join("")+`</div><div class="pager"><span>Species · 第 ${state.page+1} / ${pages} 页</span><div><button type="button" data-action="page" data-delta="-1" ${state.page===0?"disabled":""}>上一页</button><button type="button" data-action="page" data-delta="1" ${state.page===pages-1?"disabled":""}>下一页</button></div></div>`;
  }
  function render() {
    $("functional-mode").setAttribute("aria-pressed",String(state.mode==="functional"));$("pathway-mode").setAttribute("aria-pressed",String(state.mode==="pathway"));
    $("positive-only").checked=state.positiveOnly;
    document.querySelectorAll("#hierarchy [data-action='context']").forEach(b=>b.classList.toggle("selected",b.dataset.context===state.context));
    $("content").innerHTML=state.query?searchResults():state.mode==="pathway"?pathwayView():functionalView();
  }
  function renderInspector(rid) {
    const r=data.reactions[rid],t=data.transitions[rid];if(!r)return;
    state.rid=rid;
    const paths=pathMembership[rid],coeffList=side=>`<ul class="coefficients">${Object.entries(side).map(([s,n])=>`<li><b>${esc(n)}</b><span>${esc(s)}</span></li>`).join("")||"<li>无</li>"}</ul>`;
    let html=`<h2 id="inspector-rid">${rid}</h2><code class="inspector-equation" id="inspector-equation">${esc(r.equation)}</code><div class="copy-row"><button type="button" data-action="copy" data-copy="rid">复制 Reaction ID</button><button type="button" data-action="copy" data-copy="equation">复制方程</button></div><div class="tag-row">${reactionTags(rid)}</div><div class="field-title">REACTION FAMILY</div><code>${esc(r.family)}</code><div class="field-title">路径状态</div><div class="status-note" id="inspector-pathway-status">${phaseStatus(rid)}${!phaseIds.has(rid)?" · ORIGINAL_REACTIONS_AVAILABLE · HUMAN_REVIEW_REQUIRED":" · STRUCTURALLY_SUPPORTED · HUMAN_REVIEW_REQUIRED"}</div><div class="field-title">REACTANTS · 原始计量系数</div>${coeffList(r.reactants)}<div class="field-title">PRODUCTS · 原始计量系数</div>${coeffList(r.products)}`;
    html+=`<div class="field-title">CARRIER BEFORE / AFTER</div>`;
    if(t){html+=`<div class="carrier-field"><span>Carrier before</span><div id="inspector-carrier-before" data-species="${esc(JSON.stringify(t.carrier_before))}">${t.carrier_before.map(speciesButton).join(" + ")}</div><span>Carrier after</span><div id="inspector-carrier-after" data-species="${esc(JSON.stringify(t.carrier_after))}">${t.carrier_after.map(speciesButton).join(" + ")}</div></div>`;
      html+=t.tracked_carriers.map(p=>`<div class="tracked-carrier"><b>${esc(p.carrier)}</b><br>${p.before.map(esc).join(" + ")||"∅"} → ${p.after.map(esc).join(" + ")||"∅"}<br><span class="small">INFERRED_IDENTITY_PROJECTION · 同时保留</span></div>`).join("");
      html+=`<div class="field-title">OTHER REQUIRED REACTANTS</div><div id="inspector-other-reactants">${coeffList(t.other_reactants)}</div><div class="field-title">OTHER RELEASED PRODUCTS</div><div id="inspector-other-products">${coeffList(t.other_products)}</div><div class="tag-row">${topologyTypes(t).map(x=>tag(x,isSink(t.carrier_after[0])&&x==="SINK_CONVERGENCE"?"sink":"pending")).join("")}</div>`;
    }else html+=`<p class="small">${data.noncarrier_ids.includes(rid)?"样板的游离通道：没有虚构酶载体边；完整底物与产物见上方。":"PATHWAY_NOT_RECONSTRUCTED：尚未批准该模块的载体映射；完整源底物和产物见上方。"}</p>`;
    html+=`<div class="field-title">REVERSE REACTION</div>${r.reverse?ridButton(r.reverse):'<span class="small">无精确逆向伙伴</span>'}`;
    if(t){const m=data.modules[t.enzyme],out=sortedUnique(t.carrier_before.flatMap(s=>m.branches[s]||[])),down=sortedUnique(t.carrier_after.flatMap(s=>m.branches[s]||[]));
      html+=`<div class="field-title">COMPETING OUTGOING REACTIONS</div><div class="jump-list">${out.map(ridButton).join("")||"无"}</div><div class="field-title">DOWNSTREAM CARRIER-STATE CONSUMERS</div><div class="jump-list">${down.map(ridButton).join("")||"无；终端载体"}</div><p class="small">共享的真实载体状态可支持局部接续；每条反应仍需要全部其他底物。</p>`;
    }else html+=`<div class="field-title">DOWNSTREAM CONNECTIONS</div><p class="small">载体关系未重构；不从普通共享底物推断因果链。</p>`;
    html+=`<div class="field-title">定位到所属代表路径</div><div class="jump-list">${paths.map(id=>`<button type="button" data-action="path" data-path="${id}">${id}</button>`).join("")||"<span class='small'>无完整代表路径成员关系；源反应仍保留。</span>"}</div>`;
    if(t&&!paths.length)html+=`<button type="button" class="quiet" data-action="state" data-state="${esc(t.carrier_before[0])}">查看所属载体状态的出口与返回</button>`;
    html+=`<div class="field-title">查看所属功能分类</div><div class="jump-list">${r.level_c.map(c=>`<button type="button" data-action="context" data-context="${c}">${c}</button>`).join("")}</div><div class="field-title">REFERENCE ACTIVITY</div>${tag(r.reference_activity,isDisabled(rid)?"disabled":"")}<p class="small">参数非零仅表示该方向有参考参数支持，不表示实际通量。</p>`;
    html+=`<details id="source-provenance"><summary>Source provenance / author parameter</summary><div class="provenance">Reaction ID: ${rid}<br>原始参数: ${esc(r.reference_parameter)}<br>原始 pair-aware 标签: ${esc(r.reference_pair_activity)}<br>`+data.metadata.provenance.filter(p=>["CANONICAL_SBML","AUTHOR_REFERENCE_PARAMETERS","REVIEWED_LEVEL_C_V2"].includes(p.authority)).map(p=>`${esc(p.authority)}<br>${esc(p.path)}<br>SHA-256: ${esc(p.sha256)}<br>`).join("")+r.source_refs.map(p=>`${esc(p.source_file)} / ${esc(p.source_reaction_id)}<br>`).join("")+`</div></details>`;
    $("inspector-content").className="";$("inspector-content").innerHTML=html;
    if(window.innerWidth<=1180)$("inspector").scrollIntoView({behavior:"smooth",block:"start"});
  }
  function openState(sid) {
    if(!data.species[sid])return;
    const entry=Object.entries(data.modules).find(([,m])=>m.carrier_states.includes(sid));
    let html=`<h2 id="state-dialog-title">${esc(sid)}</h2>`;
    if(entry){const [enzyme,m]=entry,out=m.branches[sid]||[],incoming=m.rejoins[sid]||[],productive=Object.values(data.paths).some(p=>p.types.includes("PRODUCTIVE_PATH")&&p.states.includes(sid));
      const joinType=isSink(sid)?"SINK_CONVERGENCE":productive?"PRODUCTIVE_REJOIN":"STRUCTURAL_REJOIN";
      html+=`<div class="tag-row">${tag(enzyme)}${incoming.length>1?tag(joinType,isSink(sid)?"sink":""):""}${tag("HUMAN_REVIEW_REQUIRED","pending")}</div>`;
      if(isSink(sid))html+=`<p class="notice" data-convergence="SINK_CONVERGENCE">SINK_CONVERGENCE：多条降解方向流向这个终点。它不是产物生成路径的 PRODUCTIVE_REJOIN。</p>`;
      html+=`<h3>${out.length?`${out.length} 条并列竞争出口`:"无后续载体出口"}</h3><p class="small">全部出口来自同一真实前体，互为替代；不把这些 Reaction ID 按显示顺序串成路径。</p><div class="branch-grid" data-branch-state="${esc(sid)}" data-outgoing-count="${out.length}">`;
      for(const rid of out){const t=data.transitions[rid],sink=t.carrier_after.some(isSink);html+=`<article class="branch-outlet ${sink?"sink-outlet":""}" data-outgoing-rid="${rid}"><div>${ridButton(rid)}</div><div class="target-state">→ ${esc(t.carrier_after.join(" + "))}</div><div class="tag-row">${tag(data.reactions[rid].mechanism,"pending")}${isDisabled(rid)?tag("REFERENCE_DISABLED","disabled"):""}${sink?tag("SINK_CONVERGENCE","sink"):""}</div>`+(sink?`<details><summary>降解方程（默认折叠）</summary><div class="equation">${equationHTML(rid)}</div></details>`:`<div class="equation">${equationHTML(rid)}</div>`)+`</article>`;}
      html+=`</div>`;
      if(incoming.length)html+=`<h3>${isSink(sid)?"降解汇聚的原始入边":"到达同一真实状态的原始入边"}</h3><div class="jump-list">${incoming.map(ridButton).join(" ")}</div>`;
      const loops=m.return_loops.filter(l=>l.states.includes(sid));
      html+=`<details class="reverse-box"><summary>逆向 / 局部返回 · ${loops.length} 个有限见证</summary><div class="loop-list">${loops.map(l=>`<button type="button" data-action="loop" data-enzyme="${enzyme}" data-loop="${l.id}">${l.id}${l.reference_feasible?"":" · REFERENCE_DISABLED"}</button>`).join("")||"无返回：终端 sink"}</div></details>`;
    }else{const consumers=Object.keys(data.reactions).filter(rid=>data.reactions[rid].reactants[sid]),producers=Object.keys(data.reactions).filter(rid=>data.reactions[rid].products[sid]);
      html+=`<div class="tag-row">${tag("ORIGINAL_REACTIONS_AVAILABLE")}${tag("PATHWAY_NOT_RECONSTRUCTED","pending")}</div><p class="small">这是原始 species incidence，不据此推断载体之间的因果路径。</p><p>消耗此物种：${consumers.length} 个源反应；生成此物种：${producers.length} 个源反应。</p><button type="button" data-action="species-reactions" data-state="${esc(sid)}">分页查看全部关联源反应</button>`;
    }
    $("state-content").innerHTML=html;if(!$("state-dialog").open)$("state-dialog").showModal();
  }
  function closeState(){if($("state-dialog").open)$("state-dialog").close();}
  function clearSearch(){state.query="";$("search").value="";state.page=0;}
  function showPath(id,focus=null){if(!data.paths[id])return;closeState();clearSearch();state.mode="pathway";state.path=id;state.loop=null;state.focusState=focus;state.context="RS_binding";state.substep=null;state.enzyme=null;state.customIds=null;state.speciesFilter=null;render();$("reading").scrollTop=0;if(focus){const step=document.querySelector(".focused-step");if(step)step.scrollIntoView({block:"center"});}}
  function selectContext(id,sub=null,enzyme=null){clearSearch();state.context=id;state.substep=sub;state.enzyme=enzyme;state.customIds=null;state.speciesFilter=null;state.mode="functional";state.focusState=null;closeState();render();const section=document.querySelector(`#hierarchy details[data-context="${id}"]`);if(section){section.open=true;section.closest(".nav-group").open=true;}$("reading").scrollTop=0;}
  function toast(text){$("toast").textContent=text;$("toast").classList.add("visible");setTimeout(()=>$("toast").classList.remove("visible"),2200);}
  async function copyText(text){let copied=false;try{if(navigator.clipboard){await navigator.clipboard.writeText(text);copied=true;}}catch(_error){}
    if(!copied){const box=document.createElement("textarea");box.value=text;box.style.position="fixed";box.style.opacity="0";document.body.append(box);box.select();try{copied=document.execCommand("copy");}catch(_error){}box.remove();}
    toast(copied?"已复制到剪贴板":"浏览器未允许自动复制；可选中右栏文本后按 Ctrl+C");return copied;
  }
  document.addEventListener("click",event=>{
    const button=event.target.closest("[data-action]");if(!button)return;const a=button.dataset.action;event.preventDefault();
    if(a==="context")selectContext(button.dataset.context);
    else if(a==="substep")selectContext(button.dataset.context,button.dataset.substep,button.dataset.enzyme||null);
    else if(a==="path")showPath(button.dataset.path);
    else if(a==="rejoin")showPath(button.dataset.path,button.dataset.state);
    else if(a==="reaction"){closeState();renderInspector(button.dataset.rid);}
    else if(a==="state")openState(button.dataset.state);
    else if(a==="close-state")closeState();
    else if(a==="mode"){state.mode=button.dataset.mode;clearSearch();state.page=0;render();}
    else if(a==="page"){state.page=Math.max(0,state.page+Number(button.dataset.delta));render();}
    else if(a==="search-kind"){state.searchKind=button.dataset.kind;state.page=0;render();}
    else if(a==="toggle-nav")document.body.classList.toggle("nav-open");
    else if(a==="all-source"){clearSearch();state.context=null;state.substep=null;state.enzyme=null;state.customIds=null;state.speciesFilter=null;state.mode="functional";render();}
    else if(a==="loop"){closeState();clearSearch();state.context="RS_binding";state.mode="pathway";state.loop={enzyme:button.dataset.enzyme,id:button.dataset.loop};state.focusState=null;render();$("reading").scrollTop=0;}
    else if(a==="species-reactions"){closeState();clearSearch();state.mode="functional";state.context=null;state.substep=null;state.enzyme=null;state.customIds=null;state.speciesFilter=button.dataset.state;render();}
    else if(a==="boundary"){closeState();clearSearch();state.mode="functional";state.context=null;state.substep=null;state.enzyme=null;state.speciesFilter=null;state.customIds=sortedUnique(data.boundary_links.filter(b=>b.module===button.dataset.enzyme).map(b=>b.reaction_id));render();}
    else if(a==="copy"&&state.rid)void copyText(button.dataset.copy==="rid"?state.rid:data.reactions[state.rid].equation);
  });
  let searchTimer;
  $("search").addEventListener("input",()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{state.query=$("search").value.trim();state.page=0;state.searchKind="reactions";render();},120);});
  $("positive-only").addEventListener("change",()=>{state.positiveOnly=$("positive-only").checked;state.page=0;render();});
  document.addEventListener("keydown",event=>{if(event.key==="/"&&!/INPUT|TEXTAREA/.test(event.target.tagName)){event.preventDefault();$("search").focus();}if(event.key==="Escape")closeState();});
  renderHierarchy();render();
  // Public pure algebra functions also let the independent browser tests
  // compare the executed JavaScript with a fresh canonical-SBML calculation.
  window.Atlas={data,netForIds,netEquation,cycleCertificate,getExactReverseDisplay,mechanismDescription,getCompetingOutlets,pathStep,getState:()=>({...state}),pageSize:PAGE_SIZE};
})();
