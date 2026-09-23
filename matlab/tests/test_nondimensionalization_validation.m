function tests = test_nondimensionalization_validation()
%TEST_NONDIMENSIONALIZATION_VALIDATION Validation version v2.
% Separate same-state RHS identity, affine reconstruction roundoff, and
% independent trajectories. Historical v1 composite failure is diagnostic.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(fullfile(root,'scripts'),fullfile(root,'matlab','generated'), ...
    fullfile(root,'matlab','src','theory'),fullfile(root,'matlab','src','simulate'), ...
    fullfile(root,'matlab','src','provenance'));
tests = functiontests(localfunctions);
end

function setupOnce(tc)
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
audit = fullfile(root,'docs','audit','nondimensionalization_validation_v2_20260923');
c = jsondecode(fileread(fullfile(audit,'acceptance_criteria.json')));
reg = jsondecode(fileread(fullfile(audit,'preregistration.json')));
assert(strcmp(pure_sha256_file(fullfile(audit,'acceptance_criteria.json')),reg.criteria_sha256));
assert(strcmp(c.validation_version,'v2') && c.same_state_rhs_abs==1e-12);
assert(c.reconstruction_condition_scaled==64*eps('double'));
tc.TestData.root = root; tc.TestData.c = c;
args = {'Tfinal',c.Tfinal_s,'OutputDt',c.OutputDt_s,'RelTol',c.RelTol, ...
    'AbsTol',c.AbsTol_dimensional_uM};
for k = 1:numel(c.DNA_uM)
    f = simulate_pure_literature_reference(c.DNA_uM(k),args{:});
    d = simulate_pure_exact_reduced(c.DNA_uM(k),args{:});
    n = simulate_pure_exact_reduced_nondim(c.DNA_uM(k),args{:});
    tc.TestData.full{k} = f; tc.TestData.reduced{k} = d; tc.TestData.nondim{k} = n;
    tc.TestData.metrics{k} = measure_case(f,d,n,c);
    fprintf('REDUCED_NONDIM_CASE %s\n',jsonencode(tc.TestData.metrics{k}));
end
end

function test_mapping_scales(tc)
n = tc.TestData.nondim{1}; m = n.map; p = n.p;
tc.verifyTrue(all(isfinite(m.state_scales) & m.state_scales>0));
tc.verifyGreaterThan([m.k_nt_deg m.Vstar],0);
tc.verifyEqual(m.state_scales([1 3 4 6 8 10]), ...
    [p.y0(1);p.n_NTP*p.y0(1);p.y0(4);p.y0(5);p.y0(8);p.y0(10)]);
tc.verifyNotEqual(m.groups.rho_A,m.groups.rho_T);
tc.verifyEqual(n.solver_AbsTol_dimensionless, ...
    tc.TestData.c.AbsTol_dimensional_uM./m.state_scales([1 3 4 6 8 10]));
end

