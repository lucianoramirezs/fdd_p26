# Fundamentos de Python

> **Notebook interactivo**: este tema tiene un notebook con ejemplos ejecutables y explicaciones más profundas sobre memoria, el intérprete, y patrones eficientes.
> <a href="https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/09_python/code/02_fundamentos.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>

Ahora sí, vamos a escribir código. Esta sección cubre lo esencial: tipos de datos, variables, operadores, condicionales y ciclos. Si ya programaste en otro lenguaje, esto va a ser rápido — la sintaxis de Python es deliberadamente minimalista.

> **Puedes probar todo** en el REPL (`python3`) o en un script (`.py`). Si es algo corto, el REPL es más rápido. Si son más de 5 líneas, usa un script.

---

## Variables y asignación

En Python no declaras tipos. Simplemente asignas un valor a un nombre:

```python
x = 42
nombre = "Ana"
pi = 3.14159
activo = True
```

Python infiere el tipo por el valor. No necesitas escribir `int x = 42` como en Java o C.

### Reglas para nombres de variables

- Letras, números y guiones bajos: `mi_variable`, `dato_2`, `_privado`
- **No** pueden empezar con número: `2dato` es inválido
- **No** pueden ser palabras reservadas: `if`, `for`, `class`, `return`, etc.
- Python es **case-sensitive**: `nombre` y `Nombre` son variables diferentes

### Convención: snake_case

En Python la convención es `snake_case` para variables y funciones:

```python
# ✅ Correcto (snake_case)
mi_variable = 10
nombre_completo = "Ana García"

# ❌ Incorrecto (camelCase — eso es JavaScript)
miVariable = 10
nombreCompleto = "Ana García"
```

---

## Tipos de datos básicos

Python tiene cuatro tipos **escalares** (un solo valor) y dos tipos **colección** (múltiples valores) que vas a usar todo el tiempo.

### int — números enteros

```python
>>> edad = 25
>>> poblacion = 130_000_000  # los guiones bajos son separadores visuales
>>> negativo = -42
>>> type(edad)
<class 'int'>
```

Los enteros en Python no tienen límite de tamaño. Puedes calcular `2 ** 1000` sin problemas.

### float — números decimales

```python
>>> pi = 3.14159
>>> temperatura = -5.2
>>> cientifico = 6.022e23   # notación científica: 6.022 × 10²³
>>> type(pi)
<class 'float'>
```

> **Cuidado con floats**: `0.1 + 0.2` da `0.30000000000000004`, no `0.3`. Esto no es un bug de Python — es cómo funciona la aritmética de punto flotante en **todas** las computadoras. Para dinero o precisión exacta, usa el módulo `decimal`.

### str — cadenas de texto

```python
>>> saludo = "Hola, mundo"
>>> otro = 'También funciona con comillas simples'
>>> multilinea = """Este string
... tiene varias
... líneas"""
>>> type(saludo)
<class 'str'>
```

Los strings son **inmutables** — no puedes cambiar un carácter individual. Si necesitas modificar un string, creas uno nuevo.

#### Operaciones con strings

```python
>>> "Hola" + " " + "mundo"        # concatenación
'Hola mundo'
>>> "ja" * 3                       # repetición
'jajaja'
>>> len("Python")                  # longitud
6
>>> "python".upper()               # mayúsculas
'PYTHON'
>>> "  hola  ".strip()             # quitar espacios
'hola'
>>> "hola mundo".split()           # dividir en lista
['hola', 'mundo']
>>> "a,b,c".split(",")            # dividir por coma
['a', 'b', 'c']
```

#### f-strings: interpolación de variables

La forma moderna de incluir variables en strings:

```python
nombre = "Ana"
edad = 25
print(f"Me llamo {nombre} y tengo {edad} años")
# Me llamo Ana y tengo 25 años

# Puedes poner expresiones dentro de las llaves
print(f"En 10 años tendré {edad + 10} años")
# En 10 años tendré 35 años
```

