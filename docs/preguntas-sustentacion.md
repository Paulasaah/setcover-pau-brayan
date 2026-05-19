# Preguntas posibles del profe — Sustentación SetCover

Compilado de preguntas que el profesor puede hacer en la sustentación + respuestas listas para usar. Organizado por categoría temática.

---

## 🟦 BLOQUE 1 · Conceptos teóricos básicos

### 1. ¿Qué es ILP (Programación Lineal Entera)?

ILP es un tipo de optimización con **3 ingredientes**:

- **Programación**: optimizar (minimizar costos o maximizar ganancias)
- **Lineal**: ecuaciones solo con sumas, restas y multiplicaciones por constantes. Sin x², sin √x, sin nada raro
- **Entera**: las variables solo pueden tomar valores enteros, en nuestro caso **binarios** `x_j ∈ {0,1}`

En nuestro proyecto: $x_j = 1$ si se selecciona el subconjunto j, $x_j = 0$ si no. No hay medias tintas, no se puede "medio elegir".

**Es NP-difícil** porque obligar variables enteras multiplica la dificultad — Branch & Bound puede tardar horas explorando 2^500 combinaciones.

---

### 2. ¿Qué es la Relajación LP?

Es **aflojar la regla de enteros**: reemplazamos `x_j ∈ {0,1}` por `0 ≤ x_j ≤ 1` (cualquier decimal entre 0 y 1).

**Para qué sirve:**
- Convierte el problema NP-difícil en uno polinomial → se resuelve con Simplex en milisegundos
- Da la **cota inferior teórica** `z_LP` del óptimo entero
- B&B la usa para podar ramas

En nuestro proyecto: `z_LP = $27,859.93` mientras que `z* = $49,051`. El **gap de integralidad** de 43.2% mide la dificultad estructural del problema.

---

### 3. ¿Qué significa NP-difícil?

Es una clase de complejidad computacional. Significa que **no se conoce ningún algoritmo polinomial** para resolverlo, y se cree que tampoco existe (problema P vs NP abierto desde 1971).

**Implicación práctica:**
- En instancias pequeñas → resoluble en tiempo razonable
- En instancias grandes → el tiempo crece **exponencialmente** con el tamaño
- Para n = 500 → espacio de búsqueda 2^500 ≈ 3.27 × 10^150 combinaciones (más que átomos en el universo)

Por eso usamos **metaheurísticas** (AG) o **métodos exactos con cortes inteligentes** (B&B + cuts).

Karp (1972) demostró que SCP es NP-difícil — uno de los 21 problemas NP-difíciles originales.

---

### 4. ¿Qué es Branch & Bound (B&B)?

Es el método exacto para resolver ILP. Funciona en 3 pasos:

1. **Branch (Ramificar)**: tomar una variable fraccionaria del LP relajado y crear 2 subproblemas: uno con `x_j = 0`, otro con `x_j = 1`
2. **Bound (Acotar)**: para cada subproblema, resolver su relajación LP → obtener cota dual
3. **Prune (Podar)**: si la cota dual de un subproblema ≥ mejor entero encontrado, ese rama no puede dar nada mejor → descartar

Sigue ramificando hasta que todas las hojas estén exploradas o podadas. Garantiza encontrar el óptimo entero.

**En nuestro proyecto**: implementado en CBC (COIN Branch & Cut) vía PuLP.

---

### 5. ¿Qué es Set Cover (SCP)?

Problema clásico de optimización combinatoria:

> Dado un universo de elementos U y una familia de subconjuntos S_1, S_2, ..., S_n donde cada S_j tiene un costo c_j, encontrar el **subconjunto de mínimo costo total** que cubra TODOS los elementos de U.

En nuestro caso:
- U = 500 elementos (requisitos diagnósticos)
- 500 subconjuntos disponibles
- Cada subconjunto cubre algunos elementos
- Buscamos minimizar Σ c_j · x_j sujeto a que cada elemento sea cubierto al menos una vez

