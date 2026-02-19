# Extensiones, settings y personalización

VS Code es “un core pequeño” + extensiones. Esto es poder… y también es riesgo (puedes romper tu experiencia con demasiadas cosas).

## Marketplace: qué es y cómo usarlo bien

Una extensión es un plugin que agrega capacidades: lenguaje, debugging, linters, integración con Docker, notebooks, etc.

Regla práctica:

- Instala **pocas** extensiones, pero buenas.
- Si algo se siente raro, desactiva extensiones hasta encontrar la causa.

---

## Extensiones recomendadas (para este curso)

### Esenciales

- **Python** (Microsoft): soporte base para Python, intérpretes, debugging.
- **Pylance**: autocompletado rápido y análisis (IntelliSense).
- **Jupyter**: notebooks (`.ipynb`) dentro de VS Code.
- **Ruff**: linter/formatter moderno (rápido).

### Muy útiles (especialmente con contenedores)

- **Docker**: ver imágenes/contendedores, logs, build/run desde la IDE.
- **Dev Containers**: abrir tu proyecto “dentro” de un contenedor (reproducible).

### Opcionales

- **GitLens**: mejor UI para git blame/historial.
- **EditorConfig**: coherencia de indentación/fin de línea entre editores.

> Importante: muchas extensiones se instalan “en pares”. Por ejemplo: Python + Pylance.

---

## Settings: User vs Workspace (esto te ahorra conflictos)

Hay dos niveles de configuración:

- **User Settings**: para tu máquina (te siguen en todos los proyectos).
- **Workspace Settings**: para un proyecto (vive con el repo y se aplica solo ahí).

Regla práctica:

- Lo personal (theme, font) → **User**
- Lo reproducible (formatter, lint rules) → **Workspace**

---

## Personalización esencial (para leer mejor y cansarte menos)

### Theme y colores

- Command Palette → “Preferences: Color Theme”
- Command Palette → “Preferences: File Icon Theme”

El mejor theme es el que te deja leer 2 horas sin dolor.

### Tipografía y tamaño

Busca en Settings:

- “Font Size” (editor)
- “Font Family”
- “Terminal Font Size”

> Nota: si tu texto se ve “apretado”, sube el line height: “Editor: Line Height”.

---

## Terminal integrada: ajustes útiles

Busca:

- “Terminal: Integrated: Default Profile”
- “Terminal: Integrated: Scrollback” (más historial)
- “Terminal: Integrated: Font Size”

La terminal es tu puente con el mundo real (módulo 4). VS Code solo te la pone más cerca.

---

## Un `settings.json` mínimo para Python (ejemplo)

Este ejemplo asume que tu entorno vive en `.venv/` en la raíz del proyecto.

Archivo: `.vscode/settings.json` (workspace)

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": "explicit"
  },
  "ruff.enable": true
}
```

Notas:

- Si estás en Windows nativo (no WSL), tu path a `.venv` cambia (`.venv\\Scripts\\python.exe`).
- En WSL/Linux/macOS, el path típico es `.venv/bin/python`.

---

## Atajos: personaliza solo si ya dominas lo básico

Command Palette → “Preferences: Keyboard Shortcuts”

Te deja:

- buscar un comando
- ver su shortcut
- reasignarlo

No empieces por aquí. Primero aprende 10 atajos y ya.

---

::::exercise{title="Setup mínimo: Python + Ruff + Jupyter + Docker" difficulty="2"}

1. Instala las extensiones: Python, Pylance, Jupyter, Ruff, Docker, Dev Containers.
2. Reinicia VS Code (sí, a veces ayuda).
3. Abre un proyecto Python con `.venv/`.
4. Verifica:
   - VS Code detecta tu intérprete `.venv`
   - Puedes abrir un `.ipynb`
   - Puedes abrir la vista de Docker (aunque no tengas contenedores corriendo)

Si algo falla, anota:
- qué extensión no funciona
- qué error aparece en “Problems” o “Output”

::::

