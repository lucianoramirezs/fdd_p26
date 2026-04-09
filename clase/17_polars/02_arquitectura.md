---
title: "Arquitectura de Polars"
---

# Arquitectura de Polars

Esta sección explica **cómo funciona Polars internamente**. No es necesario conocer cada detalle para usar la librería, pero entender la arquitectura te permite tomar mejores decisiones y predecir el rendimiento.

## El pipeline completo

Cuando escribes código en Polars (modo lazy), tu código pasa por varias etapas antes de tocar un solo dato:

```
Tu código Python
      │
      ▼
┌──────────────────┐
│   Expresiones    │  pl.col("age") > 30, pl.col("name").str.to_lowercase()
│   (Python DSL)   │  → Cada expresión es un objeto, no una operación
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Plan lógico    │  Árbol de operaciones: Scan → Filter → Select → GroupBy
│   (IR tree)      │  → Describe QUÉ hacer, no CÓMO hacerlo
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Optimizador    │  Reescribe el plan: pushdown, eliminación, reordenamiento
│   (query opt.)   │  → Decide el plan MÁS EFICIENTE equivalente
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Plan físico    │  Plan concreto: qué particiones, qué hilos, qué orden
│   (exec plan)    │  → Describe CÓMO ejecutar el plan optimizado
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Rayon          │  Threadpool con work-stealing
│   (ejecución)    │  → Ejecuta en PARALELO sobre todos los cores
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Resultado      │  DataFrame en formato Arrow columnar
│   (Arrow)        │
└──────────────────┘
```

> **Conexión con sección 16:** Este pipeline es análogo a un compilador: tu código se traduce a una representación intermedia (plan lógico), se optimiza, y se ejecuta en paralelo. pandas es como un intérprete — ejecuta cada línea inmediatamente sin ver el plan completo.

## Apache Arrow: el formato de memoria

### Qué es Arrow

Apache Arrow es un formato de memoria columnar estándar. "Columnar" significa que los valores de una misma columna están contiguos en memoria:

```
Row-oriented (pandas internamente para mixed types):
┌───────┬─────┬────────┐
│ Alice │  30 │ Madrid │  → fila 0
│ Bob   │  25 │ Lima   │  → fila 1
│ Carol │  35 │ Tokyo  │  → fila 2
└───────┴─────┴────────┘
Memoria: [Alice][30][Madrid][Bob][25][Lima][Carol][35][Tokyo]

Column-oriented (Arrow / Polars):
Columna "name":  [Alice][Bob][Carol]        ← contiguo
Columna "age":   [30][25][35]               ← contiguo
Columna "city":  [Madrid][Lima][Tokyo]      ← contiguo
```

### Por qué importa para el rendimiento

1. **Cache de CPU**: cuando sumas una columna de 1M de enteros, todos están contiguos en memoria. El CPU los carga en cache de forma secuencial — el patrón de acceso más rápido posible.

2. **SIMD**: instrucciones que operan sobre múltiples valores a la vez (Single Instruction, Multiple Data). Con datos contiguos, el CPU puede sumar 4 o 8 enteros en una sola instrucción.

3. **Compresión**: valores del mismo tipo contiguos comprimen mejor que filas mezcladas.

4. **Zero-copy**: pasar datos entre Polars y otro sistema Arrow (DuckDB, PyArrow, Spark) no copia nada — comparten el mismo layout en memoria.

### Nulls en Arrow vs pandas

pandas hereda `NaN` de NumPy — un float de IEEE 754. Esto causa problemas:

```python
# pandas: una columna de enteros con un null se convierte a float
import pandas as pd
s = pd.Series([1, 2, None, 4])
print(s.dtype)  # float64 — perdiste el tipo entero
```

Arrow usa un **validity bitmap** — un bit por valor que indica si es null o no:

```
Valores:   [1] [2] [?] [4]
Bitmap:     1   1   0   1      ← el tercer valor es null

Tipo: Int64 (se mantiene entero)
```

```python
# polars: el tipo se mantiene
import polars as pl
s = pl.Series([1, 2, None, 4])
print(s.dtype)  # Int64 — el tipo se conserva
```

