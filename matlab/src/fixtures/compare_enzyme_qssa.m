function cmp = compare_enzyme_qssa(profile)
%COMPARE_ENZYME_QSSA Pointwise full-vs-reduced error calculation.
%
% Product p is common to all formulations. We also compare:
%   standard QSSA free s  versus full free s;
%   total QSSA s_T       versus full s+c.
%
% All errors are scaled by 1+s0 to avoid division problems near zero.

full = simulate_enzyme_qssa_full(profile);
sq = simulate_enzyme_qssa_reduced(profile,'standard');
tq = simulate_enzyme_qssa_reduced(profile,'total');

if ~isequal(full.t,sq.t) || ~isequal(full.t,tq.t)
    error('enzyme_qssa:gridMismatch', ...
        'Full and reduced trajectories must use the same output grid.');
end

scale = 1+full.p.s0;

cmp = struct();
cmp.profile = profile;
cmp.full = full;
cmp.standard = sq;
cmp.total = tq;

cmp.standard_product_scaled_error = ...
    max(abs(sq.p_product-full.p_product))/scale;
cmp.total_product_scaled_error = ...
    max(abs(tq.p_product-full.p_product))/scale;

cmp.standard_free_substrate_scaled_error = ...
    max(abs(sq.s_free-full.s))/scale;
cmp.total_unreacted_substrate_scaled_error = ...
    max(abs(tq.s_total_unreacted-full.s_total_unreacted))/scale;
end
