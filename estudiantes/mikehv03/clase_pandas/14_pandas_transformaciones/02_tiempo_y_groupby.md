# Timestamps, Timezones y Groupby

## Timestamps: el problema de las fechas en datos reales

Las fechas en datos reales vienen en decenas de formatos: `"2024-01-15"`, `"15/01/2024"`, `"Jan 15, 2024"`, `1705276800` (Unix timestamp). Pandas puede parsear todos, pero necesitas decirle como.

El problema mas sutil es el de **timezones**. Un timestamp sin timezone es ambiguo — no sabes si `"2024-01-15 10:00"` es hora de Ciudad de Mexico, UTC, o Nueva York. Cuando combinas datos de fuentes distintas sin normalizar a UTC primero, puedes tener diferencias de horas silenciosas en tus calculos.

La regla:
```
Siempre almacena en UTC internamente.
Convierte a timezone local solo para mostrar.
```

## Groupby: lo que probablemente ya sabes y lo que no

Ya usaste `groupby` en el curso anterior. Aqui el foco es en los tres modos que tiene y cuando usar cada uno:

| Modo | Metodo | Forma del output | Uso tipico |
|------|--------|-----------------|------------|
| **Agregar** | `.agg()` | Menos filas (una por grupo) | Calcular estadisticas por grupo |
| **Transformar** | `.transform()` | Mismas filas que el original | Agregar columna con estadistica del grupo |
| **Filtrar** | `.filter()` | Subset de filas originales | Quitar grupos que no cumplen condicion |

La mayoria solo conoce el modo agregar. `transform` es el que mas se necesita en ciencia de datos (feature engineering) y el menos conocido.

## Los notebooks

[![Open in Colab — Timestamps](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/14_pandas_transformaciones/code/02_timestamps.ipynb)

[![Open in Colab — Groupby](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/14_pandas_transformaciones/code/03_groupby.ipynb)
