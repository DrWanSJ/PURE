% NEG-ROOT and NEG-PARTITION software controls (Phase 13)
addpath('C:\Users\sean\Desktop\GUV-PURE\scripts');
model_dir = 'C:\Users\sean\Desktop\GUV-PURE\models\pnas2017_full_reference\original\simulate\Simulate_fMGG_synthesis';
addpath(model_dir);
names = reshape(fMGG_synthesis('states'), 1, []);
pt = readtable(fullfile(model_dir, 'dat', 'fMGG_synthesis_parameters.csv'));
params = pt.Value;
C = a3b_build_coords(names, 'C:/Users/sean/Desktop/GUV-PURE/docs/audit/pnas2017_aminoacylation_A3b_r12');
it = readtable(fullfile(model_dir, 'dat', 'fMGG_synthesis_initial_values.csv'));
x0 = it.Value;

% ---- NEG-ROOT: infeasible closure test state (enzyme pool drained to zero
% while the closure must populate complexes) must fail closed.
y0 = zeros(C.Ny, 1);
y0(C.keepPos) = x0(C.keepIdx);
for k = 1:C.nLedger
    L = C.ledger(k);
    y0(L.pos) = sum(L.weights .* x0(L.members));
end
bad = y0;
mt = find(strcmp({C.ledger.name}, 'MetRS_total'), 1);
bad(C.ledger(mt).pos) = 0;    % infeasible: MetRS_total = 0 but kept complexes nonzero
gscale = 1.65e4;
try
    seed = struct('q', zeros(numel(C.elimIdx),1), 'J', [], 'hasJ', false);
    [q, res] = a3b_solve_closure(C, 1e-4, bad, seed.q, params, gscale, seed);
    fprintf('NEG-ROOT: FAIL (closure returned res=%.3e without refusing)\n', res);
catch e
    fprintf('NEG-ROOT: PASS (fail-closed): %s\n', regexprep(e.message, '\s+', ' '));
end

% ---- NEG-PARTITION: the eligibility checker must reject a partition that
% eliminates a KEEP_EXPLICIT_PROTECTED_LEDGER state.
ej = jsondecode(fileread('C:/Users/sean/Desktop/GUV-PURE/docs/audit/pnas2017_aminoacylation_A3c/a3c_eligibility.json'));
illegal = 'MetRS_tRNAfMetCAU';   % tRNA-carrying: KEEP_EXPLICIT_PROTECTED_LEDGER
st = ej.states;
idxi = find(strcmp({st.state}, illegal), 1);
cls = st(idxi).classification;
blocked = st(idxi).blocking_rows;
if strcmp(cls, 'KEEP_EXPLICIT_PROTECTED_LEDGER') && ~isempty(blocked)
    fprintf('NEG-PARTITION: PASS (illegal elimination of %s rejected; blocking rows: %s)\n', ...
        illegal, strjoin(blocked, ', '));
else
    fprintf('NEG-PARTITION: FAIL (%s classified %s)\n', illegal, cls);
end
