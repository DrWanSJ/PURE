function J = jacobian_pure_literature_dimensionless(~, y, g)
%JACOBIAN_PURE_LITERATURE_DIMENSIONLESS Exact derivative of the compact RHS.
% Supplying the analytic Jacobian to ode15s avoids finite-difference Jacobian
% errors in the stiff startup. This changes no ODE, scales or solver tolerances.
sat = @(z,k) z/(k+z);
dsat = @(z,k) k/(k+z)^2;
q = zeros(4,12); % derivatives of [vTX vRS vTL vEN]
q(1,1) = g.mu_TX*g.theta_DNA*dsat(y(1),g.kappa_TX_NTP);
q(2,1) = g.mu_RS*sat(y(4),g.kappa_RS_A)*sat(y(5),g.kappa_RS_T)*dsat(y(1),g.kappa_RS_NTP);
q(2,4) = g.mu_RS*dsat(y(4),g.kappa_RS_A)*sat(y(5),g.kappa_RS_T)*sat(y(1),g.kappa_RS_NTP);
q(2,5) = g.mu_RS*sat(y(4),g.kappa_RS_A)*dsat(y(5),g.kappa_RS_T)*sat(y(1),g.kappa_RS_NTP);
q(3,1) = g.mu_TL*y(10)*sat(y(3),g.kappa_TL_nt)*sat(y(6),g.kappa_TL_AT)*dsat(y(1),g.kappa_TL_NTP);
q(3,3) = g.mu_TL*y(10)*dsat(y(3),g.kappa_TL_nt)*sat(y(6),g.kappa_TL_AT)*sat(y(1),g.kappa_TL_NTP);
q(3,6) = g.mu_TL*y(10)*sat(y(3),g.kappa_TL_nt)*dsat(y(6),g.kappa_TL_AT)*sat(y(1),g.kappa_TL_NTP);
q(3,10) = g.mu_TL*sat(y(3),g.kappa_TL_nt)*sat(y(6),g.kappa_TL_AT)*sat(y(1),g.kappa_TL_NTP);
q(4,2) = g.mu_EN*sat(y(8),g.kappa_EN_CP)*dsat(y(2),g.kappa_EN_NXP);
q(4,8) = g.mu_EN*dsat(y(8),g.kappa_EN_CP)*sat(y(2),g.kappa_EN_NXP);
J = zeros(12,12);
J(1,:) = -q(1,:)-q(2,:)-2*q(3,:)+q(4,:);
J(2,:) = q(2,:)+2*q(3,:)-q(4,:);
J(3,:) = q(1,:); J(3,3) = J(3,3)-1;
J(4,:) = -g.rho_A*q(2,:);
J(5,:) = g.rho_T*(-q(2,:)+q(3,:));
J(6,:) = -J(5,:);
J(7,:) = g.rho_A*q(3,:);
J(8,:) = -g.rho_C*q(4,:); J(9,:) = -J(8,:);
J(10,10) = -g.mu_TLdeg;
J(11,3) = 1; J(12,10) = g.mu_TLdeg;
end
