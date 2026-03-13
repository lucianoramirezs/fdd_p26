# Pandas en contexto

## De donde viene pandas

Wes McKinney creo pandas en 2008 mientras trabajaba en AQR Capital Management, un hedge fund cuantitativo. El problema era concreto: Python no tenia una herramienta decente para manipular datos tabulares con series de tiempo. R tenia su `data.frame`, pero Python solo ofrecia NumPy (arrays sin etiquetas), listas de diccionarios, o `csv.reader` manual.

El nombre viene de **panel data** — un termino de econometria para datos longitudinales (multiples entidades observadas a lo largo del tiempo). No tiene nada que ver con el animal.

McKinney lo hizo open source en 2009. Hoy es la libreria de datos tabulares mas usada en Python, con millones de descargas mensuales.

### Por que importa saber esto

Pandas fue disenado por un financiero que necesitaba mover datos rapido, no por un computer scientist optimizando rendimiento. Esto explica muchas decisiones de diseno:

- API enorme (200+ metodos en DataFrame) porque queria que todo fuera "una linea"
- Indices con etiquetas y alineacion automatica — util para series de tiempo, confuso para todo lo demas
- `NaN` como float de IEEE 754 — heredado de NumPy, con consecuencias que veremos
- Flexibilidad sobre rigidez — pandas rara vez te dice "no", pero a veces deberia

## Que problema resuelve (y cual no)

Pandas es una herramienta para **datos tabulares que caben en RAM**. Punto. Si tu problema se describe como "tengo una tabla con filas y columnas, y quiero transformarla", pandas probablemente es la respuesta correcta.

Pero no siempre. El error mas comun es usar pandas para todo:

| Situacion | Herramienta correcta | Por que no pandas |
|-----------|----------------------|-------------------|
| Tabla que cabe en RAM | **pandas** | — |
| Tabla en RAM, necesitas velocidad | **polars** | Rust, lazy eval, sin GIL, 2-10x mas rapido |
| No cabe en RAM | **dask**, **PySpark**, SQL | pandas carga todo en memoria |
| Solo filtrar y agregar | **SQL** directo | Mas claro, mas rapido, no necesitas Python |
| Arrays numericos sin etiquetas | **NumPy** directo | Menos overhead que un DataFrame |
| Datos jerarquicos/documentos | **diccionarios**, **JSON** | No fuerces un DataFrame donde no aplica |
| Iterar fila por fila | **listas/dicts** o repensar | Si haces `iterrows()` probablemente no necesitas pandas |

### La regla practica

> Si cabe en RAM y es tabular → pandas.
> Si cabe en RAM y necesitas velocidad → evalua polars.
> Si no cabe en RAM → necesitas otra cosa.

"Cabe en RAM" no significa que tu archivo sea menor que tu RAM. Pandas usa de **2x a 10x** el tamano del archivo en memoria (por tipos, indices, overhead interno). Un CSV de 2 GB puede necesitar 8-10 GB de RAM.

## La relacion con NumPy (y Arrow)

Pandas esta construido **sobre** NumPy. Cada `Series` es un wrapper de un `np.ndarray`. Esto tiene consecuencias directas:

- **Vectorizacion**: las operaciones que son rapidas en NumPy son rapidas en pandas. Las que no, no.
- **Missings**: `np.nan` es un `float` de IEEE 754. Por eso una columna de enteros con un missing se convierte en float. No es un bug de pandas — es una limitacion heredada de NumPy.
- **Strings**: NumPy no tiene un tipo string nativo. Pandas los mete en `object` (array de punteros a objetos Python) — lento y pesado.

**pandas 2.x** esta migrando a **Apache Arrow** (via PyArrow) como backend alternativo. Arrow maneja strings nativamente, tiene nullable types integrados, y es mas eficiente en memoria. Todavia es opcional, pero es el futuro.

```python
# Backend clasico (NumPy)
df = pd.read_csv("datos.csv")

# Backend Arrow (pandas 2.x)
df = pd.read_csv("datos.csv", dtype_backend="pyarrow")
```

## El ecosistema: donde encaja pandas

Pandas no vive solo. Es el **pegamento** del ecosistema de datos en Python:

