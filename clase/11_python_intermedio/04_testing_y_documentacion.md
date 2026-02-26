# Testing y documentación en Python

> **Notebook interactivo**: todo el código de esta sección está en un notebook ejecutable.
> [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/11_python_intermedio/code/04_testing_y_documentacion.ipynb)

Tu código funciona... hoy. Cómo sabes que seguirá funcionando mañana después de 10 cambios? Tests. Cómo sabe alguien más cómo usar tu código? Documentación.

Estas dos disciplinas son la diferencia entre un script que escribiste anoche y un proyecto que puedes mantener, compartir y extender durante meses. Ya tomaste el curso de DataCamp sobre ingeniería de software en Python -- sabes que existen los docstrings y que pytest existe. Ahora vamos a ir mucho más allá.

---

## 1. Documentación con docstrings

### Qué es un docstring?

Un docstring es el **primer string literal** que aparece en una función, clase o módulo. No es un comentario. Es **parte del objeto**.

```python
def sumar(a, b):
    """Suma dos numeros y retorna el resultado."""
    return a + b

# Python lo guarda automaticamente:
print(sumar.__doc__)  # "Suma dos numeros y retorna el resultado."

# help() lo muestra formateado:
help(sumar)
```

Diferencia clave con los comentarios:

| | Comentarios (`#`) | Docstrings (`"""..."""`) |
|--|-------------------|------------------------|
| **Propósito** | Explican POR QUÉ | Explican QUÉ y CÓMO usar |
| **Audiencia** | Quien lee el código fuente | Quien usa la función/clase |
| **Ubicación** | En cualquier línea | Primera línea de función/clase/módulo |
| **Acceso** | Solo leyendo el archivo | `help()`, `__doc__`, herramientas externas |
| **Ejemplo** | `# Cache para evitar re-cálculo` | `"""Calcula el factorial de n."""` |

### Docstrings de una línea

Para funciones simples donde el nombre casi lo dice todo:

```python
def sumar(a, b):
    """Suma dos numeros y retorna el resultado."""
    return a + b
```

Reglas: empieza con mayúscula, termina con punto, describe **qué** hace (no cómo lo hace).

### Estilo Google vs Estilo NumPy

Hay dos convenciones principales para docstrings multilínea. Así se ven lado a lado:

**Estilo Google** (más compacto, recomendado para proyectos nuevos):

```python
def buscar(texto: str, patron: str, ignorar_caso: bool = False) -> list[str]:
    """Busca un patron en el texto y retorna las coincidencias.

    Args:
        texto: El string donde buscar.
        patron: El substring a buscar.
        ignorar_caso: Si True, no distingue mayusculas.

    Returns:
        Lista de lineas que contienen el patron.

    Raises:
        ValueError: Si el patron esta vacio.

    Examples:
        >>> buscar("hola mundo", "hola")
        ['hola mundo']
    """
```

**Estilo NumPy** (común en librerías científicas como numpy, scipy, pandas):

```python
def buscar(texto, patron, ignorar_caso=False):
    """Busca un patron en el texto y retorna las coincidencias.

    Parameters
    ----------
    texto : str
        El string donde buscar.
    patron : str
        El substring a buscar.
    ignorar_caso : bool, default False
        Si True, no distingue mayusculas.

    Returns
    -------
    list of str
        Lineas que contienen el patron.

    Raises
    ------
    ValueError
        Si el patron esta vacio.
    """
```

Mi recomendación: usa **estilo Google** para proyectos nuevos. Es más compacto y fácil de leer. Vas a encontrar NumPy style en pandas, scikit-learn y muchas librerías de ciencia de datos, así que necesitas saber leerlo.

La regla más importante: **elige UN estilo y úsalo en todo el proyecto**. Mezclar estilos es peor que no documentar.

### Docstrings para clases

Una clase tiene tres niveles de documentación:

