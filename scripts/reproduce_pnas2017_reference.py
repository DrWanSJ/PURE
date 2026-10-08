"""Active PNAS reference entrypoint. Verification and optional author ODE; no figure work."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
from verify_pnas2017_active_authority import ROOT,verify
def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify",action="store_true")
    mode.add_argument("--execute-author",action="store_true")
    p.add_argument("--output-dir",type=Path)
    a=p.parse_args()
    result=verify()
    if a.verify: print(json.dumps(result,indent=2));return 0
    if a.output_dir is None:p.error("--execute-author requires a new external --output-dir")
    out=a.output_dir.resolve()
    if out.exists() or out.is_relative_to(ROOT.resolve()):p.error("Output must be a new external directory; frozen repository paths are protected")
    matlab=shutil.which("matlab")
    if not matlab: raise RuntimeError("MATLAB unavailable; source and verification remain usable")
    quote=lambda s:str(s).replace("'","''")
    batch="addpath('"+quote(ROOT/"scripts")+"'); reproduce_pnas2017_reference('"+quote(out)+"');"
    argv=[matlab,"-batch",batch]
    proc=subprocess.run(argv,capture_output=True,text=True,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    out.mkdir(parents=True,exist_ok=True)
    (out/"matlab_stdout.txt").write_text(proc.stdout,encoding="utf-8")
    (out/"matlab_stderr.txt").write_text(proc.stderr,encoding="utf-8")
    report={"exact_command_argv":argv,"python_argv":sys.argv,"exit_code":proc.returncode,"figure_generation":"NOT_RUN","comparison":"NOT_RUN"}
    (out/"launcher_manifest.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    manifest_path=out/"run_manifest.json"
    if manifest_path.is_file():
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["exact_command_argv"]=argv
        manifest["launcher_manifest_sha256"]=hashlib.sha256((out/"launcher_manifest.json").read_bytes()).hexdigest()
        manifest["config_sha256"]=hashlib.sha256((ROOT/"configs/benchmarks/pnas2017_reference/benchmark.json").read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2));return proc.returncode
if __name__=="__main__":sys.exit(main())
