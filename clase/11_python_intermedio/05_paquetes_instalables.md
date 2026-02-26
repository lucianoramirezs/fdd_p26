# Paquetes instalables: de código a librería

Hasta ahora tu "paquete" es un directorio con `__init__.py` que solo funciona si estás en el directorio correcto. Si te mueves a otra carpeta, `import mi_paquete` truena con `ModuleNotFoundError`. Y si le mandas tu código a alguien, tiene que adivinar dónde ponerlo y qué dependencias instalar.

En esta sección lo convertimos en algo que se puede instalar con `pip install` -- un paquete real que funciona desde cualquier directorio, en cualquier máquina.

---

## 1. Por qué hacer tu paquete instalable?

Sin instalación, tu paquete solo funciona si Python lo encuentra en `sys.path`. Eso significa estar parado en el directorio correcto o manipular `PYTHONPATH` a mano. Es frágil, feo, y no escala.

Cuando tu paquete es instalable:

- **Funciona desde cualquier directorio** -- `from mi_paquete import sumar` funciona estando en `/home/ana/` o en `/tmp/experimento/`
- **Las dependencias se resuelven solas** -- `pip install mi_paquete` instala automáticamente `requests`, `pandas`, lo que tu paquete necesite
- **Otras personas pueden usarlo** -- basta compartir un comando de instalación
- **Es reproducible** -- un `pyproject.toml` describe exactamente qué necesita tu proyecto

La diferencia entre "un directorio con archivos `.py`" y "una librería real" es un archivo de configuración y un comando.

---

## 2. La estructura de un proyecto Python moderno

```
mi_proyecto/
├── pyproject.toml       <- metadata + configuracion de build (EL archivo)
├── README.md            <- descripcion para PyPI/GitHub
├── LICENSE              <- terminos legales
├── src/                 <- source layout (opcional pero recomendado)
│   └── mi_paquete/
│       ├── __init__.py
│       ├── operaciones.py
│       └── utilidades.py
└── tests/
    ├── test_operaciones.py
    └── test_utilidades.py
```

### Flat layout vs src layout

Hay dos formas de organizar tu código fuente:

**Flat layout** -- el paquete vive en la raíz del proyecto:

```
mi_proyecto/
├── pyproject.toml
├── mi_paquete/          <- directamente en la raiz
│   ├── __init__.py
│   └── operaciones.py
└── tests/
```

**Src layout** -- el paquete vive dentro de `src/`:

```
mi_proyecto/
├── pyproject.toml
├── src/
│   └── mi_paquete/      <- dentro de src/
│       ├── __init__.py
│       └── operaciones.py
└── tests/
```

La diferencia es sutil pero importante: con flat layout, si estás en la raíz del proyecto, Python puede importar tu paquete **sin instalarlo** (porque `''` está en `sys.path`). Eso suena conveniente, pero significa que podrías estar testeando el código local en vez del paquete instalado, y no te darías cuenta.

Con src layout, **tienes que instalar** el paquete para poder importarlo. Eso te garantiza que tus tests prueban lo que el usuario final va a recibir.

**Recomendación**: src layout para librerías que alguien más va a instalar, flat layout para proyectos pequeños y scripts internos.

---

## 3. `pyproject.toml`: el archivo definitivo

`pyproject.toml` es el estándar moderno para configurar proyectos de Python. Reemplaza a `setup.py`, `setup.cfg`, y hasta parte de `requirements.txt`. Un solo archivo para todo.

Está definido por tres PEPs importantes:

- **PEP 517/518**: definen el sistema de build
- **PEP 621**: define los metadatos del proyecto (nombre, versión, dependencias...)