La `f` antes de las comillas activa la interpolación. Todo lo que esté entre `{}` se evalúa como código Python.

### bool — verdadero o falso

```python
>>> activo = True
>>> eliminado = False
>>> type(activo)
<class 'bool'>
```

Solo dos valores posibles: `True` y `False` (con mayúscula inicial).

#### Valores "truthy" y "falsy"

En Python, muchos valores se evalúan como `True` o `False` en contextos booleanos:

| Falsy (se evalúa como False) | Truthy (se evalúa como True) |
|------------------------------|------------------------------|
| `False` | `True` |
| `0`, `0.0` | Cualquier otro número |
| `""` (string vacío) | Cualquier string no vacío |
| `[]` (lista vacía) | Lista con elementos |
| `{}` (dict vacío) | Dict con elementos |
| `None` | Casi todo lo demás |

Esto es útil para verificaciones rápidas:

```python
nombre = ""
if nombre:
    print(f"Hola, {nombre}")
else:
    print("No se proporcionó nombre")
# No se proporcionó nombre
```

### list — listas ordenadas

Una lista es una colección **ordenada** y **mutable** de elementos:

```python
>>> numeros = [1, 2, 3, 4, 5]
>>> nombres = ["Ana", "Luis", "María"]
>>> mezcla = [1, "dos", 3.0, True]   # puede mezclar tipos
>>> vacia = []
>>> type(numeros)
<class 'list'>
```

#### Operaciones con listas

```python
# Acceso por índice (empieza en 0)
>>> numeros[0]
1
>>> numeros[-1]       # último elemento
5

# Slicing
>>> numeros[1:3]      # del índice 1 al 2 (no incluye el 3)
[2, 3]
>>> numeros[:3]       # primeros 3
[1, 2, 3]
>>> numeros[2:]       # del 2 en adelante
[3, 4, 5]

# Modificar
>>> numeros[0] = 99
>>> numeros
[99, 2, 3, 4, 5]

# Agregar
>>> numeros.append(6)       # al final
>>> numeros.insert(0, 0)    # en posición específica

# Eliminar
>>> numeros.remove(99)      # por valor
>>> numeros.pop()            # último elemento
>>> del numeros[0]           # por índice

# Longitud
>>> len(numeros)
4

# Ordenar
>>> [3, 1, 2].sort()        # in-place (modifica la lista)
>>> sorted([3, 1, 2])       # retorna nueva lista ordenada
[1, 2, 3]

# Verificar si un elemento existe
>>> 3 in [1, 2, 3]
True
```

### dict — diccionarios (clave-valor)

Un diccionario mapea **claves** a **valores**. Es la estructura más útil de Python:

```python
>>> persona = {
...     "nombre": "Ana",
...     "edad": 25,
...     "ciudad": "CDMX"
... }
>>> type(persona)
<class 'dict'>
```

#### Operaciones con diccionarios

```python
# Acceso por clave
>>> persona["nombre"]
'Ana'

# Acceso seguro (retorna None si no existe)
>>> persona.get("telefono")
None
>>> persona.get("telefono", "no disponible")
'no disponible'

# Agregar o modificar
>>> persona["email"] = "ana@mail.com"
>>> persona["edad"] = 26

# Eliminar
>>> del persona["ciudad"]

# Verificar si una clave existe
>>> "nombre" in persona
True

# Obtener claves y valores
>>> persona.keys()
dict_keys(['nombre', 'edad', 'email'])
>>> persona.values()
dict_values(['Ana', 26, 'ana@mail.com'])
>>> persona.items()
dict_items([('nombre', 'Ana'), ('edad', 26), ('email', 'ana@mail.com')])

# Longitud
>>> len(persona)
3
```

### Tabla resumen de tipos

