# Human reduction review — PNAS 2017 translation chemistry

**All boxes are intentionally empty.** This document organizes the 968 combined-SBML reactions by biochemical process and original source subsystem. A reaction may appear in several process cards because the 26 source diagrams reuse chemistry; the combined model still has 968 unique reaction IDs. Every suggested transformation below is `HUMAN_REVIEW_REQUIRED`. The source SBML, author simulator CSVs, and row-level [`reduction_decisions.csv`](reduction_decisions.csv) are the evidence trail. No choice here is finalized or validated. The migrated [historical reduction evidence](pnas2017_historical_evidence.md) and [open decisions](open_scientific_decisions.md) are separate from these current unapproved review cards.

For particle change, the numbers below count stoichiometric changes in the *represented species* per individual event; they are an ideal proxy, not osmotic pressure. Free ATP/GTP/Pi/PPi deltas do not include carrier moieties bound in complexes. Ionic consequences remain unknown because formula/charge/protonation/Mg metadata are absent.

## Amino-acid activation

**Chemical process.** GlyRS or MetRS binds amino acid and ATP and forms an aminoacyl-adenylate; PPi is released through explicit states.

**Original implementation.** 50 unique combined reactions map to `Aminoacylation_A_Gly.xml`, `Aminoacylation_A_Met.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 12 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `ATP`, `AMP`, `PPi`, `Gly`, `Met`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 28 increase, 16 decrease and 6 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000126`: `Gly + GlyRS → GlyRS_Gly`; tracked-particle Δ = -1.
- `re0000000127`: `GlyRS_GlyAMP_PPi → GlyRS_GlyAMP + PPi`; tracked-particle Δ = 1.

**Candidate lumping.** A net activation step could replace reversible binding and adenylate intermediates only with explicit ATP→AMP/PPi bookkeeping and a justified rate law.

**Information lost if applied.** Aminoacyl-adenylate and synthetase occupancy, reverse fluxes, and the timing of PPi release would become unobservable without reconstruction. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000126`, `re0000000127`, `re0000000128`, `re0000000129`, `re0000000130`, `re0000000131`, `re0000000132`, `re0000000133`, `re0000000134`, `re0000000135`, `re0000000136`, `re0000000137`, `re0000000138`, `re0000000139`, `re0000000140`, `re0000000141`, `re0000000142`, `re0000000143`, `re0000000144`, `re0000000145`, `re0000000146`, `re0000000147`, `re0000000148`, `re0000000149`, `re0000000150`, `re0000000151`, `re0000000152`, `re0000000153`, `re0000000154`, `re0000000155`, `re0000000156`, `re0000000157`, `re0000000158`, `re0000000159`, `re0000000160`, `re0000000161`, `re0000000162`, `re0000000163`, `re0000000164`, `re0000000165`, `re0000000166`, `re0000000167`, `re0000000168`, `re0000000169`, `re0000000170`, `re0000000171`, `re0000000172`, `re0000000173`, `re0000000174`, `re0000000175`.

Candidate complex/intermediate IDs: `GlyRS_Gly_ATP`, `GlyRS_Gly`, `GlyRS_ATP`, `GlyRS_GlyAMP_PPi`, `GlyRS_GlyAMP`, `GlyRS_AMP`, `MetRS_Met_ATP`, `MetRS_Met`, `MetRS_ATP`, `MetRS_MetAMP_PPi`, `MetRS_MetAMP`, `MetRS_AMP`.

</details>

## tRNA aminoacylation

**Chemical process.** The aminoacyl-adenylate transfers amino acid to a specific tRNA, recycles synthetase, and releases AMP through enzyme-bound intermediates.

**Original implementation.** 88 unique combined reactions map to `Aminoacylation_B_fMetCAU.xml`, `Aminoacylation_B_GlyGCC.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 28 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `ATP`, `AMP`, `PPi`, `Gly`, `Met`, `tRNAGlyGCC`, `tRNAfMetCAU`, `GlytRNAGlyGCC`, `MettRNAfMetCAU`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 46 increase, 30 decrease and 12 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000006`: `tRNAfMetCAU → tRNAfMetCAU_degraded`; tracked-particle Δ = 0.
- `re0000000031`: `GlytRNAGlyGCC → GlytRNAGlyGCC_degraded`; tracked-particle Δ = 0.

**Candidate lumping.** Binding and transfer steps might be lumped into a charging reaction that explicitly conserves each tRNA and releases AMP.

**Information lost if applied.** Synthetase occupancy, bound tRNA, and free-versus-charged recycling times would be lost unless reconstructed and tested. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000006`, `re0000000031`, `re0000000070`, `re0000000176`, `re0000000177`, `re0000000178`, `re0000000179`, `re0000000180`, `re0000000181`, `re0000000182`, `re0000000183`, `re0000000184`, `re0000000185`, `re0000000186`, `re0000000187`, `re0000000188`, `re0000000189`, `re0000000190`, `re0000000191`, `re0000000192`, `re0000000193`, `re0000000194`, `re0000000195`, `re0000000196`, `re0000000197`, `re0000000198`, `re0000000199`, `re0000000200`, `re0000000201`, `re0000000202`, `re0000000203`, `re0000000204`, `re0000000205`, `re0000000206`, `re0000000207`, `re0000000208`, `re0000000209`, `re0000000210`, `re0000000211`, `re0000000212`, `re0000000213`, `re0000000214`, `re0000000215`, `re0000000216`, `re0000000217`, `re0000000218`, `re0000000219`, `re0000000220`, `re0000000221`, `re0000000222`, `re0000000223`, `re0000000224`, `re0000000225`, `re0000000226`, `re0000000227`, `re0000000228`, `re0000000229`, `re0000000230`, `re0000000231`, `re0000000232`, `re0000000233`, `re0000000234`, `re0000000235`, `re0000000236`, `re0000000237`, `re0000000238`, `re0000000239`, `re0000000240`, `re0000000241`, `re0000000242`, `re0000000243`, `re0000000244`, `re0000000245`, `re0000000246`, `re0000000247`, `re0000000248`, `re0000000249`, `re0000000250`, `re0000000251`, `re0000000252`, `re0000000253`, `re0000000254`, `re0000000255`, `re0000000256`, `re0000000257`, `re0000000258`, `re0000000259`, `re0000000260`.

