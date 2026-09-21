# -*- coding: utf-8 -*-
"""PURE literature-reference nondimensionalization with SymPy.

Time scale:
    tau = k_ntdeg * t

The physical ODEs follow Mavelli 2015. D_nt and D_TLcat are auxiliary
accounting integrators used only to close conservation ledgers.
"""

import random
import sympy as sp

pos = dict(positive=True)

NTP, NXP, nt, A, T, AT, a, CP, C, TLcat, Dnt, DTL, DNA = sp.symbols(
    "NTP NXP nt A T AT a CP C TLcat Dnt DTL DNA", **pos
)

k_TX, C_TXcat, K_TX_DNA, K_TX_NTP = sp.symbols(
    "k_TX C_TXcat K_TX_DNA K_TX_NTP", **pos
)
k_RS, C_RScat, K_RS_A, K_RS_T, K_RS_NTP = sp.symbols(
    "k_RS C_RScat K_RS_A K_RS_T K_RS_NTP", **pos
)
k_TL, K_TL_nt, K_TL_AT, K_TL_NTP = sp.symbols(
    "k_TL K_TL_nt K_TL_AT K_TL_NTP", **pos
)
k_EN, C_ENcat, K_EN_CP, K_EN_NXP = sp.symbols(
    "k_EN C_ENcat K_EN_CP K_EN_NXP", **pos
)
k_ntdeg, k_TLdeg = sp.symbols("k_ntdeg k_TLdeg", **pos)

n_NTP, n_A, n_T, c_NTP0, cA0, cT0, cCP0, cTL0 = sp.symbols(
    "n_NTP n_A n_T c_NTP0 c_A0 c_T0 c_CP0 c_TLcat0", **pos
)

y = sp.symbols("y1:13", nonnegative=True)
y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12 = y

mu_TX, mu_RS, mu_TL, mu_EN, mu_TLdeg = sp.symbols(
    "mu_TX mu_RS mu_TL mu_EN mu_TLdeg", **pos
)
kTXdna, kTXntp, kRSa, kRSt, kRSntp, kTLnt, kTLat, kTLntp, kENcp, kENnxp = sp.symbols(
    "kappa_TX_DNA kappa_TX_NTP kappa_RS_A kappa_RS_T kappa_RS_NTP "
    "kappa_TL_nt kappa_TL_AT kappa_TL_NTP kappa_EN_CP kappa_EN_NXP",
    **pos
)
rhoA, rhoT, rhoC = sp.symbols("rho_A rho_T rho_C", **pos)

s23 = sp.Rational(23, 10)

# Dimensional rates.
V_TX = k_TX * C_TXcat * DNA / (K_TX_DNA + DNA) * NTP / (K_TX_NTP + NTP)
V_RS = (
    k_RS
    * C_RScat
    * A / (K_RS_A + A)
    * (s23 * T) / (K_RS_T + s23 * T)
    * NTP / (K_RS_NTP + NTP)
)
V_TL = (
    k_TL
    * TLcat
    * nt / (K_TL_nt + nt)
    * (s23 * AT) / (K_TL_AT + s23 * AT)
    * NTP / (K_TL_NTP + NTP)
)
V_EN = (
    k_EN
    * C_ENcat
    * CP / (K_EN_CP + CP)
    * NXP / (K_EN_NXP + NXP)
)
V_ntdeg = k_ntdeg * nt
V_TLdeg = k_TLdeg * TLcat

rhs = [
    (-V_TX - V_RS - 2 * V_TL + V_EN) / n_NTP,
    V_RS + 2 * V_TL - V_EN,
    V_TX - V_ntdeg,
    -V_RS / n_A,
    (-V_RS + V_TL) / n_T,
    (V_RS - V_TL) / n_T,
    V_TL,
    -V_EN,
    V_EN,
    -V_TLdeg,
    V_ntdeg,
    V_TLdeg,
]

scales = [
    c_NTP0,
    n_NTP * c_NTP0,
    n_NTP * c_NTP0,
    cA0,
    cT0,
    cT0,
    n_A * cA0,
    cCP0,
    cCP0,
    cTL0,
    n_NTP * c_NTP0,
    cTL0,
]

subs_conc = {
    NTP: y1 * c_NTP0,
    NXP: y2 * n_NTP * c_NTP0,
    nt: y3 * n_NTP * c_NTP0,
    A: y4 * cA0,
    T: y5 * cT0,
    AT: y6 * cT0,
    a: y7 * n_A * cA0,
    CP: y8 * cCP0,
    C: y9 * cCP0,
    TLcat: y10 * cTL0,
    Dnt: y11 * n_NTP * c_NTP0,
    DTL: y12 * cTL0,
}

subs_K = {
    K_TX_DNA: kTXdna * DNA,
    K_TX_NTP: kTXntp * c_NTP0,
    K_RS_A: kRSa * cA0,
    K_RS_T: kRSt * s23 * cT0,
    K_RS_NTP: kRSntp * c_NTP0,
    K_TL_nt: kTLnt * n_NTP * c_NTP0,
    K_TL_AT: kTLat * s23 * cT0,
    K_TL_NTP: kTLntp * c_NTP0,
    K_EN_CP: kENcp * cCP0,
    K_EN_NXP: kENnxp * n_NTP * c_NTP0,
}

subs_mu = {
    k_TX: mu_TX * k_ntdeg * n_NTP * c_NTP0 / C_TXcat,
    k_RS: mu_RS * k_ntdeg * n_NTP * c_NTP0 / C_RScat,
    k_TL: mu_TL * k_ntdeg * n_NTP * c_NTP0 / cTL0,
    k_EN: mu_EN * k_ntdeg * n_NTP * c_NTP0 / C_ENcat,
    k_TLdeg: mu_TLdeg * k_ntdeg,
}

