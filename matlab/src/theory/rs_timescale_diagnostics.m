function d = rs_timescale_diagnostics(s, ds, p, q)
%RS_TIMESCALE_DIAGNOSTICS Fixed-scale and moving-manifold D7 diagnostics.
% S and DS are single columns of ten slow physical states and derivatives.
% Concentration scales are fixed at the synthetic construction reference.
% A zero derivative gives Inf timescale and zero contribution to epsilon.
% Epsilon gates describe this synthetic profile, not a universal theorem.
if nargin < 4
    q = rs_reduction_parameters(p);
end
[~, dh, info] = rs_qssa_manifold(s, p, q);
d = struct();
d.tau_M = info.tau_M;
d.tau_A = q.A_scale/abs(ds(4));
d.tau_NTP = q.NTP_scale/abs(ds(1));
d.tau_T = q.T_scale/abs(ds(5));
d.tau_slow_state = min([d.tau_A, d.tau_NTP, d.tau_T]);
d.epsilon_state = d.tau_M/d.tau_slow_state;
d.dh_dt = dh*ds(:);
d.tau_slow_track = q.M_scale/abs(d.dh_dt);
d.epsilon_track = d.tau_M/d.tau_slow_track;
end