Candidate complex/intermediate IDs: `GlyRS_Gly_ATP`, `GlyRS_Gly`, `GlyRS_ATP`, `GlyRS_GlyAMP_PPi`, `GlyRS_GlyAMP`, `GlyRS_AMP`, `MetRS_Met_ATP`, `MetRS_Met`, `MetRS_ATP`, `MetRS_MetAMP_PPi`, `MetRS_MetAMP`, `MetRS_AMP`, `GlyRS_GlytRNAGlyGCC`, `GlyRS_AMP_GlytRNAGlyGCC`, `GlyRS_GlyAMP_tRNAGlyGCC`, `GlyRS_tRNAGlyGCC`, `GlyRS_Gly_tRNAGlyGCC`, `GlyRS_ATP_tRNAGlyGCC`, `GlyRS_Gly_ATP_tRNAGlyGCC`, `GlyRS_GlyAMP_PPi_tRNAGlyGCC`, `MetRS_MettRNAfMetCAU`, `MetRS_AMP_MettRNAfMetCAU`, `MetRS_MetAMP_tRNAfMetCAU`, `MetRS_tRNAfMetCAU`, `MetRS_Met_tRNAfMetCAU`, `MetRS_ATP_tRNAfMetCAU`, `MetRS_Met_ATP_tRNAfMetCAU`, `MetRS_MetAMP_PPi_tRNAfMetCAU`.

</details>

## Initiator-tRNA formylation

**Chemical process.** MTF transfers a formyl group from the donor system to initiator Met-tRNA, producing fMet-tRNA and donor product states.

**Original implementation.** 29 unique combined reactions map to `FMet_tRNASynthesis.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 6 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `fMet`, `tRNAfMetCAU`, `MettRNAfMetCAU`, `fMettRNAfMetCAU`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 15 increase, 9 decrease and 5 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000417`: `fMettRNAfMetCAU → fMet + tRNAfMetCAU`; tracked-particle Δ = 1.
- `re0000000420`: `MTF + MettRNAfMetCAU → MTF_MettRNAfMetCAU`; tracked-particle Δ = -1.

**Candidate lumping.** An effective formylation step may retain donor/product molecules and initiator-tRNA identity while collapsing MTF binding states.

**Information lost if applied.** The MTF occupancy and donor-bound intermediates would no longer be direct observables; donor moiety balance must be resolved first. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000416`, `re0000000417`, `re0000000418`, `re0000000419`, `re0000000420`, `re0000000421`, `re0000000422`, `re0000000423`, `re0000000424`, `re0000000425`, `re0000000426`, `re0000000427`, `re0000000428`, `re0000000429`, `re0000000430`, `re0000000431`, `re0000000432`, `re0000000433`, `re0000000434`, `re0000000435`, `re0000000436`, `re0000000437`, `re0000000438`, `re0000000439`, `re0000000440`, `re0000000441`, `re0000000442`, `re0000000443`, `re0000000444`.

Candidate complex/intermediate IDs: `MTF_FD`, `MTF_MettRNAfMetCAU`, `MTF_FD_MettRNAfMetCAU`, `MTF_THF_fMettRNAfMetCAU`, `MTF_THF`, `MTF_fMettRNAfMetCAU`.

</details>

## Initiation factor preparation

**Chemical process.** IF2 and its GTP/GDP states participate in preparation for 30S/70S initiation.

**Original implementation.** 10 unique combined reactions map to `Initiation_A.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 3 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `GTP`, `GDP`, `fMettRNAfMetCAU`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 6 increase, 3 decrease and 1 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000445`: `GTP + IF2 → IF2_GTP`; tracked-particle Δ = -1.
- `re0000000446`: `IF2_GTP → GTP + IF2`; tracked-particle Δ = 1.

**Candidate lumping.** A conditional factor-cycle aggregate could retain explicit GTP/GDP/Pi and free IF2 pools.

**Information lost if applied.** IF2 nucleotide-state occupancy and exchange timing would be lost without a reconstruction rule. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000445`, `re0000000446`, `re0000000447`, `re0000000448`, `re0000000449`, `re0000000450`, `re0000000451`, `re0000000452`, `re0000000453`, `re0000000454`.

Candidate complex/intermediate IDs: `IF2_GTP`, `IF2_GDP`, `IF2_GTP_fMettRNAfMetCAU`.

</details>

## Ribosome and mRNA initiation assembly

**Chemical process.** 30S, mRNA, fMet-tRNA, IF1/IF2/IF3 and 50S form successive initiation complexes, including GTP hydrolysis and factor release.

**Original implementation.** 336 unique combined reactions map to `Initiation_B1.xml`, `Initiation_B2.xml`, `Initiation_C.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 45 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `GTP`, `GDP`, `PO4`, `fMettRNAfMetCAU`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 227 increase, 98 decrease and 11 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000005`: `fMettRNAfMetCAU → fMettRNAfMetCAU_degraded`; tracked-particle Δ = 0.
- `re0000000009`: `elRS70SAGGU0002_fMettRNAfMetCAU → RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA`; tracked-particle Δ = 3.