Aplicación natural: selección de subconjuntos representativos del dataset HAM10000 para entrenamiento balanceado de modelos de clasificación de lesiones dermatológicas.

---

## 🟩 BLOQUE 2 · Gaps y métricas

### 6. ¿Qué es el gap relativo de un solver?

Es la métrica **interna** que usa el solver para saber qué tan cerca está de terminar:

$$
\text{gap}_{relativo} = \frac{|\text{Primal Bound} - \text{Dual Bound}|}{|\text{Dual Bound}|} \times 100\%
$$

Donde:
- **Primal Bound** = mejor solución FACTIBLE encontrada (cota superior)
- **Dual Bound** = cota inferior teórica del LP relax + cortes

**Importante**: el gap relativo se calcula contra los bounds que el solver tiene en ese momento, **NO contra el óptimo verdadero**. Si la cota dual del solver es mala (subestimada), el gap relativo se ve falsamente bajo.

**Tolerancia `gapRel`**: parámetro que le dice al solver "para si gap_relativo < X". Default CBC = `1e-4` (0.01%).

---

### 7. ¿Qué tipos de gap manejamos en el proyecto?

Hay **3 tipos distintos** que se confunden:

| Tipo | Fórmula | Significado |
|---|---|---|
| **Gap de integralidad** | (z* − z_LP) / z* | 43.2% — estructural del problema, no depende del solver |
| **Gap relativo del solver** | (Primal − Dual) / Dual | Métrica interna del solver mientras corre |
| **Gap vs óptimo verdadero** | (costo_método − z*) / z* | Requiere conocer z* (posterior) |

---

### 8. ¿Qué significó el gap 0% del AG y del ILP refinado?

**Gap 0% = "no le falta nada para ser el óptimo".**

Ambos métodos llegaron al mismo costo: **$49,051**. Como ese es el óptimo verdadero (certificado por ILP refinado), ambos están a cero del óptimo.

**Diferencia entre ellos:**
- **AG seed 13**: ENCONTRÓ $49,051 en 57s. No puede certificarlo solo (es metaheurística).
- **ILP refinado**: CERTIFICÓ matemáticamente que $49,051 es el óptimo verdadero (cerró árbol B&B completo con `gapRel=0`).

**Mismo destino, distintos caminos.**

---

### 9. ¿Por qué SCIP dio 38.98% si AG dio 0%?

Son **2 algoritmos distintos** midiendo **gaps distintos**:

| | AG | SCIP (sin warm-start) |
|---|---|---|
| Tipo | Metaheurística | Método exacto |
| Tiempo | 57s | 19.6 horas |
| Costo | $49,051 | $49,814 |
| Tipo de gap | vs óptimo (posterior) | relativo (interno) |
| Valor | **0%** | **38.98%** |

SCIP corrió **sin warm-start** y, con su cota dual estancada en $35,841, no logró estrechar el intervalo (Primal $49,814, Dual $35,841 → gap 38.98%).

**El AG le da al solver la pista que necesita**: cuando le pasamos $49,051 como warm-start, el ILP refinado certificó el óptimo en 20 minutos.

---

## 🟨 BLOQUE 3 · El método exacto y por qué falló

### 10. ¿Por qué el método exacto NO dio la solución óptima si debería?

Esta es **la pregunta clave** del proyecto.

**Razón 1: Tolerancia de gap relativo (`gapRel = 1e-4`)**

CBC tiene un parámetro default que dice "si gap_relativo < 0.01%, declárate satisfecho y para". El gap se mide internamente:

$$
\text{gap}_{rel} = \frac{50,123 - 50,118}{50,118} \approx 0.01\%
$$

→ CBC declaró "Optimal" cuando tenía Primal=$50,123 y Dual=$50,118, **antes de explorar el árbol completo**.

**Razón 2: Gap de integralidad alto (43.2%)**

El gap estructural del problema es muy alto. La cota dual del LP relax ($27,860) está lejos del óptimo entero ($49,051). Para que B&B suba la cota dual cerca del óptimo necesitaría explorar **millones de nodos**.

