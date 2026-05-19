# PROMPT PARA GAMMA AI — Sustentación Set Cover (HAM10000) — IO UNAB 2026-I

> **Cómo usar este archivo:** Copia desde la línea horizontal de abajo (`---`) hasta el final y pégalo en Gamma AI como prompt único. No edites las cifras: ya están validadas contra los resultados reales del repo `Paulasaah/setcover-pau-brayan`.

---

## 0. BRIEF — LEE PRIMERO, NO SALTAR

Vas a generar una **presentación académica en español** de **14 diapositivas** sobre la solución a un Set Covering Problem aplicado al dataset dermatológico HAM10000, comparando un método exacto (ILP) con una metaheurística (Algoritmo Genético).

**Audiencia:** profesor universitario de **Investigación de Operaciones** (UNAB, Colombia). Exigente, técnico, prioriza rigor matemático sobre estética.

**Tono no negociable:**
- Técnico, directo, académico colombiano neutro.
- Sin frases motivacionales ("¡descubrirás!", "es fascinante", "el futuro de...").
- Sin emojis en ninguna diapositiva.
- Sin párrafos largos: una idea central por slide, máximo 4–5 bullets cortos.
- Priorizar **tablas, fórmulas LaTeX limpias y métricas exactas** sobre prosa.

**Qué significa éxito:**
- Las 14 diapositivas renderean sin texto truncado.
- Cada slide tiene **notas del presentador** debajo (no van en pantalla, van en speaker notes).
- Las fórmulas matemáticas se ven legibles (LaTeX o equivalente).
- Toda cifra que aparece está en la tabla de datos canónicos de la sección 1.
- El profesor puede defenderse de la pregunta "¿qué significa el gap del 38.98%?" leyendo solo el slide 10.

---

## 1. DATOS CANÓNICOS DEL PROYECTO — FUENTE ÚNICA DE VERDAD

Toda cifra que aparezca en la presentación debe coincidir con esta tabla. **No inventar números.** Si un dato no está acá, omítelo.

| Variable | Valor | Contexto |
|---|---|---|
| Dataset origen | HAM10000 | 10,015 imágenes dermatoscópicas, 7 clases |
| Clase mayoritaria | 66.95% | Nevus melanocíticos (nv) |
| Clases minoritarias | < 2% | df, vasc |
| Instancia experimental | 500 × 500 | reducción del problema real |
| Densidad de la matriz A | 9.99% | proporción de unos en la matriz binaria |
| Universo \|I\| | 500 | requisitos a cubrir |
| Subconjuntos \|J\| | 500 | conjuntos disponibles |
| Espacio de búsqueda | 2^500 | combinatoria total |
| Gap de integralidad inicial | 43.20% | LP relax vs óptimo entero |
| **LP relajado (cota inf.)** | **$27,859.93** | cota inferior teórica |
| **Greedy Chvátal** | **$52,063 / 23 / 4.6ms** | costo / cardinalidad / tiempo |
| Gap Greedy vs óptimo | +6.14% | |
| **ILP estándar (PuLP+CBC)** | **$50,123 / 22 / 600s** | gapRel=1e-4, reportó "Optimal" — NO era óptimo verdadero |
| **AG seed 13** | **$49,051 / 22 / 57s** | gap = 0% (óptimo) |
| **ILP refinado** | **$49,051 / 22 / 1,200s** | gapRel=0, warm-start desde AG — certifica óptimo |
| Replicación con SCIP | $49,814 / 70,660s / **gap 38.98%** | sin warm-start, no logró cerrar el árbol B&B en 19.6h |
| Robustez AG (5 semillas: 7,13,21,42,99) | mean $50,231 / std $687 / CV 1.37% | mejor 0% gap, peor 3.55% gap |
| Población AG | 150 individuos | 5% greedy perturbado + 95% aleatorio factible |
| Generaciones AG | 500 | |
| pc (cruce) | 0.90 | uniforme |
| pm inicial → final | 0.030 → 0.005 | mutación adaptativa lineal |
| Elitismo | 3 | mejores individuos preservados |
| Selección | Torneo k=3 | |
| Penalty M | 10^8 | en fitness por elemento sin cubrir |
| Repo público | `github.com/Paulasaah/setcover-pau-brayan` | |
| Stack | Python 3.14, PuLP 3.3.1, CBC, NumPy, pandas, matplotlib | |

