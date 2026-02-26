# Estilo y legibilidad

Código se lee mucho más de lo que se escribe. El estilo no es estético -- es funcional. Código legible tiene menos bugs, es más fácil de modificar, y otros (incluyendo tu yo del futuro) pueden entenderlo sin querer arrancarse los ojos.

Ya viste los fundamentos de PEP 8 en el curso de DataCamp. Aquí vamos más allá: **por qué** existen estas reglas, qué herramientas automatizan el trabajo sucio, cómo usar type hints en la práctica, y cómo refactorizar código para que se entienda solo.

---

## 1. PEP 8: la guía de estilo de Python

### ¿Qué es PEP 8?

PEP 8 es la guía oficial de estilo para Python, escrita por Guido van Rossum (el creador del lenguaje). No es ley -- el intérprete no la ejecuta. Pero la comunidad sí. Si mandas un pull request a un proyecto open source con código que viola PEP 8, lo primero que te van a pedir es que lo arregles.

La frase más citada de PEP 8 es también la más malinterpretada:

> "A foolish consistency is the hobgoblin of little minds."

Esto **no** significa "ignora las reglas". Significa: si seguir la regla hace tu código **menos** legible en un caso concreto, rompe la regla. Pero primero necesitas conocerla lo suficiente para saber cuándo romperla.

Abre Python y ejecuta `import this`. Lee los aforismos. Los que más importan para este tema: **"Readability counts"**, **"Explicit is better than implicit"**, **"There should be one-- and preferably only one --obvious way to do it"**.

### Convenciones de nombres

| Tipo | Convención | Ejemplo |
|------|-----------|---------|
| Variables, funciones | `snake_case` | `mi_variable`, `calcular_total()` |
| Clases | `CamelCase` | `ValidadorCSV`, `FuenteDatos` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_INTENTOS`, `PI` |
| Módulos | `snake_case` | `operaciones.py`, `mi_modulo.py` |
| Paquetes | `lowercase` | `mipaquete` |
| "Privados" | prefijo `_` | `_cache`, `_procesar()` |

Esto no es arbitrario. Cuando ves `MiClase` sabes que es una clase. Cuando ves `mi_funcion` sabes que es una función. Cuando ves `MAX_REINTENTOS` sabes que es una constante. Las convenciones codifican información en el nombre.

**Errores comunes que veo cada semestre:**

```python
# MAL -- mezcla de convenciones
class datos_csv:         # deberia ser DatosCSV
    pass

def CalcularTotal():     # deberia ser calcular_total()
    pass

maxReintentos = 5        # deberia ser max_reintentos o MAX_REINTENTOS
```

### Espaciado e indentación

**4 espacios** por nivel de indentación. Nunca tabs. Esta no es una sugerencia -- es la regla más universal de Python. Mezclar tabs y espacios produce errores silenciosos.

```python
# BIEN
def calcular_total(precios: list[float]) -> float:
    total = 0.0
    for precio in precios:
        if precio > 0:
            total += precio
    return total

# MAL -- 2 espacios (no es Python idiomático)
def calcular_total(precios):
  total = 0.0
  for precio in precios:
    if precio > 0:
      total += precio
  return total
```

**Líneas en blanco:**

- **2 líneas** en blanco entre definiciones de nivel superior (funciones, clases)
- **1 línea** en blanco entre métodos de una clase
- **0 líneas** en blanco extra dentro de una función (no metas líneas vacías decorativas)

**Espacios alrededor de operadores:**

```python
# BIEN                              # MAL
x = 1 + 2                          x=1+2
lista = [1, 2, 3]                  lista = [1 , 2 , 3]
funcion(a, b)                       funcion( a, b )
dict["clave"]                       dict ["clave"]
tupla = (1,)                        tupla = (1 , )
```

Excepción: en argumentos con valores por defecto, **no** pongas espacios alrededor del `=`:

```python
# BIEN
def funcion(a, b=10, c="hola"):
    pass

# MAL
def funcion(a, b = 10, c = "hola"):
    pass
```

### Longitud de línea

PEP 8 dice 79 caracteres. Eso viene de la época de terminales de 80 columnas. En la práctica moderna:

- **79** -- PEP 8 estricto. Lo usan la librería estándar y proyectos puristas.
- **88** -- Black (el formateador más popular) usa este límite. Es un buen punto medio.
- **99** -- Común en proyectos que trabajan con datos (pandas, SQL). Para el curso usaremos este.
- **120+** -- Demasiado. Si necesitas tanto, tu código probablemente hace demasiado en una línea.

Cuando una línea es demasiado larga, usa **paréntesis** para romperla (preferido sobre `\`):

```python
# BIEN -- parentesis implicitos
resultado = (
    valor_base
    + impuesto
    - descuento
    + cargo_envio
)

