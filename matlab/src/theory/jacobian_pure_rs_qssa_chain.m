function [J, blocks] = jacobian_pure_rs_qssa_chain(~, s, p, q)
%JACOBIAN_PURE_RS_QSSA_CHAIN Complete reduced Jacobian by analytic chain rule.
% G(s,h(s))=0 implies dh/ds=-G_M\G_s. For ds/dt=F(s,h(s)):
% J = F_s + F_M*dh/ds = F_s - F_M*(G_M\G_s).
% The explicit analytic h gradient supplies every chain-rule correction.
% This is not obtained by deleting the fast-state row and column.
if nargin < 4
    q = rs_reduction_parameters(p);
end
[h, dh] = rs_qssa_manifold(s, p, q);
blocks = rs_explicit_jacobian_blocks(s, h, p, q);
blocks.dh = dh;
blocks.dh_implicit = -blocks.Gs/blocks.GM;
J = blocks.Fs + blocks.FM*dh;
end
