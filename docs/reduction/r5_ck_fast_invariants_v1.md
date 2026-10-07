# CK fast invariants

Species order (CK,CK_ADP,CP,CK_CP,CK_CP_ADP), columns (332,333,336,337):

```
Sf=[[-1,1,0,0],[0,0,-1,1],[-1,1,-1,1],[1,-1,0,0],[0,0,1,-1]]
Lf_local=[[1,0,0,1,0],[0,1,0,0,1],[0,0,1,1,1]]
```

rank=2; reaction nullity=2; local left-nullity=3. Append the 236 unaffected-species identity rows to obtain full-row-rank Lf (239×241), Lf Sf=0 exactly. Thus T0=CK+CK_CP, T1=CK_ADP+CK_CP_ADP, B=CP+CK_CP+CK_CP_ADP. All are FAST_SUBSYSTEM_INVARIANT and DYNAMIC_TOTAL_COORDINATE, never SOURCE_GENERAL_EXACT_CONSERVATION. slow_forcing_of_fast_totals.csv gives every touching non-fast column and coefficients. These totals change in the full model. Restricting Lf to the exact R1 SOURCE_GENERAL 214-dimensional class gives rank212; selected coordinate rows include all three totals. The 27 source-general laws are retained via the affine R1 lift, not asserted for fast totals.
