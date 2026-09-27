function [q0, res, gscale, info] = a3b_init_closure(C, t0, y0, params, poolInfo)
%A3B_INIT_CLOSURE  Consistent initial closure solve for the A3b candidate
%(Phase 10): joint 21-dim damped projected Newton on 0 = G(y0, q) with
%multi-start (all-zero, uniform-half-capacity, uniform-5%-capacity), the
%registered start-agreement discipline, and per-pool capacity feasibility.
%
%Because the slow coordinates are the ledger TOTALS, y0 = A x0_full already
%carries the exact author physical inventory (all author complexes are zero
%at t0, so every reconstructed carrier equals its author value at q = 0);
%the closure solve at the consistent q0 then debits the free carriers by the
%complexes' sequestered content automatically -- no debit matrix is needed
%(this is the structural difference from the v1r2 initialization map).
%
%poolInfo: struct with fields .pool (cell, {'MetRS','GlyRS'}), .E (cell of
%eliminated indices per pool), .K (cell of kept complex indices per pool),
%.ePool (2x1 conserved enzyme totals), used only for the capacity
%projection and the start-agreement scale.
%
%info: struct('iters', 'starts_ok', 'spread', 'residuals', 'per_start_q')

pools = poolInfo.pool;
nP = numel(pools);
nq = numel(C.elimIdx);
% per-pool eliminated positions inside the joint unknown vector
pos = cell(nP, 1);
for p = 1:nP
    pos{p} = find(ismember(C.elimIdx, poolInfo.E{p}));
end
cap = zeros(nP, 1);
for p = 1:nP
    % y positions of the kept complexes of this pool (kept complexes are
    % identity-row coordinates; keepIdx is in species space)
    kpos = find(ismember(C.keepIdx, poolInfo.K{p}));
    assert(numel(kpos) == numel(poolInfo.K{p}), 'kept complex not a coordinate');
    cap(p) = poolInfo.ePool(p) - sum(y0(kpos));
end

g0 = a3b_closure_resid(C, t0, y0, zeros(nq, 1), params);
gscale = max(abs(g0));
assert(isfinite(gscale) && gscale > 0, 'closure production scale degenerate');
tol = 1e-10 * gscale;

starts = cell(3, 1);
starts{1} = zeros(nq, 1);
starts{2} = zeros(nq, 1);
starts{3} = zeros(nq, 1);
for p = 1:nP
    starts{2}(pos{p}) = 0.5 * cap(p) / numel(pos{p});
    starts{3}(pos{p}) = 0.05 * cap(p) / numel(pos{p});
end

sols = struct('q', {}, 'res', {}, 'feas', {}, 'conv', {}, 'iters', {});
for s = 1:3
    q = starts{s};
    g = a3b_closure_resid(C, t0, y0, q, params);
    converged = false;
    iters = 0;
    Jok = false; J = [];
    for it = 1:300
        iters = it;
        if ~Jok
            J = zeros(nq);
            for j = 1:nq
                h = 1e-7 * (abs(q(j)) + 1e-10);
                qp = q; qm = q;
                qp(j) = qp(j) + h; qm(j) = qm(j) - h;
                J(:, j) = (a3b_closure_resid(C, t0, y0, qp, params) - ...
                           a3b_closure_resid(C, t0, y0, qm, params)) / (2 * h);
            end
            Jok = true;
        end
        if rcond(J) < 1e-14
            break
        end
        d = -J \ g;
        alpha = 1.0;
        accepted = false;
        while alpha > 1e-12
            trial = max(q + alpha * d, 0);
            % projected per-pool capacity feasibility
            for p = 1:nP
                ss = sum(trial(pos{p}));
                if ss > cap(p) * (1 + 1e-9)
                    trial(pos{p}) = trial(pos{p}) * (cap(p) * (1 + 1e-9) / ss);
                end
            end
            gt = a3b_closure_resid(C, t0, y0, trial, params);
            if max(abs(gt)) < max(abs(g))
                accepted = true;
                break
            end
            alpha = alpha * 0.5;
        end
        if ~accepted
            break
        end
        q = trial;
        g = gt;
        if max(abs(g)) <= tol
            converged = true;
            break
        end
    end
    res = max(abs(g));
    feas = all(q >= -1e-15);
    for p = 1:nP
        feas = feas && sum(q(pos{p})) <= cap(p) * (1 + 1e-9);
    end
    sols(end+1) = struct('q', {q}, 'res', res, 'feas', feas, ...
        'conv', converged, 'iters', iters); %#ok<AGROW>
end

ok = sols([sols.feas] & [sols.conv]);
assert(~isempty(ok), ...
    ['a3b_init_closure: no start converged feasibly (residuals %s). ' ...
     'Refusing to proceed.'], ...
    sprintf('%.3e ', [sols.res]));
if numel(ok) >= 2
    spread = 0;
    for a = 1:numel(ok)
        for b = a+1:numel(ok)
            spread = max(spread, max(abs(ok(a).q - ok(b).q)));
        end
    end
    assert(spread <= 1e-6 * max(poolInfo.ePool), ...
        ['a3b_init_closure: starts disagree (spread %.2e uM). ' ...
         'Refusing to proceed.'], spread);
end
if sols(1).feas && sols(1).conv
    cs = sols(1);
else
    [~, kk] = min([ok.res]);
    cs = ok(kk);
end
q0 = cs.q;
res = cs.res;
info = struct('iters', cs.iters, 'starts_ok', numel(ok), ...
    'spread', spread_if_any(ok), 'residuals', [sols.res], ...
    'per_start_q', {[sols.q]});
end

function s = spread_if_any(ok)
    s = 0;
    if numel(ok) >= 2
        for a = 1:numel(ok)
            for b = a+1:numel(ok)
                s = max(s, max(abs(ok(a).q - ok(b).q)));
            end
        end
    end
end
