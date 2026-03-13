# Modulo 14: Pandas — Transformaciones y Tiempo

Tienes tus datos limpios y combinados. Ahora los necesitas **transformar**: aplicar funciones, agregar por grupos, y manejar fechas correctamente.

Este modulo cubre las operaciones funcionales de pandas (`apply`, `map`, `transform`) con detalle real sobre que recibe y devuelve cada una, mas timestamps y UTC, mas `groupby` (brevemente — ya lo viste antes, aqui entramos a los casos menos obvios).

## Contenido

| Seccion | Tema | Tiempo |
|---------|------|--------|
| [Funciones vectorizadas](./01_funciones_vectorizadas.md) | El mapa mental de apply/map/transform | ~8 min |
| [Tiempo y groupby](./02_tiempo_y_groupby.md) | Timestamps, UTC, groupby avanzado | ~5 min |
| [Pandas 3.0](./03_pandas3.md) | CoW obligatorio, strings Arrow, applymap eliminado, groupby observed, migracion | ~10 min |

## Notebooks

| Notebook | Tema | Tiempo |
|----------|------|--------|
| [Apply, Map y Transform](./code/01_apply_map_transform.ipynb) | map/apply en Series, apply con axis en DataFrame, applymap, transform, edge cases, argumentos extra | ~35 min |
| [Timestamps y Timezones](./code/02_timestamps.ipynb) | to_datetime, formatos, UTC, tz_localize/convert, .dt accessor, features temporales | ~15 min |
| [Groupby](./code/03_groupby.ipynb) | agg, transform, filter, named agg, multicolumna | ~10 min |
| [Pandas 3.0](./code/04_pandas3.ipynb) | Cambios de comportamiento, codigo legacy vs moderno, checklist de migracion | ~20 min |

[![Open in Colab — Apply/Map](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/14_pandas_transformaciones/code/01_apply_map_transform.ipynb)
[![Open in Colab — Timestamps](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/14_pandas_transformaciones/code/02_timestamps.ipynb)
[![Open in Colab — Groupby](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/14_pandas_transformaciones/code/03_groupby.ipynb)
[![Open in Colab — Pandas 3.0](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/14_pandas_transformaciones/code/04_pandas3.ipynb)

## Prerequisitos

- Modulo 12 y 13: Pandas completados
- `pip install -r requirements.txt`
