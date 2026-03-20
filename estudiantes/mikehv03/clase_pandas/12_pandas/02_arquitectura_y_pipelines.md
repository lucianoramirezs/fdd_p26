# Arquitectura y pipelines de datos

Saber pandas es saber los comandos. Saber **usar** pandas es saber como organizar tu codigo para que sea reproducible, debuggeable, y que no se caiga cuando cambien los datos.

Este capitulo es sobre como pensar tu codigo de datos como un ingeniero, no como alguien que escribe celdas en un notebook hasta que sale el resultado.

## El pipeline como unidad de diseno

Tu codigo de datos no es un script lineal — es un **pipeline** con etapas. Cada etapa tiene una responsabilidad clara:

```
Ingestion → Validacion → Limpieza → Transformacion → Analisis → Exportacion
```

Esto no es teoria abstracta. Es la diferencia entre codigo que puedes mantener y codigo que tiras a la basura despues de usarlo una vez.

Cada etapa debe ser una funcion que recibe un DataFrame y devuelve un DataFrame:

```python
def limpiar_nombres(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza nombres de columnas."""
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return df
```

**Si no puedes describir que hace una etapa en una oracion, es demasiado grande.** Dividela.

## Method chaining y `.pipe()`

pandas esta disenado para encadenar operaciones. Compara estos dos estilos:

### Estilo espagueti (comun en notebooks)

```python
df = pd.read_csv("ventas.csv")
df = df.dropna(subset=["monto"])
df["monto"] = df["monto"].astype(float)
df["fecha"] = pd.to_datetime(df["fecha"])
df = df[df["monto"] > 0]
df["mes"] = df["fecha"].dt.to_period("M")
resultado = df.groupby("mes")["monto"].sum()
```

Funciona, pero: 7 reasignaciones de `df`, si algo falla no sabes en que paso, y es dificil reutilizar piezas.

### Estilo pipeline (funcional)

```python
def cargar(path):
    return pd.read_csv(path)

def limpiar_montos(df):
    return (
        df
        .dropna(subset=["monto"])
        .assign(monto=lambda d: d["monto"].astype(float))
        .query("monto > 0")
    )

def agregar_periodo(df):
    return df.assign(
        fecha=lambda d: pd.to_datetime(d["fecha"]),
        mes=lambda d: pd.to_datetime(d["fecha"]).dt.to_period("M"),
    )

# Pipeline completo
resultado = (
    cargar("ventas.csv")
    .pipe(limpiar_montos)
    .pipe(agregar_periodo)
    .groupby("mes")["monto"]
    .sum()
)
```

Cada funcion hace una cosa. Puedes testearlas individualmente. Puedes reordenarlas. Puedes reutilizarlas. Si algo falla, sabes exactamente donde.

**Regla**: si necesitas mas de 3 variables intermedias en un bloque, probablemente puedes encadenar con `.pipe()`.

## Validacion y contratos de datos

El error mas caro es el que descubres al final del pipeline. El segundo mas caro es el que nunca descubres.

**Patron defensivo**: validar en cada transicion.

```python
def validar_schema(df, columnas_esperadas):
    """Valida que el DataFrame tenga las columnas necesarias."""
    faltantes = set(columnas_esperadas) - set(df.columns)
    assert not faltantes, f"Columnas faltantes: {faltantes}"
    return df

def validar_rangos(df):
    """Asserts de cordura sobre los datos."""
    assert df["edad"].between(0, 120).all(), "Edades fuera de rango"
    assert df["monto"].ge(0).all(), "Montos negativos encontrados"
    assert df["id"].is_unique, "IDs duplicados"
    return df

# Integrado en el pipeline
resultado = (
    pd.read_csv("datos.csv")
    .pipe(validar_schema, ["id", "edad", "monto", "fecha"])
    .pipe(limpiar_nombres)
    .pipe(limpiar_montos)
    .pipe(validar_rangos)
    .pipe(agregar_periodo)
)
```

`assert` no es solo para tests. Es tu primera linea de defensa. **Fallar rapido es mejor que debuggear 200 lineas despues.**

### Que validar y cuando