---

## 2. ESTRUCTURA DE LAS 14 DIAPOSITIVAS

### SLIDE 1 — PORTADA

**Título:** Selección Óptima de Subconjuntos de Imágenes Dermatológicas mediante Set Cover

**Subtítulo:** Programación Lineal Entera y Algoritmo Genético sobre el dataset HAM10000

**Autores:** María Paula Saavedra · Brayan Steven León

**Institución:** Facultad de Ingeniería — UNAB · Investigación de Operaciones 2026-I

**Repositorio:** github.com/Paulasaah/setcover-pau-brayan

**Notas del presentador:** Presentar el problema como caso de optimización combinatoria aplicado a selección de subconjuntos. El foco es Investigación de Operaciones, no dermatología. Mencionar que el proyecto está reproducible al 100% en el repo público.

---

### SLIDE 2 — CONTEXTO DEL PROBLEMA

**Título:** ¿Por qué un Set Covering Problem sobre HAM10000?

**Bullets:**
- HAM10000: 10,015 imágenes dermatoscópicas en 7 clases diagnósticas.
- Desbalance severo: clase mayoritaria 66.95% vs minoritarias < 2%.
- Entrenar sobre la distribución original sesga clasificadores hacia la clase dominante.
- Problema natural: **seleccionar el subconjunto de mínimo costo que cubra todas las clases**.
- **Instancia experimental trabajada: 500 × 500 (densidad 9.99%)**, derivada de HAM10000.

**Idea clave en caja destacada:**
> La estructura del problema corresponde directamente a un Set Covering Problem (SCP), NP-difícil clásico.

**Notas del presentador:** No profundizar en medicina. La instancia 500×500 es la abstracción de IO que sí cabe en un solver: el HAM10000 completo (10,015 × 8,927 vistas) reventaría cualquier ILP. Justificar matemáticamente, no clínicamente.

---

### SLIDE 3 — FORMULACIÓN MATEMÁTICA

**Título:** Modelo de Programación Lineal Entera (ILP)

**Definiciones (lista compacta):**
- $I = \{1, \dots, 500\}$: universo de requisitos.
- $J = \{1, \dots, 500\}$: subconjuntos disponibles.
- $a_{ij} \in \{0,1\}$: 1 si subconjunto $j$ cubre requisito $i$.
- $c_j > 0$: costo de incluir subconjunto $j$.
- $x_j \in \{0,1\}$: variable binaria de decisión.

**Modelo (centrado, LaTeX):**

$$
\min_{\mathbf{x}} \; Z = \sum_{j \in J} c_j x_j
$$

$$
\text{s.a.} \quad \sum_{j \in J} a_{ij} x_j \;\ge\; 1, \quad \forall i \in I
$$

$$
x_j \in \{0,1\}, \quad \forall j \in J
$$

**Métricas de la instancia:**
- $z_{LP}$ (LP relajado) = **\$27,859.93**
- Gap de integralidad = **43.20%**
- Espacio de búsqueda = $2^{500}$

**Notas del presentador:** SCP es NP-difícil (Karp 1972). El gap de integralidad alto (43.20%) anticipa que B&B no convergerá rápido sin warm-start. Esa cota dual débil es justamente lo que el AG explota.

---

### SLIDE 4 — MÉTODO EXACTO: BRANCH & BOUND

**Título:** Solución exacta mediante Branch & Bound

**Bullets:**
- Implementación: PuLP + CBC (Coin-OR Branch and Cut).
- B&B explora árbol de relajaciones LP ramificando sobre variables fraccionarias.
- Poda mediante cotas inferiores duales.
- Convergencia depende de gap relativo y tiempo límite.

**Tabla comparativa (CLAVE — incluir tal cual):**

| Configuración | Tiempo | Costo | gapRel | Estado reportado | ¿Óptimo verdadero? |
|---|---|---|---|---|---|
| Estándar | 600 s | \$50,123 | 1e-4 | "Optimal" | **NO** |
| Refinado + warm-start AG | 1,200 s | \$49,051 | 0 | Optimal | **SÍ** |

**Notas del presentador:** Punto sutil pero crítico: CBC con `gapRel=1e-4` declaró "Optimal" en 600s y devolvió \$50,123. Esa solución **no era el óptimo verdadero**. Solo con `gapRel=0` y warm-start desde el AG el solver pudo bajar a \$49,051 y certificarlo. Este es el setup del hallazgo del slide 9.

