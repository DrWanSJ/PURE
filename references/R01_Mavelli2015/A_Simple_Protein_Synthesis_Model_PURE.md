<!-- page 1 -->
Bull Math Biol <u>DOI 10.1007/s11538-015-0082-8</u> ORIGINAL ARTICLE

# A Simple Protein Synthesis Model for the PURE System Operation

## Fabio Mavelli

**1** **· Roberto Marangoni** **2***,***3** **·** **Pasquale Stano** **4**

Received: 7 August 2014 / Accepted: 7 April 2015 © Society for Mathematical Biology 2015

**Abstract** The encapsulation of transcription–translation (TX–TL) cell-free machin- ery inside lipid vesicles (liposomes) is a key element in synthetic cell technology. The PURE system is a TX–TL kit composed of well-characterized parts, whose concen- trations are fine tunable, which works according to a modular architecture. For these reasons, the PURE system perfectly fulfils the requirements of synthetic biology and is widely used for constructing synthetic cells. In this work, we present a simplified mathematical model to simulate the PURE system operations. Based on Michaelis–Menten kinetics and differential equations, the model describes protein synthesis dynamics by using 9 chemical species, 6 reactions and 16 kinetic parameters. The model correctly predicts the time course for messenger RNA and protein production and allows quan- titative predictions. By means of this model, it is possible to foresee how the PURE system species affect the mechanism of proteins synthesis and therefore help in under- standing scenarios where the concentration of the PURE system components has been modified purposely or as a result of stochastic fluctuations (for example after random encapsulation inside vesicles). The model also makes the determination of response coefficients for all species involved in the TX–TL mechanism possible and allows for

B Pasquale Stano pasquale.stano@uniroma3.it Fabio Mavelli fabio.mavelli@uniba.it Roberto Marangoni roberto.marangoni@unipi.it

1 Chemistry Department, University of Bari, Via Orabona 4, Bari, Italy 2 Biology Department, University of Pisa, Via Derna 1, Pisa, Italy 3 CNR-Institute of Biophysics, Via G. Moruzzi 1, Pisa, Italy 4 Science Department, Roma Tre University, Viale G. Marconi 446, Rome, Italy

<!-- page 2 -->
F. Mavelli et al.
scrutiny on how chemical energy is consumed by the three PURE system modules (transcription, translation and aminoacylation).

**Keywords** PURE system · Cell-free transcription–translation (TX–TL) · Synthetic biology · Synthetic cells

# 1 Introduction

Synthetic biology deals with the construction of biological parts, devices and systems that do not exist in nature and that can perform well-defined and useful functions; it is often based on mathematical tools for their modeling (Endy 2005). The classical synthetic biology approach is based on the manipulation of living organisms (generally bacteria) in order to study, control and redesign biological patterns and also to produce microorganisms that are capable of synthesizing fuels, specialized drugs, or particular compounds to be used in the chemical or pharmaceutical industry (Seo et al. 2013). In addition to this research, cell-free synthetic biology (Harris and Jewett 2012; Hodgman and Jewett 2012; Zhao 2013) and among the various approaches, the “bottom-up” construction of synthetic cells which starts from separated molecules (lipids, DNA, RNA, proteins, etc.) is attracting the interest of an increasing number of researchers. In particular, the so-called *semisynthetic* approach (Luisi et al. 2006) consists of the introduction of the minimal number of molecules inside lipid vesicles in order to reconstruct living-like systems of minimal complexity, in particular for cellular self-maintenance, self-reproduction and possibility to evolve (Fig. 1a).

**Fig. 1** (Color Figure Online)**a** Semisynthetic minimal cells are composed of the minimal number of genes,

enzymes, ribosomes, tRNAs and low molecular weight compounds that are encapsulated within a synthetic compartment as in the case of lipid vesicles. The resulting construct, which is similar to a living cells and displays minimal living properties (self-maintenance, self-reproduction and possibility to evolve), is generally designed on the basis of the minimal number of functions required and of the minimal complexity of the elements needed for its construction. Reproduced from Chiarabelli et al. (2009), with permission from Elsevier. (**b**) Confocal microscopy images of giant liposomes producing the enhanced green fluorescent protein (eGFP); reproduced from Rampioni et al. (2014), with permission from Springer

<!-- page 3 -->
A Simple Protein Synthesis Model for the PURE System*...*

Semisynthetic minimal cells (in short: synthetic cells) are attractive for several reasons. First and foremost they are a model of primitive cells, and therefore, their construction sheds light on the mechanisms for the origin of life, allowing the under- standing of the physical and chemical factors that shaped the early cells. It should be remarked, however, that primitive cells containing sophisticated multimolecular systems, such as a transcription–translation machinery, were clearly preceded by sim- pler cell-like structures with lower compositional and functional complexity. Second, synthetic cells can help us to understand biological mechanisms by a constructive approach. This is feasible if a certain phenomenology can be reconstructed by means of synthetic cells with a minimal number of components, eliminating in this way the “interference” with the other background processes that occurs in living cells (Liu and Fletcher 2009). Third, synthetic cell technology could soon become so advanced as to make possible the design and the construction of systems for biotechnological applications, for example, in the fields of nanomedicine (LeDuc et al. 2007), or bio- chem-information technologies (Nakano et al. 2011; Stano et al. 2012). This is made possible thanks to peculiar features of synthetic cells: modularity, orthogonality and programmability of their internal molecular devices. Currently, synthetic cell technology is founded on the convergence of liposome technology and cell-free systems, in particular on cell-free protein synthesis. In this respect, the encapsulation of in vitro transcription/translation (TX–TL) machinery inside liposomes has played a central role in the development of the field in the last 15 years, as reviewed in Stano et al. (2011). Together with *Escherichia coli* extracts, the PURE system became very popular in the last few years (Murtas et al. 2007; Kuruma et al. 2009; Nishimura et al. 2012). The PURE system, which stands for protein synthesis using recombinant elements, was introduced in 2001 by the Ueda group (Shimizu et al. 2001, 2005), and it is now considered to be a standard cell-free system for constructing synthetic cells in the laboratory. It fits perfectly with the philosophy of biological standard parts (parts.igem.org). The PURE system includes the minimal number of molecules for producing a protein starting from a DNA sequence (35 purified enzymes, most from *E. coli*, the bacteriophage T7 RNA polymerase,

*E. coli*ribosomes and a tRNAs mixture—as well as low molecular weight compounds— for a total of about 80 macromolecules). It can be introduced inside liposomes with the aim of producing proteins and therefore endows synthetic cells with protein-embodied function (enzymes, receptors, transcriptional regulators, cytoskeletal elements, etc.) (Stano et al. 2011; Niwa et al. 2012; Stano and Luisi 2013; van Nies et al. 1963; Jewett et al. 2013; Soga et al. 2014; Matsubayashi and Ueda 2014; Matsubayashi et al. 2014; Kazuta et al. 2014). The PURE system is a commercial product that is sold with all components mixed together. In principle, however, the PURE system can be assem- bled in any laboratory starting from separated parts, which are specified in the original publications (Shimizu et al. 2001, 2005). It is then possible to vary the PURE system components to explore how protein synthesis is affected by the concentration of each individual species (Shimizu et al. 2001; Matsuura et al. 2009; Kazuta et al. 2014). In addition to the characterization and assembly of parts, the bioengineer- ing approach which characterizes synthetic biology makes use of mathematical modeling to support operations such as design, implementation and experimental test- ing/validation. To date, however, the application of mathematical model to the field

<!-- page 4 -->
F. Mavelli et al.
of synthetic cells and, in particular to TX–TL systems, has only been marginal. In particular, we and others have only very recently started to face this issue, by adopting different approaches of very different complexity, from basic coarse-grained models (Sunami et al. 2010; Karzbrun et al. 2011; Stögbauer et al. 2012) to more detailed and stochastic ones (Frazier et al. 2009; Lazzerini-Ospri et al. 2012; Calviello et al. 2013). In this paper, we present a non-stochastic model for TX–TL systems that has been specifically designed to be a companion for experiments carried out with the PURE system kit, providing a simple tool for the mathematical modeling of protein synthe- sis. This is a model that has been primarily designed for conditions where intrinsic stochastic effects—those due to small number of molecules—are negligible. With- out neglecting the importance (and the accuracy) of stochastic models, especially for micro-compartmentalized reactions such as those of interest in synthetic cell research (Mavelli et al. 2014), our model has the advantage of being simple and nevertheless able to capture most of the essential aspects of TX–TL reactions. In particular, the model mirrors the four PURE system modules (Shimizu et al. 2005), namely transcription, translation, amino acid–tRNA charging and energy regeneration. We are aimed at designing a model able to describe the macroscopic, measurable output of PURE system, on the bases of its most important, controllable variables, avoiding a finer detailed level, where most of the reactions kinetic or thermodynamic constants are unknown (or not measurable) and not controllable.

# 2 A Simplified PURE System Mechanism

Figure 2 schematically shows the set of PURE system reactions. These are as fol-

