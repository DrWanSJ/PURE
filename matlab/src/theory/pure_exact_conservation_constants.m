function b = pure_exact_conservation_constants(p)
%PURE_EXACT_CONSERVATION_CONSTANTS Six invariants from the loaded B1 initial state.
% D_nt(0) = D_TLcat(0) = 0 are the canonical no-feedback accounting convention.
% Multiplicities and all physical initial values come from P, never new defaults.
x0 = [p.y0(:); 0; 0];
b.B_NTP = p.n_NTP*x0(1) + x0(2) + x0(3) + x0(11);
b.B_AA = p.n_A*x0(4) + x0(7) + p.n_T*x0(6);
b.B_tRNA = p.n_T*x0(5) + p.n_T*x0(6);
b.B_CP = x0(8) + x0(9);
b.B_TLcat = x0(10) + x0(12);
b.I6 = x0(2) + x0(9) - 3*x0(7) - p.n_T*x0(6);
end
