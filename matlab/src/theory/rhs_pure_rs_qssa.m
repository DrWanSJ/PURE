function [ds, rates, detail] = rhs_pure_rs_qssa(t, s, p, q)
%RHS_PURE_RS_QSSA Restrict the D7 explicit extension to M = h(s).
% This is the minimal explicit surrogate's QSSA law, not an identity with
% canonical Mavelli Eq. (8). The non-RS backbone is reused without alteration.
if nargin < 4
    q = rs_reduction_parameters(p);
end
[h, ~, manifold] = rs_qssa_manifold(s, p, q);
[dy, rates, detail] = rhs_pure_rs_explicit(t, [s(:); h], p, q);
ds = dy(1:10);
detail.M_qss = h;
detail.manifold = manifold;
detail.fast_residual = dy(11);
end
