function J = appendix_a_jacobian(u,e,p)
%APPENDIX_A_JACOBIAN Analytic Jacobian from tasklist Eq. (A.8).
%
% Sign structure:
%   d(du)/du = -1
%   d(du)/de = +alpha
%   d(de)/du = -eta*psi_u
%   d(de)/de = -rho-delta-eta*psi_e

[~,psi_u,psi_e] = appendix_a_psi(u,e,p);

J = [-1, p.alpha; ...
     -p.eta*psi_u, -p.rho-p.delta-p.eta*psi_e];
end
