# Set Cover 500×500 — Solución Exacta y Algoritmo Genético

Proyecto final de la asignatura **Investigación de Operaciones** (Universidad Autónoma de Bucaramanga, 2026-I).

**Autores:** María Paula Saavedra · Brayan Steven León

## Descripción

Resolución del problema clásico de cubrimiento de conjuntos (*Set Covering Problem*) sobre una instancia de 500×500, mediante tres enfoques:

1. **Heurística greedy de Chvátal (1979)** — línea base
2. **Programación Lineal Entera con Branch & Bound** — solución exacta (PuLP + CBC)
3. **Algoritmo Genético (Beasley & Chu, 1996)** — metaheurística con operador de reparación

El problema se contextualiza en la selección óptima de subconjuntos de imágenes dermatológicas del dataset HAM10000 para entrenamiento de modelos de clasificación.

## Estructura del repositorio

```
.
├── data/                         # Instancia provista (read-only)
│   ├── set_cover_500x500.csv     # Matriz de incidencia 500×500
│   └── Costo_S.xlsx              # Vector de costos
├── src/
│   ├── loader.py                 # Carga canónica de la instancia
│   ├── greedy.py                 # Heurística de Chvátal
│   ├── exact.py                  # PLE con PuLP + CBC
│   ├── ga.py                     # Algoritmo Genético
│   ├── robustness.py             # Robustez sobre 5 semillas
│   ├── compare.py                # Tabla comparativa final
│   └── figures.py                # Generación de figuras IEEE
├── results/                      # Outputs JSON + métricas
├── paper/
│   ├── paper.tex                 # Documento IEEE
│   ├── refs.bib                  # Bibliografía
│   └── figures/                  # Figuras del paper (PNG 300 DPI)
├── requirements.txt
└── README.md
```

## Reproducir los resultados

```bash
# 1. Crear entorno virtual e instalar dependencias
python3 -m venv .venv
source .venv/bin/activate           # Linux/Mac
# .venv\Scripts\activate            # Windows
pip install -r requirements.txt

# 2. Validar la instancia
python src/loader.py

# 3. Ejecutar los métodos en orden
python src/greedy.py                # ~0.01s
python src/exact.py                 # hasta 600s (límite PLE)
python src/robustness.py            # ~3-5 min (5 corridas del GA)
python src/compare.py               # tabla resumen
python src/figures.py               # 5 figuras PNG

# 4. Compilar el paper LaTeX
cd paper
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

## Resultados de referencia

| Método              | Tipo                    | Costo aprox.     | \|S\| | Tiempo aprox. | Gap vs ILP |
|---------------------|-------------------------|-----------------:|------:|--------------:|-----------:|
| LP relajado         | Cota inferior teórica   | $27,859.93       | —     | <1s           | −44%       |
| Greedy Chvátal      | Heurística constructiva | ~$52,000         | ~23   | <0.01s        | ~+4%       |
| Algoritmo Genético  | Metaheurística          | ~$50,500         | ~23   | ~35s          | ~+1.5%     |
| ILP (CBC + B&B)     | Exacto                  | ~$50,000         | 22    | ≤600s         | ref        |

## Hiperparámetros del GA

| Parámetro              | Valor                          |
|------------------------|--------------------------------|
| Tamaño de población    | 150                            |
| Generaciones           | 500                            |
| Probabilidad cruce     | 0.90 (uniforme)                |
| Mutación inicial/final | 0.030 / 0.005 (adaptativa)     |
| Torneo                 | k=3                            |
| Elitismo               | 3 individuos                   |
| Semilla principal      | 13                             |
| Semillas robustez      | {7, 13, 21, 42, 99}            |

## Componentes clave del Algoritmo Genético

El GA implementa los 7 ingredientes propuestos por Beasley & Chu (1996):

1. **Codificación binaria** de 500 bits.
2. **Población inicial mixta**: 5% greedy perturbado + 95% aleatorio factible.
3. **Función de fitness** con penalización BIG_M = 10⁸ como red de seguridad.
4. **Selección por torneo** k=3.
5. **Cruce uniforme** con probabilidad 0.9 (Beasley & Chu).
6. **Mutación bit-flip adaptativa** decreciente de 3% a 0.5%.
7. **Operador de reparación** en dos fases (factibilidad + eliminación de redundancias).
+ **Elitismo** k=3 para convergencia monótona.

El **operador de reparación es el componente decisivo**: sin él, las brechas del GA se sitúan entre 5% y 10%; con él, por debajo del 2%.

## Referencias principales

- Karp, R. M. (1972). *Reducibility among combinatorial problems*. NP-completeness del SCP.
- Chvátal, V. (1979). *A greedy heuristic for the set-covering problem*. Mathematics of Operations Research.
- Beasley, J. E. & Chu, P. C. (1996). *A genetic algorithm for the set covering problem*. EJOR.
- Tschandl, P., Rosendahl, C., & Kittler, H. (2018). *The HAM10000 dataset*. Scientific Data.

## Licencia

Trabajo académico — uso educativo. Sin distribución comercial.
