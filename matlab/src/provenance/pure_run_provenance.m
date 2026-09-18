function prov = pure_run_provenance(root, run_inputs)
%PURE_RUN_PROVENANCE Assemble provenance fields for a new run (audit hardening).
%
%   PROV = PURE_RUN_PROVENANCE(ROOT, RUN_INPUTS)
%
%   ROOT       project root (containing models/, matlab/, results/)
%   RUN_INPUTS struct of the run's inputs, serialized canonically with
%              jsonencode (struct field order = serialization order) and
%              hashed with SHA-256 -> input_hash.
%
%   Returns the static provenance fields required in
%   results/runs/<run_id>/manifest.json. The caller adds run_id, created_at,
%   execution_status and scientific_status after (or during) the run.
%
%   Hash algorithm is fixed: SHA-256, lowercase hex (pure_sha256_file /
%   pure_sha256_string). git_commit and git_dirty are read LIVE from the
%   repository (pure_git_state); they are never inferred or back-filled.

req = {'model_definition.json', 'parameters.json'};
prov = struct();
prov.manifest_schema = '1.0';
prov.hash_algorithm  = 'SHA-256 (FIPS 180-4), lowercase hex';

def_path = fullfile(root, 'models', 'literature_reference', req{1});
par_path = fullfile(root, 'models', 'literature_reference', req{2});
if ~exist(def_path, 'file')
    error('pure_ref:provenance:noDefinition', ...
        'canonical model definition missing: %s', def_path);
end
if ~exist(par_path, 'file')
    error('pure_ref:provenance:noParameters', ...
        'parameter file missing: %s', par_path);
end
prov.model_definition_hash = pure_sha256_file(def_path);
prov.parameter_hash        = pure_sha256_file(par_path);

if ~isstruct(run_inputs)
    error('pure_ref:provenance:badInputs', 'run_inputs must be a struct');
end
prov.input_hash = pure_sha256_string(jsonencode(run_inputs));

git = pure_git_state(root);
prov.git_in_repo = git.in_repo;
prov.git_commit  = git.commit;
prov.git_dirty   = git.dirty;

prov.matlab_version = version;
prov.model_id = 'PURE_literature_reference';
end
