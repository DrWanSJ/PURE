# B1-3 原始来源与解释边界

规范SBML和作者CSV最高优先；本轮只读原始S12-S16和S27，所有来源原始字节保持。源反应结构EXTRACTED；完整分子组成及真实生理顺序未认证。

## 原始文件定位

- `references/PNAS2017_Matsuura/raw/pnas.1615351114.sd12.xlsx` SHA-256 `87051f1a25498750d16bcaccd9f4c3b8849c2b6a76efa119373b041de1ee54ed`。
- `references/PNAS2017_Matsuura/raw/pnas.1615351114.sd13.xlsx` SHA-256 `f2c6c7c20859cf1fa5cfa78415d4923422e4b2577cc0aa04a110ffe1cb83be56`。
- `references/PNAS2017_Matsuura/raw/pnas.1615351114.sd14.xlsx` SHA-256 `db1207bdabcc43f950fa86dcba4c93e82d7c0fae7af857ca6d5362a67e57c046`。
- `references/PNAS2017_Matsuura/raw/pnas.1615351114.sd15.xlsx` SHA-256 `3e292593b51b7c90b77a6c092c90592cf35311e39375e18a9934ebb839202845`。
- `references/PNAS2017_Matsuura/raw/pnas.1615351114.sd16.xlsx` SHA-256 `4f683eb04f06112b219aba97b246dd2009c3eaccf24e83bd7d51dae9b7c0f695`。
- `references/PNAS2017_Matsuura/raw/pnas.1615351114.sd27.xlsx` SHA-256 `d52052e6ce24ddcd1894e95b3f759f1a047600e6ffccff28cc2dcd2b8d94b227`。
- `references/PNAS2017_Matsuura/raw/matsuura-et-al-2017-reaction-dynamics-analysis-of-a-reconstituted-escherichia-coli-protein-translation-system-by.pdf` SHA-256 `e340ba829f87121e723059aebecc56c342c37c2cc4687692d1447f16b38f2a4e`。

原论文完整读取页2/7/8（doi 10.1073/pnas.1615351114），支持模型架构背景。具体终止/回收以原始子系统和规范SBML逐方向核对，不能从文章图推断遗漏步骤。独立完整SI文本/PDF本地仍未建立。

## S27作者源物种定义