El formato es TOML (Tom's Obvious Minimal Language) -- como un INI con tipos de datos.

### Configuración mínima

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "mi-paquete"
version = "0.1.0"
description = "Una libreria para hacer X"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

authors = [
    {name = "Tu Nombre", email = "tu@email.com"},
]

dependencies = [
    "requests>=2.28",
    "pandas>=1.5",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
]
```

### Cada campo explicado

**`[build-system]`** -- le dice a pip cómo construir tu paquete. `setuptools` es el backend más común, pero hay otros como `hatchling`, `flit`, `pdm`. Para empezar, `setuptools` funciona perfecto.

**`name`** -- el nombre de tu paquete en PyPI. Usa **guiones** (`mi-paquete`), no guiones bajos. PyPI normaliza guiones y guiones bajos como equivalentes, pero por convención se usan guiones en el nombre del proyecto y guiones bajos en el nombre del directorio Python (`mi_paquete/`).

**`version`** -- versionado semántico (lo explicamos abajo).

**`description`** -- una línea que describe tu paquete. Aparece en los resultados de búsqueda de PyPI.

**`requires-python`** -- versión mínima de Python. Si alguien con Python 3.9 intenta instalar un paquete que requiere `>=3.10`, pip le dice que no se puede.

**`dependencies`** -- lo que tu paquete **necesita** para funcionar. pip las instala automáticamente.

**`[project.optional-dependencies]`** -- grupos de dependencias opcionales. El grupo `dev` es para herramientas de desarrollo que no necesita el usuario final.

### Semantic versioning (semver)

```
MAJOR.MINOR.PATCH
  1  .  2  .  3
```

- **PATCH** (`1.0.0` -> `1.0.1`): correcciones de bugs. El código existente sigue funcionando exactamente igual.
- **MINOR** (`1.0.0` -> `1.1.0`): funcionalidad nueva, compatible hacia atrás. Todo lo que funcionaba antes sigue funcionando.
- **MAJOR** (`1.0.0` -> `2.0.0`): cambios que **rompen** compatibilidad. Funciones renombradas, parámetros eliminados, comportamiento que cambió.

Antes de `1.0.0` (o sea `0.x.y`), la librería está "en desarrollo" y cualquier cambio puede romper cosas. Es una señal de "úsalo bajo tu propio riesgo".

Ejemplos reales:

| Versión | Qué pasó |
|---------|----------|
| `pandas 1.5.3` -> `2.0.0` | Removieron muchas funciones deprecadas. Código viejo rompió. |
| `requests 2.28.0` -> `2.31.0` | Mejoras y fixes. Todo siguió funcionando. |
| `python 3.11` -> `3.12` | Minor release: nuevas features, nada rompe. |

---

## 4. `setup.py`: el archivo clásico

Antes de `pyproject.toml`, la configuración vivía en `setup.py` -- un script de Python ejecutable:

```python
from setuptools import setup, find_packages

setup(
    name="mi-paquete",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28",
        "pandas>=1.5",
    ],
    python_requires=">=3.10",
    author="Tu Nombre",
    description="Una libreria para hacer X",
)
```

### Por qué todavía importa

- **Muchos proyectos existentes lo usan** -- si contribuyes a una librería open source, probablemente tiene `setup.py`
- **El curso de DataCamp lo enseñó** -- y está bien, porque es fundamental entenderlo
- **Algunos builds avanzados todavía lo necesitan** -- extensiones en C, generación de código

### Por qué usar `pyproject.toml` en vez de `setup.py`

| `setup.py` | `pyproject.toml` |
|------------|-----------------|
| Código Python ejecutable | Configuración declarativa |
| Puede tener bugs (es código) | No puede tener bugs lógicos (es datos) |
| Cada herramienta inventa su formato | Estándar único para todo |
| Solo sirve para setuptools | Soporta cualquier backend |

**Regla**: para proyectos nuevos, **siempre** usa `pyproject.toml`. Solo toca `setup.py` si trabajas en un proyecto que ya lo tiene.

---

## 5. Instalación en modo desarrollo

### El problema

Sin instalar, el flujo es doloroso:

```bash
cd /home/ana/mi_proyecto
python -c "from mi_paquete import sumar; print(sumar(2, 3))"  # funciona