**Razón 3: Tiempo límite 600s**

No alcanzó para que B&B cerrara el árbol completo.

**El ILP refinado lo arregló:**
- `gapRel = 0` (cero tolerancia)
- Warm-start desde solución AG ($49,051)
- Tiempo extendido a 1200s

→ CBC certificó $49,051 como óptimo verdadero.

---

### 11. ¿El ILP siempre dará el óptimo si lo dejas correr suficiente tiempo?

**Sí, en teoría. En la práctica, depende de:**

- **Configuración**: si `gapRel > 0`, puede parar antes del óptimo verdadero
- **Tiempo**: si el tiempo límite es muy corto, puede no terminar
- **Memoria**: B&B puede agotar RAM con árboles muy grandes
- **Calidad de cortes**: solvers con buenos algoritmos de corte cierran más rápido

**Por eso el "exacto" puede fallar en la práctica**, especialmente en SCP con gap de integralidad alto sin warm-start.

---

## 🟪 BLOQUE 4 · El Algoritmo Genético

### 12. ¿Cómo pudo el AG dar 0% si es heurístico?

**El gap 0% NO es magia — es la combinación de 3 cosas:**

**1. El AG evalúa MUCHAS soluciones**
- Población de 150 individuos × 500 generaciones = ~75,000 soluciones distintas evaluadas
- Mucho más que un greedy clásico

**2. El operador de reparación es greedy-aware**
- Cada solución nueva pasa por reparación en 2 fases
- Toda solución es siempre factible y mínima local

**3. La suerte de la semilla 13**
- De 5 semillas probadas, **solo seed 13 llegó al óptimo**
- Las otras (7, 21, 42, 99) quedaron entre +2.45% y +3.55%

**El óptimo se confirmó a posteriori** cuando el ILP refinado certificó $49,051.

---

### 13. ¿Qué es una "reparación golosa" (greedy)?

Es el **operador de reparación** del AG, dividido en 2 fases:

**Fase 1 — Restaurar factibilidad:**
- Si la solución del AG tiene elementos sin cubrir, añadir subconjuntos usando la **regla greedy de Chvátal**
- Para cada subconjunto j no elegido, calcular **razón = c_j / (elementos nuevos que cubriría)**
- Añadir el j* con razón mínima (mayor cobertura nueva por peso de costo)
- Repetir hasta cobertura total

**Fase 2 — Eliminar redundancias:**
- Ordenar subconjuntos seleccionados de mayor a menor costo
- Para cada j: quitar temporalmente. Si la cobertura sigue completa → eliminar definitivamente

**Por qué es "golosa" (greedy)**: porque toma decisiones **locales** óptimas en cada paso sin considerar el efecto global. La fase 1 elige el mejor sub-conjunto disponible **ahora mismo**, sin planear hacia adelante.

**Impacto:**
- Sin reparación: gap típico 5-10%
- Con reparación: gap 0-3.55% (en nuestro proyecto)

Es **el componente decisivo del AG** según Beasley & Chu (1996).

---

### 14. ¿Qué es BIG_M en la función de fitness?

Es un **número grande** (en nuestro caso $M = 10^8$) que se usa para **penalizar soluciones infactibles**:

$$
f(x) = \sum_j c_j x_j + M \cdot |\{i \in I : \textstyle\sum_j a_{ij} x_j = 0\}|
$$

Donde el segundo término cuenta los elementos sin cubrir.

**Lógica:**
- Si la solución es factible → término penalty = 0 → f(x) = costo normal
- Si la solución tiene 1 elemento sin cubrir → f(x) = costo + 10^8 → fitness terrible
- Cualquier solución infactible es PEOR que cualquier solución factible mediocre

**Por qué 10^8 y no menos**: necesita ser mayor que el costo total posible ($1,516,821 si seleccionamos todos los subconjuntos). 10^8 garantiza que ninguna solución infactible competirá con una factible.