# BIEN -- llamada larga
datos_filtrados = dataframe.query(
    "edad > 18 and ciudad == 'CDMX'"
).sort_values("nombre")

# FUNCIONA PERO MENOS LIMPIO -- backslash
resultado = valor_base \
    + impuesto \
    - descuento
```

### Orden de imports

Tres grupos, separados por una línea en blanco, alfabético dentro de cada grupo:

```python
# 1. Biblioteca estándar
import os
import sys
from pathlib import Path

# 2. Paquetes de terceros
import pandas as pd
import requests

# 3. Imports locales
from mi_paquete import validador
from mi_paquete.utils import limpiar
```

Esto no es algo que debas hacer manualmente. `isort` o `ruff` lo hacen por ti en un segundo. Pero necesitas saber el orden para entender por qué tu linter te marca errores.

### Lo que PEP 8 NO dice

PEP 8 es sobre **formato** (cómo se ve el código), no sobre **diseño** (cómo se estructura). Puedes escribir código terrible que sigue PEP 8 perfectamente:

```python
# Sigue PEP 8 al 100%. Sigue siendo código horrible.
def f(d, k, v):
    """Procesa datos."""
    r = {}
    for i in d:
        if i[k] == v:
            r[i["id"]] = i
    return r
```

El estilo es **necesario pero no suficiente** para escribir buen código. Las siguientes secciones cubren lo que PEP 8 no cubre.

---

## 2. Código que se documenta solo

El mejor comentario es el que no necesitas escribir porque el código ya es claro.

### Nombres que cuentan una historia

La diferencia entre código críptico y código legible casi siempre es la calidad de los nombres:

```python
# Malo -- necesitas leer cada linea para entender qué hace
d = {}
for x in data:
    if x[2] > 0:
        d[x[0]] = x[1]

# Bueno -- se lee como una descripcion
ventas_por_region = {}
for registro in datos_ventas:
    if registro.monto > 0:
        ventas_por_region[registro.region] = registro.producto
```

El segundo ejemplo tiene exactamente la misma lógica. Pero no necesitas un comentario para entenderlo. Las variables **te dicen** lo que está pasando.

### Funciones = verbos, variables = sustantivos

```python
calcular_total(precios)              # funcion: dice qué HACE
total_ventas = calcular_total()      # variable: dice qué ES
es_valido = validar_email(texto)     # booleano: prefijo es_/tiene_/puede_
```

Nombres a evitar:

| Malo | Bueno | Por qué |
|------|-------|---------|
| `process()` | `limpiar_nulos()` | "Process" no dice nada |
| `data` | `ventas_mensuales` | "Data" es demasiado genérico |
| `handle()` | `enviar_notificacion()` | "Handle" no dice qué hace |
| `temp` | `celsius_actual` | "Temp" es ambiguo (temperatura? temporal?) |
| `flag` | `es_administrador` | "Flag" no dice de qué |
| `Manager` | `ValidadorCSV` | "Manager" no tiene significado concreto |
| `utils.py` | `conversiones.py` | "Utils" es un cajón de sastre |

### Funciones que hacen una cosa

Una función debe hacer **una cosa** y su nombre debe decir cuál. Si necesitas la palabra "y" para describir lo que hace, divídela:

```python
# MAL -- hace dos cosas: valida Y guarda
def validar_y_guardar_usuario(datos):
    if not datos.get("email"):
        raise ValueError("Email requerido")
    if not datos.get("nombre"):
        raise ValueError("Nombre requerido")
    usuario = Usuario(**datos)
    db.session.add(usuario)
    db.session.commit()
    return usuario
```

```python
# BIEN -- cada funcion hace una cosa
def validar_datos_usuario(datos: dict) -> None:
    """Lanza ValueError si los datos son invalidos."""
    campos_requeridos = ["email", "nombre"]
    for campo in campos_requeridos:
        if not datos.get(campo):
            raise ValueError(f"{campo} es requerido")