cd /home/ana/otro_lugar
python -c "from mi_paquete import sumar; print(sumar(2, 3))"  # ModuleNotFoundError
```

### `pip install -e .`

El flag `-e` significa **editable**. En vez de copiar tu paquete a `site-packages/`, crea un enlace simbólico. Resultado:

- Tu paquete se puede importar desde **cualquier directorio**
- Los cambios en tu código fuente se reflejan **inmediatamente** (sin reinstalar)
- Las dependencias se instalan automáticamente

```bash
# Desde la raiz del proyecto (donde esta pyproject.toml):
pip install -e .

# Ahora funciona desde CUALQUIER lugar:
cd /tmp
python -c "from mi_paquete import sumar; print(sumar(2, 3))"  # 5

# Con dependencias de desarrollo:
pip install -e ".[dev]"
```

Nota las comillas en `".[dev]"` -- son necesarias en zsh (el shell por defecto en Mac y muchos Linux) porque `[` y `]` son caracteres especiales.

### Con uv (más rápido)

```bash
uv pip install -e .
uv pip install -e ".[dev]"
```

`uv` hace exactamente lo mismo que pip pero órdenes de magnitud más rápido. Si ya lo tienes instalado (lo vimos en el módulo 9), úsalo.

### El flujo de desarrollo profesional

```
1. Crear proyecto con pyproject.toml
2. pip install -e ".[dev]"
3. Escribir codigo + tests
4. Los tests importan tu paquete como lo haria un usuario
5. Repetir 3-4 hasta que este listo
```

Este es el flujo que usan los desarrolladores de pandas, requests, FastAPI, y cualquier librería seria de Python.

---

## 6. Licencias: el aspecto legal

### Por qué importa

Si publicas código sin licencia, la ley de copyright aplica por defecto: **todos los derechos reservados**. Eso significa que **nadie** puede legalmente copiar, modificar, ni distribuir tu código. Ni siquiera si está en un repositorio público de GitHub.

Una licencia es un documento legal que dice: "puedes usar mi código bajo estas condiciones".

### Licencias comunes

| Licencia | Qué permite | Restricción principal |
|----------|------------|----------------------|
| **MIT** | Todo: usar, modificar, distribuir, vender | Incluir el texto de la licencia original |
| **Apache 2.0** | Todo + protección de patentes | Incluir licencia + archivo NOTICE |
| **GPL v3** | Todo | Código derivado **debe** ser GPL también (copyleft) |
| **BSD 3-Clause** | Todo | No usar el nombre del autor para promoción |

### Qué significan en la práctica

**MIT**: "haz lo que quieras, solo no me demandes si algo sale mal". Es la licencia más permisiva y la más usada en el ecosistema Python. `requests`, `Flask`, `Django` usan MIT o BSD.

**Apache 2.0**: como MIT pero con una cláusula de patentes. Si alguien patenta algo basado en tu código, no puede demandarte. La usan `TensorFlow`, `Kubernetes`.

**GPL v3**: si alguien usa tu código en su proyecto, **su proyecto también tiene que ser GPL**. Esto es controversial -- algunos lo aman (fuerza el open source), otros lo evitan (limita el uso comercial). Linux usa GPL.

### Cuál elegir

- Para tu proyecto del curso: **MIT**. Es la más simple y la más común.
- Para software comercial: MIT o Apache 2.0.
- Si quieres forzar que todo derivado sea open source: GPL.
- Si no tienes una opinión fuerte: **MIT**.

### Cómo agregar una licencia

1. Crea un archivo `LICENSE` en la raíz del proyecto (sin extensión)
2. Copia el texto de [choosealicense.com](https://choosealicense.com)
3. Reemplaza `[year]` y `[fullname]` con tus datos
4. Agrega `license = {text = "MIT"}` a tu `pyproject.toml`

El texto de la licencia MIT completo es corto:

```
MIT License

Copyright (c) 2026 Tu Nombre

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 7. README.md: la cara de tu proyecto