**Candidate lumping.** Several binding paths might be represented by a smaller occupancy graph if their factor and nucleotide balances are retained.

**Information lost if applied.** Order-of-binding paths, individual IF occupancy, preinitiation residence times, and some free/occupied ribosome fractions would become unrecoverable. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000003`, `re0000000004`, `re0000000005`, `re0000000008`, `re0000000009`, `re0000000010`, `re0000000451`, `re0000000455`, `re0000000456`, `re0000000457`, `re0000000458`, `re0000000459`, `re0000000460`, `re0000000461`, `re0000000462`, `re0000000463`, `re0000000464`, `re0000000465`, `re0000000466`, `re0000000467`, `re0000000468`, `re0000000469`, `re0000000470`, `re0000000471`, `re0000000472`, `re0000000473`, `re0000000474`, `re0000000475`, `re0000000476`, `re0000000477`, `re0000000478`, `re0000000479`, `re0000000480`, `re0000000481`, `re0000000482`, `re0000000483`, `re0000000484`, `re0000000485`, `re0000000486`, `re0000000487`, `re0000000488`, `re0000000489`, `re0000000490`, `re0000000491`, `re0000000492`, `re0000000493`, `re0000000494`, `re0000000495`, `re0000000496`, `re0000000497`, `re0000000498`, `re0000000499`, `re0000000500`, `re0000000501`, `re0000000502`, `re0000000503`, `re0000000504`, `re0000000505`, `re0000000506`, `re0000000507`, `re0000000508`, `re0000000509`, `re0000000510`, `re0000000511`, `re0000000512`, `re0000000513`, `re0000000514`, `re0000000515`, `re0000000516`, `re0000000517`, `re0000000518`, `re0000000519`, `re0000000520`, `re0000000521`, `re0000000522`, `re0000000523`, `re0000000524`, `re0000000525`, `re0000000526`, `re0000000527`, `re0000000528`, `re0000000529`, `re0000000530`, `re0000000531`, `re0000000532`, `re0000000533`, `re0000000534`, `re0000000535`, `re0000000536`, `re0000000537`, `re0000000538`, `re0000000539`, `re0000000540`, `re0000000541`, `re0000000542`, `re0000000543`, `re0000000544`, `re0000000545`, `re0000000546`, `re0000000547`, `re0000000548`, `re0000000549`, `re0000000550`, `re0000000551`, `re0000000552`, `re0000000553`, `re0000000554`, `re0000000555`, `re0000000556`, `re0000000557`, `re0000000558`, `re0000000559`, `re0000000560`, `re0000000561`, `re0000000562`, `re0000000563`, `re0000000564`, `re0000000565`, `re0000000566`, `re0000000567`, `re0000000568`, `re0000000569`, `re0000000570`, `re0000000571`, `re0000000572`, `re0000000573`, `re0000000574`, `re0000000575`, `re0000000576`, `re0000000577`, `re0000000578`, `re0000000579`, `re0000000580`, `re0000000581`, `re0000000582`, `re0000000583`, `re0000000584`, `re0000000585`, `re0000000586`, `re0000000587`, `re0000000588`, `re0000000589`, `re0000000590`, `re0000000591`, `re0000000592`, `re0000000593`, `re0000000594`, `re0000000595`, `re0000000596`, `re0000000597`, `re0000000598`, `re0000000599`, `re0000000600`, `re0000000601`, `re0000000602`, `re0000000603`, `re0000000604`, `re0000000605`, `re0000000606`, `re0000000607`, `re0000000608`, `re0000000609`, `re0000000610`, `re0000000611`, `re0000000612`, `re0000000613`, `re0000000614`, `re0000000615`, `re0000000616`, `re0000000617`, `re0000000618`, `re0000000619`, `re0000000620`, `re0000000621`, `re0000000622`, `re0000000623`, `re0000000624`, `re0000000625`, `re0000000626`, `re0000000627`, `re0000000628`, `re0000000629`, `re0000000630`, `re0000000631`, `re0000000632`, `re0000000633`, `re0000000634`, `re0000000635`, `re0000000636`, `re0000000637`, `re0000000638`, `re0000000639`, `re0000000640`, `re0000000641`, `re0000000642`, `re0000000643`, `re0000000644`, `re0000000645`, `re0000000646`, `re0000000647`, `re0000000648`, `re0000000649`, `re0000000650`, `re0000000651`, `re0000000652`, `re0000000653`, `re0000000654`, `re0000000655`, `re0000000656`, `re0000000657`, `re0000000658`, `re0000000659`, `re0000000660`, `re0000000661`, `re0000000662`, `re0000000663`, `re0000000664`, `re0000000665`, `re0000000666`, `re0000000667`, `re0000000668`, `re0000000669`, `re0000000670`, `re0000000671`, `re0000000672`, `re0000000673`, `re0000000674`, `re0000000675`, `re0000000676`, `re0000000677`, `re0000000678`, `re0000000679`, `re0000000680`, `re0000000681`, `re0000000682`, `re0000000683`, `re0000000684`, `re0000000685`, `re0000000686`, `re0000000687`, `re0000000688`, `re0000000689`, `re0000000690`, `re0000000691`, `re0000000692`, `re0000000693`, `re0000000694`, `re0000000695`, `re0000000696`, `re0000000697`, `re0000000698`, `re0000000699`, `re0000000700`, `re0000000701`, `re0000000702`, `re0000000703`, `re0000000704`, `re0000000705`, `re0000000706`, `re0000000707`, `re0000000708`, `re0000000709`, `re0000000710`, `re0000000711`, `re0000000712`, `re0000000713`, `re0000000714`, `re0000000715`, `re0000000716`, `re0000000717`, `re0000000718`, `re0000000719`, `re0000000720`, `re0000000721`, `re0000000722`, `re0000000723`, `re0000000724`, `re0000000725`, `re0000000726`, `re0000000727`, `re0000000728`, `re0000000729`, `re0000000730`, `re0000000731`, `re0000000732`, `re0000000733`, `re0000000734`, `re0000000735`, `re0000000736`, `re0000000737`, `re0000000738`, `re0000000739`, `re0000000740`, `re0000000741`, `re0000000742`, `re0000000743`, `re0000000744`, `re0000000745`, `re0000000746`, `re0000000747`, `re0000000748`, `re0000000749`, `re0000000750`, `re0000000751`, `re0000000752`, `re0000000753`, `re0000000754`, `re0000000755`, `re0000000756`, `re0000000757`, `re0000000758`, `re0000000759`, `re0000000760`, `re0000000761`, `re0000000762`, `re0000000763`, `re0000000764`, `re0000000765`, `re0000000766`, `re0000000767`, `re0000000768`, `re0000000769`, `re0000000770`, `re0000000771`, `re0000000772`, `re0000000773`, `re0000000774`, `re0000000775`, `re0000000776`, `re0000000777`, `re0000000778`, `re0000000779`, `re0000000780`, `re0000000781`, `re0000000782`, `re0000000783`.

Candidate complex/intermediate IDs: `elRS70SAGGU0002_fMettRNAfMetCAU`, `IF2_GTP`, `IF2_GDP`, `IF2_GTP_fMettRNAfMetCAU`, `RS30S_IF1`, `RS30S_IF1_IF3`, `RS30S_IF1_IF3_IF2_GTP`, `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU`, `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS30S_IF1_IF3_IF2_GTP_mRNA`, `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA`, `RS30S_IF1_IF3_mRNA`, `RS30S_IF3`, `RS30S_IF3_IF2_GTP`, `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU`, `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS30S_IF3_IF2_GTP_mRNA`, `RS30S_IF3_fMettRNAfMetCAU_mRNA`, `RS30S_IF3_mRNA`, `RS70S_IF1`, `RS70S_IF1_IF3`, `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS70S_IF3`, `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS30S_IF2_GTP`, `RS30S_IF2_GTP_fMettRNAfMetCAU`, `RS30S_mRNA`, `RS30S_fMettRNAfMetCAU_mRNA`, `RS30S_IF2_GTP_mRNA`, `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS30S_IF1_IF2_GTP`, `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU`, `RS30S_IF1_mRNA`, `RS30S_IF1_fMettRNAfMetCAU_mRNA`, `RS30S_IF1_IF2_GTP_mRNA`, `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA`, `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`, `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`, `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA`, `RS70S_IF1_fMettRNAfMetCAU_mRNA`, `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`, `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`, `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`, `RS70S_IF3_fMettRNAfMetCAU_mRNA`.

</details>

## EF-Tu ternary-complex delivery

**Chemical process.** EF-Tu, EF-Ts, GTP/GDP and aminoacyl-tRNA assemble and recycle the ternary delivery complex.

**Original implementation.** 34 unique combined reactions map to `Elongation_A_Gly.xml`, `Elongation_A_Met.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 7 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `GTP`, `GDP`, `GlytRNAGlyGCC`, `MettRNAfMetCAU`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 21 increase, 9 decrease and 4 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000031`: `GlytRNAGlyGCC → GlytRNAGlyGCC_degraded`; tracked-particle Δ = 0.
- `re0000000258`: `MettRNAfMetCAU → MettRNAfMetCAU_degraded`; tracked-particle Δ = 0.

**Candidate lumping.** An effective delivery cycle could combine assembly/exchange while retaining GTP/GDP, charged tRNA and free EF-Tu/EF-Ts inventories.

**Information lost if applied.** Ternary-complex occupancy, exchange pathway fluxes and delay to ribosome delivery would be lost. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000029`, `re0000000031`, `re0000000258`, `re0000000261`, `re0000000262`, `re0000000263`, `re0000000264`, `re0000000265`, `re0000000266`, `re0000000267`, `re0000000268`, `re0000000269`, `re0000000270`, `re0000000271`, `re0000000272`, `re0000000273`, `re0000000274`, `re0000000275`, `re0000000276`, `re0000000277`, `re0000000278`, `re0000000279`, `re0000000280`, `re0000000281`, `re0000000282`, `re0000000283`, `re0000000284`, `re0000000285`, `re0000000286`, `re0000000287`, `re0000000288`, `re0000000289`, `re0000000290`, `re0000000291`.