def guardar_usuario(datos: dict) -> Usuario:
    """Crea y persiste un usuario en la base de datos."""
    validar_datos_usuario(datos)
    usuario = Usuario(**datos)
    db.session.add(usuario)
    db.session.commit()
    return usuario
```

`guardar_usuario` todavía llama a `validar_datos_usuario`, pero ahora puedes validar **sin** guardar, testear la validación **por separado**, y reusar la validación en otros contextos.

### Comentarios: cuándo sí, cuándo no

Los comentarios deben explicar **por qué**, no **qué**. El código ya dice qué hace. Si necesitas un comentario para explicar qué hace tu código, probablemente debes refactorizar el código.

```python
# MAL -- repite lo que el codigo ya dice
x = x + 1  # incrementar x en 1
usuarios.sort(key=lambda u: u.edad)  # ordena usuarios por edad

# BIEN -- explica una decision no obvia
x = x + 1  # offset de +1 porque la API usa indices base-1

# BIEN -- explica por que esta implementacion y no otra
# Usamos binary search en vez de linear scan porque la lista
# tiene >1M elementos y esta funcion se llama en cada request
indice = bisect.bisect_left(datos_ordenados, objetivo)

# BIEN -- advierte de algo no obvio
# CUIDADO: esta funcion modifica el dataframe in-place
df.drop(columns=["temp"], inplace=True)
```

**Regla**: el código te dice el QUÉ, los comentarios te dicen el POR QUÉ. Si necesitas un comentario para explicar el QUÉ, refactoriza el código.

### Código muerto

```python
# MAL -- codigo comentado "por si acaso"
def procesar(datos):
    # resultado = datos.copy()
    # resultado = resultado.dropna()
    # if len(resultado) > 0:
    #     resultado = resultado.reset_index()
    resultado = limpiar(datos)
    return resultado
```

Borra el código muerto. Git tiene historial. Si algún día necesitas ese código (no lo vas a necesitar), está en un commit anterior. El código comentado es ruido visual que distrae a quien lee.

### Números mágicos

Un número mágico es un literal numérico que aparece en el código sin explicación. El problema no es el número -- es que **no sabes por qué es ese valor**:

```python
# Malo -- por que 0.7? por que 3? por que 86400?
if score > 0.7:
    return "aprobado"

time.sleep(3)

if edad_segundos > 86400:
    renovar_token()
```

```python
# Bueno -- el nombre explica el significado
UMBRAL_APROBACION = 0.7
SEGUNDOS_ENTRE_REINTENTOS = 3
SEGUNDOS_POR_DIA = 86_400

if score > UMBRAL_APROBACION:
    return "aprobado"

time.sleep(SEGUNDOS_ENTRE_REINTENTOS)

if edad_segundos > SEGUNDOS_POR_DIA:
    renovar_token()
```

Nota el uso de `_` como separador visual en `86_400`. Python lo permite en literales numéricos desde la versión 3.6 y hace los números grandes más legibles.

---

## 3. Type hints (anotaciones de tipo)

### ¿Qué son?

Python es dinámicamente tipado: no verificas tipos en tiempo de ejecución (a menos que tú lo hagas explícitamente). Los type hints son **anotaciones opcionales** que documentan los tipos esperados. No cambian el comportamiento de tu programa. Son documentación que herramientas pueden verificar.

Fueron introducidos en Python 3.5 (PEP 484) y han evolucionado mucho desde entonces.

```python
# Sin type hints -- tienes que leer el cuerpo para saber que espera
def calcular_promedio(valores):
    return sum(valores) / len(valores)

# Con type hints -- la firma es suficiente
def calcular_promedio(valores: list[float]) -> float:
    return sum(valores) / len(valores)
```

### Sintaxis básica

```python
# Funciones: anotas parametros y retorno
def sumar(a: int, b: int) -> int:
    return a + b

def saludar(nombre: str, formal: bool = False) -> str:
    if formal:
        return f"Estimado/a {nombre}"
    return f"Hola {nombre}"

