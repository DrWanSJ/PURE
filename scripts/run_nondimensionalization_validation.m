function summary = run_nondimensionalization_validation(outputDir)
%RUN_NONDIMENSIONALIZATION_VALIDATION V2 TestResults and measured JSON.
% First run records the new audit; reruns use a temporary directory by default
% so neither failed attempts nor historical evidence are silently overwritten.
root = fileparts(fileparts(mfilename('fullpath')));
old = pwd; cleanup = onCleanup(@() cd(old)); cd(root);
addpath(fullfile(root,'scripts'),fullfile(root,'matlab','src','provenance'));
audit = fullfile(root,'docs','audit','nondimensionalization_validation_v2_20260923');
if nargin < 1
    outputDir = audit;
    if isfile(fullfile(outputDir,'validation_results.json')), outputDir = tempname; end
end
if ~isfolder(outputDir), mkdir(outputDir); end
resultPath = fullfile(outputDir,'validation_results.json');
assert(~isfile(resultPath),'Do not overwrite recorded validation evidence.');
reg = jsondecode(fileread(fullfile(audit,'preregistration.json')));
criteriaHash = pure_sha256_file(fullfile(audit,'acceptance_criteria.json'));
assert(strcmp(criteriaHash,reg.criteria_sha256),'Preregistered criteria changed.');
summary = struct('source_commit',pure_git_state(root).commit,'matlab_version',version, ...
    'criteria_sha256',criteriaHash,'allPassed',false,'overall','FAIL');
summary.validation_version = 'v2';
summary.preregistration_sha256 = pure_sha256_file(fullfile(audit,'preregistration.json'));
summary.historical_v1_status = 'FAIL';
summary.legacy_composite_derivative_role = 'diagnostic_only';
summary.implementation = reg.implementation;
summary.started_at_utc = char(datetime('now','TimeZone','UTC','Format',"yyyy-MM-dd'T'HH:mm:ssXXX"));
for k = 1:numel(reg.implementation)
    item = reg.implementation(k);
    actualHash = pure_sha256_file(fullfile(root,item.path));
    assert(strcmp(actualHash,item.sha256),'Preregistered implementation changed: %s',item.path);
    messages = checkcode(fullfile(root,item.path),'-id');
    summary.checkcode(k) = struct('path',item.path,'messages',numel(messages));
    disp(messages);
    assert(isempty(messages),'Resolve MATLAB analyzer messages before numerical validation.');
end
mapPath = fullfile(root,'models','literature_reference','dimensionless','nondim_map.json');
if ~isfile(mapPath), export_pure_nondim_map(mapPath,summary.source_commit); end
names = {'test_nondimensionalization_validation','test_exact_conservation_reduction', ...
    'test_pure_literature_reference','test_codegen_and_provenance', ...
    'test_dimensionless_trajectory_equivalence'};
allPassed = true;
for k = 1:numel(names)
    captured = evalc('r = runtests(fullfile(root,''matlab'',''tests'',[names{k} ''.m'']));');
    fprintf('%s',captured); disp(table(r));
    summary.suites(k) = struct('name',names{k},'passed',sum([r.Passed]), ...
        'failed',sum([r.Failed]),'incomplete',sum([r.Incomplete]),'duration_s',sum([r.Duration]));
    allPassed = allPassed && ~isempty(r) && all([r.Passed]) && ~any([r.Incomplete]);
    if k==1
        summary.cases = parse_records(captured,'REDUCED_NONDIM_CASE');
        summary.state_roundtrip = parse_records(captured,'REDUCED_NONDIM_STATE_ROUNDTRIP');
        summary.time_roundtrip = parse_records(captured,'REDUCED_NONDIM_TIME_ROUNDTRIP');
        summary.symbolic_centered_equivalence = parse_records(captured,'REDUCED_NONDIM_SYMBOLIC');
        if numel(summary.cases)==3
            summary.same_state_rhs_max_abs = max([summary.cases.same_full_state_derivative_max_abs]);
            summary.legacy_composite_derivative_residual = max([summary.cases.legacy_composite_derivative_residual]);
            reconstructed = [summary.cases.reconstruction];
            summary.reconstruction_condition_scaled_max = max([reconstructed.condition_scaled_max]);
            allPassed = allPassed && all([summary.cases.pass]);
        else
            allPassed = false;
        end
    end
end
summary.allPassed = allPassed;
if allPassed, summary.overall = 'PASS'; end
summary.finished_at_utc = char(datetime('now','TimeZone','UTC','Format',"yyyy-MM-dd'T'HH:mm:ssXXX"));
fid = fopen(resultPath,'w','n','UTF-8'); assert(fid>=0);
closeFile = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(summary,'PrettyPrint',true));
fprintf('Validation results: %s\n',resultPath);
assert(allPassed,'pure_nondim:validationFailed','Validation failed; do not relax criteria or claim D6 completion.');
end

function result = parse_records(output,marker)
matches = regexp(output,[marker ' (\{[^\r\n]*\})'],'tokens');
result = struct([]);
if isempty(matches), return; end
result = jsondecode(matches{1}{1});
for k = 2:numel(matches)
    result(k) = jsondecode(matches{k}{1});
end
end