Candidate complex/intermediate IDs: `EFTu_GTP_GlytRNAGlyGCC`, `EFTu_GDP`, `EFTu_EFTs`, `EFTu_GDP_EFTs`, `EFTu_GTP`, `EFTu_GTP_EFTs`, `EFTu_GTP_MettRNAfMetCAU`.

</details>

## EF-G nucleotide cycle

**Chemical process.** EF-G associates with ribosomal states and GTP/GDP/Pi during the translocation cycle.

**Original implementation.** 40 unique combined reactions map to `Elongation_B.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 8 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `GTP`, `GDP`, `PO4`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 25 increase, 8 decrease and 7 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000292`: `EFG_GDP → EFG + GDP`; tracked-particle Δ = 1.
- `re0000000293`: `EFG + GDP → EFG_GDP`; tracked-particle Δ = -1.

**Candidate lumping.** Binding/release steps might be lumped around an explicit GTP-consuming translocation event.

**Information lost if applied.** EF-G-bound ribosome occupancy and separate hydrolysis/product-release timing would be lost. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000003`, `re0000000004`, `re0000000030`, `re0000000292`, `re0000000293`, `re0000000294`, `re0000000295`, `re0000000296`, `re0000000297`, `re0000000298`, `re0000000299`, `re0000000300`, `re0000000301`, `re0000000302`, `re0000000303`, `re0000000304`, `re0000000305`, `re0000000306`, `re0000000307`, `re0000000308`, `re0000000309`, `re0000000310`, `re0000000311`, `re0000000312`, `re0000000313`, `re0000000314`, `re0000000315`, `re0000000316`, `re0000000317`, `re0000000318`, `re0000000319`, `re0000000320`, `re0000000321`, `re0000000322`, `re0000000323`, `re0000000324`, `re0000000325`, `re0000000326`, `re0000000327`, `re0000000328`.

Candidate complex/intermediate IDs: `EFG_GTP`, `EFG_GDP`, `RS70S_EFG_GDP`, `RS50S_EFG_GDP`, `RS70S_EFG_GTP`, `RS50S_EFG_GTP`, `RS70S_EFG_GDP_PO4`, `RS50S_EFG_GDP_PO4`.

</details>

## Peptidyl-tRNA and ribosome transitions

**Chemical process.** The model advances sequence-specific peptidyl-tRNA and ribosome complexes through Gly addition and translocation toward fMGG.

**Original implementation.** 125 unique combined reactions map to `Elongation_Ca1_fMetCAU.xml`, `Elongation_Ca1_GlyGCC.xml`, `Elongation_Ca2_pept0002.xml`, `Elongation_Ca2_pept0003.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 27 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `GTP`, `GDP`, `PO4`, `fMet`, `tRNAGlyGCC`, `tRNAfMetCAU`, `GlytRNAGlyGCC`, `fMettRNAfMetCAU`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 80 increase, 20 decrease and 25 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000001`: `elRS70SAGGU0002_fMettRNAfMetCAU → elRS70SAGGU0002_fMet + tRNAfMetCAU`; tracked-particle Δ = 1.
- `re0000000002`: `elRS70SAGGU0002_fMet + tRNAfMetCAU → elRS70SAGGU0002_fMettRNAfMetCAU`; tracked-particle Δ = -1.

**Candidate lumping.** Some microscopic ribosome steps might be grouped by peptide length and occupancy while retaining amino-acid incorporation, tRNA return and GTP/Pi accounting.

**Information lost if applied.** Pre/post-translocation occupancy, intermediate peptide species and individual tRNA release times would become unavailable. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000001`, `re0000000002`, `re0000000003`, `re0000000004`, `re0000000005`, `re0000000006`, `re0000000007`, `re0000000008`, `re0000000009`, `re0000000010`, `re0000000011`, `re0000000012`, `re0000000013`, `re0000000014`, `re0000000015`, `re0000000016`, `re0000000017`, `re0000000018`, `re0000000019`, `re0000000020`, `re0000000021`, `re0000000022`, `re0000000023`, `re0000000024`, `re0000000025`, `re0000000026`, `re0000000027`, `re0000000028`, `re0000000029`, `re0000000030`, `re0000000031`, `re0000000032`, `re0000000033`, `re0000000034`, `re0000000035`, `re0000000036`, `re0000000037`, `re0000000038`, `re0000000039`, `re0000000040`, `re0000000041`, `re0000000042`, `re0000000043`, `re0000000044`, `re0000000045`, `re0000000046`, `re0000000047`, `re0000000048`, `re0000000049`, `re0000000050`, `re0000000051`, `re0000000052`, `re0000000053`, `re0000000054`, `re0000000055`, `re0000000056`, `re0000000057`, `re0000000058`, `re0000000059`, `re0000000060`, `re0000000061`, `re0000000062`, `re0000000063`, `re0000000064`, `re0000000065`, `re0000000066`, `re0000000067`, `re0000000068`, `re0000000069`, `re0000000070`, `re0000000071`, `re0000000072`, `re0000000073`, `re0000000074`, `re0000000075`, `re0000000076`, `re0000000077`, `re0000000078`, `re0000000079`, `re0000000080`, `re0000000081`, `re0000000082`, `re0000000083`, `re0000000084`, `re0000000085`, `re0000000086`, `re0000000087`, `re0000000088`, `re0000000089`, `re0000000090`, `re0000000091`, `re0000000092`, `re0000000093`, `re0000000094`, `re0000000095`, `re0000000096`, `re0000000097`, `re0000000098`, `re0000000099`, `re0000000100`, `re0000000101`, `re0000000102`, `re0000000103`, `re0000000104`, `re0000000105`, `re0000000106`, `re0000000107`, `re0000000108`, `re0000000109`, `re0000000110`, `re0000000111`, `re0000000112`, `re0000000113`, `re0000000114`, `re0000000115`, `re0000000116`, `re0000000117`, `re0000000118`, `re0000000119`, `re0000000120`, `re0000000121`, `re0000000122`, `re0000000123`, `re0000000124`, `re0000000125`.