lows: (*i*) transcription (TX); (*ii*) translation (TL); (*iii*) aminoacylation; and (*iv*) energy regeneration. Each one actually comprises several steps. In transcription, RNA polymerase catalyses the conversion of nucleotides (ATP, GTP, CTP, UTP) to messenger RNA (mRNA), based on DNA as template. Ribosomes catalyze the polymerization of aminoacyl moieties in aminoacyl tRNA to give proteins, based on mRNA as template (translation). Translation is a complex multi-step reaction where several other PURE system components are involved (initiation, elon- gation and release factors, as well as others proteins), and it consumes energy (GTP). Aminoacylation actually is a set of reactions, each catalyzed by a aminoacyl-tRNA synthase, consisting of joining 20 amino acids and 46 transfer RNAs (tRNAs) (Dong et al. 1996; Pereira de Souza et al. 2009), with the consumption of ATP. Note that despite the 64 codons of the genetic code, only 46 tRNAs are required in *E. coli* to accomplish translation (Dong et al. 1996). The energy regeneration module, consisting of three enzymes, uses creatine phosphate (present in large excess) as ultimate phosphate donor to regenerate nucleosides triphosphate and in particular the important ATP and GTP. In addition to their consumption in the transcription reaction (nucleoside triphosphates are converted to mRNA) and in initiation/termination translation steps, one ATP and two GTP molecules are needed for each amino acid incorporated in the growing protein chain, and therefore, the number of consumed ATP/GTP molecules scales as *L*, the protein length (see Sect. 5). The full list of PURE system components

<!-- page 5 -->
A Simple Protein Synthesis Model for the PURE System*...*

**Fig. 2** The four main reactions (“modules”) of protein synthesis in the PURE system. Reproduced from

Shimizu et al. (2005), with permission from Elsevier

and a comment on their function can be found in Shimizu et al. (2001), Shimizu et al. (2005). A detailed model of the PURE system operation is necessarily a very complex one, both for the high number of reactions and for the dynamics of polymerization processes (TX–TL) (think for example to the complexity of polysome modeling). Moreover, the limited knowledge of all kinetic and thermodynamic constants of every mechanistic step is a further critical point that makes difficult the formulation of a detailed model. On the other hand, a simplified model of the PURE system, based on a few kinetic stages that actually capture the essence of the four modules of Fig. 2, would be quite useful for those studies aimed at combining in vitro and in silico studies on bulk and micro-compartmentalized TX–TL systems. Our model is mainly based on four kinetic enzymatic stages assumed to be all in a stationary state, and therefore, the calculation of the enzyme-catalyzed rates *V* will have a Michaelis–Menten form, as also reported by Frazier et al. (2009), namely:

<u>[S1] [S2]</u> *V* = *k* · *C*cat··· (1) *KM,*1+[S1] *KM,*2+[S2]

where *k* is the apparent turnover number (in s −1 ) and *C*catand [S*i*] are the constant concentration of a catalyst and the time-dependent concentration of the*i*th substrate (in µM), while *KM,i*is the corresponding apparent Michaelis–Menten constant (in µM). For TX and TL reactions, which require a template (DNA and mRNA, respectively), the reaction rates have been written as modulated by the template with the same functional dependence of substrates. Our simplified approach neglects the dynamics of pre-stationary phases which are supposed to be very fast compared to the overall kinetics time, but it takes into account

<!-- page 6 -->
F. Mavelli et al.
the dependency of rate from catalyst, substrate and template concentrations. In particular, the rates reach saturation values at high substrate or template concentrations (rectangular hyperbolic dependence), whereas they will increase linearly as the concentration of the catalyst increases. Such a choice is a compromise deriving from our original intent of providing a model with a limited number of parameters. Neverthe- less, this approach will allow for the description of PURE system operations with an acceptable degree of accuracy. Another critical issue is the multiplicity of nucleotides (NTP), amino acids (A) and tRNAs (T). Here, we have adopted the strategy of describing the time evolution of these species in terms of *their average concentration*, which will be used in kinetic Eq.

(1) to calculate the rates, when these species are involved as substrates *Si*. Multiplicity coefficients have been then introduced in order to take into account the overall concentrations of these species and to fulfill the mass balance equations. In particular, we will indicate by *n*NTP= 4, *n*A= 20 and *n*T= 46 the number of different molecules of these three classes of compounds, respectively.
## 2.1 Transcription (TX)

Transcription is the polymerization of nucleosides triphosphates (ATP, GTP, CTP, UTP) to give mRNA. In the PURE system, T7 RNA polymerase is used as RNA polymerase. It recognizes and binds to the T7 promoter region upstream to the DNA starting codon and polymerizes the nucleoside triphosphates by forming new phosphodiester bonds. Here, we have modeled transcription as a polymerization reaction that transforms a generic nucleotide triphosphate (NTP) into a polimerized nucleotide (nt), releasing pyrophosphate *(*PP*i)* which is in turn hydrolyzed by pyrophosphatase (PPase) to inor- ganic phosphate *(*P*i)*. Actually, it is this final hydrolysis step that, from the energetic viewpoint, drives transcription. The reaction proceeds under catalysis from TXcat (RNA polymerase), and its rate depends on the concentration of the DNA template.

TXcat NTP −→ nt + PP*i*(2) DNA

PPase PP*i*−−−→2P*i*(3) nt −→ degradation (4)

Note that by nt, here we mean the concentration of polymerized nucleotides, not of mRNA molecules. Reaction (2) refers to the rate of nucleotide incorporation in the growing RNA chain. We have also added a degradation reaction that reduces the concentration of polymerized nucleotides (i.e., mRNA), as also reported by Karzbrun et al. (2011), Stögbauer et al. (2012). In this simplified model, we do not consider the rate of reaction 3, because PP*i*and P*i*do not affect explicitly any other reactions. Moreover, together with EN reaction (which is included for energy balance reasons), the pyrophosphate hydrolysis is much faster than the other steps.

<!-- page 7 -->
A Simple Protein Synthesis Model for the PURE System*...*

According to Eq. (1), the rate of stage (2)is: ()() <u>CDNA[NTP]</u> *V*TX= *k*TX*C*TXcat(5) *K*TX*,*DNA+ *C*DNA*K*TX*,*NTP+[NTP]

where *k*TXzis the transcription constant (polymerized nucleotides/s); *C*TXcatis the T7 RNA polymerase concentration; *C*DNAis the DNA concentration (or, more precisely, of the promoter region); *K*TX*,*DNAand *K*TX*,*NTPcorrespond to the apparent Michaelis– Menten constants for DNA and NTP interactions with TXcat, respectively. Note that Eq. 5 refers to the steady rate of the mRNA elongation. The rate of mRNA decay Eq. (4) is instead assumed as simply proportional to the total concentration of polymerized nucleotides nt:

*V*nt*,*deg= *k*nt*,*deg[*nt*] (6)

where *k*nt*,*degis the pseudo-first-order decay constant [this functional dependence has been demonstrated experimentally, see Yarchuk et al. (1992), Karzbrun et al. (2011), Siegal-Gaskins et al. (2014)].

## 2.2 tRNA Aminoacylation (RS)

Aminoacylation consists of charging tRNAs (T) with amino acids (A), to give the corresponding aminoacyl tRNA (AT), which is the activated form of amino acid, capable of being recognized and polymerized during the TL reaction. PURE system contains 20 aminoacyl-tRNA synthases (RSs), which function by consuming ATP (AMP and PP*i*is produced). *E. coli* contains 46 tRNAs [required to recognize all codons in the mRNA (Dong et al. 1996)], in different amounts. Here, we have modeled this set of reactions by using a single generic amino acid and a single tRNA species, in a reaction catalyzed by a generic synthase (RScat). Energy is provided by a generic NTP, which is converted to generic exhausted nucleotide species NXP.

RScat A+T+ NTP−−−→AT + NXP (7)

