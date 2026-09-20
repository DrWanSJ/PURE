function approx = appendix_a_approximations(p)
%APPENDIX_A_APPROXIMATIONS Eqs. (A.13) and (A.14).
%
% Returning a formula does NOT declare it globally valid. The tests explicitly
% check the small/large dimensionless conditions before judging each formula.

low = 2*p.rho / (p.rho+p.delta + ...
    sqrt((p.rho+p.delta)^2 + 4*p.rho*p.eta*p.alpha/p.K_e));

sat = (p.rho-p.eta)/(p.rho+p.delta);

approx = struct();
approx.e_low_load = low;
approx.e_saturated = sat;
approx.saturated_requires_rho_gt_eta = p.rho>p.eta;
end
