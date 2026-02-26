# Repaso: Paquetes, módulos e imports

> **Notebook interactivo**: todo el código de esta sección está en un notebook ejecutable.
> [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/11_python_intermedio/code/01_repaso_ingenieria.ipynb)

Esto es un repaso **profundo**. Ya viste los conceptos básicos en el curso de DataCamp. Aquí los consolidamos con el detalle que vas a necesitar para construir tu propia librería. Si algo ya lo dominas, avanza rápido. Si algo no te queda claro, este es el momento de resolverlo -- porque todo lo que sigue depende de estos fundamentos.

---

## 1. Módulos: archivos .py

Un módulo es simplemente un archivo `.py`. Eso es todo. Cualquier archivo Python que escribas es un módulo que otros archivos pueden importar.

```python
# operaciones.py  <-- esto ES un módulo
def sumar(a, b):
    return a + b

def restar(a, b):
    return a - b
```

Cuando escribes `import operaciones`, Python busca un archivo `operaciones.py` (o un paquete `operaciones/`) y lo ejecuta. Sí, **lo ejecuta completo** -- todo el código a nivel de módulo corre en el momento del import.

### Los módulos son objetos

En Python todo es un objeto, y los módulos no son la excepción. Cuando importas un módulo, obtienes un objeto con atributos que puedes inspeccionar:

```python
import operaciones

# ¿Qué tipo tiene?
type(operaciones)              # <class 'module'>

# ¿Dónde vive en el disco?
print(operaciones.__file__)    # /ruta/a/operaciones.py

# ¿Cómo se llama?
print(operaciones.__name__)    # operaciones

# ¿Qué tiene adentro?
dir(operaciones)               # ['__builtins__', '__doc__', ..., 'restar', 'sumar']
```

`dir()` es tu mejor amigo para explorar. Te lista todos los atributos y métodos disponibles. Combinado con `help()`, puedes entender cualquier módulo sin leer documentación externa:

```python
help(operaciones.sumar)
# Help on function sumar in module operaciones:
# sumar(a, b)
```

### Formas de importar

Hay varias formas, y cada una tiene su lugar:

```python
# 1. Importar el módulo completo
import operaciones
operaciones.sumar(2, 3)        # necesitas el prefijo

# 2. Importar funciones específicas
from operaciones import sumar, restar
sumar(2, 3)                    # sin prefijo

# 3. Importar con alias
import operaciones as ops
ops.sumar(2, 3)

# 4. Importar todo (EVITAR en producción)
from operaciones import *
sumar(2, 3)                    # funciona pero no sabes de dónde vino
```

**La forma 1 es la más segura.** Deja claro de dónde viene cada función. La forma 4 es peligrosa en código real porque contamina tu namespace -- si dos módulos exportan una función con el mismo nombre, la segunda sobreescribe la primera sin ningún warning.

La forma 2 es útil cuando usas pocas funciones frecuentemente. La forma 3 es el estándar para librerías de datos: `import pandas as pd`, `import numpy as np`.

---

## 2. ¿Cómo Python encuentra los módulos? (`sys.path`)

Cuando escribes `import algo`, Python no busca en todo tu disco duro. Busca en una lista específica de directorios, **en orden**:

```python
import sys
for ruta in sys.path:
    print(ruta)
```

El output se ve algo así:

```
/home/usuario/mi_proyecto        ← directorio del script que ejecutaste
/usr/lib/python3.12              ← librería estándar
/usr/lib/python3.12/lib-dynload  ← extensiones en C
/home/usuario/.local/lib/python3.12/site-packages  ← paquetes instalados con pip
```

### El orden de búsqueda importa

Python busca en este orden y se detiene en la **primera coincidencia**:

1. **El directorio actual** (o el directorio del script)
2. **La librería estándar** (`math`, `os`, `json`, etc.)
3. **site-packages** (paquetes instalados con `pip`)

Esto tiene una consecuencia directa que debes recordar:

```python
# Si creas un archivo llamado random.py en tu directorio...
# random.py
def choice(lista):
    return lista[0]  # "implementación" terrible

# ...y luego en otro archivo haces:
import random
random.choice([1, 2, 3])  # ¡llama TU random.py, no el de la stdlib!
```

**Nunca nombres tus archivos como módulos de la librería estándar.** Nombres prohibidos incluyen: `random.py`, `math.py`, `os.py`, `json.py`, `csv.py`, `email.py`, `test.py`, `string.py`, `calendar.py`. Si estás debuggeando un import que "no jala", revisa si tienes un archivo con nombre conflictivo.