For stoichiometric reasons (simplifying mass balance equations, see Sect. 2.5), in order to take into account the amino acids and tRNAs multiplicity, it is useful to introduce the factor *n*T/*n*A= 46/20 = 2.3 representing the average number of tRNAs per amino acid and therefore to the multiplicity of AT species. Note that [A] and [T] refer to the average amino acid and tRNAs concentrations in the PURE system, respectively. The rate of reaction (7) is therefore given by: ()()() [A] 2*.*3[T] [NTP] *V*RS= *k*RS*C*RScat(8) *K*RS*,*A+[A] *K*RS*,*T+ 2*.*3[T] *K*RS*,*NTP+[NTP]

where *k*RSis the apparent tRNA aminoacylation rate constant (s −1 ), *C*RScatis the average concentration of RSs enzymes in the PURE system, and *K*RS*,*T, *K*RS*,*Aand

<!-- page 8 -->
F. Mavelli et al.
*K*RS*,*NTPcorrespond to the average apparent Michaelis–Menten for amino acids, tRNA and NTP interactions with RScat, respectively. It is important to remark that our model does not take into account the amino acid composition of the target protein. In principle, our model can be expanded by adopting the approach proposed by Frazier and collaborators (Frazier et al. 2009), who explicitly took into account the different mRNA codons, tRNAs and RSs.

## 2.3 Translation (TL)

Translation is the polymerization of amino acids (delivered as aminoacyl tRNAs, AT) to give proteins. In the PURE system, in addition to ribosomes, all elements of the TL machinery are present (ten translation factors plus methionyl-tRNA transformylase). In addition to the energy spent in the initiation of translation and in the release of protein, each elongation step proceeds by using two GTP molecules per each new formed peptide bonds (GDP + P*i*are formed). Here, we have modeled translation as a polymerization reaction that transforms a generic aminoacyl tRNA (AT) into a polimerized amino acid (*a*), and therefore, it stands for the rate of protein elongation. Note that *a* does not represent the protein concentration. Free tRNA (T) is also released. Two NTP molecules are consumed, and two exhausted nucleotides NXP are formed (it is convenient to pool all exhausted nucleotide species NDP and NMP in the form of NXP, see Sect. 2.4). The elongation reaction is catalyzed by ribosomes and translation factors (see Fig. 2) which have been collectively represented by a fictitious species TLcat [as already proposed in Stögbauer et al. (2012)]. This drastic simplification is functional for developing a model based on few reaction steps. The reaction rate also depends on the concentration of the mRNA template, here represented by the nt species.

TLcat AT + 2NTP −→ *a* +T+ 2NXP (9) nt

By following Eq. (1) and keeping in mind the A and T multiplicities and the *n*T/*n*A factor (see Sect. 2.2), the rate of the translation stage (9) can be written as:

()()() [nt] 2*.*3[AT] [NTP] *V*TL= *k*TL[TLcat] *K*TL*,*nt+[nt] *K*TL*,*AT+ 2*.*3[AT] *K*TL*,*NTP+[NTP] (10)

where*k*TLis the apparent translation rate constant (polymerized aminoacyl residues/s), [TLcat] is the concentration of a fictitious species that represent the TL machinery, and *K*TL*,*nt, *K*TL*,*NTPand *K*TL*,*ATcorrespond to the apparent Michaelis–Menten constants for nt (i.e., mRNA), NTP and AT interactions with TLcat, respectively. Moreover, according to Sunami et al. (2010) and Stögbauer et al. (2012), the effi- ciency of translation in PURE system is limited by the lifetime of the TL apparatus. It has been shown that after reaching a plateau in protein production, if fresh ribosomes were added to PURE system, the protein synthesis could start again (Stögbauer et al.

<!-- page 9 -->
A Simple Protein Synthesis Model for the PURE System*...*

2012). As in previous reports, then we have introduced a decay process that consumes TLcat:
## TLcat −→ degradation (11)

and we model this degradation as a first-order decay:

*V*TL*,*deg= *k*TL*,*deg[TLcat] (12)

being *k*TL*,*degthe pseudo-first-order decay constant of TL machinery. Finally, it should be noted that even if two NTPs are consumed for each elongation step, a rectangular hyperbolic function has been used to describe the contribution of 2 NTPs to the rate Eq. (10), neglecting second-order contributions (e.g., [NTP])tothe stage rate. The present TL model is general and can be applied to proteins that are functional just after their synthesis, without posttranslation modifications or without the need of any maturation step. The GFP—which will be used here as a case study—does require a maturation step (i.e., cyclo-oxidation). As will be shown below, however, we have not included this reaction because of its characteristic short time [reported to be around 5 min (Stögbauer et al. 2012)].

## 2.4 Energy Regeneration (EN)

The PURE system contains three enzymes for energy regeneration, namely adenylate kinase, nucleoside-diphosphate kinase and creatine kinase. The combined action of these enzymes leads to the regeneration of NTPs at the expense of creatine phosphate (CP), the ultimate phosphate donor. In order to model this set of reactions, we have first pooled all exhausted nucleotides (NMP, NDP), generated by the other steps in a single-species NXP that is reconverted to NTP, while CP dephosphorilates to give creatine (C).

ENcat CP + NXP −−−→ C + NTP (13)

As in previous cases, ENcat represents an hypothetical enzyme that works as the whole energy regeneration machinery. The rate of Eq. (13)is

()() <u>[CP] [NXP]</u> *V*EN= *k*EN*C*ENcat(14) *K*EN*,*CP+[CP] *K*EN*,*NXP+[NXP]

where *k*ENis the apparent rate constant for the overall energy regeneration machinery −1

(s), *C*ENcatis the concentration of a fictitious energy recycling enzyme, and *K*EN*,*CP and *K*EN*,*NXPare the apparent Michaelis–Menten constant for the interaction of CP and NXP with the catalyst ENcat.

<!-- page 10 -->
F. Mavelli et al.
**Fig. 3** General view of the model presented here. The four modules (TX, TL, RS, EN) are interconnected

by means of reactants, templates, and energyzing molecules. In *bold*, the molecules initially present in the PURE system. NTP, nucleoside triphosphate; nt, polymerized nucleotides (mRNA); AT, aminoacyl tRNA; A, amino acid; T, tRNA; *a*, polymerized amino acid (protein); NXP, nucleoside mono- or diphosphate; CP, creatine phosphate; C, creatine; TXcat, TLcat, RScat, ENcat represent, respectively, the catalysts (or the set of catalysts) for transcription, translation, aminoacyl-tRNA synthesis, and energy recycling. *Dashed lines* templating interaction; *thick solid lines* the reactions

## 2.5 The Overall Model

To summarize, this simplified PURE system model consists of four kinetic complex stages (TX, TL, RS, EN) (Eqs. 5, 8, 10, 14), and two decay reactions (Eqs. 4, 11), as discussed in the previous sections. The general scheme is given in Fig. 3. The model includes:

– nine initially present species: one template (DNA), four substrates (A, T, NTP, CP) and four catalysts (TXcat, TLcat, RScat, ENcat); – five mass conservation equations (based on the initial concentrations of A, T, NTP, CP and TLcat) (Eqs. 15–19) – eight additional species that are created by the model: nt, PP*i*,AT,*a*, C, a generic NXP species (representing the pool of AMP and NDPs), and two generic degradation products (one from nt, an the other from TLcat); – six kinetic rate constants and ten Michaelis–Menten constants.

The mass balance equations (Eqs. 15–19) are written by taking into account the NTP, A and T multiplicities (*n*NTP=4,*n*A= 20 and *n*T= 46), which have been introduced to simplify the stoichiometric and kinetic treatments.

*n*NTP*C*NTP 0 = *n*NTP[NTP]+[*nt*]+[NXP]+degradation species (15) *n*A*C*A 0 = *n*A[A]+[*a*]+*n*T[AT] (16) *n*T*C*T= *n*T[T]+*n*T[AT] (17) *C*CP=[CP]+[C] (18) *C*TLcat=[TLcat]+degradation species (19)

<!-- page 11 -->
A Simple Protein Synthesis Model for the PURE System*...*

0 where the *C* values are the initial concentrations of the indicated species. Note also that [NTP] refers to an average nucleoside triphosphate concentration and that the overall NTP concentration is obtained after multiplication by *n*NTP, whereas the concentration of the other derived species (nt, NXP and the decay product) refers to the overall values. Similar considerations apply to amino acids (A) and tRNAs (T). The ordinary differential equation set that describes the PURE system reactions can be easily written by considering the stoichiometry of the four kinetic stages and the two decay processes and by taking into account the multiplicity coefficients *n*NTP, *n*A, and *n*T, as it follows:

<u>d[NTP] −VTX− 2VTL− VRS+ VEN</u> = (20) d*t n*NTP <u>d[NXP]</u> = 2*V*TL+ *V*RS− *V*EN(21) d*t* <u>d[nt]</u> = *V*TX− *V*nt*,*deg(22) d*t* <u>d[A] VRS</u> =− (23) d*t n*A d[T] d[AT] −*V*RS+ *VTL* =− = (24) d*t* d*t n*T <u>d[a]</u> = *V*TL(25) d*t* <u>d[CP] d[C]</u> − = = *VEN* (26) d*t* d*t* <u>d[TLcat]</u> =−*V*TL*,*deg(27) d*t*

where only the main species are shown. Please note that NTP and NXP rates scale differently due to the different definition of [NTP] (average concentration) and [NXP] (overall concentration)—see above. As specified in Sects. 2.1 and 2.3, the species nt and *a* represent, in this model, the overall polymerized nucleotides and amino acids, respectively. This choice is convenient because it helps to define the rates of stages 2 and 9 in clear manner (i.e., as the rates of nucleotide and amino acid polymeriza- tion, respectively). The disadvantage is that the concentration of mRNA and protein molecules are not explicit. Moreover, the kinetic parameter *K*TL*,*ntis not intuitively linked to any physical processes. It is possible to transform the “nt and *a*” model into a “mRNA and protein” one by simply substituting: [mRNA] = [nt]/3*L*, and [protein] =[*a*]/*L* (*L* is the length of protein). Moreover, it follows that:

*k*RNA*,*deg= *k*nt*,*deg(28) <u>KTL,nt</u> *K*TL*,*RNA= (29) 3*L*

Note that in this study, we did not investigate the possible existence of genuine stationary states of the TX–TL reactions, because we deal with a closed system, and

<!-- page 12 -->
F. Mavelli et al.
the resources are depleted over time. Such states could appear in open systems, where the TX–TL machinery is constantly fed with freshly added substrates.

# 3 Simulation Results

In order to integrate the set of differential equations describing the PURE system kinetics, we have used whenever possible kinetic constants taken from the literature, via databases searching (Brenda: brenda-enzymes.org, and B10NUMB3R5: bionumbers.hms.harvard.edu), while values of the initial concentrations have been taken from the PURE system standard composition (Shimizu et al. 2005). Since our simple model reactions actually summarize multiple chemical reactions (as in the TL, RS and EN stages), the concentrations of enzymes and substrates, as well as the value of kinetic constants, have been estimated as arithmetic or geometric averages of the available data. The concentration values and the kinetic parameters used in the computer calcula- tions are reported in Tables 1 and 2, respectively. The initial concentration of chemical species was taken from the known PURE system composition, except for the fictitious species TLcat that is a virtual TL catalyst, functioning as ribosomes and translation factors. Initial values of kinetic constants were mostly taken from the databases and optimized afterward. In particular, TX parameters referred to T7 RNA polymerase; TL parameters to *E. coli* ribosomes; RS (average) parameters to the 20 aminoacyl-tRNA synthases (RSs) from *E. coli*; and EN parameters to creatine kinase. By comparing the values of some PURE system species concentrations (Table 1) and the *KM* (average) values found in BRENDA databases (Table 2), it is evident that some Michaelis–Menten factors, i.e., [S*i*]*/(KM,i*+[S*i*]*)*will not play an essential role in kinetics, being in most cases *KM,i<<* [S*i*]. Nevertheless, we decided to include these terms in the rate equations because we are primarily interested in designing a general model where the four PURE system modules are explicitly represented. This