| Tipo | Ejemplo | Mutable | Uso típico |
|------|---------|---------|------------|
| `int` | `42` | — | Conteos, índices |
| `float` | `3.14` | — | Cálculos numéricos |
| `str` | `"hola"` | No | Texto, nombres, IDs |
| `bool` | `True` | — | Condiciones, flags |
| `list` | `[1, 2, 3]` | Sí | Colecciones ordenadas |
| `dict` | `{"a": 1}` | Sí | Mapeos clave-valor, registros |

---

## Operadores

### Aritméticos

```python
>>> 7 + 3      # suma: 10
>>> 7 - 3      # resta: 4
>>> 7 * 3      # multiplicación: 21
>>> 7 / 3      # división (siempre float): 2.3333...
>>> 7 // 3     # división entera: 2
>>> 7 % 3      # módulo (residuo): 1
>>> 7 ** 3     # potencia: 343
```

### Comparación

```python
>>> 5 == 5     # igual: True
>>> 5 != 3     # diferente: True
>>> 5 > 3      # mayor que: True
>>> 5 < 3      # menor que: False
>>> 5 >= 5     # mayor o igual: True
>>> 5 <= 3     # menor o igual: False
```

### Lógicos

```python
>>> True and False    # AND: False
>>> True or False     # OR: True
>>> not True          # NOT: False
```

Combinaciones comunes:

```python
edad = 25
if edad >= 18 and edad < 65:
    print("Edad laboral")
```

---

## Condicionales: if, elif, else

Python usa **indentación** (espacios) para definir bloques de código. No hay llaves `{}` ni `end` — la indentación **es** la estructura.

```python
edad = 20

if edad < 18:
    print("Menor de edad")
elif edad < 65:
    print("Adulto")
else:
    print("Adulto mayor")
```

> **IMPORTANTE**: la indentación estándar en Python es **4 espacios**. No uses tabs. Configura tu editor para que Tab inserte 4 espacios.

### Reglas

1. La condición va después de `if` / `elif`, seguida de **`:`**
2. El bloque indentado se ejecuta si la condición es `True`
3. `elif` es la abreviación de "else if" — puedes tener cuantos quieras
4. `else` es opcional — se ejecuta si ninguna condición fue `True`
5. Python evalúa **de arriba a abajo** y ejecuta el **primer** bloque cuya condición sea `True`

### Ejemplos

```python
# Simple
x = 10
if x > 0:
    print("Positivo")

# Con else
temperatura = -5
if temperatura > 0:
    print("Sobre cero")
else:
    print("Bajo cero")

# Con elif
nota = 85
if nota >= 90:
    print("A")
elif nota >= 80:
    print("B")
elif nota >= 70:
    print("C")
else:
    print("F")
# B

# Condiciones compuestas
edad = 25
tiene_id = True
if edad >= 18 and tiene_id:
    print("Puede entrar")
```

### Indentación incorrecta = error

```python
# ❌ Esto da IndentationError
if True:
print("mal")

# ❌ Esto también (mezcla de espacios e indentación)
if True:
    print("línea 1")
      print("línea 2")  # indentación inconsistente

# ✅ Correcto
if True:
    print("línea 1")
    print("línea 2")
```

---

## Ciclos: for y while

### for — iterar sobre una secuencia

`for` recorre cada elemento de una secuencia (lista, string, rango, etc.):

```python
# Recorrer una lista
frutas = ["manzana", "naranja", "plátano"]
for fruta in frutas:
    print(fruta)
# manzana
# naranja
# plátano

# Recorrer un string
for letra in "Python":
    print(letra)
# P, y, t, h, o, n (cada una en su línea)

# range(): generar secuencias de números
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 8):       # 2, 3, 4, 5, 6, 7
    print(i)

for i in range(0, 10, 2):   # 0, 2, 4, 6, 8  (de 2 en 2)
    print(i)
```

### Patrones comunes con for

