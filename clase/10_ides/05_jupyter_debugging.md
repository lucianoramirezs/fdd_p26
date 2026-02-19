# Jupyter notebooks, tabs y flujo de trabajo

VS Code puede ser:

- **IDE** (scripts + debugging + tests)
- **Notebook environment** (exploración interactiva)

En ciencia de datos vas a usar ambas formas.

## 1) ¿Qué es un notebook?

Un notebook (`.ipynb`) es un documento con:

- celdas de **código**
- celdas de **texto** (Markdown)
- salida embebida (tablas, gráficas, prints)

Ventaja: iteras rápido.  
Riesgo: el estado se acumula y puedes engañarte (“me funcionó” pero no sabes por qué).

---

## 2) Kernels: el punto que más confunde a principiantes

Un **kernel** es el proceso de Python que ejecuta tus celdas.

Si tu notebook “no encuentra un paquete”, casi siempre es porque:

- el kernel no está usando tu `.venv`

### Setup mínimo recomendado (por proyecto)

1. Crea tu entorno:

```bash
uv venv
source .venv/bin/activate
uv pip install ipykernel
```

2. Abre VS Code, abre el `.ipynb`.
3. Arriba a la derecha selecciona el kernel:
   - debe apuntar a `.venv`

### Debugging rápido: ¿qué Python corre el notebook?

En una celda:

```python
import sys
print(sys.executable)
```

Si no apunta a tu proyecto, cambia el kernel.

---

## 3) Notebook vs Script (cuándo usar cada uno)

| Necesitas… | Usa… | Por qué |
|------------|------|---------|
| explorar datos, prototipar | notebook | feedback inmediato |
| reproducibilidad, CI, producción | script/módulo | menos estado oculto |
| compartir resultados con narrativa | notebook | texto + código + output juntos |
| testear y mantener | script + tests | escalable |

Regla práctica:

- Explora en notebook
- **“Productiviza”** moviendo funciones a `.py`
- Deja el notebook como reporte/experimento, no como sistema

---

## 4) Debugging en notebooks (sí se puede)

En VS Code puedes:

- poner breakpoints dentro de una celda
- usar “Debug Cell”

Cuando algo se pone raro:

- **Restart Kernel**
- vuelve a correr “Run All” desde arriba

Eso te revela dependencias de estado oculto (la causa #1 de notebooks “no reproducibles”).

---

## 5) Tabs y organización del editor (tips de supervivencia)

### Preview tab vs pinned

VS Code a veces abre archivos en modo “preview” (no fijo). Si abres otro archivo, lo reemplaza.

Soluciones:

- haz doble click al tab para fijarlo
- o desactiva preview en settings (“Workbench: Editor: Enable Preview”)

### Split editor

Cuando comparas notebook + script:

- split (`Ctrl+\` / `Cmd+\`)
- notebook de un lado, `.py` del otro

---

::::exercise{title="Notebook reproducible (sin estado oculto)" difficulty="2"}

1. Crea un proyecto y un venv:

```bash
mkdir -p ~/nb-repro && cd ~/nb-repro
uv venv
source .venv/bin/activate
uv pip install ipykernel pandas
```

2. En VS Code crea `exploracion.ipynb`.
3. En la primera celda imprime el ejecutable:

```python
import sys
print(sys.executable)
```

4. Crea 3 celdas donde:
   - importas `pandas`
   - defines una variable `df`
   - haces una operación sobre `df`

5. Ahora: Kernel → Restart, y corre “Run All”.

Si algo falla, arregla el orden de celdas hasta que “Run All” funcione siempre.

::::

