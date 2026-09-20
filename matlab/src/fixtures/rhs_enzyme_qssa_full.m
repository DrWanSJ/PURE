function dydt = rhs_enzyme_qssa_full(~, y, p)
%RHS_ENZYME_QSSA_FULL Full mass-action model from tasklist Eq. (7.6).
%
% State order:
%   s = y(1): FREE substrate
%   c = y(2): enzyme-substrate complex
%   p = y(3): product
%
% The total enzyme pool e_T is fixed, so free enzyme is e=e_T-c.
%
% Reactions:
%   E+S -> C    v_bind   = k1*e*s
%   C -> E+S    v_unbind = k_minus1*c
%   C -> E+P    v_cat    = k2*c

s = y(1);
c = y(2);

e = p.e_T-c;
v_bind = p.k1*e*s;
v_unbind = p.k_minus1*c;
v_cat = p.k2*c;

ds = -v_bind+v_unbind;
dc =  v_bind-v_unbind-v_cat;
dp =  v_cat;

dydt = [ds;dc;dp];
end