```python
# Sumar elementos
numeros = [10, 20, 30, 40]
total = 0
for n in numeros:
    total += n
print(total)  # 100

# Filtrar elementos
edades = [15, 22, 17, 30, 12]
adultos = []
for edad in edades:
    if edad >= 18:
        adultos.append(edad)
print(adultos)  # [22, 30]

# Recorrer un diccionario
persona = {"nombre": "Ana", "edad": 25, "ciudad": "CDMX"}
for clave, valor in persona.items():
    print(f"{clave}: {valor}")
# nombre: Ana
# edad: 25
# ciudad: CDMX

# enumerate: obtener índice y valor
frutas = ["manzana", "naranja", "plátano"]
for i, fruta in enumerate(frutas):
    print(f"{i}: {fruta}")
# 0: manzana
# 1: naranja
# 2: plátano
```

### while — repetir mientras una condición sea verdadera

```python
contador = 0
while contador < 5:
    print(contador)
    contador += 1
# 0, 1, 2, 3, 4
```

> **Cuidado con ciclos infinitos**: si la condición nunca se vuelve `False`, el ciclo corre para siempre. Usa `Ctrl+C` para interrumpirlo.

```python
# ❌ Ciclo infinito (falta incrementar el contador)
x = 0
while x < 10:
    print(x)
    # x nunca cambia → imprime 0 para siempre
```

### break y continue

```python
# break: salir del ciclo inmediatamente
for i in range(100):
    if i == 5:
        break
    print(i)
# 0, 1, 2, 3, 4

# continue: saltar a la siguiente iteración
for i in range(10):
    if i % 2 == 0:
        continue    # salta los pares
    print(i)
# 1, 3, 5, 7, 9
```

### ¿for o while?

| Usa `for` cuando... | Usa `while` cuando... |
|---------------------|-----------------------|
| Sabes cuántas iteraciones hay | No sabes cuántas iteraciones |
| Recorres una colección | Esperas una condición |
| Usas `range()` | Lees input del usuario |
| **90% de los casos** | Casos especiales |

En ciencia de datos, `for` se usa mucho más que `while`.

---

## Funciones

Una función es un bloque de código reutilizable. Se define con `def`:

```python
def saludar(nombre):
    print(f"Hola, {nombre}!")

saludar("Ana")     # Hola, Ana!
saludar("Luis")    # Hola, Luis!
```

### Retornar valores

```python
def sumar(a, b):
    return a + b

resultado = sumar(3, 4)
print(resultado)  # 7
```

Sin `return`, la función retorna `None` implícitamente.

### Valores por defecto

```python
def saludar(nombre, saludo="Hola"):
    print(f"{saludo}, {nombre}!")

saludar("Ana")              # Hola, Ana!
saludar("Ana", "Buenos días")  # Buenos días, Ana!
```

### Múltiples valores de retorno

Python puede retornar varios valores a la vez usando tuplas:

```python
def min_max(numeros):
    return min(numeros), max(numeros)

minimo, maximo = min_max([3, 1, 4, 1, 5, 9])
print(f"Mín: {minimo}, Máx: {maximo}")
# Mín: 1, Máx: 9
```

---

## None

`None` es el valor "vacío" de Python. Es el equivalente a `null` en otros lenguajes:

```python
resultado = None

if resultado is None:
    print("No hay resultado")
```

> Usa `is None` / `is not None`, **no** `== None`. Es la convención de Python y es técnicamente más correcto.

---

## Conversión de tipos

Python no convierte tipos automáticamente en la mayoría de los casos. Necesitas hacerlo explícitamente:

```python
# String a número
>>> int("42")
42
>>> float("3.14")
3.14

# Número a string
>>> str(42)
'42'

# Lista de tupla
>>> list((1, 2, 3))
[1, 2, 3]

# String a lista de caracteres
>>> list("hola")
['h', 'o', 'l', 'a']

# Error si la conversión no tiene sentido
>>> int("hola")
ValueError: invalid literal for int() with base 10: 'hola'
```

---

## Por dentro: cómo funciona Python

Esta sección va más profundo. No necesitas memorizar esto, pero entenderlo te va a ahorrar horas de debugging y te va a hacer escribir mejor código.

