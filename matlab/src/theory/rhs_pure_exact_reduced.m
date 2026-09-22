function [dz, rates] = rhs_pure_exact_reduced(t, z, p, b)
%RHS_PURE_EXACT_REDUCED Restrict the canonical RHS to six exact coordinates.
% No rate law is reimplemented here. Accounting states never feed into rates.
if nargin < 4
    b = pure_exact_conservation_constants(p);
end
xfull = reconstruct_pure_exact_reduced_state(z, p, b);
[dx, rates] = rhs_pure_literature_reference(t, xfull(1:10), p);
dz = dx([1 3 4 6 8 10]);
end