Candidate complex/intermediate IDs: `elRS70SAGGU0002_fMettRNAfMetCAU`, `elRS70SAGGU0002_fMet`, `EFTu_GTP_GlytRNAGlyGCC`, `EFG_GTP`, `EFG_GDP`, `elRS70SAGGU0003_Pept0002tRNAGlyGCC`, `EFTu_GDP`, `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC`, `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC`, `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC`, `elRS70SAGGU0002_fMet_EFTu_GDP`, `elRS70SAGGU0002_fMet_GlytRNAGlyGCC`, `elRS70SBGGU0002_Pept0002tRNAGlyGCC`, `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP`, `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4`, `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP`, `elRS70SAGGU0003_Pept0002`, `elRS70SAUAA0004_Pept0003tRNAGlyGCC`, `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC`, `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC`, `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC`, `elRS70SAGGU0003_Pept0002_EFTu_GDP`, `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC`, `elRS70SBGGU0003_Pept0003tRNAGlyGCC`, `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP`, `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4`, `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP`.

</details>

## RF1/RF2 peptide release

**Chemical process.** Release factors bind the stop-codon complex and hydrolyze peptidyl-tRNA to release the fMGG peptide.

**Original implementation.** 35 unique combined reactions map to `Termination_A_RF1.xml`, `Termination_A_RF2.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 6 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `tRNAGlyGCC`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 22 increase, 6 decrease and 7 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000070`: `tRNAGlyGCC → tRNAGlyGCC_degraded`; tracked-particle Δ = 0.
- `re0000000805`: `termRS70SUAA0004_tRNAGlyGCC_RF1 → RF1 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC`; tracked-particle Δ = 4.

