(* ::Mathematica:: *)
(* verify_wolfram_v2.wl
   PURE literature-reference nondimensionalization audit.
   Physical ODEs follow Mavelli 2015; Dnt/DTL are no-feedback accounting
   integrators used to close the conservation ledgers.

   T1: 12 dimensionless ODEs, direct vs compact symbolic equivalence
   T2: 5 dimensional conservation laws
   T3: 5 dimensionless conservation laws
   T4: 5 random positive-parameter numerical residual checks
   T5: conservation check with nN=4, nA=20, nT=46
*)

$s23 = 23/10;

(* ---------- 0. Dimensional model ---------- *)
Vtx = kTX Ct DNA/(Kd + DNA) NTP/(Kt + NTP);
Vrs = kRs Cr A/(Ka + A) ($s23 T)/(Kt2 + $s23 T) NTP/(Kn2 + NTP);
Vtl = kTl TLcat nt/(Knt + nt) ($s23 AT)/(Kat + $s23 AT) NTP/(Kn3 + NTP);
Ven = kEn Ce CP/(Kcp + CP) NXP/(Knxp + NXP);
Vnd = knd nt;
Vld = kld TLcat;

dNTP = (-Vtx - Vrs - 2 Vtl + Ven)/nN;
dNXP = Vrs + 2 Vtl - Ven;
dnt  = Vtx - Vnd;
dA   = -Vrs/nA;
dT   = (-Vrs + Vtl)/nT;
dAT  = (Vrs - Vtl)/nT;
da   = Vtl;
dCP  = -Ven;
dC   = Ven;
dTLc = -Vld;
dDnt = Vnd;
dDTL = Vld;

(* ---------- T2. Dimensional conservation ---------- *)
Print["========== T2: dimensional conservation residuals =========="];
resNTPraw = nN dNTP + dnt + dNXP + dDnt;
resAAraw = nA dA + da + nT dAT;
resTraw = nT dT + nT dAT;
Print["NTP: ", FullSimplify[resNTPraw]];
Print["AA: ", FullSimplify[resAAraw]];
Print["tRNA: ", FullSimplify[resTraw]];
Print["CP: ", FullSimplify[dCP + dC]];
Print["TLcat: ", FullSimplify[dTLc + dDTL]];

(* ---------- 1. Scales and definitions ---------- *)
subc = {
 NTP -> y1 cN, NXP -> y2 nN cN, nt -> y3 nN cN,
 A -> y4 cA, T -> y5 cT, AT -> y6 cT, a -> y7 nA cA,
 CP -> y8 cC, C -> y9 cC, TLcat -> y10 cL,
 Dnt -> y11 nN cN, DTL -> y12 cL
};

scales = {cN, nN cN, nN cN, cA, cT, cT, nA cA, cC, cC, cL, nN cN, cL};
rhs = {dNTP, dNXP, dnt, dA, dT, dAT, da, dCP, dC, dTLc, dDnt, dDTL};

direct = Table[
 FullSimplify[(rhs[[i]] /. subc)/(scales[[i]] knd)],
 {i, 12}
];

dimDef = {
 muTX -> kTX Ct/(knd nN cN),
 muRS -> kRs Cr/(knd nN cN),
 muTL -> kTl cL/(knd nN cN),
 muEN -> kEn Ce/(knd nN cN),
 muTLD -> kld/knd,
 thD -> DNA/(Kd + DNA),
 kxTXN -> Kt/cN,
 kxRSA -> Ka/cA,
 kxRST -> Kt2/($s23 cT),
 kxRSN -> Kn2/cN,
 kxTLn -> Knt/(nN cN),
 kxTLa -> Kat/($s23 cT),
 kxTLN -> Kn3/cN,
 kxENC -> Kcp/cC,
 kxENX -> Knxp/(nN cN),
 rhoA -> (nN cN)/(nA cA),
 rhoT -> (nN cN)/(nT cT),
 rhoC -> (nN cN)/cC
};

(* ---------- 2. Compact dimensionless rates ---------- *)
vtx = muTX thD y1/(kxTXN + y1);
vrs = muRS y4/(kxRSA + y4) y5/(kxRST + y5) y1/(kxRSN + y1);
vtl = muTL y10 y3/(kxTLn + y3) y6/(kxTLa + y6) y1/(kxTLN + y1);
ven = muEN y8/(kxENC + y8) y2/(kxENX + y2);

compact = {
 -vtx - vrs - 2 vtl + ven,
  vrs + 2 vtl - ven,
  vtx - y3,
 -rhoA vrs,
  rhoT (-vrs + vtl),
  rhoT (vrs - vtl),
  rhoA vtl,
 -rhoC ven,
  rhoC ven,
 -muTLD y10,
  y3,
  muTLD y10
};
compactDim = compact /. dimDef;

(* ---------- T1. Per-ODE symbolic equivalence ---------- *)
Print["
========== T1: per-ODE symbolic equivalence =========="];
t1 = Table[
 Module[{d = FullSimplify[compactDim[[i]] - direct[[i]]]},
  {i, d, TrueQ[d == 0]}],
 {i, 12}
];
Print /@ t1;
Print["T1 ALL PASS: ", TrueQ[And @@ (#[[3]] & /@ t1)]];

(* ---------- T3. Dimensionless conservation ---------- *)
Print["
========== T3: dimensionless conservation =========="];
ys = {y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12};
invList = {
 y1 + y2 + y3 + y11,
 (y4 + y7)/rhoA + y6/rhoT,
 y5 + y6,
 y8 + y9,
 y10 + y12
};
invNames = {
 "nucleotide", "amino-acid", "tRNA", "CP", "TLcat"
};
t3 = Table[
 Module[{grad, dfdt},
  grad = D[invList[[k]], #] & /@ ys;
  dfdt = FullSimplify[grad . compact];
  {invNames[[k]], dfdt, TrueQ[dfdt == 0]}],
 {k, 5}
];
Print /@ t3;
Print["T3 ALL PASS: ", TrueQ[And @@ (#[[3]] & /@ t3)]];

(* ---------- T4. Random numerical residuals ---------- *)
Print["
========== T4: numeric residuals =========="];
SeedRandom[2026];
parsDim = {
 kTX, Ct, Kd, Kt, kRs, Cr, Ka, Kt2, Kn2, kTl, Knt, Kat, Kn3,
 kEn, Ce, Kcp, Knxp, knd, kld, nN, nA, nT, cN, cA, cT, cC, cL, DNA
};
maxRes = 0.;
Do[
 vals = Thread[parsDim -> RandomReal[{0.05, 5}, Length[parsDim]]];
 yv = Thread[ys -> RandomReal[{0.05, 3}, 12]];
 res = Max[Abs[N[(compactDim - direct) /. vals /. yv]]];
 maxRes = Max[maxRes, res];
 Print["trial ", tr, ": max|residual| = ", res],
 {tr, 5}
];
Print["T4 global max |residual| = ", maxRes,
      "  (<1e-12: ", TrueQ[maxRes < 10^-12], ")"];

(* ---------- T5. PURE multiplicities ---------- *)
Print["
========== T5: nN=4, nA=20, nT=46 =========="];
Print["AA: ", FullSimplify[resAAraw /. {nA -> 20, nT -> 46}]];
Print["tRNA: ", FullSimplify[resTraw /. nT -> 46]];
Print["NTP: ", FullSimplify[resNTPraw /. nN -> 4]];
