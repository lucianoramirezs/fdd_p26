# Repaso: Ingeniería de Software en Python

> **Notebook interactivo**: todo el código de esta sección está en un notebook ejecutable.
> [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/11_python_intermedio/code/01_repaso_ingenieria.ipynb)

Esto es un **repaso rápido**. Ya viste estos conceptos en el curso de DataCamp. Aquí los consolidamos con ejemplos concretos que vas a necesitar para diseñar tu librería.

---

## 1. Paquetes y módulos

Un **módulo** es un archivo `.py`. Un **paquete** es un directorio con un archivo `__init__.py`.

```
mi_paquete/
├── __init__.py       ← hace que el directorio sea un paquete
├── operaciones.py    ← módulo
└── utilidades.py     ← módulo
```

### `__init__.py`: la puerta de entrada

Este archivo se ejecuta cuando alguien hace `import mi_paquete`. Su trabajo principal es **definir qué se exporta**:

```python
# mi_paquete/__init__.py
from .operaciones import sumar, restar
from .utilidades import formatear

# Ahora el usuario puede hacer:
# from mi_paquete import sumar
# en vez de:
# from mi_paquete.operaciones import sumar
```

El punto en `.operaciones` es un **import relativo** — significa "el módulo `operaciones` dentro de este mismo paquete".

### ¿Cuándo crear un módulo nuevo?

- **Un módulo** = un grupo de funciones/clases **relacionadas entre sí**
- Si un módulo tiene más de ~200 líneas, probablemente hace demasiadas cosas
- Si dos funciones se usan siempre juntas, van en el mismo módulo
- Si puedes describir el módulo con **una frase**, es buen tamaño

### Ejemplo mínimo

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

```python
# uso
from mi_paquete import sumar, formatear

resultado = sumar(3.14159, 2.71828)
print(formatear(resultado))  # "5.86"
```

---

## 2. Clases

Una clase agrupa **datos** (atributos) y **comportamiento** (métodos) en una sola unidad.

### ¿Cuándo usar una clase vs funciones sueltas?

| Usa funciones cuando... | Usa una clase cuando... |
|-------------------------|------------------------|
| No hay estado compartido entre llamadas | Hay datos que persisten entre operaciones |
| Las operaciones son independientes | Las operaciones trabajan sobre los mismos datos |
| Son 3-5 funciones simples | Los datos + operaciones forman un **concepto** |

### Anatomía de una clase

```python
class Contador:
    """Cuenta eventos por categoría."""

    def __init__(self, nombre):
        """Inicializa el contador con un nombre."""
        self.nombre = nombre
        self._conteos = {}  # ← convención: _ = uso interno

    def registrar(self, categoria):
        """Registra un evento en la categoría dada."""
        self._conteos[categoria] = self._conteos.get(categoria, 0) + 1

    def total(self):
        """Retorna el total de eventos registrados."""
        return sum(self._conteos.values())

    def resumen(self):
        """Retorna el conteo por categoría."""
        return dict(self._conteos)
```

```python
c = Contador("errores web")
c.registrar("404")
c.registrar("500")
c.registrar("404")
print(c.total())     # 3
print(c.resumen())   # {"404": 2, "500": 1}
```

### Convenciones importantes

- `self` = la instancia. Siempre es el primer parámetro de un método.
- `__init__` = el constructor. Se llama automáticamente al crear la instancia.
- `_nombre` = convención de "uso interno". Python no lo impide, pero dice "no toques esto desde fuera".
- `__nombre` = name mangling. Python lo renombra a `_Clase__nombre`. Rara vez necesario.

### Herencia: compartir comportamiento

```python
class FuenteDatos:
    """Base para cualquier fuente de datos."""

    def __init__(self, nombre):
        self.nombre = nombre

    def leer(self):
        raise NotImplementedError("Cada fuente debe implementar leer()")

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.nombre}')"


class FuenteCSV(FuenteDatos):
    """Lee datos desde un archivo CSV."""

    def __init__(self, nombre, ruta):
        super().__init__(nombre)  # llama al __init__ del padre
        self.ruta = ruta

    def leer(self):
        with open(self.ruta) as f:
            return f.readlines()


class FuenteAPI(FuenteDatos):
    """Lee datos desde una API REST."""

    def __init__(self, nombre, url):
        super().__init__(nombre)
        self.url = url

    def leer(self):
        import requests
        return requests.get(self.url).json()
```