function test_state_roundtrip(tc)
m = tc.TestData.nondim{1}.map;
X = [m.initial_dimensional'; ((1:12)/17).*m.state_scales'; ...
    ((12:-1:1)/13).*m.state_scales'; 1e-4*(1:12);1e4*(1:12)];
raw = abs((X./m.state_scales').*m.state_scales'-X);
scaled = max(raw./max(1,abs(X)),[],'all');
tc.verifyLessThanOrEqual(scaled,tc.TestData.c.roundtrip_max_relative_to_max_one);
fprintf('REDUCED_NONDIM_STATE_ROUNDTRIP %s\n', ...
    jsonencode(struct('max_abs_uM',max(raw,[],'all'),'max_scaled',scaled)));
end

function test_time_roundtrip(tc)
m = tc.TestData.nondim{1}.map; t = [0;1e-8;10;1234.5;14400];
raw = abs(m.k_nt_deg*t/m.k_nt_deg-t); scaled = max(raw./max(1,abs(t)));
tc.verifyLessThanOrEqual(scaled,tc.TestData.c.roundtrip_max_relative_to_max_one);
fprintf('REDUCED_NONDIM_TIME_ROUNDTRIP %s\n', ...
    jsonencode(struct('max_abs_s',max(raw),'max_scaled',scaled)));
end

function test_initial_condition(tc)
for k = 1:3
    n = tc.TestData.nondim{k};
    tc.verifyEqual(n.map.initial_dimensionless,[1;0;0;1;1;0;0;1;0;1;0;0]);
    tc.verifyEqual(n.q(1,:)',n.map.initial_dimensionless([1 3 4 6 8 10]));
    tc.verifyEqual(n.yfull_dimensionless(1,:)',n.map.initial_dimensionless,'AbsTol',1e-14);
    tc.verifyEqual(n.yfull_dimensional(1,:)',n.map.initial_dimensional,'AbsTol',1e-12);
end
end

function test_direct_reconstruction(tc)
for k = 1:3
    e = tc.TestData.metrics{k};
    tc.verifyLessThanOrEqual(e.reconstruction_max_scaled,tc.TestData.c.reconstruction_max_relative_to_max_one);
end
end

function test_centered_symbolic_equivalence(tc)
result = diagnose_nondim_reconstruction('',true);
tc.verifyTrue(result.symbolic.all_passed);
tc.verifyEqual(result.symbolic.residuals,repmat({'0'},6,1));
fprintf('REDUCED_NONDIM_SYMBOLIC %s\n',jsonencode(result.symbolic));
end

function test_conditioning_scaled_reconstruction(tc)
for k = 1:3
    e = tc.TestData.metrics{k};
    tc.verifySize(e.reconstruction.condition_scaled,[17 6]);
    tc.verifyLessThanOrEqual(e.reconstruction.condition_scaled, ...
        tc.TestData.c.reconstruction_condition_scaled);
end
end

function test_invariant_constants(tc)
for k = 1:3
    n = tc.TestData.nondim{k}; p = n.p; m = n.map;
    b = pure_exact_conservation_constants(p);
    expected = [b.B_NTP/m.state_scales(2);b.B_AA/m.state_scales(2); ...
        b.B_tRNA/(p.n_T*m.state_scales(5));b.B_CP/m.state_scales(8); ...
        b.B_TLcat/m.state_scales(10);b.I6/m.state_scales(2)];
    tc.verifyEqual(n.invariants,expected,'AbsTol',1e-14);
end
end

function test_same_full_state_rhs_identity(tc)
for k = 1:3
    e = tc.TestData.metrics{k};
    tc.verifyEqual(e.derivative_points,tc.TestData.c.derivative_samples_per_DNA);
    tc.verifyLessThanOrEqual(e.same_full_state_derivative_max_abs,tc.TestData.c.same_state_rhs_abs);
end
end

function test_trajectory_low(tc), check_trajectory(tc,1); end
function test_trajectory_middle(tc), check_trajectory(tc,2); end
function test_trajectory_high(tc), check_trajectory(tc,3); end

function test_physicality(tc)
for k = 1:3
    e = tc.TestData.metrics{k}; tc.verifyTrue(e.all_finite);
    tc.verifyGreaterThanOrEqual(e.minimum_full_state,-e.roundoff_allowance_uM);
    tc.verifyEqual(e.meaningful_negative_count,0);
end
end

function test_six_invariant_residuals(tc)
for k = 1:3
    e = tc.TestData.metrics{k};
    tc.verifyLessThanOrEqual(max(e.invariant_scaled_residual),tc.TestData.c.invariant_max_scaled);
end
end

function test_all_six_rate_backtransforms(tc)
for k = 1:3
    e = tc.TestData.metrics{k};
    tc.verifyLessThanOrEqual(max(e.same_state_rate_scaled_residual),tc.TestData.c.rate_same_state_max_scaled);
    n = tc.TestData.nondim{k};
    tc.verifyEqual(n.dimensionless_rates(:,2),n.yfull_dimensionless(:,3));
    tc.verifyEqual(n.dimensional_rates(:,5),n.p.k_TL_deg*n.yfull_dimensional(:,10),'AbsTol',1e-14);
end
end

function test_json_matches_runtime(tc)
path = fullfile(tc.TestData.root,'models','literature_reference','dimensionless','nondim_map.json');
c = jsondecode(fileread(path));
expected = export_pure_nondim_map('',c.generated_from_commit);
tc.verifyEqual(c,jsondecode(jsonencode(expected)));
for k = 1:3
    n = tc.TestData.nondim{k};
    % Use the exported numbers as an actual transform, not metadata alone.
    tc.verifyEqual(n.q.*c.reduced_coordinates.scales_uM',n.z_dimensional);
    tc.verifyEqual(n.tau/c.time.k_nt_deg_per_s,n.t_s);
    tc.verifyEqual(c.dimensionless_parameters.input_dependent(k).theta_DNA,n.map.groups.theta_DNA);
end
end

function test_synthetic_algebra_fixture(tc)
% In-memory software regression only; not a new scientific parameter set.
p = pure_literature_reference_params(); p.DNA = 0;
p.y0 = p.y0.*(1+(1:10)'/13)+(1:10)'/17;
p.n_NTP = 1.3*p.n_NTP; p.n_A = 1.1*p.n_A; p.n_T = 0.8*p.n_T;
p.k_nt_deg = 1.7*p.k_nt_deg; p.k_TL_deg = 0.7*p.k_TL_deg;
m = pure_nondim_map(p); idx = [1 3 4 6 8 10]; s = m.state_scales(idx);
I = pure_dimensionless_invariants(m.initial_dimensionless,m);
b = pure_exact_conservation_constants(p);
expected = [b.B_NTP/m.state_scales(2);b.B_AA/m.state_scales(2); ...
    b.B_tRNA/(p.n_T*m.state_scales(5));b.B_CP/m.state_scales(8); ...
    b.B_TLcat/m.state_scales(10);b.I6/m.state_scales(2)];
tc.verifyEqual(I,expected,'AbsTol',1e-14);
tc.verifyEqual(m.state_scales(idx),[p.y0(1);p.n_NTP*p.y0(1);p.y0(4);p.y0(5);p.y0(8);p.y0(10)]);
for f = [1 0.999]
    q = f*m.initial_dimensionless(idx); y = reconstruct_pure_exact_reduced_nondim_state(q,m,I);
    x = reconstruct_pure_exact_reduced_state(s.*q,p,b);
    tc.verifyEqual(y,x./m.state_scales,'AbsTol',1e-12);
    dq = rhs_pure_exact_reduced_nondim(0,q,m,I);
    sameX = m.state_scales.*y;
    dx = rhs_pure_literature_reference(0,sameX(1:10),p);
    tc.verifyLessThanOrEqual(max(abs(dq-dx(idx)./s/m.k_nt_deg)),tc.TestData.c.same_state_rhs_abs);
    dep = [2 5 7 9 11 12]; terms = reconstruction_terms(y,m);
    tc.verifyLessThanOrEqual(abs(y(dep)-x(dep)./m.state_scales(dep))./max(terms,1), ...
        tc.TestData.c.reconstruction_condition_scaled);
end
tc.verifyEqual(m.groups.theta_DNA,0); tc.verifyNotEqual(m.groups.rho_A,m.groups.rho_T);
end

function test_short_output_grid(tc)
for tf = [7 25]
    n = simulate_pure_exact_reduced_nondim(0,'Tfinal',tf,'OutputDt',10);
    t = unique([(0:10:tf)';tf]);
    tc.verifySize(n.q,[numel(t),6]);
    tc.verifyEqual(n.t_s,t,'AbsTol',1e-13);
    tc.verifyTrue(n.qc.all_finite);
    tc.verifyEqual(n.dimensional_rates(:,1),zeros(numel(t),1));
end
end

function check_trajectory(tc,k)
e = tc.TestData.metrics{k}; c = tc.TestData.c;
tc.verifyEqual(e.output_points,c.output_points);
tc.verifyLessThanOrEqual(e.output_time_scaled_error,c.output_time_max_relative_to_max_one);
for name = {'states','rates','mRNA','protein'}
    tc.verifyLessThanOrEqual(e.canonical.(name{1}).max_normalized,c.trajectory_max_normalized);
    tc.verifyLessThanOrEqual(e.dimensional_reduced.(name{1}).max_normalized,c.trajectory_max_normalized);
end
end

function e = measure_case(f,d,n,c)
m = n.map; p = n.p; idx = [1 3 4 6 8 10]; s = m.state_scales(idx);
e.DNA_uM = p.DNA; e.output_points = numel(n.t_s);
e.state_names = m.state_order; e.rate_names = m.rate_order;
e.output_time_max_abs_s = max(abs(n.t_s-f.t));
e.output_time_scaled_error = max(abs(n.t_s-f.t)./max(1,abs(f.t)));
e.canonical = compare(n,f); e.dimensional_reduced = compare(n,d);
e.validation_version = 'v2';
e.legacy_composite_derivative_residual = 0; e.derivative_points = 0;
e.legacy_composite_derivative_role = 'diagnostic_only';
e.same_full_state_derivative_max_abs = 0;
e.sampled_NXP_reconstruction_difference_uM = 0;
b = pure_exact_conservation_constants(p);
samples = unique(round(linspace(1,numel(n.t_s),c.derivative_samples_per_DNA)));
dep = [2 5 7 9 11 12];
e.reconstruction.dependent_indices = dep;
e.reconstruction.sample_indices = samples;
for j = 1:numel(samples)
    i = samples(j);
    q = n.q(i,:)';
    dq = rhs_pure_exact_reduced_nondim(n.tau(i),q,m,n.invariants);
    dz = rhs_pure_exact_reduced(n.t_s(i),s.*q,p,b);
    % Legacy v1 composite metric remains visible, never a v2 acceptance gate.
    legacy = max(abs(dq-dz./s/m.k_nt_deg));
    e.legacy_composite_derivative_residual = max(e.legacy_composite_derivative_residual,legacy);
    e.legacy_composite_per_sample(j) = legacy;
    % Gate 1: exactly one reconstruction, shared physical full state.
    directX = m.state_scales.*n.yfull_dimensionless(i,:)';
    fullDX = rhs_pure_literature_reference(n.t_s(i),directX(1:10),p);
    e.same_full_state_derivative_max_abs = max(e.same_full_state_derivative_max_abs, ...
        max(abs(dq-fullDX(idx)./s/m.k_nt_deg)));
    e.sampled_NXP_reconstruction_difference_uM = max(e.sampled_NXP_reconstruction_difference_uM, ...
        abs(directX(2)-n.yfull_dimensional(i,2)));
    e.same_state_rhs_per_sample(j) = max(abs(dq-fullDX(idx)./s/m.k_nt_deg));
    % Gate 2: two reconstruction paths, scaled by centered affine term sums.
    y = n.yfull_dimensionless(i,:)';
    scaledDim = n.yfull_dimensional(i,:)'./m.state_scales;
    terms = reconstruction_terms(y,m);
    raw = abs(y(dep)-scaledDim(dep));
    e.reconstruction.raw_dimensionless(j,:) = raw';
    e.reconstruction.absolute_term_sums(j,:) = terms';
    e.reconstruction.condition_scaled(j,:) = (raw./max(terms,1))';
    e.reconstruction.raw_dimensional_uM(j,:) = abs(directX(dep)-n.yfull_dimensional(i,dep)')';
    e.derivative_points = e.derivative_points+1;
end
e.reconstruction.condition_scaled_max = max(e.reconstruction.condition_scaled,[],'all');
restored = n.yfull_dimensional./m.state_scales';
e.reconstruction_max_scaled = max(abs(restored-n.yfull_dimensionless)./max(1,abs(restored)),[],'all');
I = zeros(numel(n.t_s),6); R = zeros(numel(n.t_s),6);
for i = 1:numel(n.t_s)
    I(i,:) = pure_dimensionless_invariants(n.yfull_dimensionless(i,:)',m)';
    [~,R(i,:)] = rhs_pure_literature_reference(n.t_s(i),n.yfull_dimensional(i,1:10)',p);
end
e.invariant_names = {'I_NTP','I_AA','I_tRNA','I_CP','I_TLcat','I6'};
e.invariant_initial = n.invariants';
e.invariant_raw_residual = max(abs(I-n.invariants'),[],1);
e.invariant_scaled_residual = e.invariant_raw_residual./max(1,abs(n.invariants'));
e.same_state_rate_raw_residual = max(abs(R-n.dimensional_rates),[],1);
e.same_state_rate_scaled_residual = e.same_state_rate_raw_residual./max(1,max(abs(R),[],1));
bv = cell2mat(struct2cell(b));
e.roundoff_allowance_uM = 64*eps(max([1;abs(m.initial_dimensional);abs(bv)]));
e.minimum_full_state = min(n.yfull_dimensional,[],'all');
e.minimum_per_state = min(n.yfull_dimensional,[],1);
e.negative_count_per_state = sum(n.yfull_dimensional<0,1);
e.negative_count = sum(e.negative_count_per_state);
e.meaningful_negative_count = sum(n.yfull_dimensional < -e.roundoff_allowance_uM,'all');
e.reference_minimum = min(f.yfull,[],'all');
e.reduced_minimum = min(d.yfull,[],'all');
e.all_finite = n.qc.all_finite && all(isfinite([f.yfull f.rates d.yfull d.rates]),'all');
e.pass = e.all_finite && e.meaningful_negative_count==0 && ...
    e.same_full_state_derivative_max_abs<=c.same_state_rhs_abs && ...
    e.reconstruction.condition_scaled_max<=c.reconstruction_condition_scaled && ...
    max(e.invariant_scaled_residual)<=c.invariant_max_scaled && ...
    e.reconstruction_max_scaled<=c.reconstruction_max_relative_to_max_one && ...
    max(e.same_state_rate_scaled_residual)<=c.rate_same_state_max_scaled && ...
    e.output_points==c.output_points && e.output_time_scaled_error<=c.output_time_max_relative_to_max_one;
for name = {'states','rates','mRNA','protein'}
    e.pass = e.pass && e.canonical.(name{1}).max_normalized<=c.trajectory_max_normalized ...
        && e.dimensional_reduced.(name{1}).max_normalized<=c.trajectory_max_normalized;
end
end

function S = reconstruction_terms(y,m)
% Order [y2 y5 y7 y9 y11 y12], exactly as preregistered for v2.
y0 = m.initial_dimensionless; g = m.groups; d = y-y0;
S = [abs(y0(2))+abs(d(8)/g.rho_C)+abs(3*d(4)/g.rho_A)+abs(2*d(6)/g.rho_T); ...
    abs(y0(5))+abs(d(6)); ...
    abs(y0(7))+abs(d(4))+abs((g.rho_A/g.rho_T)*d(6)); ...
    abs(y0(9))+abs(d(8)); ...
    abs(y0(11))+abs(d(1))+abs(d(2))+abs(d(3)); ...
    abs(y0(12))+abs(d(10))];
end

function e = compare(n,r)
e.states = trajectory_error(n.yfull_dimensional,r.yfull);
e.rates = trajectory_error(n.dimensional_rates,r.rates);
e.mRNA = trajectory_error(n.mRNA,r.mRNA);
e.protein = trajectory_error(n.protein,r.protein);
end

function e = trajectory_error(candidate,reference)
e.scale = max(max(abs(reference),[],1),1e-12);
e.raw_max_abs_per_quantity = max(abs(candidate-reference),[],1);
e.normalized_per_quantity = e.raw_max_abs_per_quantity./e.scale;
e.max_normalized = max(e.normalized_per_quantity);
end