> **Todo lo de esta sección está en el notebook con código ejecutable.** Si prefieres aprender ejecutando, abre el notebook en Colab.

### Todo es un objeto

En Python, **absolutamente todo** es un objeto: números, strings, listas, funciones, clases, módulos. Cada objeto tiene tres cosas:

| Propiedad | Qué es | Cómo verla |
|-----------|--------|------------|
| **Identidad** | Dirección en memoria (fija) | `id(x)` |
| **Tipo** | Qué operaciones soporta | `type(x)` |
| **Valor** | El dato en sí | `print(x)` |

Cuando escribes `x = 42`, Python crea un **objeto** `int` con valor `42` en memoria y pega la **etiqueta** `x` a ese objeto. La variable `x` **no contiene** el 42 — es un **post-it** pegado al objeto.

Esto significa que `b = a` no copia el valor — pega otra etiqueta al **mismo objeto**:

```python
a = [1, 2, 3]
b = a           # b apunta al MISMO objeto

a.append(4)
print(b)        # [1, 2, 3, 4] — ¡b también cambió!
```

Esto se llama **aliasing** y es fuente de muchos bugs.

### `is` vs `==`

- `==` compara **valores** — ¿tienen el mismo contenido?
- `is` compara **identidad** — ¿son el **mismo objeto** en memoria?

```python
lista1 = [1, 2, 3]
lista2 = [1, 2, 3]    # mismo contenido, objeto DIFERENTE

lista1 == lista2       # True  (mismo valor)
lista1 is lista2       # False (objetos diferentes)
```

**Regla**: siempre usa `==` para comparar valores. Solo usa `is` para comparar con `None`.

### Mutabilidad e inmutabilidad

| Inmutables | Mutables |
|------------|----------|
| `int`, `float`, `str`, `bool`, `tuple` | `list`, `dict`, `set` |
| Reasignar = crear nuevo objeto | Modificar = mismo objeto cambia |

```python
# Inmutable: x = x + 1 crea un NUEVO int
x = 10
id_antes = id(x)
x = x + 1
id_despues = id(x)
# id_antes != id_despues — son objetos diferentes

# Mutable: append modifica el MISMO objeto
nums = [1, 2, 3]
id_antes = id(nums)
nums.append(4)
# id(nums) == id_antes — mismo objeto
```

### Copias: shallow vs deep

```python
import copy

original = [1, 2, [3, 4]]

alias   = original            # NO copia — misma referencia
shallow = original.copy()     # Copia la lista exterior, pero las sublistas son compartidas
deep    = copy.deepcopy(original)  # Copia TODO recursivamente

original[2].append(5)
# alias   → [1, 2, [3, 4, 5]]  (mismo objeto)
# shallow → [1, 2, [3, 4, 5]]  (sublista compartida — ¡sorpresa!)
# deep    → [1, 2, [3, 4]]     (copia independiente)
```

**Regla**: si tu estructura tiene listas dentro de listas (o dicts dentro de listas), usa `copy.deepcopy()`.

### Paso de argumentos: pass by object reference

Python no es "pass by value" ni "pass by reference". Es **pass by object reference**: el parámetro apunta al **mismo objeto** que el argumento.

- Con **inmutables** (int, str): parece "pass by value" porque no puedes modificar el objeto original
- Con **mutables** (list, dict): parece "pass by reference" porque modificas el objeto original

```python
def agregar(lista, elem):
    lista.append(elem)   # modifica el MISMO objeto

mi_lista = [1, 2, 3]
agregar(mi_lista, 4)
print(mi_lista)          # [1, 2, 3, 4] — ¡cambió!
```

### El bug clásico: mutable default argument

```python
# ❌ MAL: lista como valor por defecto
def agregar(elem, lista=[]):
    lista.append(elem)
    return lista

print(agregar(1))    # [1]
print(agregar(2))    # [1, 2]  ← ¡se acumuló!
print(agregar(3))    # [1, 2, 3]

# ✅ BIEN: usar None
def agregar(elem, lista=None):
    if lista is None:
        lista = []
    lista.append(elem)
    return lista
```