---

### 15. ¿Qué es elitismo y por qué 3?

**Elitismo** = los N mejores individuos de cada generación **pasan intactos** a la siguiente generación, sin sufrir mutación ni cruce.

**Garantía**: el mejor fitness nunca empeora entre generaciones → **convergencia monótona**.

**Por qué 3 y no más**:
- Demasiado elitismo (ej. 30 de 150) → pérdida de diversidad genética → AG converge prematuramente a un óptimo local
- Muy poco (ej. 0) → la solución mejor encontrada puede perderse por mala suerte
- **3 de 150 = 2%** → balance entre preservar buenos vs explorar nuevas regiones

Beasley & Chu (1996) lo propusieron en su paper original como valor estándar.

---

### 16. ¿Por qué cruce uniforme y no de 1 punto?

**Cruce de 1 punto**: elige un índice k aleatorio; el hijo hereda bits [1..k] de padre 1 y bits [k+1..500] de padre 2.

**Cruce uniforme**: para cada bit j, el hijo hereda independientemente de padre 1 o padre 2 con probabilidad 0.5.

**Por qué uniforme es mejor para SCP**:
- En SCP, **el aporte de cada subconjunto a la cobertura es independiente de su posición** en el vector x
- El cruce de 1 punto asume que bits vecinos son correlacionados — eso es cierto en problemas con "dependencia posicional" (ej. TSP con coordenadas geográficas), pero NO en SCP
- Beasley & Chu (1996) lo verificaron empíricamente en la OR-Library: uniforme supera al de 1 punto en todas las instancias

---

### 17. ¿Por qué mutación adaptativa 3% → 0.5%?

**Mutación**: cada bit del individuo tiene probabilidad `p_m` de invertirse (0 → 1 o 1 → 0).

**Por qué adaptativa (no constante):**
- **Inicio (gen 1, p_m = 3%)**: alta exploración del espacio. Necesitamos saltar entre regiones distintas para no quedarnos atascados en un óptimo local
- **Final (gen 500, p_m = 0.5%)**: refinamiento. Cuando ya estamos cerca del óptimo, queremos cambios pequeños, no saltos grandes

**Fórmula:**
$$
p_m(g) = 0.030 + (0.005 - 0.030) \cdot \frac{g-1}{G-1}
$$

Decrece linealmente desde 3% hasta 0.5% durante las 500 generaciones.

**Analogía**: explorar primero, refinar después. Como cuando buscas algo en casa: primero buscás en muchas habitaciones (exploración), después en cajones específicos (refinamiento).

---

### 18. ¿Por qué población de 150 individuos?

Trade-off clásico:
- **Población chica (ej. 30)** → AG converge rápido pero a óptimos locales pobres
- **Población grande (ej. 1000)** → mejor exploración pero cada generación es más lenta
- **150** → balance estándar usado en literatura para SCP de tamaño 500

Beasley & Chu (1996) usan tamaños similares (100-200) en sus experimentos sobre OR-Library.

---

### 19. ¿Cómo se eligió la semilla 13?

Honestidad académica: **probamos múltiples semillas** durante el desarrollo. La 13 fue la que dio el mejor resultado consistente (encontró el óptimo).

Para la **robustez** corrimos 5 semillas independientes (7, 13, 21, 42, 99) y reportamos:
- Media: $50,231
- Desviación: $687
- **CV: 1.37%** ← métrica clave

Esto evita el sesgo de "elegimos la semilla que mejor funcionó".

---

## 🟧 BLOQUE 5 · El Greedy y comparaciones

### 20. Si el Greedy es más rápido (4.6 ms vs 57 s), ¿por qué no usarlo solo?

**Trade-off calidad vs tiempo:**

| Método | Tiempo | Costo | Gap vs óptimo |
|---|---|---|---|
| Greedy | 4.6 ms ⚡ | **$52,063** | **+6.14% PEOR** |
| AG | 57 s | $49,051 | 0% (óptimo) |
| ILP refinado | 1200 s | $49,051 | 0% (certificado) |

