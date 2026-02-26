# Clases y Programación Orientada a Objetos

Ya viste los básicos de clases en el curso de DataCamp y en la sección anterior. Aquí vamos **más profundo**: los mecanismos internos que hacen que tus clases se comporten como tipos nativos de Python, los decoradores que controlan acceso y construcción, clases abstractas para definir contratos, y -- quizá lo más importante -- cuándo **no** usar clases.

---

## 1. Anatomía de una clase

### `__init__` y `self`

`self` es la instancia. Siempre es el primer parámetro de cada método. Python lo pasa automáticamente -- tú solo defines el método con `self` y lo llamas sin él:

```python
class Rectangulo:
    def __init__(self, ancho, alto):
        self.ancho = ancho   # self.ancho pertenece a ESTA instancia
        self.alto = alto

    def area(self):
        return self.ancho * self.alto

r = Rectangulo(3, 4)    # Python llama Rectangulo.__init__(r, 3, 4)
print(r.area())          # Python llama Rectangulo.area(r) -> 12
```

`__init__` es el **constructor** (técnicamente el "inicializador" -- `__new__` crea el objeto, `__init__` lo configura, pero en la práctica no necesitas tocar `__new__`). Se ejecuta automáticamente cuando creas una instancia con `Clase(...)`.

### Atributos de instancia vs de clase

```python
class Perro:
    especie = "Canis familiaris"  # atributo de CLASE -- compartido por todas las instancias

    def __init__(self, nombre):
        self.nombre = nombre      # atributo de INSTANCIA -- unico por objeto
```

```python
rex = Perro("Rex")
luna = Perro("Luna")

# Los atributos de clase son compartidos
print(rex.especie)    # "Canis familiaris"
print(luna.especie)   # "Canis familiaris"

# Los atributos de instancia son independientes
print(rex.nombre)     # "Rex"
print(luna.nombre)    # "Luna"

# Si cambias el atributo de clase, cambia para TODOS
Perro.especie = "Canino domestico"
print(rex.especie)    # "Canino domestico"
print(luna.especie)   # "Canino domestico"
```

**Cuándo usar cada uno:**

- **Atributo de clase**: valores que son iguales para todas las instancias (configuraciones por defecto, constantes de la clase, contadores compartidos).
- **Atributo de instancia**: valores que varían entre instancias (nombre, estado, datos propios).

### La trampa del atributo de clase mutable

Esto es un bug clásico. Si el atributo de clase es mutable (lista, diccionario, set), **todas las instancias comparten el mismo objeto**:

```python
class Equipo:
    miembros = []   # PELIGRO: esta lista es compartida

    def agregar(self, nombre):
        self.miembros.append(nombre)

a = Equipo()
b = Equipo()
a.agregar("Ana")
print(b.miembros)   # ["Ana"] -- sorpresa! b tambien lo tiene
```

La solución es inicializar mutables en `__init__`:

```python
class Equipo:
    def __init__(self):
        self.miembros = []   # cada instancia tiene su propia lista

a = Equipo()
b = Equipo()
a.agregar("Ana")
print(b.miembros)   # [] -- correcto
```

**Regla**: si el atributo de clase es inmutable (`int`, `str`, `tuple`), no hay problema. Si es mutable (`list`, `dict`, `set`), inicialízalo en `__init__`.

### Convenciones de privacidad

Python **no tiene** `private` ni `protected`. Todo es accesible. Pero la comunidad usa estas convenciones y las respeta:

| Forma | Significado | Ejemplo |
|-------|-------------|---------|
| `atributo` | Público | `self.nombre` |
| `_atributo` | "Privado por convención" | `self._cache` |
| `__atributo` | Name mangling | `self.__secreto` |
| `__atributo__` | Método mágico (reservado) | `self.__init__` |

```python
class Cuenta:
    def __init__(self, titular, saldo):
        self.titular = titular      # publico: el usuario lo necesita
        self._saldo = saldo         # interno: no toques directamente
        self.__pin = 1234           # name mangling: Python lo renombra

c = Cuenta("Ana", 1000)
print(c.titular)          # "Ana" -- ok
print(c._saldo)           # 1000 -- funciona, pero no deberias
print(c._Cuenta__pin)     # 1234 -- Python lo renombro a _Cuenta__pin
# print(c.__pin)          # AttributeError
```

**En la práctica, usa casi siempre `_`** para lo interno. El name mangling (`__`) existe para evitar colisiones de nombres en herencia múltiple -- un caso raro. Si tu clase no participa en herencia múltiple compleja, `_` es suficiente.