| 源物种 | S27行 | 作者定义（摘录原始数据） | 初始uM |
|---|---:|---|---:|
| `RS50S` | 7 | ribosomal 50S subunit | 0 |
| `RS30S` | 8 | ribosomal 30S subunit | 0 |
| `mRNA` | 9 | mRNA | 0.1 |
| `PO4` | 16 | phosphate | 0 |
| `EFG_GTP` | 19 | a complex composed of EF-G and GTP | 0 |
| `EFG_GDP` | 20 | a complex composed of EF-G and GDP | 0 |
| `GTP` | 24 | GTP (guanosine-5'-triphosphate) | 2500 |
| `GDP` | 25 | GDP (guanosine-5'-diphosphate) | 0 |
| `tRNAGlyGCC` | 41 | tRNAGlyGCC | 3.5476718403547673 |
| `elRS70SAUAA0004_Pept0003tRNAGlyGCC` | 46 | an elongation complex with fMet-Gly-Gly-tRNAGlyGCC at the P site and UAA codon (stop codon in the ORF) at the A site | 0 |
| `RF1` | 206 | RF1 (release factor 1) | 0.2 |
| `Pept0003` | 207 | fMet-Gly-Gly | 0 |
| `termRS70SUAA0004_tRNAGlyGCC` | 209 | a post-termination complex with tRNAGlyGCC at the P site and UAA stop codon at the A site | 0 |
| `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1` | 210 | a pre-termination complex with fMet-Gly-Gly-tRNAGlyGCC at the P site and UAA stop codon and RF1 at the A site | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RF1` | 211 | a post-termination complex after the peptidyl-tRNA hydrolysis in No. 209 complex | 0 |
| `RF2` | 212 | RF2 (release factor 2) | 0.2 |
| `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2` | 214 | a pre-termination complex with fMet-Gly-Gly-tRNAGlyGCC at the P site and UAA stop codon and RF2 at the A site | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RF2` | 215 | a post-termination complex after the peptidyl-tRNA hydrolysis in No. 213 complex | 0 |
| `RF3` | 216 | RF3 (release factor 3) | 0.7 |
| `RF3_GDP` | 218 | a complex composed of RF3 and GDP | 0 |
| `RF3_GTP` | 219 | a complex composed of RF3 and GTP | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP` | 220 | a post-termination complex with tRNAGlyGCC at the P site, UAA stop codon and RF1 at the A site, and RF3 complex with GDP | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP` | 221 | a post-termination complex with tRNAGlyGCC at the P site, UAA stop codon and RF1 at the A site, and RF3 complex with GTP | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3` | 222 | a post-termination complex with tRNAGlyGCC at the P site, UAA stop codon and RF1 at the A site, and RF3 | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP` | 223 | a post-termination complex with tRNAGlyGCC at the P site, UAA stop codon at the A site, and RF3 complex with GTP, after RF1 or RF2 dissociation from No. 220 or No. 226 complex, respectively | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP` | 224 | a complex after phophate is dissociated from No. 224 complex | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4` | 225 | a complex just after GTP hydrolysis in No. 222 complex | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP` | 226 | a post-termination complex with tRNAGlyGCC at the P site, UAA stop codon and RF2 at the A site, and RF3 complex with GDP | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP` | 227 | a post-termination complex with tRNAGlyGCC at the P site, UAA stop codon and RF2 at the A site, and RF3 complex with GTP | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3` | 228 | a post-termination complex with tRNAGlyGCC at the P site, UAA stop codon and RF2 at the A site, and RF3 | 0 |
| `RRF` | 229 | RRF (ribosome recycling factor) | 16 |
| `RS50S_RRF` | 231 | a complex composed of 50S ribosomal subunit and RRF | 0 |
| `RS50S_tRNAGlyGCC_RRF` | 235 | a complex composed of 50S ribosomal subunit, tRNAGlyGCC, and RRF | 0 |
| `RS50S_tRNAGlyGCC_RRF_EFG_GDP` | 236 | a complex composed of 50S ribosomal subunit, tRNAGlyGCC, RRF, and EF-G complex with GDP | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP` | 237 | a post-termination complex with tRNAGlyGCC at the P site, UAA stop codon at the A site, and EF-G complex with GTP | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RRF` | 238 | a post-termination complex with tRNAGlyGCC at the P site, UAA stop codon at the A site, and RRF | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP` | 239 | a complex after phosphate is dissociated from No. 239 complex | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4` | 240 | a complex just after GTP is hydrolyzed in No. 240 complex | 0 |
| `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP` | 241 | a post-termination complex with tRNAGlyGCC at the P site, UAA stop codon at the A site, RRF, and EF-G complex with GTP | 0 |
| `termRS30S_mRNA` | 242 | a complex composed of 30S ribosomal subunit and mRNA, which is formed by the ribosome recycling step | 0 |

T_pre是项目缩写；作者把RF-free入口称为elongation complex，RF结合态称为pre-termination complex。RF3/EF-G的GDP/GTP/PO4状态保留为原始独立物种。S27和CSV的初始条件不同不能自动用有限witness lot替代作者浓度；操作CSV原值见机器附录。

初始浓度原始差异：`[{"species_id": "tRNAGlyGCC", "S27_uM": "3.5476718403547673", "operational_CSV_value": "3.54767184", "agrees": false, "authority": "OPERATIONAL_CSV_FOR_OPERATION; S27_RETAINED_AS_ORIGINAL_DEFINITION"}]`。不调和或改写来源。

## S27参数、假设与原始逆向列

| 源ID | S27行 | 参数 | 说明 | 作者逆向列 |
|---|---:|---:|---|---|
| re0000000796 | 797 | 60 |  | re0000000797 |
| re0000000797 | 798 | 0.0028 |  | re0000000796 |
| re0000000798 | 799 | 0.5 |  | re0000000810 |
| re0000000799 | 800 | 0.0028 |  | re0000000800 |
| re0000000800 | 801 | 60 |  | re0000000799 |
| re0000000810 | 811 | 0 | assumed to be an irreversible reaction | re0000000798 |
| re0000000811 | 812 | 23 |  | re0000000812 |
| re0000000812 | 813 | 0.016 |  | re0000000811 |
| re0000000813 | 814 | 1.5 |  | re0000000823 |
| re0000000814 | 815 | 0.016 |  | re0000000815 |
| re0000000815 | 816 | 23 |  | re0000000814 |
| re0000000823 | 824 | 0 | assumed to be an irreversible reaction | re0000000813 |
| re0000000829 | 830 | 30 | the value was obtained from EF-G, a similar GTPase factor | re0000000830 |
| re0000000830 | 831 | 25 | the value was obtained from EF-G, a similar GTPase factor | re0000000829 |
| re0000000831 | 832 | 30 | the value was obtained from EF-G, a similar GTPase factor | re0000000832 |
| re0000000832 | 833 | 25 | the value was obtained from EF-G, a similar GTPase factor | re0000000831 |
| re0000000833 | 834 | 30 | the value was obtained from EF-G, a similar GTPase factor | re0000000834 |
| re0000000834 | 835 | 25 | the value was obtained from EF-G, a similar GTPase factor | re0000000833 |
| re0000000838 | 839 | 0.3 |  | re0000000839 |
| re0000000839 | 840 | 60 |  | re0000000838 |
| re0000000840 | 841 | 31 | the value was obtained from EF-G, a similar GTPase factor | re0000000841 |
| re0000000841 | 842 | 5 | the value was obtained from EF-G, a similar GTPase factor | re0000000840 |
| re0000000842 | 843 | 5 | the value was obtained from EF-G, a similar GTPase factor | re0000000868 |
| re0000000843 | 844 | 10.5 |  | re0000000844 |
| re0000000844 | 845 | 5.82 |  | re0000000843 |
| re0000000845 | 846 | 10 |  | re0000000846 |
| re0000000846 | 847 | 25 |  | re0000000845 |
| re0000000847 | 848 | 1000 | assumed to be a fast reaction | re0000000869 |
| re0000000868 | 869 | 0 | assumed to be an irreversible reaction | re0000000842 |
| re0000000869 | 870 | 0 | assumed that RF3 does not bind to the ribosome without RF1 or RF2 | re0000000847 |
| re0000000870 | 871 | 30 | the value was obtained from EF-G, a similar GTPase factor | re0000000871 |
| re0000000871 | 872 | 25 | the value was obtained from EF-G, a similar GTPase factor | re0000000870 |
| re0000000872 | 873 | 30 | the value was obtained from EF-G, a similar GTPase factor | re0000000873 |
| re0000000873 | 874 | 25 | the value was obtained from EF-G, a similar GTPase factor | re0000000872 |
| re0000000874 | 875 | 30 | the value was obtained from EF-G, a similar GTPase factor | re0000000875 |
| re0000000875 | 876 | 25 | the value was obtained from EF-G, a similar GTPase factor | re0000000874 |
| re0000000879 | 880 | 0.77 |  | re0000000880 |
| re0000000880 | 881 | 23 |  | re0000000879 |
| re0000000881 | 882 | 10.5 |  | re0000000882 |
| re0000000882 | 883 | 5.82 |  | re0000000881 |
| re0000000883 | 884 | 10 |  | re0000000884 |
| re0000000884 | 885 | 25 |  | re0000000883 |
| re0000000895 | 896 | 31 |  | re0000000896 |
| re0000000896 | 897 | 2.4 |  | re0000000895 |
| re0000000900 | 901 | 0.6 |  | re0000000901 |
| re0000000901 | 902 | 3.1 |  | re0000000900 |
| re0000000902 | 903 | 5 |  | re0000000956 |
| re0000000904 | 905 | 3.1 |  | re0000000905 |
| re0000000905 | 906 | 0.6 |  | re0000000904 |
| re0000000906 | 907 | 31 |  | re0000000907 |
| re0000000907 | 908 | 2.4 |  | re0000000906 |
| re0000000908 | 909 | 31 |  | re0000000909 |
| re0000000909 | 910 | 5 |  | re0000000908 |
| re0000000910 | 911 | 1000 | assumed to be a fast reaction | re0000000957 |
| re0000000911 | 912 | 1000 | assumed to be a fast reaction | re0000000912 |
| re0000000912 | 913 | 0 | assumed to be an irreversible reaction | re0000000911 |
| re0000000913 | 914 | 1000 | assumed to be a fast reaction | re0000000959 |
| re0000000916 | 917 | 1000 | assumed to be a fast reaction | re0000000965 |
| re0000000918 | 919 | 1000 | assumed to be a fast reaction | re0000000968 |
| re0000000956 | 957 | 0 | assumed to be an irreversible reaction | re0000000902 |
| re0000000957 | 958 | 0 | assumed to be an irreversible reaction | re0000000910 |
| re0000000959 | 960 | 0 | assumed to be an irreversible reaction | re0000000913 |
| re0000000965 | 966 | 0 | assumed to be an irreversible reaction | re0000000916 |
| re0000000968 | 969 | 0 | assumed to be an irreversible reaction | re0000000918 |

反向关系独立由规范方程双边精确交换重算；作者逆向列仅保留原始语义。参数正值仅代表方向可用，不证明主导通量。完整S12-S16行级映射及零参数/降解记录见JSON和source_scope。

本轮核对232条五子系统工作簿反应行、64条S27参数、40条S27定义；不保存来源工作簿。完整元素、核苷酸基团、电荷/渗透守恒、H2O/H+显式化均未证明。

