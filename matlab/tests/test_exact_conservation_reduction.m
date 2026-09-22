function tests = test_exact_conservation_reduction()
%TEST_EXACT_CONSERVATION_REDUCTION D6 exact reduction, never QSSA or a fit.
% Thresholds preregistered in docs/audit/exact_conservation_20260922/acceptance_criteria.json.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(fullfile(root,'matlab','generated'), ...
    fullfile(root,'matlab','src','simulate'), fullfile(root,'matlab','src','theory'));
tests = functiontests(localfunctions);
end

function setupOnce(tc)
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
c = jsondecode(fileread(fullfile(root,'docs','audit', ...
    'exact_conservation_20260922','acceptance_criteria.json')));
% Refuse a changed preregistration, even if it would make a failing run pass.
assert(isequal(c.DNA_uM(:)', [0.00034 0.0017 0.0068]));
assert(isequal([c.Tfinal_s c.OutputDt_s c.RelTol c.AbsTol], [14400 10 1e-10 1e-12]));
assert(all([c.max_normalized_state_error c.max_normalized_rate_error ...
    c.max_normalized_mRNA_error c.max_normalized_protein_error] == 1e-6));
assert(c.derivative_absolute_tolerance == 1e-12 && c.structural_absolute_tolerance == 1e-14);
tc.TestData.criteria = c;
tc.TestData.full = cell(1,3);
tc.TestData.reduced = cell(1,3);
for k = 1:3
    args = {'Tfinal',c.Tfinal_s,'OutputDt',c.OutputDt_s,'RelTol',c.RelTol,'AbsTol',c.AbsTol};
    tc.TestData.full{k} = simulate_pure_literature_reference(c.DNA_uM(k), args{:});
    tc.TestData.reduced{k} = simulate_pure_exact_reduced(c.DNA_uM(k), args{:});
end
end

function test_initial_reconstruction(tc)
p = pure_literature_reference_params();
x = reconstruct_pure_exact_reduced_state(p.y0([1 3 4 6 8 10]), p);
tc.verifyEqual(x, [p.y0(:);0;0], 'AbsTol', 1e-12);
fprintf('EXACT_REDUCTION_INITIAL %s\n', jsonencode(x'));
end

function test_constants_follow_initial_state_and_multiplicities(tc)
% Synthetic algebra fixture only: no canonical file or simulation parameter is changed.
% Nonzero omitted physical pools and I6 expose standard-initial-value hardcoding.
p = pure_literature_reference_params();
p.y0 = 1.1*p.y0 + (1:10)'/10;
p.n_NTP = 1.25*p.n_NTP; p.n_A = 1.1*p.n_A; p.n_T = 0.9*p.n_T;
x0 = [p.y0;0;0];
[~, L] = structural_matrices(p);
b = pure_exact_conservation_constants(p);
tc.verifyEqual(cell2mat(struct2cell(b)), L*x0, 'AbsTol', 1e-10);
x = reconstruct_pure_exact_reduced_state(p.y0([1 3 4 6 8 10]), p, b);
tc.verifyEqual(x, x0, 'AbsTol', 1e-10);
end

function test_structural_regression(tc)
p = pure_literature_reference_params();
[S, L] = structural_matrices(p);
tc.verifySize(S, [12 6]);
tc.verifyEqual(rank(S), 6);
tc.verifyEqual(rank(L), 6);
residual = max(abs(L*S), [], 'all');
tc.verifyLessThanOrEqual(residual, tc.TestData.criteria.structural_absolute_tolerance);
% Independently read the canonical pre-divisor stoichiometry, then append sinks.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
def = jsondecode(fileread(fullfile(root,'models','literature_reference','model_definition.json')));
tc.verifyEqual(def.stoichiometry.species_order(:), p.state_names(:));
tc.verifyEqual(def.stoichiometry.rates_order(:), p.rate_names(:));
divisors = [p.n_NTP;1;1;p.n_A;p.n_T;p.n_T;1;1;1;1];
canonical = [def.stoichiometry.matrix./divisors; 0 1 0 0 0 0; 0 0 0 0 1 0];
tc.verifyEqual(S, canonical);
fprintf('EXACT_REDUCTION_STRUCTURE %s\n', jsonencode(struct( ...
    'shape',size(S),'rank_S',rank(S),'rank_L',rank(L),'max_abs_LS',residual)));
end

function test_derivative_consistency(tc)
maxError = 0;
for k = 1:3
    r = tc.TestData.reduced{k}; p = r.p;
    [S, ~] = structural_matrices(p);
    for i = unique(round(linspace(1,numel(r.t),17)))
        x = reconstruct_pure_exact_reduced_state(r.z(i,:)', p, r.invariants);
        [dy, rates] = rhs_pure_literature_reference(r.t(i), x(1:10), p);
        dz = rhs_pure_exact_reduced(r.t(i), r.z(i,:)', p, r.invariants);
        % Differentiate the reconstruction, independently of its implementation.
        dx = zeros(12,1); dx([1 3 4 6 8 10]) = dz;
        dx(5) = -dx(6);
        dx(7) = -p.n_A*dx(4) - p.n_T*dx(6);
        dx(9) = -dx(8);
        dx(2) = -dx(9) + 3*dx(7) + p.n_T*dx(6);
        dx(12) = -dx(10);
        dx(11) = -p.n_NTP*dx(1) - dx(2) - dx(3);
        augmented = [dy; rates(2); rates(5)];
        maxError = max([maxError; abs(dx-augmented); abs(S*rates(:)-augmented)]);
    end
end
tc.verifyLessThanOrEqual(maxError, tc.TestData.criteria.derivative_absolute_tolerance);
fprintf('EXACT_REDUCTION_DERIVATIVE max_abs=%.17g points=51\n', maxError);
end

function test_trajectory_DNA_low(tc)
check_trajectory(tc, 1);
end

function test_trajectory_DNA_middle(tc)
check_trajectory(tc, 2);
end

function test_trajectory_DNA_high(tc)
check_trajectory(tc, 3);
end

function test_physicality_and_six_invariants(tc)
for k = 1:3
    r = tc.TestData.reduced{k}; f = tc.TestData.full{k};
    [~, L] = structural_matrices(r.p);
    b0 = L*[r.p.y0;0;0];
    allowance = 64*eps(max([1;abs(r.p.y0);abs(b0)]));
    tc.verifyTrue(r.qc.all_finite);
    tc.verifyTrue(all(isfinite([f.yfull f.rates f.mRNA f.protein]), 'all'));
    % Also check accounting sinks; report raw negative magnitudes without repair.
    tc.verifyGreaterThanOrEqual(min(r.yfull,[],'all'), -allowance);
    tc.verifyGreaterThanOrEqual(min(f.yfull,[],'all'), -allowance);
    residual = max(abs(r.yfull*L' - b0'), [], 'all');
    tc.verifyLessThanOrEqual(residual, allowance);
    fprintf('EXACT_REDUCTION_PHYSICALITY %s\n', jsonencode(struct( ...
        'DNA_uM',r.p.DNA,'full_min_per_state',min(f.yfull,[],1), ...
        'reduced_min_per_state',r.qc.min_per_full_state, ...
        'reduced_negative_count_per_state',r.qc.negative_count_per_full_state, ...
        'roundoff_allowance_uM',allowance,'max_abs_invariant_residual',residual)));
end
end

function check_trajectory(tc, k)
f = tc.TestData.full{k}; r = tc.TestData.reduced{k}; c = tc.TestData.criteria;
tc.assertEqual(r.t, f.t);
tc.assertEqual(f.t, (0:c.OutputDt_s:c.Tfinal_s)');
tc.verifyEqual(r.opts, f.opts);
tc.verifyEqual(r.p, f.p);
tc.verifyEqual(r.z, r.yfull(:,[1 3 4 6 8 10]));
tc.verifyEqual(r.mRNA, r.yfull(:,3)/(3*r.p.L));
tc.verifyEqual(r.protein, r.yfull(:,7)/r.p.L);
m = struct('DNA_uM',r.p.DNA,'output_points',numel(r.t), ...
    'state_names',{r.full_state_names},'rate_names',{r.p.rate_names});
m.states = trajectory_error(r.yfull, f.yfull);
m.rates = trajectory_error(r.rates, f.rates);
m.mRNA = trajectory_error(r.mRNA, f.mRNA);
m.protein = trajectory_error(r.protein, f.protein);
tc.verifyLessThanOrEqual(m.states.max_normalized, c.max_normalized_state_error);
tc.verifyLessThanOrEqual(m.rates.max_normalized, c.max_normalized_rate_error);
tc.verifyLessThanOrEqual(m.mRNA.max_normalized, c.max_normalized_mRNA_error);
tc.verifyLessThanOrEqual(m.protein.max_normalized, c.max_normalized_protein_error);
m.trajectory_pass = all([m.states.max_normalized m.rates.max_normalized ...
    m.mRNA.max_normalized m.protein.max_normalized] <= 1e-6);
fprintf('EXACT_REDUCTION_CASE %s\n', jsonencode(m));
end

function e = trajectory_error(reduced, reference)
e.scale = max(max(abs(reference),[],1), 1e-12);
e.raw_max_abs_per_quantity = max(abs(reduced-reference),[],1);
e.normalized_per_quantity = e.raw_max_abs_per_quantity./e.scale;
e.max_raw_abs = max(e.raw_max_abs_per_quantity);
e.max_normalized = max(e.normalized_per_quantity);
end

function [S, L] = structural_matrices(p)
% Literal structure from docs/theory_notes.md sections 3.1 and 4.4;
% only the reference multiplicities are replaced with the loaded parameters.
S = [-1/p.n_NTP 0 -1/p.n_NTP -2/p.n_NTP 0 1/p.n_NTP;
     0 0 1 2 0 -1;
     1 -1 0 0 0 0;
     0 0 -1/p.n_A 0 0 0;
     0 0 -1/p.n_T 1/p.n_T 0 0;
     0 0 1/p.n_T -1/p.n_T 0 0;
     0 0 0 1 0 0;
     0 0 0 0 0 -1;
     0 0 0 0 0 1;
     0 0 0 0 -1 0;
     0 1 0 0 0 0;
     0 0 0 0 1 0];
L = [p.n_NTP 1 1 0 0 0 0 0 0 0 1 0;
     0 0 0 p.n_A 0 p.n_T 1 0 0 0 0 0;
     0 0 0 0 p.n_T p.n_T 0 0 0 0 0 0;
     0 0 0 0 0 0 0 1 1 0 0 0;
     0 0 0 0 0 0 0 0 0 1 0 1;
     0 1 0 0 0 -p.n_T -3 0 1 0 0 0];
end