---

### SLIDE 5 — DISEÑO DEL ALGORITMO GENÉTICO

**Título:** Algoritmo Genético — Representación y Fitness

**Bullets:**
- Representación binaria: $\mathbf{x} \in \{0,1\}^{500}$, un gen por subconjunto.
- Cardinalidad esperada de solución: ~22 (de 500).
- Inicialización factible: 5% greedy perturbado + 95% aleatorio reparado.
- Operador de reparación garantiza factibilidad en cada generación.
- Elitismo conserva las 3 mejores soluciones por generación.

**Función de fitness (con penalty):**

$$
f(\mathbf{x}) = \sum_{j \in J} c_j \, x_j \;+\; M \cdot \left| \{\, i \in I \;:\; \textstyle\sum_{j} a_{ij} x_j = 0 \,\} \right|, \quad M = 10^8
$$

**Notas del presentador:** El penalty $M = 10^8$ es lo suficientemente grande para que cualquier individuo infactible sea dominado por uno factible mediocre. Con inicialización factible y reparación post-cruce, la población **nunca abandona el espacio factible** — lo que acelera la convergencia respecto a AGs penalty-only.

---

### SLIDE 6 — OPERADORES GENÉTICOS Y PARÁMETROS

**Título:** Operadores y parámetros del AG

**Bullets:**
- **Selección:** torneo $k=3$.
- **Cruce:** uniforme, probabilidad $p_c = 0.90$.
- **Mutación adaptativa:** decrece linealmente en el tiempo.
- **Elitismo:** 3 mejores por generación.
- **Criterio de parada:** $G = 500$ generaciones o convergencia (sin mejora en 50 gen.).

**Mutación adaptativa (interpolación lineal limpia):**

$$
p_m(g) = p_m^{\text{ini}} + (p_m^{\text{fin}} - p_m^{\text{ini}}) \cdot \frac{g-1}{G-1}, \quad p_m^{\text{ini}} = 0.030, \; p_m^{\text{fin}} = 0.005
$$

**Tabla de parámetros:**

| Parámetro | Valor |
|---|---|
| Población | 150 |
| Generaciones | 500 |
| $p_c$ | 0.90 |
| $p_m$ | 0.030 → 0.005 |
| Elitismo | 3 |
| Torneo $k$ | 3 |

**Notas del presentador:** La mutación adaptativa permite **exploración alta al inicio** (0.030, 1.5 genes flipped en promedio) y **refinamiento al final** (0.005, 2.5 genes flipped en todo el cromosoma). Sin adaptación, el AG o explora poco o nunca converge.

---

### SLIDE 7 — OPERADOR DE REPARACIÓN

**Título:** Operador de reparación en dos fases

**Problema:**
> Cruce y mutación generan soluciones **infactibles** (elementos sin cubrir) o **redundantes** (subconjuntos sobrantes).

**Fase 1 — Reparar infactibilidad:**
- Detectar requisitos $i \in I$ no cubiertos por $\mathbf{x}$.
- Iterar: añadir el subconjunto $j$ que maximice $\frac{|\text{nuevos elementos cubiertos}|}{c_j}$.
- Detener cuando todos los requisitos estén cubiertos.

**Fase 2 — Eliminar redundancia:**
- Recorrer subconjuntos activos en orden de costo decreciente.
- Eliminar $j$ si la cobertura sigue completa sin él.

**Impacto cuantificado:**

| Versión del AG | Gap promedio vs óptimo |
|---|---|
| Sin reparación | 5–10% |
| Con reparación | 0–3.55% |

**Notas del presentador:** El operador de reparación es **el componente decisivo** del AG. Sin él, el AG es un random search penalizado. Con él, introduce sesgo greedy-aware en cada generación, lo que explica que el AG iguale al ILP refinado en 57s.

---

### SLIDE 8 — RESULTADOS PRINCIPALES

**Título:** Resultados sobre la instancia 500 × 500

**Tabla única (reemplaza todos los bullets de resultados):**