## Lazy vs Eager

Polars tiene dos modos de operación:

### Modo eager (DataFrame)

Cada operación se ejecuta inmediatamente — igual que pandas:

```python
df = pl.read_csv("datos.csv")           # lee TODO el archivo AHORA
df2 = df.filter(pl.col("age") > 30)     # filtra AHORA
df3 = df2.select("name", "age")         # selecciona AHORA
```

### Modo lazy (LazyFrame)

Las operaciones se registran pero no se ejecutan:

```python
lf = pl.scan_csv("datos.csv")           # NO lee nada — registra "leer CSV"
lf2 = lf.filter(pl.col("age") > 30)     # NO filtra — registra "filtrar"
lf3 = lf2.select("name", "age")         # NO selecciona — registra "seleccionar"

# Ver el plan SIN ejecutar:
print(lf3.explain())

# AHORA ejecuta todo (optimizado):
result = lf3.collect()
```

### ¿Por qué lazy es mejor?

Porque el optimizador puede ver el plan completo y reescribirlo:

```
Plan original (lo que escribiste):
  Scan CSV (50 columnas)
    → Filter (age > 30)
      → Select (name, age)

Plan optimizado (lo que Polars ejecuta):
  Scan CSV (solo 2 columnas: name, age)   ← projection pushdown
    con filtro (age > 30)                  ← predicate pushdown
```

Sin lazy, Polars leería las 50 columnas, las cargaría todas en memoria, filtraría, y luego descartaría 48 columnas. Con lazy, solo lee las 2 columnas que necesitas y filtra durante la lectura.

> **Verifica en el notebook:** Notebook 02 — Sección 2 muestra el plan creciendo paso a paso con `.explain()` en cada etapa del pipeline.

## El optimizador de consultas

El optimizador aplica transformaciones al plan lógico para hacerlo más eficiente. Las principales:

### Predicate pushdown

Mueve los filtros lo más cerca posible de la fuente de datos:

```
Antes:                          Después:
Scan CSV                        Scan CSV con filtro age > 30
  → Join con otra tabla           → Join con otra tabla
    → Filter (age > 30)             (el filtro se aplicó antes)
```

Si filtras por `age > 30` y el scan lee un Parquet, Polars puede usar las estadísticas de los row groups para **saltar bloques enteros** que no tienen valores > 30.

### Projection pushdown

Solo lee las columnas que se usan al final:

```
Antes:                          Después:
Scan CSV (50 cols)              Scan CSV (2 cols: name, age)
  → Select (name, age)           (las otras 48 nunca se leen)
```

### Common subexpression elimination (CSE)

Si calculas lo mismo dos veces, lo calcula una sola vez:

```python
# El usuario escribe:
df.with_columns(
    (pl.col("price") * pl.col("qty")).alias("total"),
    (pl.col("price") * pl.col("qty") * 0.16).alias("iva"),
)
# El optimizador detecta que price * qty se repite y lo calcula una vez
```

### Ver el plan

Puedes inspeccionar el plan en cualquier momento:

```python
lf = (
    pl.scan_csv("ventas.csv")
    .filter(pl.col("monto") > 1000)
    .select("cliente", "monto")
    .group_by("cliente").agg(pl.col("monto").sum())
)

# Plan optimizado en texto:
print(lf.explain())

# Plan sin optimizar (para comparar):
print(lf.explain(optimized=False))
```

## Rayon: paralelismo transparente

Polars usa **Rayon** — un framework de paralelismo en Rust — para ejecutar operaciones en múltiples cores simultáneamente.

### Cómo funciona

1. Los datos se **particionan** en chunks
2. Cada chunk se asigna a un hilo del threadpool
3. Los hilos procesan en paralelo (sin GIL — es Rust)
4. Los resultados se combinan

