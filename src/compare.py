"""Tabla comparativa final de los 4 métodos."""
import json
from pathlib import Path
from loader import PROJECT_ROOT

RESULTS = PROJECT_ROOT / "results"


def main():
    with open(RESULTS / "ilp.json") as f:
        ilp = json.load(f)
    with open(RESULTS / "greedy.json") as f:
        greedy = json.load(f)
    with open(RESULTS / "robustness.json") as f:
        robust = json.load(f)
    # GA principal: seed=13
    seed13 = next(r for r in robust["results"] if r["seed"] == 13)

    ilp_cost = ilp["cost"]
    z_lp = ilp.get("z_lp")

    rows = [
        {
            "metodo": "LP Relajado",
            "tipo": "Cota inferior teórica",
            "costo": z_lp,
            "n_selected": None,
            "time_s": None,
            "gap_vs_ilp": (z_lp - ilp_cost) / ilp_cost if z_lp else None,
        },
        {
            "metodo": "Greedy Chvátal",
            "tipo": "Heurística constructiva",
            "costo": greedy["cost"],
            "n_selected": greedy["n_selected"],
            "time_s": greedy["time_s"],
            "gap_vs_ilp": (greedy["cost"] - ilp_cost) / ilp_cost,
        },
        {
            "metodo": "Algoritmo Genético (seed 13)",
            "tipo": "Metaheurística poblacional",
            "costo": seed13["cost"],
            "n_selected": seed13["n_selected"],
            "time_s": seed13["time_s"],
            "gap_vs_ilp": (seed13["cost"] - ilp_cost) / ilp_cost,
        },
        {
            "metodo": "ILP (CBC + B&B)",
            "tipo": "Exacto",
            "costo": ilp_cost,
            "n_selected": ilp["n_selected"],
            "time_s": ilp["time_s"],
            "gap_vs_ilp": 0.0,
            "status": ilp["status"],
        },
    ]
    summary = {"comparison": rows, "ilp_status": ilp["status"]}
    with open(RESULTS / "comparison.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"{'Método':<35} {'Costo':>12} {'|S|':>6} {'Tiempo':>10} {'Gap':>10}")
    print("-" * 75)
    for r in rows:
        cost_s = f"${r['costo']:,.2f}" if r["costo"] is not None else "-"
        s_s = f"{r['n_selected']}" if r["n_selected"] is not None else "-"
        t_s = f"{r['time_s']:.3f}s" if r["time_s"] is not None else "-"
        gap_s = f"{r['gap_vs_ilp']*100:+.3f}%" if r["gap_vs_ilp"] is not None else "-"
        print(f"{r['metodo']:<35} {cost_s:>12} {s_s:>6} {t_s:>10} {gap_s:>10}")
    return summary


if __name__ == "__main__":
    main()
