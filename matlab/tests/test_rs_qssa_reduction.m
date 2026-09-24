function tests = test_rs_qssa_reduction()
%TEST_RS_QSSA_REDUCTION Preregistered D7 synthetic RS reduction evidence.
% Independent formulas and complex-step derivatives test the full backbone.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(fullfile(root,'matlab','generated'),fullfile(root,'matlab','src','theory'), ...
    fullfile(root,'matlab','src','provenance'));
tests = functiontests(localfunctions);
end

function setupOnce(tc)
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
c = jsondecode(fileread(fullfile(root,'docs','audit', ...
    'rs_qssa_d7_20260924','acceptance_criteria.json')));
assert(isequal(c.DNA_uM(:)',[0.00034 0.0017 0.0068]));
assert(isequal([c.Tfinal_s c.OutputDt_s c.RelTol c.AbsTol],[14400 10 1e-10 1e-12]));
assert(isequal([c.phi_alpha c.phi_beta c.phi_gamma],[0.05 0.90 0.05]));
assert(c.reference_match_normalized==1e-12 && c.qss_residual_normalized==1e-12);
assert(c.manifold_derivative_normalized==1e-10 && c.chain_jacobian_normalized==1e-8);
assert(c.explicit_jacobian_normalized==1e-8 && c.fast_relaxation_normalized==1e-6);
assert(all([c.trajectory_max_normalized c.flux_max_normalized ...
    c.mRNA_max_normalized c.protein_max_normalized]==1e-3));
assert(c.invariant_max_normalized==1e-8 && c.epsilon_state_max_strict==1e-2);
assert(c.random_seed==20260924 && c.random_positive_states==64 && c.complex_step==1e-20);
tc.TestData.root = root; tc.TestData.c = c;
p = pure_literature_reference_params(); p.DNA = c.DNA_uM(2);
tc.TestData.p = p; tc.TestData.q = rs_reduction_parameters(p);
old_rng = rng; restore_rng = onCleanup(@() rng(old_rng));
rng(c.random_seed,'twister');
tc.TestData.states = max(abs(p.y0),1).*10.^(-2+3*rand(10,c.random_positive_states));
tc.TestData.occupancies = tc.TestData.q.E_T_ref*(0.05+0.9*rand(1,c.random_positive_states));
args = {'Tfinal',c.Tfinal_s,'OutputDt',c.OutputDt_s,'RelTol',c.RelTol,'AbsTol',c.AbsTol};
artifact_dir = getenv('PURE_D7_ARTIFACT_DIR');
for k = 1:numel(c.DNA_uM)
    f = simulate_pure_rs_explicit(c.DNA_uM(k),args{:});
    r = simulate_pure_rs_qssa(c.DNA_uM(k),args{:});
    tc.TestData.full{k} = f; tc.TestData.reduced{k} = r;
    if ~isempty(artifact_dir)
        export_trajectory(artifact_dir,k,f,r);
    end
end
end

function test_synthetic_parameter_provenance_schema(tc)
j = jsondecode(fileread(fullfile(tc.TestData.root,'models','reductions','rs_qssa','parameters.json')));
required = {'schema_version','model_id','source_type','evidence_level','input_commit', ...
    'construction','reference_state','parameters','source_review','source_fingerprints'};
tc.assertTrue(all(isfield(j,required)));
tc.verifyEqual(j.source_type,'synthetic_reduction_only');
tc.verifyTrue(contains(j.evidence_level,'synthetic'));
tc.verifyTrue(contains(j.evidence_level,'NOT experimentally supported'));
tc.verifyEqual(j.input_commit,'c2bb0ae63ba106d4f51bf2182dfd28dfe187e743');
tc.verifyNotEmpty(j.source_review); tc.verifyNotEmpty(j.source_fingerprints);
for i = 1:numel(j.source_fingerprints)
    source = j.source_fingerprints(i);
    tc.verifyEqual(pure_sha256_file(fullfile(tc.TestData.root,source.path)),source.sha256);
end
q = tc.TestData.q; p = tc.TestData.p;
tc.verifyEqual([j.construction.phi_alpha j.construction.phi_beta j.construction.phi_gamma], ...
    [0.05 0.90 0.05]);
tc.verifyNotEmpty(j.construction.method);
names = {'k1','kminus1','k2'}; units = {'uM^-2 s^-1','s^-1','uM^-1 s^-1'};
for k = 1:3
    v = j.parameters.(names{k});
    tc.verifyEqual(v.source_type,'synthetic_reduction_only');
    tc.verifyEqual(v.unit,units{k});
    tc.verifyLessThanOrEqual(abs(v.value-q.(names{k}))/abs(q.(names{k})),1e-12);
end
tc.verifyEqual(j.reference_state.state_order(:),p.state_names(:));
tc.verifyEqual(j.reference_state.y0(:),p.y0);
tc.verifyEqual(j.reference_state.fTA,p.n_T/p.n_A,'AbsTol',1e-14);
tc.verifyEqual(j.reference_state.T_eff0,(p.n_T/p.n_A)*p.y0(5),'AbsTol',1e-14);
tc.verifyEqual(j.reference_state.E_T,p.RScat);
tc.verifyEqual(j.reference_state.D_ref,q.D_ref,'RelTol',1e-12);
tc.verifyEqual(j.reference_state.tau_M_ref,1/q.D_ref,'RelTol',1e-12);
tc.verifyEqual(j.reference_state.V_RS_ref,q.V_RS_ref,'RelTol',1e-12);
tc.verifyEqual(j.reference_state.M_qss0,q.E_T_ref*q.phi_alpha,'RelTol',1e-12);
fprintf('\nD7_SCHEMA %s\n',jsonencode(struct('source_type',j.source_type, ...
    'evidence_level',j.evidence_level,'input_commit',j.input_commit,'schema_pass',true)));
end

function test_reference_parameter_construction(tc)
p = tc.TestData.p; q = tc.TestData.q;
[~,rates] = rhs_pure_literature_reference(0,p.y0,p);
D = rates(3)/(p.RScat*0.05*0.05);
expected = [0.05*D/(p.y0(4)*p.y0(1)),0.90*D,0.05*D/((p.n_T/p.n_A)*p.y0(5))];
tc.verifyEqual([q.k1 q.kminus1 q.k2],expected,'RelTol',1e-12);
tc.verifyEqual([q.phi_alpha q.phi_beta q.phi_gamma],[0.05 0.90 0.05]);
tc.verifyEqual(q.phi_alpha+q.phi_beta+q.phi_gamma,1,'AbsTol',eps);
tc.verifyEqual([q.alpha_ref q.beta_ref q.gamma_ref],[0.05 0.90 0.05]*D,'RelTol',1e-12);
tc.verifyEqual(q.E_T_ref,p.RScat); tc.verifyEqual(q.source_type,'synthetic_reduction_only');
[h,~,info] = rs_qssa_manifold(p.y0,p,q);
ef = abs(info.V_RS-rates(3))/abs(rates(3));
em = abs(h-p.RScat*0.05)/(p.RScat*0.05);
tc.verifyLessThanOrEqual(ef,tc.TestData.c.reference_match_normalized);
tc.verifyLessThanOrEqual(em,tc.TestData.c.reference_match_normalized);
fprintf('\nD7_PARAMETERS %s\n',jsonencode(struct('k1',q.k1,'kminus1',q.kminus1, ...
    'k2',q.k2,'D_ref',q.D_ref,'tau_M_ref',1/q.D_ref,'V_RS_ref',rates(3), ...
    'M_qss0',h,'E_T',q.E_T_ref,'phi_alpha',q.phi_alpha,'phi_beta',q.phi_beta, ...
    'phi_gamma',q.phi_gamma,'reference_flux_normalized_error',ef, ...
    'reference_M_normalized_error',em,'source_type',q.source_type)));
end

function test_manifold_and_multiplicity(tc)
p = tc.TestData.p; q = tc.TestData.q;
residual = 0; formula_error = 0;
for k = 1:size(tc.TestData.states,2)
    s = tc.TestData.states(:,k);
    [h,~,info] = rs_qssa_manifold(s,p,q);
    alpha = q.k1*s(4)*s(1); gamma = q.k2*(p.n_T/p.n_A)*s(5);
    D = alpha+q.kminus1+gamma; expected = q.E_T_ref*alpha/D;
    [dy,~,detail] = rhs_pure_rs_explicit(0,[s;h],p,q);
    rate_scale = max(abs(detail.v1_f)+abs(detail.v1_r)+abs(detail.v2),1e-12);
    residual = max(residual,abs(dy(11))/rate_scale);
    formula_error = max(formula_error,abs(h-expected)/max(abs(expected),1e-12));
    tc.verifyEqual([info.alpha info.beta info.gamma info.D info.tau_M info.V_RS], ...
        [alpha q.kminus1 gamma D 1/D gamma*h],'RelTol',1e-12);
end
% An altered multiplicity and a non-reference state expose a literal 2.3.
pa = p; pa.n_T = 57; pa.n_A = 13;
qa = rs_reduction_parameters(pa); sa = p.y0;
[~,ra] = rhs_pure_literature_reference(0,pa.y0,pa);
Da0 = ra(3)/(pa.RScat*0.05*0.05);
tc.verifyEqual(qa.k2,0.05*Da0/((pa.n_T/pa.n_A)*pa.y0(5)),'RelTol',1e-12);
sa([1 4 5]) = sa([1 4 5]).*[0.67;1.31;0.42];
[ha,~,ia] = rs_qssa_manifold(sa,pa,qa);
Da = qa.kminus1+qa.k2*(pa.n_T/pa.n_A)*sa(5)+qa.k1*sa(4)*sa(1);
expected_h = qa.E_T_ref*qa.k1*sa(4)*sa(1)/Da;
[~,~,da] = rhs_pure_rs_explicit(0,[sa;0.37*qa.E_T_ref],pa,qa);
expected_v2 = qa.k2*0.37*qa.E_T_ref*(pa.n_T/pa.n_A)*sa(5);
mult_error = max([abs(ha-expected_h)/expected_h, ...
    abs(ia.V_RS-qa.k2*(pa.n_T/pa.n_A)*sa(5)*expected_h)/max(abs(ia.V_RS),1e-12), ...
    abs(da.v2-expected_v2)/expected_v2]);
tc.verifyLessThanOrEqual(residual,tc.TestData.c.qss_residual_normalized);
tc.verifyLessThanOrEqual(formula_error,tc.TestData.c.reference_match_normalized);
tc.verifyLessThanOrEqual(mult_error,tc.TestData.c.reference_match_normalized);
fprintf('\nD7_ALGEBRA %s\n',jsonencode(struct('random_states',size(tc.TestData.states,2), ...
    'max_QSS_normalized_residual',residual,'max_manifold_formula_error',formula_error, ...
    'multiplicity_fixture_error',mult_error,'multiplicity_fixture_fTA',pa.n_T/pa.n_A)));
end

function test_backbone_stoichiometry_and_no_RS_double_count(tc)
p = tc.TestData.p; q = tc.TestData.q; max_error = 0;
for k = 1:size(tc.TestData.states,2)
    s = tc.TestData.states(:,k); M = tc.TestData.occupancies(k);
    [~,canonical] = rhs_pure_literature_reference(0,s,p);
    [dy,rates,detail] = rhs_pure_rs_explicit(0,[s;M],p,q);
    vf = q.k1*s(4)*s(1)*(q.E_T_ref-M); vr = q.kminus1*M;
    v2 = q.k2*M*(p.n_T/p.n_A)*s(5); vn = vf-vr;
    expected = independent_rhs(canonical,vn,v2,p);
    max_error = max(max_error,scaled_derivative_error(dy,expected));
    tc.verifyEqual(rates([1 2 4 5 6]),canonical([1 2 4 5 6]));
    tc.verifyEqual(rates(3),v2,'RelTol',1e-12);
    tc.verifyEqual([detail.v1_f detail.v1_r detail.v1_net detail.v2 detail.canonical_V_RS], ...
        [vf vr vn v2 canonical(3)],'RelTol',1e-12);
    % With microparameters held fixed, canonical RS is diagnostic only.
    pp = p; pp.k_RS = 100*p.k_RS;
    changed = rhs_pure_rs_explicit(0,[s;M],pp,q);
    max_error = max(max_error,scaled_derivative_error(changed,dy));
    [h,~,info] = rs_qssa_manifold(s,p,q);
    reduced = rhs_pure_rs_qssa(0,s,p,q);
    full_on_manifold = rhs_pure_rs_explicit(0,[s;h],p,q);
    expected_reduced = independent_rhs(canonical,info.V_RS,info.V_RS,p);
    max_error = max([max_error,scaled_derivative_error(reduced,expected_reduced(1:10)), ...
        scaled_derivative_error(reduced,full_on_manifold(1:10))]);
    changed_reduced = rhs_pure_rs_qssa(0,s,pp,q);
    max_error = max(max_error,scaled_derivative_error(changed_reduced,reduced));
end
tc.verifyLessThanOrEqual(max_error,tc.TestData.c.qss_residual_normalized);
fprintf('\nD7_BACKBONE %s\n',jsonencode(struct('max_normalized_RHS_error',max_error, ...
    'canonical_non_RS_rates_reused',true,'canonical_RS_no_feedback',true)));
end

function test_manifold_and_full_chain_derivatives(tc)
p = tc.TestData.p; q = tc.TestData.q; step = tc.TestData.c.complex_step;
edh = 0; echain = 0; efull = 0; eimplicit = 0; chain_effect = 0;
for k = 1:size(tc.TestData.states,2)
    s = tc.TestData.states(:,k); M = tc.TestData.occupancies(k);
    [~,dh] = rs_qssa_manifold(s,p,q);
    numerical_dh = complex_jacobian(@(x) rs_qssa_manifold(x,p,q),s,step);
    [J,b] = jacobian_pure_rs_qssa_chain(0,s,p,q);
    numerical_J = complex_jacobian(@(x) rhs_pure_rs_qssa(0,x,p,q),s,step);
    full_J = jacobian_pure_rs_explicit(0,[s;M],p,q);
    numerical_full = complex_jacobian(@(x) rhs_pure_rs_explicit(0,x,p,q),[s;M],step);
    tc.verifySize(dh,[1 10]); tc.verifySize(J,[10 10]); tc.verifySize(full_J,[11 11]);
    tc.verifySize(b.Fs,[10 10]); tc.verifySize(b.FM,[10 1]);
    tc.verifySize(b.Gs,[1 10]); tc.verifySize(b.GM,[1 1]);
    tc.verifyEqual(J,b.Fs+b.FM*dh,'AbsTol',1e-12);
    tc.verifyEqual(b.dh,dh,'AbsTol',1e-12);
    edh = max(edh,scaled_derivative_error(dh,numerical_dh));
    echain = max(echain,scaled_derivative_error(J,numerical_J));
    efull = max(efull,scaled_derivative_error(full_J,numerical_full));
    eimplicit = max(eimplicit,scaled_derivative_error(dh,-b.Gs/b.GM));
    chain_effect = max(chain_effect,max(abs(J-b.Fs),[],'all'));
end
tc.verifyLessThanOrEqual(edh,tc.TestData.c.manifold_derivative_normalized);
tc.verifyLessThanOrEqual(echain,tc.TestData.c.chain_jacobian_normalized);
tc.verifyLessThanOrEqual(efull,tc.TestData.c.explicit_jacobian_normalized);
tc.verifyLessThanOrEqual(eimplicit,tc.TestData.c.manifold_derivative_normalized);
tc.verifyGreaterThan(chain_effect,1e-12);
fprintf('\nD7_DERIVATIVES %s\n',jsonencode(struct('max_dh_normalized_error',edh, ...
    'max_chain_J_normalized_error',echain,'max_explicit_J_normalized_error',efull, ...
    'max_implicit_dh_normalized_error',eimplicit,'max_chain_correction_abs',chain_effect, ...
    'random_states',size(tc.TestData.states,2),'complex_step',step)));
end

function test_frozen_slow_fast_relaxation(tc)
p = tc.TestData.p; q = tc.TestData.q; s = p.y0;
[h,~,info] = rs_qssa_manifold(s,p,q);
tau = 1/info.D; M0 = 0.5*q.E_T_ref; tgrid = (0:0.05:10)'*tau;
opts = odeset('RelTol',tc.TestData.c.RelTol,'AbsTol',tc.TestData.c.AbsTol, ...
    'Jacobian',-info.D);
[t,M] = ode15s(@(t,m) frozen_fast_rhs(t,m,s,p,q),tgrid,M0,opts);
expected = h+(M0-h)*exp(-info.D*t);
err = max(abs(M-expected))/q.E_T_ref;
[~,itau] = min(abs(t-tau));
measured_tau = -tau/log((M(itau)-h)/(M0-h));
tau_error = abs(measured_tau-tau)/tau;
tc.verifyEqual(t,tgrid); tc.verifyEqual(t(itau),tau,'RelTol',1e-14);
tc.verifyLessThanOrEqual(err,tc.TestData.c.fast_relaxation_normalized);
tc.verifyLessThanOrEqual(tau_error,tc.TestData.c.fast_relaxation_normalized);
fprintf('\nD7_FAST_RELAXATION %s\n',jsonencode(struct('max_normalized_error',err, ...
    'tau_M',tau,'measured_tau_M',measured_tau,'normalized_tau_error',tau_error, ...
    'M0',M0,'M_qss',h,'output_points',numel(t))));
end

function test_extended_stoichiometric_invariants(tc)
p = tc.TestData.p; q = tc.TestData.q;
[S,L] = independent_structure(p,true);
ls_error = max(abs(L*S),[],'all'); rhs_error = 0; i6_error = 0;
for k = 1:size(tc.TestData.states,2)
    s = tc.TestData.states(:,k); M = tc.TestData.occupancies(k);
    [dy,r,d] = rhs_pure_rs_explicit(0,[s;M],p,q);
    dx = [dy;r(2);r(5)];
    v = [r(1);r(2);d.v1_net;d.v2;r(4);r(5);r(6)];
    tc.verifyLessThanOrEqual(scaled_derivative_error(dx,S*v),1e-12);
    normalizer = max(1,abs(L)*abs(dx));
    rhs_error = max(rhs_error,max(abs(L*dx)./normalizer));
    i6_error = max(i6_error,abs(L(6,:)*dx));
end
tc.verifyLessThanOrEqual(ls_error,1e-14);
tc.verifyLessThanOrEqual(rhs_error,tc.TestData.c.invariant_max_normalized);
tc.verifyEqual(L(6,11),0); % I6 cancellation does not need an M term.
fprintf('\nD7_STRUCTURE %s\n',jsonencode(struct('max_abs_LS',ls_error, ...
    'max_normalized_derivative_residual',rhs_error,'I6_derivative_max_abs',i6_error, ...
    'invariant_names',{{'B_NTP','B_AA','B_tRNA','B_CP','B_TLcat','I6'}})));
end

function test_trajectory_DNA_low(tc), check_trajectory(tc,1); end
function test_trajectory_DNA_middle(tc), check_trajectory(tc,2); end
function test_trajectory_DNA_high(tc), check_trajectory(tc,3); end

function test_physicality_and_trajectory_invariants(tc)
for k = 1:3
    f = tc.TestData.full{k}; r = tc.TestData.reduced{k};
    [~,Lf] = independent_structure(f.p,true); [~,Lr] = independent_structure(r.p,false);
    bf = Lf*f.yfull(1,:)'; br = Lr*r.yfull(1,:)';
    allowance = 64*eps(max([1;abs(f.yfull(1,:)');abs(r.yfull(1,:)');abs(bf);abs(br)]));
    ef = invariant_error(f.yfull,Lf); er = invariant_error(r.yfull,Lr);
    physical_f = [f.yfull, f.q.E_T_ref-f.y(:,11)];
    h = zeros(numel(r.t),1);
    for j = 1:numel(r.t), h(j) = rs_qssa_manifold(r.y(j,:)',r.p,r.q); end
    physical_r = [r.yfull,h,r.q.E_T_ref-h];
    all_finite = all(isfinite([physical_f f.rates f.mRNA f.protein]),'all') && ...
        all(isfinite([physical_r r.rates r.mRNA r.protein]),'all');
    tc.verifyTrue(all_finite);
    tc.verifyGreaterThanOrEqual(min(physical_f,[],'all'),-allowance);
    tc.verifyGreaterThanOrEqual(min(physical_r,[],'all'),-allowance);
    tc.verifyLessThanOrEqual(ef.max_normalized,tc.TestData.c.invariant_max_normalized);
    tc.verifyLessThanOrEqual(er.max_normalized,tc.TestData.c.invariant_max_normalized);
    fprintf('\nD7_PHYSICALITY %s\n',jsonencode(struct('DNA_uM',f.p.DNA, ...
        'all_finite',all_finite,'full_min_per_quantity',min(physical_f,[],1), ...
        'reduced_min_per_quantity',min(physical_r,[],1), ...
        'full_negative_count_per_quantity',sum(physical_f<0,1), ...
        'reduced_negative_count_per_quantity',sum(physical_r<0,1), ...
        'roundoff_allowance_uM',allowance,'full_invariants',ef,'reduced_invariants',er, ...
        'full_max_normalized_invariant_residual',ef.max_normalized, ...
        'reduced_max_normalized_invariant_residual',er.max_normalized)));
end
end

function test_timescale_formulas_and_zero_derivatives(tc)
p = tc.TestData.p; q = tc.TestData.q; max_error = 0;
for k = 1:size(tc.TestData.states,2)
    s = tc.TestData.states(:,k); ds = rhs_pure_rs_qssa(0,s,p,q);
    d = rs_timescale_diagnostics(s,ds,p,q);
    D = q.kminus1+q.k2*(p.n_T/p.n_A)*s(5)+q.k1*s(4)*s(1);
    dh = zeros(1,10);
    dh(1) = q.E_T_ref*q.k1*s(4)*(q.kminus1+q.k2*(p.n_T/p.n_A)*s(5))/D^2;
    dh(4) = q.E_T_ref*q.k1*s(1)*(q.kminus1+q.k2*(p.n_T/p.n_A)*s(5))/D^2;
    dh(5) = -q.E_T_ref*q.k1*s(4)*s(1)*q.k2*(p.n_T/p.n_A)/D^2;
    tau = [p.y0(4);p.y0(1);p.y0(5)]./abs(ds([4 1 5]));
    track = dh*ds;
    expected = [1/D;min(tau);1/(D*min(tau));track;q.E_T_ref/abs(track);abs(track)/(D*q.E_T_ref)];
    actual = [d.tau_M;d.tau_slow_state;d.epsilon_state;d.dh_dt;d.tau_slow_track;d.epsilon_track];
    max_error = max(max_error,scaled_derivative_error(actual,expected));
end
dzero = rs_timescale_diagnostics(p.y0,zeros(10,1),p,q);
tc.verifyEqual([dzero.tau_slow_state dzero.tau_slow_track],[Inf Inf]);
tc.verifyEqual([dzero.epsilon_state dzero.epsilon_track dzero.dh_dt],[0 0 0]);
tc.verifyLessThanOrEqual(max_error,tc.TestData.c.manifold_derivative_normalized);
fprintf('\nD7_TIMESCALE_FORMULAS %s\n',jsonencode(struct('max_normalized_error',max_error, ...
    'zero_derivative_tau_is_Inf',true,'zero_derivative_epsilon_is_zero',true)));
end

function test_main_backbone_epsilon(tc)
for k = 1:3
    f = tc.TestData.full{k}; r = tc.TestData.reduced{k};
    sf = summarize_diagnostics(f.diagnostics); sr = summarize_diagnostics(r.diagnostics);
    tc.verifyLessThan(sf.max_epsilon_state,tc.TestData.c.epsilon_state_max_strict);
    tc.verifyLessThan(sr.max_epsilon_state,tc.TestData.c.epsilon_state_max_strict);
    tc.verifyTrue(all(isfinite([f.diagnostics.tau_M(:);r.diagnostics.tau_M(:); ...
        f.diagnostics.epsilon_state(:);r.diagnostics.epsilon_state(:); ...
        f.diagnostics.epsilon_track(:);r.diagnostics.epsilon_track(:)])));
    tc.verifyGreaterThan([f.diagnostics.tau_M(:);r.diagnostics.tau_M(:)],0);
    fprintf('\nD7_TIMESCALES %s\n',jsonencode(struct('DNA_uM',f.p.DNA, ...
        'full',sf,'reduced',sr,'epsilon_track_report_only',true)));
end
end

function check_trajectory(tc,k)
f = tc.TestData.full{k}; r = tc.TestData.reduced{k}; c = tc.TestData.c;
tc.assertEqual(f.t,r.t); tc.assertEqual(f.t,(0:c.OutputDt_s:c.Tfinal_s)');
tc.verifySize(f.y,[c.output_points_per_DNA 11]);
tc.verifySize(r.y,[c.output_points_per_DNA 10]);
tc.verifySize(f.yfull,[c.output_points_per_DNA 13]);
tc.verifySize(r.yfull,[c.output_points_per_DNA 12]);
tc.verifyEqual(f.y(1,1:10)',f.p.y0); tc.verifyEqual(r.y(1,:)',r.p.y0);
tc.verifyEqual(f.y(1,11),rs_qssa_manifold(f.p.y0,f.p,f.q),'AbsTol',1e-14);
tc.verifyEqual(f.p,r.p); tc.verifyEqual(f.q,r.q); tc.verifyEqual(f.opts,r.opts);
tc.verifyEqual(f.mRNA,f.y(:,3)/(3*f.p.L)); tc.verifyEqual(r.mRNA,r.y(:,3)/(3*r.p.L));
tc.verifyEqual(f.protein,f.y(:,7)/f.p.L); tc.verifyEqual(r.protein,r.y(:,7)/r.p.L);
m = struct('DNA_uM',f.p.DNA,'output_points',numel(f.t),'state_names',{f.p.state_names});
m.states = trajectory_error(r.y,f.y(:,1:10));
m.RS_flux = trajectory_error(r.rates(:,3),f.rates(:,3));
m.mRNA = trajectory_error(r.mRNA,f.mRNA); m.protein = trajectory_error(r.protein,f.protein);
h = zeros(numel(r.t),1);
for j = 1:numel(r.t), h(j) = rs_qssa_manifold(r.y(j,:)',r.p,r.q); end
m.supplemental_M = trajectory_error(h,f.y(:,11));
tc.verifyLessThanOrEqual(m.states.max_normalized,c.trajectory_max_normalized);
tc.verifyLessThanOrEqual(m.RS_flux.max_normalized,c.flux_max_normalized);
tc.verifyLessThanOrEqual(m.mRNA.max_normalized,c.mRNA_max_normalized);
tc.verifyLessThanOrEqual(m.protein.max_normalized,c.protein_max_normalized);
m.trajectory_pass = all([m.states.max_normalized m.RS_flux.max_normalized ...
    m.mRNA.max_normalized m.protein.max_normalized] <= c.trajectory_max_normalized);
fprintf('\nD7_CASE %s\n',jsonencode(m));
end

function dy = independent_rhs(r,v1,v2,p)
dy = [(-r(1)-2*r(4)-v1+r(6))/p.n_NTP;2*r(4)+v2-r(6);r(1)-r(2); ...
    -v1/p.n_A;(-v2+r(4))/p.n_T;(v2-r(4))/p.n_T;r(4);-r(6);r(6);-r(5);v1-v2];
end

function [S,L] = independent_structure(p,explicit)
% Columns: TX, nt degradation, RS activation, RS transfer, TL, TL decay, EN.
S = [-1/p.n_NTP 0 -1/p.n_NTP 0 -2/p.n_NTP 0 1/p.n_NTP; ...
    0 0 0 1 2 0 -1;1 -1 0 0 0 0 0;0 0 -1/p.n_A 0 0 0 0; ...
    0 0 0 -1/p.n_T 1/p.n_T 0 0;0 0 0 1/p.n_T -1/p.n_T 0 0; ...
    0 0 0 0 1 0 0;0 0 0 0 0 0 -1;0 0 0 0 0 0 1; ...
    0 0 0 0 0 -1 0;0 0 1 -1 0 0 0;0 1 0 0 0 0 0;0 0 0 0 0 1 0];
L = [p.n_NTP 1 1 0 0 0 0 0 0 0 1 1 0; ...
    0 0 0 p.n_A 0 p.n_T 1 0 0 0 1 0 0; ...
    0 0 0 0 p.n_T p.n_T 0 0 0 0 0 0 0; ...
    0 0 0 0 0 0 0 1 1 0 0 0 0;0 0 0 0 0 0 0 0 0 1 0 0 1; ...
    0 1 0 0 0 -p.n_T -3 0 1 0 0 0 0];
if ~explicit
    L(:,11) = []; S(11,:) = [];
end
end

function e = trajectory_error(reduced,reference)
e.scale = max(max(abs(reference),[],1),1e-12);
e.raw_max_abs_per_quantity = max(abs(reduced-reference),[],1);
e.normalized_per_quantity = e.raw_max_abs_per_quantity./e.scale;
e.max_raw_abs = max(e.raw_max_abs_per_quantity);
e.max_normalized = max(e.normalized_per_quantity);
end

function e = invariant_error(x,L)
b = x(1,:)*L'; residual = x*L'-b;
e.names = {'B_NTP','B_AA','B_tRNA','B_CP','B_TLcat','I6'};
e.initial = b; e.scale = max(1,abs(b));
e.raw_max_abs_per_invariant = max(abs(residual),[],1);
e.normalized_per_invariant = e.raw_max_abs_per_invariant./e.scale;
e.max_normalized = max(e.normalized_per_invariant);
e.max_raw_abs = max(e.raw_max_abs_per_invariant);
end

function J = complex_jacobian(fun,x,step)
base = fun(x); J = zeros(numel(base),numel(x));
for j = 1:numel(x)
    xc = x; xc(j) = xc(j)+1i*step;
    J(:,j) = imag(fun(xc))/step;
end
end

function e = scaled_derivative_error(actual,reference)
e = max(abs(actual-reference)./max(1,abs(reference)),[],'all');
end

function dM = frozen_fast_rhs(t,M,s,p,q)
dy = rhs_pure_rs_explicit(t,[s;M],p,q); dM = dy(11);
end

function s = summarize_diagnostics(d)
s.min_median_max_tau_M = [min(d.tau_M) median(d.tau_M) max(d.tau_M)];
s.min_median_max_tau_slow_state = [min(d.tau_slow_state) median(d.tau_slow_state) max(d.tau_slow_state)];
s.min_median_max_tau_slow_track = [min(d.tau_slow_track) median(d.tau_slow_track) max(d.tau_slow_track)];
s.max_epsilon_state = max(d.epsilon_state); s.max_epsilon_track = max(d.epsilon_track);
end

function export_trajectory(folder,k,f,r)
if ~isfolder(folder), mkdir(folder); end
full_explicit = f; qssa = r;
save(fullfile(folder,sprintf('dna_%d_trajectories.mat',k)),'full_explicit','qssa');
write_trajectory_csv(fullfile(folder,sprintf('dna_%d_full_explicit.csv',k)),f,true);
write_trajectory_csv(fullfile(folder,sprintf('dna_%d_qssa.csv',k)),r,false);
end

function write_trajectory_csv(path,out,explicit)
names = out.p.state_names(:)';
if explicit, names{end+1} = 'M'; end
names = [{'time_s'},names,{'D_nt','D_TLcat'},out.p.rate_names(:)',{'mRNA','protein'}];
tab = array2table([out.t out.yfull out.rates out.mRNA out.protein],'VariableNames',names);
fields = fieldnames(out.diagnostics);
for k = 1:numel(fields)
    tab.(['diag_' fields{k}]) = out.diagnostics.(fields{k})(:);
end
writetable(tab,path);
end
