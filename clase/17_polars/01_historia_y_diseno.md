---
title: "Historia y diseño de Polars"
---

# Historia y diseño de Polars

## De dónde viene: la autocrítica de pandas

En 2017, Wes McKinney — el creador de pandas — publicó un artículo titulado *"Apache Arrow and the '10 Things I Hate About pandas'"*. No era un ataque externo: era el creador de la librería más usada de Python para datos tabulares explicando por qué su propia creación tenía problemas fundamentales que **no se podían arreglar sin reescribirla**.

Los problemas que identificó:

| Problema | Causa raíz | Consecuencia |
|----------|-----------|--------------|
| Uso excesivo de memoria | Backend NumPy no diseñado para datos tabulares | Un CSV de 2 GB puede usar 8-10 GB en RAM |
| Strings lentos | `object` dtype = array de punteros a objetos Python | Operaciones de texto 10-100x más lentas que C |
| Tipos nullable rotos | `NaN` es un float de IEEE 754 | Columna de enteros con un null → toda se convierte a float |
| Sin paralelismo | GIL de Python | Un solo core, sin importar cuántos tengas |
| Evaluación eager | Cada operación se ejecuta inmediatamente | No hay oportunidad de optimizar el plan completo |
| Copias innecesarias | Semántica de copia defensiva | Operaciones simples duplican DataFrames enteros |

McKinney no solo listó los problemas — propuso la solución: **Apache Arrow** como formato de memoria estándar, compartido entre lenguajes y sistemas. Él mismo cofundó el proyecto Arrow en 2016.

Pero pandas no podía adoptar Arrow completamente sin romper su API. El backend Arrow en pandas 2.x es opcional y parcial — un parche sobre una arquitectura que no fue diseñada para él.

## Polars: diseñado con la ventaja de la retrospectiva

En 2020, Ritchie Vink — un ingeniero holandés — empezó a construir Polars. La pregunta era simple: **¿cómo se vería pandas si lo diseñaras hoy, sabiendo todo lo que sabemos?**

Las decisiones de diseño:

### 1. Rust en lugar de Python/C

pandas está escrito en Python con extensiones en C/Cython. Polars está escrito en **Rust** — un lenguaje compilado con:

- **Sin garbage collector** — gestión de memoria determinista
- **Sin GIL** — paralelismo real entre hilos (threads)
- **Zero-cost abstractions** — el compilador optimiza sin overhead en runtime
- **Seguridad de memoria** — sin segfaults, sin data races

El frontend en Python (`import polars`) es una capa delgada que llama al motor Rust. Cuando ejecutas una operación en Polars, Python se sale del camino y Rust hace todo el trabajo.

### 2. Apache Arrow como formato nativo

Mientras pandas adoptó Arrow como parche, Polars **nació con Arrow**:

```
pandas:  Python objects → NumPy arrays → (opcionalmente) Arrow
polars:  Arrow columnar format desde el primer byte
```

Esto significa:
- **Strings nativos**: tipo `Utf8`, no `object`. Operaciones de texto en Rust, no en Python.
- **Nullable types reales**: cada columna tiene un bitmap de validez. Un entero con nulls sigue siendo entero.
- **Zero-copy IPC**: pasar datos entre Polars y otro sistema Arrow (DuckDB, Spark) no copia nada.
- **Formato columnar**: los datos de una columna están contiguos en memoria → mejor uso de cache de CPU.

### 3. Lazy por defecto

pandas ejecuta cada operación inmediatamente:
```python
# pandas — cada línea ejecuta y materializa un DataFrame nuevo
df2 = df[df["age"] > 30]           # filtra AHORA, crea df2
df3 = df2[["name", "age"]]         # selecciona AHORA, crea df3
df4 = df3.groupby("name").mean()   # agrupa AHORA, crea df4
```

Polars puede construir un **plan de ejecución** y optimizarlo antes de ejecutar:
```python
# polars lazy — nada se ejecuta hasta .collect()
result = (
    pl.scan_csv("datos.csv")        # no lee el archivo todavía
    .filter(pl.col("age") > 30)     # registra: "filtrar age > 30"
    .select("name", "age")          # registra: "seleccionar 2 columnas"
    .group_by("name").agg(          # registra: "agrupar y promediar"
        pl.col("age").mean()
    )
    .collect()                       # AHORA: optimiza el plan → ejecuta todo
)
```

