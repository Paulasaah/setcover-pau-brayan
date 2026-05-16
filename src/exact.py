"""Método exacto: Programación Lineal Entera con PuLP + CBC (Branch and Bound)."""
import json
import time
from pathlib import Path
import pulp
from loader import load_instance, PROJECT_ROOT

RESULTS = PROJECT_ROOT / "results"


def solve_exact(A, c, time_limit=600, gap_rel=1e-4, warm_start=None):
    m, n = A.shape
    prob = pulp.LpProblem("SCP", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x{j}", cat="Binary") for j in range(n)]
    prob += pulp.lpSum(float(c[j]) * x[j] for j in range(n))
    for i in range(m):
        coverers = [j for j in range(n) if A[i, j] == 1]
        prob += pulp.lpSum(x[j] for j in coverers) >= 1, f"cover_{i}"

    if warm_start is not None:
        warm_set = set(warm_start)
        for j in range(n):
            x[j].setInitialValue(1 if j in warm_set else 0)

    solver = pulp.PULP_CBC_CMD(
        msg=False, timeLimit=time_limit, gapRel=gap_rel,
        warmStart=warm_start is not None,
    )
    t0 = time.time()
    prob.solve(solver)
    elapsed = time.time() - t0

    selected = sorted(
        [j for j in range(n) if x[j].varValue is not None and x[j].varValue > 0.5]
    )
    cost = float(sum(c[j] for j in selected))
    status = pulp.LpStatus[prob.status]
    return {
        "method": "ILP (PuLP + CBC)",
        "status": status,
        "cost": cost,
        "n_selected": len(selected),
        "selected": selected,
        "time_s": elapsed,
        "time_limit": time_limit,
    }


def solve_lp_relaxation(A, c):
    """Resolver la relajación LP para obtener cota inferior."""
    m, n = A.shape
    prob = pulp.LpProblem("SCP_LP", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x{j}", lowBound=0, upBound=1, cat="Continuous") for j in range(n)]
    prob += pulp.lpSum(float(c[j]) * x[j] for j in range(n))
    for i in range(m):
        coverers = [j for j in range(n) if A[i, j] == 1]
        prob += pulp.lpSum(x[j] for j in coverers) >= 1
    t0 = time.time()
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    elapsed = time.time() - t0
    return {"z_lp": float(pulp.value(prob.objective)), "time_s": elapsed}


def main():
    A, c = load_instance()
    print(f"Solving ILP on {A.shape[0]}x{A.shape[1]} instance...")
    lp = solve_lp_relaxation(A, c)
    print(f"LP relajada: z_LP = ${lp['z_lp']:,.2f} (cota inferior, {lp['time_s']:.2f}s)")
    print("Solving ILP (CBC, 600s limit)...")
    result = solve_exact(A, c, time_limit=600)
    result["z_lp"] = lp["z_lp"]
    result["gap_integrality"] = (result["cost"] - lp["z_lp"]) / result["cost"]
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "ilp.json", "w") as f:
        json.dump(result, f, indent=2)
    print(
        f"Status: {result['status']}, cost: ${result['cost']:,.2f}, "
        f"|S|: {result['n_selected']}, time: {result['time_s']:.2f}s, "
        f"gap integralidad: {result['gap_integrality']*100:.2f}%"
    )
    return result


if __name__ == "__main__":
    main()