El README es lo primero que la gente ve cuando llega a tu repositorio en GitHub o a tu página en PyPI. Es tu oportunidad de convencer a alguien en 10 segundos de que tu librería vale la pena.

### Qué debe incluir

1. **Qué hace** (un párrafo, máximo dos)
2. **Cómo instalar** (`pip install mi-paquete`)
3. **Ejemplo rápido** (5-10 líneas de código que muestren el uso principal)
4. **Link a documentación** (si existe)
5. **Licencia** (una línea)

### Ejemplo

```markdown
# Mi Paquete

Validador de archivos CSV con reglas configurables. Define un esquema,
apuntalo a un archivo, y obtiene un reporte detallado de errores.

## Instalacion

pip install mi-paquete

## Uso rapido

from mi_paquete import ValidadorCSV, Esquema

esquema = Esquema()
esquema.columna("nombre", tipo=str, obligatoria=True)
esquema.columna("edad", tipo=int, min=0)

reporte = ValidadorCSV("datos.csv", esquema).validar()
print(reporte.resumen())  # "2 errores en 100 filas"

## Licencia

MIT
```

### Anti-patrones

- **README vacío**: la gente asume que el proyecto está abandonado
- **README que solo dice "TODO"**: peor que vacío
- **README con 500 líneas de documentación**: para eso existe una página de docs
- **README sin ejemplo de código**: nadie quiere leer prosa para entender cómo usar tu librería

---

## 8. Dependencias: lo que tu paquete necesita

### Pinning vs ranging

Hay dos filosofías para declarar versiones de dependencias:

```toml
# Rangos flexibles (para LIBRERIAS):
dependencies = [
    "requests>=2.28",
    "pandas>=1.5,<3.0",
]

# Versiones exactas (para APLICACIONES):
dependencies = [
    "requests==2.31.0",
    "pandas==2.1.4",
]
```

**Si estás escribiendo una librería** (algo que otros importan), usa rangos. Si fijas `requests==2.31.0`, y el usuario ya tiene `requests==2.32.0` instalado, pip tiene un conflicto y no puede instalar tu paquete. Los rangos dicen "cualquier versión compatible".

**Si estás escribiendo una aplicación** (algo que se despliega y ejecuta), usa versiones exactas o un lock file. Quieres reproducibilidad total: la misma versión en tu laptop, en CI, y en producción.

### Operadores de versión

| Operador | Significado | Ejemplo | Acepta |
|----------|-------------|---------|--------|
| `>=` | Mínimo | `requests>=2.28` | 2.28, 2.31, 3.0... |
| `==` | Exacta | `requests==2.31.0` | Solo 2.31.0 |
| `~=` | Compatible | `requests~=2.28.0` | 2.28.x pero no 2.29 |
| `<` | Máximo | `pandas<3.0` | 1.x, 2.x, nunca 3.x |
| `!=` | Excluir | `numpy!=1.24.0` | Cualquiera menos 1.24.0 |

La más útil: `>=minima,<siguiente_major`. Por ejemplo, `pandas>=1.5,<3.0` dice "cualquier pandas 1.x o 2.x, pero no 3.x que podría romper cosas".

### `requirements.txt` vs `pyproject.toml`

| Aspecto | `requirements.txt` | `pyproject.toml` |
|---------|---------------------|-----------------|
| Para | Aplicaciones desplegables | Librerías y paquetes |
| Versiones | Exactas (pin) | Rangos flexibles |
| Instalar | `pip install -r requirements.txt` | `pip install .` |
| Historia | Existe desde siempre | Estándar desde ~2021 |
| Incluye metadata | No (solo dependencias) | Sí (nombre, versión, autor...) |

No son mutuamente exclusivos. Puedes tener `pyproject.toml` para tu paquete y un `requirements.txt` adicional si necesitas pinear versiones para CI o despliegue.

**Para tu librería del curso**: usa `pyproject.toml`. Punto.

---

## 9. Distribución: compartir con el mundo

### Construir el paquete

"Construir" un paquete significa generar los archivos que pip puede instalar. Son dos formatos:

```bash
pip install build
python -m build
```

Esto crea un directorio `dist/` con dos archivos:

```
dist/
├── mi_paquete-0.1.0.tar.gz        <- source distribution (sdist)
└── mi_paquete-0.1.0-py3-none-any.whl  <- wheel (bdist)
```

- **sdist** (`.tar.gz`): tu código fuente comprimido. pip lo descomprime y ejecuta el build.
- **wheel** (`.whl`): paquete pre-compilado, listo para instalar. Es más rápido porque no necesita ejecutar nada.

Cuando haces `pip install algo`, pip prefiere el wheel si existe. Si no, usa el sdist.

### Subir a PyPI (panorama general)

PyPI (Python Package Index) es el repositorio central de paquetes de Python. Es lo que pip consulta cuando haces `pip install requests`.

```bash
pip install twine
twine upload dist/*
```

Antes de subir a PyPI real, puedes probar con TestPyPI:

```bash
twine upload --repository testpypi dist/*
# Y para instalar desde TestPyPI:
pip install --index-url https://test.pypi.org/simple/ mi-paquete
```

Necesitas una cuenta en [pypi.org](https://pypi.org). Para este curso, **no necesitas subir a PyPI** -- construir el paquete es suficiente.

### Instalar desde GitHub (más práctico para el curso)

Si tu proyecto está en GitHub, cualquiera puede instalarlo directamente:

```bash
# Instalar desde un repositorio publico:
pip install git+https://github.com/usuario/mi-proyecto.git

# Una branch especifica:
pip install git+https://github.com/usuario/mi-proyecto.git@develop

# Un tag (version):
pip install git+https://github.com/usuario/mi-proyecto.git@v0.1.0
```

Esto es práctico para proyectos internos, del curso, o de trabajo. No necesitas pasar por PyPI.

---

## 10. Juntando todo: ejemplo paso a paso

Vamos a tomar un paquete simple y hacerlo instalable desde cero.

### Paso 1: la estructura

```
mi_calculadora/
├── pyproject.toml
├── LICENSE
├── README.md
├── src/
│   └── calculadora/
│       ├── __init__.py
│       ├── basica.py
│       └── estadistica.py
└── tests/
    ├── test_basica.py
    └── test_estadistica.py
```

### Paso 2: el código

```python
# src/calculadora/basica.py
def sumar(a, b):
    """Suma dos numeros."""
    return a + b

def dividir(a, b):
    """Divide a entre b.

    Raises:
        ZeroDivisionError: Si b es cero.
    """
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero")
    return a / b
```

```python
# src/calculadora/estadistica.py
def promedio(valores):
    """Calcula el promedio de una lista de numeros.

    Args:
        valores: Lista de numeros.

    Returns:
        float: El promedio.

    Raises:
        ValueError: Si la lista esta vacia.
    """
    if not valores:
        raise ValueError("La lista no puede estar vacia")
    return sum(valores) / len(valores)
```

```python
# src/calculadora/__init__.py
from .basica import sumar, dividir
from .estadistica import promedio
```

### Paso 3: `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "calculadora"
version = "0.1.0"
description = "Operaciones matematicas basicas y estadisticas"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Tu Nombre", email = "tu@itam.mx"},
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
]

[tool.setuptools.packages.find]
where = ["src"]
```

La sección `[tool.setuptools.packages.find]` le dice a setuptools que busque paquetes dentro de `src/`. Sin esto, no encontraría tu código con el src layout.

### Paso 4: instalar y verificar

```bash
# Crear un entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar en modo editable con dependencias dev
pip install -e ".[dev]"

# Verificar que funciona desde cualquier directorio
cd /tmp
python -c "from calculadora import sumar, promedio; print(sumar(2, 3)); print(promedio([1, 2, 3]))"
# 5
# 2.0

