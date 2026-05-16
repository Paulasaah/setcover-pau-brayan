"""Generación de 5 figuras estilo IEEE (300 DPI, serif, fondo blanco)."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from loader import load_instance, PROJECT_ROOT

RESULTS = PROJECT_ROOT / "results"
FIGS = PROJECT_ROOT / "paper" / "figures"

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 10,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def fig_convergence():
    with open(RESULTS / "ga_histories.json") as f:
        histories = json.load(f)
    with open(RESULTS / "ilp.json") as f:
        ilp = json.load(f)
    h = next(r for r in histories if r["seed"] == 13)
    gens = np.arange(1, len(h["best_history"]) + 1)
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    ax.plot(gens, h["best_history"], label="Mejor individuo", linewidth=1.2, color="#1f77b4")
    ax.plot(gens, h["avg_history"], label="Promedio población", linewidth=0.9, color="#ff7f0e", alpha=0.8)
    ax.axhline(ilp["cost"], color="#2ca02c", linestyle="--", linewidth=1.0,
               label=f"ILP $\\${ilp['cost']:,.0f}$")
    ax.set_xlabel("Generación")
    ax.set_ylabel("Costo")
    ax.set_title("Convergencia del AG (semilla 13)")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)
    fig.savefig(FIGS / "fig_convergencia_ga.png")
    plt.close(fig)


def fig_times():
    with open(RESULTS / "comparison.json") as f:
        comp = json.load(f)
    rows = [r for r in comp["comparison"] if r["time_s"] is not None]
    names = [r["metodo"].replace(" (seed 13)", "").replace(" (CBC + B&B)", "") for r in rows]
    times = [r["time_s"] for r in rows]
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    bars = ax.bar(names, times, color=["#999999", "#ff7f0e", "#1f77b4"])
    ax.set_yscale("log")
    ax.set_ylabel("Tiempo (s, escala log)")
    ax.set_title("Comparativa de tiempos de cómputo")
    for bar, t in zip(bars, times):
        ax.text(bar.get_x() + bar.get_width() / 2, t, f"{t:.2f}s",
                ha="center", va="bottom", fontsize=8)
    ax.grid(alpha=0.3, axis="y", which="both")
    fig.savefig(FIGS / "fig_comparativa_tiempos.png")
    plt.close(fig)


def fig_robustness():
    with open(RESULTS / "robustness.json") as f:
        robust = json.load(f)
    with open(RESULTS / "ilp.json") as f:
        ilp = json.load(f)
    seeds = [r["seed"] for r in robust["results"]]
    costs = [r["cost"] for r in robust["results"]]
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    ax.scatter(range(len(seeds)), costs, color="#1f77b4", s=60, zorder=3, label="Costo AG")
    ax.axhline(ilp["cost"], color="#2ca02c", linestyle="--", linewidth=1.0,
               label=f"ILP $\\${ilp['cost']:,.0f}$")
    ax.axhline(robust["mean"], color="#ff7f0e", linestyle=":", linewidth=1.0,
               label=f"Media AG $\\${robust['mean']:,.0f}$")
    ax.set_xticks(range(len(seeds)))
    ax.set_xticklabels([str(s) for s in seeds])
    ax.set_xlabel("Semilla")
    ax.set_ylabel("Costo final")
    ax.set_title("Robustez del AG — 5 semillas independientes")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)
    fig.savefig(FIGS / "fig_robustez.png")
    plt.close(fig)


def fig_hist_costos():
    A, c = load_instance()
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    ax.hist(c, bins=30, color="#1f77b4", edgecolor="black", alpha=0.85)
    ax.set_xlabel("Costo del subconjunto ($)")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Distribución de los 500 costos de la instancia")
    ax.grid(alpha=0.3, axis="y")
    fig.savefig(FIGS / "fig_hist_costos.png")
    plt.close(fig)


def fig_hist_cobertura():
    A, c = load_instance()
    cobertura = A.sum(axis=1)
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    ax.hist(cobertura, bins=20, color="#ff7f0e", edgecolor="black", alpha=0.85)
    ax.set_xlabel("Número de subconjuntos que cubren al elemento")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Cobertura por elemento (500 elementos)")
    ax.grid(alpha=0.3, axis="y")
    fig.savefig(FIGS / "fig_hist_cobertura.png")
    plt.close(fig)


def main():
    FIGS.mkdir(parents=True, exist_ok=True)
    print("Generating figures...")
    fig_convergence()
    print("  fig_convergencia_ga.png OK")
    fig_times()
    print("  fig_comparativa_tiempos.png OK")
    fig_robustness()
    print("  fig_robustez.png OK")
    fig_hist_costos()
    print("  fig_hist_costos.png OK")
    fig_hist_cobertura()
    print("  fig_hist_cobertura.png OK")


if __name__ == "__main__":
    main()