all_subs = {}
all_subs.update(subs_conc)
all_subs.update(subs_K)
all_subs.update(subs_mu)

Vstar = k_ntdeg * n_NTP * c_NTP0

def nondim_rate(expr):
    return sp.factor(sp.cancel(expr.subs(all_subs) / Vstar))

vTX = nondim_rate(V_TX)
vRS = nondim_rate(V_RS)
vTL = nondim_rate(V_TL)
vEN = nondim_rate(V_EN)

rho_defs = {
    rhoA: n_NTP * c_NTP0 / (n_A * cA0),
    rhoT: n_NTP * c_NTP0 / (n_T * cT0),
    rhoC: n_NTP * c_NTP0 / cCP0,
}

dy = [
    -vTX - vRS - 2 * vTL + vEN,
    vRS + 2 * vTL - vEN,
    vTX - y3,
    -rhoA * vRS,
    rhoT * (-vRS + vTL),
    rhoT * (vRS - vTL),
    rhoA * vTL,
    -rhoC * vEN,
    rhoC * vEN,
    -mu_TLdeg * y10,
    y3,
    mu_TLdeg * y10,
]

# Dimensionless conservation checks.
inv_res = [
    sp.simplify(dy[0] + dy[1] + dy[2] + dy[10]),
    sp.simplify((dy[3] + dy[6]) / rhoA + dy[5] / rhoT),
    sp.simplify(dy[4] + dy[5]),
    sp.simplify(dy[7] + dy[8]),
    sp.simplify(dy[9] + dy[11]),
]
assert all(r == 0 for r in inv_res), inv_res
print("CONSERVATION CHECK: ALL PASS (5 invariants)")

# Random direct-vs-compact numerical check.
random.seed(42)

pdim = [
    NTP, NXP, nt, A, T, AT, a, CP, C, TLcat, Dnt, DTL, DNA,
    k_TX, C_TXcat, K_TX_DNA, K_TX_NTP,
    k_RS, C_RScat, K_RS_A, K_RS_T, K_RS_NTP,
    k_TL, K_TL_nt, K_TL_AT, K_TL_NTP,
    k_EN, C_ENcat, K_EN_CP, K_EN_NXP,
    k_ntdeg, k_TLdeg,
    n_NTP, n_A, n_T, c_NTP0, cA0, cT0, cCP0, cTL0,
]
state_dim = [NTP, NXP, nt, A, T, AT, a, CP, C, TLcat, Dnt, DTL]

ok = True
for trial in range(5):
    vals = {s: random.uniform(0.05, 5.0) for s in pdim}

    yvals = {}
    for i in range(12):
        scale_val = float(scales[i].subs(vals))
        yvals[y[i]] = vals[state_dim[i]] / scale_val

    dimless_vals = {
        mu_TX: vals[k_TX] * vals[C_TXcat] / (vals[k_ntdeg] * vals[n_NTP] * vals[c_NTP0]),
        mu_RS: vals[k_RS] * vals[C_RScat] / (vals[k_ntdeg] * vals[n_NTP] * vals[c_NTP0]),
        mu_TL: vals[k_TL] * vals[cTL0] / (vals[k_ntdeg] * vals[n_NTP] * vals[c_NTP0]),
        mu_EN: vals[k_EN] * vals[C_ENcat] / (vals[k_ntdeg] * vals[n_NTP] * vals[c_NTP0]),
        mu_TLdeg: vals[k_TLdeg] / vals[k_ntdeg],
        kTXdna: vals[K_TX_DNA] / vals[DNA],
        kTXntp: vals[K_TX_NTP] / vals[c_NTP0],
        kRSa: vals[K_RS_A] / vals[cA0],
        kRSt: vals[K_RS_T] / (float(s23) * vals[cT0]),
        kRSntp: vals[K_RS_NTP] / vals[c_NTP0],
        kTLnt: vals[K_TL_nt] / (vals[n_NTP] * vals[c_NTP0]),
        kTLat: vals[K_TL_AT] / (float(s23) * vals[cT0]),
        kTLntp: vals[K_TL_NTP] / vals[c_NTP0],
        kENcp: vals[K_EN_CP] / vals[cCP0],
        kENnxp: vals[K_EN_NXP] / (vals[n_NTP] * vals[c_NTP0]),
        rhoA: vals[n_NTP] * vals[c_NTP0] / (vals[n_A] * vals[cA0]),
        rhoT: vals[n_NTP] * vals[c_NTP0] / (vals[n_T] * vals[cT0]),
        rhoC: vals[n_NTP] * vals[c_NTP0] / vals[cCP0],
    }

    compact_subs = {}
    compact_subs.update(yvals)
    compact_subs.update(dimless_vals)

    for i in range(12):
        direct = rhs[i].subs(vals) / (scales[i].subs(vals) * vals[k_ntdeg])
        compact = dy[i].subs(compact_subs)
        err = abs(float(sp.N(direct - compact)))
        if err > 1e-9 * max(1.0, abs(float(sp.N(direct)))):
            print(f"MISMATCH trial={trial} eq={i+1}: err={err}")
            ok = False

print("NUMERIC CHECK:", "ALL PASS (5 trials x 12 eqs)" if ok else "FAILED")

if not ok:
    raise SystemExit(1)

print("\nCompact dimensionless rates:")
print("v_TX =", sp.latex(vTX))
print("v_RS =", sp.latex(vRS))
print("v_TL =", sp.latex(vTL))
print("v_EN =", sp.latex(vEN))

print("\nCompact dimensionless ODEs:")
for i, expr in enumerate(dy, start=1):
    print(f"dy{i}/dtau =", sp.latex(sp.factor(expr)))
