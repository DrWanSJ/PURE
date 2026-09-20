function fp = appendix_a_fixed_point(p)
%APPENDIX_A_FIXED_POINT Bracketed root solve on the proved interval [0,1].
%
% Appendix A gives H(0)>0 and H(1)<0.  We check those signs before calling
% fzero instead of using an unconstrained root guess.

H0 = appendix_a_H(0,p);
H1 = appendix_a_H(1,p);
if ~(H0>0 && H1<0)
    error('appendix_a:invalidBracket', ...
        'Expected H(0)>0 and H(1)<0; parameter assumptions were violated.');
end

e_star = fzero(@(e) appendix_a_H(e,p),[0 1]);
u_star = p.alpha*e_star;

fp = struct();
fp.u = u_star;
fp.e = e_star;
fp.y = [u_star;e_star];
fp.H_residual = appendix_a_H(e_star,p);
end