```python
"""Modulo de utilidades para procesamiento de texto.

Proporciona funciones para limpiar, buscar y transformar strings.
Uso tipico: importar las funciones que necesites directamente.
"""


class Contador:
    """Cuenta la frecuencia de elementos en una secuencia.

    Attributes:
        nombre: Identificador del contador.
        datos: Diccionario interno con las frecuencias.
    """

    def __init__(self, nombre):
        """Inicializa el contador.

        Args:
            nombre: Identificador unico para el contador.
        """
        self.nombre = nombre
        self.datos = {}

    def registrar(self, elemento):
        """Incrementa el conteo de un elemento.

        Args:
            elemento: El elemento a contar.
        """
        self.datos[elemento] = self.datos.get(elemento, 0) + 1
```

- **Docstring de módulo**: lo primero en el archivo. Describe qué proporciona el módulo.
- **Docstring de clase**: qué representa la clase y sus atributos principales.
- **Docstring de `__init__`**: los parámetros del constructor.
- **Docstring de método**: qué hace cada método.

### `help()` y `dir()`: introspección gratis

Python tiene herramientas integradas para explorar cualquier objeto sin salir de la terminal:

```python
# help() muestra el docstring formateado
help(len)          # documentacion de len()
help(str.split)    # documentacion de str.split()
help(mi_funcion)   # tu propio docstring, formateado bonito
```

```python
# dir() lista todos los atributos y metodos
import math
dir(math)  # muestra todo: acos, asin, atan, ceil, cos, ...

# Filtrar solo los publicos
publicos = [x for x in dir(math) if not x.startswith("_")]

# type() muestra la clase
type(42)           # <class 'int'>
type("hola")       # <class 'str'>
type(math)         # <class 'module'>
```

Flujo práctico cuando te encuentras con una librería nueva:

```python
import alguna_libreria as lib

# 1. Que hay disponible?
dir(lib)

# 2. Esto se ve interesante, que hace?
help(lib.funcion_interesante)

# 3. Cual es el tipo de este objeto?
type(lib.alguna_cosa)

# 4. Acceso directo al docstring como string
print(lib.funcion_interesante.__doc__)
```

### Generación automática de documentación

Tus docstrings no solo sirven para `help()`. Herramientas especializadas los extraen y generan sitios web completos.

**Sphinx** es el estándar para documentar proyectos de Python. Lo usan Django, Flask, NumPy, pandas y Python mismo:

```bash
pip install sphinx
sphinx-quickstart docs/
```

El concepto es simple: escribes docstrings en tu código, Sphinx los extrae automáticamente, y genera un sitio HTML (o PDF) navegable. La extensión `sphinx-napoleon` habilita docstrings estilo Google y NumPy para que no tengas que escribir en reStructuredText dentro de tus funciones.

**MkDocs** es una alternativa más moderna que usa Markdown en vez de RST:

```bash
pip install mkdocs mkdocstrings
mkdocs new mi-docs
mkdocs serve    # servidor local
```

El plugin `mkdocstrings` extrae docstrings igual que Sphinx.

**Read the Docs** es un servicio gratuito de hosting para documentación. Se conecta a tu repo de GitHub y regenera la documentación en cada push. Si alguna vez has visto una URL `proyecto.readthedocs.io`, es esto.

Para tu librería del curso: buenos docstrings son suficientes. Sphinx y MkDocs son para proyectos más grandes. Pero entender que existen te explica por qué los buenos docstrings importan tanto -- son la base de cualquier sitio de documentación que generes después.

### Cuándo documentar?

- **SIEMPRE**: funciones públicas, clases, módulos -- cualquier cosa que alguien pueda importar
- **A VECES**: funciones internas complejas (las que empiezan con `_`)
- **NUNCA**: cosas obvias (`x = x + 1  # incrementar x`)

Un buen docstring responde cuatro preguntas:

1. Qué hace esta función?
2. Qué parámetros recibe?
3. Qué retorna?
4. Qué puede salir mal (excepciones)?

---

## 2. Por qué testear?

