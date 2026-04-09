---
title: "Polars vs pandas"
---

# Polars vs pandas: comparación lado a lado

Esta sección muestra las operaciones más comunes en ambas librerías, lado a lado, con explicaciones de **por qué la API es diferente** — no solo *cómo* es diferente.

## Leer datos

```python
# pandas
df = pd.read_csv("datos.csv")                  # lee TODO inmediatamente
df = pd.read_csv("datos.csv", usecols=["a","b"])  # selección manual de columnas

# polars — eager
df = pl.read_csv("datos.csv")                   # lee TODO inmediatamente

# polars — lazy (recomendado)
lf = pl.scan_csv("datos.csv")                   # NO lee nada
result = lf.select("a", "b").collect()           # projection pushdown automático
```

**¿Por qué?** En pandas, si quieres leer solo 2 columnas debes decirlo en `read_csv`. En Polars lazy, el optimizador detecta qué columnas usas en todo el pipeline y solo lee esas.

## Seleccionar columnas

```python
# pandas
df[["nombre", "edad"]]                  # indexación con lista
df.loc[:, ["nombre", "edad"]]           # loc explícito

# polars
df.select("nombre", "edad")            # método explícito
df.select(pl.col("nombre", "edad"))     # con expresión
```

**¿Por qué?** Polars evita la ambigüedad de `df[x]` que en pandas puede ser una columna (string), varias (lista), o filas (slice).

## Crear / modificar columnas

```python
# pandas
df["salario_anual"] = df["salario"] * 12          # modifica in-place
df = df.assign(salario_anual=df["salario"] * 12)  # retorna copia

# polars
df = df.with_columns(
    (pl.col("salario") * 12).alias("salario_anual")
)
```

**¿Por qué?** Polars es inmutable — `with_columns` siempre retorna un DataFrame nuevo. No hay `SettingWithCopyWarning` porque no hay asignación in-place.

## Filtrar filas

```python
# pandas
df[df["edad"] > 30]                             # máscara booleana
df.query("edad > 30")                           # string query

# polars
df.filter(pl.col("edad") > 30)                  # expresión
df.filter(
    (pl.col("edad") > 30) & (pl.col("ciudad") == "Madrid")
)
```

**¿Por qué?** Las expresiones son objetos que el optimizador puede analizar. La indexación booleana de pandas es opaca — pandas no puede "ver dentro" de `df[mask]`.

## Agrupar y agregar

```python
# pandas
df.groupby("ciudad").agg(
    salario_medio=("salario", "mean"),
    n=("nombre", "count"),
)

# polars
df.group_by("ciudad").agg(
    pl.col("salario").mean().alias("salario_medio"),
    pl.col("nombre").count().alias("n"),
)
```

**¿Por qué?** En Polars, cada agregación es una expresión completa — puedes hacer transformaciones complejas dentro del `agg`:

```python
# polars — imposible en una sola línea de pandas
df.group_by("ciudad").agg(
    pl.col("salario").filter(pl.col("edad") > 30).mean().alias("salario_senior"),
    (pl.col("salario").max() - pl.col("salario").min()).alias("rango"),
    pl.col("nombre").sort().first().alias("primer_nombre_alfa"),
)
```

## Joins

```python
# pandas
pd.merge(df1, df2, on="id", how="left")
# o
df1.merge(df2, on="id", how="left")

# polars
df1.join(df2, on="id", how="left")
```

La API es similar, pero Polars usa hash joins paralelos internamente. En modo lazy, el optimizador puede hacer projection pushdown en ambos lados del join.

## Apply / Map

```python
# pandas — apply fila por fila (LENTO)
df["resultado"] = df["texto"].apply(lambda x: x.upper().strip())
# pandas — vectorizado (RÁPIDO)
df["resultado"] = df["texto"].str.upper().str.strip()

# polars — expresión (RÁPIDO, Rust)
df = df.with_columns(
    pl.col("texto").str.to_uppercase().str.strip_chars().alias("resultado")
)
# polars — map_elements (LENTO, Python, último recurso)
df = df.with_columns(
    pl.col("texto").map_elements(
        lambda x: x.upper().strip(),
        return_dtype=pl.String
    ).alias("resultado")
)
```

**¿Por qué?** Tanto en pandas como en Polars, `.apply()` / `map_elements` es lento porque ejecuta Python fila por fila. La diferencia: en Polars, las expresiones nativas (`.str.*`, `.dt.*`, etc.) son mucho más completas, así que necesitas `map_elements` con menos frecuencia.

## Operaciones de texto

```python
# pandas
df["nombre"].str.lower()
df["nombre"].str.contains("alice")
df["nombre"].str.replace("old", "new")
df["nombre"].str.split(",")
df["nombre"].str.len()

# polars
pl.col("nombre").str.to_lowercase()
pl.col("nombre").str.contains("alice")
pl.col("nombre").str.replace("old", "new")
pl.col("nombre").str.split(",")            # retorna List[String]
pl.col("nombre").str.len_chars()
```