**Table 1** Initial concentrations of DNA template, catalysts, and substrates

|Species|Concentration (µM)|Ref.|
|---|---|---|
|DNA|from 0.34 to 6.8 10−3|Dataset from Stögbauer et al. (2012)|
|TXcat|0.1|PURE system|
|TLcat|2.2 ± 0.3|Fitting|
|RScat|0.16|PURE system (avg.)|
|ENcat|0.08|PURE system (avg.)|
|A|300|PURE system (×20 species)|
|T|1.9|PURE system (×46 species Dong et al. (1996), Pereira de Souza et al. (2009), avg.)|
|NTP|1500|PURE system (×4 species, avg.)|
|CP|20,000|PURE system|

<!-- page 13 -->
A Simple Protein Synthesis Model for the PURE System*...*

**Table 2** Values of kinetic parameters used in the model

|Constant|Value|( s−1|)|Value|( µM|)|Ref.|
|---|---|---|---|---|---|---|---|
|k TX|1.67 ± 0.14||||||Fitting|
|k TL|0.085 ± 0.020||||||Fitting|
|k RS|6.2||||||Brenda (avg.)|
|k EN|100||||||Brenda (EC 2.7.2.3)|
|k nt, deg|7.92 ± 0.51 10−5||||||Fitting|
|k TL, deg|1.86 ± 0.11 10−4||||||Fitting|
|K TX, DNA||||5.00 ± 0.75 10−3|||Fitting|
|K TX, NTP||||80|||Brenda (EC 2.7.7.6)|
|K TL, nt||||226 ± 16|||Fitting|
|K TL, RNA||||0.32 ± 0.02|||Fitting|
|K TL, AT||||10|||Estimated|
|K TL, NTP||||10|||Estimated|
|K RS, A||||23|||Brenda (avg.)|
|K RS, T||||0.7|||Brenda (avg.)|
|K RS, NTP||||200|||Brenda (avg.)|
|K EN, CP||||200|||Brenda (EC 2.7.2.3)|
|K EN, NXP||||40|||Brenda (EC 2.7.2.3)|

will allow us to scan the concentration ranges of the PURE system components in order to test the yield and the efficiency of the protein production (see Sect. 4). First, we optimized some kinetic parameters by a fitting procedure. The six experi- mentally determined [mRNA] versus time and [protein] versus time curves reported in Stögbauer et al. (2012) were simultaneously fitted in order to obtain the best estimates of the rate constants *k*TX, *k*TL, *k*nt*,*deg, *k*TL*,*deg, of the Michaelis–Menten constants *K*TX*,*DNA, *K*TL*,*ntand of the initial concentration of the fictitious species TLcat. The values obtained by our fitting procedure satisfactory agree with the values reported in Stögbauer et al. (2012). The experimental dataset refers to the synthesis of the green fluorescent protein (GFP, 238 amino acids long) by the PURE system, starting from three different DNA concentration (6.8, 1.7, 0.34 nM). The comparison between the experimental and calculated curves is shown in Fig. 4, showing that the model reproduces the three transcription curves ([nt] versus time) quite well, whereas the fit is not completely satisfactory for the translation ones ([*a*] versus time), although a sigmoidal time course is correctly obtained. Such a divergence could be due to oversimplifications introduced in the model, especially with respect to the TL mechanism, but it could also be due to the limited amount of data available for the fitting procedure. Empirically, the set of [*a*] versus time curves can be fitted slightly better by intro- ducing a Hill factor in Eq. 10, in particular [nt] *v* /(*K* TL *v* *,*nt +[nt] *v* ), with*v* = 3*.*465 (data not shown). We did not introduce this empirical term in the present model because the available experimental data prevent its correct evaluation and validation, and therefore, we will postpone this analysis to future experimental/theoretical work.

<!-- page 14 -->
F. Mavelli et al.
**Fig. 4** Fitting of experimental data. Experimental (*dotted lines*) and calculated (*continuous lines*) time

profiles of mRNA synthesis (*top*) and protein synthesis (*bottom*), at three different DNA concentrations,

i.e., 0.34 (*blue*), 1.7 (*green*) and 6.8 nM (*red*). Note that the mRNA and protein concentrations are given in terms of polymerized nucleotides [nt] and amino acids [*a*], respectively (the actual concentrations can be calculated by dividing the values in the *y*-axes by 3*L* and *L*, respectively. *L* = 238). Data have been obtained by digitalization of published *curves* (Stögbauer et al. 2012) (Color figure online) Despite these limitations, our model reproduces the essence of a TX–TL mechanism as well as the ones proposed in Karzbrun et al. (2011), Stögbauer et al. (2012), but moreover it introduces explicitly the modules of energy regeneration (EN) and tRNA aminoacylation (RS), and therefore, it can be used to explore the behavior of PURE system in several different experimental conditions.
# 4 Simulating the Behavior of Hypothetical PURE Systems of Different Compositions

The main reasons for modeling the PURE system reactions have to do with their use for producing proteins inside lipid vesicles. Generally, lipid vesicles form spontaneously,

<!-- page 15 -->
A Simple Protein Synthesis Model for the PURE System*...*

in a variety of ways, simply by hydrating lipids with an aqueous buffer. The solutes present in the solution have the chance to be encapsulated inside vesicles. In typical experiments, lipid vesicles are assembled by using the PURE system as hydrating solution (including DNA), so that the entire TX–TL machinery can be found inside vesicles. Consequently, the protein encoded in the DNA sequence is produced inside liposomes, as shown, for example, in Fig. 1b, where the enhanced GFP (eGFP) was used as reporter protein. Due to the low concentration of the PURE system macromole- cules (typically*<* 1µM) and the small vesicle size, stochastic effects play a major role in determining the individual content of each vesicle. We will provide some numerical examples in Sect. 6. In other words, following a unique path of vesicle formation and solutes encapsu- lation, each vesicle has a unique internal reaction mixture, which will differ from any other vesicle in terms of the number of encapsulated molecules. In turn this means that at the level of vesicle population, a potentially large heterogeneity is observed in terms of rate and amount of protein produced. This “diversity” (Stano et al. 2015) originates stochastically from local microscopic pathways, and it is one of the several intriguing emerging properties of micro-compartmentalized systems (Walde et al. 2014). Detailed accounts of the determination of the solute contents of each vesicles of various size, and prepared with different methods, are still under investigation, but experimental results suggest that such an aspect of compartmentalized reactions is worth studying (van Nies et al. 1963; Pereira de Souza et al. 2009, 2011; Sun and Chiu 2005; Dominak and Keating 2007; Lohse et al. 2008; Saito et al. 2009; Luisi et al. 2010; Kato et al. 2012; Stano et al. 2013). In fact, it is known that both in giant lipid vesicles (diameter *>* 1 µm) (Sun and Chiu 2005; Dominak and Keating 2007) and in conventional vesicles (diameter *<* 1µm) (Lohse et al. 2008), the concentration of encapsulated solutes varies from vesicle to vesicle. Recent studies by Luisi’s group have also shown a peculiar super-concentration phenomenon that leads to the formation of solute-filled vesicles even when starting from diluted solutions (Luisi et al. 2010; Stano et al. 2013). Here we would like to explore the effects of compositional diversity on the TX–TL reactions by analyzing the performance of hypothetical PURE system kits whereby the concentration of the components has been increased or decreased by a factor *F* (*F* = actual concentration/standard concentration, and the standard concentrations correspond to the values reported in Table 1, and [DNA] = 6.8 nM). Instead of using the *F* factors for each chemical species, we will change the concentration of the groups of species, as indicated in Table 3. The “DNA” group includes only DNA, “E” group includes the four catalysts (TXcat, TLcat, RScat, ENcat), and the “B” group includes tRNAs and all low molecular weight compounds. Accordingly, a certain PURE system composition will be indicated by the notation [*F*DNA*F*E*F*B], referring, respectively, to the *F* factors for DNA, group “E” components and group “B” components. We will change the *F* values at three levels (case I: 0.33, 0.67, 1.00; and case II: 0.67, 1.00, 1.33) to simulate, respectively, a PURE system whose components are diluted, or the case when the components can be diluted or concentrated. Consequently, a total of 3 × 3 × 3 = 27 different PURE system compositions are generated, and the production of a model protein (*L* = 238 amino acids) simulated by the ODEs set is shown above.

