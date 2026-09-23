function y = reconstruct_pure_exact_reduced_nondim_state(q, m, I)
%RECONSTRUCT_PURE_EXACT_REDUCED_NONDIM_STATE Direct affine reconstruction.
% q=[y1;y3;y4;y6;y8;y10]; I=[I_NTP;I_AA;I_tRNA;I_CP;I_TLcat;I6].
% Operates only in dimensionless variables; no clipping or state repair.
if nargin < 3
    I = pure_dimensionless_invariants(m.initial_dimensionless,m);
end
assert(isvector(q) && numel(q)==6,'pure_nondim:badState','q must have six coordinates.');
g = m.groups;
y1 = q(1); y3 = q(2); y4 = q(3); y6 = q(4); y8 = q(5); y10 = q(6);
y5 = I(3)-y6;
y7 = g.rho_A*I(2)-y4-(g.rho_A/g.rho_T)*y6;
y9 = I(4)-y8;
y2 = I(6)-y9/g.rho_C+3*y7/g.rho_A+y6/g.rho_T;
y12 = I(5)-y10;
y11 = I(1)-y1-y2-y3;
y = [y1;y2;y3;y4;y5;y6;y7;y8;y9;y10;y11;y12];
end
