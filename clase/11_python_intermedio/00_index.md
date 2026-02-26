# Módulo 11: Python Intermedio

En el módulo de Python aprendiste los fundamentos del lenguaje y tomaste un curso de principios de ingeniería de software. Ahora vamos a **usar** todo eso: repasar los conceptos clave a fondo y empezar a pensar como alguien que diseña software, no solo alguien que escribe scripts.

## Proyecto: Tu propia librería de Python

A lo largo de los próximos módulos vas a diseñar y construir una **librería de Python** desde cero. No un script. No un notebook. Una librería que alguien más podría instalar y usar.

El proyecto tiene varias fases:

| Fase | Enfoque | Herramientas |
|------|---------|--------------|
| **Fase 1** — Diseño (este módulo) | Pensar, abstraer, documentar | Tu cerebro, papel, markdown |
| **Fase 2** — Implementación mínima | Traducir el diseño a código funcional | Python, pytest, tu editor |
| **Fase 3** — Iteración con ChatGPT | Extender, refactorizar, comparar | ChatGPT |
| **Fase 4** — Iteración con Cursor | Flujo de desarrollo con IA integrada | Cursor IDE |

La idea es que **compares** lo que produces en cada fase. El mismo proyecto, diferentes herramientas, y — lo más importante — tu entendimiento creciendo en cada paso.

> **En este módulo NO vas a escribir código funcional.** Vas a pensar, dibujar, y escribir un documento de diseño. El código viene después.

## Contenido

### Parte 1: Repaso de ingeniería de software

Revisión profunda de los conceptos del curso de DataCamp. No es un resumen — es una referencia detallada con ejemplos que vas a necesitar.

| Sección | Tema | Tiempo estimado |
|---------|------|-----------------|
| [Paquetes, módulos e imports](./01_repaso_ingenieria.md) | Módulos, paquetes, `__init__.py`, `sys.path`, librería estándar, manejo de errores | ~25 min |
| [Clases y OOP](./02_clases_y_oop.md) | Dunder methods, properties, decoradores, herencia, composición, ABC | ~25 min |
| [Estilo y legibilidad](./03_estilo_y_legibilidad.md) | PEP 8, naming, type hints, linters, refactoring | ~20 min |
| [Testing y documentación](./04_testing_y_documentacion.md) | Docstrings, pytest (fixtures, parametrize), doctest, cobertura | ~25 min |
| [Paquetes instalables](./05_paquetes_instalables.md) | `pyproject.toml`, `pip install -e`, licencias, distribución | ~20 min |

### Parte 2: Diseño de tu librería

| Sección | Tema | Tiempo estimado |
|---------|------|-----------------|
| [Diseñando una librería](./06_disenando_una_libreria.md) | Quantum, vocabulario, dream usage, documento de diseño | ~30 min + trabajo |

## Prerequisitos

- Módulo 9: Fundamentos de Python completado
- Curso de DataCamp: Software Engineering Principles in Python completado
- `python3`, `pip`, `uv`, `pytest` instalados