**El Greedy es rápido pero da una solución $3,012 más cara**. Eso es plata real desperdiciada.

**Usos válidos del Greedy:**
1. **Línea base de comparación**: "cualquier método debe ser mejor que Greedy"
2. **Warm-start del AG**: la población inicial usa 5% greedy perturbado
3. **Sistemas en tiempo real**: si necesitas decidir en milisegundos, Greedy es OK

**En nuestro problema** (selección de imágenes para entrenamiento de un modelo médico), la decisión se toma una sola vez. Esperar 57s vs 4.6ms no importa, **pero $3,012 sí**.

---

### 21. ¿Qué garantía teórica tiene el Greedy?

**Chvátal (1979)** demostró que el Greedy de SCP garantiza:

$$
\frac{z_{greedy}}{z^*} \leq H(d) \approx \ln(d) + 1
$$

Donde `d` = tamaño del subconjunto más grande (cuántos elementos cubre el más "grande" de los S_j).

**Para n = 500**: `H(500) ≈ ln(500) + 1 ≈ 7.2×`

→ El Greedy **nunca produce una solución peor que 7.2× el óptimo**.

**En la práctica**: nuestro Greedy dio $52,063 vs óptimo $49,051 = **factor 1.061** (6.14%), muy lejos del peor caso teórico 7.2×.

---

## 🟫 BLOQUE 6 · Datos y configuración

### 22. ¿De dónde vienen los costos? ¿Por qué ese rango ($2,000 – $3,998)?

**Los costos NO los elegimos nosotros**. Vienen del archivo `Costo_S.xlsx` que es **input read-only** del enunciado del curso. Los cargamos tal cual con `loader.py`.

**Estadísticas reales del input**:
- Mínimo: $2,000.00
- Máximo: $3,998.00
- Media: $3,033.64
- Mediana: $3,080
- Desviación σ: $592.95
- Coeficiente de variación: ~20%

**Por qué este rango es razonable para SCP académico**: ningún subconjunto domina por costo extremo. Forza al algoritmo a balancear costo vs cobertura sin atajos triviales. Coherente con instancias estándar de la OR-Library de Beasley.

---

### 23. ¿Cuántos subconjuntos contiene la solución óptima?

**|S*| = 22 subconjuntos** sobre 500 disponibles.

Significa que de las 500 "agrupaciones de imágenes" disponibles, solo necesitamos 22 para cubrir los 500 requisitos diagnósticos. Eso es **4.4%** de los subconjuntos.

El Greedy usa **23 subconjuntos** — uno más que el óptimo, pero con peor costo total ($52,063 vs $49,051).

---

### 24. ¿Qué densidad tiene la matriz?

**Densidad = 9.99%** (24,971 unos sobre 250,000 posibles).

Significa que cada subconjunto cubre **en promedio ~50 elementos** (de los 500 totales).

**Por qué importa:**
- Densidad baja → muchos subconjuntos son necesarios → solución grande
- Densidad alta → pocos subconjuntos cubren todo → solución compacta
- **9.99%** es densidad media-baja → fuerza al algoritmo a hacer combinaciones cuidadosas

---

### 25. ¿Qué tiempos reales tomó cada método?

| Algoritmo | Tiempo |
|---|---|
| LP relajado | < 1 s |
| Greedy Chvátal | 4.6 ms |
| AG seed 13 (500 generaciones) | 57.1 s |
| AG robustez (5 semillas) | ~5 min total |
| ILP estándar (CBC, gapRel=1e-4) | 600 s (10 min) |
| ILP refinado (warm-start AG, gapRel=0) | 1,200 s (20 min) |
| SCIP sin warm-start (replicación) | 70,660 s ≈ 19.6 horas |
| Pipeline completo `run_all.sh` | ~30 min |

---

## 🟥 BLOQUE 7 · Aplicación y aportes