# Variables: cuando el tipo no es obvio
nombre: str = "Ana"
edades: list[int] = [20, 25, 30]
config: dict[str, int] = {"timeout": 30, "max_reintentos": 5}
```

### Tipos comunes

| Tipo | Ejemplo | Desde |
|------|---------|-------|
| Básicos | `int`, `float`, `str`, `bool` | siempre |
| Colecciones | `list[int]`, `dict[str, float]`, `tuple[int, str]`, `set[str]` | Python 3.9 |
| Opcional | `str \| None` | Python 3.10 |
| Union | `int \| str` | Python 3.10 |
| Callable | `Callable[[int, int], int]` | `from typing import Callable` |
| Any | `Any` | `from typing import Any` |

En Python < 3.9, los tipos de colección se importan de `typing`: `List[int]`, `Dict[str, float]`, etc. En Python < 3.10, usas `Optional[str]` y `Union[int, str]` del módulo `typing`. Para este curso usamos Python 3.12, así que puedes usar la sintaxis moderna.

### `Optional` y `None`

Una función que puede retornar un valor o `None` necesita anotarlo:

```python
def buscar_usuario(email: str) -> dict | None:
    """Retorna los datos del usuario o None si no existe."""
    for usuario in usuarios:
        if usuario["email"] == email:
            return usuario
    return None
```

`dict | None` es equivalente a `Optional[dict]`. La sintaxis con `|` es más limpia y funciona desde Python 3.10.

### Tipos para colecciones anidadas

Las cosas se ponen más expresivas con tipos compuestos:

```python
# Lista de diccionarios con string como clave y cualquier tipo como valor
def cargar_registros(ruta: str) -> list[dict[str, str | int | float]]:
    ...

# Función que recibe otra función como argumento
from typing import Callable

def aplicar_a_todos(
    datos: list[float],
    transformacion: Callable[[float], float],
) -> list[float]:
    return [transformacion(x) for x in datos]

# Uso:
aplicar_a_todos([1.0, 2.0, 3.0], lambda x: x ** 2)
```

### TypeAlias: nombres para tipos complejos

Cuando un tipo se repite o es largo, dale un nombre:

```python
# Sin alias -- dificil de leer y se repite
def filtrar(datos: list[dict[str, str | int | float]], campo: str) -> list[dict[str, str | int | float]]:
    ...

# Con alias -- mucho mas claro
type Registro = dict[str, str | int | float]  # Python 3.12+

def filtrar(datos: list[Registro], campo: str) -> list[Registro]:
    ...
```

En Python < 3.12, usas `Registro = dict[str, str | int | float]` directamente (sin la keyword `type`), o `TypeAlias` de `typing`.

### ¿Por qué usar type hints?

1. **Tu IDE te da mejor autocompletado.** Si tu función dice que retorna un `dict`, el IDE te muestra `.keys()`, `.values()`, `.items()` automáticamente. Sin el hint, te muestra todo y nada.

2. **`mypy` encuentra bugs antes de ejecutar.** Error de tipo que descubrirías en producción a las 3am? `mypy` lo encuentra en 2 segundos sin ejecutar nada.

3. **Son documentación que nunca se desactualiza.** Un comentario que dice "recibe una lista de enteros" se puede quedar obsoleto. Un type hint `list[int]` lo verifica `mypy` en cada commit.

4. **Hacen las interfaces más claras.** Cuando lees `def procesar(datos)`, no sabes qué es `datos`. Cuando lees `def procesar(datos: pd.DataFrame) -> pd.DataFrame`, sabes exactamente qué esperar.

### `mypy`: verificador estático de tipos

`mypy` lee tus type hints y verifica que los tipos sean consistentes **sin ejecutar** el código:

```bash
pip install mypy
mypy mi_archivo.py
```

```python
# mi_archivo.py
def duplicar(texto: str) -> str:
    return texto * 2

resultado = duplicar(42)  # mypy error: Argument 1 has incompatible type "int"; expected "str"
```

Python ejecuta esto sin error (retorna `84`). Pero `mypy` te avisa que probablemente no es lo que querías. Este tipo de bugs son los que llegan a producción porque "funciona en mi máquina".

### Cuándo usar type hints (y cuándo no)

**Úsalos siempre en:**

- Firmas de funciones públicas (parámetros y retorno)
- Atributos de clases
- Variables cuyo tipo no es obvio

**No los necesitas en:**

```python
# Redundante -- el tipo es obvio
x: int = 5
nombre: str = "Ana"
lista: list = []

# Mejor asi -- Python infiere el tipo, mypy tambien
x = 5
nombre = "Ana"
lista = []
```

**La regla de oro**: si alguien puede mirar la línea y saber el tipo inmediatamente, no lo anotes. Si hay ambigüedad, sí.

```python
# Aqui SI anota -- no es obvio que retorna
resultado: float | None = cache.get("valor_promedio")

