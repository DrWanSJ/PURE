function r = a3b_rhs(t, y, C, params, NC, used_rows, A, seed, statsH, refscale)
%A3B_RHS  Reduced A3b RHS: solve the closure at (t, y) from the fixed seed,
%then evaluate the reduced flow dy/dt = A f(R(y, q)) plus the cumulative
%rows.  Identity rows take the author RHS; ledger rows take the DIRECT
%weighted author-row sum over the row members (the literal Phase-2
%transformed equation, author-faithful; see run_pnas2017_aa_a3b_formal).
%The closure solve warm-starts from the FIXED seed (passed by value) so
%that odefun(t, y) is a deterministic function of (t, y), as ode15s
%requires; only the stats handle accumulates and never feeds back into r.

cache = seed;
st = statsH('s');
[q, res, nit, info] = a3b_solve_closure(C, t, y, seed.q, params, refscale, cache);
st.calls = st.calls + 1;
st.iters = st.iters + nit;
st.iters_all(end+1) = nit; %#ok<AGROW>
st.ls_rejections = st.ls_rejections + info(1);
st.jacobian_refreshes = st.jacobian_refreshes + info(2);
st.plateau_accepts = st.plateau_accepts + info(3);
st.min_q = min(st.min_q, info(4));
st.max_res = max(st.max_res, res);
st.max_res_scaled = max(st.max_res_scaled, res / max(refscale, 1e-300));
if res > 1e-10 * refscale
    error(['a3b closure-lost at t=%.3e: max|G| = %.3e (scaled %.3e ' ...
           '> registered 1e-10)'], t, res, res / max(refscale, 1e-300));
end
x = a3b_reconstruct(C, y, q);
dx = fMGG_synthesis(t, x, params);
v = pnas2017_aa_v1_rates(x, params);
Ny = C.Ny;
r = zeros(Ny + NC, 1);
r(C.keepPos) = dx(C.keepIdx);
% ledger rows: dy_k = (w^T S) v -- the exact per-reaction ledger balances
% evaluated on the monomial rate vector.  This form is cancellation-free:
% for the five exact rows (enzyme x2, tRNA x2, phosphate) (w^T S) is zero
% on every active reaction and its remaining entries multiply rates that
% are identically zero (k1 = 0), so the reduced dynamics of those
% coordinates is EXACTLY zero and the solver never integrates noise (the
% direct weighted author-row sum carries ~1e-9 of cancellation noise from
% author rows of size ~1e6, which is above the error-test tolerance of the
% small enzyme-total rows and made ode15s take ~1e5 steps/decade).  For the
% interface rows (adenine, Met/Gly material) (w^T S) v reproduces the
% retained interface fluxes exactly.  B6 of the pre-QSSA verification
% documents the agreement of the two forms to the double-precision
% cancellation limit of these rows (worst 5.7e-9 relative to the
% cancellation scale over the reference trajectory).
for k = 1:C.nLedger
    L = C.ledger(k);
    r(L.pos) = L.dotS.vals' * v(L.dotS.ridx);
end
if NC > 0
    r(Ny+1:Ny+NC) = (A(:, used_rows) * v(used_rows))';
end
statsH('s') = st;   %#ok<NASGU> % handle accumulation; does not affect r
end
