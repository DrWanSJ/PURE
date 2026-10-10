"""Freeze a reviewed research release without rewriting its historical evidence.

Run after verification and dashboard generation. Every original file is retained
in Git, including failed campaigns and raw trajectories; category is not an
instruction to delete, ignore or regenerate the file.
"""
import argparse
import ast
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / 'docs/reduction/rapid_reduction'
BASELINE = DOC / 'release_preflight_20261010.json'
MANIFEST = DOC / 'release_manifest_v1.json'
GRAPH = DOC / 'release_evidence_navigation_v1.json'
MILESTONE = 'PNAS2017_PHASE_C_REDUCTION_V1_20261010'
ALLOWED_TRACKED = {
    '.gitattributes', 'README.md', 'docs/README.md', 'tasklist.md',
    'docs/visualization/visualization_plan.md',
    'docs/visualization/reduction_reasoning_atlas.html',
    'scripts/reduction_reasoning_atlas.template.html',
    'scripts/build_reduction_reasoning_atlas.py',
    'scripts/test_reduction_reasoning_atlas.py',
}
ADDITIVE_FILES = {
    'docs/reduction/pathways/phase_b1_3_formal_acceptance_20261010.md',
    'docs/visualization/phase_c_release_v1.json',
    'scripts/build_phase_c_dashboard.py', 'scripts/test_phase_c_dashboard.py',
    'scripts/phase_c_dashboard.css', 'scripts/phase_c_dashboard.js',
    'scripts/phase_c_dashboard.inc',
    'docs/reduction/rapid_reduction/current_decision_v1.json',
    'docs/reduction/rapid_reduction/human_decision_source_20261010.txt',
    'docs/reduction/rapid_reduction/independent_mathematical_audit_20261010.md',
    'docs/reduction/rapid_reduction/phase_c_formal_acceptance_20261010.md',
    'docs/reduction/rapid_reduction/release_notes_v1.md',
    'docs/reduction/rapid_reduction/release_preflight_20261010.json',
    'docs/reduction/rapid_reduction/release_manifest_v1.json',
    'docs/reduction/rapid_reduction/release_evidence_navigation_v1.json',
    'docs/reduction/rapid_reduction/publication_gate_review_20261010.json',
    'scripts/reduction/rapid_v1/package_release.py',
    'scripts/reduction/rapid_v1/release.py',
    'scripts/reduction/rapid_v1/requirements-release.txt',
    'scripts/reduction/rapid_v1/test_release.py',
    'scripts/reduction/rapid_v1/verify_b1_3_release.py',
    'results/reduction/phase_c_release_v1/cross_parser_matrix.json',
}
ADDITIVE_PREFIXES = (
    'results/reduction/phase_c_release_v1/b1_3_20261010/',
    'results/reduction/phase_c_release_v1/closure_20261010/',
    'results/reduction/phase_c_release_v1/dashboard/',
    'results/reduction/phase_c_release_v1/publication_verify_20261010/',
    'results/reduction/phase_c_release_v1/publication_verify_20261010_final/',
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, obj):
    path.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode())


def git(*args):
    return subprocess.check_output(['git', '-c', 'core.quotepath=false', *args],
                                   cwd=ROOT, text=True, encoding='utf-8').splitlines()


def classify(path):
    p = Path(path)
    if p.suffix == '.npz':
        return 'ARCHIVAL_SCIENTIFIC_DATA', 'Original numerical arrays, accepted-step inventories and local failure fixtures'
    if '/errors/' in path or p.suffix == '.png' or p.name in {
        'window_errors.csv', 'cost_and_feasibility.csv', 'model_summary.json',
        'review_and_decision.pdf',
    }:
        return 'REGENERABLE_OUTPUT', 'Derived table or figure retained with its original bytes'
    return 'VERSION_CONTROL_REQUIRED', 'Source, configuration, mathematical or review evidence, run metadata or critical summary'


def inspect_original(row):
    p = ROOT / row['path']
    assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], row['path']
    if p.suffix == '.py':
        ast.parse(p.read_text(encoding='utf-8'))
        return {'format': 'PYTHON_SOURCE', 'parse': 'PASS'}
    if p.suffix == '.json':
        x = load(p)
        return {'format': 'JSON', 'structure': 'object' if isinstance(x, dict) else 'array',
                'entries': len(x), 'parse': 'PASS'}
    if p.suffix == '.jsonl':
        lines = p.read_text(encoding='utf-8-sig').splitlines()
        for line in lines:
            if line.strip():
                json.loads(line)
        return {'format': 'JSONL', 'entries': len(lines), 'parse': 'PASS'}
    if p.suffix == '.csv':
        with p.open(encoding='utf-8-sig', newline='') as handle:
            rows = list(csv.reader(handle))
        assert rows and rows[0]
        return {'format': 'CSV', 'data_rows': len(rows)-1, 'columns': len(rows[0]), 'parse': 'PASS'}
    if p.suffix == '.npz':
        import numpy as np
        with np.load(p, allow_pickle=False) as arrays:
            shapes = {key: list(arrays[key].shape) for key in arrays.files}
            assert 't' in shapes
            finite = all(bool(np.isfinite(arrays[key]).all()) for key in arrays.files if arrays[key].dtype.kind in 'fc')
        return {'format': 'NPZ', 'arrays': shapes, 'parse': 'PASS', 'finite_arrays': finite,
                'meaning': 'Format/integrity inspection only; historical failures remain evidence'}
    if p.suffix == '.pdf':
        assert p.read_bytes().startswith(b'%PDF-')
    if p.suffix == '.png':
        assert p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    return {'format': p.suffix.lstrip('.').upper(), 'identity': 'SHA256_VERIFIED'}


