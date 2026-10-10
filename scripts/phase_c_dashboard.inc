<!-- Phase C release section, inlined into the existing reasoning atlas. -->
<section class="release" id="phase-c" aria-label="Phase C 正式研究发布">
  <div class="eyebrow">PNAS2017 · 正式研究里程碑 · 2026-10-10</div>
  <div class="hero">
    <div>
      <h2>更少的状态，清楚的适用边界</h2>
      <div id="phase-dim" class="dimension"></div>
      <p>Matsuura et al. · PNAS 2017 · fMet–Gly–Gly</p>
      <p>先用精确守恒与作者支持面缩小状态空间，再组合 Gly 近似聚合与回收观测商系统。</p>
      <p id="phase-counts" class="fine"></p>
    </div>
    <div><div id="phase-stat" class="stats"></div><p id="phase-status" class="fine"></p></div>
  </div>
  <div class="rule"><span id="phase-b1" class="fine"></span></div>
  <aside class="limits" aria-label="持续可见的科学限制">
    <h3>接受范围的一部分：这些限制持续有效</h3>
    <ul>
      <li>R2/R3 依赖作者固定零参数与初值支持面；0952 重激活时阻断。</li>
      <li>Gly 仅近似；初始层可失准，部分投影初态不物理可行。</li>
      <li>回收商系统无唯一微观逆，个别路径 gross extents 不可恢复。</li>
      <li>未实现计算提速；不是一般蛋白序列或全 PURE 的普适验证。</li>
      <li>不认证完整分子、元素、离子、电荷、渗透压或生理时序。</li>
      <li>RF1/RF2 不合并；既有 QSSA 与能量循环失败证据继续保留。</li>
    </ul>
    <p id="phase-local" class="fine"></p>
  </aside>
  <div class="subnav"><a href="#phase-flow">降维依据</a><a href="#phase-curves">真实轨迹</a><a href="#phase-numbers">数值门与尺度</a><a href="#phase-speed">运行时</a><a href="#phase-mechanism">源机制</a><a href="#phase-provenance">证据与 freshness</a><a href="#s1">历史图谱与筛选器 ↓</a></div>

  <div class="subsection" id="phase-flow">
    <h3>不同变换，有不同的数学承诺</h3>
    <p class="fine">绿色：声明域内完整源状态精确重构。蓝色：精确受保护观测投影。琥珀虚线：条件动力学近似。每个变换都链接原始映射和证明。</p>
    <div id="phase-source" class="rule"></div>
    <div id="phase-flow-exact" class="branch"></div>
    <div class="flowline">从 R2 另走 Gly 支线：第一轮 → 第二轮；随后与回收商系统组合 ↓</div>
    <div id="phase-flow-chain" class="branch"></div>
    <div id="phase-merged" class="merged"></div>
    <div id="phase-equations" class="equations"></div>
  </div>

  <div class="subsection" id="phase-curves">
    <h3>实际保存的源模型与最终候选轨迹</h3>
    <div class="card">
      <div class="controls">
        <label for="phase-scenario">冻结场景<select id="phase-scenario"></select></label>
        <label for="phase-observable">观测量 / 积分事件量<select id="phase-observable"></select></label>
        <label for="phase-window">源时间窗口<select id="phase-window"></select></label>
      </div>
      <div class="legendline"><span><i class="linekey"></i>R0_TIGHT 规范源模型 · 紧 BDF 参考</span><span><i class="linekey approx"></i>R3_CHAIN12_RECYCLE 条件候选</span></div>
      <svg id="phase-plot" class="plot" viewBox="0 0 1000 330" role="img" aria-label="实际保存轨迹比较"></svg>
      <p class="fine" id="phase-plot-note" aria-live="polite"></p>
      <p class="fine">纵轴为源浓度 / 源累计事件尺度；不猜测时间单位。CONSUMED_ATP/GTP 含从自由池取入的可逆结合事件，不能解释为不可逆水解量或按肽产量固定倍数的能耗。</p>
      <details><summary>所选曲线的全部保存点与误差（可访问的数据表）</summary><div id="phase-point-data" class="tablewrap" style="max-height:360px"></div></details>
    </div>
    <div class="tablewrap" id="phase-window-results"></div>
    <p class="fine">上表始终列出三个窗口；通过长期门不表示初始层被批准为精确。其他模型的完整窗口指标保留在数据 contract 和原数值报告。</p>
  </div>

  <div class="subsection" id="phase-numbers">
    <h3>四场景、长期窗口的冻结数值结果</h3>
    <p class="fine">以下是源时间 1–1000 的固定尺度归一化误差，不是全时间、全参数或任意初值的普适误差。</p>
    <div id="phase-maxima" class="metrics"></div>
    <div id="phase-results" class="tablewrap" style="margin-top:14px"></div>
    <div class="two">
      <div><h3>原注册门</h3><div id="phase-gates" class="tablewrap"></div></div>
      <div><h3>误差如何归一化</h3><p class="fine">状态 / 累计事件：maxₜ |候选 − 参考| / 固定初值库存尺度。流量：√[∫((J候选 − J参考)/固定尺度)²dt / 窗口长度]。尺度不使用最终产量或累计量作分母。</p><pre id="phase-scale-rules"></pre></div>
    </div>
    <details><summary>当前选择场景的精确初值覆盖与每个观测 / 计数器的固定尺度</summary><pre id="phase-scales"></pre></details>
  </div>

  <div class="subsection" id="phase-speed">
    <h3>维数下降，但尚无计算提速</h3>
    <div class="callout"><p id="phase-runtime-note"></p></div>
    <div id="phase-runtime" class="tablewrap"></div>
  </div>

  <div class="subsection" id="phase-mechanism">
    <h3>从每个简化回到原始源反应</h3>
    <p class="fine">点击原始 Reaction ID 可沿用既有图谱查看反应详情；展开方程可直接检查源计量与作者参数。概念性流程不新增化学反应。</p>
    <div id="phase-mechanisms" class="mechanisms"></div>
  </div>

  <div class="subsection" id="phase-provenance">
    <h3>可复查的科学决定与证据</h3>
    <p class="fine" id="phase-freshness"></p>
    <div class="linkgrid" id="phase-evidence-links"></div>
    <details><summary>正式接受的机器可读记录、条件与明确未批准事项</summary><pre id="phase-decision-json"></pre></details>
    <details><summary>所有本页输入的相对路径、字节数与 SHA-256</summary><div id="phase-inputs" class="tablewrap"></div></details>
    <p class="fine">历史 PENDING / HUMAN_REVIEW_REQUIRED 原报告仍保持原样。当前人工决定由上方带日期的新记录单独给出；本页不是“普适验证 PURE_reduced_core”的声明。</p>
  </div>
</section>