### PYTHONPATH

Puedes agregar directorios al path de búsqueda con la variable de entorno `PYTHONPATH`:

```bash
export PYTHONPATH="/home/usuario/mis_librerias:$PYTHONPATH"
python3 mi_script.py
```

Esto inserta `/home/usuario/mis_librerias` al inicio de `sys.path`. Es útil para desarrollo, pero en producción es mejor instalar tus paquetes correctamente con `pip install -e .` (lo veremos después).

También puedes modificar `sys.path` directamente en tu código, aunque rara vez deberías necesitarlo:

```python
import sys
sys.path.insert(0, "/ruta/a/mis/modulos")
```

---

## 3. Paquetes: directorios con `__init__.py`

Un módulo es un archivo. Un **paquete** es un directorio que contiene módulos. La diferencia clave: el directorio necesita un archivo `__init__.py` para que Python lo reconozca como paquete.

```
mi_paquete/
├── __init__.py       ← hace que el directorio sea un paquete
├── operaciones.py    ← módulo
└── utilidades.py     ← módulo
```

Sin el `__init__.py`, Python no reconoce el directorio como paquete importable. Es como una puerta sin manija -- el contenido está ahí pero no puedes acceder.

> **Nota técnica**: desde Python 3.3 existen los "namespace packages" que no requieren `__init__.py`. En la práctica, **siempre crea `__init__.py`**. Es más explícito, más compatible, y te da control sobre qué se exporta. Los namespace packages resuelven un problema muy específico que probablemente no tienes.

### `__init__.py`: la puerta de entrada

`__init__.py` se ejecuta automáticamente cuando alguien hace `import mi_paquete`. Su trabajo principal es **definir la interfaz pública** del paquete -- qué ve el usuario cuando importa tu paquete.

Supongamos esta estructura:

```python
# mi_paquete/operaciones.py
def sumar(a, b):
    """Suma dos números."""
    return a + b

def restar(a, b):
    """Resta b de a."""
    return a - b
```

```python
# mi_paquete/utilidades.py
def formatear(resultado, decimales=2):
    """Formatea un número con N decimales."""
    return f"{resultado:.{decimales}f}"
```

**Sin nada en `__init__.py`**, el usuario tiene que escribir rutas largas:

```python
from mi_paquete.operaciones import sumar
from mi_paquete.utilidades import formatear
```

**Con imports en `__init__.py`**, el usuario accede directo:

```python
# mi_paquete/__init__.py
from .operaciones import sumar, restar
from .utilidades import formatear
```

```python
# ahora el usuario puede hacer:
from mi_paquete import sumar, formatear

resultado = sumar(3.14159, 2.71828)
print(formatear(resultado))  # "5.86"
```

El punto en `.operaciones` es un **import relativo** -- significa "el módulo `operaciones` que está dentro de este mismo paquete". Más sobre esto abajo.

### Absolute vs relative imports

Dentro de un paquete puedes importar de dos formas:

```python
# mi_paquete/__init__.py

# ABSOLUTO: usa la ruta completa desde la raíz
from mi_paquete.operaciones import sumar

# RELATIVO: usa punto(s) para referirse al paquete actual
from .operaciones import sumar
```

Ambos funcionan. ¿Cuándo usar cuál?

| Tipo | Sintaxis | Ventaja | Desventaja |
|------|----------|---------|------------|
| Absoluto | `from mi_paquete.modulo import func` | Explícito, fácil de leer | Si renombras el paquete, cambias todos los imports |
| Relativo | `from .modulo import func` | Se adapta si renombras el paquete | Puede ser confuso en paquetes profundos |

**Mi recomendación**: usa imports **relativos dentro** del paquete (en `__init__.py` y entre módulos del mismo paquete) e imports **absolutos fuera** del paquete (en scripts que usan tu paquete). Es la convención más común en proyectos profesionales.

```python
# Dentro de mi_paquete/  →  relativo
from .operaciones import sumar      # ← punto = mismo paquete
from .utilidades import formatear

# Fuera de mi_paquete/  →  absoluto
from mi_paquete import sumar        # ← ruta completa
```

### Sub-paquetes (paquetes anidados)

Los paquetes pueden contener otros paquetes. Cada subdirectorio necesita su propio `__init__.py`:

```
mi_paquete/
├── __init__.py
├── operaciones.py
├── utilidades.py
└── io/                        ← sub-paquete
    ├── __init__.py
    ├── lectura.py
    └── escritura.py
```

```python
# mi_paquete/io/__init__.py
from .lectura import leer_csv, leer_json
from .escritura import escribir_csv
```

```python
# mi_paquete/__init__.py
from .operaciones import sumar, restar
from .utilidades import formatear
from . import io               # expone el sub-paquete
```

Ahora el usuario puede acceder a las cosas de varias formas:

```python
# Acceso directo a funciones del nivel superior
from mi_paquete import sumar

# Acceso al sub-paquete
from mi_paquete.io import leer_csv

# O importar el sub-paquete completo
from mi_paquete import io
datos = io.leer_csv("datos.csv")
```

La notación con `..` (dos puntos) permite imports relativos al paquete padre:

```python
# mi_paquete/io/lectura.py
from ..utilidades import formatear   # ← sube un nivel, luego busca utilidades
```

**Regla práctica**: si necesitas más de dos puntos (`...`), tu paquete probablemente está demasiado anidado. Reestructura.

---

## 4. `__all__`: controlando qué se exporta

Cuando alguien escribe `from mi_paquete import *`, ¿qué se importa exactamente? La variable `__all__` lo controla:

```python
# mi_paquete/__init__.py
from .operaciones import sumar, restar, _validar_numeros
from .utilidades import formatear

__all__ = ["sumar", "restar", "formatear"]
```

`__all__` es una lista de strings con los nombres que se exportan con `*`. En este ejemplo, `_validar_numeros` **no** se exporta porque no está en la lista.

### ¿Qué pasa sin `__all__`?

Sin `__all__`, `from modulo import *` importa **todo lo que no empiece con `_`**. Esto puede ser problemático:

```python
# mi_modulo.py (sin __all__)
import os                # ← esto TAMBIÉN se exportaría con *
import sys               # ← y esto también

def sumar(a, b):
    return a + b

def _helper_interno():
    pass
```

Si alguien hace `from mi_modulo import *`, obtiene `os`, `sys` y `sumar`. No quieres exportar `os` y `sys` -- no son parte de tu API. Con `__all__`, eso se soluciona:

```python
# mi_modulo.py (con __all__)
import os
import sys

__all__ = ["sumar"]

def sumar(a, b):
    return a + b
```

### Buenas prácticas con `__all__`

1. **Siempre define `__all__` en `__init__.py`**. Es documentación explícita de tu API pública.
2. **Mantenlo actualizado**. Si agregas una función pública, agrégala a `__all__`.
3. **Úsalo en módulos grandes** que importan cosas de otros módulos.
4. **No lo necesitas en módulos pequeños** donde todo lo que definiste es la API pública.

```python
# mi_paquete/__init__.py
from .operaciones import sumar, restar
from .utilidades import formatear

__all__ = [
    "sumar",
    "restar",
    "formatear",
]
```

Piensa en `__all__` como el menú de un restaurante. El chef sabe hacer muchas cosas, pero el menú solo muestra lo que quiere que el cliente pida.

---

## 5. `if __name__ == "__main__":`

Este es uno de los patrones más importantes de Python y aparece en prácticamente todo proyecto serio.

### ¿Qué es `__name__`?

Cada módulo tiene una variable especial `__name__` que Python asigna automáticamente:

- Cuando **ejecutas** el archivo directamente (`python3 mi_modulo.py`): `__name__` vale `"__main__"`
- Cuando **importas** el archivo (`import mi_modulo`): `__name__` vale `"mi_modulo"`

```python
# prueba.py
print(f"Mi __name__ es: {__name__}")
```

```bash
$ python3 prueba.py
Mi __name__ es: __main__
```

```python
>>> import prueba
Mi __name__ es: prueba
```

### El patrón

Esto te permite que un archivo funcione **tanto como script** (ejecutable) **como módulo** (importable):

```python
# convertidor.py

def celsius_a_fahrenheit(celsius):
    """Convierte grados Celsius a Fahrenheit."""
    return celsius * 9/5 + 32

def fahrenheit_a_celsius(fahrenheit):
    """Convierte grados Fahrenheit a Celsius."""
    return (fahrenheit - 32) * 5/9


if __name__ == "__main__":
    # Este bloque SOLO se ejecuta si corres:  python3 convertidor.py
    # NO se ejecuta si haces:  import convertidor

    print("=== Convertidor de temperatura ===")
    print(f"  0°C = {celsius_a_fahrenheit(0):.1f}°F")
    print(f" 20°C = {celsius_a_fahrenheit(20):.1f}°F")
    print(f"100°C = {celsius_a_fahrenheit(100):.1f}°F")
    print(f" 72°F = {fahrenheit_a_celsius(72):.1f}°C")
```