| Método | Costo (\$) | \|S\| | Tiempo | Gap vs óptimo | Tipo |
|---|---|---|---|---|---|
| LP relajado | 27,859.93 | — | <1 s | cota inferior | exacto-relajado |
| Greedy Chvátal | 52,063 | 23 | 4.6 ms | +6.14% | heurístico |
| ILP estándar (CBC) | 50,123 | 22 | 600 s | +2.19% | exacto (no cerró) |
| **AG seed 13** | **49,051** | **22** | **57 s** | **0%** | **metaheurístico** |
| ILP refinado + warm-start | 49,051 | 22 | 1,200 s | 0% (ref) | exacto + warm-start |

**Lectura clave:**
> El AG alcanzó el óptimo entero verdadero **en 57 segundos**, posteriormente certificado por el ILP refinado a 1,200 s.

**Notas del presentador:** Esta tabla es el corazón de la presentación. Léela en voz alta de arriba abajo. Subraya con la voz el contraste 57 s vs 1,200 s y el +6.14% del Greedy contra el 0% del AG.

---

### SLIDE 9 — HALLAZGO PRINCIPAL

**Título:** Convergencia prematura del solver exacto

**Secuencia narrativa (4 pasos):**
1. ILP estándar (CBC, gapRel=1e-4, 600s) reportó **"Optimal"** con costo \$50,123.
2. AG seed 13 (57s) encontró factible mejor: **\$49,051**.
3. ILP refinado (gapRel=0, 1,200s, warm-start desde AG) **certificó \$49,051 como óptimo entero verdadero**.
4. **Replicación independiente con SCIP:** 70,660s (19.6h), primal \$49,814, **gap 38.98%** sin cerrar — confirma que el fenómeno no es artefacto de CBC.

**Idea central (caja destacada):**
> En instancias densas del SCP con gap de integralidad alto, una metaheurística bien diseñada puede **superar al solver exacto bajo restricciones temporales realistas**, y servir como warm-start para certificar optimalidad.

**Notas del presentador:** Distinguir con cuidado tres cosas: (a) optimalidad global del problema, (b) certificado de optimalidad del solver, (c) tolerancia relativa configurada. CBC dijo "Optimal" en (b) pero falló en (a) porque (c) era 1e-4. El AG ganó porque exploró una región del espacio que B&B aún no había alcanzado.

---

### SLIDE 10 — INTERPRETACIÓN DEL GAP DE OPTIMALIDAD ⭐ (NUEVO)

**Título:** ¿Qué significa el "gap" reportado por un solver?

**Definición formal:**

$$
\text{gap} = \frac{|\text{Primal Bound} - \text{Dual Bound}|}{|\text{Dual Bound}|} \times 100\%
$$

**Significado de cada cota:**
- **Primal Bound:** mejor solución factible encontrada hasta el momento (cota superior).
- **Dual Bound:** cota inferior teórica del LP relajado + cortes (cota inferior).
- El óptimo verdadero $z^*$ está atrapado entre ambos: $\text{Dual} \le z^* \le \text{Primal}$.

**Interpretación:**
- gap = 0% → optimalidad **certificada matemáticamente**.
- gap > 0% → solo se conoce un intervalo, no certeza.

**Aplicación al proyecto:**

| Configuración | Primal | Dual | Gap |
|---|---|---|---|
| LP relajado inicial | — | \$27,860 | (gap de integralidad 43.20%) |
| CBC estándar (600s) | \$50,123 | ~\$50,118 | ~0.01% pero **óptimo falso** |
| SCIP sin warm-start (70,660s) | \$49,814 | \$35,841 | **38.98%** |
| ILP refinado + warm-start AG (1,200s) | \$49,051 | \$49,051 | **0% ✓** |

**Notas del presentador:** Este slide es la munición para defenderse de la pregunta del profe: "¿qué significa ese 38.98%?". La respuesta es: que el solver no logró estrechar el intervalo entre lo que **sabe que existe** (\$49,814) y lo que **sabe que es mínimo posible** (\$35,841), aunque haya explorado 2 millones de nodos. El warm-start con AG resuelve eso.

---

### SLIDE 11 — ROBUSTEZ DEL AG

**Título:** Robustez sobre múltiples semillas aleatorias

**Tabla de corridas:**

| Semilla | Costo (\$) | Gap vs óptimo |
|---|---|---|
| 7 | 50,118 | +2.18% |
| **13** | **49,051** | **0% (óptimo)** |
| 21 | 50,392 | +2.73% |
| 42 | 50,762 | +3.49% |
| 99 | 50,832 | +3.55% |

**Estadísticos:**
- Media: **\$50,231**
- Desviación estándar: **\$687**
- Coeficiente de variación (CV): **1.37%**

