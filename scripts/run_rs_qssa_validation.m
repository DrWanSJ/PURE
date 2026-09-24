function summary = run_rs_qssa_validation(varargin)
%RUN_RS_QSSA_VALIDATION Retain native TestResults and all formal D7 runs.
% RunLabel must be new; prior evidence is never overwritten.
root = fileparts(fileparts(mfilename('fullpath')));
old = pwd; cleanup = onCleanup(@() cd(old)); cd(root);
addpath(fullfile(root,'scripts'),fullfile(root,'matlab','generated'), ...
    fullfile(root,'matlab','src','theory'),fullfile(root,'matlab','src','provenance'));
ip = inputParser;
ip.addParameter('RunLabel','run_001',@(x) ischar(x) && ~isempty(regexp(x,'^run_[0-9]+$','once')));
ip.addParameter('FullSuite',true,@islogical);
ip.parse(varargin{:}); opt = ip.Results;
audit = fullfile(root,'docs','audit','rs_qssa_d7_20260924');
runDir = fullfile(audit,opt.RunLabel);
assert(~exist(runDir,'dir'),'pure_rs:existingRun','Choose a new RunLabel; never overwrite evidence.');
% Both files must already be committed and unmodified before running.
for name = {'acceptance_criteria.json','preregistration.json'}
    rel = ['docs/audit/rs_qssa_d7_20260924/' name{1}];
    [status,committed] = system(['git show cec84861ab829bf451d6902283e5f078a6e89401:' rel]);
    assert(status==0 && strcmp(strtrim(committed),strtrim(fileread(fullfile(root,rel)))), ...
        'pure_rs:changedPreregistration','Preregistered criteria changed.');
end
mkdir(runDir);
summary = struct('run_label',opt.RunLabel,'started_utc', ...
    char(datetime('now','TimeZone','UTC','Format',"yyyy-MM-dd'T'HH:mm:ssXXX")), ...
    'matlab_version',version,'git',pure_git_state(root), ...
    'preregistration_commit','cec84861ab829bf451d6902283e5f078a6e89401', ...
    'criteria_sha256',pure_sha256_file(fullfile(audit,'acceptance_criteria.json')));
diary(fullfile(runDir,'matlab_stdout.txt'));
diaryCleanup = onCleanup(@() diary('off'));
fprintf('D7_RUN_STARTED %s\n',jsonencode(summary));
export_rs_qssa_parameters();
files = [dir(fullfile(root,'matlab','src','theory','*rs*.m')); ...
    dir(fullfile(root,'matlab','tests','test_rs_qssa_reduction.m')); ...
    dir(fullfile(root,'scripts','*rs_qssa*.m')); ...
    dir(fullfile(root,'scripts','run_all_tests.m'))];
for i = 1:numel(files)
    path = fullfile(files(i).folder,files(i).name);
    messages = checkcode(path,'-id');
    rel = strrep(path(numel(root)+2:end),'\','/');
    summary.checkcode(i) = struct('path',rel,'messages',messages);
    summary.implementation(i) = struct('path',rel,'sha256',pure_sha256_file(path));
    fprintf('CHECKCODE %s messages=%d\n',rel,numel(messages)); disp(messages);
end
oldArtifactDir = getenv('PURE_D7_ARTIFACT_DIR');
envCleanup = onCleanup(@() setenv('PURE_D7_ARTIFACT_DIR',oldArtifactDir));
setenv('PURE_D7_ARTIFACT_DIR',runDir);
r = [];
testText = evalc("r = runtests(fullfile(root,'matlab','tests','test_rs_qssa_reduction.m'));");
fprintf('%s',testText); disp(table(r));
summary.d7_tests = counts(r);
summary.native_test_results = test_records(r);
save(fullfile(runDir,'native_TestResults.mat'),'r');
summary.measurements = extract_records(testText);
setenv('PURE_D7_ARTIFACT_DIR','');
if opt.FullSuite
    repo = struct();
    repoText = evalc('repo = run_all_tests();');
    % run_all_tests owns its own diary; resume this run's log afterwards.
    diary(fullfile(runDir,'matlab_stdout.txt'));
    fprintf('%s',repoText);
    summary.repository = repo;
    summary.all_passed = all([r.Passed]) && ~any([r.Incomplete]) ...
        && repo.unit_tests_failed==0 && repo.unit_tests_incomplete==0 ...
        && strcmp(repo.smoke_test,'passed');
else
    summary.all_passed = all([r.Passed]) && ~any([r.Incomplete]);
end
summary.finished_utc = char(datetime('now','TimeZone','UTC','Format',"yyyy-MM-dd'T'HH:mm:ssXXX"));
fprintf('D7_TEST_SUMMARY %s\n',jsonencode(summary.d7_tests));
fprintf('D7_ALL_PASSED %d\n',summary.all_passed);
write_json(fullfile(runDir,'validation_results.json'),summary);
write_json(fullfile(audit,'validation_results.json'),summary);
diary off;
copyfile(fullfile(runDir,'matlab_stdout.txt'),fullfile(audit,'matlab_stdout.txt'));
end

function c = counts(r)
c = struct('Passed',sum([r.Passed]),'Failed',sum([r.Failed]), ...
    'Incomplete',sum([r.Incomplete]),'Duration_s',sum([r.Duration]));
end

function rows = test_records(r)
rows = repmat(struct('Name','','Passed',false,'Failed',false, ...
    'Incomplete',false,'Duration_s',0),numel(r),1);
for i = 1:numel(r)
    rows(i) = struct('Name',r(i).Name,'Passed',r(i).Passed,'Failed',r(i).Failed, ...
        'Incomplete',r(i).Incomplete,'Duration_s',r(i).Duration);
end
end

function records = extract_records(txt)
records = struct();
matches = regexp(txt,'(?m)^D7_([A-Z_]+) (\{[^\r\n]*\})','tokens');
for i = 1:numel(matches)
    key = matches{i}{1}; value = jsondecode(matches{i}{2});
    if ~isfield(records,key)
        records.(key) = value;
    else
        records.(key)(end+1) = value;
    end
end
end

function write_json(path,value)
fid = fopen(path,'w','n','UTF-8'); assert(fid>=0);
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s\n',jsonencode(value,'PrettyPrint',true));
end
