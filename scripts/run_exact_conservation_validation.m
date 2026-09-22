function summary = run_exact_conservation_validation()
%RUN_EXACT_CONSERVATION_VALIDATION Persist actual required MATLAB TestResults.
root = fileparts(fileparts(mfilename('fullpath')));
old = pwd; cleanup = onCleanup(@() cd(old)); cd(root);
addpath(fullfile(root,'matlab','src','provenance'));
fprintf('MATLAB %s\n', version);
fprintf('HEAD %s\n', pure_git_state(root).commit);
criteria = fullfile(root,'docs','audit','exact_conservation_20260922','acceptance_criteria.json');
fprintf('Preregistered criteria SHA256 %s\n', pure_sha256_file(criteria));
r1 = runtests('matlab/tests/test_exact_conservation_reduction.m');
r2 = runtests('matlab/tests/test_pure_literature_reference.m');
r3 = runtests('matlab/tests/test_codegen_and_provenance.m');
allPassed = all([r1.Passed]) && all([r2.Passed]) && all([r3.Passed]);
results = {r1,r2,r3};
names = {'test_exact_conservation_reduction','test_pure_literature_reference','test_codegen_and_provenance'};
summary = struct('matlab_version',version,'allPassed',allPassed);
for k = 1:3
    r = results{k};
    disp(table(r));
    s = struct('name',names{k},'passed',sum([r.Passed]), ...
        'failed',sum([r.Failed]),'incomplete',sum([r.Incomplete]), ...
        'duration_s',sum([r.Duration]));
    summary.suites(k) = s;
    fprintf('SUITE %s passed=%d failed=%d incomplete=%d\n', ...
        s.name,s.passed,s.failed,s.incomplete);
end
fprintf('EXACT_REDUCTION_TEST_SUMMARY %s\n', jsonencode(summary));
fprintf('allPassed = %d\n', allPassed);
assert(allPassed, 'pure_exact:validationFailed', ...
    'Validation failed. Do not fit, clip, relax criteria, or claim success.');
end
