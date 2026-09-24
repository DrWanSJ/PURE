function blocks = rs_explicit_jacobian_blocks(s, M, p, q)
%RS_EXPLICIT_JACOBIAN_BLOCKS Analytic partial derivatives of F(s,M), G(s,M).
% F_s holds M fixed; it is not the reduced Jacobian. The reduced Jacobian
% additionally requires F_M*dh/ds, evaluated at M=h(s).
dr = rs_nonrs_rate_derivatives(s, p);
Fs = zeros(10, 10);
Fs(1,:) = (-dr(1,:) - 2*dr(4,:) + dr(6,:))/p.n_NTP;
Fs(2,:) = 2*dr(4,:) - dr(6,:);
Fs(3,:) = dr(1,:) - dr(2,:);
Fs(5,:) = dr(4,:)/p.n_T;
Fs(6,:) = -dr(4,:)/p.n_T;
Fs(7,:) = dr(4,:);
Fs(8,:) = -dr(6,:);
Fs(9,:) = dr(6,:);
Fs(10,:) = -dr(5,:);

fTA = p.n_T / p.n_A;
alpha = q.k1 * s(4) * s(1);
beta = q.kminus1;
gamma = q.k2 * fTA * s(5);
dv1_s = zeros(1, 10);
dv1_s(1) = q.k1*s(4)*(p.RScat - M);
dv1_s(4) = q.k1*s(1)*(p.RScat - M);
dv2_s = zeros(1, 10);
dv2_s(5) = q.k2*M*fTA;
dv1_M = -alpha - beta;
dv2_M = gamma;
S_activation = zeros(10, 1);
S_activation(1) = -1/p.n_NTP;
S_activation(4) = -1/p.n_A;
S_transfer = zeros(10, 1);
S_transfer(2) = 1;
S_transfer(5) = -1/p.n_T;
S_transfer(6) = 1/p.n_T;
Fs = Fs + S_activation*dv1_s + S_transfer*dv2_s;
FM = S_activation*dv1_M + S_transfer*dv2_M;
Gs = dv1_s - dv2_s;
GM = -alpha - beta - gamma;
blocks = struct('Fs', Fs, 'FM', FM, 'Gs', Gs, 'GM', GM);
end
