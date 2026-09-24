function [dy, rates, detail] = rhs_pure_rs_explicit(t, y, p, q)
%RHS_PURE_RS_EXPLICIT D7 two-step RS surrogate in the actual PURE backbone.
% Y = canonical ten physical states followed by M = RScat.A-AMP.
% ATP_RS := NTP is a coarse bookkeeping mapping; PPi is not a state.
% kminus1 is apparent pseudo-first-order with PPi effects lumped into it.
% All non-RS rates are obtained from the frozen canonical implementation.
% Returned rate slot 3 is transfer v2; canonical V_RS is diagnostic only.
if nargin < 4
    q = rs_reduction_parameters(p);
end
[~, rates] = rhs_pure_literature_reference(t, y(1:10), p);
canonical_V_RS = rates(3);
M = y(11);
fTA = p.n_T / p.n_A;
v1_f = q.k1 * y(4) * y(1) * (p.RScat - M);
v1_r = q.kminus1 * M;
v1_net = v1_f - v1_r;
v2 = q.k2 * M * fTA * y(5);
rates(3) = v2;
V_TX = rates(1);
V_nt_deg = rates(2);
V_TL = rates(4);
V_TL_deg = rates(5);
V_EN = rates(6);
dy = [(-V_TX - 2*V_TL - v1_net + V_EN)/p.n_NTP; ...
    2*V_TL + v2 - V_EN; ...
    V_TX - V_nt_deg; ...
    -v1_net/p.n_A; ...
    (-v2 + V_TL)/p.n_T; ...
    (v2 - V_TL)/p.n_T; ...
    V_TL; -V_EN; V_EN; -V_TL_deg; v1_net - v2];
detail = struct('v1_f', v1_f, 'v1_r', v1_r, 'v1_net', v1_net, ...
    'v2', v2, 'canonical_V_RS', canonical_V_RS);
end