```bash
# Como script: ejecuta el bloque __main__
$ python3 convertidor.py
=== Convertidor de temperatura ===
  0°C = 32.0°F
 20°C = 68.0°F
100°C = 212.0°F
 72°F = 22.2°C
```

```python
# Como módulo: NO ejecuta el bloque __main__
>>> from convertidor import celsius_a_fahrenheit
>>> celsius_a_fahrenheit(37)
98.6
```

### ¿Por qué importa?

Sin el guard `if __name__ == "__main__":`, todo el código a nivel de módulo se ejecuta al importar. Eso significa que si tienes `print()` o demos en tu archivo, se ejecutan cada vez que alguien importa tu módulo -- lo cual es molesto y puede tener efectos secundarios no deseados.

```python
# MAL -- el print se ejecuta al importar
def sumar(a, b):
    return a + b

print("Probando sumar:", sumar(2, 3))  # ← se imprime al hacer import

# BIEN -- el print solo corre si ejecutas el archivo directamente
def sumar(a, b):
    return a + b

if __name__ == "__main__":
    print("Probando sumar:", sumar(2, 3))
```

### Usos comunes del bloque `__main__`

- **Demos**: mostrar cómo se usa el módulo
- **Tests rápidos**: verificar que las funciones básicas funcionan
- **CLI**: convertir el módulo en herramienta de línea de comandos

```python
# analizador.py
import sys

def contar_lineas(ruta):
    """Cuenta las líneas de un archivo."""
    with open(ruta) as f:
        return sum(1 for _ in f)

def contar_palabras(ruta):
    """Cuenta las palabras de un archivo."""
    with open(ruta) as f:
        return sum(len(linea.split()) for linea in f)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 analizador.py <archivo>")
        sys.exit(1)

    archivo = sys.argv[1]
    print(f"Líneas:  {contar_lineas(archivo)}")
    print(f"Palabras: {contar_palabras(archivo)}")
```

```bash
$ python3 analizador.py mi_archivo.txt
Líneas:  42
Palabras: 318
```

---

## 6. La librería estándar: lo que Python trae gratis

Python tiene una de las librerías estándar más completas de cualquier lenguaje. Antes de buscar un paquete externo, revisa si la stdlib ya resuelve tu problema. Aquí van los módulos que más vas a usar en ciencia de datos y desarrollo general.

### `pathlib` -- rutas de archivos modernas

`pathlib` reemplaza al viejo `os.path`. En vez de manipular strings, trabajas con objetos `Path` que entienden el sistema de archivos:

```python
from pathlib import Path

# Crear rutas
proyecto = Path("/home/usuario/mi_proyecto")
datos = proyecto / "datos" / "ventas.csv"  # el operador / une rutas

# Inspeccionar
print(datos.name)        # ventas.csv
print(datos.stem)        # ventas
print(datos.suffix)      # .csv
print(datos.parent)      # /home/usuario/mi_proyecto/datos
print(datos.exists())    # True o False

# Leer y escribir
contenido = datos.read_text(encoding="utf-8")
datos.write_text("nuevo contenido", encoding="utf-8")

# Buscar archivos
for csv in proyecto.glob("**/*.csv"):       # recursivo
    print(csv)

for py in proyecto.glob("*.py"):            # solo en el directorio actual
    print(py)

# Crear directorios
(proyecto / "resultados").mkdir(exist_ok=True)   # no falla si ya existe
```

**¿Por qué es mejor que `os.path`?** Compara:

```python
# os.path -- manipulación de strings, feo y propenso a errores
import os
ruta = os.path.join("/home", "usuario", "datos", "archivo.csv")
nombre = os.path.basename(ruta)
existe = os.path.exists(ruta)

# pathlib -- objetos, limpio y legible
from pathlib import Path
ruta = Path("/home") / "usuario" / "datos" / "archivo.csv"
nombre = ruta.name
existe = ruta.exists()
```

Usa `pathlib` para todo lo que tenga que ver con archivos y directorios. No hay razón para usar `os.path` en código nuevo.