<!-- page 16 -->
F. Mavelli et al.
**Table 3** PURE system: chemical groups

|Group|PURE system components|In silico component|
|---|---|---|
|DNA|DNA|DNA|
|E|T7 RNA polymerase|TXcat|
|E|Ribosomes, ten translation factors, MTF|TLcat|
|E|20 aminoacyl-tRNA synthases|RScat|
|E|Adenylate kinase, NDP kinase, creatine kinase, PPase|ENcat|
|B|ATP, CTP, GTP, UTP|NTP|
|B|20 amino acids|A|
|B|tRNA mixture (46 species Dong et al. (1996), Pereira de Souza et al. (2009))|T|
|B|Creatine phosphate|CP|
|B|Other low MW components||

## 4.1 Case I: Diluting the PURE System Components

Firstly, we examine the case where PURE system components are just diluted. It is known that the amount of protein produced by the PURE system is a highly sensitive function of PURE system concentration (Stano et al. 2013). Here we compare the amount of produced protein after 4 h by 27 different PURE systems. Each combination formally derives from mixing DNA, group E compounds and group B compounds in a certain way. Note that this design reflects the material way in which the commercial PURE system is delivered, i.e., two vials (E and B) to which DNA is added. This means that the predictions of our simulation can be tested by experimental assays. The histograms of Fig. 5, left column, clearly indicate a common trend. By diluting DNA, E and B components, the protein yield decrease from 0.58 µM of the non-diluted [1.00 1.00 1.00] PURE system to about 0.08 µM for the most diluted case [0.33 0.33

0.33]. The concentration of DNA seems not to affect the protein synthesis too much, whereas by keeping *F*DNAconstant, the variations of groups E and B profoundly influence the protein yield. A quite evident reduction in PURE system efficiency is observed when group E concentrations are more than halved (*cf. F*E= 0.67 with *F*E=
0.33 bars). This is easily understandable because enzymes are in the E group. However, compounds of the B group also play a major role in determining the productivity, for example, when *F*DNA= *F*E= 1, a decrease in *F*Bcorresponds to an almost linear decrease in the produced protein. An interesting “turning” point is always observed along all variation series, irre- spective of the DNA concentration. This corresponds to the *decrease* of the protein yield by moving from [*F*DNA0.67 1.00] to [*F*DNA1.00 0.33]. The protein production in the case of partially diluted group E and non-diluted group B is always 35–50 % higher than the case when group E is present at its standard value, whereas group B is diluted to one-third of its standard value. We will see in Sect. 4.4 what the role of individual components is in determining this behavior.

<!-- page 17 -->
A Simple Protein Synthesis Model for the PURE System*...*

**Fig. 5** Amount of protein (*L* = 238) produced after 4 h by hypothetical PURE system kits obtained by

dilution (case I) or dilution/concentration (case II) of the components, according to the following *F* factors:

0.33, 0.67, 1.00 (case I); 0.67, 1.00, 1.33 (case II). *F*DNA*, F*E*, F*B refer, respectively, to the dilution factors of the groups of chemicals DNA, E and B shown in Table 3. *F*B values are coded by *different colors*,shown in the *inset box*. *F*DNA = 1 corresponds to 6.8 nM. The *green lines* the concentration of proteins obtained by a standard PURE system (*F*E = *F*B = 1) and [DNA] = 6.8 nM. The standard PURE system compositions have been marked by an *asterisk* (Color figure online)
## 4.2 Case II: Increasing and Decreasing Concentrations Around the Standard Values

Next, we move to the case where the PURE system components’ concentrations can be higher or lower than the standard case [1.0 1.0 1.0]. This scenario simulates the realistic case of micro-compartmentalized PURE system whereby—due to stochastic fluctuations—its components result to be concentrated or diluted. Data presented in Fig. 5, right column, again follow the same trend commented in Sect. 4.1, included weak dependence from DNA concentration in the explored range, and the turning point. The most effective PURE system composition, as expected, is the most concentrated one [1.33 1.33 1.33], where the synthesis of about 1.1 µM protein is predicted. The compositions that produce more protein than the standard case are all those of the types [*F*DNA≥ 0*.*67 *F*E= 1*.*33 *F*B≥ 0*.*67] and [*F*DNA≥ 0*.*67 *F*E= 1*.*00 *F*B= 1*.*33], showing that the compounds of group E are essential for high productivity, even with diluted group B; an increase in group B concentration also increase the protein production when compared to the standard case. Overall, reducing or concentrating the PURE system components in the explored *F* range (from 0.67 to 1.33) induces a variation of a factor five in the protein concentration,

i.e., from 0.22 to 1.1 µM.

<!-- page 18 -->
F. Mavelli et al.
## 4.3 Statistical Analysis

The data presented in Fig. 5, which have been qualitatively commented on in previous Sections, have been also quantitatively analyzed in order to correlate the concentrations of DNA and group E and B components to the amount of protein produced after 4 h. Linear and linearized multiple regressions have been used, which are based on Eq. 30

*f (*protein*)* = *β*0+ *β*DNA*F*DNA+ *β*E*F*E+ *β*B*F*B(30)

where *f (*protein*)*is the protein concentration itself (linear model) or a nonlinear func- tion of it (logarithm or power: linearized models) and the *β* values are the regression coefficients. For every tested model, all regression coefficients resulted to be statisti- cally significant (*p <* 0*.*05). In particular, the coefficients of the simplest model (linear multiple regression) model are as follows: *β*DNA= 0*.*12 ± 0*.*04; *β*E= 0*.*72 ± 0*.*04; *β*B= 0*.*42 ± 0*.*04, indicating that a change in concentration of the group E chemi- cals dominates the PURE system response in terms of protein concentration. Similar conclusions are obtained by fitting the data with linearized models (data not shown). Principal component analysis reveals that all variables (in the order: [protein], *F*DNA*, F*E*, F*B) have concordant projections (−0.97, −0.58, −0.82 and −0.70, respectively) on the first main component, further confirming that the weight of the group E component concentration greatly affects the protein synthesis. The projections of the variables on the second component are, respectively, −0.18, 0.74, −0.44 and 0.16, showing again a strong correlation between [protein] and *F*E.

## 4.4 Response Coefficients

In order to account for the effect of each individual variable (the nine species of the in silico PURE system model, *cf*. Table 1) on transcription and translation, their concentrations have been varied of two orders of magnitude (scaling factors *F* from 10 −1 to 10 1 ), calculating in each case the amount of mRNA and protein synthesized after 4 h. This analysis reveals to which variable(s) the PURE system mechanism is sensitive.

Figure 6 shows that DNA concentration influences the amount of produced protein

only in the low-concentration range ([DNA] *<* 10 nM), whereas the dependence becomes weaker for higher values. This prediction is in agreement with several pub- lished experimental reports carried out with PURE system or cell extracts (Noireaux et al. 2003; Shin et al. 2012; Matsuura et al. 2012; Okano et al. 2014; Siegal-Gaskins et al. 2014). Of the four catalysts, only TXcat and TLcat play a major role. In particular, the first causes a linear response when it is increased by almost two orders of magnitude (from10nMtoalmost0.4µM), with a peculiar inversion for higher values. TLcat concentration, on the other hand, linearly affects the response in terms of produced protein (note the logarithmic abscissa) and is the most important species impacting on protein synthesis.

<!-- page 19 -->
A Simple Protein Synthesis Model for the PURE System*...*

**Fig. 6** (Color Figure Online) Variations of the amount of produced protein (*L* = 238, 4 h) when the

concentration of the nine species of the in silico PURE system is varied by two orders of magnitude around their standard concentrations (*F* = 1), which are shown in Table 1. Protein concentration is expressed in terms of polymerized amino acid concentration [*a*]