**Candidate lumping.** RF1 and RF2 pathways might share a net release step only if branch-specific kinetics and factor usage are preserved or explicitly discarded.

**Information lost if applied.** RF1-versus-RF2 occupancy, pathway-specific release kinetics and bound peptide states would be lost. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000003`, `re0000000004`, `re0000000008`, `re0000000070`, `re0000000090`, `re0000000116`, `re0000000117`, `re0000000796`, `re0000000797`, `re0000000798`, `re0000000799`, `re0000000800`, `re0000000801`, `re0000000802`, `re0000000803`, `re0000000804`, `re0000000805`, `re0000000806`, `re0000000807`, `re0000000808`, `re0000000809`, `re0000000810`, `re0000000811`, `re0000000812`, `re0000000813`, `re0000000814`, `re0000000815`, `re0000000816`, `re0000000817`, `re0000000818`, `re0000000819`, `re0000000820`, `re0000000821`, `re0000000822`, `re0000000823`.

Candidate complex/intermediate IDs: `elRS70SAUAA0004_Pept0003tRNAGlyGCC`, `termRS70SUAA0004_tRNAGlyGCC`, `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1`, `termRS70SUAA0004_tRNAGlyGCC_RF1`, `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2`, `termRS70SUAA0004_tRNAGlyGCC_RF2`.

</details>

## RF3-assisted termination

**Chemical process.** RF3 and GTP/GDP states promote turnover of release-factor-bound posttermination complexes.

**Original implementation.** 76 unique combined reactions map to `Termination_B_RF1.xml`, `Termination_B_RF2.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 14 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `GTP`, `GDP`, `PO4`, `tRNAGlyGCC`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 51 increase, 16 decrease and 9 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000070`: `tRNAGlyGCC → tRNAGlyGCC_degraded`; tracked-particle Δ = 0.
- `re0000000825`: `RF3_GDP → GDP + RF3`; tracked-particle Δ = 1.

**Candidate lumping.** An effective RF3 recycling step could preserve nucleotide consumption and factor availability.

**Information lost if applied.** RF1/RF2/RF3 complex occupancy and GDP/Pi release timing would be lost. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000003`, `re0000000004`, `re0000000008`, `re0000000070`, `re0000000803`, `re0000000818`, `re0000000824`, `re0000000825`, `re0000000826`, `re0000000827`, `re0000000828`, `re0000000829`, `re0000000830`, `re0000000831`, `re0000000832`, `re0000000833`, `re0000000834`, `re0000000835`, `re0000000836`, `re0000000837`, `re0000000838`, `re0000000839`, `re0000000840`, `re0000000841`, `re0000000842`, `re0000000843`, `re0000000844`, `re0000000845`, `re0000000846`, `re0000000847`, `re0000000848`, `re0000000849`, `re0000000850`, `re0000000851`, `re0000000852`, `re0000000853`, `re0000000854`, `re0000000855`, `re0000000856`, `re0000000857`, `re0000000858`, `re0000000859`, `re0000000860`, `re0000000861`, `re0000000862`, `re0000000863`, `re0000000864`, `re0000000865`, `re0000000866`, `re0000000867`, `re0000000868`, `re0000000869`, `re0000000870`, `re0000000871`, `re0000000872`, `re0000000873`, `re0000000874`, `re0000000875`, `re0000000876`, `re0000000877`, `re0000000878`, `re0000000879`, `re0000000880`, `re0000000881`, `re0000000882`, `re0000000883`, `re0000000884`, `re0000000885`, `re0000000886`, `re0000000887`, `re0000000888`, `re0000000889`, `re0000000890`, `re0000000891`, `re0000000892`, `re0000000893`.

Candidate complex/intermediate IDs: `termRS70SUAA0004_tRNAGlyGCC`, `termRS70SUAA0004_tRNAGlyGCC_RF1`, `termRS70SUAA0004_tRNAGlyGCC_RF2`, `RF3_GDP`, `RF3_GTP`, `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP`, `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP`, `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3`, `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP`, `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP`, `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4`, `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP`, `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP`, `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3`.

</details>

## Ribosome recycling

**Chemical process.** RRF and EF-G split/recycle posttermination ribosome and tRNA/mRNA complexes with explicit guanylate states.

**Original implementation.** 86 unique combined reactions map to `Termination_C.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 16 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `GTP`, `GDP`, `PO4`, `tRNAGlyGCC`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 59 increase, 19 decrease and 8 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000070`: `tRNAGlyGCC → tRNAGlyGCC_degraded`; tracked-particle Δ = 0.
- `re0000000296`: `EFG_GTP → EFG_degraded + GTP`; tracked-particle Δ = 1.

