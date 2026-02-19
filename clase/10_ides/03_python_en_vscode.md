# Python en VS Code (entornos, ejecutar y debuggear)

La pregunta #1 cuando “no funciona” en Python es:

> **¿Qué Python estoy ejecutando y con qué dependencias?**

VS Code puede ayudarte mucho, pero solo si configuras bien el intérprete.

## 1) Entorno virtual por proyecto (regla de oro)

En este curso, la convención más práctica es:

- un proyecto = una carpeta
- dentro de esa carpeta: un entorno virtual `.venv/` (o `venv/`)

Ejemplo:

```
mi-proyecto/
├── .venv/
├── pyproject.toml  (o requirements.txt)
└── src/
```

### Crear `.venv` (dos opciones)

**Opción A: uv (recomendado en este curso)**

```bash
cd mi-proyecto
uv venv
source .venv/bin/activate
uv pip install requests
```

**Opción B: venv estándar**

```bash
cd mi-proyecto
python3 -m venv .venv
source .venv/bin/activate
python -m pip install requests
```

Si esto todavía te suena raro, repasa la sección de entornos virtuales en [Python](../09_python/01_introduccion.md).

---

## 2) Seleccionar el intérprete correcto en VS Code

Con la extensión de Python instalada, VS Code debe detectar tu `.venv`.

Pasos típicos:

1. Abre **la carpeta** del proyecto en VS Code.
2. Abre Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`).
3. Busca: **“Python: Select Interpreter”**.
4. Elige el Python que vive en tu proyecto:
   - algo como `.../mi-proyecto/.venv/bin/python`

Luego verifica en la **Status Bar** (abajo) que el intérprete seleccionado sea el correcto.

### Debugging esencial: comprobar el Python real

En la terminal integrada (con el venv activado), corre:

```bash
which python
python -c "import sys; print(sys.executable)"
python -m pip --version
```

Eso te dice exactamente qué ejecutable y qué `pip` estás usando.

---

## 3) Formas de ejecutar Python en VS Code

### A) Terminal integrada (la forma más “real”)

```bash
python src/main.py
```

Ventajas:
- aprendes el flujo real (sirve fuera de VS Code)
- ves exactamente qué comando se ejecutó

### B) Botón “Run Python File”

Cuando abres un `.py`, VS Code ofrece “Run” arriba a la derecha.

Ventaja: rápido para principiantes.  
Riesgo: si tu intérprete está mal seleccionado, “corre” pero con otro Python.

### C) Debugger (F5)

Esto es para cuando quieres **entender** un bug, no solo “probar cosas”.

---

## 4) Debugging en 5 minutos (breakpoints + variables)

### Cómo funciona

1. Pon un breakpoint (clic a la izquierda del número de línea).
2. Abre el panel “Run and Debug”.
3. Presiona **F5**.
4. Cuando se detenga, observa:
   - **Variables**
   - **Call Stack**
   - **Watch**

Atajos típicos:

| Acción | Shortcut |
|-------|----------|
| Continuar | `F5` |
| Step Over | `F10` |
| Step Into | `F11` |
| Step Out | `Shift+F11` |
| Stop | `Shift+F5` |

### `launch.json` mínimo (cuando lo necesites)

VS Code puede generar un archivo `.vscode/launch.json`. Un ejemplo básico:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: archivo actual",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

> Si todavía no entiendes `launch.json`, no pasa nada. Empieza debuggeando “archivo actual” y vuelve a esto cuando quieras correr scripts con argumentos o con variables de entorno.

---

## 5) Errores típicos (y cómo reconocerlos rápido)

### “ModuleNotFoundError”

Significa: instalaste el paquete en **otro entorno**.

Checklist:
- ¿Está activado el venv en la terminal?
- ¿El intérprete de VS Code apunta a `.venv/bin/python`?
- ¿`python -m pip list` muestra el paquete?

### “I pressed run and nothing happens”

En scripts, las expresiones no imprimen solas (a diferencia del REPL).

---

::::prompt{title="Mi VS Code usa el Python incorrecto" for="ChatGPT/Claude"}

Estoy en Linux/macOS/Windows(WSL2) y VS Code no está usando el intérprete correcto.

Mi estructura de proyecto es:
```
[pega el resultado de: ls -la]
```

En VS Code seleccioné este intérprete:
[pega el path que aparece en la Status Bar o en Select Interpreter]

En la terminal integrada ejecuté:
```
which python
python -c "import sys; print(sys.executable)"
python -m pip --version
python -c "import pkgutil; print('requests' in [m.name for m in pkgutil.iter_modules()])"
```

Estoy intentando correr:
```
[pega el comando o cómo lo ejecutas]
```

Y obtengo este error:
```
[pega el error completo]
```

Explícame paso a paso qué está pasando y cómo arreglarlo.

::::