Transfer RNA and the other low molecular weight compounds also reveal inter- esting patterns. In fact, the increase in tRNAs concentration (in the 0.19–19 µM range, average concentration) induces a corresponding increase in protein concentration, whereas NTPs weigh on protein synthesis only in the 150–600 mM range (average concentration). The dilution or concentration of the two remaining species, amino acids and phosphocreatine, does not cause a change in the protein amount. A similar analysis has been done for pointing out the effect of the nine PURE systems species on transcription (data not shown). In this case, DNA, TXcat and NTP are the main factors which are responsible for mRNA synthesis, as expected. In particular, TXcat affects mRNA synthesis in the same way as TLcat affects protein synthesis (*cf*.Fig.6, top-right plot). However, when mRNA concentration is too high, its degradation—which has been modeled here as a pseudo-first-order reaction— becomes more important and a reduction in mRNA concentration is observed. This means that the peculiar inversion noted in Fig. 6 (top central plot) is due to a reduction in mRNA synthesis. The effect of NTPs concentration on transcription follows a saturation-like pattern, whereby the most significant variations occur when 150 µM *<* [NTP] *<* 1500 µM (average concentration). This shape is somehow expected also considering the *K*TX,NTPvalue of 80 µM (Table 2). Finally, in the case of standard PURE system composition (*F* = 1), we carried out an analysis of the response coefficients *Ri*, defined by Eq. 31

() <u>C0,i∂[protein]</u> *Ri*= (31) [protein] *∂C*0*,i*

<!-- page 20 -->
F. Mavelli et al.
**Fig. 7** Percentage response coefficient %*Ri*

protein referred to the protein production after 4 h, of the nine PURE system species, evaluated for PURE system of standard composition, i.e., *F* = 1 for all species

where *C*0*,i*is the initial concentration of the *i*th PURE system species (i.e., the nine species of Table 1)and *Ri*represents quantitatively the normalized variation of the response function (in this case, the protein concentration) when the initial concentration of the *i*th species changes (keeping constant all the others):

[] <u>dln protein</u> ∑ = *Ri*(32) d*F* *i*

Actually, it is the normalized slope of each curve in Fig. 6. *Ri*sign and the amplitude indicate the degree of correlation between the response function, i.e., the relative protein concentration change and the *C*0*,i*relative concentration variation. ∑

Figure 7 summarizes the values of %*Ri*= *Ri/jRj*in percentage for the effects

of the nine PURE system species on the relative amount of produced protein. The most relevant contribution refers to changes in TLcat concentrations, accounting for about 45 %, followed by the tRNA (30 %) and by TXcat (17 %). The species DNA and NTP have a minor control on how PURE system produces protein, at least near the *F* = 1 conditions. A similar analysis on transcription analogously confirms that TXcat (67 %), DNA (28 %) and NTP (5 %) essentially control the changes in mRNA concentration in the case of standard PURE system composition. By comparing Figs. 5, 6 and 7, it is now possible to rationalize that in order to improve the protein yield, the better strategy could be to increase the concentration of TLcat and T, since both of them have a direct positive effect on the protein production. On the contrary, increasing the concentration of DNA and TXcat would have the main effect of enhancing the mRNA formation and only a minor positive effect on the translation, by causing also a higher consumption of energy resources by transcription compared to translation, as will be discussed in the following section.

<!-- page 21 -->
A Simple Protein Synthesis Model for the PURE System*...*

# 5 Energy Balance in the PURE System

It is interesting to study how energy is used by the PURE system, as obtained from our simplified model. Our approach just takes into account the stoichiometric influence of energy molecules on the mechanism which is described by our model, and does not deal with the issue of the adenylate energy charge (Atkinson 1968), which has been previously shown to be an important determinant of cell-free protein synthesis reaction lifetime in vitro (Matveev et al. 1996; Schoborg et al. 2014; Choudhury et al.

2014). By referring to Fig. 3, it is possible to see that the PURE system actually counts on two primary high-energy phosphate molecules, namely the nucleoside triphosphates (NTPs, which are phosphoanhydrides) and the creatine phosphate (CP, a phospho- ramidate). NTPs (in particular GTP and ATP) drive the endergonic TL and RS reactions and are converted to exhausted species as nucleoside diphosphates and monophosphates, here indicated generically as NXPs. The TX reaction uses NTPs as substrates, but their conversion to mRNA (nt) is only weakly exergonic (ca. −4kJ/mol)(Heinonen
2001). As evidenced in Sect. 2.1, the reaction is ultimately driven by PP*i*hydrolysis (ca. −22 kJ/mol) (Heinonen 2001). It is clear, however, that the amount of PP*i*(which is itself a high-energy phosphate molecule) is equivalent to the amount of NTPs used in the transcription, and therefore, it will not be included in the energy balance. By defining the PURE system “chemical energy” *χε*as the overall concentration of energy-rich phosphate molecules:
*χε*= *n*NTP[NTP]+[CP] (33)

it is possible to determine the rate of the energy consumption (Eq. 34).

d*χε*d[NTP] d[CP] − =−*n*NTP− = *V*TX+ 2*V*TL+ *V*RS(34) d*t* d*t* d*t*

which is the sum of three terms, referring to the TX, TL and RS processes with correct stoichiometric coefficients. However, due to the fact that these three rates vary in time, the amount of chemical energy flowing in each process is not constant along the course of PURE system reaction. The relative rate *φ* of the energy consumption for each process is more informative in this respect, and it can be simply calculated, as shown, for instance, in the case of the TL reaction, as in Eq. 35:

<u>2VTL</u> *φ*TL= (35) *V*TX+ 2*V*TL+ *V*RS

It is interesting to monitor how *φ*TX*,φ*TLand *φ*RSchanges in time (Fig. 8). In the first very fast phase (*t* ∼ 1 minute), the rate of RS reactions dominates the energy consumption landscape (*φ*RS≃ 85 %), because the other two reactions (TX and TL) are slower in this time window. This causes a rapid consumption of ATP for aminoacylating the tRNA species, which proceeds until all the tRNA pool is converted

<!-- page 22 -->
F. Mavelli et al.
**Fig. 8** Time profiles of the functions *φ*TX (*blue*) *φ*TL (*red*) *φ*RS (*black*) expressed as percent values. Note

that logarithmic *x*-axis span from 1 s to 4 h (Color figure online)

in aminoacylated tRNAs (note also that amino acids are present in excess amount when compared with tRNAs). The minimal RS reaction rate occurs at about 4 minutes. Next, a second phase follows where TX and TL reactions become relevant. The rate of mRNA synthesis accounts for about 15 % of the energy consumption in the early stage, but when the RS reaction rate decreases, *φ*TXincreases to about 85 %. The accumulation of mRNA triggers the slowest process, which is translation. The value of*φ*TLbecome significantly different from zero (ca. 2 %) only after about 2 min, but a sort of steady state is reached slightly later, between 4 and 32 min, when the burst phase of RS reaction is completed and the two reactions (TL and RS) use the energy resources in a linked manner (in a 2 GTP : 1 ATP ratio). In particular, when the maximal flux of energy is channeled in TL/RS reaction (after about 30 min), *φ*TL+*φ*RS= 24 % + 12 % = 36 %. Correspondingly,*φ*TX= 64 % represents the minimal contribution of TX rate to the energy consumption. A third phase is also evident in Fig. 8, whereby the relative energy consumption rates of TL/RS reactions decrease. This is due to the degradation of TLcat, which takes place in this time range and brings about to the end of protein synthesis, whereas according to our model, TX reaction continues to produce mRNA. When this happens, the RS reaction also stops because the AT pool is not depleted anymore by the ribosomal reactions. From this analysis, it results that in the explored conditions (Table 1, and [DNA] =

6.8 nM), the usage of PURE system chemical energy *χϵ*is very much biased toward the transcription, which consumes much more energy than the sum of translation and aminoacylation reactions (5.7 times faster at 4 minutes, 1.8 times faster at 32 min). How do these calculations on energy consumption rates translate in terms of the amount of chemical energy *χϵ*used by each processes? To this aim, we calculate the percent amount *Q* of chemical energy used by each process by integrating the corresponding rates of energy consumption from *t* = 0to4h.

<!-- page 23 -->
A Simple Protein Synthesis Model for the PURE System*...*

**Fig. 9** DNA dependence on the percent amount *Q* of chemical energy *χϵ* consumed by TX (*blue*), TL

(*red*)andRS(*black*) processes, as obtained by integration of the corresponding rates of NTP consumption from 0 to 4 h. Note that the logarithmic *x*-axis spans from [DNA] = 6.8 pM (*F*DNA = 10−2)to6.8nM (*F*DNA = 100) (Color figure online)