# Aqui NO anota -- es obvio
total = 0
nombres = ["Ana", "Luis"]
```

---

## 4. Linters y formateadores

Memorizar PEP 8 no es buena inversión de tu tiempo. Para eso existen herramientas que verifican y corrigen automáticamente.

### ¿Qué hace un linter?

Un linter **analiza** tu código sin ejecutarlo y te dice:

- Violaciones de estilo (PEP 8)
- Bugs potenciales (variables no usadas, imports que sobran, código inalcanzable)
- Problemas de complejidad (funciones demasiado largas o con demasiados condicionales anidados)

Un formateador va un paso más allá: **reescribe** tu código automáticamente para que siga las reglas.

| Tipo | Qué hace | Ejemplos |
|------|----------|----------|
| **Linter** | Señala problemas (no los arregla todos) | flake8, pylint |
| **Formateador** | Reescribe el código automáticamente | black, autopep8 |
| **Ambos** | Señala Y arregla | **ruff** |

### `ruff`: el linter moderno

`ruff` es la herramienta que recomiendo. Está escrita en Rust, es órdenes de magnitud más rápida que las alternativas, y reemplaza varias herramientas a la vez: flake8, isort, pycodestyle, pydocstyle, y más.

```bash
# Instalar
pip install ruff

# Verificar estilo
ruff check mi_archivo.py

# Verificar y arreglar automaticamente lo que pueda
ruff check --fix mi_archivo.py

# Formatear (como Black)
ruff format mi_archivo.py
```

Ejemplo en acción:

```python
# ANTES: mi_archivo.py
import os,sys
import pandas as pd
from pathlib import Path
import json

def Calcular_Total( lista_precios,descuento = 0.1 ):
  x = 0
  for i in lista_precios:
    x=x+i
  return x * (1 - descuento)
```

```bash
$ ruff check mi_archivo.py
mi_archivo.py:1:10: E401 Multiple imports on one line
mi_archivo.py:1:1: F401 `os` imported but unused
mi_archivo.py:1:1: F401 `sys` imported but unused
mi_archivo.py:3:1: I001 Import block is un-sorted or un-formatted
mi_archivo.py:4:1: F401 `json` imported but unused
mi_archivo.py:6:5: N802 Function name should be lowercase
mi_archivo.py:6:20: E211 Whitespace before '('
...
```

```bash
$ ruff format mi_archivo.py
# Reescribe el archivo con indentacion correcta, espaciado consistente, etc.
```

### Diferencia entre `ruff check` y `ruff format`

- **`ruff check`** = linter. Encuentra errores lógicos y de estilo. Puede arreglar algunos con `--fix`.
- **`ruff format`** = formateador. Se enfoca en el formato visual: indentación, espacios, comillas, longitud de línea. Reescribe el archivo.

Usa **ambos**. Son complementarios.

### Configuración en `pyproject.toml`

En lugar de pasarle flags por la terminal, configura `ruff` en tu `pyproject.toml`. Así todo el equipo usa las mismas reglas:

```toml
[tool.ruff]
line-length = 99
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # errores de pycodestyle
    "F",   # errores de pyflakes (imports no usados, variables indefinidas)
    "W",   # warnings de pycodestyle
    "I",   # isort (orden de imports)
    "N",   # pep8-naming (convenciones de nombres)
    "UP",  # pyupgrade (modernizar sintaxis)
]

