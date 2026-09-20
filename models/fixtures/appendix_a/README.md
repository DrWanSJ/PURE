# B0 fixture: appendix_a

This is the dimensionless two-state analytic test system from tasklist Appendix A.
It is not the Mavelli model and e must not be renamed into a real PURE ATP pool.

The fixture has known structural answers:
- u>=0 and 0<=e<=1 is forward invariant;
- one fixed point exists in the bracket e in (0,1);
- the analytic Jacobian has trace<0 and determinant>0;
- both fixed-point eigenvalues have negative real part;
- the system must not produce a Hopf crossing under the allowed parameters.

Three synthetic profiles are frozen:
- baseline: generic interior dynamics;
- low_load: tests Eq. A.13 only where its assumptions hold;
- saturated: tests Eq. A.14 only where its assumptions hold.
