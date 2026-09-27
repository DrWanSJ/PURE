function g = a3b_closure_resid(C, t, y, q, params)
%A3B_CLOSURE_RESID  A3b algebraic closure G(y, q) = Q f(R(y, q)).
%
% The rows are the AUTHOR RHS rows of the eliminated complexes evaluated at
% the reconstructed state (the same registered closure equations as the A3a
% candidate; only the slow coordinates differ).  No clipping, no
% projection: the residual is the raw author field.

x = a3b_reconstruct(C, y, q);
dx = fMGG_synthesis(t, x, params);
g = dx(C.elimIdx);
end