**Candidate lumping.** A reduced recycling path could retain 30S/50S/70S, free versus occupied pools, tRNA return and GTP→GDP/Pi.

**Information lost if applied.** Posttermination residence times and RRF/EF-G occupancy would no longer be direct observables. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000003`, `re0000000004`, `re0000000008`, `re0000000030`, `re0000000070`, `re0000000296`, `re0000000297`, `re0000000308`, `re0000000314`, `re0000000315`, `re0000000327`, `re0000000894`, `re0000000895`, `re0000000896`, `re0000000897`, `re0000000898`, `re0000000899`, `re0000000900`, `re0000000901`, `re0000000902`, `re0000000903`, `re0000000904`, `re0000000905`, `re0000000906`, `re0000000907`, `re0000000908`, `re0000000909`, `re0000000910`, `re0000000911`, `re0000000912`, `re0000000913`, `re0000000914`, `re0000000915`, `re0000000916`, `re0000000917`, `re0000000918`, `re0000000919`, `re0000000920`, `re0000000921`, `re0000000922`, `re0000000923`, `re0000000924`, `re0000000925`, `re0000000926`, `re0000000927`, `re0000000928`, `re0000000929`, `re0000000930`, `re0000000931`, `re0000000932`, `re0000000933`, `re0000000934`, `re0000000935`, `re0000000936`, `re0000000937`, `re0000000938`, `re0000000939`, `re0000000940`, `re0000000941`, `re0000000942`, `re0000000943`, `re0000000944`, `re0000000945`, `re0000000946`, `re0000000947`, `re0000000948`, `re0000000949`, `re0000000950`, `re0000000951`, `re0000000952`, `re0000000953`, `re0000000954`, `re0000000955`, `re0000000956`, `re0000000957`, `re0000000958`, `re0000000959`, `re0000000960`, `re0000000961`, `re0000000962`, `re0000000963`, `re0000000964`, `re0000000965`, `re0000000966`, `re0000000967`, `re0000000968`.

Candidate complex/intermediate IDs: `EFG_GTP`, `EFG_GDP`, `RS50S_EFG_GDP`, `termRS70SUAA0004_tRNAGlyGCC`, `RS50S_RRF`, `RS50S_RRF_EFG_GDP`, `RS50S_tRNAGlyGCC`, `RS50S_tRNAGlyGCC_EFG_GDP`, `RS50S_tRNAGlyGCC_RRF`, `RS50S_tRNAGlyGCC_RRF_EFG_GDP`, `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP`, `termRS70SUAA0004_tRNAGlyGCC_RRF`, `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP`, `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4`, `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP`, `termRS30S_mRNA`.

</details>

## Creatine-kinase energy regeneration

**Chemical process.** CK exchanges phosphoryl groups between creatine phosphate/creatine and ADP/ATP through bound enzyme states.

**Original implementation.** 25 unique combined reactions map to `EnergyRegeneration_A.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 6 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `ATP`, `ADP`, `CP`, `Cr`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 14 increase, 8 decrease and 3 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000330`: `ADP + CK → CK_ADP`; tracked-particle Δ = -1.
- `re0000000331`: `CK_ADP → ADP + CK`; tracked-particle Δ = 1.

**Candidate lumping.** A reversible net CP + ADP ↔ Cr + ATP candidate could preserve these four explicit resources if supported by kinetics.

**Information lost if applied.** CK occupancy and mechanistic forward/reverse rates would be lost; the ideal-particle effect and proton/Mg chemistry need separate review. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000329`, `re0000000330`, `re0000000331`, `re0000000332`, `re0000000333`, `re0000000334`, `re0000000335`, `re0000000336`, `re0000000337`, `re0000000338`, `re0000000339`, `re0000000340`, `re0000000341`, `re0000000342`, `re0000000343`, `re0000000344`, `re0000000345`, `re0000000346`, `re0000000347`, `re0000000348`, `re0000000349`, `re0000000350`, `re0000000351`, `re0000000352`, `re0000000353`.

Candidate complex/intermediate IDs: `CK_ADP`, `CK_ATP`, `CK_CP`, `CK_CP_ADP`, `CK_Cr`, `CK_Cr_ATP`.

</details>

## Nucleotide-diphosphate kinase exchange

**Chemical process.** NDK couples adenylate and guanylate carriers through nucleotide-bound enzyme states.

**Original implementation.** 25 unique combined reactions map to `EnergyRegeneration_B.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 6 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `ATP`, `ADP`, `GTP`, `GDP`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 14 increase, 8 decrease and 3 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000355`: `ATP + NDK → NDK_ATP`; tracked-particle Δ = -1.
- `re0000000356`: `NDK_ATP → ATP + NDK`; tracked-particle Δ = 1.

**Candidate lumping.** A net ATP + GDP ↔ ADP + GTP candidate could retain both carrier pools.

