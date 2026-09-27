# PNAS2017_full_reference

The unchanged author-site combined SBML is
[`original/fMGG_synthesis.xml`](original/fMGG_synthesis.xml). It is byte-identical
to the captured file under `references/PNAS2017_Matsuura/raw/`. Source URLs,
checksums and missing publisher supplements are recorded there.

`normalized/` contains a **derived execution compatibility copy**. It replaces
literal constant `stoichiometryMath` elements with equal numeric stoichiometry
attributes because tested solver imports read one `2 PO4` coefficient as `1`.
The source SBML remains the scientific definition. `audit/` contains generated
inventories and qualified resource annotations; neither directory is a
scientific modification or a reduced model.

This reference describes mRNA-directed fMGG translation. Transcription and
membrane transport are outside its source scope.