[tool.ruff.format]
quote-style = "double"
```

Las reglas se identifican por letras. `E` y `W` son errores y warnings de estilo. `F` son bugs potenciales. `I` es orden de imports. Puedes activar muchas más en la [documentación de ruff](https://docs.astral.sh/ruff/rules/).

### Integración con tu editor

Instala la extensión de **ruff** en VS Code (o en Cursor). Se configura para correr al guardar:

```json
// .vscode/settings.json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    }
}
```

Con esto, cada vez que guardas un archivo Python:

1. `ruff format` arregla el formato
2. `ruff check --fix` arregla imports, ordena, y corrige lo que pueda
3. Los errores que no puede arreglar aparecen subrayados en el editor

**Ya no tienes que pensar en PEP 8.** El editor lo hace por ti. Tu trabajo es escribir buena lógica con buenos nombres.

### Herramienta legacy: Black

Antes de `ruff format`, el formateador dominante era **Black**. Lo vas a encontrar en muchos proyectos existentes. `ruff format` es compatible con el estilo de Black, así que la migración es transparente. Si estás empezando un proyecto nuevo, usa `ruff` para todo.

---

## 5. Refactoring: mejorar sin cambiar comportamiento

### ¿Qué es refactoring?

Refactorizar es cambiar la **estructura** del código sin cambiar su **comportamiento**. Los tests pasan antes y después del cambio. El objetivo es hacer el código más legible, más mantenible, o más fácil de extender.

No es un paso "extra" que haces cuando tienes tiempo. Es parte fundamental de escribir código. Escribes la primera versión que funciona, y luego la mejoras.

### Patrón 1: Extraer función

Cuando un bloque de código hace una cosa lógica que puedes nombrar, hazlo función:

```python
# ANTES: todo mezclado
def generar_reporte(transacciones):
    # Filtrar transacciones validas
    validas = []
    for t in transacciones:
        if t["monto"] > 0 and t["estado"] == "completada":
            validas.append(t)

    # Calcular totales por categoria
    totales = {}
    for t in validas:
        cat = t["categoria"]
        totales[cat] = totales.get(cat, 0) + t["monto"]

    # Formatear salida
    lineas = []
    for cat, total in sorted(totales.items()):
        lineas.append(f"{cat}: ${total:,.2f}")

    return "\n".join(lineas)
```

```python
# DESPUES: cada responsabilidad tiene nombre
def filtrar_validas(transacciones: list[dict]) -> list[dict]:
    """Retorna solo transacciones completadas con monto positivo."""
    return [
        t for t in transacciones
        if t["monto"] > 0 and t["estado"] == "completada"
    ]


def totalizar_por_categoria(transacciones: list[dict]) -> dict[str, float]:
    """Suma los montos agrupados por categoria."""
    totales: dict[str, float] = {}
    for t in transacciones:
        cat = t["categoria"]
        totales[cat] = totales.get(cat, 0) + t["monto"]
    return totales


def formatear_totales(totales: dict[str, float]) -> str:
    """Formatea los totales como texto legible."""
    lineas = [f"{cat}: ${total:,.2f}" for cat, total in sorted(totales.items())]
    return "\n".join(lineas)


def generar_reporte(transacciones: list[dict]) -> str:
    """Genera un reporte de totales por categoria."""
    validas = filtrar_validas(transacciones)
    totales = totalizar_por_categoria(validas)
    return formatear_totales(totales)
```

`generar_reporte` ahora se lee como un resumen ejecutivo: filtra, totaliza, formatea. Si hay un bug en el cálculo de totales, sabes exactamente dónde buscar.

### Patrón 2: Guard clauses (retorno temprano)

La "pirámide de la muerte" es código con muchos niveles de anidación. Cada `if` anidado es un nivel más de complejidad mental:

```python
# MAL -- piramide de la muerte
def procesar_pedido(pedido):
    if pedido is not None:
        if pedido.estado == "activo":
            if pedido.tiene_stock():
                if pedido.monto <= pedido.usuario.saldo:
                    cobrar(pedido)
                    enviar(pedido)
                    return "enviado"
                else:
                    return "saldo insuficiente"
            else:
                return "sin stock"
        else:
            return "pedido inactivo"
    else:
        return "pedido invalido"
```

La solución: invierte las condiciones y retorna temprano. Los casos de error salen primero:

```python
# BIEN -- guard clauses, un solo nivel de indentacion
def procesar_pedido(pedido):
    if pedido is None:
        return "pedido invalido"
    if pedido.estado != "activo":
        return "pedido inactivo"
    if not pedido.tiene_stock():
        return "sin stock"
    if pedido.monto > pedido.usuario.saldo:
        return "saldo insuficiente"

    cobrar(pedido)
    enviar(pedido)
    return "enviado"
```

El "happy path" (el caso exitoso) queda al final, sin indentación extra. Los errores se manejan y salen rápido. Lees de arriba a abajo sin tener que rastrear cuál `else` corresponde a cuál `if`.

### Patrón 3: Reemplazar número mágico con constante

Ya lo vimos arriba, pero vale la pena enfatizar que aplica también a strings mágicos:

```python
# MAL
if response.status_code == 429:
    time.sleep(60)

if usuario.rol == "admin":
    ...

# BIEN
HTTP_TOO_MANY_REQUESTS = 429
SEGUNDOS_ESPERA_RATE_LIMIT = 60
ROL_ADMINISTRADOR = "admin"

