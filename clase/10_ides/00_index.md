# Módulo 10: IDEs (VS Code)

Una **IDE** (Integrated Development Environment) es un conjunto de herramientas que convierten “editar texto” en “construir software” con fricción mínima: editor, navegación, terminal, ejecución, debugging, git, extensiones, notebooks, etc.

En este módulo nos enfocamos en **Visual Studio Code** porque es el estándar de facto en ciencia de datos + software, y porque se integra muy bien con Python, Docker y notebooks.

::::homework{id="10.0" title="Instalar y configurar VS Code para Python" points="0"}

Tu meta es que al final puedas:
- Abrir un proyecto Python (con entorno virtual)
- Ejecutar y debuggear código desde VS Code
- Usar Jupyter notebooks dentro de VS Code
- Correr tu proyecto dentro de Docker desde la IDE

Si ya lo tienes instalado, igual recorre este módulo y asegura que tu setup es reproducible.

::::

## Prerequisitos

Este módulo asume que ya viste (o al menos puedes consultar):

- **Terminal**: [Módulo 4](../04_terminal/00_index.md) (vas a usar la terminal integrada todo el tiempo)
- **Python**: [Módulo 9](../09_python/00_index.md) (entornos virtuales, pip/uv, ejecutar scripts)
- **Docker**: [Módulo 8](../08_containers/00_index.md) (Dockerfile, imágenes/contendedores, volúmenes)

## Contenido del módulo

| # | Sección | Descripción |
|---|---------|-------------|
| 1 | [¿Qué es una IDE?](./01_que_es_una_ide.md) | La idea, por qué importa, editor vs IDE, proyecto vs archivo suelto |
| 2 | [VS Code: instalación + layout + shortcuts](./02_vscode_instalacion_layout.md) | Ventanas/paneles, Command Palette, atajos esenciales, terminal integrada |
| 3 | [Python en VS Code (venv/uv, ejecutar, depurar)](./03_python_en_vscode.md) | Selección de intérprete, `.venv`, `launch.json`, debugging básico |
| 4 | [Extensiones, settings y personalización](./04_extensiones_y_config.md) | Marketplace, Python/Jupyter/Docker/Dev Containers, themes, tipografía, settings.json |
| 5 | [Jupyter notebooks, tabs y flujo de trabajo](./05_jupyter_debugging.md) | Kernels, `ipykernel`, celdas, variables, breakpoints, notebooks vs scripts |
| 6 | [Ejercicio E2E: proyecto Python + Docker en VS Code](./06_proyecto_e2e_python_docker.md) | Proyecto completo, build/run, debugging, terminal, reproducibilidad |

---

## Modelo mental (lo mínimo que debes recordar)

Una IDE es como un “cockpit”: todo está diseñado para reducir el tiempo entre **idea → cambio → ejecutar → ver resultado → iterar**.

```mermaid
flowchart LR
  A[Editar] --> B[Ejecutar]
  B --> C[Observar]
  C --> D[Debuggear]
  D --> A

  style A fill:#4a3080,stroke:#7c5cbf
  style B fill:#2d5a1e,stroke:#4a8f32
  style C fill:#1a3a5c,stroke:#2a6a9c
  style D fill:#8b1a1a,stroke:#cc3333
```

La terminal (módulo 4) sigue siendo esencial: VS Code no reemplaza a la terminal; la integra.

