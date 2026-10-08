"""Negative controls for authority/source/semantic mapping, without modifying inputs."""
import copy,io,json,unittest,zipfile
import xml.etree.ElementTree as ET
from verify_pnas2017_active_authority import *
class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads((ROOT/CONFIG).read_text());cls.raw=(ROOT/S28).read_bytes()
        cls.book=workbook(cls.raw);cls.species=[r["Name"] for r in csvrows((ROOT/INPUTS[4]).read_bytes())]
        cls.f5=headers(cls.book,cls.species);cls.rows=csvrows((ROOT/MAPPING).read_bytes())
    def rejected_input(self,path,raw):
        def read(p):return raw if p==path else (ROOT/p).read_bytes()
        with self.assertRaises(IntegrityError):verify(read)
    def test_s28_hash_mutation(self): self.rejected_input(S28,self.raw+b"x")
    def test_species_permutation_semantic(self):
        b=copy.deepcopy(self.book);b["Fig. 2B"]["B2"],b["Fig. 2B"]["C2"]=b["Fig. 2B"]["C2"],b["Fig. 2B"]["B2"]
        with self.assertRaisesRegex(IntegrityError,"column order"):headers(b,self.species)
    def test_author_initial_mutation(self):
        raw=(ROOT/INPUTS[4]).read_bytes().replace(b"2,tRNAfMetCAU,3.54767184",b"2,tRNAfMetCAU,3.64767184")
        self.assertNotEqual(raw,(ROOT/INPUTS[4]).read_bytes());self.rejected_input(INPUTS[4],raw)
    def test_k1_mutation(self):
        raw=(ROOT/INPUTS[5]).read_bytes().replace(b"re0000000001_k1,1000",b"re0000000001_k1,1001")
        self.assertNotEqual(raw,(ROOT/INPUTS[5]).read_bytes());self.rejected_input(INPUTS[5],raw)
    def test_po4_normalization_semantic(self):
        raw=(ROOT/NORMALIZED).read_bytes();doc=ET.fromstring(raw)
        r=next(r for r in doc.findall(".//{*}reaction") if r.get("id")=="re0000000414")
        s=next(s for s in r.findall("{*}listOfProducts/{*}speciesReference") if s.get("species")=="PO4")
        s.set("stoichiometry","1")
        self.assertNotEqual(signatures((ROOT/SBML).read_bytes())[1],signatures(ET.tostring(doc))[1])
        self.rejected_input(NORMALIZED,ET.tostring(doc))
    def test_time_start_mutation(self):
        c=copy.deepcopy(self.config);c["time_grid"]["start_seconds"]=1e-5
        with self.assertRaisesRegex(IntegrityError,"grid"):check_config(c)
    def test_unresolved_qss_promotion(self):
        rows=copy.deepcopy(self.rows)
        r=next(r for r in rows if r["sheet_name"]=="Fig. 3A" and r["mapping_type"]!="TIME")
        r["status"]="RESOLVED";r["mapping_expression"]="guessed"
        with self.assertRaisesRegex(IntegrityError,"Unresolved QSS"):check_mapping(rows,self.book,self.species,self.f5)
    def test_figure_pass_promotion(self):
        c=copy.deepcopy(self.config);c["figure_reproduction"]["published_figure_reproduction"]="PASS"
        with self.assertRaisesRegex(IntegrityError,"figure promotion"):check_config(c)
if __name__=="__main__":unittest.main()