**¿Por qué herencia aquí?** Porque `FuenteCSV` y `FuenteAPI` comparten el concepto de "fuente de datos con nombre que puede leerse". El padre define el **contrato** (`leer()`), los hijos lo implementan.

**¿Cuándo NO usar herencia?** Si la relación no es "X **es un tipo de** Y", probablemente no necesitas herencia. Una `FuenteCSV` **es un tipo de** `FuenteDatos`. Un `Carro` **no es un tipo de** `Motor` — un carro **tiene** un motor (composición, no herencia).

---

## 3. Documentación

### Docstrings: documentación que vive en el código

```python
def buscar(texto, patron, ignorar_caso=False):
    """Busca un patrón en el texto y retorna las coincidencias.

    Args:
        texto: El string donde buscar.
        patron: El patrón a buscar (string o regex).
        ignorar_caso: Si True, la búsqueda no distingue mayúsculas.

    Returns:
        Lista de strings con las coincidencias encontradas.

    Raises:
        ValueError: Si el patrón está vacío.
    """
```

Este formato se llama **Google style**. Es el más legible. La alternativa es **NumPy style** (usa secciones con guiones). Elige uno y sé consistente en todo tu proyecto.

### `help()` y `dir()`: introspección gratis

```python
help(buscar)       # muestra el docstring formateado
dir(mi_objeto)     # lista todos los atributos y métodos
```

Cuando escribes buenos docstrings, `help()` se convierte en la documentación de tu librería **sin esfuerzo extra**.

### ¿Cuándo documentar?

- **Siempre**: funciones/clases públicas (las que importa el usuario)
- **A veces**: funciones internas complejas
- **Nunca**: cosas obvias (`x = x + 1  # incrementa x` no aporta nada)

---

## 4. Testing

### pytest: un test = un comportamiento

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

Ejecutar:

```bash
pytest tests/
# ✓ test_sumar_positivos PASSED
# ✓ test_sumar_negativos PASSED
# ✓ test_restar PASSED
```

### Convenciones de pytest

- Archivos de test empiezan con `test_`
- Funciones de test empiezan con `test_`
- Usa `assert` para verificar resultados
- Un test verifica **una sola cosa**
- El nombre del test dice **qué comportamiento verifica**

### doctest: documentación que se verifica

```python
def sumar(a, b):
    """Suma dos números.

    >>> sumar(2, 3)
    5
    >>> sumar(-1, 1)
    0
    """
    return a + b
```

```bash
python -m doctest mi_paquete/operaciones.py
# Sin output = todo pasó
```

Los doctests son ejemplos en el docstring que Python puede ejecutar. Son útiles para funciones simples — documentan **y** verifican al mismo tiempo.

### ¿pytest o doctest?

| doctest | pytest |
|---------|--------|
| Ejemplos simples en el docstring | Tests completos y organizados |
| Documentación que no se pudre | Lógica de test compleja |
| Funciones puras con inputs/outputs claros | Edge cases, setup/teardown, fixtures |
| **Complemento** | **Base** |

Usa ambos: doctest para los ejemplos del docstring, pytest para los tests reales.

---

:::exercise{title="Verificación rápida" difficulty="1"}

Sin ver el material de arriba, responde:

1. ¿Qué archivo necesita un directorio para ser un paquete de Python?
2. ¿Cuál es la diferencia entre `_metodo` y `metodo` en una clase?
3. ¿Qué hace `super().__init__()`?
4. ¿Cómo ejecutas todos los tests de un directorio con pytest?
5. ¿Para qué sirve un docstring?

Si no pudiste responder alguna, vuelve a la sección correspondiente.

:::

:::exercise{title="Mini-paquete" difficulty="2"}

Crea un paquete llamado `calculadora` con esta estructura:

```
calculadora/
├── __init__.py
├── basica.py        # sumar, restar, multiplicar, dividir
└── estadistica.py   # promedio, mediana
```

1. Implementa las funciones (mantén cada una en 1-3 líneas)
2. En `__init__.py`, exporta todo para que el usuario pueda hacer `from calculadora import promedio`
3. Agrega un docstring con ejemplo a cada función
4. Crea `tests/test_calculadora.py` con al menos un test por función
5. Ejecuta `pytest` y verifica que todo pase

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
2. ¿Los imports en `__init__.py` son correctos?
3. ¿Hay algo que un usuario encontraría confuso?

:::
