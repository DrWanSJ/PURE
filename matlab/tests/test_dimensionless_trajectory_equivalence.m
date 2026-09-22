function tests = test_dimensionless_trajectory_equivalence()
%TEST_DIMENSIONLESS_TRAJECTORY_EQUIVALENCE Independent compact B1 runtime audit.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(fullfile(root,'matlab','generated'),fullfile(root,'matlab','src','simulate'), ...
    fullfile(root,'matlab','src','theory'),fullfile(root,'matlab','src','provenance'));
tests = functiontests(localfunctions);
end

function setupOnce(tc)
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
audit = fullfile(root,'docs','audit','nondim_trajectory_20260923');
c = jsondecode(fileread(fullfile(audit,'acceptance_criteria.json')));
reg = jsondecode(fileread(fullfile(audit,'preregistration.json')));
assert(strcmp(pure_sha256_file(fullfile(audit,'acceptance_criteria.json')),reg.criteria_sha256));
assert(isequal(c.DNA_uM(:)',[0.00034 0.0017 0.0068]));
assert(isequal([c.Tfinal_s c.OutputDt_s c.RelTol c.AbsTol],[14400 10 1e-10 1e-12]));
assert(all([c.max_normalized_state_error c.max_normalized_rate_error ...
    c.max_normalized_mRNA_error c.max_normalized_protein_error]==1e-6));
assert(c.rhs_absolute_tolerance==1e-12 && c.rate_backtransform_scaled_tolerance==1e-12);
assert(c.invariant_scaled_tolerance==1e-8 && c.output_points_per_condition==1441);
tc.TestData.criteria = c;
for k = 1:3
    args = {'Tfinal',c.Tfinal_s,'OutputDt',c.OutputDt_s,'RelTol',c.RelTol,'AbsTol',c.AbsTol};
    tc.TestData.full{k} = simulate_pure_literature_reference(c.DNA_uM(k),args{:});
    tc.TestData.nondim{k} = simulate_pure_literature_dimensionless(c.DNA_uM(k),args{:});
end
end

function test_mapping_roundtrips(tc)
p = pure_literature_reference_params(); p.DNA = 0.0017;
m = pure_nondim_map(p);
% Deterministic positive algebra fixtures, independent of conservation leaves.
X = [m.initial_dimensional'; ((1:12)/13).*m.state_scales'; ...
    ((12:-1:1)/7).*m.state_scales'; 1e-4*(1:12); 1e4*(1:12)];
Y = X./m.state_scales'; Xback = Y.*m.state_scales';
t = [0;1e-8;10;1234.5;14400]; tback = (m.k_nt_deg*t)/m.k_nt_deg;
V = reshape((1:30)/17,5,6); V(1,:) = 0;
Vback = (V/m.Vstar)*m.Vstar;
tc.verifyLessThanOrEqual(abs(Xback-X),64*eps(max(1,abs(X))));
tc.verifyLessThanOrEqual(abs(tback-t),64*eps(max(1,abs(t))));
tc.verifyLessThanOrEqual(abs(Vback-V),64*eps(max(1,abs(V))));
fprintf('NONDIM_ROUNDTRIP %s\n',jsonencode(struct( ...
    'state_max_abs_uM',max(abs(Xback-X),[],'all'), ...
    'time_max_abs_s',max(abs(tback-t)), ...
    'rate_max_abs_uM_per_s',max(abs(Vback-V),[],'all'))));
end

function test_canonical_initial_condition(tc)
for k = 1:3
    r = tc.TestData.nondim{k};
    expected = [1;0;0;1;1;0;0;1;0;1;0;0];
    tc.verifyEqual(r.map.initial_dimensionless,expected);
    tc.verifyEqual(r.ydimless(1,:)',expected);
    tc.verifyEqual(r.yfull(1,:)',[r.p.y0;0;0]);
end
fprintf('NONDIM_INITIAL %s\n',jsonencode(tc.TestData.nondim{1}.map.initial_dimensionless'));
end

function test_parameter_definitions_and_metadata(tc)
p = pure_literature_reference_params(); p.DNA = 0.0017;
for trial = 1:2
    if trial == 2
        % In-memory algebra stress only: detect fixed 2.3 or fixed pool scales.
        p.y0 = p.y0.*(1+(1:10)'/13)+(1:10)'/17;
        p.n_NTP = 1.3*p.n_NTP; p.n_A = 1.1*p.n_A; p.n_T = 0.8*p.n_T;
        p.k_nt_deg = 1.7*p.k_nt_deg; p.k_TL_deg = 0.7*p.k_TL_deg;
        p.DNA = 0;
    end
    m = pure_nondim_map(p); g = m.groups;
    s = [p.y0(1);p.n_NTP*p.y0(1);p.n_NTP*p.y0(1);p.y0(4); ...
        p.y0(5);p.y0(5);p.n_A*p.y0(4);p.y0(8);p.y0(8);p.y0(10); ...
        p.n_NTP*p.y0(1);p.y0(10)];
    tc.verifyEqual(m.state_scales,s);
    tc.verifyEqual(m.k_nt_deg,p.k_nt_deg);
    tc.verifyEqual(m.Vstar,p.k_nt_deg*p.n_NTP*p.y0(1),'RelTol',1e-14);
    names = {'fTA','mu_TX','mu_RS','mu_TL','mu_EN','mu_TLdeg','theta_DNA', ...
        'kappa_TX_NTP','kappa_RS_A','kappa_RS_T','kappa_RS_NTP','kappa_TL_nt', ...
        'kappa_TL_AT','kappa_TL_NTP','kappa_EN_CP','kappa_EN_NXP', ...
        'rho_A','rho_T','rho_C','TLcat_to_nucleotide_scale'};
    expected = [p.n_T/p.n_A, p.k_TX*p.TXcat/(p.k_nt_deg*s(2)), ...
        p.k_RS*p.RScat/(p.k_nt_deg*s(2)),p.k_TL*s(10)/(p.k_nt_deg*s(2)), ...
        p.k_EN*p.ENcat/(p.k_nt_deg*s(2)),p.k_TL_deg/p.k_nt_deg, ...
        p.DNA/(p.K_TX_DNA+p.DNA),p.K_TX_NTP/s(1),p.K_RS_A/s(4), ...
        p.K_RS_T*p.n_A/(p.n_T*s(5)),p.K_RS_NTP/s(1),p.K_TL_nt/s(3), ...
        p.K_TL_AT*p.n_A/(p.n_T*s(6)),p.K_TL_NTP/s(1),p.K_EN_CP/s(8), ...
        p.K_EN_NXP/s(2),s(2)/(p.n_A*s(4)),s(2)/(p.n_T*s(5)), ...
        s(2)/s(8),s(10)/s(2)];
    tc.verifyEqual(sort(fieldnames(g)),sort(names(:)));
    for i = 1:numel(names)
        tc.verifyEqual(g.(names{i}),expected(i),'AbsTol',64*eps(max(1,abs(expected(i)))));
    end
    tc.verifyNotEqual(g.rho_A,g.rho_T);
    tc.verifyEqual(m.certificate.state_order,m.state_order);
    tc.verifyEqual(numel(m.certificate.states),12);
    tc.verifyEqual(m.certificate.dimensionless_state_order, ...
        arrayfun(@(i) sprintf('y%d',i),1:12,'UniformOutput',false));
    tc.verifyEqual(sort(fieldnames(m.certificate.dimensionless_group_definitions)),sort(names(:)));
    [dy,v] = rhs_pure_literature_dimensionless(0,(1:12)'/13,g);
    x = s.*((1:12)'/13);
    [dx,V] = rhs_pure_literature_reference(0,x(1:10),p);
    tc.verifyLessThanOrEqual(max(abs(dy-[dx;V(2);V(5)]./(s*p.k_nt_deg))),1e-12);
    tc.verifyEqual(v(5)*m.Vstar,p.k_TL_deg*x(10),'AbsTol',1e-12);
end
fprintf('NONDIM_PARAMETERS %s\n',jsonencode(struct('groups_checked',numel(names), ...
    'canonical_and_synthetic',true,'source','loaded p plus in-memory algebra stress fixture')));
end

function test_pointwise_rhs_equivalence(tc)
maxError = 0; count = 0; rawRate = zeros(1,6);
for k = 1:3
    f = tc.TestData.full{k}; m = tc.TestData.nondim{k}.map;
    for i = unique(round(linspace(1,numel(f.t),17)))
        x = f.yfull(i,:)'; y = x./m.state_scales;
        [dcompact,v] = rhs_pure_literature_dimensionless(m.k_nt_deg*f.t(i),y,m.groups);
        [dx,V] = rhs_pure_literature_reference(f.t(i),x(1:10),f.p);
        direct = [dx;V(2);V(5)]./(m.state_scales*m.k_nt_deg);
        maxError = max(maxError,max(abs(dcompact-direct)));
        rawRate = max(rawRate,abs(v*m.Vstar-V)); count = count+1;
    end
end
tc.verifyLessThanOrEqual(maxError,tc.TestData.criteria.rhs_absolute_tolerance);
tc.verifyLessThanOrEqual(max(rawRate),tc.TestData.criteria.rhs_absolute_tolerance);
fprintf('NONDIM_RHS %s\n',jsonencode(struct('max_absolute_residual',maxError, ...
    'feasible_trajectory_points',count,'rate_max_abs_per_quantity',rawRate)));
end

function test_passive_states_do_not_feed_back(tc)
m = tc.TestData.nondim{1}.map; y = (1:12)'/17;
[dy,v] = rhs_pure_literature_dimensionless(0,y,m.groups);
y(11:12) = [53;79];
[dy2,v2] = rhs_pure_literature_dimensionless(999,y,m.groups);
tc.verifyEqual(dy2,dy); tc.verifyEqual(v2,v);
end

function test_analytic_jacobian(tc)
% Complex-step differentiation independently checks every Jacobian entry.
maxScaled = 0; maxInvariantDerivative = 0; count = 0;
for k = 1:3
    r = tc.TestData.nondim{k}; g = r.map.groups; s = r.map.state_scales;
    l6 = [0 s(2) 0 0 0 -r.p.n_T*s(6) -3*s(7) 0 s(9) 0 0 0];
    for i = unique(round(linspace(1,numel(r.t),17)))
        y = r.ydimless(i,:)'; J = jacobian_pure_literature_dimensionless(r.tau(i),y,g);
        numerical = zeros(12,12);
        for j = 1:12
            z = y; z(j) = z(j)+1i*1e-20;
            numerical(:,j) = imag(rhs_pure_literature_dimensionless(r.tau(i),z,g))/1e-20;
        end
        maxScaled = max(maxScaled,max(abs(J-numerical)./max(1,abs(numerical)),[],'all'));
        dy = rhs_pure_literature_dimensionless(r.tau(i),y,g);
        maxInvariantDerivative = max(maxInvariantDerivative,abs(l6*dy*r.p.k_nt_deg));
        count = count+1;
    end
end
tc.verifyLessThanOrEqual(maxScaled,1e-12);
tc.verifyLessThanOrEqual(maxInvariantDerivative,tc.TestData.criteria.rhs_absolute_tolerance);
fprintf('NONDIM_JACOBIAN %s\n',jsonencode(struct('points',count, ...
    'max_scaled_complex_step_residual',maxScaled, ...
    'max_abs_I6_derivative_uM_per_s',maxInvariantDerivative)));
end

function test_trajectory_DNA_low(tc)
check_trajectory(tc,1);
end

function test_trajectory_DNA_middle(tc)
check_trajectory(tc,2);
end

function test_trajectory_DNA_high(tc)
check_trajectory(tc,3);
end

function test_compact_rate_backtransform(tc)
for k = 1:3
    r = tc.TestData.nondim{k};
    e = trajectory_error(r.rates_backtransformed,r.rates);
    scale = max(max(abs(r.rates),[],1),1);
    scaled = e.raw_max_abs_per_quantity./scale;
    tc.verifyLessThanOrEqual(max(scaled),tc.TestData.criteria.rate_backtransform_scaled_tolerance);
    tc.verifyEqual(r.compact_rates(:,2),r.ydimless(:,3));
    tc.verifyEqual(r.rates_backtransformed(:,5),r.p.k_TL_deg*r.yfull(:,10),'AbsTol',1e-12);
    fprintf('NONDIM_RATE_BACKTRANSFORM %s\n',jsonencode(struct('DNA_uM',r.p.DNA, ...
        'raw_max_abs_per_rate',e.raw_max_abs_per_quantity,'comparison_scale',scale, ...
        'scaled_residual_per_rate',scaled,'max_scaled_residual',max(scaled))));
end
end

function test_physicality_and_six_invariants(tc)
for k = 1:3
    r = tc.TestData.nondim{k}; f = tc.TestData.full{k}; p = r.p; X = r.yfull;
    b = pure_exact_conservation_constants(p); b0 = cell2mat(struct2cell(b))';
    B = [p.n_NTP*X(:,1)+X(:,2)+X(:,3)+X(:,11), ...
        p.n_A*X(:,4)+X(:,7)+p.n_T*X(:,6),p.n_T*(X(:,5)+X(:,6)), ...
        X(:,8)+X(:,9),X(:,10)+X(:,12),X(:,2)+X(:,9)-3*X(:,7)-p.n_T*X(:,6)];
    raw = max(abs(B-b0),[],1); scale = max(abs(b0),1); scaled = raw./scale;
    allowance = 64*eps(max([1;abs(p.y0);abs(b0(:))]));
    tc.verifyTrue(r.qc.all_finite);
    tc.verifyTrue(all(isfinite([f.yfull f.rates f.mRNA f.protein]),'all'));
    tc.verifyGreaterThanOrEqual(min(X,[],'all'),-allowance);
    tc.verifyGreaterThanOrEqual(min(f.yfull,[],'all'),-allowance);
    tc.verifyLessThanOrEqual(max(scaled),tc.TestData.criteria.invariant_scaled_tolerance);
    fprintf('NONDIM_PHYSICALITY %s\n',jsonencode(struct('DNA_uM',p.DNA, ...
        'all_finite',r.qc.all_finite,'state_names',{r.full_state_names}, ...
        'backtransform_min_per_state',min(X,[],1), ...
        'backtransform_negative_count_per_state',sum(X<0,1), ...
        'reference_min_per_state',min(f.yfull,[],1), ...
        'reference_negative_count_per_state',sum(f.yfull<0,1), ...
        'roundoff_allowance_uM',allowance,'invariant_names',{fieldnames(b)'}, ...
        'invariant_reference',b0,'invariant_scale',scale, ...
        'invariant_raw_max_abs_per_quantity',raw,'invariant_scaled_residual_per_quantity',scaled, ...
        'max_abs_invariant_residual',max(raw),'max_scaled_invariant_residual',max(scaled))));
end
end

function test_output_grid_and_zero_DNA(tc)
for tf = [7 25]
    r = simulate_pure_literature_dimensionless(0,'Tfinal',tf,'OutputDt',10);
    expected = unique([(0:10:tf)';tf]);
    tc.verifySize(r.ydimless,[numel(expected),12]);
    tc.verifyEqual(r.t,expected,'AbsTol',64*eps(max(1,tf)));
    tc.verifyEqual(r.tau,r.map.k_nt_deg*expected);
    tc.verifyEqual(r.map.groups.theta_DNA,0);
    tc.verifyEqual(r.rates(:,1),zeros(numel(expected),1));
    tc.verifyTrue(r.qc.all_finite);
end
end

function check_trajectory(tc,k)
r = tc.TestData.nondim{k}; f = tc.TestData.full{k}; c = tc.TestData.criteria;
tc.assertEqual(f.t,(0:c.OutputDt_s:c.Tfinal_s)');
tc.verifyEqual(r.t,f.t,'AbsTol',64*eps(c.Tfinal_s));
tc.verifyEqual(r.tau,r.map.k_nt_deg*f.t);
tc.verifyEqual(r.physical_output_grid,f.t);
tc.verifyEqual(r.p,f.p); tc.verifyEqual(r.opts,f.opts);
tc.verifySize(r.yfull,[1441 12]); tc.verifySize(r.rates,[1441 6]);
tc.verifyEqual(r.yfull,r.ydimless.*r.map.state_scales');
tc.verifyEqual(r.mRNA,r.yfull(:,3)/(3*r.p.L));
tc.verifyEqual(r.protein,r.yfull(:,7)/r.p.L);
m = struct('DNA_uM',r.p.DNA,'output_points',numel(r.t), ...
    'tau_final',r.tau(end),'max_time_roundtrip_error_s',max(abs(r.t-f.t)), ...
    'state_names',{r.full_state_names},'rate_names',{r.p.rate_names});
m.states = trajectory_error(r.yfull,f.yfull);
m.rates = trajectory_error(r.rates,f.rates);
m.compact_backtransformed_rates = trajectory_error(r.rates_backtransformed,f.rates);
m.mRNA = trajectory_error(r.mRNA,f.mRNA); m.protein = trajectory_error(r.protein,f.protein);
tc.verifyLessThanOrEqual(m.states.max_normalized,c.max_normalized_state_error);
tc.verifyLessThanOrEqual(m.rates.max_normalized,c.max_normalized_rate_error);
tc.verifyLessThanOrEqual(m.compact_backtransformed_rates.max_normalized,c.max_normalized_rate_error);
tc.verifyLessThanOrEqual(m.mRNA.max_normalized,c.max_normalized_mRNA_error);
tc.verifyLessThanOrEqual(m.protein.max_normalized,c.max_normalized_protein_error);
m.trajectory_pass = all([m.states.max_normalized m.rates.max_normalized ...
    m.compact_backtransformed_rates.max_normalized m.mRNA.max_normalized m.protein.max_normalized]<=1e-6);
fprintf('NONDIM_CASE %s\n',jsonencode(m));
end

function e = trajectory_error(candidate,reference)
e.scale = max(max(abs(reference),[],1),1e-12);
e.raw_max_abs_per_quantity = max(abs(candidate-reference),[],1);
e.normalized_per_quantity = e.raw_max_abs_per_quantity./e.scale;
e.max_raw_abs = max(e.raw_max_abs_per_quantity);
e.max_normalized = max(e.normalized_per_quantity);
end