The next point is whether, and to what extent, it is possible to obtain a more balanced energy consumption by changing the composition of the PURE system. We reasoned that since the main reason for this imbalance is an excessive TX rate, a reduction in DNA concentration would slow down the transcription, allowing a more efficient use of chemical energy resources. Figure 9 shows the amount of chemical energy used by the TX, TL and EN processes when the DNA concentration is decreased by up to 100 times. When [DNA] = 6.8 nM, it results that TX, TL and RS processes have used, respectively, 74, 15 and 11 % of *χϵ*. By reducing the DNA concentration to 0.68 nM, these values become, respectively, 55, 22 and 23 %. After a further reduction to 68 pM, the figures of 25, 15 and 60 % are obtained. Thanks to our model, it is possible to predict what would be the best PURE system composition in order to have a more balanced energy usage (in particular, for favoring the TL reaction rather than the TX reaction). To this aim, we have carried out simula- tions similar to those shown in Fig. 9 for a number of cases, and the results have been summarized in Table 4. In the case of standard PURE system, with [DNA] = 6.8 nM (entry 1), about 75 % of available chemical energy *χϵ*is employed for synthesizing mRNA, and only about 25 % of it is instead used for producing protein. Clearly, this is a consequence of a high transcription rate and of the continuous mRNA production, not necessary for protein production. Actually, TX and RS/TL processes compete for energy. In order to have a proper energy balance, therefore, transcription must be slowed down. This can be done by reducing the amount of template (entries 2 and 3) or of the catalyst TXcat (entry 4). As expected, the ratios between the Q values now increase

<!-- page 24 -->
F. Mavelli et al.

|Table 4|Amount Q (%) of chemical energy used by TX and TL/RS processes in PURE systems of variable||||
|---|---|---|---|---|
|compositions|||||
|Entry|Variation|QTX|QTL + QRS|QTL + QRS|
|||||QTX|
|1|None (reference)|74|26|0.35|
|2|tenfold reduction in [DNA]|55|45|0.82|
|3|100-fold reduction in [DNA]|25|75|2.99|
|4|tenfold reduction in [TXcat]|45|55|1.24|
|5|tenfold increase in [TLcat]|25|75|2.99|
|6|Abrogation of TLcat decay|45|55|1.24|
|7 The reference values refer to the PURE system standard composition (Table 1) and [DNA] = 6.8 nM|tenfold increase of [NTP]|75|25|0.34|

from 0.35 to 2.99 or 1.24, respectively, for 100-fold DNA dilution or tenfold TXcat dilution. Another possibility, although not easily to implement experimentally, would be the increase in ribosome concentration, and this would bring about the case of a tenfold increase in the TLcat species to revert the energy consumption in favor of TL and RS processes (cf. entry 1 and entry 5). Similarly, the abrogation of ribosomal decay (entry 6) concurs to a better employment of energy, because the TL process can safely run for longer time. Finally, an increase in NTP concentration does not change the Q ratio (cf. entry 1 and entry 7). From these calculations, it is evident that tuning the otherwise too efficient tran- scription is one of the key mechanism for modifying the use of chemical energy in the PURE system. The excess mRNA production is not only useless, but also detrimental because it “burns” ATP and GTP that are instead essential for RS/TL reactions.

# 6 PURE System Entrapped in Liposomes

What next? The approach followed in the present paper deals with the behavior of PURE system in systems consisting of large volumes and very high number of molecules. This was a necessary study before investigating the more intriguing pattern of PURE system entrapped in liposomes. In the second case, the approach should be changed: In fact, the smaller the liposome is, the higher the stochasticity of the system is, since a single molecule presence/absence can affect the global behavior (extrinsic stochastic effects). Moreover, intrinsic stochastic effects will also become relevant, and the deterministic strategy presented here (differential equations) should be sub- stituted by a stochastic modeling (master equation). Experiments where the PURE system is encapsulated inside lipid vesicles often display both extrinsic and intrinsic stochastic effects. For example, considering the case of random fluctuations of the √ number of entrapped molecules, of the order of 10 % or higher (*ΔN /N* = 1*/ N* ≥

0.1), these will appear in vesicles with diameters ≤ 0.7 µmor≤ 7 µm, respectively, for solutes with concentration 1 µM or 1 nM (the concentration of PURE system macromolecules lies in this range). In such a scenario, it is mandatory to provide a

<!-- page 25 -->
A Simple Protein Synthesis Model for the PURE System*...*

detailed description of the PURE system reactions and an accurate evaluation of the number of molecules for each chemical species. The interactions between molecules should have a stochastic nature, able to describe systems with a very low number of components. A first stochastic model of PURE system entrapped in liposomes has been provided by us in Lazzerini-Ospri et al. (2012), Calviello et al. (2013). It is interesting to note that the preliminary results presented in that paper are in agreement with the results obtained by the present model. Calviello *et al.* suggest that the DNA concentration is the least important parameter in the system, while enzyme and metabolite concentra- tions play a central role (Calviello et al. 2013). Also the energetic balance presents a similar distribution on both the studies, with the TX block that dominates the energy consumption. These similarities suggest that an in-depth exploration into the behavior of highly diluted PURE system entrapped in liposomes of diverse size could be useful, but this is beyond the present work and it will be faced by future papers (in preparation) dedicated to such an exploration.

# 7 Concluding Remarks

We have presented a mathematical model of the transcription–translation mechanisms, specifically designed to simulate the reactions occurring when the PURE system is employed as cell-free protein synthesis machinery. This model includes both real and fictitious species, introduced to simplify the mechanism, and consists of four modules that mirror the PURE system architecture. Many aspects of true biochemical mechanisms have been intentionally omitted but can be easily implemented in future optimizations. The related open question refers to what is the minimal complexity of in silico models which is capable of producing realistic patterns that mimic those of in vitro systems. Essentially, this model can be used in future work for investigating the PURE system dynamics, especially in those cases where an accurate model is not needed. However, it is remarkable that despite its simplicity, the presented model is capable of being informative with respect to several quantitative aspects of protein synthesis. In this work, we have studied only some particular facets of the fascinating TX–TL mechanism—probably the most important mechanism for cellular biology. Several additional analyses are possible, especially by combining these biochemical reactions, micro-compartmentation and diffusion-driven reactions. In addition, the present model can be extended to simulate synthetic genetic circuits (Hockenberry and Jewett 2012), by introducing transcription factors and their control on the TX reactions. Experimental reports on synthetic genetic circuits in vitro have been already reported (Noireaux et al. 2003; Shin et al. 2012; Siegal-Gaskins et al. 2014), and such data can be used for tuning the model. With this work, we aim at contributing to the integration between theoretical and experimental approaches in bottom-up synthetic biology. This is particularly true in the field of synthetic cell construction, which until now did not benefit enough from mathematical modeling.

<!-- page 26 -->
F. Mavelli et al.
**Acknowledgments** We are grateful to Pier Luigi Luisi for his guidance in the field of synthetic cells and for useful comments on the manuscript. The modeling work has been started within the PRIN2008 (2008FY7RJ4) Synthetic Cells project and further expanded thanks to networking initiatives such EU-COST Actions CM0703 (Systems Chemistry) and CM1304 (Emergence and Evolution of Complex Chemical Systems). We thank Margherita Caputo (Univ. Bari) and Francesca D’Angelo (Roma Tre Univ.) for their involvement in the initial phase of the work.

# References

Atkinson DE (1968) The energy charge of the adenylate pool as a regulatory parameter. Interaction with feedback modifiers. Biochemistry 7(11):4030 Calviello L, Stano P, Mavelli F, Luisi PL, Marangoni R (2013) Quasi-cellular systems: stochastic simulation analysis at nanoscale range. BMC Bioinform 14(Suppl 7):S7 Chiarabelli C, Stano P, Luisi PL (2009) Chemical approaches to synthetic biology. Curr Opin Biotechnol 20(4):492 Choudhury A, Hodgman CE, Anderson MJ, Jewett MC (2014) Evaluating fermentation effects on cell growth and crude extract metabolic activity for improved yeast cell-free protein synthesis. Biochem Eng J 91:140 Dominak LM, Keating CD (2007) Polymer encapsulation within giant lipid vesicles. Langmuir 23(13):7148 Dong H, Nilsson L, Kurland CG (1996) Co-variation of tRNA abundance and codon usage in *Escherichia* *coli* at different growth rates. J Mol Biol 260(5):649 Endy D (2005) Foundations for engineering biology. Nature 438(7067):449 Frazier JM, Chushak Y, Foy B (2009) Stochastic simulation and analysis of biomolecular reaction networks. BMC Syst Biol 3:64 Harris DC, Jewett MC (2012) Cell-free biology: exploiting the interface between synthetic biology and synthetic chemistry. Curr Opin Biotechnol 23(5):672 Heinonen JK (2001) Biological role of inorganic pyrophosphate. Kluver Academic Publisher, New York Hockenberry AJ, Jewett MC (2012) Synthetic in vitro circuits. Curr Opin Chem Biol 16(3–4):253 Hodgman CE, Jewett MC (2012) Cell-free synthetic biology: thinking outside the cell. Metab Eng 14(3):261 Jewett MC, Fritz BR, Timmerman LE, Church GM (2013) In vitro integration of ribosomal RNA synthesis, ribosome assembly, and translation. Mol Syst Biol 9(1):678 Karzbrun E, Shin J, Bar-Ziv RH, Noireaux V (2011) Coarse-grained dynamics of protein synthesis in a cell-free system. Phys Rev Lett 106(4):048104 Kato A, Yanagisawa M, Sato YT, Fujiwara K, Yoshikawa K (2012) Cell-sized confinement in microspheres accelerates the reaction of gene expression. Sci Rep 2:283 Kazuta Y, Matsuura T, Ichihashi N, Yomo T (2014) Synthesis of milligram quantities of proteins using a reconstituted in vitro protein synthesis system. J Biosci Bioeng 118(5):554 Kuruma Y, Stano P, Ueda T, Luisi PL (2009) A synthetic biology approach to the construction of membrane proteins in semi-synthetic minimal cells. Biochim Biophys Acta 1788(2):567 Lazzerini-Ospri L, Stano P, Luisi P, Marangoni R (2012) Characterization of the emergent properties of a synthetic quasi-cellular system. BMC Bioinform 13(Suppl 4):S9 LeDuc PR, Wong MS, Ferreira PM, Groff RE, Haslinger K, Koonce MP, Lee WY, Love JC, McCammon JA, Monteiro-Riviere NA, Rotello VM, Rubloff GW, Westervelt R, Yoda M (2007) Towards an in vivo biologically inspired nanofactory. Nat Nano 2(1):3 Liu AP, Fletcher DA (2009) Biology under construction: in vitro reconstitution of cellular function. Nat Rev Mol Cell Biol 10(9):644 Lohse B, Bolinger PY, Stamou D (2008) Encapsulation efficiency measured on single small unilamellar vesicles. J Am Chem Soc 130(44):14372 Luisi PL, Ferri F, Stano P (2006) Approaches to semi-synthetic minimal cells: a review. Naturwissenschaften 93(1):1 Luisi PL, Allegretti M, Pereira de Souza T, Steiniger F, Fahr A, Stano P (2010) Spontaneous protein crowding in liposomes: a new vista for the origin of cellular metabolism. ChemBioChem 11(14):1989 Matsubayashi H, Ueda T (2014) Purified cell-free systems as standard parts for synthetic biology. Curr Opin Chem Biol 22:158 Matsubayashi H, Kuruma Y, Ueda T (2014) In vitro synthesis of the *E. coli* sec translocon from DNA. Angew Chem Int Ed 53(29):7535

