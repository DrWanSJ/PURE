function H = appendix_a_H(e,p)
%APPENDIX_A_H Scalar fixed-point residual from tasklist Eq. (A.5).
%
% At steady state du/dtau=0 gives u=alpha*e. Substituting that relation into
% de/dtau leaves H(e)=0 on the proven bracket [0,1].

u = p.alpha.*e;
psi = appendix_a_psi(u,e,p);
H = p.rho*(1-e)-p.delta*e-p.eta*psi;
end