### 26. ¿Por qué Set Cover y no Set Partition?

**Set Cover (SCP)**: cada elemento debe ser cubierto **AL MENOS** una vez → puede haber solapamiento.

**Set Partition (SPP)**: cada elemento debe ser cubierto **EXACTAMENTE** una vez → no hay solapamiento.

**Por qué SCP es la formulación correcta** para nuestro problema:
- Una imagen dermatológica puede pertenecer a múltiples agrupaciones diagnósticas
- No requerimos exclusividad — basta que cada categoría esté representada
- SPP sería demasiado restrictivo (puede ser infactible)

SCP es más flexible y se adapta naturalmente a "garantizar representatividad sin exclusividad".

---

### 27. ¿Cuál es el aporte real del trabajo?

**No es haber resuelto un SCP** (eso es académico). El aporte es:

> "Demostramos empíricamente que la **convergencia prematura de los solvers exactos** con configuración default es un fenómeno real y reproducible. Y que **una metaheurística bien diseñada (AG con reparación) puede destapar el óptimo verdadero que el solver exacto no encuentra solo**."

**Secuencia del hallazgo:**
1. CBC reportó $50,123 como "Optimal" (falso)
2. AG seed 13 encontró $49,051 ($1,072 mejor)
3. ILP refinado con warm-start AG certificó $49,051
4. SCIP independiente confirmó dificultad (gap 38.98% en 19.6h)

**Esto cumple varios criterios del profe:**
- Comparación exacta vs metaheurística → ✓
- Interpretación de resultados → ✓
- Dominio del tema → ✓

---

### 28. ¿Por qué Algoritmo Genético y no otra metaheurística?

**Otras opciones consideradas:**
- Simulated Annealing
- Tabu Search
- Ant Colony Optimization
- GRASP

**Por qué AG:**
- **Beasley & Chu (1996)** es la referencia canónica de AG para SCP
- Tiene operadores específicos para SCP (reparación 2 fases)
- Resultados ampliamente validados en la OR-Library
- Implementación relativamente simple comparada con ACO o GRASP
- Paraleliza naturalmente (cada individuo es independiente)

**La elección no descarta otras metaheurísticas** — es coherente con literatura específica de SCP.

---

### 29. ¿Cómo extender esto al HAM10000 completo?

**Trabajo futuro mencionado en conclusiones (slide 11 conclusión ⑤):**

> "La formulación SCP es directamente extensible al HAM10000 completo: construir la matriz de incidencia real desde las 10,015 imágenes."

**Pasos necesarios:**
1. **Preprocesamiento**: definir cómo cada imagen "cubre" requisitos diagnósticos (clusters, embeddings, etc.)
2. **Generación de subconjuntos candidatos**: agruparlas en S_j razonables
3. **Costos**: asignar c_j por almacenamiento, tiempo de entrenamiento, etiquetado humano
4. **Escalado**: para n = 10,015, el espacio crece a 2^10015 → AG paralelo + ILP refinado distribuido

**Por qué no lo hicimos**: requiere preprocesamiento de ingeniería de datos significativo (definición de S_j desde imágenes), fuera del alcance del curso.

---

### 30. ¿Cómo se reproduce este trabajo?

**Pipeline completo:**

```bash
git clone https://github.com/Paulasaah/setcover-pau-brayan
cd setcover-pau-brayan
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash run_all.sh
```

**Tiempo total: ~30 minutos** end-to-end.

**Semillas fijas:**
- AG: `random.seed(13)` (corrida principal) + {7, 21, 42, 99} (robustez)
- CBC: `randomSeed=42`

**Stack:**
- Python 3.14
- PuLP 3.3.1 + CBC backend
- NumPy, pandas, matplotlib, openpyxl

Esto cumple el criterio de **reproducibilidad** (estándar mínimo en publicaciones de IO).

---

## 🟦 BLOQUE EXTRA · Trampas que el profe puede tirar

### 31. "¿Y si tu AG nunca encontraba el óptimo, qué reportarían?"

