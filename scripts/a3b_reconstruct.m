function x = a3b_reconstruct(C, y, q)
%A3B_RECONSTRUCT  Exact pre-QSSA reconstruction x = R(y, q).
%
%   y  220x1 slow coordinates: [identity rows (212, C.keepPos order);
%                                 ledger totals (8, C.ledger order)]
%   q  21x1 eliminated-complex values (C.elimIdx order)
%
% The eliminated complexes and the identity-row species are read off
% directly; each replaced free carrier is reconstructed from its ledger
% total,
%     x_carrier = (y_total - sum_{j != carrier} w_j x_j) / w_carrier,
% in the frozen order (eliminated -> free enzymes -> free tRNAs -> ATP ->
% PPi -> Met -> Gly) so every member value is available when needed.  The
% map is exactly invertible (rank(T) = 241, see protected_ledger_rowspace.json).

x = zeros(241, 1);
x(C.keepIdx) = y(C.keepPos);
x(C.elimIdx) = q(:);
for k = 1:C.nLedger
    L = C.ledger(k);
    s = 0;
    for m = 1:numel(L.members)
        j = L.members(m);
        if j ~= L.replIdx
            s = s + L.weights(m) * x(j);
        end
    end
    x(L.replIdx) = (y(L.pos) - s) / L.wself;
end
end
