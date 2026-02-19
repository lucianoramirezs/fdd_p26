# ¿Qué es una IDE?

Antes de aprender botones, hay que entender el concepto.

## Editor vs IDE

- Un **editor de texto** te deja escribir archivos.
- Una **IDE** te da un “entorno”: entiende tu proyecto, te ayuda a navegarlo, ejecutarlo, probarlo, depurarlo y mantenerlo.

Piensa en esto como diferencia entre:

- **Notepad**: “puedo escribir”
- **IDE**: “puedo construir”

## ¿Qué problemas resuelve una IDE?

### 1) Navegación y escala

Un proyecto real no es un archivo: son carpetas, módulos, dependencias, tests, configs. Una IDE te da:

- Búsqueda global
- Ir a definición / referencias
- Refactors (renombrar símbolos sin romper todo)
- Exploración por árbol (carpetas)

### 2) Feedback rápido (errores antes de correr)

Una IDE puede marcar:

- Errores de sintaxis
- Imports rotos
- Tipos (si usas type hints)
- Estilo (formatters)
- Problemas comunes (linters)

Eso reduce tu ciclo de prueba/error.

### 3) Debugging (la diferencia entre “adivinar” y “ver”)

Con un debugger puedes:

- Poner breakpoints
- Ver variables en tiempo real
- Entrar/salir de funciones paso a paso
- Inspeccionar stacks y excepciones

> En data science, esto te evita imprimir 200 `print()` y perderte.

### 4) Integración con herramientas modernas

En este curso, tres herramientas aparecen todo el tiempo:

- **Terminal**: ejecutar comandos, scripts, git, docker, etc.
- **Git**: versiones, branches, PRs.
- **Docker**: reproducibilidad, ambientes idénticos.

Una IDE buena no “las reemplaza”, pero sí:

- te muestra el estado,
- te facilita comandos comunes,
- y te reduce el contexto que tienes que sostener en tu cabeza.

---

## El concepto clave: “proyecto”

Muchos principiantes trabajan así:

- abren un archivo suelto `script.py`
- lo ejecutan “como sea”
- y cuando algo falla, no saben qué Python están usando o dónde se instaló el paquete

Una IDE funciona mejor cuando trabajas como **proyecto**:

```
mi-proyecto/
├── pyproject.toml   (o requirements.txt)
├── .venv/           (entorno virtual)
├── src/             (código)
└── tests/           (pruebas)
```

VS Code “entiende” mejor tu código cuando:

- abres la **carpeta del proyecto** (no solo un archivo)
- seleccionas el **intérprete correcto** (el de tu `.venv`)

---

## ¿Por qué VS Code?

Porque es:

- **ligero** (comparado con IDEs pesadas)
- **modular** (extensiones)
- **cross-platform**
- muy fuerte en **Python + Jupyter + Git + Docker**

> No es la única opción. Pero es la mejor “opción por defecto” para este curso.

---

## Ejercicio rápido

::::exercise{title="Proyecto vs archivo suelto" difficulty="1"}

1. Crea una carpeta:

```bash
mkdir -p ~/prueba-ide && cd ~/prueba-ide
```

2. Crea un archivo `hola.py`:

```python
print("hola")
```

3. Abre la carpeta en VS Code (lo veremos en la siguiente sección) y contesta:

- ¿Qué aparece en el panel del explorador cuando abres una **carpeta** vs solo un archivo?
- ¿Dónde ves el “Python interpreter” seleccionado?

::::

