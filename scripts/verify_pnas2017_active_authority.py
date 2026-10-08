"""Current authority/source integrity only; never assigns figure/scientific PASS."""
from __future__ import annotations
import argparse, csv, hashlib, io, json, posixpath, re, subprocess, sys, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
BASE="0b6f9ad649a7e283e440e0294a021123551f6858"
AUTHOR="models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/"
SBML="models/pnas2017_full_reference/original/fMGG_synthesis.xml"
S28="references/PNAS2017_Matsuura/raw/pnas.1615351114.sd28.xlsx"
NORMALIZED="models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml"
CONFIG="configs/benchmarks/pnas2017_reference/benchmark.json"
MAPPING="models/pnas2017_full_reference/audit/s28_observable_mapping.csv"
INPUTS=(SBML,S28,AUTHOR+"fMGG_synthesis.m",AUTHOR+"fMGG_synthesis_Sample.m",
        AUTHOR+"dat/fMGG_synthesis_initial_values.csv",AUTHOR+"dat/fMGG_synthesis_parameters.csv",NORMALIZED)
SHEETS=["Fig. 2B","Fig. 3A","Fig. 5A","Fig. S1B","Fig. S4","Fig.S7A","Fig. S8"]
ACTIVE=[".github/workflows/matlab-ci.yml","README.md","configs/README.md","data/README.md","data/provenance.csv",
"docs/README.md","docs/interfaces/flow_contract.json","docs/model_card.md","docs/project/benchmark_registry.md",
"matlab/README.md","results/README.md","schemas/README.md","tasklist.md"]
ALLOW=sorted(ACTIVE+[".gitattributes","docs/migration/pnas2017_active_authority_inventory.md","docs/migration/pnas2017_active_authority_inventory.csv"])
class IntegrityError(ValueError): pass
def need(ok,detail):
    if not ok: raise IntegrityError(detail)
def digest(raw): return hashlib.sha256(raw).hexdigest()
def csvrows(raw): return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
def git(*args): return subprocess.check_output(["git",*args],cwd=ROOT)
def col(n):
    out=""
    while n: n,r=divmod(n-1,26);out=chr(65+r)+out
    return out
