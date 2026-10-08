"""Current PNAS evidence qualification, preserving mutating historical verifier outputs."""
import argparse,hashlib,json,os,platform,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=["verify_pnas2017_active_authority.py","verify_pnas2017_artifacts.py","verify_pnas2017_integration.py",
"verify_reaction_level_annotation.py","verify_reaction_level_annotation_v2.py","verify_reaction_level_contract.py",
"verify_species_information_contract.py","verify_reduction_audit_v0.py","verify_source_coordinate_certificate_v1.py",
"verify_pnas2017_reduction_evidence.py","verify_r3_preregistration_v1.py","verify_r3_bounded_closeout_v1.py"]
MUTATING=["docs/audit/pnas2017_integration/verification.json","docs/reduction/r3_source_reaction_candidate_map_v1.csv","docs/reduction/r3_preregistration_certificate_v1.json"]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--report-dir",type=Path,required=True);a=p.parse_args()
    out=a.report_dir.resolve()
    if out.exists() or out.is_relative_to(ROOT):p.error("Use a new external report directory")
    out.mkdir(parents=True)
    originals={p:(ROOT/p).read_bytes() for p in MUTATING}
    commands=[[sys.executable,"-B",str(ROOT/"scripts"/s)] for s in SCRIPTS]
    commands += [[sys.executable,"-B",str(ROOT/"scripts/verify_source_coordinate_pointwise_v1.py"),"--chart","v"+str(n),"--out",str(out/("pointwise_v"+str(n)+".json"))] for n in range(1,8)]
    commands += [[sys.executable,"-B","-m","unittest","discover","-s","scripts","-p","test_pnas2017_active_authority.py"],
                 [sys.executable,"-B","-m","unittest","discover","-s","scripts","-p","test_pnas2017_s28_status.py"]]
    results=[]
    try:
        for i,cmd in enumerate(commands,1):
            label=Path(cmd[2]).stem
            if label=="verify_pnas2017_integration":
                # Its current implementation writes a successor detail record.
                # Redirect only the destination; retain every original check and
                # never replace the hash-bound historical report.
                native=out/"current_integration_verification.json"
                code=("import sys;from pathlib import Path;"
                      f"sys.path.insert(0,{str(ROOT/'scripts')!r});"
                      "import verify_pnas2017_integration as v;"
                      f"v.OUT=Path({str(native)!r});raise SystemExit(v.main())")
                cmd=[sys.executable,"-B","-c",code]
            run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace")
            log=out/(str(i).zfill(2)+"_"+label+".txt")
            log.write_text(run.stdout+"\n"+run.stderr,encoding="utf-8")
            results.append({"argv":cmd,"exit_code":run.returncode,"log":log.name,"log_sha256":hashlib.sha256(log.read_bytes()).hexdigest()})
            print(json.dumps({"check":i,"command":Path(cmd[2]).name,"exit_code":run.returncode}),flush=True)
        rewrites=[]
        for path,raw in originals.items():
            current=(ROOT/path).read_bytes()
            if current!=raw:
                target=out/("native_"+Path(path).name);target.write_bytes(current)
                rewrites.append({"path":path,"native_output":target.name,"original_sha256":hashlib.sha256(raw).hexdigest(),"native_sha256":hashlib.sha256(current).hexdigest()})
        # Report writes are retained externally; differing protected bytes block qualification.
        report={"schema":"pnas2017_preflight/v1","git_HEAD":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "git_dirty_status":subprocess.check_output(["git","status","--porcelain=v1"],cwd=ROOT,text=True),
        "input_hashes":{("scripts/"+name):hashlib.sha256((ROOT/"scripts"/name).read_bytes()).hexdigest() for name in SCRIPTS},
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),"scope":"ENGINEERING_INTEGRITY_ONLY_FIGURES_PAUSED",
        "numerical_runtime":{"python_version":sys.version,"platform":platform.platform(),
                             "environment":{key:os.environ.get(key) for key in ("MKL_ENABLE_INSTRUCTIONS","MKL_NUM_THREADS","OMP_NUM_THREADS")}},
        "results":results,"historical_verifier_rewrites":rewrites,"all_checks_pass":all(r["exit_code"]==0 for r in results) and not rewrites,
        "figure_reproduction":"PAUSED_NOT_RUN","experimental_validation":"NOT_ESTABLISHED"}
        (out/"preflight.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    finally:
        for path,raw in originals.items():
            if (ROOT/path).read_bytes()!=raw:(ROOT/path).write_bytes(raw)
    print(json.dumps({"all_checks_pass":report["all_checks_pass"],"checks":len(results),"report":str(out/"preflight.json")},indent=2))
    return 0 if report["all_checks_pass"] else 1
if __name__=="__main__":sys.exit(main())
