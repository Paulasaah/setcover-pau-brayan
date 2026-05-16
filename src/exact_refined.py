"""ILP refinado con warm-start desde la mejor solución del GA y time limit extendido."""
import json
from pathlib import Path
from loader import load_instance, PROJECT_ROOT
from exact import solve_exact, solve_lp_relaxation

RESULTS = PROJECT_ROOT / "results"


def main():
    A, c = load_instance()
    with open(RESULTS / "ga_seed13.json") as f:
        ga = json.load(f)
    warm = ga["selected"]
    print(f"Warm-start desde GA seed 13: ${ga['cost']:,.2f}, |S|={ga['n_selected']}")

    lp = solve_lp_relaxation(A, c)
    print(f"LP relajada: z_LP = ${lp['z_lp']:,.2f}")

    print("Solving ILP refinado (warm-start + 1200s + gapRel=0)...")
    result = solve_exact(A, c, time_limit=1200, gap_rel=0.0, warm_start=warm)
    result["z_lp"] = lp["z_lp"]
    result["gap_integrality"] = (result["cost"] - lp["z_lp"]) / result["cost"]
    result["warm_start_cost"] = ga["cost"]

    with open(RESULTS / "ilp_refined.json", "w") as f:
        json.dump(result, f, indent=2)
    print(
        f"Status: {result['status']}, cost: ${result['cost']:,.2f}, "
        f"|S|: {result['n_selected']}, time: {result['time_s']:.2f}s, "
        f"gap integralidad: {result['gap_integrality']*100:.2f}%"
    )
    if result["cost"] < ga["cost"] - 0.01:
        print(f"  → ILP MEJORÓ al GA por ${ga['cost'] - result['cost']:,.2f}")
    elif abs(result["cost"] - ga["cost"]) < 0.01:
        print(f"  → ILP confirma óptimo del GA (${result['cost']:,.2f})")
    else:
        print(f"  → ILP no superó al GA (GA: ${ga['cost']:,.2f}, ILP: ${result['cost']:,.2f})")


if __name__ == "__main__":
    main()