**Information lost if applied.** NDK occupancy and exchange intermediates would be lost; charge/Mg and reverse-flow assumptions remain unresolved. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000354`, `re0000000355`, `re0000000356`, `re0000000357`, `re0000000358`, `re0000000359`, `re0000000360`, `re0000000361`, `re0000000362`, `re0000000363`, `re0000000364`, `re0000000365`, `re0000000366`, `re0000000367`, `re0000000368`, `re0000000369`, `re0000000370`, `re0000000371`, `re0000000372`, `re0000000373`, `re0000000374`, `re0000000375`, `re0000000376`, `re0000000377`, `re0000000378`.

Candidate complex/intermediate IDs: `NDK_GDP`, `NDK_ATP`, `NDK_GDP_ATP`, `NDK_GTP_ADP`, `NDK_ADP`, `NDK_GTP`.

</details>

## Adenylate kinase exchange

**Chemical process.** MK interconverts adenylate carrier states with distinct bound-ADP intermediates.

**Original implementation.** 25 unique combined reactions map to `EnergyRegeneration_C.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 6 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `ATP`, `ADP`, `AMP`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 14 increase, 8 decrease and 3 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000380`: `ATP + MK → MK_ATP`; tracked-particle Δ = -1.
- `re0000000381`: `MK_ATP → ATP + MK`; tracked-particle Δ = 1.

**Candidate lumping.** A net ATP + AMP ↔ 2 ADP candidate could retain the three free adenylate species.

**Information lost if applied.** MK occupancy and its two ADP-bound configurations would be lost; adenylate moiety and particle checks are required. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000379`, `re0000000380`, `re0000000381`, `re0000000382`, `re0000000383`, `re0000000384`, `re0000000385`, `re0000000386`, `re0000000387`, `re0000000388`, `re0000000389`, `re0000000390`, `re0000000391`, `re0000000392`, `re0000000393`, `re0000000394`, `re0000000395`, `re0000000396`, `re0000000397`, `re0000000398`, `re0000000399`, `re0000000400`, `re0000000401`, `re0000000402`, `re0000000403`.

Candidate complex/intermediate IDs: `MK_AMP`, `MK_ATP`, `MK_ATP_AMP`, `MK_ADP_1`, `MK_ADP_2`, `MK_ADP_ADP`.

</details>

## Pyrophosphate hydrolysis

**Chemical process.** PPiase binds PPi and releases two `PO4` species; the source MathML coefficient of 2 must be preserved.

**Original implementation.** 12 unique combined reactions map to `EnergyRegeneration_D.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 3 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `PO4`, `PPi`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 6 increase, 3 decrease and 3 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000405`: `PPi + PPiase → PPiase_PPi`; tracked-particle Δ = -1.
- `re0000000406`: `PPiase_PPi → PPi + PPiase`; tracked-particle Δ = 1.

**Candidate lumping.** A net PPi → 2 Pi step could collapse PPiase binding while keeping PPi/Pi and the +1 ideal-particle event change explicit.

**Information lost if applied.** PPiase occupancy and hydrolysis delay would be lost. Any model that hides Pi production fails the resource requirement. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000404`, `re0000000405`, `re0000000406`, `re0000000407`, `re0000000408`, `re0000000409`, `re0000000410`, `re0000000411`, `re0000000412`, `re0000000413`, `re0000000414`, `re0000000415`.

Candidate complex/intermediate IDs: `PPiase_PPi`, `PPiase_PO4`, `PPiase_PO4_PO4`.

</details>

## Shared small-molecule transitions

**Chemical process.** The source subsystem records small-molecule reactions shared with other process modules.

**Original implementation.** 12 unique combined reactions map to `SmallMolecules.xml`. Exact combined IDs are below; original module-local IDs are in the decision CSV.

**Intermediates.** 0 candidate complex states participate across these module files. Their source IDs are listed below; classification from IDs is provisional.

**Explicit free resources.** Event-level changes occur for: `ATP`, `ADP`, `AMP`, `GTP`, `GDP`, `GMP`, `PO4`, `PPi`. Bound resource moieties, amino-acid incorporation and tRNA recycling must be checked against the full reactant/product JSON, not inferred from this free-species summary.

**Particle number.** Among these event stoichiometries, 6 increase, 6 decrease and 0 leave unchanged the represented-species particle count. This does not weight events by flux or establish osmotic pressure. ATP/GTP and PPi/Pi importance is indicated by the explicit free-resource list, with bound contributions unresolved.

**Representative original reactions.**

- `re0000000784`: `ATP → ADP + PO4`; tracked-particle Δ = 1.
- `re0000000785`: `ADP → AMP + PO4`; tracked-particle Δ = 1.

**Candidate lumping.** A shared bookkeeping representation might avoid duplicate display edges, but chemical events must retain one unique combined-SBML ID.

**Information lost if applied.** Any deletion would risk free-resource, phosphate and particle accounting; shared display membership is not duplicate chemistry. Any free-resource, tRNA, moiety or particle delta hidden by a proposed aggregate must reappear explicitly in its reduced reaction or in a validated reconstruction. Formula/charge gaps currently block quantitative ionic-strength consequences.

**Evidence needed.** Compare trajectories and microscopic fluxes of the relevant intermediates over proposed conditions; derive conserved pools and resource/moiety identities; test effective rate laws and time-scale separation; review temperature, units, charge/protonation and Mg binding where ionic claims are sought. No QSSA or chemostat is accepted from the current parameter table alone.

**Researcher choice (`HUMAN_REVIEW_REQUIRED`):**

- [ ] KEEP
- [ ] LUMP
- [ ] QSSA
- [ ] CHEMOSTAT
- [ ] DROP
- [ ] NEED MORE INFORMATION

<details><summary>All original combined reaction IDs and intermediate IDs for this process</summary>

Original combined reaction IDs: `re0000000784`, `re0000000785`, `re0000000786`, `re0000000787`, `re0000000788`, `re0000000789`, `re0000000790`, `re0000000791`, `re0000000792`, `re0000000793`, `re0000000794`, `re0000000795`.

Candidate complex/intermediate IDs: none classified.

</details>

## Review decision record

For every approved transformation, create a versioned decision that cites original combined IDs, source/module IDs, exact equations, assumptions, domain, species/observable reconstruction rules, ATP/GTP/Pi/PPi/AMP/ADP/GDP/tRNA balances, particle and ionic coverage, numerical evidence and researcher/date. Until then `PURE_reduced_core` remains a proposal.
