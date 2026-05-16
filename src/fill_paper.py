"""Sustituye los placeholders %%VAR%% del paper.tex con los resultados reales."""
import json
from pathlib import Path
from loader import PROJECT_ROOT

RESULTS = PROJECT_ROOT / "results"
PAPER_TEX = PROJECT_ROOT / "paper" / "paper.tex"


def fmt_money(v):
    return f"\\${v:,.2f}"


def fmt_pct(v):
    return f"{v*100:+.2f}".replace("+", "")


def main():
    with open(RESULTS / "ilp.json") as f:
        ilp = json.load(f)
    with open(RESULTS / "greedy.json") as f:
        greedy = json.load(f)
    with open(RESULTS / "robustness.json") as f:
        robust = json.load(f)

    seed_map = {r["seed"]: r for r in robust["results"]}
    seed13 = seed_map[13]
    ilp_cost = ilp["cost"]

    repl = {
        "%%ILP_STATUS%%": ilp["status"],
        "%%ILP_COST%%": fmt_money(ilp["cost"]),
        "%%ILP_NSEL%%": str(ilp["n_selected"]),
        "%%ILP_TIME%%": f"{ilp['time_s']:.2f}",
        "%%ILP_GAP%%": f"{ilp.get('gap_integrality', 0)*100:.2f}",
        "%%GREEDY_COST%%": fmt_money(greedy["cost"]),
        "%%GREEDY_NSEL%%": str(greedy["n_selected"]),
        "%%GREEDY_TIME%%": f"{greedy['time_s']:.4f}",
        "%%GREEDY_GAP%%": fmt_pct((greedy["cost"] - ilp_cost) / ilp_cost),
        "%%GA13_COST%%": fmt_money(seed13["cost"]),
        "%%GA13_NSEL%%": str(seed13["n_selected"]),
        "%%GA13_TIME%%": f"{seed13['time_s']:.2f}",
        "%%GA13_GAP%%": fmt_pct((seed13["cost"] - ilp_cost) / ilp_cost),
        "%%R_MEAN%%": fmt_money(robust["mean"]),
        "%%R_STD%%": fmt_money(robust["std"]),
        "%%R_CV%%": f"{robust['coefficient_of_variation']*100:.3f}",
    }
    for s in [7, 13, 21, 42, 99]:
        r = seed_map[s]
        repl[f"%%R{s}_C%%"] = fmt_money(r["cost"])
        repl[f"%%R{s}_S%%"] = str(r["n_selected"])
        repl[f"%%R{s}_G%%"] = fmt_pct((r["cost"] - ilp_cost) / ilp_cost)

    with open(PAPER_TEX) as f:
        tex = f.read()
    for k, v in repl.items():
        tex = tex.replace(k, str(v))
    with open(PAPER_TEX, "w") as f:
        f.write(tex)

    print(f"Paper actualizado: {PAPER_TEX}")
    print(f"  ILP: ${ilp['cost']:,.2f} ({ilp['status']}, {ilp['time_s']:.1f}s)")
    print(f"  Greedy: ${greedy['cost']:,.2f}")
    print(f"  GA seed 13: ${seed13['cost']:,.2f} (gap {(seed13['cost']-ilp_cost)/ilp_cost*100:+.2f}%)")
    print(f"  Robustez mean ${robust['mean']:,.2f} ± ${robust['std']:,.2f} (CV {robust['coefficient_of_variation']*100:.3f}%)")


if __name__ == "__main__":
    main()