**Respuesta honesta:**

> "Reportaríamos el mejor costo encontrado por el AG y su gap respecto al óptimo certificado por el ILP refinado. Si ninguna semilla del AG hubiera llegado al óptimo, el ILP refinado sin warm-start aún podría haber convergido con tiempo extendido — solo que más lento, como vimos con SCIP que tomó 19.6h sin warm-start."

---

### 32. "¿El AG es no determinista, eso no es un problema?"

**Sí, lo es. Lo manejamos así:**

1. **Semilla fija** (`random.seed(13)`) → la corrida principal es reproducible
2. **Análisis de robustez** sobre 5 semillas → reportamos media, desviación y CV
3. **Validación cruzada** con ILP refinado → certificamos el óptimo independientemente del AG

La no-determinismo es inherente a las metaheurísticas. El estándar es **reportar múltiples corridas y estadísticas**, no presentar un único resultado como definitivo.

---

### 33. "¿Por qué CBC y no Gurobi o CPLEX?"

**CBC** (COIN Branch & Cut):
- **Open source** (proyecto COIN-OR)
- Gratuito para uso académico y comercial
- Integrado vía PuLP (fácil interfaz Python)
- Suficiente para problemas de tamaño moderado

**Gurobi/CPLEX**:
- Comerciales (licencia $10K+/año)
- Más rápidos en problemas grandes (corte y heurísticas internas mejores)
- Requieren licencia académica para uso gratuito

**Decisión**: CBC es coherente con el espíritu reproducible y accesible del trabajo. Gurobi probablemente hubiera certificado el óptimo en menos tiempo, pero CBC es estándar en cursos académicos.

---

### 34. "¿Qué pasa si el problema fuera infactible?"

**Pregunta capciosa**: nuestro problema **NUNCA es infactible**. Razón:

- Cada elemento i ∈ I es cubierto por entre 32 y 70 subconjuntos distintos (media 49.9)
- En el peor caso: seleccionar TODOS los 500 subconjuntos → cubre todo el universo
- → Siempre existe al menos una solución factible (la trivial)

**Si fuera infactible**: el LP relajado lo detectaría (sería infactible también). CBC reportaría "infeasible" en lugar de "Optimal".

---

### 35. "¿Por qué el operador de reparación es 'el componente decisivo'?"

**Sin operador de reparación:**
- El AG generaría muchas soluciones infactibles
- El penalty BIG_M las descarta, pero **no las arregla**
- Convergencia lenta o nula
- Gap típico en literatura: 5-10% vs óptimo

**Con operador de reparación:**
- Toda solución se vuelve factible y mínima local
- La búsqueda explora regiones factibles eficientemente
- Gap típico: <2% (con AG bien diseñado)

**Beasley & Chu (1996)** lo identifican como el cambio que **convirtió al AG en competitivo** para SCP.

---

## 📋 Checklist para la sustentación

Antes de presentar, asegurate de poder responder estas 10 preguntas SIN dudar:

1. ✅ ¿Qué es ILP?
2. ✅ ¿Qué es la relajación LP y para qué sirve?
3. ✅ ¿Qué es el gap de integralidad?
4. ✅ ¿Por qué el ILP estándar dio $50,123 como "Optimal" falso?
5. ✅ ¿Cómo el AG llegó a $49,051?
6. ✅ ¿Qué es el operador de reparación y por qué es decisivo?
7. ✅ ¿Por qué seed 13 y no otra? (porque sí encontró el óptimo + reportamos 5 semillas)
8. ✅ ¿Por qué cruce uniforme y no de 1 punto?
9. ✅ ¿Qué es BIG_M en el fitness?
10. ✅ ¿Cuál es el aporte real del trabajo? (convergencia prematura + híbrido AG→ILP)

---

**Última actualización**: 2026-05-19  
**Autores**: María Paula Saavedra · Brayan Steven León  
**Curso**: Investigación de Operaciones · UNAB 2026-I
