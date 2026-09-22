function xfull = reconstruct_pure_exact_reduced_state(z, p, b)
%RECONSTRUCT_PURE_EXACT_REDUCED_STATE Exact affine reconstruction; no clipping.
% Z is one 6x1 column [NTP; nt; A; AT; CP; TLcat].
% XFULL is [NTP; NXP; nt; A; T; AT; a; CP; C; TLcat; D_nt; D_TLcat].
% B must be fixed from the initial state, not recomputed along the trajectory.
if nargin < 3
    b = pure_exact_conservation_constants(p);
end
if ~isvector(z) || numel(z) ~= 6
    error('pure_exact:badState', 'z must contain exactly six independent coordinates.');
end
NTP = z(1); nt = z(2); A = z(3); AT = z(4); CP = z(5); TLcat = z(6);
T = b.B_tRNA/p.n_T - AT;
a = b.B_AA - p.n_A*A - p.n_T*AT;
C = b.B_CP - CP;
NXP = b.I6 - C + 3*a + p.n_T*AT;
D_TLcat = b.B_TLcat - TLcat;
D_nt = b.B_NTP - p.n_NTP*NTP - NXP - nt;
xfull = [NTP; NXP; nt; A; T; AT; a; CP; C; TLcat; D_nt; D_TLcat];
end
