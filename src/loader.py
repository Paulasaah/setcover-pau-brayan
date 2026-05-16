"""Carga canónica de la instancia 500x500."""
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA = PROJECT_ROOT / "data"


def load_instance(csv_path=None, xlsx_path=None):
    csv_path = csv_path or (DATA / "set_cover_500x500.csv")
    xlsx_path = xlsx_path or (DATA / "Costo_S.xlsx")
    A = pd.read_csv(csv_path, header=0).values.astype(np.int8)
    # Costo_S.xlsx tiene formato horizontal:
    # fila 0: ['Conjunto', 1, 2, ..., 500]
    # fila 1: ['Costo', 3771, 3254, ..., 2229]
    df = pd.read_excel(xlsx_path, engine="openpyxl", header=None)
    cost_row = df.iloc[1, 1:].values  # saltar "Costo" en col 0
    c = np.asarray(cost_row, dtype=float)
    m, n = A.shape
    assert (m, n) == (500, 500), f"A debe ser 500x500, es {(m, n)}"
    assert c.shape == (n,), f"c shape {c.shape} != ({n},)"
    return A, c


if __name__ == "__main__":
    A, c = load_instance()
    print(f"A: {A.shape}, dtype={A.dtype}")
    print(f"c: {c.shape}, min=${c.min():,.2f}, max=${c.max():,.2f}, mean=${c.mean():,.2f}")
    print(f"Densidad A: {A.mean()*100:.2f}%")
    print(f"Total de 1s: {int(A.sum())}")
    cobertura_por_elem = A.sum(axis=1)
    print(f"Cobertura por elemento: min={cobertura_por_elem.min()}, max={cobertura_por_elem.max()}, mean={cobertura_por_elem.mean():.1f}")
    print(f"Costo total si todos los subconjuntos: ${c.sum():,.2f}")