`from modulo import *` **no importa** nombres que empiezan con `_`. Eso es otra razón para usar el prefijo: marca lo que es detalle de implementación.

---

## 2. Métodos especiales (dunder methods)

Los métodos `__nombre__` (dunder = double underscore) le dicen a Python cómo debe comportarse tu clase con operadores y funciones built-in. Sin ellos, tu clase es una caja opaca. Con ellos, se integra naturalmente al lenguaje.

### `__repr__` vs `__str__`

Son dos formas de convertir tu objeto a texto, pero con propósitos distintos:

- **`__repr__`**: para **desarrolladores**. Debe ser preciso e idealmente producir Python válido que recree el objeto.
- **`__str__`**: para **usuarios**. Debe ser legible y amigable.

```python
class Producto:
    def __init__(self, nombre, precio):
        self.nombre = nombre
        self.precio = precio

    def __repr__(self):
        # Para el desarrollador: exacto, evaluable
        return f"Producto({self.nombre!r}, {self.precio})"

    def __str__(self):
        # Para el usuario: legible
        return f"{self.nombre} - ${self.precio:.2f}"
```

```python
p = Producto("Cafe", 45.5)

repr(p)     # "Producto('Cafe', 45.5)"  -- en el REPL y debugger
str(p)      # "Cafe - $45.50"           -- con print()
print(p)    # "Cafe - $45.50"           -- print llama str()

# En una lista, Python usa repr:
print([p])  # [Producto('Cafe', 45.5)]
```

**Si solo vas a implementar uno, implementa `__repr__`**. Cuando Python necesita `__str__` y no lo encuentra, usa `__repr__` como fallback. Al revés no funciona.

El `!r` en el f-string (`self.nombre!r`) aplica `repr()` al valor, lo que pone comillas alrededor de strings. Es útil para que el output sea copy-pasteable como Python válido.

### `__eq__`, `__lt__`, `__hash__`

Sin `__eq__`, el operador `==` compara **identidad** (la misma dirección de memoria, igual que `is`):

```python
class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y

a = Punto(1, 2)
b = Punto(1, 2)
print(a == b)   # False! -- son objetos distintos en memoria
print(a is b)   # False  -- misma comparacion sin __eq__
```

Con `__eq__`, defines qué significa igualdad para tu clase:

```python
class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, otro):
        if not isinstance(otro, Punto):
            return NotImplemented   # deja que Python intente al reves
        return self.x == otro.x and self.y == otro.y

    def __lt__(self, otro):
        """Compara por distancia al origen."""
        if not isinstance(otro, Punto):
            return NotImplemented
        return (self.x**2 + self.y**2) < (otro.x**2 + otro.y**2)

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Punto({self.x}, {self.y})"

a = Punto(1, 2)
b = Punto(1, 2)
c = Punto(3, 4)

print(a == b)   # True  -- ahora compara valores
print(a < c)    # True  -- sqrt(5) < sqrt(25)
print({a, b})   # {Punto(1, 2)} -- hash permite usarlo en sets y como key de dict
```

**Reglas importantes:**

1. Si defines `__eq__`, Python **anula `__hash__` automáticamente** (lo pone en `None`). Esto hace que tu objeto no sea hasheable y no puedas meterlo en un `set` ni usarlo como key de `dict`. Si necesitas eso, define `__hash__` explícitamente.
2. Si tu objeto es mutable, **no deberías definir `__hash__`** -- un objeto mutable que cambia después de insertarlo en un set causa bugs silenciosos.
3. `NotImplemented` (sin `raise`) le dice a Python "yo no sé comparar esto, intenta con el otro operando". Es diferente de `NotImplementedError`.

**`@functools.total_ordering`**: si defines `__eq__` y **uno** de `__lt__`, `__le__`, `__gt__`, `__ge__`, este decorador genera los demás automáticamente:

```python
from functools import total_ordering

@total_ordering
class Calificacion:
    def __init__(self, valor):
        self.valor = valor

    def __eq__(self, otro):
        return self.valor == otro.valor

    def __lt__(self, otro):
        return self.valor < otro.valor

# Ahora tienes ==, !=, <, <=, >, >= sin escribirlos todos
```

### `__len__`, `__getitem__`, `__contains__`

Estos métodos hacen que tu clase se comporte como una colección:

```python
class Playlist:
    """Coleccion ordenada de canciones."""

    def __init__(self, nombre, canciones=None):
        self.nombre = nombre
        self._canciones = list(canciones) if canciones else []

    def agregar(self, cancion):
        self._canciones.append(cancion)

    def __len__(self):
        """len(playlist) -> numero de canciones."""
        return len(self._canciones)

    def __getitem__(self, indice):
        """playlist[i] -> acceso por indice. Tambien habilita slicing."""
        return self._canciones[indice]

    def __contains__(self, cancion):
        """'cancion' in playlist -> busqueda."""
        return cancion in self._canciones

    def __repr__(self):
        return f"Playlist({self.nombre!r}, {len(self)} canciones)"
```

```python
rock = Playlist("Rock Clasico", ["Bohemian Rhapsody", "Stairway to Heaven", "Hotel California"])

print(len(rock))                    # 3
print(rock[0])                      # "Bohemian Rhapsody"
print(rock[-1])                     # "Hotel California"
print(rock[0:2])                    # ["Bohemian Rhapsody", "Stairway to Heaven"]
print("Hotel California" in rock)   # True

# Bonus: __getitem__ habilita iteracion automatica
for cancion in rock:
    print(cancion)
```

**Protocolo importante**: si tu clase tiene `__getitem__`, Python puede iterar sobre ella aunque no definas `__iter__`. Esto es porque Python intenta llamar `obj[0]`, `obj[1]`, `obj[2]`... hasta recibir un `IndexError`. Es un mecanismo legacy pero funciona.

### `__enter__` y `__exit__` (context managers)

El statement `with` llama a `__enter__` al inicio y `__exit__` al final (incluso si hay una excepción). Esto es perfecto para manejar recursos que necesitan limpieza:

```python
import time

class Timer:
    """Mide cuanto tarda un bloque de codigo."""

    def __init__(self, nombre="bloque"):
        self.nombre = nombre
        self.inicio = None
        self.duracion = None

    def __enter__(self):
        self.inicio = time.time()
        return self   # el valor que recibe la variable despues de 'as'

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duracion = time.time() - self.inicio
        print(f"{self.nombre}: {self.duracion:.4f}s")
        return False   # False = no suprimir excepciones
```

```python
with Timer("carga de datos") as t:
    datos = [i**2 for i in range(1_000_000)]

# Salida: "carga de datos: 0.0823s"
print(t.duracion)   # 0.0823... -- accesible despues del with
```

**Cuándo usar context managers**: archivos, conexiones a bases de datos, locks, transacciones, cualquier recurso que necesite un "abrir/cerrar" o "setup/teardown".

`__exit__` recibe información sobre la excepción (si la hubo). Si retorna `True`, la excepción se suprime. Casi siempre quieres retornar `False` para dejar que las excepciones se propaguen.

Para casos simples, `contextlib.contextmanager` es más práctico que escribir una clase completa (ya lo viste en la sección de buenas prácticas).

---

## 3. Properties: `@property`

### El problema

Tienes una clase con un atributo que necesita validación. Sin `@property`, tienes dos opciones malas:

1. Dejar que el usuario asigne lo que quiera (sin validar).
2. Crear métodos `get_edad()` y `set_edad()` como en Java (feo y no-pytónico).

### La solución

`@property` convierte un método en algo que **parece** un atributo. El usuario accede con `obj.edad` pero internamente se ejecuta un método:

```python
class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad       # esto llama al setter!

    @property
    def edad(self):
        """Getter: se ejecuta al leer self.edad."""
        return self._edad

    @edad.setter
    def edad(self, valor):
        """Setter: se ejecuta al asignar self.edad = valor."""
        if not isinstance(valor, (int, float)):
            raise TypeError(f"Edad debe ser numerica, recibio {type(valor).__name__}")
        if valor < 0:
            raise ValueError(f"Edad no puede ser negativa: {valor}")
        self._edad = valor
```

```python
p = Persona("Ana", 25)
print(p.edad)       # 25 -- llama al getter, parece atributo normal

p.edad = 30         # ok -- llama al setter, valida
# p.edad = -5       # ValueError: Edad no puede ser negativa: -5
# p.edad = "viejo"  # TypeError: Edad debe ser numerica, recibio str
```

Nota que en `__init__` escribimos `self.edad = edad` (sin guión bajo). Esto **llama al setter**, así la validación se ejecuta desde la creación del objeto. El valor real se guarda en `self._edad`.

### Properties como atributos calculados

Puedes exponer valores derivados que se calculan al vuelo:

```python
class Rectangulo:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto

    @property
    def area(self):
        return self.ancho * self.alto

    @property
    def perimetro(self):
        return 2 * (self.ancho + self.alto)

    @property
    def es_cuadrado(self):
        return self.ancho == self.alto
```