<!-- page 27 -->
A Simple Protein Synthesis Model for the PURE System*...*

Matsuura T, Kazuta Y, Aita T, Adachi J, Yomo T (2009) Quantifying epistatic interactions among the components constituting the protein translation system. Mol Syst Biol 5:297 Matsuura T, Hosoda K, Kazuta Y, Ichihashi N, Suzuki H, Yomo T (2012) Effects of compartment size on the kinetics of intracompartmental multimeric protein synthesis. ACS Synth Biol 1(9):431 Matveev SV, Vinokurov LM, Shaloiko LA, Davies C, Matveeva EA, Alakhov YuB (1996) Effect of the ATP level on the overall protein biosynthesis rate in a wheat germ cell-free system. Biochim Et Biophys Acta 1293(2):207 Mavelli F, Altamura E, Cassidei L, Stano P (2014) Recent theoretical approaches to minimal artificial cells. Entropy 16(5):2488–2511 Murtas G, Kuruma Y, Bianchini P, Diaspro A, Luisi PL (2007) Protein synthesis in liposomes with a minimal set of enzymes. Biochem Biophys Res Commun 363(1):12 NakanoT Moore M, Enomoto A, Suda T (2011) Biological functions for information and communication technologies. In: Sawai H (ed) Studies in computational intelligence, no. 320. Springer, Berlin, pp 49–86 Nishimura K, Matsuura T, Nishimura K, Sunami T, Suzuki H, Yomo T (2012) Cell-free protein synthesis inside giant unilamellar vesicles analyzed by flow cytometry. Langmuir 28(22):8426 Niwa T, Kanamori T, Ueda T, Taguchi H (2012) Global analysis of chaperone effects using a reconstituted cell-free translation system. Proc Nat Acad Sci 109(23):8937 Noireaux V, Bar-Ziv R, Libchaber A (2003) Principles of cell-free genetic circuit assembly. Proc Natl Acad Sci USA 100(22):12672 Okano T, Matsuura T, Suzuki H, Yomo T (2014) Cell-free protein synthesis in a microchamber revealed the presence of an optimum compartment volume for high-order reactions. ACS Synth Biol 3(6):347 Pereira de Souza T, Stano P, Luisi PL (2009) The minimal size of liposome-based model cells brings about a remarkably enhanced entrapment and protein synthesis. ChemBioChem 10(6):1056 Pereira de Souza T, Steiniger F, Stano P, Fahr A, Luisi PL (2011) Spontaneous crowding of ribosomes and proteins inside vesicles: a possible mechanism for the origin of cell metabolism. ChemBioChem 12(15):2325 Rampioni G, Mavelli F, Damiano L, DAngelo F, Messina M, Leoni L, Stano P (2014) A synthetic biology approach to bio-chem-ICT: first moves towards chemical communication between synthetic and natural cells. Nat Comput 13:333–349 Saito H, Kato Y, Le Berre M, Yamada A, Inoue T, Yosikawa K, Baigl D (2009) Time-resolved tracking of a minimum gene expression system reconstituted in giant liposomes. ChemBioChem 10(10):1640 Schoborg JA, Hodgman CE, Anderson MJ, Jewett MC (2014) Substrate replenishment and byproduct removal improve yeast cell-free protein synthesis. Biotechnol J 9(5):630 Seo SW, Yang J, Min BE, Jang S, Lim JH, Lim HG, Kim SC, Kim SY, Jeong JH, Jung GY (2013) Synthetic biology: tools to design microbes for the production of chemicals and fuels. Biotechnol Adv 31(6):811 Shimizu Y, Inoue A, Tomari Y, Suzuki T, Yokogawa T, Nishikawa K, Ueda T (2001) Cell-free translation reconstituted with purified components. Nat Biotechnol 19(8):751. doi:10.1038/90802 Shimizu Y, Kanamori T, Ueda T (2005) Protein synthesis by pure translation systems. Methods 36(3):299 Shin J, Jardine P, Noireaux V (2012) Genome replication, synthesis, and assembly of the bacteriophage T7 in a single cell-free reaction. ACS Synth Biol 1(9):408 Siegal-Gaskins D, Tuza ZA, Kim J, Noireaux V, Murray RM (2014) Gene circuit performance characteri- zation and resource usage in a cell-free “breadboard”. ACS Synth Biol 3(6):416 Soga H, Fujii S, Yomo T, Kato Y, Watanabe H, Matsuura T (2014) In vitro membrane protein synthesis inside cell-sized vesicles reveals the dependence of membrane protein integration on vesicle volume. ACS Synth Biol 3:372–379 Stano P, Carrara P, Kuruma Y, de Souza TP, Luisi PL (2011) Compartmentalized reactions as a case of soft-matter biotechnology: synthesis of proteins and nucleic acids inside lipid vesicles. J Mater Chem 21(47):18887 Stano P, Rampioni G, Carrara P, Damiano L, Leoni L, Luisi PL (2012) Semi-synthetic minimal cells as a tool for biochemical ICT. BioSystems 109(1):24 Stano P, Luisi PL (2013) Semi-synthetic minimal cells: origin and recent developments. Curr Opin Biotechnol 24:633–638 Stano P, D’Aguanno E, Bolz J, Fahr A, Luisi PL (2013) A remarkable self-organization process as the origin of primitive functional cells. Angew Chem Int Ed Engl 52(50):13397

<!-- page 28 -->
F. Mavelli et al.
Stano P, Souza T, Carrara P, Altamura E, D’Aguanno E, Caputo M, Luisi PL, Mavelli F (2015) Recent biophysical issues about the preparation of solute-filled lipid vesicles. Mech Adv Mater Struct 22:748– 759 Stögbauer T, Windhager L, Zimmer R, Rädler JO (2012) Experiment and mathematical modeling of gene expression dynamics in a cell-free system. Integr Biol 4(5):494 Sun BY, Chiu DT (2005) Determination of the encapsulation efficiency of individual vesicles using single-vesicle photolysis and confocal single-molecule detection. Anal Chem 77(9):2770 Sunami T, Hosoda K, Suzuki H, Matsuura T, Yomo T (2010) Cellular compartment model for exploring the effect of the lipidic membrane on the kinetics of encapsulated biochemical reactions. Langmuir 26(11):8544 van Nies P, Nourian Z, Kok M, van Wijk R, Moeskops J, Westerlaken I, Poolman JM, Eelkema R, van Esch JH, Kuruma Y, Ueda T, Danelon C (1963) Unbiased tracking of the progression of mRNA and protein synthesis in bulk and in liposome-confined reactions. ChemBioChem 14(15):1963–1966 Walde P, Umakoshi H, Stano P, Mavelli F (2014) Emergent properties arising from the assembly of amphiphiles. Artificial vesicle membranes as reaction promoters and regulators. Chem Comm 50:10177–10197 Yarchuk O, Jacques N, Guillerez J, Dreyfus M (1992) Interdependence of translation, transcription and mRNA degradation in the lacZ gene. J Mol Biol 226(3):581 Zhao H (ed) (2013) Synthetic Biology. Tools and applications. Academic Press-Elsevier, Amsterdam