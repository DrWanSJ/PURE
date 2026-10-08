"""Generate evidence-bound CHAIN_01 report/navigation without new simulations."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/reduction/chain01_four_step"
REPORT = ROOT / "docs/reduction/chain01_four_step_validation_report.md"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def number(value):
    return f"{value:.9g}" if isinstance(value, (int, float)) else str(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    summary, source, freeze = read("validation_summary.json"), read("source_manifest.json"), read("protocol_freeze.json")
    config_path = ROOT / freeze["config_path"]
    assert sha(config_path) == freeze["config_sha256"], "Frozen protocol drift"
    assert sha(OUT / "source_manifest.json") == freeze["source_manifest_sha256"], "Source audit drift"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    verification = read("verification_report.json")
    independent = read("independent_verification.json")
    assert independent["status"] == "PASS", "Independent verification has not passed"
    before = read("protected_files_before.json")
    checked = {path: {"sha256": sha(ROOT / path), "bytes": (ROOT / path).stat().st_size}
               for path in before["files"] if (ROOT / path).is_file()}
    changed = [path for path, item in before["files"].items() if checked.get(path) != item]
    protection = {"status": "PASS" if not changed else "FAIL", "checked_file_count": len(before["files"]),
                  "changed_or_missing": changed, "before_snapshot_sha256": sha(OUT / "protected_files_before.json"),
                  "head_unchanged": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip() == before["git_head"],
                  "files": checked}
    write("protected_files_after.json", protection)
    assert protection["status"] == "PASS" and protection["head_unchanged"], "Protected source/history drift"
    tau, ke = summary["tau"], summary["k_eff"]
    rates = list(summary["rates"].values())
    variance_full = sum(1 / k**2 for k in rates)
    variance_direct = tau**2
    dmean = .25 * sum(1/k for k in rates[1:]) + .5 * sum(1/k for k in rates[2:]) + .25 / rates[3]
    metric_names = {"product_trajectory": "S4 trajectory", "product_flux": "S4 current", "pi_current": "Pi current",
                    "pi_extent": "Pi extent", "eftu_gdp_current": "EF-Tu-GDP current", "eftu_gdp_extent": "EF-Tu-GDP extent",
                    "occupancy": "unfinished occupancy", "hidden_inventory": "hidden S1-S3 inventory"}
    def metric(test, window, name, field="max_normalized"):
        return summary["tests"][test]["metrics"][window][name][field]
    def gate_row(test, window):
        gates = summary["tests"][test]["gates"][window]
        return " | ".join(gates[name]["status"] for name in ("product_output", "resource_current", "resource_extent", "occupancy", "domain"))
    lines = ["# CHAIN_01 四步有效速率局部验证报告", "",
             f"最终状态：**{summary['status']}**。数值正确性：**{verification['status']}**；独立复核：**{independent['status']}**。",
             "本报告是本轮预注册探索性筛选结果；不赋予人工科学批准。PURE_reduced_core 的已有状态与 R1–R8 结论保持原样。",
             "", "## 1. 来源、模型及边界", "",
             f"工作树：`{ROOT.as_posix()}`；分支 `{before['branch']}`；HEAD `{before['git_head']}`。日期：2026-10-08（Asia/Shanghai）。",
             "来源规范 SBML，参数为 author CSV overlay；不得使用 SBML 的局部 k1=1 占位值。全部 968 行已有反应表被交叉核对。",
             "", "| State | Source species ID | Chemical stage |", "| --- | --- | --- |"]
    compositions = ["EF-Tu-GTP bound; hydrolysis not completed", "GDP + Pi bound", "GDP bound; free Pi released", "EF-Tu released", "peptide extended; ribosome still bound"]
    for (alias, species), composition in zip(source["species_aliases"].items(), compositions):
        lines.append(f"| {alias} | `{species}` | {composition} |")
    lines += ["", "| Reaction | k from author CSV | Local kinetic law |", "| --- | ---: | --- |"]
    for reaction, key in zip(["re0000000014", "re0000000016", "re0000000017", "re0000000018"], ["k14", "k16", "k17", "k18"]):
        lines.append(f"| {reaction} | {number(summary['rates'][key])} | {key} × its single substrate |")
    lines += ["", "S1–S3 的所有结构旁支仍保留在 canonical SBML；作者固定参数下这些旁支 k=0。全部 reactant/product/modifier/kinetic incidences 与参数见 [source_incidence_audit.csv](../../results/reduction/chain01_four_step/source_incidence_audit.csv)。",
              "S0 的 re13（k=140）被规定外部输入 u 替代；活跃竞争解离 re21（k=0.23）在局部实验中省略。S4 的 re19（k=30）和 re20（k=25）亦被隔离。这是边界干预，不是原作者完整网络中无条件串联的声明。",
              "时间轴保留 source model time unit，不解释成秒；浓度/库存沿用模型数值尺度，不做源单位修正。原模型未提供足以证明元素/电荷闭合的元数据；本轮 mass balance 是精确反应计量与模型库存闭合。",
              "", "## 2. 首次运行前固定的协议", "",
              f"冻结时间（UTC）：`{freeze['frozen_utc']}`；config SHA-256：`{freeze['config_sha256']}`。",
              "配置： [chain01_four_step_validation.json](../../configs/reduction/chain01_four_step_validation.json)；锁定记录：[protocol_freeze.json](../../results/reduction/chain01_four_step/protocol_freeze.json)。",
              f"程序从已审计的四个作者参数计算 τ={tau:.15g}，k_eff={ke:.15g}，候选标签 MEAN_DWELL_MATCHED_CANDIDATE。没有拟合或调参。",
              "", "| Test | Initial full x0…x4 | Input in tau units | Amount scale | Current scale | Domain |", "| --- | --- | --- | ---: | ---: | --- |"]
    for test, item in config["tests"].items():
        amount = item.get("amount_scale", tau)
        current = item.get("current_scale", 1/tau)
        lines.append(f"| {test} | `{item['initial_full']}` | `{item['input_segments']}` | {number(amount)} | {number(current)} | {item['domain_status']} |")
    lines += ["", "D 使用 y0=x0+x1+x2+x3=1、y4=x4=0 的重新开始等待映射；库存没有被删除，但剩余等待时间与原始化学组成不保留，属于预声明负对照。",
              f"采样固定为 {summary['sample_count']} 个点，0–10τ；初始及每个切换后加密。事件左右极限单独保存；状态、extent 和这些释放 current 连续，输入与入口导数可跳变。",
              "窗口：ENTIRE=0–10τ；TRANSIENT 是 [0,0.25τ] 与每个输入切换后的 [event,event+0.25τ] 的并集（含端点）；POST_TRANSIENT 是其严格补集；LATE=[5τ,10τ] 是预声明补充窗口，不能替代全窗口筛选。0.25τ 是观察带，不意味着慢阶段已完成松弛。",
              "预注册预算：product trajectory 和 resource extents 最大归一化误差≤0.01；product/resource currents 与未完成 occupancy≤0.05。量尺度为一批初始库存或一个 τ 的单位输入量，通量尺度为 cohort/τ 或单位输入率。1%/5% 是探索性分辨率预算，非既有科学批准标准。",
              "numerical gate：库存/extent 账本残差≤1e-8、矩阵指数误差≤1e-8、收紧积分差≤5e-9、负值容许≤1e-12、mean dwell 相对误差≤1e-8。数值误差预算远小于动力学近似预算。",
              "所有峰值指固定采样网格上的最大值；不声称是连续时间 supremum。相对误差仅在原参考值非零处定义，参考=0 处保留未定义值；很小的非零参考产生的大相对误差仍保留，但不拿它作 gate。RMS 按时间加权，各窗口连通段分别积分。",
              "", "## 3. 数学与数值正确性", "",
              "四列源计量以有理数逐物种相加，全部 241 个物种差值精确为零：S0 → S4 + PO4 + EFTu_GDP。该恒等式不证明瞬时动力学等价。",
              "Full ODE 保存五状态和四个 ξ；direct 保存 y0,y4,ξ_eff。Σx=Σx(0)+∫u，Σy=Σy(0)+∫u。",
              "一般账本：ξ14−ξ18=Δ(x1+x2+x3)，ξ16−ξ18=Δ(x2+x3)，ξ17−ξ18=Δx3。零内部初值时退化为无初始修正项的式子。",
              "自由 Pi=ξ16；结合态 Pi=x1；x0 的 GTP γ-phosphate 与已水解结合态 Pi 分列。自由 EF-Tu-GDP=ξ17，结合態 GDP=x1+x2，结合態 GTP=x0。故 ξ16+x1−x1(0)=ξ14；ξ17+x1+x2−x1(0)−x2(0)=ξ14。这些不是完整共享池的净轨迹。",
              "主积分 Radau(rtol=1e-10,atol=1e-12)，收紧 Radau(1e-12,1e-14)，每个输入事件分段；独立 augmented matrix exponential 与额外 source-reconstructed sparse expm_multiply 复核。没有负值裁剪或库存投影。实际完成状态、步数与残差记录于 verification_report.json / independent_verification.json。",
              "", "| Test | Numerical status | Max primary-vs-expm state/extent error | Max invariant residual |", "| --- | --- | ---: | ---: |"]
    for test, item in verification["tests"].items():
        maximum = max(v for k,v in item["solver_error"].items() if k.startswith("primary_") and "vs_expm" in k)
        lines.append(f"| {test} | {item['status']} | {number(maximum)} | {number(max(item['invariant_max_absolute'].values()))} |")
    lines += ["", "等待时间是四个独立指数阶段之和：E[T]=Σ1/k=τ；Var[T]=Σ1/k²。Direct E[T]=τ，Var[T]=τ²。",
              f"Full variance={variance_full:.15g}，direct variance={variance_direct:.15g}；direct 增大 {(variance_direct/variance_full-1)*100:.9g}%。数值存活积分加 10τ 后的解析剩余尾部，避免把截断均值误当无限时均值；完整 mean/variance 检查见 summary 的 dwell 字段。",
              "", "## 4. 筛选结果与全部窗口", "",
              "A/B/C 的 ENTIRE_WINDOW 所有强制类别必须同时 PASS；D 不进入域内筛选，失败按预期负对照解释。",
              "", "| Test | Window | Product output | Resource current | Resource extent | Occupancy | Domain |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for test,item in summary["tests"].items():
        for window in item["gates"]:
            lines.append(f"| {test} | {window} | {gate_row(test,window)} |")
    lines += ["", "| Test | Window | Metric | Max absolute error | Max normalized error |", "| --- | --- | --- | ---: | ---: |"]
    for test, item in summary["tests"].items():
        for window, metrics in item["metrics"].items():
            for name, value in metrics.items():
                lines.append(f"| {test} | {window} | {metric_names.get(name,name)} | {number(value['max_absolute'])} | {number(value['max_normalized'])} |")
    lines += ["", "逐时 signed/absolute/normalized/relative 误差、峰值时刻和 RMS 都保留在 error_tables；本表不隐去失败窗口。hidden_inventory 是消失的显式微态库存，不等于 total occupancy 误差。",
              "", "阈值敏感性只对动力学预算乘 0.5/1/2，不移动窗口或分母，numerical/domain 预算保持不变。", "",
              "| Factor | Test | Entire product | Entire current | Entire extent | Entire occupancy |", "| --- | --- | --- | --- | --- | --- |"]
    for test,item in summary["tests"].items():
        for factor,windows in item["threshold_sensitivity"].items():
            groups=windows["entire"]
            lines.append(f"| {factor} | {test} | " + " | ".join(groups[n]["status"] for n in ("product_output","resource_current","resource_extent","occupancy")) + " |")
    lines += ["", "## 5. Q1–Q8 科学判断", "",
              "**Q1 净计量：** 精确相同，全部 241 个物种差为零；S0 的结合態 GTP 经四阶段产生自由 Pi 与 EF-Tu-GDP，不能将此精确净向量等同释放时序。",
              f"**Q2 平均等待：** 解析和尾部修正数值检查 `{summary['dwell']['status']}`；τ={tau:.15g}，k_eff={ke:.15g}。仅均值匹配，不是 exact Markov lumping。",
              f"**Q3 形成时间分布：** full H(s)=260×7×1000²/[(s+260)(s+7)(s+1000)²]，direct H(s)=k_eff/(s+k_eff)。full density 初始为 O(t³)、CDF 为 O(t⁴)，direct CDF 为 O(t)。A 在 t=0 full product current=0、direct={ke:.12g}，是结构差异；A 全窗口 product trajectory 最大误差={metric('A','entire','product_trajectory'):.9g}（归一化）。两个 k=1000 重复根应包含 t exp(-1000t)，不能套不同速率的奇异公式。",
              f"**Q4 资源释放：** A 的 Pi current 最大归一化误差={metric('A','entire','pi_current'):.9g}，Pi extent={metric('A','entire','pi_extent'):.9g}；EF-Tu-GDP current={metric('A','entire','eftu_gdp_current'):.9g}，extent={metric('A','entire','eftu_gdp_extent'):.9g}。单步把二者都绑定到完成事件，Pi 的快速释放被明显延迟。D 的无限时增量 full Pi=.25、Tu-GDP=.75、product=1，direct 均为1；多释放 .75/.25 来自重启映射改变组成，非求解器错误。",
              f"**Q5 核糖体占据：** y0 把等待库存移到单一入口状态，未删除总 cohort。A 的 unfinished occupancy 最大归一化误差={metric('A','entire','occupancy'):.9g}，显式 hidden S1-S3 最大库存={metric('A','entire','hidden_inventory', 'max_absolute'):.9g}。总 ribosome inventory 包含 S4，局部 S4 仍结合核糖体，守恒不等于核糖体释放。恒定输入的 unfinished inventory 两模型均趋 τ，但化学阶段、bound GDP/Pi 及真实 S0 占据无法由 y0 同时恢复。",
              f"**Q6 允许的近似：** 逐窗口支持由上述 gate 表限定。A 的预声明晚期窗口通过声明尺度的门槛，S4 最大误差={metric('A','late','product_trajectory'):.9g}，可支持已输入 cohort 的接近完成量；不能把晚期吻合扩展到初始或任意输入。晚期 current 支持是按初始 cohort/τ 的绝对通量预算，不是尾部相对精度：A 晚期 product current 相对误差最大为 {summary['tests']['A']['metrics']['late']['product_flux']['max_relative_defined']:.9g}，几乎消失的 Pi reference 可给出极大相对误差，原始记录完整保留。B 的两模型完成通量均趋1、产物渐近 t−τ、unfinished inventory 趋τ，但 Pi extent 的持续差趋 1/7+1/1000=0.143857142857，按 τ 归一化为0.967410582348，累计资源门槛持续失败。C 的切换记忆必须逐窗口审查，固定切换后0.25τ不保证慢瞬态消失。D不在适用域。任一窗口支持均只针对边界干预、作者固定参数和所声明可观测量。",
              f"**Q7 保留 S2/E_mid：** 有理由另行预注册候选。S2 是 Pi 已释放、EF-Tu-GDP 仍被结合的慢 k17 阶段，独立保存它有助区分 Pi 早期释放与较晚 Tu/产物事件。若 A=S0、D=S4，定义 E_mid=x1+x2+x3，可保留链内库存；该 aggregate 的 microscopic exit rates=(0,0,k18) 不相等，不满足强 Markov lumpability，组成决定通量。另一个总量 E_all=x0+x1+x2+x3 的 exit rates=(0,0,0,k18)；二者不能混用。四步中的 S2 与旧三步案例的同名 alias 并非同一位置。D 真正剩余均值={dmean:.12g}，direct restart τ 延长 {(tau/dmean-1)*100:.9g}%，也说明组成信息的必要性。A→E_mid→D 值得作为下一阶段局部候选测试，必须定义每个状态的资源组成/释放事件并重新注册，本轮没有模拟它。",
              "**Q8 Full-coupled：** 不建议把当前 direct candidate 作为通过候选进入完整 968 反应验证：本轮已测 resource/product 瞬态缺陷与边界 re21 竞争/共享池耦合尚未解决。先测试保留 Pi admission、慢 Tu-bound intermediate 和占据量的局部候选；其成功与新增人工授权之后再决定完整 coupled validation。本次没有启动完整网络实验，也不推断所有串联简化不可能。",
              "", "## 6. 图与数据", ""]
    names = ["01_product_trajectory","02_product_flux","03_pi_release_current","04_pi_release_extent","05_eftu_gdp_current","06_eftu_gdp_extent","07_internal_occupancy","08_normalized_errors","09_pulse_and_switch_responses","10_model_comparison_summary"]
    for name in names:
        lines.append(f"- [{name}](../../results/reduction/chain01_four_step/figures/{name}.png)")
    lines += ["", "图中 Full four-step reference 与 Direct effective candidate 显式标注；每个测试完整范围及初始放大并列。figure 09 检查双矩形输入切换；figure 10 汇总窗口而不只展示吻合区间。全部图对应原始 numerical_results/test_A…D.csv 与 error_tables。",
              "", "## 7. 复现与文件保护", "",
              "在本工作树中，用现有 Python（本次 D:/Code/Anaconda/python.exe；NumPy/SciPy/Matplotlib 版本见 runtime_manifest）顺序运行：", "", "```text",
              "python scripts/reduction/audit_chain01_sources.py --verify",
              "python scripts/reduction/validate_chain01_four_step.py",
              "python scripts/tests/test_chain01_four_step.py",
              "python scripts/reduction/report_chain01_four_step.py", "```", "",
              "保留 config 与 protocol_freeze 原始字节；重跑沿用同一协议。新协议必须另存版本并单独冻结。运行尝试与首次失败记录若存在会保留，不混同 scientific approximation fail。",
              f"本工作树全部 {len(before['files'])} 个原有 tracked 文件逐字节 SHA-256 前后核对 PASS，HEAD 未变；新增来源/结果不改写 canonical source、author parameters、历史证据、reduction_decisions.csv 或 PURE_reduced_core。没有 commit/push/merge、软件安装、参数拟合或全局 QSSA 搜索。",
              "导航：knowledge_graph.json 标注 EXTRACTED/INFERRED 与源 hash、confidence、freshness；只是来源与结果索引，不替代原始证据。最终所有新增文件列于 workspace_changes.json、delivery_manifest.json。", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    nodes, edges = [], []
    def node(id, kind, provenance, evidence, **extra):
        nodes.append({"id": id,"kind": kind,"provenance": provenance,"confidence": "HIGH" if provenance=="EXTRACTED" else "BOUNDED_INFERENCE",
                      "freshness": "2026-10-08_CURRENT_FROZEN_LOCAL_RUN","evidence": evidence,**extra})
    for index, item in enumerate(source["sources"]):
        node(f"source:{index}", "source", "EXTRACTED", item["path"], sha256=item["sha256"])
        edges.append({"from":f"source:{index}","to":"source_audit","relation":"supports"})
    node("source_audit","exact_source_audit","EXTRACTED","source_manifest.json",sha256=sha(OUT/"source_manifest.json"))
    node("protocol","frozen_protocol","EXTRACTED",freeze["config_path"],sha256=freeze["config_sha256"])
    node("candidate","mean_dwell_candidate","EXTRACTED","validation_summary.json",status=summary["status"],label=summary["candidate_label"])
    for test,item in summary["tests"].items():
        evidence=f"numerical_results/test_{test}.csv"
        node(f"test:{test}","local_test","EXTRACTED",evidence,sha256=sha(OUT/evidence),domain=item["domain_status"],gates=item["gates"])
        edges += [{"from":"protocol","to":f"test:{test}","relation":"defines"},{"from":f"test:{test}","to":"candidate","relation":"screens"}]
    node("independent","independent_verification","EXTRACTED","independent_verification.json",sha256=sha(OUT/"independent_verification.json"),status=independent["status"])
    node("recommendation","scientific_recommendation","INFERRED",str(REPORT.relative_to(ROOT)).replace("\\","/"),scope="local candidate; no human approval",full_coupled="NOT_RECOMMENDED_FOR_CURRENT_DIRECT_CANDIDATE",next="LOCAL_AGGREGATE_CANDIDATE_REQUIRES_NEW_PREREGISTRATION")
    edges += [{"from":"source_audit","to":"candidate","relation":"bounds_chemistry"},{"from":"candidate","to":"recommendation","relation":"supports_bounded_inference"},{"from":"independent","to":"candidate","relation":"verifies_computation_only"}]
    write("knowledge_graph.json",{"authority":"DERIVED_NAVIGATION_ONLY_SUBORDINATE_TO_SOURCE_AND_RAW_ARRAYS","nodes":nodes,"edges":edges})
    status = subprocess.check_output(["git","status","--porcelain=v1","-uall"],cwd=ROOT).decode()
    untracked = subprocess.check_output(["git","ls-files","--others","--exclude-standard","-z"],cwd=ROOT).decode().split("\0")
    paths = sorted({p for p in untracked if p} | {"results/reduction/chain01_four_step/workspace_changes.json", "results/reduction/chain01_four_step/delivery_manifest.json"})
    write("workspace_changes.json",{"branch":before["branch"],"head":before["git_head"],"tracked_files_changed":changed,"new_files":paths,"status_porcelain":status,"no_git_mutations":True})
    artifacts = [{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p),"bytes":p.stat().st_size}
                 for p in sorted(OUT.rglob("*")) if p.is_file() and p.name!="delivery_manifest.json"]
    artifacts += [{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p),"bytes":p.stat().st_size}
                  for p in [config_path,REPORT,*sorted((ROOT/"scripts/reduction").glob("*chain01*.py")),ROOT/"scripts/tests/test_chain01_four_step.py"]]
    write("delivery_manifest.json",{"status":summary["status"],"config_sha256":freeze["config_sha256"],"artifacts":artifacts,"inventory_note":"this manifest excludes itself to avoid cyclic fingerprints"})
    print(json.dumps({"status":summary["status"],"report":str(REPORT),"protected_files":len(before["files"]),"artifacts":len(artifacts)},indent=2))


if __name__ == "__main__":
    main()
