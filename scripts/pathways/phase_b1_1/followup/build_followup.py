#!/usr/bin/env python3
"""Additive Human Review follow-up; source-state discovery of IF3-first release."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import csv
import json
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'docs/reduction/pathways'
sys.path.insert(0, str(ROOT / 'scripts/pathways/phase_b1_1'))
import build_initiation_witnesses as audited_builder


def write(path, data):
    path.write_bytes((json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'))


def build():
    b = audited_builder
    rx = b.low.read_source()  # Fresh canonical SBML/author CSV; not the saved P1.
    with (ROOT / b.low.V2).open(encoding='utf-8-sig', newline='') as f:
        ann = {r['reaction_id']: r for r in csv.DictReader(f)}
    _, core, _ = b.scope(rx, ann)
    enabled = sorted(r for r in core if F(rx[r]['reference_parameter']) > 0)
    initial = {s: '1' for s in (b.INTERFACE, 'RS30S', 'RS50S', 'IF1', 'IF3', 'mRNA')}
    full = 'RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA'
    seventy = full.replace('30S', '70S')
    waypoints = ['RS30S_IF3', 'RS30S_IF1_IF3', 'RS30S_IF1_IF3_mRNA', full, seventy,
                 seventy.replace('GTP', 'GDP_PO4'), seventy.replace('GTP', 'GDP'),
                 'RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA',
                 'RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA', b.E1]
    ids, legs = b.search(initial, waypoints, enabled, rx)
    wid = 'B1-1-FOLLOWUP-IF3-FIRST'
    occurrences = [(f'{wid}:E{i+1:02d}', r, f'{wid}:E{i+1:02d}') for i, r in enumerate(ids)]
    witness = b.construct(wid, occurrences, initial, b.E1, rx, ('IF1', 'IF3'))
    witness['classification'] = 'SOURCE_SUPPORTED_IF3_FIRST_RELEASE_WITNESS'
    witness['selection_basis'] = 'SOURCE_STATE_WAYPOINT_FOR_IF3_RELEASE; SHORTEST_ENABLED_ROUTE; SORTED_ORIGINAL_IDS'
    witness['unresolved_assumptions'].append('IF3-first is a structural positive, not a measured physiological route or flux ranking')
    primary = {b.low.rid(n) for n in (724, 747, 749, 1, 13)} | set(ids)
    inventory_ids = primary | {r for t in primary for r in rx[t]['reverse_reaction_ids']}
    records = {r: {**rx[r], 'reaction_family_id': ann[r]['reaction_family_id'],
                   'source_subsystems': ann[r]['level_b_subsystem_candidates'], 'evidence_status': 'EXTRACTED',
                   'confidence': 'EXACT_SOURCE_REACTION_VERIFIED', 'freshness': 'CANONICAL_HASH_CHECKED_AT_BUILD'}
               for r in sorted(inventory_ids)}
    branches = [{'reaction_id': b.low.rid(n), 'source_states': rx[b.low.rid(n)]['reactants'],
                 'outputs': rx[b.low.rid(n)]['products'], 'reference_parameter': rx[b.low.rid(n)]['reference_parameter'],
                 'reference_activity': rx[b.low.rid(n)]['reference_activity'],
                 'reverse_reaction_ids': rx[b.low.rid(n)]['reverse_reaction_ids'], 'evidence_status': 'EXTRACTED'}
                for n in (724, 747, 749)]
    historical = json.loads((OUT / 'phase_b1_1_witnesses.json').read_text(encoding='utf-8'))
    p1 = next(w for w in historical['witnesses'] if w['witness_id'] == 'P1')
    references = [b.low.provenance(p, a) for p, a in (
        ('docs/reduction/pathways/phase_b1_1_witnesses.json', 'IMMUTABLE_HISTORICAL_WITNESSES'),
        ('docs/reduction/pathways/phase_b1_1_validation_report.json', 'IMMUTABLE_HISTORICAL_A_J_RESULTS'),
        (b.low.SOURCE, 'CANONICAL_SBML'), (b.low.CSV, 'AUTHOR_PARAMETERS'), (b.low.ARCHIVE, 'AUTHOR_ARCHIVE'),
        (b.low.V2, 'REVIEWED_LEVEL_C_V2'))]
    return {'schema': 'B1_1_HUMAN_REVIEW_FOLLOWUP_V1', 'review_date': '2026-10-09', 'phase': 'B1-1 Human Review Follow-up',
            'authority': 'EXPLICIT_USER_SUPPLIED_REVIEW_CONCLUSIONS_AND_FOLLOWUP_AUTHORIZATION',
            'suggested_review_status': 'B1_1_CONDITIONALLY_ACCEPTED', 'researcher_formally_signed': False,
            'formal_signoff_status': 'PENDING_FINAL_RESEARCHER_CONFIRMATION', 'commit_push_authorized': False,
            'phase_b1_2_authorized': False, 'qssa_authorized': False, 'kinetic_reduction_authorized': False,
            'human_review': [
                {'id': 'H1', 'item': 'E1 initiation exit', 'user_conclusion': 'Y', 'required_treatment': 'RETAIN_SOURCE_MODEL_BOUNDARY'},
                {'id': 'H2', 'item': '0001 elongation handoff', 'user_conclusion': 'Y', 'required_treatment': 'DISTINGUISH_MODEL_ORDER_FROM_PHYSIOLOGICAL_MECHANISM'},
                {'id': 'H3', 'item': 'Alternative assembly/release routes', 'user_conclusion': 'Y，限定', 'required_treatment': 'LABEL_ID_ORDER_AND_TEST_0747_0757'},
                {'id': 'H4', 'item': 'Nucleotide/resource ledger', 'user_conclusion': 'Y', 'required_treatment': 'RETAIN_IF2_GDP_VS_IF2_GTP_DISTINCTION'},
                {'id': 'H5', 'item': 'Composite molecular identity', 'user_conclusion': '限定接受', 'required_treatment': 'FULL_COMPOSITION_REMAINS_INFERRED'}],
            'historical_P1_annotation': {'witness_id': 'P1', 'source_file': 'docs/reduction/pathways/phase_b1_1_witnesses.json',
                'classification': 'LEXICOGRAPHIC_STRUCTURAL_WITNESS', 'historical_source_reaction_ids': p1['source_reaction_ids'],
                'selected_release_direction': b.low.rid(724), 'selection_basis': 'SORTED_ORIGINAL_ID_TIE_BREAK_IN_SOURCE_MARKING_SEARCH',
                'kinetic_dominance_claimed': False, 'measured_path_flux_claimed': False,
                'overlay_semantics': 'ADDITIVE_ANNOTATION; ORIGINAL_P1_AND_HISTORICAL_PASS_BYTES_UNCHANGED'},
            'new_witness': witness, 'search_evidence': {'waypoints': waypoints, 'legs': legs,
                'scope_direction_count': len(core), 'enabled_scope_count': len(enabled), 'max_states_per_leg': 50000, 'max_depth_per_leg': 16},
            'release_branch_inventory': branches, 'reactions': records, 'source_provenance': references,
            'interpretation_limits': {'model_0001_context': 'ELONG_tRNA_release', 'model_order': ['re0000000001', 're0000000013'],
                'order_evidence': 'E2_EXACT_SOURCE_PRODUCTION_AND_CONSUMPTION; NOT_PHYSIOLOGICAL_TIME_CERTIFICATE',
                'model_order_is_complete_physiological_mechanism': False,
                'initiator_release_peptide_bond_translocation_complete_physical_mechanism_claimed': False,
                'E1_E2_composition': {endpoint: {'mRNA': 'INFERRED', 'peptidyl_state': 'INFERRED', 'full_complex_components': 'INFERRED'}
                                      for endpoint in (b.E1, b.E2)},
                'IF2_GDP_release_equals_IF2_GTP_recovery': False,
                'source_species_continuity_is_global_composition_certificate': False},
            'future_original_source_evidence_required': [
                {'id': 'Q1', 'question': 'Locate original article/SI/state definitions explaining why 0001 precedes first Gly-tRNA encounter 0013',
                 'status': 'UNRESOLVED_NOT_SEARCHED_IN_THIS_STRUCTURAL_FOLLOWUP'},
                {'id': 'Q2', 'question': 'Obtain explicit E1/E2 mappings for mRNA, peptide/initiator-tRNA and complete ribosome composition',
                 'status': 'UNRESOLVED_FULL_COMPOSITION_INFERRED'},
                {'id': 'Q3', 'question': 'Require original-source mechanistic evidence before mapping model states to initiator release, peptide-bond formation and translocation',
                 'status': 'NO_COMPLETE_PHYSIOLOGICAL_MECHANISM_CERTIFIED'}]}


def markdown(data):
    w, rx = data['new_witness'], data['reactions']
    lines = ['# B1-1 Human Review Follow-up — IF3-first release', '',
             '建议审阅状态：`B1_1_CONDITIONALLY_ACCEPTED`。这不是研究者正式签署；等待正式确认。原有 A–J PASS 和历史文件保持原样。', '',
             '## 五项 Human Review', '', '| 项目 | 用户结论 | 本次必要处理 |', '|---|---|---|']
    lines += [f"| {h['id']} — {h['item']} | {h['user_conclusion']} | {h['required_treatment']} |" for h in data['human_review']]
    lines += ['', '## 现有 P1 的追加标记', '',
              'P1 保留，并在本记录中追加 `LEXICOGRAPHIC_STRUCTURAL_WITNESS` 标记。'
              '`re0000000724` 由源 ID 排序选中，不代表动力学主导路径。此标记通过带哈希的历史文件引用应用，未重写原 P1 或原 PASS 报告。', '',
              '## 独立 IF3-first 正例', '',
              '新见证：`' + w['witness_id'] + '`；10 个实际有向反应事件；源状态里程碑选择 IF3 先释放，再释放 IF1。'
              '这是与 P1 并列的独立场景，不能把两条路线串成同一核糖体的连续处理。', '',
              '边界供应（各 1 个形式 token）：`' + ', '.join(w['initial_marking']) + '`。'
              'IF2/fMet-tRNA 为明确的 B0-W3 接口条件输入；本正例不重复执行或重复计数 B0 事件。形式库存不是浓度或实验轨迹。', '',
              '| Event | Original directed reaction | Complete source equation | Level-C | Author k1 | Exact inverse / k1 |',
              '|---|---|---|---|---:|---|']
    for e in w['reaction_occurrences']:
        q = rx[e['reaction_id']]
        inverse = ', '.join(r + ' / ' + rx[r]['reference_parameter'] + ' (' + rx[r]['reference_activity'] + ')' for r in q['reverse_reaction_ids']) or 'none'
        lines.append(f"| {e['event_id']} | {e['reaction_id']} | `{e['equation']}` | {q['level_c']} | {q['reference_parameter']} ({q['reference_activity']}) | {inverse} |")
    lines += ['', '**精确净计量（CONCEPTUAL_NET；不是新的源反应或速率律）：**', '', '```text', w['net_reaction'], '```', '',
              'IF1 和 IF3 以各自原始游离状态恢复；IF2_GDP 为释放产物，不是 IF2_GTP 再生。'
              '源状态链、所有共反应物、逐事件标记和 token 来源保存在 JSON，执行结果属于独立验证报告。', '',
              '## 共享 GDP 源状态的三个竞争出口', '',
              '| Original ID | Complete source equation | Reference k1 | Exact inverse / k1 |', '|---|---|---:|---|']
    for branch in data['release_branch_inventory']:
        r = branch['reaction_id']
        inverse = ', '.join(t + ' / ' + rx[t]['reference_parameter'] for t in branch['reverse_reaction_ids'])
        lines.append(f"| {r} | `{rx[r]['equation']}` | {branch['reference_parameter']} | {inverse} |")
    lines += ['', '三条方向消耗同一个原始物种 `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`。'
              '它们是竞争出口；逆向是保留的源方向，不会自动执行。参考速率常数不是实测路径通量，本次不计算或比较轨迹通量。', '',
              '## E1 / E2 生化解释限制', '',
              '`re0000000001` 是作者原始模型定义的 `ELONG_tRNA_release` 状态转换：', '',
              '```text', rx['re0000000001']['equation'], '```', '',
              '在当前模型交接见证中，它先产生 E2；随后第一次 Gly-tRNA 延伸结合反应 `re0000000013` 消耗 E2：', '',
              '```text', rx['re0000000013']['equation'], '```', '',
              '这验证了源模型中 0001 → 0013 的状态依赖顺序。不得把此顺序直接解释为真实细菌核糖体中'
              '起始 tRNA 释放、肽键形成和转位的完整物理机制，也不据此确定常规生理时间顺序。'
              '本 follow-up 的事实权威是原始 SBML 方程及状态依赖；没有新增论文级物理机制证书。', '',
              'E1/E2 的 mRNA、肽基状态及完整复合物组分继续为 `INFERRED`。源物种 ID 的连续性不等于全局分子组成验证；'
              '不从名称缺失推断 mRNA 释放，也不自行补写化学步骤。', '',
              '## 后续原文证据需求（与当前解释限制分列）', '']
    lines += ['- ' + q['question'] + ' — `' + q['status'] + '`.' for q in data['future_original_source_evidence_required']]
    lines += ['', '本次仅补充结构正例及审阅证据。正式接受仍待研究者确认；不得 commit/push、开始 B1-2、QSSA 或动力学降阶。']
    return '\n'.join(lines) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, default=OUT)
    args = p.parse_args()
    data = build()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write(args.output_dir / 'phase_b1_1_followup_witness.json', data)
    (args.output_dir / 'phase_b1_1_followup_pathway.md').write_bytes(markdown(data).encode('utf-8'))
    print(json.dumps({'status': 'BUILT', 'events': len(data['new_witness']['reaction_occurrences']),
                      'reaction_sequence': [e['reaction_id'] for e in data['new_witness']['reaction_occurrences']]}))


if __name__ == '__main__':
    main()