```python
r = Rectangulo(3, 4)
print(r.area)         # 12 -- sin parentesis, parece atributo
print(r.perimetro)    # 14
print(r.es_cuadrado)  # False

r.ancho = 4
print(r.es_cuadrado)  # True -- se recalcula automaticamente
```

### Cuándo usar `@property`

- **Validación**: verificar que un valor es correcto antes de asignarlo.
- **Atributos calculados**: valores que se derivan de otros (`area` a partir de `ancho` y `alto`).
- **Compatibilidad**: empezaste con un atributo público y ahora necesitas lógica -- `@property` no rompe el código existente.

### Anti-patrón

**No hagas que una property haga trabajo pesado**. Si acceder a `obj.datos` tarda 5 segundos porque consulta una base de datos, el usuario espera la velocidad de un atributo, no de una operación. Usa un método explícito: `obj.cargar_datos()`.

```python
# MAL -- parece atributo pero tarda una eternidad
@property
def datos(self):
    return self._consultar_base_de_datos()  # 5 segundos

# BIEN -- el nombre del metodo comunica que hay trabajo
def cargar_datos(self):
    return self._consultar_base_de_datos()
```

---

## 4. `@classmethod` y `@staticmethod`

### `@classmethod`: constructores alternativos

Un método de clase recibe `cls` (la clase) como primer argumento en vez de `self` (la instancia). Su uso principal es crear **formas alternativas de construir objetos**:

```python
class Fecha:
    def __init__(self, anio, mes, dia):
        self.anio = anio
        self.mes = mes
        self.dia = dia

    @classmethod
    def from_string(cls, texto):
        """Crea una Fecha desde un string 'AAAA-MM-DD'."""
        partes = texto.split("-")
        return cls(int(partes[0]), int(partes[1]), int(partes[2]))

    @classmethod
    def hoy(cls):
        """Crea una Fecha con la fecha actual."""
        from datetime import date
        d = date.today()
        return cls(d.year, d.month, d.day)

    def __repr__(self):
        return f"Fecha({self.anio}, {self.mes}, {self.dia})"
```

```python
f1 = Fecha(2026, 2, 24)                # constructor normal
f2 = Fecha.from_string("2026-02-24")   # constructor alternativo
f3 = Fecha.hoy()                        # otro constructor alternativo

print(f1)   # Fecha(2026, 2, 24)
print(f2)   # Fecha(2026, 2, 24)
```

**Por qué `cls(...)` y no `Fecha(...)`?** Porque si alguien hereda de `Fecha`, `cls` será la subclase y el constructor retornará una instancia del tipo correcto:

```python
class FechaConHora(Fecha):
    pass

f = FechaConHora.from_string("2026-02-24")
print(type(f))   # <class 'FechaConHora'> -- correcto!
```

Si hubieras escrito `Fecha(...)` en vez de `cls(...)`, retornaría siempre una `Fecha`, incluso al llamarlo desde `FechaConHora`.

### `@staticmethod`: utilidades asociadas

Un método estático no recibe ni `self` ni `cls`. Es una función regular que vive dentro de la clase por organización:

```python
class Validador:
    def __init__(self, datos):
        self._datos = datos

    @staticmethod
    def es_email_valido(texto):
        """Verifica formato basico de email."""
        return "@" in texto and "." in texto.split("@")[-1]

    @staticmethod
    def es_telefono_valido(texto):
        """Verifica que sea solo digitos, 10 caracteres."""
        return texto.isdigit() and len(texto) == 10

    def validar_campo(self, campo, tipo):
        for registro in self._datos:
            valor = registro.get(campo, "")
            if tipo == "email" and not self.es_email_valido(valor):
                print(f"Email invalido: {valor}")
            elif tipo == "telefono" and not self.es_telefono_valido(valor):
                print(f"Telefono invalido: {valor}")
```

```python
# Puedes llamarlo sin instancia:
Validador.es_email_valido("ana@correo.com")    # True
Validador.es_email_valido("no-tiene-arroba")   # False

# O desde una instancia:
v = Validador([{"email": "test@x.com"}])
v.es_email_valido("test@x.com")                # True
```

**Cuándo usar `@staticmethod`**: cuando la función está conceptualmente relacionada con la clase pero no necesita acceder a datos de instancia ni de clase. Podría ser una función a nivel de módulo, pero ponerla en la clase comunica la relación.

### Resumen: cuál usar

| Tipo | Primer argumento | Acceso a | Uso principal |
|------|-----------------|----------|---------------|
| Método regular | `self` | instancia y clase | La mayoría de métodos |
| `@classmethod` | `cls` | clase (no instancia) | Constructores alternativos |
| `@staticmethod` | nada | nada | Utilidades asociadas |

