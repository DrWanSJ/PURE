function ref = analytic_reversible_conversion(t, p)
%ANALYTIC_REVERSIBLE_CONVERSION Independent analytic solution for the B0 fixture.
%
%   The reference is derived analytically and does not call the numerical RHS.

t = t(:);
M0 = p.A0 + p.B0;
lambda = p.k_f + p.k_r;

A_eq = p.k_r / lambda * M0;
B_eq = p.k_f / lambda * M0;

A = A_eq + (p.A0 - A_eq) .* exp(-lambda .* t);
B = M0 - A;

ref = struct();
ref.t = t;
ref.A = A;
ref.B = B;
ref.M0 = M0;
ref.lambda = lambda;
ref.A_eq = A_eq;
ref.B_eq = B_eq;
ref.forward_eq = p.k_f * A_eq;
ref.reverse_eq = p.k_r * B_eq;
end