### `collections` -- estructuras de datos especializadas

La librería estándar tiene varias estructuras de datos que resuelven problemas comunes de forma eficiente:

#### `Counter` -- contar cosas

```python
from collections import Counter

palabras = ["hola", "mundo", "hola", "python", "mundo", "hola"]
conteo = Counter(palabras)

print(conteo)                   # Counter({'hola': 3, 'mundo': 2, 'python': 1})
print(conteo["hola"])           # 3
print(conteo.most_common(2))    # [('hola', 3), ('mundo', 2)]

# Funciona con cualquier iterable
letras = Counter("abracadabra")
print(letras)                   # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
```

Sin `Counter`, tendrías que escribir un loop con un diccionario. `Counter` lo hace en una línea.

#### `defaultdict` -- dict con valor por defecto

```python
from collections import defaultdict

# Agrupar elementos por categoría
estudiantes = [
    ("Actuaría", "Ana"),
    ("Economía", "Luis"),
    ("Actuaría", "María"),
    ("Economía", "Carlos"),
]

por_carrera = defaultdict(list)  # si la clave no existe, crea una lista vacía
for carrera, nombre in estudiantes:
    por_carrera[carrera].append(nombre)

print(dict(por_carrera))
# {'Actuaría': ['Ana', 'María'], 'Economía': ['Luis', 'Carlos']}
```

Sin `defaultdict`, necesitas verificar si la clave existe antes de operar:

```python
# Sin defaultdict (más código, más feo)
por_carrera = {}
for carrera, nombre in estudiantes:
    if carrera not in por_carrera:
        por_carrera[carrera] = []
    por_carrera[carrera].append(nombre)
```

#### `namedtuple` -- clases ligeras

Cuando necesitas agrupar datos pero no justifica una clase completa:

```python
from collections import namedtuple

Punto = namedtuple("Punto", ["x", "y"])
p = Punto(3, 4)
print(p.x, p.y)        # 3 4
print(p)                # Punto(x=3, y=4)

# Es inmutable (como una tupla)
# p.x = 5              # AttributeError
```

En código nuevo, considera usar `dataclasses` en vez de `namedtuple` -- son más flexibles. Pero `namedtuple` sigue siendo útil para datos inmutables simples.

### `itertools` -- iteradores eficientes

`itertools` genera secuencias sin materializar listas completas en memoria. Es esencial cuando trabajas con datos grandes:

```python
from itertools import chain, product, combinations, groupby

# chain: concatenar iterables sin crear una lista nueva
lista1 = [1, 2, 3]
lista2 = [4, 5, 6]
for item in chain(lista1, lista2):
    print(item)  # 1, 2, 3, 4, 5, 6

# product: producto cartesiano
colores = ["rojo", "azul"]
tallas = ["S", "M", "L"]
for color, talla in product(colores, tallas):
    print(f"{color}-{talla}")
# rojo-S, rojo-M, rojo-L, azul-S, azul-M, azul-L

# combinations: todas las combinaciones posibles
equipos = ["A", "B", "C", "D"]
for partido in combinations(equipos, 2):
    print(partido)
# ('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'C'), ('B', 'D'), ('C', 'D')
```

**¿Cuándo usar `itertools`?** Cuando tienes datasets grandes y no quieres materializar todo en memoria. `chain` no crea una nueva lista -- simplemente itera por las existentes una tras otra. Si tienes dos listas de un millón de elementos, `chain` usa prácticamente cero memoria extra, mientras que `lista1 + lista2` crea una nueva lista de dos millones de elementos.

### `functools` -- herramientas para funciones

#### `lru_cache` -- memoización automática

