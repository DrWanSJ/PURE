"""Read actual repository sources; do not generate a replacement model.

Runs the Python derivation, then compares its expressions and the parsed WL
expressions against model_definition.json and the generated MATLAB RHS.
"""
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys

import sympy as sp
from sympy.parsing.mathematica import parse_mathematica

ROOT = Path(__file__).resolve().parents[3]
DIM = ROOT / "models/literature_reference/dimensionless"
print("PYTHON:", sys.version)
print("SYMPY:", sp.__version__)
py = runpy.run_path(str(DIM / "derive_dimensionless.py"))


def plain(expr):
    expr = sp.sympify(expr)
    return expr.xreplace({s: sp.Symbol(str(s)) for s in expr.free_symbols})


def check(label, actual, expected):
    residual = sp.cancel(plain(actual) - plain(expected))
    assert residual == 0, (label, residual)
    print(label + ": PASS (0)")


source = json.loads((ROOT / "models/literature_reference/model_definition.json").read_text())
wl = (DIM / "verify_wolfram_v2.wl").read_text(encoding="utf-8")
alias = dict(zip(
    "kTX Ct Kd Kt kRs Cr Ka Kt2 Kn2 kTl Knt Kat Kn3 kEn Ce Kcp Knxp knd kld nN nA nT cN cA cT cC cL".split(),
    "k_TX C_TXcat K_TX_DNA K_TX_NTP k_RS C_RScat K_RS_A K_RS_T K_RS_NTP k_TL K_TL_nt K_TL_AT K_TL_NTP k_EN C_ENcat K_EN_CP K_EN_NXP k_ntdeg k_TLdeg n_NTP n_A n_T c_NTP0 c_A0 c_T0 c_CP0 c_TLcat0".split()))
alias.update(dict(zip(
    "muTX muRS muTL muEN muTLD kxTXN kxRSA kxRST kxRSN kxTLn kxTLa kxTLN kxENC kxENX rhoA rhoT rhoC".split(),
    "mu_TX mu_RS mu_TL mu_EN mu_TLdeg kappa_TX_NTP kappa_RS_A kappa_RS_T kappa_RS_NTP kappa_TL_nt kappa_TL_AT kappa_TL_NTP kappa_EN_CP kappa_EN_NXP rho_A rho_T rho_C".split())))
wl_env = {sp.Symbol(k): sp.Symbol(v) for k, v in alias.items()}
wl_env[sp.Symbol("fTA")] = plain(py["s23"])
wl_env[sp.Symbol("thD")] = 1/(1 + plain(py["kTXdna"]))


def assignment(name):
    return re.search(r"(?m)^" + re.escape(name) + r"\s*=\s*(.*?);", wl, re.S)[1]


def wparse(text):
    return parse_mathematica(text.replace("$s23", "fTA")).xreplace(wl_env)


env = {str(s): plain(s) for v in py.values() if isinstance(v, sp.Expr) for s in v.free_symbols}
env.update({"TXcat": plain(py["C_TXcat"]), "RScat": plain(py["C_RScat"]),
            "ENcat": plain(py["C_ENcat"]), "k_nt_deg": plain(py["k_ntdeg"]),
            "k_TL_deg": plain(py["k_TLdeg"]), "fTA": plain(py["s23"])})


def cparse(text):
    return sp.sympify(text.replace("p.", ""), locals=env)


wl_rates = dict(zip(["V_TX", "V_RS", "V_TL", "V_EN", "V_nt_deg", "V_TL_deg"],
                    ["Vtx", "Vrs", "Vtl", "Ven", "Vnd", "Vld"]))
py_rates = {"V_nt_deg": "V_ntdeg", "V_TL_deg": "V_TLdeg"}
for item in source["rates"]:
    key = item["id"]
    expected = cparse(item["codegen"])
    actual = wparse(assignment(wl_rates[key]))
    check("canonical vs WL rate " + key, actual, expected)
    check("canonical vs Python rate " + key, py[py_rates.get(key, key)], expected)
    env[key] = expected
    wl_env[sp.Symbol(wl_rates[key])] = actual

generated = (ROOT / "matlab/generated/rhs_pure_literature_reference.m").read_text(encoding="utf-8")
for item in source["rates"]:
    match = re.search(r"(?m)^" + item["id"] + r"\s*=\s*(.*?);", generated)
    check("canonical vs generated rate " + item["id"], cparse(match[1]), env[item["id"]])

