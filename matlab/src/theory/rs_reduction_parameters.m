function q = rs_reduction_parameters(p)
%RS_REDUCTION_PARAMETERS Reproducible synthetic D7 micro-parameter construction.
% This is local reference-state matching, not fitting or literature kinetics.
% The one-intermediate surrogate is not algebraically Mavelli Eq. (8).
% P is the frozen canonical parameter struct with a specified P.DNA.
% Units: concentrations uM; time seconds; k1 uM^-2/s, kminus1 1/s,
% k2 uM^-1/s. ATP_RS maps to canonical NTP for backbone bookkeeping.
if ~isfield(p, 'DNA')
    error('pure_rs:MissingDNA', 'Specify p.DNA before constructing D7 parameters.');
end
q = struct();
q.source_type = 'synthetic_reduction_only';
q.evidence_level = 'derived + synthetic numerical validation; NOT experimentally supported';
q.construction_method = 'local_reference_state_matching_fixed_rate_fractions';
q.phi_alpha = 0.05;
q.phi_beta = 0.90;
q.phi_gamma = 0.05;
q.reference_state = p.y0(:);
q.reference_DNA = p.DNA;
q.fTA_ref = p.n_T / p.n_A;
q.E_T_ref = p.RScat;
q.A_scale = p.y0(4);
q.NTP_scale = p.y0(1);
q.T_scale = p.y0(5);
q.M_scale = p.RScat;
q.T_eff_ref = q.fTA_ref * q.T_scale;
[~, canonical_rates] = rhs_pure_literature_reference(0, q.reference_state, p);
q.V_RS_ref = canonical_rates(3);
q.D_ref = q.V_RS_ref / (p.RScat * q.phi_alpha * q.phi_gamma);
q.alpha_ref = q.phi_alpha * q.D_ref;
q.beta_ref = q.phi_beta * q.D_ref;
q.gamma_ref = q.phi_gamma * q.D_ref;
q.k1 = q.alpha_ref / (q.A_scale * q.NTP_scale);
q.kminus1 = q.beta_ref;
q.k2 = q.gamma_ref / q.T_eff_ref;
q.M_qss_ref = p.RScat * q.phi_alpha;
q.tau_M_ref = 1 / q.D_ref;
q.units = struct('k1', 'uM^-2 s^-1', 'kminus1', 's^-1', ...
    'k2', 'uM^-1 s^-1', 'D_ref', 's^-1', 'V_RS_ref', 'uM s^-1', ...
    'M_qss_ref', 'uM', 'tau_M_ref', 's');
end