```
DataFrame: 1M filas
          │
          ▼ particionar
┌──────────┬──────────┬──────────┬──────────┐
│ 250K     │ 250K     │ 250K     │ 250K     │
│ filas    │ filas    │ filas    │ filas    │
│          │          │          │          │
│ Thread 0 │ Thread 1 │ Thread 2 │ Thread 3 │
│ filter() │ filter() │ filter() │ filter() │
│ 50K res  │ 62K res  │ 48K res  │ 55K res  │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┘
     │          │          │          │
     └──────────┴──────────┴──────────┘
                    │
                    ▼ combinar
              215K filas resultado
```

### Work-stealing

Si un thread termina antes que los otros, **roba trabajo** de la cola de otro thread. Esto balancea la carga automáticamente:

```
Thread 0: [████████░░]  ← terminó temprano, roba de Thread 2
Thread 1: [████████████]
Thread 2: [████████████████]  ← Thread 0 le ayuda
Thread 3: [██████████░░]
```

> **Conexión con sección 16:** Esto es M5a (paralelismo real, CPU-bound) de la sección 16.5. La diferencia es que con `ProcessPoolExecutor` tú gestionas los procesos manualmente y cada proceso tiene su propia copia de los datos. Con Rayon, los hilos comparten memoria (Rust garantiza seguridad) y el work-stealing es automático.

## Tipos de datos en Arrow

Polars usa los tipos de Arrow, que son más estrictos que los de pandas:

### Tipos numéricos

| Tipo | Tamaño | Rango | Notas |
|------|--------|-------|-------|
| `Int8` | 1 byte | -128 a 127 | |
| `Int16` | 2 bytes | -32K a 32K | |
| `Int32` | 4 bytes | -2B a 2B | |
| `Int64` | 8 bytes | -9.2E18 a 9.2E18 | Default para enteros |
| `UInt8/16/32/64` | 1-8 bytes | Solo positivos | |
| `Float32` | 4 bytes | ~7 dígitos | |
| `Float64` | 8 bytes | ~15 dígitos | Default para flotantes |

**`Float16` NO está soportado.** Arrow define el tipo, pero Polars no lo implementa porque la mayoría de CPUs no tienen instrucciones nativas para float16. Si necesitas float16 (modelos de ML), convierte al final con NumPy.

### Tipos de texto y binarios

| Tipo | Descripción |
|------|-------------|
| `Utf8` (o `String`) | Texto UTF-8, longitud variable |
| `Binary` | Bytes crudos |
| `Categorical` | Enteros + diccionario de strings (menor memoria) |
| `Enum` | Como Categorical pero con categorías fijas — error si aparece un valor nuevo |

### Tipos temporales

| Tipo | Ejemplo | Precisión |
|------|---------|-----------|
| `Date` | `2026-03-23` | Días |
| `Datetime` | `2026-03-23 14:30:00` | Microsegundos (configurable) |
| `Duration` | `3h 15m` | Diferencia entre dos Datetime |
| `Time` | `14:30:00` | Hora del día sin fecha |

### Tipos compuestos

| Tipo | Descripción | Uso típico |
|------|-------------|------------|
| `List` | Lista de valores del mismo tipo por fila | Features temporales, embeddings |
| `Array` | Lista de tamaño fijo por fila | Vectores de dimensión fija |
| `Struct` | Registro con campos nombrados | Datos anidados sin JSON |

> **Verifica en el notebook:** Notebook 01 — Sección 1 muestra la creación de cada tipo y las conversiones con `.cast()`.

## Streaming: más allá de la RAM

Polars puede procesar datasets más grandes que la RAM en **modo streaming**:

```python
result = (
    pl.scan_csv("archivo_enorme.csv")
    .filter(pl.col("status") == "active")
    .group_by("category").agg(pl.col("amount").sum())
    .collect(streaming=True)    # ← procesa en chunks, no carga todo
)
```

En modo streaming, Polars:
1. Lee el archivo en chunks
2. Aplica las transformaciones chunk por chunk
3. Combina los resultados al final

No todas las operaciones soportan streaming (joins grandes pueden necesitar materialización), pero para filter + groupby + aggregation funciona muy bien.

Este módulo no profundiza en streaming — solo es importante saber que existe para cuando tus datos no caben en RAM pero tampoco necesitas un cluster.
