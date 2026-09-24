function dr = rs_nonrs_rate_derivatives(s, p)
%RS_NONRS_RATE_DERIVATIVES Analytic dimensional canonical non-RS derivatives.
% Rows follow canonical [V_TX,V_nt_deg,V_RS,V_TL,V_TL_deg,V_EN]; row 3
% is zero because canonical V_RS has no role in either D7 state update.
% Only derivatives are implemented here; runtime rates call canonical RHS.
% Forms follow jacobian_pure_literature_dimensionless in physical units.
sat = @(z, k) z/(k + z);
dsat = @(z, k) k/(k + z)^2;
fTA = p.n_T / p.n_A;
dr = zeros(6, 10);
dr(1,1) = p.k_TX*p.TXcat*sat(p.DNA,p.K_TX_DNA)*dsat(s(1),p.K_TX_NTP);
dr(2,3) = p.k_nt_deg;
dr(4,1) = p.k_TL*s(10)*sat(s(3),p.K_TL_nt) ...
    *sat(fTA*s(6),p.K_TL_AT)*dsat(s(1),p.K_TL_NTP);
dr(4,3) = p.k_TL*s(10)*dsat(s(3),p.K_TL_nt) ...
    *sat(fTA*s(6),p.K_TL_AT)*sat(s(1),p.K_TL_NTP);
dr(4,6) = p.k_TL*s(10)*sat(s(3),p.K_TL_nt) ...
    *fTA*dsat(fTA*s(6),p.K_TL_AT)*sat(s(1),p.K_TL_NTP);
dr(4,10) = p.k_TL*sat(s(3),p.K_TL_nt) ...
    *sat(fTA*s(6),p.K_TL_AT)*sat(s(1),p.K_TL_NTP);
dr(5,10) = p.k_TL_deg;
dr(6,2) = p.k_EN*p.ENcat*sat(s(8),p.K_EN_CP)*dsat(s(2),p.K_EN_NXP);
dr(6,8) = p.k_EN*p.ENcat*dsat(s(8),p.K_EN_CP)*sat(s(2),p.K_EN_NXP);
end