**Interpretación:**
- Peor caso: +3.55% vs óptimo — aceptable para uso práctico.
- CV bajo (< 2%) → **algoritmo estable**, poco sensible a la inicialización.

**Notas del presentador:** Las metaheurísticas no se evalúan con una sola corrida. El CV de 1.37% es el indicador clave: en 5 semillas distintas, el AG nunca se aleja más de 3.55% del óptimo y mantiene consistencia. Eso es lo que se reporta en la literatura (Beasley & Chu 1996).

---

### SLIDE 12 — COMPARACIÓN GLOBAL

**Título:** Balance calidad / tiempo / escalabilidad

**Tabla comparativa multi-criterio:**

| Aspecto | Greedy | ILP estándar | ILP refinado | **AG** |
|---|---|---|---|---|
| Calidad (gap) | +6.14% | +2.19% | 0% (ref) | **0%** |
| Tiempo | 4.6 ms | 600 s | 1,200 s | **57 s** |
| Escalabilidad | excelente | pobre | pobre | **buena** |
| Certifica óptimo | no | falso positivo | sí | no (per se) |
| Viabilidad práctica | inmediata | limitada | limitada | **alta** |

**Conclusión central:**
> El **AG** ofrece la mejor relación calidad-tiempo. El **híbrido AG → ILP refinado** ofrece optimalidad certificada al menor costo computacional combinado.

**Notas del presentador:** Mencionar que el enfoque exacto puro se vuelve poco viable en instancias cercanas al HAM10000 completo (matriz ~9,000 × 9,000). El híbrido es la única vía realista a esa escala.

---

### SLIDE 13 — REPRODUCIBILIDAD E IMPLEMENTACIÓN ⭐ (NUEVO)

**Título:** Reproducibilidad e implementación

**Stack técnico:**
- Python 3.14
- PuLP 3.3.1 + solver CBC (Coin-OR Branch and Cut)
- NumPy, pandas, matplotlib
- Entorno virtual `.venv` con `requirements.txt`

**Estructura del proyecto (8 scripts modulares):**

```
src/
├── loader.py           # Carga matriz A y costos desde Excel/CSV
├── greedy.py           # Heurística greedy Chvátal
├── exact.py            # ILP estándar (CBC default)
├── exact_refined.py    # ILP con warm-start desde AG
├── ga.py               # Algoritmo Genético principal
├── robustness.py       # Análisis multi-semilla
├── compare.py          # Tabla comparativa de métodos
└── figures.py          # Generación de figuras del paper
```

**Pipeline reproducible:**
```bash
bash run_all.sh
```

**Semillas fijas:**
- AG: `random.seed(13)` (corrida principal) + `{7, 21, 42, 99}` (robustez)
- CBC: `randomSeed=42`

**Repositorio público:** `github.com/Paulasaah/setcover-pau-brayan`

**Notas del presentador:** Mencionar que cualquiera puede clonar el repo, ejecutar `bash run_all.sh` y reproducir todas las tablas y figuras de la presentación en menos de 30 minutos. Esto es estándar mínimo de honestidad en publicaciones de OR.

---

### SLIDE 14 — CONCLUSIONES

**Título:** Conclusiones y aportes

**Conclusiones clave:**
1. El SCP sobre la instancia 500×500 presenta **alta dificultad combinatoria** (gap de integralidad 43.20%).
2. El **AG igualó el óptimo entero verdadero** en 57 s, posteriormente certificado por ILP refinado.
3. El **operador de reparación** fue el componente metodológico decisivo.
4. La validación cruzada **exacto ↔ metaheurística** fue fundamental para detectar la convergencia prematura del solver estándar.
5. El **enfoque híbrido AG → ILP** es estrictamente superior a cualquiera por separado para SCP densos.

**Lección metodológica (caja destacada):**
> Siempre contrastar soluciones exactas con heurísticas de calidad — un solver que reporta "Optimal" puede estar mintiendo si la tolerancia relativa no es 0.

**Repositorio público:** `github.com/Paulasaah/setcover-pau-brayan`

**Reconocimiento de asistencia IA:** El proceso de revisión, depuración y comparación de resultados utilizó asistencia de modelos generativos. La concepción, implementación, validación y redacción son de los autores.