**¿Por qué?** pandas opera sobre objetos Python (dtype `object`). Polars opera sobre Arrow `Utf8` en Rust. La API es similar, pero el rendimiento difiere 5-50x en operaciones de texto pesadas.

## Operaciones temporales

```python
# pandas
df["fecha"] = pd.to_datetime(df["fecha_str"])
df["anio"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month
df["dia_semana"] = df["fecha"].dt.dayofweek

# polars
df = df.with_columns(
    pl.col("fecha_str").str.to_date("%Y-%m-%d").alias("fecha"),
).with_columns(
    pl.col("fecha").dt.year().alias("anio"),
    pl.col("fecha").dt.month().alias("mes"),
    pl.col("fecha").dt.weekday().alias("dia_semana"),
)
```

**¿Por qué?** En pandas, `pd.to_datetime` intenta adivinar el formato (lento). En Polars, especificas el formato (rápido y predecible).

## Window functions

```python
# pandas — rank dentro de grupo
df["rank"] = df.groupby("grupo")["valor"].rank()

# polars — .over() como window function
df = df.with_columns(
    pl.col("valor").rank().over("grupo").alias("rank")
)
```

`over()` es el equivalente Polars de una window function SQL — aplica la expresión particionada por grupo, sin colapsar filas.

```python
# Más ejemplos de .over()
df.with_columns(
    pl.col("valor").mean().over("grupo").alias("media_grupo"),
    pl.col("valor").sum().over("grupo").alias("total_grupo"),
    (pl.col("valor") - pl.col("valor").mean().over("grupo")).alias("desv_de_media"),
)
```

## Valores faltantes

```python
# pandas
df["col"].isna()                    # NaN check
df["col"].fillna(0)                 # reemplazar
df.dropna(subset=["col"])           # eliminar filas

# polars
pl.col("col").is_null()             # null check (no NaN)
pl.col("col").fill_null(0)          # reemplazar
df.drop_nulls(subset=["col"])       # eliminar filas
```

**¿Por qué?** pandas usa `NaN` (float IEEE 754) para representar datos faltantes — un entero con un null se convierte a float. Polars usa nulls nativos de Arrow con validity bitmap — el tipo se preserva.

## Pivot / Unpivot

```python
# pandas — pivot
df.pivot_table(index="fecha", columns="producto", values="ventas", aggfunc="sum")

# polars — pivot
df.pivot(on="producto", index="fecha", values="ventas", aggregate_function="sum")

# pandas — melt (unpivot)
pd.melt(df, id_vars=["fecha"], value_vars=["prod_a", "prod_b"])

# polars — unpivot
df.unpivot(index="fecha", on=["prod_a", "prod_b"])
```

## Encadenar operaciones

```python
# pandas — pipe o paréntesis
resultado = (
    df
    .query("precio > 100")
    .assign(total=lambda d: d["precio"] * d["cantidad"])
    .groupby("categoria")
    .agg(revenue=("total", "sum"))
    .sort_values("revenue", ascending=False)
)

# polars — encadenamiento natural con lazy
resultado = (
    pl.scan_csv("datos.csv")
    .filter(pl.col("precio") > 100)
    .with_columns(
        (pl.col("precio") * pl.col("cantidad")).alias("total")
    )
    .group_by("categoria").agg(
        pl.col("total").sum().alias("revenue")
    )
    .sort("revenue", descending=True)
    .collect()
)
```

**¿Por qué?** El encadenamiento en Polars es más natural porque cada método retorna un LazyFrame. No necesitas `lambda` ni `pipe` — cada operación es una expresión.

## Tabla resumen

| Operación | pandas | polars | Ventaja Polars |
|-----------|--------|--------|----------------|
| Leer CSV | `read_csv` | `scan_csv` (lazy) | Projection/predicate pushdown |
| Seleccionar | `df[cols]` | `df.select(cols)` | Sin ambigüedad |
| Crear columna | `df["x"] = ...` | `with_columns(expr)` | Inmutable, sin warnings |
| Filtrar | `df[mask]` | `df.filter(expr)` | Optimizable |
| Agrupar | `groupby().agg()` | `group_by().agg()` | Expresiones en agg |
| Join | `merge()` | `join()` | Hash join paralelo |
| Apply | `.apply()` | `map_elements()` | Más expresiones nativas |
| Strings | `.str.*` (object) | `.str.*` (Arrow Utf8) | 5-50x más rápido |
| Fechas | `.dt.*` | `.dt.*` | Formato explícito |
| Window | `groupby().transform()` | `.over()` | Sintaxis SQL natural |
| Nulls | `NaN` (float) | Arrow null (tipado) | Tipos preservados |

> **Verifica en el notebook:** Notebook 03 ejecuta cada una de estas comparaciones con código real, midiendo tiempos cuando la diferencia de rendimiento es significativa.