canonical_rhs = [cparse(v["codegen"]) for v in source["state_codegen"]]
canonical_rhs += [env["V_nt_deg"], env["V_TL_deg"]]
names = "dNTP dNXP dnt dA dT dAT da dCP dC dTLc dDnt dDTL".split()
for i, (name, expected) in enumerate(zip(names, canonical_rhs)):
    check(f"canonical vs WL RHS {i+1}", wparse(assignment(name)), expected)
    check(f"canonical vs Python RHS {i+1}", py["rhs"][i], expected)
    if i < 10:
        match = re.search(r"dydt\(" + str(i+1) + r"\)\s*=\s*(.*?);", generated)
        check(f"canonical vs generated RHS {i+1}", cparse(match[1]), expected)

scales = list(wparse(assignment("scales")))
for i, value in enumerate(scales):
    check(f"state scale {i+1}", value, py["scales"][i])
for rule in assignment("subc").strip("{} \n").split(","):
    left, right = rule.split("->")
    state = wparse(left.strip())
    expected = {plain(k): plain(v) for k, v in py["subs_conc"].items()}[state]
    check("state mapping " + str(state), wparse(right), expected)

for name in ("vtx", "vrs", "vtl", "ven"):
    wl_env[sp.Symbol(name)] = wparse(assignment(name))
compact = list(wparse(assignment("compact")))
definitions = {}
for rule in assignment("dimDef").strip("{} \n").split(","):
    left, right = rule.split("->")
    # Preserve theta as a symbol here; the ordinary parser substitutes 1/(1+kappa).
    name = left.strip()
    definitions[sp.Symbol(alias.get(name, name))] = wparse(right)

py_defs = {plain(k): plain(v) for k, v in py["rho_defs"].items()}
for orig, expr in {**py["subs_K"], **py["subs_mu"]}.items():
    group = [s for s in expr.free_symbols if str(s).startswith(("mu_", "kappa_"))][0]
    py_defs[plain(group)] = plain(sp.solve(sp.Eq(orig, expr), group)[0])
for key, value in definitions.items():
    if str(key) != "thD":
        check("dimensionless definition " + str(key), value, py_defs[key])
check("DNA theta", definitions[sp.Symbol("thD")],
      1/(1 + py_defs[plain(py["kTXdna"])]))

for i, expr in enumerate(compact):
    check(f"WL vs Python compact {i+1}", expr, py["dy"][i])
    back = expr.subs(py_defs, simultaneous=True)
    direct = canonical_rhs[i].subs({plain(k): plain(v) for k, v in py["subs_conc"].items()},
                                   simultaneous=True)/(scales[i]*plain(py["k_ntdeg"]))
    check(f"canonical chain rule vs WL compact {i+1}", back, direct)

# Also check the preserved, human-readable compact reference itself.
reference = (DIM / "dimensionless_result.txt").read_text(encoding="utf-8")
ref_env = dict(env)
ref_env["theta_DNA"] = 1/(1 + plain(py["kTXdna"]))
for ref_name, py_name in [("v_TX", "vTX"), ("v_RS", "vRS"), ("v_TL", "vTL"), ("v_EN", "vEN")]:
    text = re.search(r"(?ms)^" + ref_name + r"\s*=\s*(.*?)(?=\n\s*\n)", reference)[1]
    value = sp.sympify(" ".join(text.split()), locals=ref_env, rational=True)
    check("compact reference rate " + ref_name, value, py[py_name])
    ref_env[ref_name] = value
for i in range(12):
    text = re.search(r"(?m)^dy" + str(i+1) + r"/dtau\s*=\s*(.*)$", reference)[1]
    check(f"compact reference ODE {i+1}", sp.sympify(text, locals=ref_env), py["dy"][i])
physical = {sp.Symbol("n_A"): 20, sp.Symbol("n_T"): 46}
for key, expected in py_defs.items():
    match = re.search(r"(?m)^" + re.escape(str(key)) + r"\s*=\s*(.*)$", reference)
    if match:
        value = sp.sympify(match[1], locals=ref_env, rational=True)
        check("compact reference parameter " + str(key), value.subs(physical), expected.subs(physical))

# State/rate topology and source provenance are independent of conservation.
assert all(not (v.free_symbols & {sp.Symbol("Dnt"), sp.Symbol("DTL")}) for v in canonical_rhs)
source_hash = hashlib.sha256((ROOT / "models/literature_reference/model_definition.json").read_bytes()).hexdigest()
assert source_hash in generated
print("CANONICAL HASH:", source_hash)
print("SOURCE BRIDGE ALL PASS")
