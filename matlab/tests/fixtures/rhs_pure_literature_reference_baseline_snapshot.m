function [dydt, rates] = rhs_pure_literature_reference_baseline_snapshot(~, y, p)
%RHS_PURE_LITERATURE_REFERENCE Right-hand side of the Mavelli 2015 PURE model.
%
%   [DYDT, RATES] = RHS_PURE_LITERATURE_REFERENCE(T, Y, P)
%
%   Literal deterministic translation of:
%     Mavelli, F., Marangoni, R., Stano, P. (2015),
%     "A Simple Protein Synthesis Model for the PURE System Operation",
%     Bulletin of Mathematical Biology 77:1185-1212,
%     DOI: 10.1007/s11538-015-0082-8.
%   Implemented here: Sect. 2, Eqs. (5), (6), (8), (10), (12), (14), (20)-(27).
%   NO equation was altered, added, or re-fitted (B1 literature benchmark).
%
%   State vector Y (concentrations in uM, time in s), fixed order:
%     y(1)  NTP   : average NTP concentration (per nucleotide species)      [uM]
%     y(2)  NXP   : overall exhausted-nucleotide pool (NDP + NMP pooled)    [uM]
%     y(3)  nt    : overall polymerized nucleotides (mRNA in monomer units) [uM]
%     y(4)  A     : average amino-acid concentration (per species)          [uM]
%     y(5)  T     : average tRNA concentration (per species)                [uM]
%     y(6)  AT    : average aminoacyl-tRNA concentration (per species)      [uM]
%     y(7)  a     : overall polymerized amino acids (protein monomer units) [uM]
%     y(8)  CP    : creatine phosphate                                      [uM]
%     y(9)  C     : creatine                                                [uM]
%     y(10) TLcat : fictitious effective translation catalyst               [uM]
%   DNA, TXcat, RScat, ENcat are FIXED inputs inside P, not states.
%
%   RATES (uM/s), fixed order:
%     rates(1) V_TX     transcription polymerization   paper Eq. (5)
%     rates(2) V_nt_deg polymerized-nucleotide decay  paper Eq. (6)
%     rates(3) V_RS     aminoacylation                 paper Eq. (8)
%     rates(4) V_TL     translation elongation         paper Eq. (10)
%     rates(5) V_TL_deg TL machinery decay             paper Eq. (12)
%     rates(6) V_EN     energy regeneration            paper Eq. (14)
%
%   NOTE (paper Sect. 2.3): each elongation event consumes two NTP
%   molecules; this two-fold factor appears in the stoichiometry of
%   Eqs. (20)-(21) below, but the NTP dependence of V_TL remains a SINGLE
%   rectangular-hyperbolic factor. Do not replace it by NTP^2.

NTP = y(1);  NXP = y(2);  nt  = y(3);  A  = y(4);
T   = y(5);  AT  = y(6);  a   = y(7);  CP = y(8);
TLcat = y(10);  % y(9) = C (creatine) appears in no rate law (Eqs. (13)-(14))

% ---- multiplicity factors (paper Sect. 2, Eqs. (8), (10), (15)-(19)) ----
n_NTP = p.n_NTP;   % = 4
n_A   = p.n_A;     % = 20
n_T   = p.n_T;     % = 46
fTA   = n_T/n_A;   % = 46/20 = 2.3, the paper's "2.3[T]" / "2.3[AT]" factor

% ---- rate laws ----
% Eq. (5): transcription, NTP -> nt + PPi, catalyzed by TXcat, templated by DNA
V_TX = p.k_TX * p.TXcat * (p.DNA/(p.K_TX_DNA + p.DNA)) ...
                      * (NTP /(p.K_TX_NTP + NTP));

% Eq. (6): polymerized-nucleotide (mRNA) degradation, pseudo-first order
V_nt_deg = p.k_nt_deg * nt;

% Eq. (8): aminoacylation, A + T + NTP -> AT + NXP, catalyzed by RScat
V_RS = p.k_RS * p.RScat * (A     /(p.K_RS_A   + A)) ...
                       * (fTA*T/(p.K_RS_T   + fTA*T)) ...
                       * (NTP  /(p.K_RS_NTP + NTP));

% Eq. (10): translation elongation, AT + 2NTP -> a + T + 2NXP,
%           catalyzed by TLcat, templated by nt
V_TL = p.k_TL * TLcat * (nt    /(p.K_TL_nt  + nt)) ...
                      * (fTA*AT/(p.K_TL_AT  + fTA*AT)) ...
                      * (NTP   /(p.K_TL_NTP + NTP));

% Eq. (12): TL machinery decay, pseudo-first order
V_TL_deg = p.k_TL_deg * TLcat;

% Eq. (14): energy regeneration, CP + NXP -> C + NTP, catalyzed by ENcat
V_EN = p.k_EN * p.ENcat * (CP /(p.K_EN_CP  + CP)) ...
                       * (NXP/(p.K_EN_NXP + NXP));

rates = [V_TX, V_nt_deg, V_RS, V_TL, V_TL_deg, V_EN];

% ---- ODEs (paper Eqs. (20)-(27); comments give the paper equation no.) ----
dydt = zeros(10,1);
dydt(1)  = (-V_TX - 2*V_TL - V_RS + V_EN)/n_NTP;   % Eq. (20)  d[NTP]/dt
dydt(2)  =  2*V_TL + V_RS - V_EN;                  % Eq. (21)  d[NXP]/dt
dydt(3)  =  V_TX - V_nt_deg;                       % Eq. (22)  d[nt]/dt
dydt(4)  = -V_RS/n_A;                              % Eq. (23)  d[A]/dt
dydt(5)  = (-V_RS + V_TL)/n_T;                     % Eq. (24)  d[T]/dt
dydt(6)  = ( V_RS - V_TL)/n_T;                     % Eq. (24)  d[AT]/dt
dydt(7)  =  V_TL;                                  % Eq. (25)  d[a]/dt
dydt(8)  = -V_EN;                                  % Eq. (26)  d[CP]/dt
dydt(9)  =  V_EN;                                  % Eq. (26)  d[C]/dt
dydt(10) = -V_TL_deg;                              % Eq. (27)  d[TLcat]/dt
end
