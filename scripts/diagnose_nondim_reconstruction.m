function result = diagnose_nondim_reconstruction(outputPath, symbolicOnly)
%DIAGNOSE_NONDIM_RECONSTRUCTION Fixed-sample comparison, no production edits.
% SymbolicOnly proves all six centered identities without numerical runs.
if nargin<1, outputPath = ''; end
if nargin<2, symbolicOnly = false; end
root = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(root,'matlab','generated'),fullfile(root,'matlab','src','theory'), ...
    fullfile(root,'matlab','src','provenance'));
result.symbolic = prove_centered();
assert(result.symbolic.all_passed,'Centered reconstruction is not equivalent.');
if symbolicOnly, return; end
criteriaPath = fullfile(root,'docs','audit','nondimensionalization_validation_20260923','acceptance_criteria.json');
c = jsondecode(fileread(criteriaPath));
result.source_commit = pure_git_state(root).commit;
result.criteria_sha256 = pure_sha256_file(criteriaPath);
result.selection = 'Original invariant-form trajectory; fixed 17 uniformly indexed points per DNA';
idx = [1 3 4 6 8 10]; dep = [2 5 7 9 11 12];
for k = 1:numel(c.DNA_uM)
    n = simulate_pure_exact_reduced_nondim(c.DNA_uM(k), ...
        'Tfinal',c.Tfinal_s,'OutputDt',c.OutputDt_s,'RelTol',c.RelTol, ...
        'AbsTol',c.AbsTol_dimensional_uM);
    m = n.map; s = m.state_scales(idx); b = pure_exact_conservation_constants(n.p);
    samples = unique(round(linspace(1,numel(n.t_s),c.derivative_samples_per_DNA)));
    e = struct('DNA_uM',c.DNA_uM(k),'dependent_indices',dep,'sample_indices',samples);
    for j = 1:numel(samples)
        i = samples(j); q = n.q(i,:)';
        yo = reconstruct_pure_exact_reduced_nondim_state(q,m,n.invariants);
        yc = centered(q,m);
        xd = reconstruct_pure_exact_reduced_state(s.*q,n.p,b); yd = xd./m.state_scales;
        oldDQ = rhs_pure_exact_reduced_nondim(n.tau(i),q,m,n.invariants);
        fullOld = rhs_pure_literature_dimensionless(n.tau(i),yo,m.groups);
        assert(isequal(oldDQ,fullOld(idx)),'Diagnostic compact RHS must match production arithmetic.');
        fullCentered = rhs_pure_literature_dimensionless(n.tau(i),yc,m.groups);
        dimDQ = rhs_pure_exact_reduced(n.t_s(i),s.*q,n.p,b)./s/m.k_nt_deg;
        e.samples(j) = struct('index',i,'t_s',n.t_s(i),'q',q', ...
            'old_full_dimensionless',yo','centered_full_dimensionless',yc', ...
            'dimensional_reconstruction_scaled',yd', ...
            'old_dependent_difference',(yo(dep)-yd(dep))', ...
            'centered_dependent_difference',(yc(dep)-yd(dep))', ...
            'old_NXP_difference_uM',m.state_scales(2)*yo(2)-xd(2), ...
            'centered_NXP_difference_uM',m.state_scales(2)*yc(2)-xd(2), ...
            'old_derivative_max',max(abs(oldDQ-dimDQ)), ...
            'centered_derivative_max',max(abs(fullCentered(idx)-dimDQ)));
    end
    e.old_derivative_max = max([e.samples.old_derivative_max]);
    e.centered_derivative_max = max([e.samples.centered_derivative_max]);
    e.old_NXP_max_difference_uM = max(abs([e.samples.old_NXP_difference_uM]));
    e.centered_NXP_max_difference_uM = max(abs([e.samples.centered_NXP_difference_uM]));
    e.centered_original_gate_pass = e.centered_derivative_max<=c.derivative_max_abs;
    result.cases(k) = e;
    fprintf('DNA %.5g old %.17g centered %.17g; NXP old %.17g centered %.17g\n', ...
        e.DNA_uM,e.old_derivative_max,e.centered_derivative_max, ...
        e.old_NXP_max_difference_uM,e.centered_NXP_max_difference_uM);
end
result.old_derivative_max = max([result.cases.old_derivative_max]);
result.centered_derivative_max = max([result.cases.centered_derivative_max]);
result.old_NXP_max_difference_uM = max([result.cases.old_NXP_max_difference_uM]);
result.centered_NXP_max_difference_uM = max([result.cases.centered_NXP_max_difference_uM]);
result.centered_original_gate_pass = all([result.cases.centered_original_gate_pass]);
if ~isempty(outputPath)
    assert(~isfile(outputPath),'Do not overwrite diagnostic evidence.');
    fid = fopen(outputPath,'w','n','UTF-8'); assert(fid>=0);
    closeFile = onCleanup(@() fclose(fid));
    fprintf(fid,'%s\n',jsonencode(result,'PrettyPrint',true));
end
end

function y = centered(q,m)
% Temporary diagnostic only; independent of the production reconstruction.
y0 = m.initial_dimensionless; g = m.groups;
y1=q(1); y3=q(2); y4=q(3); y6=q(4); y8=q(5); y10=q(6);
y5 = y0(5)-(y6-y0(6));
y7 = y0(7)-(y4-y0(4))-(g.rho_A/g.rho_T)*(y6-y0(6));
y9 = y0(9)-(y8-y0(8));
y2 = y0(2)+(y8-y0(8))/g.rho_C-3*(y4-y0(4))/g.rho_A-2*(y6-y0(6))/g.rho_T;
y12 = y0(12)-(y10-y0(10));
y11 = y0(11)-(y1-y0(1))-(y2-y0(2))-(y3-y0(3));
y = [y1;y2;y3;y4;y5;y6;y7;y8;y9;y10;y11;y12];
end

function out = prove_centered()
q = sym('q',[6 1],'real'); y0 = sym('y0',[12 1],'real');
syms rho_A rho_T rho_C positive
m.groups = struct('rho_A',rho_A,'rho_T',rho_T,'rho_C',rho_C);
m.initial_dimensionless = y0;
I = pure_dimensionless_invariants(y0,m);
old = reconstruct_pure_exact_reduced_nondim_state(q,m,I);
new = centered(q,m); dep = [2 5 7 9 11 12];
residual = simplify(old(dep)-new(dep));
out.dependent_indices = dep;
out.residuals = arrayfun(@(x) char(x),residual,'UniformOutput',false);
out.all_passed = all(isAlways(residual==0));
syms NXP0 CP CP0 A A0 AT AT0 a0 C0 n_A n_T real
a = n_A*A0+a0+n_T*AT0-n_A*A-n_T*AT;
C = CP0+C0-CP;
I6 = NXP0+C0-3*a0-n_T*AT0;
dimensionalResidual = simplify(I6-C+3*a+n_T*AT ...
    -(NXP0+(CP-CP0)-3*n_A*(A-A0)-2*n_T*(AT-AT0)));
out.dimensional_NXP_residual = char(dimensionalResidual);
out.all_passed = out.all_passed && isAlways(dimensionalResidual==0);
end