Hay una forma simple de explicarlo: "It works on my machine" no es un test.

El problema es real y lo vas a vivir (si no lo has vivido ya): cambias una función y rompes tres otras sin darte cuenta. Sin tests, te enteras cuando un usuario se queja o cuando tu programa explota en producción a las 3 AM.

Los tests te dan:

- **Confianza para cambiar código** -- refactorizas sabiendo que si algo se rompe, lo vas a saber inmediatamente
- **Documentación ejecutable** -- los tests muestran exactamente cómo se supone que debe comportarse tu código, con ejemplos concretos
- **Detección temprana de bugs** -- el costo de arreglar un bug crece exponencialmente con el tiempo. Un bug detectado por un test cuesta minutos. Uno detectado en producción puede costar días

### La pirámide de testing

```
        /   E2E    \          <-- Pocos: navegador, API completa
       / Integración \        <-- Algunos: componentes juntos
      /  Unit Tests    \      <-- Muchos: funciones individuales
```

- **Unit tests**: prueban UNA función o método en aislamiento. Son rápidos, precisos y fáciles de escribir.
- **Tests de integración**: prueban que varios componentes funcionan juntos (ej: tu función + la base de datos).
- **Tests end-to-end (E2E)**: prueban el sistema completo como lo usaría un usuario (ej: abrir navegador, hacer clic, verificar resultado).

Para tu librería del curso: enfócate en **unit tests**. Son la base de todo lo demás.

---

## 3. pytest en profundidad

pytest es la herramienta estándar para testing en Python. Es más poderosa y flexible que el módulo `unittest` de la librería estándar, y su sintaxis es mucho más limpia.

### Lo básico (repaso rápido)

pytest descubre tests automáticamente si sigues estas reglas:

- Archivos que empiezan con `test_`: `test_operaciones.py`
- Funciones que empiezan con `test_`: `def test_sumar_positivos():`
- Usa `assert` directamente: `assert resultado == esperado`
- Ejecuta con: `pytest tests/ -v`

```python
# tests/test_operaciones.py
from mi_paquete import sumar, restar

def test_sumar_positivos():
    assert sumar(2, 3) == 5

def test_sumar_negativos():
    assert sumar(-1, -1) == -2

def test_restar():
    assert restar(10, 3) == 7
```

```bash
pytest                              # todos los tests
pytest tests/                       # un directorio
pytest tests/test_operaciones.py    # un archivo
pytest -v                           # verbose: muestra cada test
pytest -x                           # para en el primer fallo
pytest -k "sumar"                   # solo tests cuyo nombre contenga "sumar"
pytest --tb=short                   # traceback corto
```

### Estructura de un test: Arrange-Act-Assert

Todo buen test tiene tres fases claramente separadas:

```python
def test_sumar_positivos():
    # Arrange: preparar los inputs
    a, b = 2, 3

    # Act: ejecutar la funcion bajo prueba
    resultado = sumar(a, b)

    # Assert: verificar el resultado
    assert resultado == 5
```

```python
def test_filtrar_mayores():
    # Arrange
    personas = [
        {"nombre": "Ana", "edad": 25},
        {"nombre": "Bob", "edad": 17},
        {"nombre": "Carlos", "edad": 30},
    ]

    # Act
    resultado = filtrar_mayores(personas, edad_minima=18)

    # Assert
    assert len(resultado) == 2
    assert resultado[0]["nombre"] == "Ana"
    assert resultado[1]["nombre"] == "Carlos"
```

Cuando un test falla y está bien estructurado, sabes exactamente dónde buscar: el Arrange tiene datos malos? El Act llama mal a la función? El Assert tiene la expectativa equivocada?

### Testing excepciones

A veces lo correcto es que una función **lance una excepción**. Necesitas verificar eso:

```python
import pytest

def test_dividir_por_cero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)

def test_dividir_por_cero_mensaje():
    with pytest.raises(ZeroDivisionError, match="dividir entre cero"):
        dividir(10, 0)
```