| Momento | Que validar |
|---------|-------------|
| **Al ingestar** | ¿Llegaron las columnas? ¿Los tipos basicos? ¿El archivo no esta vacio? |
| **Despues de limpiar** | ¿Se eliminaron los nulls esperados? ¿Los rangos son razonables? |
| **Antes de exportar** | ¿El output tiene el schema correcto? ¿No hay duplicados inesperados? |
| **Antes de un merge** | ¿Las keys estan limpias? ¿Son del mismo tipo? ¿Hay duplicados en la key? |

## Exploracion vs. produccion

Hay dos modos de usar pandas, y confundirlos es un error comun:

| | Exploracion | Produccion |
|---|---|---|
| **Donde** | Notebook | Script `.py` / modulo |
| **Objetivo** | Entender los datos | Que corra sin ti |
| **Estilo** | `head()`, plots, prueba y error | Funciones, tipos, logging |
| **Calidad** | Esta bien ser desordenado | Reproducible, validado |
| **Duracion** | Una sesion | Meses o anos |

El flujo sano:

```
Notebook (explorar)
    → Identificar patrones
        → Extraer logica a funciones
            → Mover funciones a modulo .py
                → Notebook solo importa y llama al modulo
```

**El error**: quedarse en modo exploracion para siempre. Un notebook de 200 celdas sin funciones es deuda tecnica pura. Nadie (incluyendote en 3 meses) va a entender que hace.

**El otro error**: intentar escribir codigo de produccion desde el principio sin explorar. Primero entiende los datos, despues estructura el codigo.

## Formatos de archivo como decision arquitectonica

Elegir formato no es trivial. Afecta velocidad, espacio, compatibilidad, y correctitud:

| Formato | Ventajas | Desventajas | Cuando usarlo |
|---------|----------|-------------|---------------|
| **CSV** | Universal, legible por humanos | Pierde tipos, lento, encoding hell | Compartir con no-programadores, datos pequenos |
| **Parquet** | Columnar, comprimido, preserva tipos | No legible por humanos | **Default para todo lo demas** |
| **Feather** | Muy rapido en I/O local | Sin compresion | Cache temporal entre pasos |
| **SQLite/SQL** | Consultas ad-hoc, concurrencia | Overhead de setup | Datos que cambian, acceso concurrente |
| **Excel** | Lo conoce todo el mundo | Lento, limites de filas, fragil | Cuando tu audiencia vive en Excel |

### La regla de Parquet

> Si guardas un CSV y luego lo lees con pandas en otro script, deberias estar usando Parquet.

¿Por que?

```python
# CSV: pierde tipos, lento
df.to_csv("datos.csv", index=False)
df2 = pd.read_csv("datos.csv")  # tipos reinferidos, fechas son strings

# Parquet: preserva todo, rapido, comprimido
df.to_parquet("datos.parquet")
df2 = pd.read_parquet("datos.parquet")  # tipos exactos, 3-5x mas rapido
```

Parquet ademas permite leer **solo las columnas que necesitas**:

```python
# Solo 2 columnas de un archivo con 50
df = pd.read_parquet("datos.parquet", columns=["id", "monto"])
```

## Memoria y performance como decision de diseno

Esto no es optimizacion prematura. Es saber que escala y que no, **antes** de que tu pipeline tarde 40 minutos.

### Diagnostico rapido

```python
df.info(memory_usage="deep")  # Primer reflejo al cargar datos
df.memory_usage(deep=True)    # Por columna, en bytes
```

### Las trampas de memoria

| Situacion | Problema | Solucion |
|-----------|----------|----------|
| Columna de strings como `object` | 5-10x mas cara de lo que parece | `category` si tiene pocos valores unicos, `StringDtype` si no |
| `float64` por default | Desperdicia RAM | Downcast a `float32` si la precision no importa |
| `int64` con missings | Se promueve a `float64` | `Int64` (nullable) |
| Cargar archivo completo | Todo en RAM | `usecols=` para leer solo columnas necesarias |
| Archivo grande, solo explorar | Carga 1M filas para ver 5 | `nrows=1000` para inspeccionar |

### Jerarquia de velocidad

Del mas rapido al mas lento para la misma operacion:

```
Operacion vectorizada NumPy/pandas  →  mas rapido (10-100x)
     ↓
List comprehension                  →  rapido para cosas simples
     ↓
.apply() con funcion Python         →  lento (loop disfrazado)
     ↓
.iterrows()                         →  muy lento (nunca en produccion)
```

