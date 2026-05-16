"""Algoritmo Genético para el SCP (Beasley & Chu, 1996).

Implementa los 7 ingredientes obligatorios:
1. Codificación binaria
2. Población inicial mixta (5% greedy perturbado + 95% aleatorio factible)
3. Fitness con penalización BIG_M
4. Selección por torneo k=3
5. Cruce uniforme p_c=0.9
6. Mutación bit-flip adaptativa 3% → 0.5%
7. Operador de reparación en 2 fases (factibilidad + redundancias)
+ Elitismo k=3
"""
import json
import time
import argparse
from pathlib import Path
import numpy as np
from loader import load_instance, PROJECT_ROOT
from greedy import greedy_chvatal

RESULTS = PROJECT_ROOT / "results"

BIG_M = 1e8


def repair(ind, A, c):
    """Operador de reparación Beasley & Chu (1996, §3.4) en 2 fases."""
    ind = ind.copy()
    # Fase 1: cubrir lo que falte usando greedy de Chvátal
    if ind.any():
        covered = A[:, ind].any(axis=1)
    else:
        covered = np.zeros(A.shape[0], dtype=bool)
    while not covered.all():
        gain = A[~covered].sum(axis=0).astype(float)
        cand = (gain > 0) & (~ind)
        ratios = np.full(len(c), np.inf)
        ratios[cand] = c[cand] / gain[cand]
        j = int(np.argmin(ratios))
        ind[j] = True
        covered = covered | A[:, j].astype(bool)
    # Fase 2: eliminar redundancias en orden de costo decreciente
    sel = np.where(ind)[0]
    order = sel[np.argsort(-c[sel])]
    for j in order:
        ind[j] = False
        if ind.any():
            still = A[:, ind].any(axis=1)
            if not still.all():
                ind[j] = True
        else:
            ind[j] = True
    return ind


def fitness(ind, A, c):
    if not ind.any():
        return BIG_M * A.shape[0]
    covered = A[:, ind].any(axis=1)
    uncovered = int((~covered).sum())
    return float(c[ind].sum()) + BIG_M * uncovered


def construct_random_cover(rng, A, c, coverers_per_elem):
    m, n = A.shape
    ind = np.zeros(n, dtype=bool)
    covered = np.zeros(m, dtype=bool)
    order = rng.permutation(m)
    for i in order:
        if not covered[i]:
            options = coverers_per_elem[i]
            j = int(rng.choice(options))
            ind[j] = True
            covered = covered | A[:, j].astype(bool)
    return ind


def initialize_population(rng, A, c, pop_size, greedy_solution):
    m, n = A.shape
    coverers_per_elem = [np.where(A[i] == 1)[0] for i in range(m)]
    pop = np.zeros((pop_size, n), dtype=bool)
    n_greedy = max(1, int(0.05 * pop_size))  # 5% greedy perturbado
    for k in range(n_greedy):
        ind = greedy_solution.copy()
        n_flips = int(rng.integers(2, 9))
        flips = rng.choice(n, size=n_flips, replace=False)
        ind[flips] = ~ind[flips]
        pop[k] = repair(ind, A, c)
    for k in range(n_greedy, pop_size):  # 95% aleatorio factible
        ind = construct_random_cover(rng, A, c, coverers_per_elem)
        pop[k] = repair(ind, A, c)
    return pop


def tournament(rng, pop, fits, k=3):
    n = len(pop)
    idx = rng.integers(0, n, size=k)
    winner = idx[int(np.argmin(fits[idx]))]
    return pop[winner].copy()


def uniform_crossover(rng, p1, p2):
    mask = rng.random(len(p1)) < 0.5
    return np.where(mask, p1, p2)


def mutate(rng, ind, p_mut):
    flips = rng.random(len(ind)) < p_mut
    return ind ^ flips


def run_ga(
    A, c, seed=13, pop_size=150, generations=500,
    p_cross=0.9, p_mut_ini=0.03, p_mut_fin=0.005,
    k_torneo=3, elitism=3, verbose=False,
):
    rng = np.random.default_rng(seed)
    m, n = A.shape

    greedy_sol = greedy_chvatal(A, c)
    pop = initialize_population(rng, A, c, pop_size, greedy_sol)
    fits = np.array([fitness(ind, A, c) for ind in pop])

    best_history = []
    avg_history = []

    for g in range(generations):
        if generations > 1:
            p_mut = p_mut_ini + (p_mut_fin - p_mut_ini) * g / (generations - 1)
        else:
            p_mut = p_mut_ini

        new_pop = np.zeros_like(pop)
        elite_idx = np.argsort(fits)[:elitism]
        for i, e in enumerate(elite_idx):
            new_pop[i] = pop[e]

        for i in range(elitism, pop_size):
            p1 = tournament(rng, pop, fits, k_torneo)
            p2 = tournament(rng, pop, fits, k_torneo)
            child = uniform_crossover(rng, p1, p2) if rng.random() < p_cross else p1.copy()
            child = mutate(rng, child, p_mut)
            child = repair(child, A, c)
            new_pop[i] = child

        pop = new_pop
        fits = np.array([fitness(ind, A, c) for ind in pop])
        best_history.append(float(fits.min()))
        avg_history.append(float(fits.mean()))
        if verbose and (g % 50 == 0 or g == generations - 1):
            print(f"  Gen {g}: best={fits.min():,.2f}, avg={fits.mean():,.2f}, p_mut={p_mut:.4f}")

    best_idx = int(np.argmin(fits))
    best_ind = pop[best_idx]
    return {
        "seed": seed,
        "cost": float(c[best_ind].sum()),
        "n_selected": int(best_ind.sum()),
        "selected": sorted(np.where(best_ind)[0].tolist()),
        "best_history": best_history,
        "avg_history": avg_history,
        "hyperparams": {
            "pop_size": pop_size,
            "generations": generations,
            "p_cross": p_cross,
            "p_mut_ini": p_mut_ini,
            "p_mut_fin": p_mut_fin,
            "k_torneo": k_torneo,
            "elitism": elitism,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--pop", type=int, default=150)
    parser.add_argument("--gens", type=int, default=500)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    A, c = load_instance()
    print(f"Running GA: seed={args.seed}, pop={args.pop}, gens={args.gens}...")
    t0 = time.time()
    result = run_ga(
        A, c, seed=args.seed, pop_size=args.pop, generations=args.gens, verbose=args.verbose,
    )
    result["time_s"] = time.time() - t0
    result["method"] = f"GA (seed {args.seed})"

    RESULTS.mkdir(exist_ok=True)
    out_path = RESULTS / f"ga_seed{args.seed}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(
        f"GA seed {args.seed}: cost ${result['cost']:,.2f}, "
        f"|S|: {result['n_selected']}, time: {result['time_s']:.2f}s"
    )
    return result


if __name__ == "__main__":
    main()
