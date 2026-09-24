function [J, blocks] = jacobian_pure_rs_explicit(~, y, p, q)
%JACOBIAN_PURE_RS_EXPLICIT Analytic 11-by-11 Jacobian for the explicit model.
if nargin < 4
    q = rs_reduction_parameters(p);
end
blocks = rs_explicit_jacobian_blocks(y(1:10), y(11), p, q);
J = [blocks.Fs, blocks.FM; blocks.Gs, blocks.GM];
end