def original_entry(row):
    path = row['path']
    category, role = classify(path)
    historical = '/campaign_scoring_v1/' in path or path.endswith('validation_results_scoring_implementation_v1.json')
    return {**row, 'category': category, 'role': role,
            'inspection': inspect_original(row),
            'reproduction_command': ('git archive --format=zip --output=<new-archive.zip> <release-commit> ' + path
                if row['origin'] == 'B1_3' or historical else
                'python scripts/reduction/rapid_v1/release.py reproduce --run-id <new-unique-id>'),
            'reproduction_note': ('Historical bytes are retrieved from Git and SHA-256 verified; never regenerate this path. '
                'A fresh numerical run reproduces scientific objects and scores, not machine times, logs or historical failed scoring bytes.'),
            'preservation_location': 'git:' + path,
            'publication': 'INCLUDED_IN_GIT', 'original_research_file': True}


def build():
    baseline = load(BASELINE)
    originals = baseline['original_research_files']
    assert len(originals) == 277
    changed = []
    for row in baseline['tracked']:
        if not (ROOT / row['path']).is_file() or sha(ROOT / row['path']) != row['sha256']:
            changed.append(row['path'])
    assert set(changed) <= ALLOWED_TRACKED, ('UNAUTHORIZED_TRACKED_CHANGE', changed)
    entries = [original_entry(row) for row in originals]
    paths = {row['path'] for row in entries}
    extras = set(changed)
    untracked = set(git('ls-files', '--others', '--exclude-standard'))
    unknown = sorted(p for p in untracked - paths - ADDITIVE_FILES
                     if not p.startswith(ADDITIVE_PREFIXES))
    assert not unknown, ('UNKNOWN_UNTRACKED_WORK_STOP', unknown)
    extras.update(untracked)
    # Also works after committing: all additive paths are known from the release
    # directories, while frozen originals are de-duplicated by their paths.
    for base in [DOC, ROOT / 'results/reduction/phase_c_release_v1']:
        if base.exists():
            extras.update(p.relative_to(ROOT).as_posix() for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    extras.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'scripts/reduction/rapid_v1').glob('*') if p.is_file())
    extras.update(ADDITIVE_FILES)
    exclusions = {p.relative_to(ROOT).as_posix() for p in [MANIFEST, GRAPH]}
    for path in sorted(extras - paths - exclusions):
        p = ROOT / path
        if not p.is_file():
            continue
        assert '__pycache__' not in p.parts and p.suffix != '.pyc', path
        category, role = classify(path)
        entries.append({'path': path, 'bytes': p.stat().st_size, 'sha256': sha(p),
                        'category': category,
                        'origin': 'FORMAL_RELEASE_CLOSURE_20261010',
                        'role': 'Acceptance, packaging, verification or existing dashboard upgrade',
                        'reproduction_command': 'python scripts/reduction/rapid_v1/release.py verify --run-id <new-unique-id> --require-manifest',
                        'reproduction_note': 'Verify published bytes; human acceptance records are not generated scientific results.',
                        'preservation_location': 'git:' + path, 'publication': 'INCLUDED_IN_GIT',
                        'original_research_file': False})
    source_paths = [
        'models/pnas2017_full_reference/original/fMGG_synthesis.xml',
        'models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv',
        'results/reduction/chain01_v2/mathematical_certificate.json',
    ]
    sources = [{'path': path, 'bytes': (ROOT/path).stat().st_size, 'sha256': sha(ROOT/path)} for path in source_paths]
    manifest = {
        'schema': 'PHASE_C_RELEASE_MANIFEST_V1', 'milestone': MILESTONE,
        'decision_date': '2026-10-10', 'starting_head': baseline['starting_head'],
        'authorized_branch': baseline['branch'],
        'scientific_status': 'PHASE_C_FORMALLY_ACCEPTED_WITH_SCOPE_CONDITIONS',
        'numerical_gate_status': 'FULL_COUPLED_CANDIDATE_GATES_PASS',
        'source_inputs_and_older_certificate': sources,
        'original_inventory': {'B1_3': 26, 'PHASE_C': 251,
            'bytes': sum(row['bytes'] for row in originals),
            'categories': {category: sum(row['category'] == category for row in entries if row['original_research_file'])
                           for category in ['VERSION_CONTROL_REQUIRED', 'REGENERABLE_OUTPUT',
                                            'ARCHIVAL_SCIENTIFIC_DATA', 'CACHE_OR_TEMPORARY']},
            'all_original_bytes_unchanged': True},
        'storage': {'strategy': 'ALL_ORIGINAL_EVIDENCE_VERSIONED_IN_GIT',
            'largest_original_file_bytes': max(row['bytes'] for row in originals),
            'external_archive_required': False, 'intentionally_excluded_original_files': [],
            'retrieval': 'Fetch the authorized branch on the other computer using its normal two-computer workflow, then run release.py verify. All 277 original files are Git objects; no sean-local-only evidence dependency.'},
        'authorized_tracked_changes': sorted(changed),
        'protected_tracked_files_unchanged': len(baseline['tracked']) - len(changed),
        'self_hash_exclusions': sorted(exclusions),
        'self_hash_note': 'These two hash-index files are identified by the release Git commit; no fabricated self-hash.',
        'files': sorted(entries, key=lambda row: row['path']),
    }
    save(MANIFEST, manifest)
    nodes = [{'id': row['path'], 'path': row['path'], 'sha256': row['sha256'],
              'source_authority': 'HUMAN_CONVERSATION_DECISION' if 'formal_acceptance_20261010' in row['path'] or 'human_decision_source' in row['path'] or 'current_decision' in row['path'] else 'DERIVED_RESEARCH_EVIDENCE',
              'evidence_status': 'EXTRACTED', 'confidence': 'BYTES_VERIFIED; CLAIM_SCOPE_RETAINED',
              'freshness': {'date': '2026-10-10', 'starting_head': baseline['starting_head'], 'sha256': row['sha256']}}
             for row in manifest['files']]
    nodes += [{**row, 'id': row['path'], 'source_authority': 'CANONICAL_INPUT_OR_HISTORICAL_CERTIFICATE',
               'evidence_status': 'EXTRACTED', 'confidence': 'SOURCE_HASH_VERIFIED'} for row in sources]
    edges = [
        {'from': 'docs/reduction/pathways/phase_b1_3_review.md', 'to': 'docs/reduction/pathways/phase_b1_3_formal_acceptance_20261010.md', 'relation': 'HISTORICAL_PENDING_SUPERSEDED_AS_CURRENT_DECISION'},
        {'from': 'docs/reduction/rapid_reduction/review_and_decision.md', 'to': 'docs/reduction/rapid_reduction/phase_c_formal_acceptance_20261010.md', 'relation': 'HISTORICAL_PENDING_SUPERSEDED_AS_CURRENT_DECISION'},
        {'from': 'docs/reduction/rapid_reduction/mathematical_certificate.json', 'to': 'docs/reduction/rapid_reduction/phase_c_formal_acceptance_20261010.md', 'relation': 'MATHEMATICAL_EVIDENCE_WITH_DOMAIN_CONDITIONS'},
        {'from': 'results/reduction/rapid_v1/validation_results.json', 'to': 'docs/visualization/reduction_reasoning_atlas.html', 'relation': 'FROZEN_NUMERICAL_PRESENTATION_SOURCE'},
        {'from': 'docs/reduction/rapid_reduction/human_decision_source_20261010.txt', 'to': 'docs/reduction/rapid_reduction/current_decision_v1.json', 'relation': 'AUTHORIZED_CONVERSATION_DECISION'},
    ]
    save(GRAPH, {'schema': 'PHASE_C_RELEASE_EVIDENCE_NAVIGATION_V1', 'milestone': MILESTONE,
                 'manifest_sha256': sha(MANIFEST), 'nodes': nodes, 'edges': edges,
                 'ambiguities': [{'status': 'AMBIGUOUS', 'subject': 'general parameter and initial-condition validity', 'effect': 'Not approved'},
                                 {'status': 'AMBIGUOUS', 'subject': 'charge, osmosis and general sequence validity', 'effect': 'Not certified'}]})
    print(json.dumps({'files': len(entries), 'originals': manifest['original_inventory'],
                      'protected_tracked_files_unchanged': manifest['protected_tracked_files_unchanged'],
                      'manifest_sha256': sha(MANIFEST)}))


def verify():
    m = load(MANIFEST)
    bad = [row['path'] for row in m['files'] + m['source_inputs_and_older_certificate']
           if not (ROOT/row['path']).is_file() or sha(ROOT/row['path']) != row['sha256']]
    assert not bad, bad
    assert load(GRAPH)['manifest_sha256'] == sha(MANIFEST)
    print(json.dumps({'status': 'PASS', 'manifest_files': len(m['files']), 'changed': bad}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'verify'])
    args = parser.parse_args()
    (build if args.command == 'build' else verify)()
