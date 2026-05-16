"""Análisis de robustez del GA sobre 5 semillas independientes."""
import json
import time
from pathlib import Path
import numpy as np
from loader import load_instance, PROJECT_ROOT
from ga import run_ga

RESULTS = PROJECT_ROOT / "results"
SEEDS = [7, 13, 21, 42, 99]


def main():
    A, c = load_instance()
    print(f"Robustness over seeds: {SEEDS}")
    all_runs = []
    for seed in SEEDS:
        print(f"\n[seed={seed}]")
        t0 = time.time()
        r = run_ga(A, c, seed=seed)
        r["time_s"] = time.time() - t0
        all_runs.append(r)
        print(
            f"  cost ${r['cost']:,.2f}, |S|: {r['n_selected']}, "
            f"time: {r['time_s']:.2f}s"
        )

    costs = np.array([r["cost"] for r in all_runs])
    mean = float(costs.mean())
    std = float(costs.std(ddof=1))
    cv = std / mean

    summary = {
        "seeds": SEEDS,
        "results": [
            {
                "seed": r["seed"],
                "cost": r["cost"],
                "n_selected": r["n_selected"],
                "time_s": r["time_s"],
            }
            for r in all_runs
        ],
        "mean": mean,
        "std": std,
        "coefficient_of_variation": cv,
        "min_cost": float(costs.min()),
        "max_cost": float(costs.max()),
    }
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "robustness.json", "w") as f:
        json.dump(summary, f, indent=2)

    histories = [
        {
            "seed": r["seed"],
            "best_history": r["best_history"],
            "avg_history": r["avg_history"],
        }
        for r in all_runs
    ]
    with open(RESULTS / "ga_histories.json", "w") as f:
        json.dump(histories, f, indent=2)

    print(
        f"\nMean: ${mean:,.2f} | Std: ${std:,.2f} | "
        f"CV: {cv*100:.3f}% | min: ${costs.min():,.2f} | max: ${costs.max():,.2f}"
    )
    return summary


if __name__ == "__main__":
    main()
