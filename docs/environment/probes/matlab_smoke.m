function matlab_smoke(kind)
% Minimal environment probes only; no project model/parameter writes.
fprintf('SMOKE_START=%s\n', kind);
switch kind
    case 'base'
        [t, y] = ode15s(@(~, y) -y, [0 1], 1, ...
            odeset('RelTol', 1e-8, 'AbsTol', 1e-10));
        assert(t(end) == 1 && all(isfinite(y(:))));
        assert(abs(y(end) - exp(-1)) < 1e-6);
        fprintf('ode15s: PASS; final=%.17g; expected=%.17g\n', y(end), exp(-1));
        j = jsondecode('{"answer":42}');
        assert(j.answer == 42);
        fprintf('jsondecode: PASS\n');
        f = fullfile(getenv('PURE_AUDIT_SCRATCH'), 'base_writetable.csv');
        writetable(table([1; 2], [3; 4], 'VariableNames', {'a', 'b'}), f);
        r = readtable(f);
        assert(isequal(r.a, [1; 2]) && isequal(r.b, [3; 4]));
        fprintf('writetable/readback: PASS\n');
    case 'symbolic'
        syms x
        residual = simplify(diff(x^2, x) - 2*x);
        assert(isequal(residual, sym(0)));
        fprintf('symbolic residual=%s\n', char(residual));
    case 'optimization'
        options = optimoptions('lsqnonlin', 'Display', 'off');
        [x, resnorm, ~, flag] = lsqnonlin(@(x) x - 2, 0, [], [], options);
        assert(flag > 0 && abs(x - 2) < 1e-6 && resnorm < 1e-12);
        fprintf('lsqnonlin: x=%.17g; resnorm=%.17g; optimizer_exitflag=%d\n', x, resnorm, flag);
    case 'simbiology'
        m = sbiomodel('CZ_environment_probe');
        c = addcompartment(m, 'cell', 1);
        s = addspecies(c, 'X', 'InitialAmount', 1);
        assert(isa(m, 'SimBiology.Model') && numel(m.Compartments) == 1);
        assert(s.InitialAmount == 1);
        fprintf('sbiomodel: PASS; class=%s; compartments=%d; species=%d\n', ...
            class(m), numel(m.Compartments), numel(m.Species));
    otherwise
        error('CZEnvironment:UnknownProbe', 'Unknown probe: %s', kind);
end
% Feature names actually checked out; deliberately omit usernames/licenses.
used = license('inuse');
for i = 1:numel(used)
    fprintf('LICENSE_INUSE_FEATURE=%s\n', used(i).feature);
end
fprintf('SMOKE_PASS=%s\n', kind);
end
