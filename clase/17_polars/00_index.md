---
title: "Polars — DataFrames modernos"
---

# Polars — DataFrames modernos

Ya sabes pandas. Sabes leer datos, transformar columnas, agrupar, unir tablas. Entonces, ¿por qué aprender otra librería de DataFrames?

Porque **pandas tiene límites estructurales que no se pueden arreglar sin romperlo**. Su creador, Wes McKinney, los documentó él mismo en 2017. Polars es la respuesta: una librería diseñada desde cero en Rust, con evaluación lazy, paralelismo real (sin GIL), y Apache Arrow como formato nativo de memoria.

Este módulo conecta dos hilos del curso:

```
Secciones 12–14: pandas (manipulación de datos tabulares)
Secciones 15–16: modelos de ejecución (paralelismo, lazy eval, GIL)
        │                              │
        └──────────┬───────────────────┘
                   ▼
        Sección 17: Polars
        = arquitectura de cómputo aplicada a datos tabulares
```

Polars no es "pandas pero más rápido" — es una forma diferente de pensar sobre transformación de datos. Las expresiones reemplazan la indexación booleana, la evaluación lazy reemplaza la ejecución inmediata, y el optimizador de consultas decide el mejor plan de ejecución antes de tocar un solo dato.

## Contenido

| Archivo | Tema | Notebook | Tiempo est. |
|---------|------|----------|-------------|
| [Historia y diseño](./01_historia_y_diseno.md) | Origen, motivación, filosofía de diseño | — | ~10 min |
| [Arquitectura](./02_arquitectura.md) | Arrow, lazy vs eager, optimizador, Rayon, tipos | — | ~15 min |
| [Polars puro](./03_polars_puro.md) | Expresiones, contextos, UDFs, listas, Struct, LazyFrame | [01_polars_fundamentos](./code/01_polars_fundamentos.ipynb) | ~20 min + ~35 min |
| [Pipeline E2E](./04_pipeline_e2e.md) | Limpieza de datos completa en Polars | [02_pipeline_e2e](./code/02_pipeline_e2e.ipynb) | ~15 min + ~30 min |
| [Polars vs pandas](./05_polars_vs_pandas.md) | Comparación lado a lado de operaciones comunes | [03_polars_vs_pandas](./code/03_polars_vs_pandas.ipynb) | ~15 min + ~25 min |
| [Benchmarks](./06_benchmarks.md) | Análisis de rendimiento con explicación arquitectónica | [04_benchmarks_y_avanzado](./code/04_benchmarks_y_avanzado.ipynb) | ~10 min + ~60 min |

## Notebooks

| Notebook | Tema | Tiempo est. |
|----------|------|-------------|
| [01 — Fundamentos](./code/01_polars_fundamentos.ipynb) | Expresiones, contextos, UDFs, listas, LazyFrame | ~35 min |
| [02 — Pipeline E2E](./code/02_pipeline_e2e.ipynb) | Limpieza de datos completa paso a paso | ~30 min |
| [03 — Polars vs pandas](./code/03_polars_vs_pandas.ipynb) | Comparaciones lado a lado con timing | ~25 min |
| [04 — Benchmarks y avanzado](./code/04_benchmarks_y_avanzado.ipynb) | Benchmarks, series de tiempo avanzadas, ejercicios | ~60 min |

[![Open NB01 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/17_polars/code/01_polars_fundamentos.ipynb)
[![Open NB02 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/17_polars/code/02_pipeline_e2e.ipynb)
[![Open NB03 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/17_polars/code/03_polars_vs_pandas.ipynb)
[![Open NB04 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/17_polars/code/04_benchmarks_y_avanzado.ipynb)

## Prerequisitos

- Módulos 12–14: pandas completados
- Módulo 16: modelos de ejecución (recomendado, no obligatorio)
- Python 3.10+
- `polars` ≥ 1.0, `pandas`, `numpy`, `matplotlib` instalados

```bash
pip install polars pandas numpy matplotlib
```
