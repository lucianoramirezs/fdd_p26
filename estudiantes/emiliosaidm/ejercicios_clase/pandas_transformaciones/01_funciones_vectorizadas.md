# Funciones vectorizadas: apply, map y transform

La pregunta central es siempre la misma: **¿sobre que objeto corre mi funcion?**

```
¿Que recibe f()?
─────────────────────────────────────────────────────────
Series.map(f)              → 1 valor escalar por llamada
Series.apply(f)            → 1 valor escalar por llamada

DataFrame.apply(f, axis=0) → 1 columna completa (Series)
DataFrame.apply(f, axis=1) → 1 fila completa (Series)

DataFrame.map(f)           → 1 valor escalar (celda a celda)

DataFrame.pipe(f)          → el DataFrame entero
```

La confusion mas comun: `DataFrame.apply(axis=0)` no aplica `f` a cada celda — aplica `f` a cada **columna**. Si tu funcion espera un escalar y recibes una Serie, falla de maneras inesperadas.

## El contrato de output importa

Lo que `f` devuelve determina la forma del resultado:

| `f` devuelve | `Series.apply` devuelve | `DataFrame.apply` devuelve |
|---|---|---|
| escalar | Serie | Serie |
| Serie (mismo indice) | DataFrame | DataFrame |
| Serie (indice diferente) | DataFrame con NaN | DataFrame con NaN |
| dict | DataFrame | DataFrame |

Esto no es obvio y tiene edge cases que el notebook cubre en detalle.

## `transform` vs `apply`

Misma firma, contrato diferente:

- `apply`: puede cambiar la forma del resultado — devuelve lo que devuelva `f`
- `transform`: **debe** devolver un objeto del mismo tamano que la entrada — util con `groupby`

El caso clasico de `transform`: agregar una columna con el promedio del grupo sin perder filas.

```python
# apply: colapsa a un valor por grupo
df.groupby("ciudad")["salario"].apply(np.mean)    # → Serie con un valor por ciudad

# transform: mantiene la forma original, repite el valor por grupo
df["salario_medio_ciudad"] = df.groupby("ciudad")["salario"].transform(np.mean)  # → Serie misma longitud
```

## El notebook

Todo el detalle, los edge cases, y los experimentos estan en el notebook.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/14_pandas_transformaciones/code/01_apply_map_transform.ipynb)