if response.status_code == HTTP_TOO_MANY_REQUESTS:
    time.sleep(SEGUNDOS_ESPERA_RATE_LIMIT)

if usuario.rol == ROL_ADMINISTRADOR:
    ...
```

### Patrón 4: Simplificar condicionales

Extraer una condición compleja a una variable con nombre es uno de los refactorings más poderosos:

```python
# MAL -- que condicion es esta?
if (usuario.edad >= 18 and usuario.cuenta_activa
        and not usuario.tiene_deuda and usuario.verificado):
    aprobar_credito(usuario)

# BIEN -- la variable nombra la condicion
es_elegible_para_credito = (
    usuario.edad >= 18
    and usuario.cuenta_activa
    and not usuario.tiene_deuda
    and usuario.verificado
)
if es_elegible_para_credito:
    aprobar_credito(usuario)
```

Otros patrones comunes de simplificación:

```python
# Innecesario                      # Simplificado
if x == True:                       if x:
if x == False:                      if not x:
if len(lista) > 0:                  if lista:
if len(lista) == 0:                 if not lista:
if x is not None:                   if x is not None:  # este esta bien, dejalo asi

# Anti-patron clasico
if condicion:                       return condicion
    return True
else:
    return False
```

### Patrón 5: Eliminar código muerto

Si una función no se llama desde ningún lado, bórrala. Si un import no se usa, quítalo. Si una variable se asigna pero nunca se lee, elimínala. `ruff` detecta todo esto automáticamente.

**No tengas miedo de borrar código.** Git recuerda todo.

### Ejemplo completo: refactoring paso a paso

Empezamos con esto:

```python
def proc(d):
    r = []
    for i in range(len(d)):
        if d[i]["age"] >= 18 and d[i]["active"] == True and d[i]["score"] > 0.7:
            x = d[i]["name"].strip().title()
            r.append({"name": x, "score": d[i]["score"], "cat": "A" if d[i]["score"] > 0.9 else "B" if d[i]["score"] > 0.8 else "C"})
    r.sort(key=lambda x: x["score"], reverse=True)
    return r
```

**Paso 1: Nombres descriptivos**

```python
def filtrar_candidatos_aprobados(personas):
    aprobados = []
    for i in range(len(personas)):
        persona = personas[i]
        if persona["age"] >= 18 and persona["active"] == True and persona["score"] > 0.7:
            nombre = persona["name"].strip().title()
            categoria = "A" if persona["score"] > 0.9 else "B" if persona["score"] > 0.8 else "C"
            aprobados.append({"name": nombre, "score": persona["score"], "cat": categoria})
    aprobados.sort(key=lambda x: x["score"], reverse=True)
    return aprobados
```

**Paso 2: Extraer lógica, eliminar anti-patrones**

```python
EDAD_MINIMA = 18
SCORE_MINIMO = 0.7

def es_candidato_valido(persona: dict) -> bool:
    return (
        persona["age"] >= EDAD_MINIMA
        and persona["active"]  # sin == True
        and persona["score"] > SCORE_MINIMO
    )

def clasificar_score(score: float) -> str:
    if score > 0.9:
        return "A"
    if score > 0.8:
        return "B"
    return "C"

def filtrar_candidatos_aprobados(personas: list[dict]) -> list[dict]:
    """Filtra y clasifica candidatos aprobados, ordenados por score."""
    aprobados = []
    for persona in personas:  # iterar directamente, sin range(len(...))
        if not es_candidato_valido(persona):
            continue
        aprobados.append({
            "name": persona["name"].strip().title(),
            "score": persona["score"],
            "cat": clasificar_score(persona["score"]),
        })
    aprobados.sort(key=lambda p: p["score"], reverse=True)
    return aprobados
```

El resultado tiene la misma funcionalidad. Pero ahora:

- Puedes testear `es_candidato_valido` por separado
- Puedes testear `clasificar_score` por separado
- Los umbrales son constantes con nombre
- El loop itera directamente (sin `range(len(...))`)
- No hay `== True` innecesario
- La función principal se lee como una receta

---

## Ejercicios

:::exercise{title="Detecta los problemas" difficulty="1"}

Este código tiene al menos **10 problemas** de estilo, naming y legibilidad. Identifica cada uno, explica qué regla viola, y reescribe el código completo corregido:

```python
import pandas as pd
import os,sys
from pathlib import Path
import json
import requests