El bloque `with pytest.raises(...)` verifica que se lance la excepción esperada. Si la función NO lanza la excepción, el test falla. El parámetro `match` verifica que el mensaje de error contenga ese texto (acepta regex).

```python
def test_edad_negativa():
    with pytest.raises(ValueError, match="no puede ser negativa"):
        crear_persona("Ana", edad=-5)

def test_tipo_invalido():
    with pytest.raises(TypeError):
        sumar("hola", 5)
```

### Fixtures: setup reutilizable

El problema: muchos tests necesitan el mismo setup (crear un objeto, cargar datos, inicializar estado). Copiar y pegar ese setup en cada test es una mala idea -- si el setup cambia, tienes que tocarlo en N lugares.

Las fixtures de pytest resuelven esto. Son funciones decoradas con `@pytest.fixture` que proporcionan datos o setup a los tests:

```python
import pytest

@pytest.fixture
def datos_ejemplo():
    """Crea una lista de datos para pruebas."""
    return [1, 2, 3, 4, 5]

def test_promedio(datos_ejemplo):
    assert promedio(datos_ejemplo) == 3.0

def test_mediana(datos_ejemplo):
    assert mediana(datos_ejemplo) == 3

def test_suma(datos_ejemplo):
    assert sum(datos_ejemplo) == 15
```

pytest inyecta la fixture automáticamente al hacer coincidir el nombre del parámetro con el nombre de la fixture. Cada test recibe una **instancia fresca** -- los tests no comparten estado.

Un ejemplo más realista con una clase:

```python
@pytest.fixture
def contador():
    """Crea un contador con datos de prueba."""
    c = Contador("test")
    c.registrar("a")
    c.registrar("b")
    c.registrar("a")
    return c

def test_total(contador):
    assert contador.total() == 3

def test_resumen(contador):
    assert contador.resumen() == {"a": 2, "b": 1}

def test_nombre(contador):
    assert contador.nombre == "test"
```

### Fixtures con teardown (yield)

A veces el setup necesita limpieza después del test (cerrar archivos, borrar datos temporales). Usa `yield` en vez de `return`:

```python
@pytest.fixture
def archivo_temporal():
    """Crea un archivo temporal y lo elimina al terminar."""
    ruta = "test_datos.txt"
    with open(ruta, "w") as f:
        f.write("datos de prueba\n")
    yield ruta                          # <-- el test se ejecuta aqui
    import os
    os.remove(ruta)                     # <-- teardown: limpieza despues del test
```

Todo lo que está antes del `yield` es setup. Todo lo que está después es teardown. El teardown se ejecuta siempre, incluso si el test falla.

### Scopes de fixtures

Por defecto, una fixture se ejecuta **una vez por cada test** que la usa. Puedes cambiar esto con el parámetro `scope`:

```python
@pytest.fixture(scope="module")
def conexion_db():
    """Se crea una sola vez para todo el modulo de tests."""
    conn = conectar_a_db("test.db")
    yield conn
    conn.cerrar()
```

| Scope | Se ejecuta una vez por... | Uso típico |
|-------|---------------------------|------------|
| `function` (default) | Cada test | Datos que cada test puede modificar |
| `class` | Cada clase de tests | Setup compartido entre métodos |
| `module` | Cada archivo de tests | Conexiones costosas de crear |
| `session` | Toda la sesión de pytest | Recursos globales |

### `@pytest.mark.parametrize`: un test, muchos datos

Cuando quieres testear la misma lógica con datos distintos, `parametrize` evita que escribas funciones repetitivas:

```python
@pytest.mark.parametrize("entrada, esperado", [
    (0, 1),
    (1, 1),
    (5, 120),
    (10, 3628800),
])
def test_factorial(entrada, esperado):
    assert factorial(entrada) == esperado
```

Esto genera **cuatro tests separados**. En modo verbose, cada combinación aparece como un test independiente:

```
test_math.py::test_factorial[0-1] PASSED
test_math.py::test_factorial[1-1] PASSED
test_math.py::test_factorial[5-120] PASSED
test_math.py::test_factorial[10-3628800] PASSED
```

Un solo `parametrize` reemplaza cuatro funciones de test separadas. Y si necesitas agregar un caso más, es una línea en la lista.

Otro ejemplo con strings:

```python
@pytest.mark.parametrize("texto, esperado", [
    ("  hola  ", "hola"),
    ("MUNDO", "mundo"),
    ("  Python  ", "python"),
    ("", ""),
])
def test_limpiar_texto(texto, esperado):
    assert limpiar_texto(texto) == esperado
```

Puedes combinar `parametrize` con excepciones:

```python
@pytest.mark.parametrize("valor", [-1, 101, -50, 200])
def test_nota_invalida_lanza_error(valor):
    with pytest.raises(ValueError):
        clasificar_nota(valor)
```

### Marks útiles

Además de `parametrize`, pytest tiene otras marcas:

```python
@pytest.mark.skip(reason="Endpoint de la API esta caido")
def test_consultar_api():
    ...

@pytest.mark.xfail(reason="Bug conocido, issue #42")
def test_caso_borde_raro():
    ...

@pytest.mark.slow
def test_procesamiento_pesado():
    ...
```

- `skip`: salta el test (aparece como 's' en el reporte). Útil cuando algo está temporalmente roto.
- `xfail`: "expected failure". Si falla, es OK. Si pasa, te avisa. Útil para bugs conocidos que aún no arreglas.
- Marcas personalizadas como `slow`: te permiten filtrar. `pytest -m "not slow"` ejecuta todo menos los lentos.

### Organización de tests

La convención es tener un directorio `tests/` que refleje la estructura de tu paquete:

```
mi_proyecto/
├── mi_paquete/
│   ├── __init__.py
│   ├── operaciones.py
│   └── validador.py
└── tests/
    ├── conftest.py            # fixtures compartidas entre archivos
    ├── test_operaciones.py
    └── test_validador.py
```

- Un archivo de test por módulo (aproximadamente): `operaciones.py` -> `test_operaciones.py`
- **`conftest.py`**: archivo especial que pytest descubre automáticamente. Las fixtures definidas aquí están disponibles para **todos** los tests del directorio (y subdirectorios) sin necesidad de importarlas.

```python
# tests/conftest.py
import pytest

@pytest.fixture
def datos_ejemplo():
    """Disponible para TODOS los tests sin importar."""
    return {"nombre": "Ana", "edad": 25, "email": "ana@test.com"}

@pytest.fixture
def lista_numeros():
    return [1, 2, 3, 4, 5, 10, 20, 50]
```

```python
# tests/test_operaciones.py -- usa la fixture sin importar nada
def test_promedio(lista_numeros):
    assert promedio(lista_numeros) == 11.875
```

### Testing floats

Esto es clásico y te va a morder si no lo sabes:

```python
# Esto FALLA por imprecision de punto flotante:
assert 0.1 + 0.2 == 0.3  # False! (0.30000000000000004 != 0.3)

# Solucion 1: pytest.approx
assert 0.1 + 0.2 == pytest.approx(0.3)

# Solucion 2: tolerancia manual
assert abs(0.1 + 0.2 - 0.3) < 1e-9

# pytest.approx tambien funciona con listas:
assert [0.1 + 0.2, 0.3 + 0.4] == pytest.approx([0.3, 0.7])
```

Siempre que compares floats en tus tests, usa `pytest.approx`. Es más legible que la tolerancia manual.

### Cobertura de tests

La **cobertura** (coverage) mide qué porcentaje de tu código es ejecutado por los tests:

```bash
pip install pytest-cov

# Ejecutar tests con reporte de cobertura
pytest --cov=mi_paquete tests/
```

El reporte muestra algo como:

```
---------- coverage: mi_paquete ----------
Name                      Stmts   Miss  Cover
-----------------------------------------------
mi_paquete/__init__.py        2      0   100%
mi_paquete/operaciones.py    15      3    80%
mi_paquete/validador.py      22      8    64%
-----------------------------------------------
TOTAL                        39     11    72%
```

Para ver exactamente **cuáles líneas** no están cubiertas:

```bash
pytest --cov=mi_paquete --cov-report=term-missing tests/
```

La columna `Missing` muestra los números de línea sin cobertura. Eso te dice exactamente dónde agregar tests.

**Importante**: 100% de cobertura **NO** es la meta. Es posible tener 100% de cobertura y seguir teniendo bugs -- la cobertura dice qué líneas se ejecutaron, no que los resultados sean correctos. Pero baja cobertura sí significa que hay caminos de código que nunca se prueban.

---

## 4. doctest: documentación que se verifica

Los doctests son tests que viven **dentro de tus docstrings**. Las líneas `>>>` son código, y las líneas siguientes son la salida esperada:

```python
def factorial(n):
    """Calcula el factorial de n.

    Args:
        n: Entero no negativo.

    Returns:
        int: El factorial de n.

    Examples:
        >>> factorial(0)
        1
        >>> factorial(5)
        120
        >>> factorial(1)
        1
    """
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

### Ejecutar doctests

```bash
# Modo silencioso: si no imprime nada, todo paso
python -m doctest mi_modulo.py

# Modo verbose: muestra cada test
python -m doctest mi_modulo.py -v
```

También puedes ejecutarlos desde el código:

```python
if __name__ == "__main__":
    import doctest
    doctest.testmod()
```

### pytest + doctest

pytest puede ejecutar tus doctests automáticamente:

```bash
pytest --doctest-modules mi_paquete/
```

Esto busca y ejecuta todos los ejemplos `>>>` en todos los docstrings de tu paquete. Es una forma excelente de verificar que tus ejemplos de documentación siguen siendo correctos.

### Limitaciones

- La salida debe coincidir **exactamente** (espacios, orden de diccionarios, etc.)
- Difícil testear escenarios complejos o con efectos secundarios
- No tienen setup ni teardown
- El orden de llaves en un dict puede variar entre versiones de Python

Los doctests son excelentes para funciones puras con entrada/salida simple. Úsalos como **complemento** de pytest, no como reemplazo. La idea es: tus docstrings tienen ejemplos para que el usuario entienda la función, y de paso esos ejemplos se verifican automáticamente.

---

## 5. Buenas prácticas de testing

### Un test = un comportamiento

No metas 5 asserts que prueban cosas distintas en una función. Si el primer assert falla, no sabes nada sobre los otros cuatro.

```python
# MAL: un test que prueba tres cosas distintas
def test_calculadora():
    assert sumar(2, 3) == 5
    assert restar(10, 3) == 7
    assert multiplicar(4, 5) == 20

# BIEN: un test por comportamiento
def test_sumar_positivos():
    assert sumar(2, 3) == 5

def test_restar_resultado_positivo():
    assert restar(10, 3) == 7

def test_multiplicar_enteros():
    assert multiplicar(4, 5) == 20
```

### Testea comportamiento, no implementación

Si cambias la implementación interna y los tests se rompen, tus tests estaban demasiado acoplados al "cómo" en vez del "qué":

```python
# MAL: acoplado a la implementacion interna
def test_contador_usa_diccionario():
    c = Contador("test")
    c.registrar("a")
    assert c._datos == {"a": 1}  # depende del nombre del atributo privado

# BIEN: prueba el comportamiento publico
def test_contador_registra_elemento():
    c = Contador("test")
    c.registrar("a")
    assert c.total() == 1
    assert c.resumen() == {"a": 1}