```python
class Ejemplo:
    def metodo(self):          # necesita la instancia
        return self.dato

    @classmethod
    def crear(cls, x):        # necesita la clase
        return cls(x)

    @staticmethod
    def validar(x):           # no necesita nada del objeto
        return x > 0
```

---

## 5. Herencia en profundidad

### Herencia simple (repaso rápido)

El padre define el contrato, los hijos lo implementan:

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
    def __init__(self, nombre, ruta):
        super().__init__(nombre)   # siempre llama al constructor del padre
        self.ruta = ruta

    def leer(self):
        with open(self.ruta) as f:
            return f.readlines()


class FuenteJSON(FuenteDatos):
    def __init__(self, nombre, ruta):
        super().__init__(nombre)
        self.ruta = ruta

    def leer(self):
        import json
        with open(self.ruta) as f:
            return json.load(f)
```

Lo clave: `super().__init__(nombre)` llama al constructor del padre. **Siempre llámalo**. Si no lo haces, los atributos del padre no se inicializan y tendrás `AttributeError` en momentos inesperados.

### Herencia multinivel

Puedes encadenar herencia: Padre -> Hijo -> Nieto.

```python
class Animal:
    def __init__(self, nombre):
        self.nombre = nombre

    def hablar(self):
        raise NotImplementedError

class Mamifero(Animal):
    def __init__(self, nombre, patas):
        super().__init__(nombre)
        self.patas = patas

    def describir(self):
        return f"{self.nombre} ({self.patas} patas)"

class Perro(Mamifero):
    def __init__(self, nombre, raza):
        super().__init__(nombre, patas=4)
        self.raza = raza

    def hablar(self):
        return "Guau!"
```

```python
rex = Perro("Rex", "Labrador")
print(rex.describir())   # "Rex (4 patas)" -- metodo heredado de Mamifero
print(rex.hablar())      # "Guau!"         -- override de Animal
print(rex.nombre)        # "Rex"           -- atributo heredado de Animal
```

### MRO: Method Resolution Order

Cuando llamas un método, Python lo busca en un orden específico. El **MRO** (Method Resolution Order) te dice el orden exacto:

```python
print(Perro.__mro__)
# (<class 'Perro'>, <class 'Mamifero'>, <class 'Animal'>, <class 'object'>)
```

Python busca de izquierda a derecha: primero en `Perro`, luego en `Mamifero`, luego en `Animal`, y finalmente en `object` (la clase base de todo en Python).

Esto se calcula con el **algoritmo C3** (no necesitas saber los detalles, pero es bueno saber que existe y que es determinista). El MRO importa especialmente cuando hay herencia múltiple:

```python
class A:
    def metodo(self):
        return "A"

class B(A):
    def metodo(self):
        return "B"

class C(A):
    def metodo(self):
        return "C"

class D(B, C):
    pass

print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)

d = D()
print(d.metodo())   # "B" -- B viene antes que C en el MRO
```

**Consejo**: si necesitas consultar el MRO para entender qué método se llama, tu jerarquía probablemente es demasiado compleja. Simplifica.

### El principio DRY con herencia

Don't Repeat Yourself: si dos clases comparten lógica idéntica, extrae lo común al padre.

```python
# MAL: logica de logging duplicada
class ProcesadorCSV:
    def procesar(self, ruta):
        print(f"Inicio: {ruta}")          # duplicado
        datos = self._leer_csv(ruta)
        print(f"Fin: {len(datos)} filas")  # duplicado
        return datos

class ProcesadorJSON:
    def procesar(self, ruta):
        print(f"Inicio: {ruta}")          # duplicado
        datos = self._leer_json(ruta)
        print(f"Fin: {len(datos)} filas")  # duplicado
        return datos
```

```python
# BIEN: lo comun vive en el padre
class Procesador:
    def leer(self, ruta):
        raise NotImplementedError

    def procesar(self, ruta):
        print(f"Inicio: {ruta}")
        datos = self.leer(ruta)
        print(f"Fin: {len(datos)} filas")
        return datos

class ProcesadorCSV(Procesador):
    def leer(self, ruta):
        # solo la logica especifica de CSV
        with open(ruta) as f:
            return f.readlines()

class ProcesadorJSON(Procesador):
    def leer(self, ruta):
        import json
        with open(ruta) as f:
            return json.load(f)
