"""Heurística greedy de Chvátal (1979) — baseline + warm-start del GA."""
import json
import time
from pathlib import Path
import numpy as np
from loader import load_instance, PROJECT_ROOT

RESULTS = PROJECT_ROOT / "results"


def greedy_chvatal(A, c):
    """Selecciona iterativamente el subconjunto con mejor razón costo/cobertura nueva."""
    m, n = A.shape
    selected = np.zeros(n, dtype=bool)
    covered = np.zeros(m, dtype=bool)
    while not covered.all():
        gain = A[~covered].sum(axis=0).astype(float)
        cand = (gain > 0) & (~selected)
        ratios = np.full(n, np.inf)
        ratios[cand] = c[cand] / gain[cand]
        j = int(np.argmin(ratios))
        selected[j] = True
        covered = covered | A[:, j].astype(bool)
    return selected


def main():
    A, c = load_instance()
    t0 = time.time()
    sel = greedy_chvatal(A, c)
    elapsed = time.time() - t0
    cost = float(c[sel].sum())
    sel_idx = sorted(np.where(sel)[0].tolist())
    result = {
        "method": "Greedy Chvátal",
        "cost": cost,
        "n_selected": int(sel.sum()),
        "selected": sel_idx,
        "time_s": elapsed,
    }
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "greedy.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Greedy: cost ${cost:,.2f}, |S|: {sel.sum()}, time: {elapsed:.4f}s")
    return result


if __name__ == "__main__":
    main()
