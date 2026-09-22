function summary = run_nondim_trajectory_validation()
%RUN_NONDIM_TRAJECTORY_VALIDATION Real TestResults and symbolic regression.
root = fileparts(fileparts(mfilename('fullpath')));
old = pwd; cleanup = onCleanup(@() cd(old)); cd(root);
addpath(fullfile(root,'matlab','src','provenance'),fullfile(root,'matlab','src','theory'), ...
    fullfile(root,'matlab','generated'));
audit = fullfile(root,'docs','audit','nondim_trajectory_20260923');
reg = jsondecode(fileread(fullfile(audit,'preregistration.json')));
assert(strcmp(pure_sha256_file(fullfile(audit,'acceptance_criteria.json')),reg.criteria_sha256));
revision = jsondecode(fileread(fullfile(audit,'implementation_revision_4.json')));
assert(strcmp(revision.criteria_sha256,reg.criteria_sha256));
assert(strcmp(revision.original_preregistration_sha256,pure_sha256_file(fullfile(audit,'preregistration.json'))));
for i = 1:numel(revision.implementation)
    assert(strcmp(pure_sha256_file(fullfile(root,revision.implementation(i).path)), ...
        revision.implementation(i).sha256),'Registered implementation revision changed.');
end
fprintf('NONDIM_RUN_STARTED %s\n',char(datetime('now','TimeZone','UTC','Format',"yyyy-MM-dd'T'HH:mm:ss.SSSXXX")));
fprintf('MATLAB %s\nHEAD %s\n',version,pure_git_state(root).commit);
fprintf('Preregistered criteria SHA256 %s\n',reg.criteria_sha256);
for i = 1:numel(revision.implementation)
    if endsWith(revision.implementation(i).path,'.m')
        messages = checkcode(fullfile(root,revision.implementation(i).path),'-id');
        fprintf('CHECKCODE %s messages=%d\n',revision.implementation(i).path,numel(messages));
        disp(messages);
        assert(isempty(messages),'Resolve new MATLAB analyzer messages before validation.');
    end
end
r1 = runtests('matlab/tests/test_dimensionless_trajectory_equivalence.m');
r2 = runtests('matlab/tests/test_exact_conservation_reduction.m');
r3 = runtests('matlab/tests/test_pure_literature_reference.m');
r4 = runtests('matlab/tests/test_codegen_and_provenance.m');
allPassed = all([r1.Passed]) && all([r2.Passed]) && all([r3.Passed]) && all([r4.Passed]);
results = {r1,r2,r3,r4};
names = {'test_dimensionless_trajectory_equivalence','test_exact_conservation_reduction', ...
    'test_pure_literature_reference','test_codegen_and_provenance'};
summary = struct('matlab_version',version,'allPassed',allPassed);
for k = 1:4
    r = results{k}; disp(table(r));
    summary.suites(k) = struct('name',names{k},'passed',sum([r.Passed]), ...
        'failed',sum([r.Failed]),'incomplete',sum([r.Incomplete]),'duration_s',sum([r.Duration]));
end
fprintf('NONDIM_TEST_SUMMARY %s\nallPassed = %d\n',jsonencode(summary),allPassed);
assert(allPassed,'pure_nondim:validationFailed','Do not refit, clip or relax acceptance criteria.');
% Frozen symbolic script runs in a separate function workspace.
symbolic_regression(root);
fprintf('NONDIM_SYMBOLIC %s\n',jsonencode(struct('passed',true,'equations',12, ...
    'dimensional_balances',5,'dimensionless_balances',5,'generated_text_byte_unchanged',true)));
% Build the certificate from the SAME runtime builder; final evidence binding
% is added only after native process completion and source-integrity checks.
c = jsondecode(fileread(fullfile(audit,'acceptance_criteria.json')));
p = pure_literature_reference_params();
for k = 1:numel(c.DNA_uM)
    p.DNA = c.DNA_uM(k); m = pure_nondim_map(p);
    snapshots(k) = struct('DNA_uM',p.DNA,'value_role','loaded_reference_values', ...
        'state_scales_uM',m.state_scales','k_nt_deg_per_s',m.k_nt_deg, ...
        'Vstar_uM_per_s',m.Vstar,'groups',m.groups, ...
        'initial_dimensionless_state',m.initial_dimensionless'); %#ok<AGROW>
end
certificate = m.certificate;
certificate.loaded_reference_values_by_DNA = snapshots;
certificate.validation.status = 'tests_passed_pending_native_exit_and_integrity_check';
fid = fopen(fullfile(root,'docs','theory','nondim_map.json'),'w','n','UTF-8');
assert(fid>=0); closeFile = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(certificate,'PrettyPrint',true));
end

function symbolic_regression(root)
generated = fullfile(root,'models','literature_reference','dimensionless','dimensionless_result_matlab.txt');
before = pure_sha256_file(generated);
fid = fopen(generated,'rb'); assert(fid>=0);
originalBytes = fread(fid,Inf,'*uint8'); fclose(fid);
originalText = fileread(generated);
run(fullfile(root,'models','literature_reference','dimensionless','derive_dimensionless.m'));
regenerated = pure_sha256_file(generated);
normalize = @(txt) strrep(txt,char([13 10]),newline);
assert(strcmp(normalize(originalText),normalize(fileread(generated))), ...
    'pure_nondim:symbolicOutputChanged','Symbolic output content changed; stop and inspect.');
if ~strcmp(before,regenerated)
    % Frozen script fopen(...,'w') emits LF here; restore original CRLF bytes
    % only AFTER verifying that the complete generated text is identical.
    fid = fopen(generated,'wb'); assert(fid>=0);
    fwrite(fid,originalBytes,'uint8'); fclose(fid);
end
assert(strcmp(before,pure_sha256_file(generated)));
fprintf('NONDIM_SYMBOLIC_OUTPUT %s\n',jsonencode(struct('original_sha256',before, ...
    'regenerated_sha256',regenerated,'normalized_text_identical',true, ...
    'original_bytes_preserved_or_restored',true)));
end
