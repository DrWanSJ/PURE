function tests = test_codegen_and_provenance()
%TEST_CODEGEN_AND_PROVENANCE Generator-sync, numerical-equivalence and
% provenance tests added by the B1 audit hardening (branch audit/b1-hardening).
%
%   results = runtests('matlab/tests/test_codegen_and_provenance.m')
%
%   1. SHA-256 implementation pinned to the FIPS 180-4 known vector ("abc").
%   2. Regeneration sync: the checked-in generated RHS must be byte-stable
%      under the generator (canonical definition = single source).
%   3. Numerical equivalence: generated RHS vs the FROZEN AI-baseline
%      snapshot at fixed states, tolerance = exact (floating-point identity).
%   4. Stoichiometry cross-check: state_codegen expressions vs the
%      canonical stoichiometry matrix, to floating-point roundoff.
%   5. Git provenance: pure_git_state reads the LIVE commit/dirty state and
%      agrees with a direct git call.

thisdir = fileparts(mfilename('fullpath'));   % .../matlab/tests
root    = fileparts(fileparts(thisdir));      % project root
addpath(fullfile(root, 'matlab', 'generated'));
addpath(fullfile(root, 'matlab', 'simulate'));
addpath(fullfile(root, 'matlab', 'codegen'));
addpath(fullfile(root, 'matlab', 'provenance'));
tests = functiontests(localfunctions);
end

% =========================================================================
function test_sha256_known_vector(tc)
% FIPS 180-4 test vector: SHA-256("abc") = ba7816bf...
tmp = [tempname(), '.sha256test.txt'];
cleanup = onCleanup(@() delete(tmp));
fid = fopen(tmp, 'w');
fwrite(fid, 'abc', 'uchar');
fclose(fid);
expected = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad';
tc.verifyEqual(pure_sha256_file(tmp), expected, ...
    'pure_sha256_file does not implement the FIPS 180-4 test vector');
tc.verifyEqual(pure_sha256_string('abc'), expected, ...
    'pure_sha256_string does not implement the FIPS 180-4 test vector');
end

% =========================================================================
function test_generator_output_in_sync(tc)
% The checked-in generated RHS must be exactly what the canonical
% definition regenerates (byte-stable, modulo line endings/trailing blanks).
thisdir0 = fileparts(mfilename('fullpath'));  % .../matlab/tests
root    = fileparts(fileparts(thisdir0));  % project root
tmp = [tempname(), '.m'];
cleanup = onCleanup(@() delete(tmp));
generate_pure_literature_reference('OutputFile', tmp, 'SkipConsistencyCheck', true);
a = normalize_src(fileread(fullfile(root, 'matlab', 'generated', ...
    'rhs_pure_literature_reference.m')));
b = normalize_src(fileread(tmp));
tc.verifyEqual(b, a, ...
    'generated RHS is out of sync with model_definition.json - regenerate it');
end

% =========================================================================
function test_generated_matches_baseline_snapshot(tc)
% The generated RHS must be numerically IDENTICAL (not just close) to the
% frozen AI-baseline snapshot at multiple fixed states.
p = pure_literature_reference_params(); p.DNA = 0.0017;
rng(7);
Y = [p.y0'; p.y0'; p.y0' + 100*rand(8, 10)];   % y0 twice + 8 perturbed states
for i = 1:size(Y, 1)
    [d1, r1] = rhs_pure_literature_reference(0, Y(i, :), p);
    [d2, r2] = rhs_pure_literature_reference_baseline_snapshot(0, Y(i, :), p);
    tc.verifyEqual(d1, d2, sprintf('dydt differs from baseline snapshot at state %d', i));
    tc.verifyEqual(r1, r2, sprintf('rates differ from baseline snapshot at state %d', i));
end
end

% =========================================================================
function test_stoichiometry_matches_code(tc)
% Canonical stoichiometry matrix (with average-species divisors) must agree
% with the emitted state expressions to floating-point roundoff.
thisdir0 = fileparts(mfilename('fullpath'));  % .../matlab/tests
root    = fileparts(fileparts(thisdir0));  % project root
S = jsondecode(fileread(fullfile(root, 'models', 'literature_reference', ...
    'model_definition.json')));
p = pure_literature_reference_params(); p.DNA = 0.0068;
rng(20260918);
Y = [p.y0'; p.y0' + 500*rand(10, 10)];
Smat = S.stoichiometry.matrix;
divnames = S.stoichiometry.species_divisor;
maxviol = 0;
for i = 1:size(Y, 1)
    [dydt_gen, rates_gen] = rhs_pure_literature_reference(0, Y(i, :), p);
    R = rates_gen(:);
    for s = 1:numel(S.stoichiometry.species_order)
        dv = 1;
        spName = S.stoichiometry.species_order{s};
        if isfield(divnames, spName) && ~strcmp(divnames.(spName), '1')
            dv = p.(divnames.(spName));
        end
        expect = (Smat(s, :) * R) / dv;
        maxviol = max(maxviol, abs(expect - dydt_gen(s)));
    end
end
tc.verifyLessThan(maxviol, 1e-9, ...
    sprintf('stoichiometry vs state expressions violate to %.3e uM/s', maxviol));
end

% =========================================================================
function test_git_state_live(tc)
% pure_git_state must read LIVE repository facts, and its commit must agree
% with a direct `git rev-parse HEAD` call.
thisdir0 = fileparts(mfilename('fullpath'));  % .../matlab/tests
root    = fileparts(fileparts(thisdir0));  % project root
st = pure_git_state(root);
tc.verifyTrue(st.in_repo, 'project root must be inside a git work tree');
[stt, out] = system(sprintf('git -C "%s" rev-parse HEAD', root));
if stt == 0
    tc.verifyEqual(st.commit, strtrim(out), ...
        'pure_git_state commit must equal live git rev-parse HEAD');
else
    tc.verifyEqual(st.commit, 'unavailable_git_not_found');
end
tc.verifyTrue(islogical(st.dirty) || strcmp(st.dirty, 'unknown'), ...
    'git_dirty must be a real check result (logical) or unknown');
end

% =========================================================================
function t = normalize_src(txt)
t = strrep(txt, sprintf('\r\n'), sprintf('\n'));
lines = regexp(t, sprintf('\n'), 'split');
lines = regexprep(lines, '[ \t]+$', '');
lines = lines(1:max(find(~strcmp(strtrim(lines), ''))));   % drop trailing blanks
t = strjoin(lines, sprintf('\n'));
end
