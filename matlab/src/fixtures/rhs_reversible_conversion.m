function dydt = rhs_reversible_conversion(~, y, p)
%RHS_REVERSIBLE_CONVERSION RHS for the B0 reversible-conversion fixture.
%
%   A <-> B
%   forward rate = k_f*A
%   reverse rate = k_r*B
%
%   No clipping or state projection is applied.

A = y(1);
B = y(2);

v_forward = p.k_f * A;
v_reverse = p.k_r * B;

dydt = [ ...
    -v_forward + v_reverse; ...
     v_forward - v_reverse];
end