```
                    ┌─────────────┐
                    │  Fuentes    │
                    │ CSV, SQL,   │
                    │ Parquet,API │
                    └──────┬──────┘
                           │ pd.read_*
                           ▼
              ┌────────────────────────┐
              │       pandas           │
              │  Limpiar, transformar, │
              │  explorar, agregar     │
              └───┬────────┬───────┬───┘
                  │        │       │
                  ▼        ▼       ▼
            matplotlib  scikit   to_parquet
            seaborn     learn    to_sql
            plotly      XGBoost  to_csv
```

- **Entrada**: `read_csv`, `read_parquet`, `read_sql`, `read_json`, `read_excel`
- **Procesamiento**: pandas para transformar, NumPy para calculo vectorizado pesado
- **Salida**: Parquet (entre sistemas), CSV (para humanos), SQL (para produccion)
- **Visualizacion**: matplotlib, seaborn, plotly — todos entienden DataFrames nativamente
- **ML**: scikit-learn, XGBoost, LightGBM esperan DataFrames o arrays como input

### Cuando escalar mas alla de pandas

Si tu pipeline en pandas tarda demasiado o se queda sin memoria, tienes opciones:

| Libreria | Modelo | Cuando usarla |
|----------|--------|---------------|
| **polars** | Single machine, Rust, lazy | DataFrames grandes, necesitas velocidad, API similar |
| **dask** | Paralelo, distribuido | DataFrames que no caben en RAM, cluster |
| **PySpark** | Distribuido, JVM | Datos masivos, infraestructura enterprise |
| **DuckDB** | SQL analitico, in-process | Queries analiticas sobre archivos locales |

No te cambies a otra herramienta "por si acaso". Pandas resuelve el 90% de los casos reales en ciencia de datos. Cambia cuando pandas te de un problema concreto, no antes.

## Versiones que importan

pandas tiene dos eras:

| | pandas 1.x | pandas 2.x |
|---|---|---|
| Backend | NumPy | NumPy + Arrow (opcional) |
| Copy-on-Write | Off | On por default |
| Nullable dtypes | Experimentales | Estables |
| Strings | `object` | `StringDtype` / Arrow string |
| Fecha release | 2020 | 2023 |

```python
import pandas as pd
print(pd.__version__)  # Saber tu version es el paso 0
```

### Copy-on-Write (CoW)

El cambio más importante de pandas 2.x es cómo maneja “subsets” (subconjuntos) de datos.

Cuando haces algo como `df[df["x"] > 0]` o `df[["a", "b"]]`, obtienes un **subset**: otro objeto “basado en” `df`.

- **Vista (view)**: el subset *comparte* los mismos datos en memoria que el DataFrame original. Si escribes sobre la vista, puedes terminar modificando el original.
- **Copia (copy)**: el subset trae sus propios datos (memoria separada). Si escribes, el original no cambia.

En pandas 1.x, a veces obtenías una vista y a veces una copia (según el caso y optimizaciones internas). Por eso era difícil razonar si esta línea iba a afectar a `df` o no.
El `SettingWithCopyWarning` es justamente la alerta de “no estoy seguro si estás modificando una copia o una vista; tu asignación puede no hacer lo que crees”.

Con **Copy-on-Write**, el comportamiento se vuelve más predecible:

- **Lecturas**: los objetos pueden compartir memoria (eficiente).
- **Escrituras**: si intentas modificar un subset, pandas primero separa los datos necesarios (hace la copia *en ese momento*) y luego aplica el cambio.

Eso es lo que significa **copia lógica**: *se comporta* como si fuera una copia desde el punto de vista del usuario, aunque la copia física solo ocurra cuando escribes. Resultado: menos ambigüedad, menos warnings y menos bugs silenciosos.

## Filosofia y consejo practico

Pandas tiene una API enorme. DataFrame tiene mas de 200 metodos. No necesitas conocerlos todos — dominar 20-30 cubre el 90% de los casos reales.

Los LLMs conocen toda la API pero no siempre eligen el metodo correcto para tu contexto. Saber **cuando no usar pandas** y **como estructurar tu codigo** es mas valioso que memorizar metodos. Eso es lo que cubre el siguiente capitulo.

:::exercise{title="Reflexion" difficulty="1"}
Piensa en un proyecto de datos que hayas hecho (o un ejercicio del curso anterior). ¿Hubo algun momento donde pandas no era la herramienta correcta? ¿Usaste `iterrows()` o un loop sobre el DataFrame? ¿Que alternativa habrias usado sabiendo lo que sabes ahora?
:::
