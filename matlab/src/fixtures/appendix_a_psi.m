function [psi,psi_u,psi_e] = appendix_a_psi(u,e,p)
%APPENDIX_A_PSI Flux and analytic partial derivatives, Eqs. (A.1),(A.7).
%
%   psi   = u/(1+u) * e/(K_e+e)
%   psi_u = e / ((1+u)^2*(K_e+e))
%   psi_e = u*K_e / ((1+u)*(K_e+e)^2)

psi = (u./(1+u)).*(e./(p.K_e+e));

if nargout >= 2
    psi_u = e./((1+u).^2.*(p.K_e+e));
end
if nargout >= 3
    psi_e = (u.*p.K_e)./((1+u).*(p.K_e+e).^2);
end
end