```

**Pero**: herencia no es la única herramienta para DRY. Una función compartida, un decorador, o composición pueden lograr lo mismo con menos acoplamiento.

### Composición vs herencia

Esta es una de las decisiones de diseño más importantes en OOP. La regla:

- **Herencia** = "X **es un tipo de** Y" -> `Perro` es un `Animal`
- **Composición** = "X **tiene** un Y" -> `Carro` tiene un `Motor`

```python
# Composicion: Carro TIENE un Motor y una Transmision
class Motor:
    def __init__(self, caballos):
        self.caballos = caballos

    def encender(self):
        return f"Motor de {self.caballos}HP encendido"

class Transmision:
    def __init__(self, tipo):
        self.tipo = tipo   # "manual" o "automatica"

    def cambiar(self, velocidad):
        return f"Cambio a {velocidad}a ({self.tipo})"

class Carro:
    def __init__(self, marca, caballos, transmision):
        self.marca = marca
        self.motor = Motor(caballos)              # composicion
        self.transmision = Transmision(transmision) # composicion

    def arrancar(self):
        return f"{self.marca}: {self.motor.encender()}"

    def acelerar(self, velocidad):
        return self.transmision.cambiar(velocidad)
```

```python
c = Carro("Toyota", 150, "manual")
print(c.arrancar())          # "Toyota: Motor de 150HP encendido"
print(c.acelerar(3))         # "Cambio a 3a (manual)"
```

**Ventajas de composición sobre herencia:**

1. **Flexibilidad**: puedes cambiar el motor sin cambiar el carro.
2. **Reutilización**: el mismo `Motor` sirve para `Carro`, `Lancha`, `Generador`.
3. **Sin acoplamiento vertical**: cambiar la clase padre no rompe nada.
4. **Testing**: puedes probar `Motor` y `Carro` por separado.

**Regla de oro**: cuando dudes, usa composición. Python favorece el duck typing -- si camina como pato y hace cuack como pato, es un pato. A menudo no necesitas herencia en absoluto.

| Pregunta | Respuesta |
|----------|-----------|
| X **es un tipo de** Y? | Herencia |
| X **tiene** un Y? | Composición |
| Solo necesitas parte del padre? | Composición |
| La jerarquía tiene más de 2-3 niveles? | Refactoriza a composición |

---

## 6. Clases abstractas (ABC)

### El problema con `raise NotImplementedError`

En los ejemplos anteriores, la clase base lanza `NotImplementedError` si un hijo no implementa el método. Pero el error ocurre **cuando llamas al método**, no cuando creas la instancia:

```python
class FuenteDatos:
    def leer(self):
        raise NotImplementedError

class FuenteMal(FuenteDatos):
    pass   # olvido implementar leer()

f = FuenteMal()    # no hay error aqui!
f.leer()           # NotImplementedError -- error tardio
```

### La solución: ABC

Las clases abstractas de Python (`ABC` + `@abstractmethod`) fuerzan que los hijos implementen ciertos métodos. El error ocurre **al intentar instanciar**, no al llamar:

```python
from abc import ABC, abstractmethod