Cachea los resultados de una función para que no recalcule con los mismos argumentos:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    """Calcula el n-ésimo número de Fibonacci."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Sin cache: fibonacci(100) tardaría siglos (exponencial)
# Con cache: fibonacci(100) es instantáneo (lineal)
print(fibonacci(100))  # 354224848179261915075
```

`lru_cache` funciona con funciones que reciben argumentos hashables (números, strings, tuplas). No funciona con listas o diccionarios como argumentos.

#### `partial` -- pre-llenar argumentos

```python
from functools import partial

def potencia(base, exponente):
    return base ** exponente

cuadrado = partial(potencia, exponente=2)
cubo = partial(potencia, exponente=3)

print(cuadrado(5))   # 25
print(cubo(3))       # 27
```

`partial` crea una nueva función con algunos argumentos ya fijados. Es útil cuando necesitas pasar una función como argumento pero con ciertos parámetros predefinidos.

### `json`, `csv`, `datetime`

Tres módulos que usas constantemente en ciencia de datos:

```python
# json -- serialización de datos
import json

datos = {"nombre": "Ana", "edad": 25, "cursos": ["FDD", "Estadística"]}
texto_json = json.dumps(datos, indent=2, ensure_ascii=False)  # dict → string
datos_de_vuelta = json.loads(texto_json)                       # string → dict

# Leer/escribir archivos JSON
with open("datos.json", "w") as f:
    json.dump(datos, f, indent=2)

with open("datos.json") as f:
    datos = json.load(f)
```

```python
# csv -- archivos CSV sin pandas
import csv

with open("datos.csv") as f:
    lector = csv.DictReader(f)      # cada fila es un diccionario
    for fila in lector:
        print(fila["nombre"], fila["edad"])

with open("salida.csv", "w", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=["nombre", "edad"])
    escritor.writeheader()
    escritor.writerow({"nombre": "Ana", "edad": 25})
```

```python
# datetime -- fechas y tiempos
from datetime import datetime, date, timedelta

hoy = date.today()
print(hoy)                                  # 2026-02-24

ahora = datetime.now()
print(ahora.strftime("%Y-%m-%d %H:%M"))     # 2026-02-24 14:30

manana = hoy + timedelta(days=1)
hace_una_semana = hoy - timedelta(weeks=1)

fecha = datetime.strptime("2026-03-15", "%Y-%m-%d")  # string → datetime
```

### ¿Cuándo usar stdlib vs paquetes externos?

**Regla general**: si la librería estándar resuelve tu problema razonablemente bien, úsala. Menos dependencias = vida más simple.

| Stdlib | Externo | ¿Por qué? |
|--------|---------|-----------|
| `csv` | `pandas` | pandas es mejor para análisis, csv para lectura simple |
| `urllib` | `requests` | requests es **mucho** más fácil de usar |
| `json` | `orjson` | json funciona bien, orjson solo si necesitas velocidad |
| `logging` | `loguru` | logging es verbose pero funcional |
| `pathlib` | -- | pathlib es excelente, no necesitas nada más |
| `collections` | -- | Counter, defaultdict son perfectos |
| `unittest` | `pytest` | pytest es mejor en todo sentido |

La decisión no es absoluta. `requests` es tan superior a `urllib` que nadie usa `urllib` por gusto. Pero `pathlib` es tan bueno que no necesitas alternativa. Evalúa caso por caso.

---

## 7. Manejo de errores

Los errores van a pasar. Tu código va a recibir datos inesperados, archivos que no existen, APIs que fallan. La pregunta no es "si" sino "cuándo". El manejo de errores no es un extra -- es parte fundamental de escribir software que funciona en el mundo real.

### `try` / `except` / `else` / `finally`

La estructura completa tiene cuatro bloques. No todos son obligatorios:

```python
try:
    # Código que PUEDE fallar
    resultado = dividir(a, b)

except ZeroDivisionError:
    # Se ejecuta SOLO si ocurre esta excepción específica
    print("No se puede dividir por cero")

except (TypeError, ValueError) as e:
    # Puedes agrupar excepciones y capturar el objeto de error
    print(f"Error de entrada: {e}")

else:
    # Se ejecuta SOLO si NO hubo excepción
    print(f"Resultado: {resultado}")

finally:
    # Se ejecuta SIEMPRE, haya o no excepción
    # Útil para limpiar recursos
    print("Operación terminada")
```

**`else`** es el bloque que la gente olvida. Se ejecuta si el `try` se completó sin errores. ¿Por qué no poner ese código dentro del `try`? Porque quieres que solo el código que puede fallar esté en el `try`. Si pones más código ahí, podrías capturar excepciones que no esperabas.

**`finally`** se ejecuta pase lo que pase. Incluso si hay un `return` dentro del `try` o del `except`. Es para garantizar que los recursos se liberen (cerrar archivos, cerrar conexiones, etc.).

### Captura específica vs genérica

**NUNCA hagas un bare except**. Es el peor anti-patrón de Python:

```python
# MAL -- captura TODO, incluyendo Ctrl+C y errores de sintaxis
try:
    resultado = operacion_riesgosa()
except:
    pass    # silencia el error -- los bugs se vuelven invisibles

# MAL -- casi tan malo como bare except
try:
    resultado = operacion_riesgosa()
except Exception:
    pass    # al menos no captura SystemExit/KeyboardInterrupt, pero sigue siendo malo

# BIEN -- captura SOLO lo que esperas
try:
    resultado = int(texto_usuario)
except ValueError:
    print(f"'{texto_usuario}' no es un número válido")
    resultado = 0
```

La regla: **captura la excepción más específica posible**. Si sabes que `int()` puede lanzar `ValueError`, captura `ValueError`, no `Exception`.

### Raising exceptions

Tú también puedes (y debes) lanzar excepciones cuando tu código recibe datos inválidos:

```python
def calcular_promedio(valores):
    """Calcula el promedio de una lista de números.

    Args:
        valores: Lista no vacía de números.

    Raises:
        TypeError: Si valores no es una lista.
        ValueError: Si la lista está vacía.
    """
    if not isinstance(valores, list):
        raise TypeError(f"Se esperaba una lista, se recibió {type(valores).__name__}")
    if not valores:
        raise ValueError("La lista no puede estar vacía")
    return sum(valores) / len(valores)
```

### ¿Cuándo lanzar excepciones?

| Lanza excepción cuando... | Retorna None/valor por defecto cuando... |
|---------------------------|------------------------------------------|
| El input es fundamentalmente inválido | La ausencia de resultado es normal |
| Es imposible continuar | El usuario puede razonablemente esperar "no encontrado" |
| El error es del programador (bug) | El error es una condición esperada del negocio |

```python
# Lanza excepción: el input no tiene sentido
def factorial(n):
    if n < 0:
        raise ValueError(f"n debe ser >= 0, se recibió {n}")
    ...

# Retorna None: "no encontrado" es un resultado válido
def buscar_usuario(id):
    usuario = db.query(id)
    return usuario  # None si no existe -- es esperado, no excepcional
```

### Custom exceptions

Cuando escribes una librería, crea tus propias excepciones. Esto permite que los usuarios de tu librería capturen errores específicos de tu código:

```python
# mi_paquete/errores.py

class MiPaqueteError(Exception):
    """Excepción base para mi_paquete."""
    pass

class ArchivoInvalidoError(MiPaqueteError):
    """El archivo no tiene el formato esperado."""
    pass

class ColumnaFaltanteError(MiPaqueteError):
    """Falta una columna requerida en los datos."""
    pass
```

```python
# mi_paquete/lector.py
from .errores import ArchivoInvalidoError, ColumnaFaltanteError

def leer_datos(ruta):
    if not ruta.endswith(".csv"):
        raise ArchivoInvalidoError(f"Se esperaba un .csv, se recibió: {ruta}")
    ...
```

```python
# El usuario puede capturar a distintos niveles de especificidad
from mi_paquete.errores import MiPaqueteError, ArchivoInvalidoError

try:
    datos = leer_datos("archivo.txt")
except ArchivoInvalidoError:
    print("El archivo no es CSV")
except MiPaqueteError:
    print("Algo salió mal con mi_paquete")
```

La jerarquía de excepciones es la clave: `ArchivoInvalidoError` hereda de `MiPaqueteError`, que hereda de `Exception`. El usuario puede capturar al nivel de detalle que necesite.

### Buenas prácticas

1. **Captura lo más específico posible.** `except ValueError` es mejor que `except Exception`.
2. **No silencies errores.** `except: pass` es como tapar la luz del check engine con cinta. El problema sigue ahí.
3. **Usa excepciones para casos excepcionales, no para flujo de control.** No uses `try/except` como si fuera `if/else` para lógica normal.
4. **Documenta qué lanza tu función.** Usa la sección `Raises:` en el docstring.
5. **Incluye información útil en el mensaje.** `raise ValueError("x debe ser positivo")` es mucho mejor que `raise ValueError()`.
6. **Crea excepciones personalizadas** para tu librería. Los usuarios de tu código lo van a agradecer.

---

## Ejercicios

:::exercise{title="Verificación rápida" difficulty="1"}

Sin ver el material de arriba, responde estas preguntas. Si no puedes responder alguna, vuelve a la sección correspondiente:

1. ¿Cuál es la diferencia entre un módulo y un paquete?
2. Si creas un archivo llamado `json.py` en tu directorio de trabajo y luego haces `import json`, ¿qué pasa? ¿Por qué?
3. ¿Para qué sirve `__init__.py`?
4. ¿Cuál es la diferencia entre `from .modulo import func` y `from paquete.modulo import func`?
5. ¿Qué controla la variable `__all__`?
6. Cuando ejecutas `python3 mi_script.py`, ¿cuál es el valor de `__name__` dentro de ese archivo? ¿Y cuando lo importas?
7. ¿Qué tiene de malo `except: pass`?
8. ¿Cuándo usarías `lru_cache`?
9. ¿Por qué `pathlib.Path` es mejor que `os.path.join`?
10. ¿Cuándo deberías crear excepciones personalizadas?

:::

:::exercise{title="Explorar la librería estándar" difficulty="2"}

Resuelve las siguientes tareas usando **solo la librería estándar** (no puedes usar pandas ni ningún paquete externo):

**Tarea 1: pathlib**

Usando `pathlib`, escribe un script que reciba un directorio como argumento y:
- Cuente cuántos archivos `.py` hay (recursivamente)
- Imprima el nombre del archivo `.py` más grande (en bytes)
- Liste todos los subdirectorios que contienen un `__init__.py`

**Tarea 2: Counter y defaultdict**

Dado el siguiente texto:

```python
texto = """
Python es un lenguaje de programación. Python es fácil de aprender.
La programación en Python es divertida. Python tiene una gran comunidad.
La comunidad de Python es activa y amigable.
"""
```

- Usa `Counter` para encontrar las 5 palabras más frecuentes (convierte a minúsculas y quita puntuación primero)
- Usa `defaultdict` para agrupar las palabras por su primera letra

**Tarea 3: functools**

Escribe una función `fibonacci(n)` con `@lru_cache` que calcule el n-ésimo número de Fibonacci. Verifica que `fibonacci(100)` se calcula instantáneamente. Luego usa `fibonacci.cache_info()` para ver cuántos hits y misses tuvo el cache.

:::

:::exercise{title="Mini-paquete" difficulty="2"}

Construye un paquete llamado `texto_utils` con esta estructura:

```
texto_utils/
├── __init__.py
├── limpieza.py       # limpiar, quitar_acentos, normalizar
├── analisis.py       # contar_palabras, contar_caracteres, frecuencias
└── errores.py        # TextoVacioError
```

Requisitos:

1. **`errores.py`**: define `TextoVacioError(Exception)` -- se lanza cuando una función recibe un string vacío.

2. **`limpieza.py`**: implementa estas funciones:
   - `limpiar(texto)` -- quita espacios al inicio/final, convierte a minúsculas
   - `normalizar(texto)` -- quita puntuación y espacios dobles
   - Ambas deben lanzar `TextoVacioError` si el texto está vacío

3. **`analisis.py`**: implementa estas funciones:
   - `contar_palabras(texto)` -- retorna el número de palabras
   - `frecuencias(texto)` -- retorna un `Counter` con las frecuencias de cada palabra

4. **`__init__.py`**: exporta las funciones principales para que el usuario pueda hacer:
   ```python
   from texto_utils import limpiar, contar_palabras, frecuencias
   ```

5. Define `__all__` correctamente.

6. Agrega un bloque `if __name__ == "__main__":` en `analisis.py` que demuestre cómo usar las funciones.

7. Agrega un docstring Google style a cada función.

Verifica que todo funciona:

```python
from texto_utils import limpiar, frecuencias, TextoVacioError

texto = limpiar("  Hola Mundo! Hola Python!  ")
print(texto)                    # "hola mundo! hola python!"
print(frecuencias(texto))       # Counter({'hola': 2, ...})

try:
    limpiar("")
except TextoVacioError:
    print("Texto vacío detectado")
```

:::

:::prompt{title="Revisar estructura de un paquete Python" for="ChatGPT/Claude"}

Tengo un paquete de Python con esta estructura:

```
[pega aquí tu estructura de directorios]
```

Y este es mi `__init__.py`:

```python
[pega aquí tu código]
```

Revisa:
1. ¿La estructura tiene sentido? ¿Algún módulo debería dividirse o fusionarse?
2. ¿Los imports en `__init__.py` son correctos? ¿Estoy usando relativos donde debo?
3. ¿`__all__` está bien definido?
4. ¿Hay algo que un usuario de mi paquete encontraría confuso?
5. ¿Mis excepciones personalizadas tienen una jerarquía razonable?
6. Si tengo sub-paquetes, ¿la separación de responsabilidades es clara?

Sugiéreme mejoras concretas con código.

:::