# Correr tests
cd -
pytest tests/ -v
```

---

## 11. Errores comunes

### "Mi paquete no se encuentra después de `pip install -e .`"

- Verifica que estás en el directorio que tiene `pyproject.toml`
- Si usas src layout, asegúrate de tener `[tool.setuptools.packages.find] where = ["src"]`
- Verifica que activaste el entorno virtual correcto

### "Mis tests importan el código local, no el instalado"

- Esto pasa con flat layout. Si usas src layout, no puede pasar.
- Solución: cambia a src layout, o siempre ejecuta tests después de `pip install -e .`

### "No sé qué versión poner"

- Empieza con `0.1.0`. El `0` al inicio dice "esto está en desarrollo".
- Sube el PATCH cuando arregles bugs.
- Sube el MINOR cuando agregues funcionalidad.
- Cuando consideres que es estable, lanza `1.0.0`.

### "Pongo mis tests dentro del paquete o afuera?"

- **Afuera** (en `tests/` al nivel de `pyproject.toml`). Los tests no son parte de lo que el usuario instala.
- Si los pones dentro del paquete, se instalan con `pip install` y el usuario los recibe innecesariamente.

---

## Ejercicios

:::exercise{title="pyproject.toml mínimo" difficulty="1"}

Tienes un paquete llamado `texto_utils` que depende de `unidecode>=1.3` y `regex>=2023.0`. El paquete tiene dos módulos: `limpieza.py` y `analisis.py`. Usa flat layout.

Escribe un `pyproject.toml` completo y válido que incluya:

1. Build system con setuptools
2. Nombre, versión `0.1.0`, descripción
3. `requires-python >= 3.10`
4. Las dos dependencias
5. Un grupo `dev` con `pytest` y `ruff`
6. Licencia MIT
7. Tu nombre como autor

Verifica que el TOML es válido: la indentación no importa en TOML, pero los tipos sí. Los strings van entre comillas, las listas entre corchetes.

:::

:::exercise{title="Haz tu paquete instalable" difficulty="2"}

Toma el paquete `calculadora` que creaste en el ejercicio del repaso de ingeniería (sección 01) y hazlo instalable:

1. Agrega un `pyproject.toml` con toda la metadata necesaria
2. Crea un archivo `LICENSE` con la licencia MIT
3. Escribe un `README.md` con descripción, instrucciones de instalación y un ejemplo de uso
4. Instala con `pip install -e .` en un entorno virtual
5. Abre una terminal **en un directorio diferente** y verifica que `from calculadora import sumar` funciona
6. Ejecuta tus tests con `pytest` y verifica que pasan

Si no tienes el paquete `calculadora`, créalo con al menos 3 funciones (sumar, restar, dividir) y 2 tests por función.

:::

:::exercise{title="Elige tu licencia" difficulty="1"}

Investiga las licencias MIT, Apache 2.0 y GPL v3. Responde:

1. Cuál elegirías para una librería que quieres que cualquier empresa pueda usar? Por qué?
2. Cuál elegirías si quieres que todo código derivado sea open source? Por qué?
3. Un proyecto usa GPL v3. Puedes usar una función de ese proyecto en tu librería MIT? Por qué sí o por qué no?
4. Tu librería MIT usa `requests` (Apache 2.0) y `pandas` (BSD 3-Clause) como dependencias. Hay algún conflicto de licencias?

:::

:::prompt{title="Revisa mi pyproject.toml" for="ChatGPT/Claude"}

Estoy creando un paquete de Python que [describe brevemente qué hace tu paquete]. Este es mi `pyproject.toml`:

```toml
[pega aqui tu pyproject.toml completo]
```

Y esta es la estructura de mi proyecto:

```
[pega aqui tu arbol de directorios]
```

Revisa:

1. Falta algún campo importante en la metadata?
2. Los rangos de versiones de mis dependencias son razonables? Alguno es demasiado amplio o demasiado restrictivo?
3. La configuración del build system es correcta para mi layout (flat vs src)?
4. Hay algo que me impediría hacer `pip install -e .` exitosamente?
5. Si quisiera subir a PyPI, qué me falta?

:::