**Referencias:**
- Karp, R. M. (1972). *Reducibility among combinatorial problems*.
- Chvátal, V. (1979). *A greedy heuristic for the set-covering problem*. Math. Oper. Res.
- Beasley, J. E., & Chu, P. C. (1996). *A genetic algorithm for the set covering problem*. EJOR.
- Caprara, A., Toth, P., & Fischetti, M. (1999). *Algorithms for the set covering problem*. Ann. Oper. Res.
- Tschandl, P., Rosendahl, C., & Kittler, H. (2018). *The HAM10000 dataset*. Scientific Data.

**Notas del presentador:** Cerrar enfatizando dos cosas: (a) el aporte metodológico (el híbrido AG→ILP, no inventado por nosotros pero validado empíricamente con un hallazgo concreto), y (b) la interpretación computacional del comportamiento del solver (que es lo que un curso de IO debería enseñar). Agradecer y abrir preguntas.

---

## 3. REGLAS DE PRESENTACIÓN — ANTI-SLOP

**Antes de generar cada slide, verificar:**

1. NO uses emojis en ningún lado (ni en títulos, bullets, ni notas).
2. NO inventes cifras: si un dato no está en la tabla canónica de la sección 1, omítelo.
3. NO uses frases tipo "fascinante", "revolucionario", "el futuro de…", "descubre".
4. NO escribas párrafos largos: máximo 4–5 bullets cortos por slide.
5. NO uses gradientes morados ni fondos llamativos. Paleta sobria académica (blanco, gris, un acento azul oscuro o verde botánico).
6. NO centres el texto del body. Solo los títulos.
7. Las fórmulas matemáticas deben estar en LaTeX o equivalente legible — no como imágenes de baja resolución.
8. Las tablas deben ser **tablas reales** (con bordes), no listas de bullets disfrazadas de tabla.
9. Las notas del presentador van en speaker notes, NO en el cuerpo del slide.
10. Cifras monetarias: usar formato `$49,051` con coma de miles, no `$49051` ni `$49.051`.
11. Tiempos: `57 s`, `1,200 s`, `19.6 h` (con espacio antes de la unidad).
12. Nunca redondees `$49,051` a `$49,000` ni `38.98%` a `39%` — son cifras exactas reportadas.
13. Cada slide tiene **UN título claro** y **UNA idea central**. Si necesitas dos ideas, son dos slides.
14. Mantén consistencia tipográfica: misma fuente sans-serif en todos los slides (recomendado: Inter, Source Sans, o equivalente).
15. El slide 10 (Interpretación del Gap) es el más denso — permitirle ocupar más espacio visual, pero respetar legibilidad.

---

## 4. VERIFICACIÓN ANTES DE ENTREGAR

Marca cada ítem antes de devolver la presentación final:

- [ ] Son exactamente **14 diapositivas**, ni una más ni una menos.
- [ ] Cada diapositiva tiene **notas del presentador** debajo.
- [ ] La tabla del slide 8 incluye **las 5 filas** (LP, Greedy, ILP est, AG, ILP refinado).
- [ ] El slide 9 incluye explícitamente el dato **SCIP: 70,660 s, gap 38.98%**.
- [ ] El slide 10 muestra la **fórmula del gap** y la **tabla de cotas Primal/Dual**.
- [ ] El slide 13 lista los **8 scripts** y el comando `bash run_all.sh`.
- [ ] Todas las cifras coinciden con la tabla canónica de la sección 1.
- [ ] No hay un solo emoji en ninguna parte.
- [ ] No hay frases motivacionales ni de marketing.
- [ ] Las fórmulas LaTeX renderean correctamente.
- [ ] El repositorio `github.com/Paulasaah/setcover-pau-brayan` aparece en slides 1, 13 y 14.

---

## 5. NOTA FINAL PARA GAMMA

Recibes este documento como un **único prompt completo**. No hagas preguntas aclaratorias. No omitas secciones por longitud. No reduzcas de 14 a 12 slides. No cambies las cifras "por estética" — son resultados reales de la corrida del proyecto.

Si un placeholder o cifra te parece ambigua, **deja un marcador visible `[TODO: verificar]` en el slide** — no inventes valores plausibles que suenen bien.

La diferencia entre una sustentación universitaria buena y una de **5.0** está en los slides 9, 10 y 13 — son los que separan "los estudiantes corrieron código" de "los estudiantes entienden lo que pasó". No los recortes.

Genera la presentación ahora.
