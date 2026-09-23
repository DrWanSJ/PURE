function [dq, v] = rhs_pure_exact_reduced_nondim(~, q, m, I)
%RHS_PURE_EXACT_REDUCED_NONDIM Direct audited compact rates and six ODEs.
% Independent of dimensional RHS. All six returned rates use V/Vstar.
y = reconstruct_pure_exact_reduced_nondim_state(q,m,I);
g = m.groups;
TX = g.mu_TX*g.theta_DNA*y(1)/(g.kappa_TX_NTP+y(1));
RS = g.mu_RS*y(4)/(g.kappa_RS_A+y(4))*y(5)/(g.kappa_RS_T+y(5)) ...
    *y(1)/(g.kappa_RS_NTP+y(1));
TL = g.mu_TL*y(10)*y(3)/(g.kappa_TL_nt+y(3))*y(6)/(g.kappa_TL_AT+y(6)) ...
    *y(1)/(g.kappa_TL_NTP+y(1));
EN = g.mu_EN*y(8)/(g.kappa_EN_CP+y(8))*y(2)/(g.kappa_EN_NXP+y(2));
dq = [-TX-RS-2*TL+EN; TX-y(3); -g.rho_A*RS; ...
    g.rho_T*(RS-TL); -g.rho_C*EN; -g.mu_TLdeg*y(10)];
v = [TX,y(3),RS,TL,g.mu_TLdeg*g.TLcat_to_nucleotide_scale*y(10),EN];
end