class FuenteDatos(ABC):
    """Contrato: toda fuente de datos debe poder leerse y describirse."""

    def __init__(self, nombre):
        self.nombre = nombre

    @abstractmethod
    def leer(self):
        """Lee datos de la fuente. Debe retornar una lista."""
        pass

    @abstractmethod
    def describir(self):
        """Retorna una descripcion de la fuente."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.nombre}')"
```

```python
# Esto falla INMEDIATAMENTE -- no puedes instanciar una clase abstracta
# f = FuenteDatos("test")
# TypeError: Can't instantiate abstract class FuenteDatos
#            with abstract methods describir, leer

# Esto tambien falla -- no implementa todos los metodos abstractos
class FuenteIncompleta(FuenteDatos):
    def leer(self):
        return []
    # falta describir()

# f = FuenteIncompleta("test")
# TypeError: Can't instantiate abstract class FuenteIncompleta
#            with abstract method describir
```

```python
# Esto funciona -- implementa TODOS los metodos abstractos
class FuenteCSV(FuenteDatos):
    def __init__(self, nombre, ruta):
        super().__init__(nombre)
        self.ruta = ruta

    def leer(self):
        with open(self.ruta) as f:
            return f.readlines()

    def describir(self):
        return f"CSV: {self.ruta}"


class FuenteAPI(FuenteDatos):
    def __init__(self, nombre, url):
        super().__init__(nombre)
        self.url = url

    def leer(self):
        import requests
        return requests.get(self.url).json()

    def describir(self):
        return f"API: {self.url}"
```

### Cuándo usar ABC

- Cuando defines un **contrato** que múltiples clases deben seguir.
- Cuando quieres errores **tempranos** (al instanciar, no al llamar un método).
- Cuando trabajas en equipo y quieres que las interfaces sean explícitas.

**Cuándo NO usar ABC**: si solo tienes una implementación, una ABC es burocracia innecesaria. Si estás en Python y puedes confiar en duck typing, a veces basta con documentar la interfaz esperada. Las ABCs brillan cuando tienes 3+ implementaciones del mismo contrato.

---

## 7. Cuándo usar clases?

Esta es la pregunta más importante de toda esta sección. Muchos programadores que aprenden OOP quieren hacer clases para todo. Resiste esa tentación.

| Usa funciones | Usa una clase | Piénsalo dos veces |
|---------------|---------------|---------------------|
| No hay estado entre llamadas | Datos que persisten entre operaciones | God class (una clase que hace todo) |
| Operaciones independientes | Datos + comportamiento forman un concepto | Clase con solo `__init__` y un método |
| 3-5 funciones simples | El concepto tiene identidad propia | Clases `Manager`, `Handler`, `Processor` |
| Transformaciones puras | Necesitas polimorfismo | Herencia donde composición basta |

### La prueba del método solitario

> Si tu clase solo tiene `__init__` y un método, probablemente debería ser una función.

```python
# MAL: clase innecesaria
class Calculadora:
    def __init__(self, datos):
        self.datos = datos

    def calcular_promedio(self):
        return sum(self.datos) / len(self.datos)

# USO: c = Calculadora(datos).calcular_promedio()

# BIEN: una funcion hace lo mismo
def calcular_promedio(datos):
    return sum(datos) / len(datos)

# USO: calcular_promedio(datos)
```

### Las clases son para agrupar estado + comportamiento

Si tienes datos que cambian y operaciones que trabajan sobre esos datos, una clase tiene sentido:

```python
# Esto SI justifica una clase:
class Carrito:
    def __init__(self):
        self._items = []

    def agregar(self, producto, cantidad=1):
        self._items.append({"producto": producto, "cantidad": cantidad})

    def quitar(self, producto):
        self._items = [i for i in self._items if i["producto"] != producto]

    @property
    def total(self):
        return sum(i["producto"].precio * i["cantidad"] for i in self._items)

    def __len__(self):
        return len(self._items)
```

Aquí hay **estado** (`_items`) que **múltiples métodos** modifican y consultan. Eso es exactamente lo que una clase modela bien.

### Composición de funciones como alternativa

A veces, lo que parece necesitar una clase se resuelve mejor con funciones que se pasan datos:

```python
# Enfoque funcional -- sin clase
def leer_csv(ruta):
    with open(ruta) as f:
        return f.readlines()

def filtrar(datos, condicion):
    return [d for d in datos if condicion(d)]

def transformar(datos, funcion):
    return [funcion(d) for d in datos]

# Composicion: encadenas funciones
datos = leer_csv("ventas.csv")
datos = filtrar(datos, lambda d: "2026" in d)
datos = transformar(datos, str.strip)
```

No hay nada malo con este enfoque. No necesitas forzar una clase `Pipeline` o `DataProcessor` si las funciones son claras y el estado no persiste.

---

:::exercise{title="Dunder methods" difficulty="2"}

Tienes esta clase básica. Agrega los dunder methods necesarios para que el código de prueba funcione:

```python
class Inventario:
    def __init__(self, nombre, productos=None):
        self.nombre = nombre
        self._productos = dict(productos) if productos else {}

    def agregar(self, producto, cantidad):
        self._productos[producto] = self._productos.get(producto, 0) + cantidad
```

Código de prueba que debe funcionar:

```python
inv = Inventario("Almacen Central", {"manzanas": 50, "peras": 30})

# __repr__
repr(inv)        # "Inventario('Almacen Central', 2 productos)"

# __len__
len(inv)         # 2

# __contains__
"manzanas" in inv   # True
"kiwi" in inv       # False

# __getitem__
inv["manzanas"]     # 50
inv["peras"]        # 30

# __eq__
inv2 = Inventario("Almacen Central", {"manzanas": 50, "peras": 30})
inv == inv2         # True

inv3 = Inventario("Otro", {"manzanas": 50})
inv == inv3         # False
```

Implementa `__repr__`, `__len__`, `__contains__`, `__getitem__` y `__eq__`.

:::

:::exercise{title="Property y validación" difficulty="2"}

Crea una clase `CuentaBancaria` con las siguientes reglas:

1. `titular` es un string no vacío (valida con `@property`).
2. `saldo` no puede ser negativo (valida con `@property`).
3. Tiene un método `depositar(monto)` que acepta solo montos positivos.
4. Tiene un método `retirar(monto)` que verifica que el monto sea positivo y que haya saldo suficiente.
5. Tiene una property `esta_sobregirada` que retorna `True` si el saldo es 0.

```python
# Tu clase debe soportar esto:
cuenta = CuentaBancaria("Ana Lopez", 1000)
cuenta.depositar(500)
print(cuenta.saldo)          # 1500

cuenta.retirar(200)
print(cuenta.saldo)          # 1300

print(cuenta.esta_sobregirada)  # False

# Estas deben lanzar errores:
# CuentaBancaria("", 100)         # ValueError: titular no puede estar vacio
# CuentaBancaria("Ana", -500)     # ValueError: saldo no puede ser negativo
# cuenta.depositar(-100)          # ValueError: monto debe ser positivo
# cuenta.retirar(99999)           # ValueError: saldo insuficiente
```

:::

:::exercise{title="Composición vs herencia" difficulty="2"}

Diseña un sistema de notificaciones usando **composición** (no herencia). Necesitas:

1. Clase `Mensaje` que tenga `destinatario`, `asunto` y `cuerpo`.
2. Clase `EnviadorEmail` con método `enviar(mensaje)` que imprima `"Email a {destinatario}: {asunto}"`.
3. Clase `EnviadorSMS` con método `enviar(mensaje)` que imprima `"SMS a {destinatario}: {asunto}"`.
4. Clase `Notificador` que reciba un enviador en su constructor (composición) y tenga un método `notificar(destinatario, asunto, cuerpo)`.

```python
# Uso esperado:
email_sender = EnviadorEmail()
sms_sender = EnviadorSMS()

notificador_email = Notificador(email_sender)
notificador_sms = Notificador(sms_sender)

notificador_email.notificar("ana@correo.com", "Alerta", "Tu servidor esta caido")
# "Email a ana@correo.com: Alerta"

notificador_sms.notificar("5512345678", "Alerta", "Tu servidor esta caido")
# "SMS a 5512345678: Alerta"
```

**Pregunta de reflexión**: por qué composición es mejor que herencia aquí? Qué pasaría si quieres agregar `EnviadorSlack` o `EnviadorTelegram`?

:::

:::exercise{title="Mini-framework con ABC" difficulty="3"}

Crea un mini-framework de transformación de datos:

1. Clase abstracta `Transformacion(ABC)` con:
   - `@abstractmethod def aplicar(self, datos: list) -> list`
   - `@abstractmethod def describir(self) -> str`
   - Método concreto `__repr__` que use `describir()`

2. Dos subclases concretas:
   - `Filtro`: recibe una función condición en `__init__`. `aplicar()` retorna solo los elementos que la cumplen.
   - `Mapeador`: recibe una función de transformación en `__init__`. `aplicar()` la aplica a cada elemento.

3. Clase `Pipeline` que:
   - Reciba una lista de `Transformacion` en su constructor.
   - Tenga un método `ejecutar(datos)` que aplique cada transformación en orden.
   - Implemente `__len__` (número de pasos) y `__repr__`.

```python
# Uso esperado:
datos = [1, -2, 3, -4, 5, -6, 7, 8, -9, 10]

pipeline = Pipeline([
    Filtro(lambda x: x > 0, "solo positivos"),
    Mapeador(lambda x: x ** 2, "elevar al cuadrado"),
    Filtro(lambda x: x > 10, "mayores a 10"),
])

print(len(pipeline))         # 3
print(pipeline.ejecutar(datos))  # [25, 49, 64, 100]
```

**Bonus**: agrega un método `agregar(transformacion)` al Pipeline que valide con `isinstance` que sea una `Transformacion`.

:::

:::prompt{title="Revisa esta clase Python y dime qué dunder methods le agregarías y por qué" for="ChatGPT/Claude"}

Tengo esta clase en Python:

```python
[pega aqui tu clase]
```

Analiza:

1. Qué **dunder methods** le agregarías para que se integre mejor con Python? (`__repr__`, `__str__`, `__eq__`, `__len__`, `__getitem__`, `__contains__`, `__iter__`, `__bool__`, etc.)
2. Para cada uno, explica **por qué** lo necesita esta clase específica.
3. Hay alguna **property** que debería tener en vez de un método o atributo directo?
4. Necesita **validación** en `__init__` o en algún setter?
5. Muestra la clase completa con tus mejoras.

:::
