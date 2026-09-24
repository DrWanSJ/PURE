function [h, dh, info] = rs_qssa_manifold(s, p, q)
%RS_QSSA_MANIFOLD Analytic fast-state manifold and complete slow gradient.
% S order: [NTP,NXP,nt,A,T,AT,a,CP,C,TLcat]. DH is a 1-by-10 row.
% h = E_T*alpha/(alpha+beta+gamma); QSSA sets dM/dt approximately zero,
% not M approximately zero. No clipping or state projection is used.
if nargin < 3
    q = rs_reduction_parameters(p);
end
fTA = p.n_T / p.n_A;
alpha = q.k1 * s(4) * s(1);
beta = q.kminus1;
gamma = q.k2 * fTA * s(5);
D = alpha + beta + gamma;
h = p.RScat * alpha / D;
dh = zeros(1, 10);
dh(1) = p.RScat * q.k1 * s(4) * (beta + gamma) / D^2;
dh(4) = p.RScat * q.k1 * s(1) * (beta + gamma) / D^2;
dh(5) = -p.RScat * alpha * q.k2 * fTA / D^2;
info = struct('D', D, 'tau_M', 1/D, 'alpha', alpha, ...
    'beta', beta, 'gamma', gamma, 'V_RS', gamma*h, 'fTA', fTA);
end