```

### Qué testear

| Categoría | Ejemplo | Por qué |
|-----------|---------|---------|
| **Happy path** | Uso normal y esperado | Es lo mínimo |
| **Casos borde** | Input vacío, None, 0, negativo, un solo elemento | Aquí viven los bugs |
| **Casos de error** | Input inválido que debe lanzar excepción | Verificar que falla correctamente |
| **Valores límite** | Min, max, off-by-one | Los clásicos "uno más, uno menos" |

### Qué NO testear

- **El lenguaje**: `assert 1 + 1 == 2` no prueba tu código, prueba Python
- **Librerías de terceros**: pandas ya tiene sus propios tests
- **Código trivial**: getters/setters sin lógica, `def get_nombre(self): return self.nombre`

### Naming: el nombre del test es documentación

Un buen nombre de test describe exactamente qué verifica. Cuando falla, el nombre te dice qué se rompió sin tener que abrir el archivo:

```python
# MAL: no dice nada util
def test_1():
    ...

def test_sumar():
    ...

# BIEN: describe el escenario y la expectativa
def test_sumar_dos_positivos_retorna_suma():
    assert sumar(2, 3) == 5

def test_sumar_con_negativos_retorna_resultado_correcto():
    assert sumar(-1, -4) == -5

def test_dividir_por_cero_lanza_error():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)

def test_promedio_lista_vacia_lanza_value_error():
    with pytest.raises(ValueError):
        promedio([])
```

Patrón: `test_<funcion>_<escenario>_<resultado_esperado>`. Es largo? Sí. Pero cuando `test_dividir_por_cero_lanza_error` aparece en rojo en tu terminal, sabes exactamente qué pasó sin abrir ningún archivo.

---

## 6. CI/CD: pruebas automáticas

### Continuous Integration (CI)

La idea: cada vez que haces push o abres un pull request, un servidor ejecuta tus tests automáticamente. Si fallan, no se puede hacer merge.

**GitHub Actions** es el sistema de CI/CD integrado en GitHub. Defines un workflow en un archivo YAML:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --tb=short
```

Cada push activa el workflow: clona el repo, instala dependencias, ejecuta los tests. Si algo falla, GitHub muestra una X roja en el commit o PR.

### Continuous Deployment (CD)

La extensión natural: si los tests pasan, el código se despliega automáticamente (a un servidor, a PyPI, a una página web). No lo vamos a implementar ahora, pero el concepto es importante.

### El flujo profesional

```
Escribir codigo --> push --> CI ejecuta tests --> Verde? Merge. Rojo? Corregir.
```

**Ningún código llega a la rama principal sin pasar los tests.** Esa es la norma en cualquier equipo profesional. Te da la confianza de que `main` siempre funciona.

---

## Ejercicios

:::exercise{title="Docstrings estilo Google" difficulty="1"}

Las siguientes funciones no tienen documentación. Escribe docstrings estilo Google para cada una, incluyendo Args, Returns y al menos un Example:

```python
def limpiar_texto(texto, quitar_numeros=False):
    resultado = texto.strip().lower()
    if quitar_numeros:
        resultado = ''.join(c for c in resultado if not c.isdigit())
    return resultado


def encontrar_duplicados(lista):
    vistos = set()
    duplicados = set()
    for elemento in lista:
        if elemento in vistos:
            duplicados.add(elemento)
        vistos.add(elemento)
    return list(duplicados)


def crear_reporte(datos, titulo="Reporte", incluir_fecha=True):
    from datetime import date
    lineas = [titulo, "=" * len(titulo)]
    if incluir_fecha:
        lineas.append(f"Fecha: {date.today()}")
    for clave, valor in datos.items():
        lineas.append(f"  {clave}: {valor}")
    return "\n".join(lineas)
```

Verifica que tus docstrings funcionan ejecutando `help()` sobre cada función.

:::

:::exercise{title="Suite de tests para una Calculadora" difficulty="2"}

Dada la siguiente clase, escribe un archivo `test_calculadora.py` con al menos 8 tests usando pytest:

```python
# calculadora.py
class Calculadora:
    def __init__(self):
        self.historial = []

    def sumar(self, a, b):
        resultado = a + b
        self.historial.append(f"{a} + {b} = {resultado}")
        return resultado

    def restar(self, a, b):
        resultado = a - b
        self.historial.append(f"{a} - {b} = {resultado}")
        return resultado

    def multiplicar(self, a, b):
        resultado = a * b
        self.historial.append(f"{a} * {b} = {resultado}")
        return resultado

    def dividir(self, a, b):
        if b == 0:
            raise ValueError("No se puede dividir entre cero")
        resultado = a / b
        self.historial.append(f"{a} / {b} = {resultado}")
        return resultado

    def limpiar_historial(self):
        self.historial = []
```

Tus tests deben cubrir:

1. `sumar` con positivos y negativos
2. `restar` verificando el orden de los operandos
3. `multiplicar` por cero
4. `dividir` caso normal y división entre cero (con `pytest.raises`)
5. Que el historial se actualiza correctamente
6. Que `limpiar_historial` funciona
7. Usa una fixture para crear la Calculadora
8. Usa `parametrize` en al menos un test

Ejecuta con `pytest -v` y verifica que todos pasan.

:::

:::exercise{title="Encuentra el bug con tests" difficulty="3"}

La siguiente función tiene un bug. No lo arregles todavía -- primero **escribe tests que expongan el bug**. Tu misión:

1. Escribe al menos 5 tests para `calcular_descuento`, cubriendo happy path, casos borde y valores límite
2. Al menos uno de tus tests debe **fallar** (exponer el bug)
3. Una vez que identifiques el bug, arréglalo y verifica que todos los tests pasen

```python
def calcular_descuento(precio, porcentaje):
    """Aplica un descuento porcentual al precio.

    Args:
        precio: Precio original (debe ser >= 0).
        porcentaje: Porcentaje de descuento (0-100).

    Returns:
        float: Precio con descuento aplicado.

    Raises:
        ValueError: Si precio es negativo o porcentaje fuera de rango.
    """
    if precio < 0:
        raise ValueError("El precio no puede ser negativo")
    if porcentaje < 0 or porcentaje > 100:
        raise ValueError("El porcentaje debe estar entre 0 y 100")
    return precio * (1 - porcentaje)
```

**Pista**: piensa en qué unidad está el porcentaje y qué unidad espera la fórmula.

:::

:::exercise{title="Parametrize a fondo" difficulty="2"}

Escribe una función `clasificar_nota(nota)` que recibe un número del 0 al 100 y retorna:

- `"Reprobado"` si nota < 60
- `"Suficiente"` si 60 <= nota < 70
- `"Bien"` si 70 <= nota < 80
- `"Notable"` si 80 <= nota < 90
- `"Excelente"` si 90 <= nota <= 100
- Lanza `ValueError` si nota < 0 o nota > 100

Ahora escribe tests usando `@pytest.mark.parametrize` con al menos estas combinaciones:

| nota | resultado esperado |
|------|--------------------|
| 0 | "Reprobado" |
| 59 | "Reprobado" |
| 60 | "Suficiente" |
| 75 | "Bien" |
| 85 | "Notable" |
| 90 | "Excelente" |
| 100 | "Excelente" |

Agrega un test parametrizado separado para los valores inválidos (-1, 101, -50, 200) que verifique el `ValueError`.

:::

:::prompt{title="Generar tests para una función" for="ChatGPT/Claude"}

Tengo la siguiente función de Python:

```python
[pega tu funcion aqui, con su docstring]
```

Genera tests exhaustivos usando pytest que cubran:

1. El caso de uso normal (happy path)
2. Casos borde (entrada vacía, None, cero, valores negativos, un solo elemento)
3. Casos de error (qué excepciones debería lanzar con inputs inválidos)
4. Usa `@pytest.mark.parametrize` donde tenga sentido para no repetir lógica
5. Usa una `@pytest.fixture` si varios tests necesitan el mismo setup
6. Cada test debe tener un nombre descriptivo que diga qué verifica

Explica brevemente por qué elegiste cada caso de prueba.

:::
