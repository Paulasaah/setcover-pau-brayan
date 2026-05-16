#!/usr/bin/env bash
# Pipeline completo: corre los 6 scripts en orden y llena el paper.tex.
# Uso: bash run_all.sh
set -euo pipefail

cd "$(dirname "$0")"
if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi
source .venv/bin/activate

cd src
echo "=== [1/7] Loader (validación) ==="
python loader.py
echo
echo "=== [2/7] Greedy Chvátal ==="
python greedy.py
echo
echo "=== [3/7] ILP (PuLP + CBC, hasta 600s) ==="
python exact.py
echo
echo "=== [4/7] Robustez (5 semillas GA) ==="
python robustness.py
echo
echo "=== [5/7] Comparativa final ==="
python compare.py
echo
echo "=== [6/7] Figuras IEEE ==="
python figures.py
echo
echo "=== [7/7] Rellenar paper.tex ==="
python fill_paper.py
echo
echo "Pipeline completo. Subir paper/paper.tex + paper/figures/ + paper/refs.bib a Overleaf."