**Si un LLM te sugiere `.apply()`, preguntate si hay una operacion vectorizada equivalente.** En el 80% de los casos la hay.

```python
# Lento: apply
df["upper"] = df["nombre"].apply(lambda x: x.upper())

# Rapido: vectorizado
df["upper"] = df["nombre"].str.upper()

# Lento: apply para aritmetica
df["total"] = df.apply(lambda row: row["precio"] * row["cantidad"], axis=1)

# Rapido: vectorizado
df["total"] = df["precio"] * df["cantidad"]
```

## Errores comunes (y de LLMs)

Estos son errores que ves en codigo real y que los LLMs cometen frecuentemente:

### 1. `inplace=True`

```python
# No hagas esto
df.dropna(inplace=True)
df.reset_index(inplace=True)

# Haz esto
df = df.dropna().reset_index(drop=True)
```

`inplace=True` no ahorra memoria (pandas crea una copia interna de todas formas), rompe method chaining, y esta deprecated en espiritu. No lo uses.

### 2. Chained indexing

```python
# Bug silencioso: puede no modificar df
df[df["edad"] > 30]["score"] = 100

# Correcto
df.loc[df["edad"] > 30, "score"] = 100
```

### 3. `fillna()` sin pensar

```python
# Peligroso: 0 tiene significado en temperatura, balance, score...
df["temperatura"].fillna(0)

# Mejor: pensar que significa el missing
df["temperatura"].fillna(df["temperatura"].median())
```

### 4. Pipeline acoplado

```python
# Mal: una funcion que hace TODO
def procesar_datos(path):
    df = pd.read_csv(path)
    df = df.dropna()
    df["x"] = df["x"] * 2
    df.to_csv("resultado.csv")
    fig = df.plot()
    fig.savefig("grafica.png")
    return df

# Bien: funciones separadas por responsabilidad
def cargar(path):
    return pd.read_csv(path)

def limpiar(df):
    return df.dropna()

def transformar(df):
    return df.assign(x=lambda d: d["x"] * 2)

def exportar(df, path):
    df.to_parquet(path)
```

### 5. No versionar datos intermedios

Si tu pipeline tarda 10 minutos y falla en el paso 8, no quieres re-ejecutar los pasos 1-7. Guarda checkpoints:

```python
# Despues de limpieza pesada
df_limpio.to_parquet("intermedios/01_limpio.parquet")

# En la siguiente sesion, retoma desde ahi
df_limpio = pd.read_parquet("intermedios/01_limpio.parquet")
```

### 6. Ignorar tipos al cargar

```python
# Mal: pandas infiere todo, a veces mal
df = pd.read_csv("datos.csv")

# Bien: tu defines los tipos
df = pd.read_csv("datos.csv", dtype={
    "id": "Int64",
    "nombre": "string",
    "activo": "boolean",
    "monto": "float64",
}, parse_dates=["fecha"])
```

## Resumen

| Principio | Aplicacion |
|-----------|------------|
| Pipeline con etapas | Cada funcion: `DataFrame → DataFrame`, una responsabilidad |
| `.pipe()` y chaining | Codigo legible, debuggeable, reutilizable |
| Validacion defensiva | `assert` entre etapas, fallar rapido |
| Exploracion ≠ Produccion | Notebook para explorar, `.py` para produccion |
| Parquet > CSV | Para datos intermedios y finales, siempre |
| Tipos explicitos | Definir al cargar, no dejar que pandas adivine |
| Vectorizar | Antes de `.apply()`, buscar operacion nativa |
| Checkpoints | Guardar intermedios en pipelines largos |

:::exercise{title="Disena tu pipeline" difficulty="2"}
Piensa en un dataset que hayas trabajado (o inventa uno: ventas de una tienda con fecha, producto, monto, cliente). Escribe en pseudocodigo (o Python real) un pipeline con al menos 4 etapas usando `.pipe()`. Incluye al menos 2 validaciones con `assert`.
:::

:::prompt{title="Critica mi pipeline" for="ChatGPT/Claude"}
Pega tu pipeline de pandas en el prompt y pregunta:

"Revisa este pipeline de limpieza de datos en pandas. Identifica: (1) pasos que podrian fallar silenciosamente, (2) oportunidades de vectorizacion donde uso apply, (3) validaciones que faltan, (4) si los tipos de datos son correctos. Se especifico y da ejemplos de como mejorarlo."
:::
