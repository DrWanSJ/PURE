# B0 fixture: enzyme_qssa

Reaction:

    E + S <-> C -> E + P

The full model tracks free substrate s, complex c and product p. Free enzyme is
derived from e = e_T - c.

Two reductions are intentionally kept separate:

1. Standard QSSA uses free substrate s:
       c_qss = e_T*s/(K_M+s)

2. Total QSSA uses total unreacted substrate s_T=s+c and solves the algebraic
   binding relation for c. The smaller physical root is evaluated in rationalized
   form to avoid subtracting nearly equal numbers.

Two synthetic parameter profiles are frozen:
- valid: e_T/s0 = 0.01, where standard QSSA should work.
- failure: e_T/s0 = 0.5, where binding sequesters substantial substrate and the
  standard free-substrate QSSA should visibly fail.

This is a reduction verification problem, not a claim about a specific PURE enzyme.
