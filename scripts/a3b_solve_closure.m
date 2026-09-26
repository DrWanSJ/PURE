function [q, res, nit, info] = a3b_solve_closure(C, t, y, q0, params, refscale, Jcache)
%A3B_SOLVE_CLOSURE  Damped projected Newton on the 21 A3b closure rows
%0 = G(y, q) (author RHS rows of the eliminated complexes at R(y, q)).
%
% Registered discipline (same class as the v1r1/v1r2 block solver):
%   - one-sided FD columns, step 1e-7*(|q_j| + 1e-10) (the registered
%     trajectory-solver convention; the initializer uses central columns),
%     cached Jacobian (pass Jcache = [] to start without one; the returned
%     cache can be reused for warm starts);
%   - feasibility line search: a step is accepted only if max|G| decreases
%     and every component stays >= -1e-14 (NO clipping anywhere);
%   - Jacobian refresh once on slow progress (rn > 0.1 * res);
%   - convergence target 1e-12 * refscale; the plateau branch accepts a
%     double-precision floor only if it is within the registered 1e-10
%     scaled acceptance, otherwise the run terminates fail-closed;
%   - max 12 iterations.
%
% info = [ls_rejections, jacobian_refreshes, plateau_accepts, min_q].
% refscale is the FIXED production scale of the closure rows (seeded once
% at the author initial state); the scaled residual res/refscale is the
% registered QSSA quantity.

if nargin < 7
    Jcache = struct('J', [], 'hasJ', false);
end
q = q0(:);
g = a3b_closure_resid(C, t, y, q, params);
res = max(abs(g));
tol = 1e-12 * refscale;
nit = 0;
ls_rej = 0; jref = 0; plateau = 0;
info = [0, 0, 0, min(q)];
if res <= tol
    return
end
refreshed = false;
for it = 1:12
    nit = it;
    if ~Jcache.hasJ
        n = numel(q);
        J = zeros(n);
        for j = 1:n
            h = 1e-7 * (abs(q(j)) + 1e-10);
            qp = q;
            qp(j) = qp(j) + h;
            J(:, j) = (a3b_closure_resid(C, t, y, qp, params) - g) / h;
        end
        Jcache.J = J;
        Jcache.hasJ = true;
    end
    d = -Jcache.J \ g;
    alpha = 1.0;
    accepted = false;
    qn = q;
    while alpha >= 1e-8
        qn = q + alpha * d;
        gn = a3b_closure_resid(C, t, y, qn, params);
        rn = max(abs(gn));
        if rn < res && all(qn >= -1e-14)
            accepted = true;
            break
        end
        alpha = alpha * 0.5;
        ls_rej = ls_rej + 1;
    end
    if ~accepted
        if Jcache.hasJ && ~refreshed
            Jcache.hasJ = false;      % retry once with a fresh Jacobian
            refreshed = true;
            jref = jref + 1;
            continue
        end
        % plateau at the double-precision floor of the author RHS: converged
        % only if within the registered scaled acceptance, else fail-closed
        if res <= 1e-10 * refscale
            plateau = plateau + 1;
            break
        end
        error(['a3b closure root failure at t=%.3e: res = %.3e (scaled %.3e), ' ...
               'min q = %.3e (no feasible improving step above registered acceptance)'], ...
            t, res, res / max(refscale, 1e-300), min(q));
    end
    if rn > 0.1 * res
        Jcache.hasJ = false;          % slow progress -> refresh J
        jref = jref + 1;
    end
    q = qn;
    g = gn;
    res = rn;
    if res <= tol
        break
    end
end
info = [ls_rej, jref, plateau, min(q)];
end