def Process_Data( data,Config = {} ):
  temp = []
  for i in range(0,len(data)):
    x = data[i]
    if x["value"]>0:
      if x["status"]=="active":
        if x["type"] in ["A","B","C"]:
          temp.append({"n": x["name"].upper(), "v": x["value"] * 1.16, "t": x["type"]})
  temp.sort(key=lambda x: x["v"],reverse=True)
  return temp

class data_processor:
  def __init__(self,Data,name):
    self.Data=Data
    self.name = name
    self.Results = []
  def run(self):
    for D in self.Data:
      r = Process_Data(D)
      self.Results.append(r)
    return self.Results
```

Pistas: busca violaciones de PEP 8, nombres malos, pirámide de la muerte, números mágicos, argumentos mutables por defecto, código que no se documenta solo.

:::

:::exercise{title="Agrega type hints" difficulty="2"}

Agrega type hints completos a estas funciones. No cambies la lógica -- solo anota parámetros y retorno. Usa la sintaxis moderna de Python 3.12:

```python
def agrupar_por(registros, campo):
    """Agrupa una lista de dicts por el valor de un campo."""
    grupos = {}
    for registro in registros:
        clave = registro[campo]
        if clave not in grupos:
            grupos[clave] = []
        grupos[clave].append(registro)
    return grupos


def top_n(elementos, n, clave=None, reverso=True):
    """Retorna los n elementos mas grandes."""
    ordenados = sorted(elementos, key=clave, reverse=reverso)
    return ordenados[:n]


def buscar_todos(registros, campo, valor):
    """Retorna todos los registros donde campo == valor."""
    return [r for r in registros if r.get(campo) == valor]


def resumen_numerico(valores):
    """Retorna dict con min, max, promedio y conteo. Retorna None si la lista esta vacia."""
    if not valores:
        return None
    return {
        "min": min(valores),
        "max": max(valores),
        "promedio": sum(valores) / len(valores),
        "conteo": len(valores),
    }


def transformar(datos, funciones):
    """Aplica una lista de funciones en secuencia a los datos."""
    resultado = datos
    for funcion in funciones:
        resultado = funcion(resultado)
    return resultado
```

Para cada función, justifica brevemente por qué elegiste esos tipos. Pon especial atención en `top_n` y `transformar` -- hay más de una opción válida.

:::

:::exercise{title="Refactoring paso a paso" difficulty="2"}

Toma esta función y mejórala en tres pasos, como el ejemplo de la sección 5. En cada paso, aplica un patrón de refactoring diferente (renombrar, extraer función, eliminar número mágico, guard clause, simplificar condicional, etc.):

```python
def f(l, t):
    res = []
    for item in l:
        if item is not None:
            if type(item) == dict:
                if "name" in item and "score" in item:
                    if item["score"] >= 60:
                        if t == "all" or item.get("dept") == t:
                            n = item["name"]
                            s = item["score"]
                            g = "A" if s >= 90 else "B" if s >= 75 else "C"
                            res.append({"nombre": n, "puntaje": s, "nivel": g})
    res = sorted(res, key=lambda x: x["puntaje"], reverse=True)
    return res
```

Para cada paso escribe:

1. Qué patrón de refactoring aplicaste
2. El código resultante
3. Qué mejoró respecto al paso anterior

El resultado final debe ser código que un compañero entienda sin preguntarte nada.

:::

:::prompt{title="Revisión de estilo y legibilidad" for="ChatGPT/Claude"}

Revisa el siguiente código Python y dame retroalimentación detallada sobre estilo y legibilidad:

```python
[pega aqui tu codigo]
```

Evalúa estos aspectos con ejemplos concretos de código corregido:

1. **PEP 8**: convenciones de nombres, espaciado, imports, longitud de línea
2. **Type hints**: ¿las funciones tienen anotaciones? ¿son correctas?
3. **Nombres**: ¿son descriptivos? ¿las funciones usan verbos? ¿las variables describen qué contienen?
4. **Comentarios**: ¿explican el "por qué" y no el "qué"? ¿hay código comentado que debería borrarse?
5. **Números mágicos**: ¿hay literales que deberían ser constantes con nombre?
6. **Complejidad**: ¿hay condicionales anidados que se puedan aplanar con guard clauses?
7. **Funciones**: ¿alguna hace más de una cosa? ¿se puede extraer lógica?

Para cada problema, muestra el código original y la versión corregida. Al final, muestra el archivo completo refactorizado.

:::