Los valores por defecto se evalúan **una sola vez** cuando se define la función. Si es un objeto mutable, todas las llamadas comparten el mismo objeto.

### Memoria: ¿cuánto pesa cada tipo?

Cada objeto Python tiene un **header** de 16 bytes mínimo: 8 bytes para el conteo de referencias (garbage collection) y 8 bytes para el puntero al tipo. Encima de eso va el valor.

```python
import sys
sys.getsizeof(None)     # 16 bytes — solo el header, sin datos
sys.getsizeof(0)        # 24 bytes — header + metadata de tamaño
sys.getsizeof(42)       # 28 bytes — header + 1 dígito de 30 bits
sys.getsizeof(2**100)   # 40 bytes — header + 4 dígitos (crece)
sys.getsizeof(3.14)     # 24 bytes — header + double de C (siempre fijo)
sys.getsizeof(True)     # 28 bytes — bool es subclase de int
sys.getsizeof("")       # 49 bytes — header + metadata de string
sys.getsizeof("hola")   # 53 bytes — 49 + 4 caracteres ASCII
```

- **int**: CPython almacena enteros como arrays de dígitos de 30 bits. 42 cabe en 1 dígito (28 bytes), 2^100 necesita 4 dígitos (40 bytes). Crecen sin límite.
- **float**: siempre 24 bytes — un `double` de C (8 bytes) + header (16). No crece.
- **str**: 49 bytes base + 1 byte por carácter ASCII. Caracteres Unicode usan 2 o 4 bytes cada uno.
- **None**: 16 bytes — el objeto más ligero posible.

Un `int` de C son 4 bytes. Un `int` de Python son **28+ bytes** (7x más). Este es el precio de "todo es un objeto". Para ciencia de datos usamos `numpy`/`pandas` que almacenan datos en arrays nativos de C, sin este overhead.

### El intérprete CPython y bytecode

Cuando ejecutas `python3 script.py`:
1. El código se **compila a bytecode** (archivos `.pyc`)
2. La **VM de Python** ejecuta el bytecode instrucción por instrucción

Puedes ver el bytecode con `dis`:

```python
import dis
def sumar(a, b):
    return a + b
dis.dis(sumar)
# LOAD_FAST    0 (a)
# LOAD_FAST    1 (b)
# BINARY_ADD
# RETURN_VALUE
```

Esto explica por qué las **list comprehensions son más rápidas** que loops con `.append()` — generan menos instrucciones de bytecode y usan operaciones optimizadas en C.

### El GIL (Global Interpreter Lock)

El **GIL** es un mutex en CPython que solo permite que **un thread** ejecute bytecode a la vez. Existe porque el conteo de referencias no es thread-safe.

**Implicaciones prácticas:**
- **Threads NO dan paralelismo** para trabajo CPU-bound
- **Threads SÍ sirven** para I/O-bound (red, disco) porque liberan el GIL durante la espera
- Para paralelismo CPU real: usa `multiprocessing`

En ciencia de datos normalmente no te afecta porque `numpy`, `pandas` y similares **liberan el GIL** internamente.

### Buenos y malos patrones

| Malo | Bueno | ¿Por qué? |
|------|-------|------------|
| `s += "x"` en loop | `"".join(lista)` | O(n²) vs O(n) |
| loop + `.append()` | List comprehension | Menos bytecode |
| `x in lista` (búsqueda) | `x in set` | O(n) vs O(1) |
| `list.insert(0, x)` | `collections.deque.appendleft(x)` | O(n) vs O(1) |
| `range(len(x))` | `enumerate(x)` | Más legible |
| `def f(x=[])` | `def f(x=None)` | Bug vs correcto |

---

## Errores comunes para principiantes