El optimizador puede:
- **Projection pushdown**: si solo necesitas 2 de 50 columnas, solo lee esas 2 del CSV
- **Predicate pushdown**: si filtras `age > 30`, aplica el filtro durante la lectura
- **Common subexpression elimination**: si calculas `pl.col("x") + 1` dos veces, lo calcula una sola vez

> **Conexión con sección 16:** La evaluación lazy es análoga a la diferencia entre interpretar y compilar. pandas "interpreta" cada operación. Polars "compila" el plan completo y lo optimiza antes de ejecutar.

### 4. Paralelismo automático

pandas opera en un solo hilo (GIL). Polars usa **Rayon** — un threadpool de Rust con work-stealing:

```
pandas:                          polars:
┌────────┐                       ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Core 0 │ ← todo aquí           │ Core 0 │ │ Core 1 │ │ Core 2 │ │ Core 3 │
│ GIL    │                       │ part 0 │ │ part 1 │ │ part 2 │ │ part 3 │
└────────┘                       └────────┘ └────────┘ └────────┘ └────────┘
```

Polars particiona los datos automáticamente y distribuye el trabajo entre todos los cores disponibles. No necesitas `ProcessPoolExecutor`, no necesitas `multiprocessing` — el paralelismo es transparente.

> **Conexión con sección 16:** Esto es M5a (parallelism, CPU-bound) pero implementado dentro de la librería. Compara con la sección 16.5 donde usamos `ProcessPoolExecutor` manualmente — Polars hace lo mismo, pero mejor, porque Rust no tiene GIL y el threadpool es más eficiente que crear procesos.

## Dónde encaja Polars en el ecosistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    Datos tabulares en Python                     │
│                                                                  │
│  Cabe en RAM          No cabe en RAM         Distribuido         │
│  ┌──────────────┐     ┌──────────────┐      ┌──────────────┐   │
│  │   pandas      │     │    dask       │      │   PySpark    │   │
│  │ (flexible,    │     │ (lazy pandas, │      │ (JVM, cluster│   │
│  │  ecosistema)  │     │  cluster)     │      │  enterprise) │   │
│  ├──────────────┤     └──────────────┘      └──────────────┘   │
│  │   polars      │                                               │
│  │ (rápido, lazy,│     ┌──────────────┐                         │
│  │  Arrow, ||)   │     │   DuckDB      │                        │
│  └──────────────┘     │ (SQL analítico │                        │
│                        │  embebido)     │                        │
│                        └──────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

| Situación | Herramienta | Por qué |
|-----------|------------|---------|
| Tabla en RAM, exploración rápida | pandas | Ecosistema enorme, todos lo conocen |
| Tabla en RAM, necesitas rendimiento | **polars** | 2-10x más rápido, lazy eval, paralelismo |
| Tabla en RAM, SQL es más natural | DuckDB | SQL analítico, también Arrow-native |
| No cabe en RAM, Python | dask | API similar a pandas, escala a cluster |
| No cabe en RAM, empresa grande | PySpark | Infraestructura Spark, JVM |

### ¿Cuándo NO usar Polars?

- **Cuando el ecosistema importa más que la velocidad**: scikit-learn, matplotlib, seaborn esperan pandas DataFrames (aunque Polars puede convertir con `.to_pandas()`)
- **Cuando trabajas con datos pequeños** (< 10K filas): el overhead de optimización no se amortiza
- **Cuando necesitas mutación in-place**: Polars es inmutable por diseño — cada operación retorna un DataFrame nuevo
- **Cuando tu equipo solo sabe pandas**: la curva de aprendizaje existe, especialmente para expresiones y lazy eval

## Lo que vamos a aprender

En las siguientes secciones vamos a:

1. **Entender la arquitectura** — Arrow, lazy vs eager, el optimizador, Rayon, tipos de datos
2. **Escribir Polars idiomático** — expresiones, contextos, UDFs, listas
3. **Construir un pipeline E2E** — limpieza de datos completa, solo Polars
4. **Comparar con pandas** — operación por operación, con explicaciones
5. **Medir** — benchmarks reales con visualizaciones
6. **Ir más allá** — series de tiempo, ventanas, funciones temporales avanzadas

> **Verifica en el notebook:** El Notebook 04 — Sección 1 genera los benchmarks que confirman las diferencias de rendimiento que discutimos aquí.
