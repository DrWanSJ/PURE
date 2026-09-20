function c = enzyme_qssa_algebraic_complex(x, p, method)
%ENZYME_QSSA_ALGEBRAIC_COMPLEX Complex concentration under two QSSA choices.
%
% method='standard':
%   x is FREE substrate s.
%   c=e_T*s/(K_M+s).
%
% method='total':
%   x is total unreacted substrate s_T=s+c.
%   The physical solution is the smaller root of tasklist Eq. (7.9).
%   We use the rationalized form
%
%   c = 2*e_T*s_T / (A + sqrt(A^2-4*e_T*s_T)),
%   A = e_T+s_T+K_M,
%
%   because it is numerically safer than subtracting two close numbers.

method = validatestring(method, {'standard','total'});

switch method
    case 'standard'
        s = x;
        c = p.e_T.*s./(p.K_M+s);

    case 'total'
        sT = x;
        A = p.e_T+sT+p.K_M;
        disc = A.^2-4*p.e_T.*sT;

        if any(disc(:) < -1e-12)
            error('enzyme_qssa:negativeDiscriminant', ...
                'Total-QSSA algebraic discriminant became negative.');
        end

        % Only roundoff-sized negative values are projected back to zero.
        disc = max(disc,0);
        denom = A+sqrt(disc);

        c = zeros(size(sT));
        nz = denom>0;
        c(nz) = 2*p.e_T.*sT(nz)./denom(nz);
end
end