def workbook(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        need(z.testzip() is None,"S28 ZIP CRC")
        for p in z.namelist():
            if p.endswith((".xml",".rels")): ET.fromstring(z.read(p))
        shared=[]
        if "xl/sharedStrings.xml" in z.namelist():
            shared=["".join(x.itertext()) for x in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("{*}si")]
        rels={x.get("Id"):x.get("Target") for x in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        result={}
        for s in ET.fromstring(z.read("xl/workbook.xml")).findall("{*}sheets/{*}sheet"):
            rid=s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            target=rels[rid]
            path=target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/"+target)
            cells={}
            for c in ET.fromstring(z.read(path)).findall(".//{*}c"):
                v=c.find("{*}v")
                value=v.text if v is not None else ""
                if c.get("t")=="s": value=shared[int(value)]
                elif c.get("t")=="inlineStr": value="".join(c.find("{*}is").itertext())
                cells[c.get("r")]=value
            result[s.get("name")]=cells
        need(list(result)==SHEETS,"S28 seven sheet names/order")
        return result
def headers(book,species):
    for sheet,start in [("Fig. 2B",2),("Fig. 3A",3)]:
        actual=[book[sheet].get(col(i)+"2","").strip("'") for i in range(start,start+241)]
        need(actual==species,"S28 exact species column order: "+sheet)
    f5=[book["Fig. 5A"].get(col(i)+"2","").strip("'") for i in range(2,45)]
    need(len(set(f5))==43 and set(f5)<=set(species),"S28 Fig5A exact43 source IDs")
    return f5
def signatures(raw):
    model=ET.fromstring(raw).find("{*}model")
    sig=[];literal_count=0
    for r in model.findall("{*}listOfReactions/{*}reaction"):
        roles=[]
        for side in ("listOfReactants","listOfProducts"):
            items=[]
            for s in r.findall("{*}"+side+"/{*}speciesReference"):
                sm=s.find("{*}stoichiometryMath")
                if sm is not None:
                    numbers=sm.findall(".//{*}cn")
                    need(len(numbers)==1 and len(list(sm.iter()))==3,"Nonliteral stoichiometryMath")
                    value=float(numbers[0].text);literal_count+=1
                else: value=float(s.get("stoichiometry","1"))
                items.append((s.get("species"),value))
            roles.append(items)
        sig.append((r.get("id"),roles))
    return model,sig,literal_count
def check_config(c):
    need(c["model_id"]=="PNAS2017_full_reference","Active model")
    need(c["time_grid"]=={"expression":"logspace(-4,3,200)","start_seconds":1e-4,"end_seconds":1000,"points":200},"Author executable grid")
    need(c["solver"]=={"engine":"AUTHOR_MATLAB","name":"ode15s","NonNegative":"1:241","RelTol":1e-3,"AbsTol":1e-9,"post_integration_clipping":False},"Author solver semantics")
    need(c["figure_reproduction"]=={"execution":"PAUSED_BY_USER","comparison":"NOT_RUN","published_figure_reproduction":"NOT_ESTABLISHED"},"No figure promotion")
    need(c["experimental_validation"]=="NOT_ESTABLISHED" and c["reduced_model_status"]=="NOT_VALIDATED" and c["mechanistic_decisions"]=="968_PENDING","Scientific boundaries")
    need(set(c["source_hashes"])==set(INPUTS),"Frozen input set")
    expected_paths={"source_sbml":SBML,"author_rhs":INPUTS[2],"author_sample":INPUTS[3],"initial_values":INPUTS[4],"parameters":INPUTS[5],"normalized_sbml":NORMALIZED,"s28_path":S28,"observable_mapping":MAPPING}
    need(all(c[k]==v for k,v in expected_paths.items()),"Canonical input/mapping paths")
def check_mapping(rows,book,species,f5):
    need(len(rows)==528,"Mapping scope525 states plus3 time columns")
    for sheet,start,ids in [("Fig. 2B",2,species),("Fig. 3A",3,species),("Fig. 5A",2,f5)]:
        group=[r for r in rows if r["sheet_name"]==sheet and r["mapping_type"]!="TIME"]
        need(len(group)==len(ids),"Mapping coverage "+sheet)
        for offset,(r,sid) in enumerate(zip(group,ids)):
            need(r["source_column"]==col(start+offset) and r["source_species_id_or_formula"]==sid,"Mapping column/ID "+sheet)
            need(r["source_header"]==book[sheet][r["source_column"]+"2"],"Mapping source header "+sheet)
            need(bool(r["mapping_evidence"]),"Mapping evidence absent")
            if sheet=="Fig. 3A":
                need(r["status"]=="UNRESOLVED" and not r["mapping_expression"] and r["mapping_type"]=="DERIVED_OBSERVABLE","Unresolved QSS cannot be promoted")
            else:
                need(r["status"]=="RESOLVED_IDENTITY_ONLY" and r["mapping_expression"]==sid and r["mapping_type"]=="DIRECT_SPECIES","Direct identity boundary")
    for sheet,column in [("Fig. 2B","A"),("Fig. 3A","B"),("Fig. 5A","A")]:
        times=[r for r in rows if r["sheet_name"]==sheet and r["mapping_type"]=="TIME"]
        need(len(times)==1 and times[0]["source_column"]==column and times[0]["status"]=="RESOLVED","Time identity "+sheet)
def verify(read=None):
    read=read or (lambda p:(ROOT/p).read_bytes())
    c=json.loads(read(CONFIG));check_config(c)
    for p,h in c["source_hashes"].items():
        need(digest(read(p))==h,"Registered hash mismatch: "+p)
        need(h==digest(git("show",BASE+":"+p)),"Input hash differs from baseline source: "+p)
    need(c["source_hashes"][SBML]=="dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df","Canonical SBML")
    need(c["source_hashes"][S28]=="8297f2348f5ebdfc3c14083577f2c5f276f35a7ee8ab30f8a37fd8431ef565ec" and len(read(S28))==2317660,"Canonical S28")
    model,sig,count=signatures(read(SBML));_,nsig,ncount=signatures(read(NORMALIZED))
    species=[s.get("id") for s in model.findall("{*}listOfSpecies/{*}species")]
    reactions=[r[0] for r in sig]
    need(len(species)==241 and len(set(species))==241 and len(reactions)==968 and count==3854 and ncount==0 and sig==nsig,"Inventory/normalization identity")
    need(("PO4",2.0) in next(roles[1] for rid,roles in sig if rid=="re0000000414"),"Source PO4 coefficient2")
    initials=csvrows(read(c["initial_values"]));params=csvrows(read(c["parameters"]))
    need([r["Name"] for r in initials]==species and sum(float(r["Value"])>0 for r in initials)==27,"Author initial241 mapping/27 positive")
    need([r["Name"] for r in params[:968]]==[rid+"_k1" for rid in reactions] and len(params)==969 and params[-1]["Name"]=="default","Author parameter968 mapping/sentinel")
    need(sum(float(r["Value"])>0 for r in params[:968])==483,"Author positive k1 count")
    need(len(csvrows(read("models/pnas2017_full_reference/audit/modules.csv")))==26,"26 subsystem inventory")
    need(re.search(rb"logspace\(\s*-4\s*,\s*3\s*,\s*200\s*\)",read(c["author_sample"])) is not None,"Author executable grid authority")
    book=workbook(read(S28));f5=headers(book,species);check_mapping(csvrows(read(MAPPING)),book,species,f5)
    flow=json.loads(read("docs/interfaces/flow_contract.json"))
    need(flow["model_id"]=="PNAS2017_full_reference" and flow["canonical_model_source"]==SBML and flow["source_sha256"]==c["source_hashes"][SBML],"Active flow authority")
    need(flow["model_boundary"]=={"translation_only":True,"transcription":False,"species":241,"reactions":968,"subsystem_xmls":26},"Flow model boundary")
    need(flow["figure_execution"]=="PAUSED_BY_USER" and flow["reduction"]["future_model_status"]=="NOT_VALIDATED","Flow status scope")
    status=json.loads(read("docs/project/pnas2017_active_status.json"))
    need(status["active_model"]==c["model_id"] and not status["legacy_active"] and status["figure_execution"]=="PAUSED_BY_USER","Active status authority")
    need(status["status"]["pnas_figure_benchmark_status"]=="PAUSED_NOT_ESTABLISHED" and status["status"]["reduced_model_status"]=="NOT_VALIDATED","No active scientific promotion")
    need(all(status["status"][k].startswith("PAUSED") for k in ("fig2b_reproduction","fig3a_reproduction","fig5a_reproduction","supplementary_figure_reproduction")),"Per-panel pause boundaries")
    need(status["status"]["fig3a_mapping"]=="UNRESOLVED_EXACT_QSS_TRANSFORM" and status["status"]["experimental_validation_status"]=="NOT_ESTABLISHED" and status["mechanistic_decisions"]=="968_PENDING","Observable/experimental/kinetic status boundaries")
    preserve=json.loads(read("docs/migration/pnas2017_preservation_contract.json"))
    need(preserve["base_commit"]==BASE and preserve["allowed_existing_changes"]==ALLOW,"Preservation scope")
    original=set(git("ls-tree","-r","--name-only",BASE).decode().splitlines())
    need(set(preserve["original_tracked_paths"])==original,"Complete baseline inventory")
    changed=set(git("diff",BASE,"--name-only").decode().splitlines())
    need(not (changed & original-set(ALLOW)),"Protected original Git blobs changed: "+str(sorted(changed & original-set(ALLOW))))
    need(git("rev-parse",preserve["archive_tag"]).decode().strip()==preserve["archive_tag_object"],"Archive tag identity")
    for x in preserve["legacy_copies"]:
        need(digest(read(x["legacy_path"]))==x["sha256"],"Frozen legacy copy "+x["legacy_path"])
    for p in ACTIVE:
        text=read(p).decode("utf-8-sig")
        if p in ("README.md","docs/model_card.md","docs/project/benchmark_registry.md"):
            need("PNAS2017" in text[:150],"Current opening authority "+p)
        if p==".github/workflows/matlab-ci.yml":
            need("run_pnas2017_preflight.py" in text and "run_all_tests" not in text and "matlab-actions" not in text,"PNAS CI default")
    need((ROOT/"scripts/reproduce_pnas2017_reference.py").is_file() and (ROOT/"scripts/reproduce_pnas2017_reference.m").is_file(),"Primary entrypoints")
    return {"authority_source_integrity":"PASS","figure_execution":"PAUSED_BY_USER","figure_comparison":"NOT_RUN","published_figure_reproduction":"NOT_ESTABLISHED","experimental_validation":"NOT_ESTABLISHED","reduced_model_status":"NOT_VALIDATED","species":241,"reactions":968,"subsystems":26,"mapped_main_columns":528,"historical_git_blobs":"PRESERVED"}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--report",type=Path);a=parser.parse_args()
    try: result=verify();code=0
    except Exception as e: result={"authority_source_integrity":"FAIL","error":str(e)};code=1
    if a.report: a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result,indent=2));return code
if __name__=="__main__": sys.exit(main())
