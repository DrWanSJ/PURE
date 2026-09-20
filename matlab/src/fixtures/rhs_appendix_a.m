function dydt = rhs_appendix_a(~,y,p)
%RHS_APPENDIX_A Dimensionless system from tasklist Eq. (A.2).
%
% y(1)=u: effective expression load, analytically constrained to u>=0.
% y(2)=e: available carrier fraction, analytically constrained to 0<=e<=1.
%
% No clipping is used; the vector field itself must preserve the domain.

u = y(1);
e = y(2);
psi = appendix_a_psi(u,e,p);

du = p.alpha*e-u;
de = p.rho*(1-e)-p.eta*psi-p.delta*e;

dydt = [du;de];
end
