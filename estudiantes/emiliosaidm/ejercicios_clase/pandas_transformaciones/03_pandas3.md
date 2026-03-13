# Pandas 3.0 — Que cambio y por que importa

pandas 3.0 salio en enero de 2025. No es una actualizacion menor: consolida anos de cambios que venian siendo opcionales o experimentales en pandas 2.x y elimina APIs que llevaban tiempo deprecadas. Si tu codigo fue escrito para pandas 1.x o 2.x, probablemente tiene cosas que ya no funcionan igual.

Este capitulo documenta los cambios que mas afectan el trabajo cotidiano en ciencia de datos.

## Copy-on-Write es ahora obligatorio

El cambio mas importante. En pandas 2.x, Copy-on-Write (CoW) era opt-in:

```python
# pandas 2.x: habia que activarlo manualmente
pd.options.mode.copy_on_write = True
```

En pandas 3.0, CoW **es el comportamiento default e inamovible**. Ya no existe la opcion de desactivarlo.

### Que significa esto en la practica

El problema que CoW resuelve: en pandas 1.x/2.x (sin CoW), modificar un subconjunto de un DataFrame a veces modificaba el original y a veces no, dependiendo de si pandas habia creado una vista o una copia interna. El resultado era impredecible y generaba el infame `SettingWithCopyWarning`.

```python
# pandas < 3.0: comportamiento AMBIGUO
subset = df[df["edad"] > 30]
subset["score"] = 100  # ¿Modifica df? Depende. SettingWithCopyWarning.

# pandas 3.0: comportamiento PREDECIBLE
# subset es siempre una copia logica. Modificarla nunca afecta df.
subset = df[df["edad"] > 30]
subset["score"] = 100  # Modifica subset, df no cambia. Sin warning.

# Para modificar df, usa .loc explicitamente:
df.loc[df["edad"] > 30, "score"] = 100  # Esto si modifica df.
```

Si tu codigo dependia del comportamiento de modificar vistas, necesita ser revisado.

## Strings con Arrow por default

pandas 3.0 cambia el tipo por default de columnas de texto. En pandas 2.x, leer un CSV con texto daba columnas de tipo `object` (arrays de punteros a objetos Python — lento y pesado). En pandas 3.0, el default es `pd.StringDtype()` respaldado por Apache Arrow.

```python
# pandas 2.x
df = pd.read_csv("datos.csv")
df["nombre"].dtype  # object

# pandas 3.0
df = pd.read_csv("datos.csv")
df["nombre"].dtype  # string[python] o string[pyarrow]
```

Ventajas: mas rapido, menos memoria, mejor soporte para `pd.NA`. El comportamiento con `NaN` cambia: antes una columna `object` podia mezclar strings y `NaN`; ahora usa `pd.NA` consistentemente.

Si necesitas el comportamiento legacy:
```python
df = pd.read_csv("datos.csv", dtype_backend="numpy_nullable")
```

## `applymap` eliminado — usar `map`

`DataFrame.applymap()` fue renombrado a `DataFrame.map()` en pandas 2.1 (dejando `applymap` como alias deprecado). En pandas 3.0 el alias fue **eliminado**. Codigo que use `applymap` lanzara `AttributeError`.

```python
# pandas < 3.0 (funciona pero lanza DeprecationWarning en 2.1+)
df.applymap(lambda x: round(x, 2))

# pandas 3.0 (correcto)
df.map(lambda x: round(x, 2))
```

Este cambio conecta directamente con lo que viste en el notebook de `apply/map/transform` de este modulo.

## `groupby` con `observed=True` por default

Cambio que afecta a cualquiera que use `groupby` con columnas categoricas. En pandas 2.x, el default era `observed=False`, que incluia en el resultado todas las combinaciones de categorias aunque no hubiera datos para esa combinacion. En pandas 3.0 el default es `observed=True`.

```python
cat = pd.Categorical(["a", "a", "b"], categories=["a", "b", "c"])
df = pd.DataFrame({"grupo": cat, "valor": [1, 2, 3]})

# pandas 2.x (observed=False por default)
df.groupby("grupo")["valor"].sum()
# grupo
# a    3
# b    3
# c    0  ← categoria "c" sin datos aparece con 0

# pandas 3.0 (observed=True por default)
df.groupby("grupo")["valor"].sum()
# grupo
# a    3
# b    3   ← "c" no aparece porque no hay datos
```

Si tu pipeline depende de que aparezcan todas las categorias (por ejemplo, para reportes), especifica `observed=False` explicitamente.

## APIs eliminadas

pandas 3.0 elimina varios metodos y parametros que llevaban versiones con `DeprecationWarning`. Los mas comunes:

| Eliminado en 3.0 | Reemplazo |
|---|---|
| `DataFrame.applymap()` | `DataFrame.map()` |
| `DataFrame.swapaxes()` | Transponer manualmente |
| `Series.swapaxes()` | Igual |
| `DataFrame.append()` | `pd.concat([df1, df2])` |
| Parametro `inplace=` en muchos metodos | Reasignar: `df = df.metodo()` |

`DataFrame.append()` era el mas usado. Fue eliminado desde pandas 2.0 pero aun aparece en codigo legacy y tutoriales viejos. La alternativa correcta es `pd.concat()`.

## Mejoras de performance

pandas 3.0 aprovecha Arrow mas agresivamente internamente:

- Operaciones sobre strings hasta 3-5x mas rapidas con Arrow backend
- Menor uso de memoria para columnas de texto
- Mejoras en `read_csv`, `read_parquet`, y operaciones de `groupby`
- Copy-on-Write elimina copias innecesarias en pipelines encadenados

## El notebook

El notebook recorre estos cambios con codigo ejecutable: comparaciones de comportamiento, casos donde codigo de pandas 2.x falla en 3.0, y como migrar.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/14_pandas_transformaciones/code/04_pandas3.ipynb)

:::exercise{title="Auditoria de compatibilidad" difficulty="2"}
Toma cualquier notebook de pandas que hayas escrito (de los modulos 12, 13 o 14). Busca: (1) uso de `applymap`, (2) patrones de chained indexing como `df[cond]["col"] = val`, (3) uso de `.append()`, (4) `groupby` sobre columnas categoricas. Documenta que cambiaria al correr ese codigo en pandas 3.0.
:::