| Error | Causa | Solución |
|-------|-------|----------|
| `IndentationError` | Indentación inconsistente | Usa siempre 4 espacios |
| `NameError: name 'x' is not defined` | Variable no existe | Verifica el nombre, ¿la definiste antes? |
| `TypeError: can only concatenate str to str` | Mezclaste tipos con `+` | Usa `f""` o convierte con `str()` |
| `IndexError: list index out of range` | Accediste a un índice que no existe | Verifica con `len()` primero |
| `KeyError: 'clave'` | La clave no existe en el dict | Usa `.get()` en vez de `[]` |
| `SyntaxError` | Olvidaste `:`, cerraste mal comillas, etc. | Lee el mensaje de error, señala la línea |

---

:::exercise{title="Tipos y variables" difficulty="1"}

En el REPL, ejecuta lo siguiente y **predice el resultado antes de presionar Enter**:

```python
>>> type(42)
>>> type(42.0)
>>> type("42")
>>> type(True)
>>> type([1, 2, 3])
>>> type({"a": 1})
```

Ahora prueba estas operaciones:

```python
>>> "3" + "4"
>>> 3 + 4
>>> "3" * 4
>>> 3 * "4"
```

¿Por qué `"3" + "4"` no da `7`?

:::

:::exercise{title="Control de flujo" difficulty="1"}

Crea un archivo `notas.py` con el siguiente código:

```python
notas = [85, 92, 67, 74, 95, 88, 71, 60, 99, 43]

for nota in notas:
    if nota >= 90:
        letra = "A"
    elif nota >= 80:
        letra = "B"
    elif nota >= 70:
        letra = "C"
    elif nota >= 60:
        letra = "D"
    else:
        letra = "F"
    print(f"Nota: {nota} → {letra}")
```

Ejecútalo con `python3 notas.py`.

Ahora **modifícalo** para que además cuente cuántos alumnos aprobaron (nota >= 60) y cuántos reprobaron:

```bash
python3 notas.py
# Nota: 85 → B
# Nota: 92 → A
# ...
# Aprobados: 9
# Reprobados: 1
```

:::

:::exercise{title="Listas y diccionarios" difficulty="2"}

Crea un archivo `estudiantes.py`:

```python
estudiantes = [
    {"nombre": "Ana", "edad": 22, "carrera": "Actuaría"},
    {"nombre": "Luis", "edad": 21, "carrera": "Economía"},
    {"nombre": "María", "edad": 23, "carrera": "Actuaría"},
    {"nombre": "Carlos", "edad": 20, "carrera": "Matemáticas"},
    {"nombre": "Sofía", "edad": 22, "carrera": "Economía"},
]
```

Usando `for`, `if`, listas y diccionarios, escribe código que:

1. Imprima el nombre de cada estudiante y su carrera
2. Cuente cuántos estudiantes hay por carrera (usa un diccionario para contar)
3. Encuentre al estudiante más joven
4. Filtre solo los estudiantes de Actuaría en una nueva lista

:::

:::exercise{title="Funciones" difficulty="2"}

Crea un archivo `funciones.py` con las siguientes funciones:

1. `es_par(n)` — retorna `True` si `n` es par, `False` si no
2. `promedio(numeros)` — recibe una lista de números y retorna su promedio
3. `contar_vocales(texto)` — retorna cuántas vocales tiene un string

Prueba cada función:

```python
print(es_par(4))        # True
print(es_par(7))        # False
print(promedio([10, 20, 30]))   # 20.0
print(contar_vocales("murcielago"))  # 5
```

:::

:::prompt{title="Depurar errores de Python" for="ChatGPT/Claude"}

Estoy aprendiendo Python y tengo el siguiente error:

```
[pega aquí el mensaje de error completo]
```

Mi código es:

```python
[pega aquí tu código]
```

Explícame:
1. ¿Qué significa este error en español simple?
2. ¿En qué línea está el problema?
3. ¿Cómo lo corrijo?
4. ¿Cómo puedo evitar este error en el futuro?

:::
