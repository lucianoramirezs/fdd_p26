# Diseñando una librería

No vas a escribir código funcional hoy. Vas a **pensar**, y vas a documentar ese pensamiento. El código viene después.

Esto es intencional: los mejores programadores pasan más tiempo pensando que tecleando. Un buen diseño hace que la implementación sea casi obvia. Un mal diseño (o ningún diseño) te lleva a reescribir todo tres veces.

---

## 1. Script vs librería

Ya escribiste scripts en Python: archivos que hacen algo específico de principio a fin. Un script que limpia un CSV. Un script que descarga datos de una API. Un script que genera una gráfica.

Una **librería** es diferente. No resuelve **un** problema — resuelve una **clase** de problemas.

| | Script | Librería |
|--|--------|----------|
| **Resuelve** | Un problema concreto | Un tipo de problema |
| **Uso** | Lo ejecutas directamente | Otro código lo importa |
| **Ejemplo** | `limpiar_ventas_2024.py` | `import pandas` |
| **Reutilización** | Copy-paste, modificar | `pip install`, importar |

Piensa en las librerías que ya usas:

- **`requests`** no descarga *una* URL — resuelve el problema de "hacer cualquier petición HTTP"
- **`pandas`** no limpia *un* CSV — resuelve el problema de "manipular cualquier dato tabular"
- **`pytest`** no prueba *una* función — resuelve el problema de "verificar cualquier comportamiento"

La pregunta clave para empezar:

> **¿Qué problema estoy resolviendo una y otra vez que podría resolver una sola vez?**

---

## 2. El quantum: lo mínimo útil

Antes de pensar en grande, piensa en **lo más pequeño posible que ya sea útil**.

En física, un quantum es la cantidad mínima de energía. En diseño de software, el quantum de tu librería es la **funcionalidad mínima que alguien usaría por sí sola**.

### Ejemplos

| Librería | Quantum | Qué viene después |
|----------|---------|-------------------|
| Validador de CSVs | Verificar que un CSV tiene las columnas esperadas | Validar tipos, rangos, nulos, formatos |
| Convertidor de unidades | Convertir entre dos unidades del mismo tipo | Múltiples sistemas, formatos, parseo de strings |
| Buscador de texto | Buscar un patrón en un string | Regex, múltiples archivos, reemplazos |
| Generador de reportes | Generar una tabla formateada a partir de un dict | Gráficas, PDFs, templates, estilos |

El quantum te da dos cosas:

1. **Foco**: sabes exactamente qué construir primero
2. **Validación**: si el quantum no es útil solo, tu idea es demasiado grande o demasiado vaga

> **Si no puedes describir tu quantum en una oración, todavía no entiendes tu problema.**

:::exercise{title="Define tu quantum" difficulty="1"}

Elige un dominio que te interese (o usa uno de estos):

- Validación de datos (CSVs, JSONs, inputs de usuario)
- Conversión de formatos (fechas, unidades, monedas, archivos)
- Análisis de texto (frecuencias, patrones, limpieza)
- Utilidades matemáticas/estadísticas
- Automatización de archivos (renombrar, organizar, comprimir)

Escribe:
1. **El problema general** que tu librería resuelve (una oración)
2. **El quantum** — la funcionalidad mínima que ya sería útil sola (una oración)

:::

---

## 3. El vocabulario: sustantivos y verbos

Toda librería define un **lenguaje**. Cuando usas pandas, piensas en DataFrames, Series, columnas, índices, filtros, agrupaciones. Esas palabras son el **vocabulario** de pandas.

Tu librería también va a definir un vocabulario. Los **sustantivos** son las cosas con las que trabaja. Los **verbos** son las operaciones que hace sobre ellas.

### De sustantivos y verbos a Python

| Concepto | En tu diseño | En Python |
|----------|-------------|-----------|
| **Sustantivo con estado** | "Un archivo CSV con sus columnas y tipos" | **Clase** |
| **Sustantivo simple** | "Una regla de validación" | **Diccionario**, **tupla**, o **clase simple** |
| **Verbo independiente** | "Convertir Celsius a Fahrenheit" | **Función** |
| **Verbo sobre un sustantivo** | "Validar un CSV contra sus reglas" | **Método** de una clase |
| **Grupo de cosas relacionadas** | "Todas las conversiones de temperatura" | **Módulo** (archivo `.py`) |

### El principio de menor sorpresa

El nombre de cada cosa debe decir **qué hace**, no cómo lo hace:

| Malo | Bueno | ¿Por qué? |
|------|-------|------------|
| `process_data()` | `limpiar_nulos()` | "Process" no dice nada |
| `run()` | `validar_columnas()` | "Run" no dice qué corre |
| `handle()` | `convertir_a_celsius()` | "Handle" es genérico |
| `DataManager` | `ValidadorCSV` | "Manager" es la palabra más vacía en programación |
| `utils.py` | `conversiones.py` | "Utils" es el cajón de sastre donde mueren las buenas ideas |

### ¿Cuándo necesitas una clase?

Regla simple:

- **3-5 funciones sin estado compartido** → solo funciones en un módulo
- **Funciones que operan sobre los mismos datos** → una clase
- **Variaciones del mismo concepto** → herencia

```
# ¿Necesitas una clase? Hazte estas preguntas:

¿Hay datos que persisten entre llamadas?
  NO  → funciones
  SÍ  → ¿Las operaciones sobre esos datos forman un concepto coherente?
         NO  → probablemente funciones + un dict/tupla para los datos
         SÍ  → clase
```

:::exercise{title="Vocabulario de tu librería" difficulty="2"}

Para la librería que elegiste en el ejercicio anterior:

1. Lista **5-7 sustantivos** (las cosas con las que trabaja tu librería)
2. Lista **5-7 verbos** (las operaciones que hace)
3. Para cada sustantivo, decide: ¿clase, diccionario, o valor simple?
4. Para cada verbo, decide: ¿función suelta o método de una clase?

Ejemplo para una librería de validación de CSVs:

| Sustantivos | En Python | Verbos | En Python |
|-------------|-----------|--------|-----------|
| Archivo CSV | clase `ArchivoCSV` | Validar columnas | método `.validar_columnas()` |
| Regla de validación | dict `{"columna": "edad", "tipo": int}` | Cargar archivo | función `cargar(ruta)` |
| Reporte de errores | clase `Reporte` | Generar reporte | método `.generar_reporte()` |
| Columna | string (solo el nombre) | Verificar tipos | método `.verificar_tipos()` |
| Esquema | lista de reglas | Exportar resultado | función `exportar(reporte, ruta)` |

:::

---

## 4. Dream usage: el código que desearías que existiera

Este es el ejercicio más importante del módulo.

**Antes de pensar en cómo implementar**, escribe el código que tú — como usuario — desearías poder ejecutar. Esto se llama **diseño desde afuera hacia adentro** (outside-in design).

```python
# dream_usage.py — esto NO existe todavía, es lo que QUIERES que exista

from mi_libreria import ValidadorCSV, Esquema

# Definir las reglas
esquema = Esquema()
esquema.columna("nombre", tipo=str, obligatoria=True)
esquema.columna("edad", tipo=int, min=0, max=150)
esquema.columna("email", tipo=str, patron=r".*@.*\..*")

# Validar un archivo
validador = ValidadorCSV("datos.csv", esquema)
reporte = validador.validar()

# Ver resultados
print(reporte.es_valido)        # False
print(reporte.errores)          # ["Fila 3: 'edad' = -5 (min es 0)", ...]
print(reporte.resumen())        # "2 errores en 100 filas"
```

¿Ves lo que hicimos? Sin escribir una sola línea de implementación, ya sabemos:

- **Qué clases necesitamos**: `ValidadorCSV`, `Esquema`, un objeto reporte
- **Qué métodos tienen**: `.columna()`, `.validar()`, `.resumen()`
- **Cómo se conectan**: el esquema se pasa al validador, el validador produce un reporte
- **Qué interfaz exponen**: `.es_valido`, `.errores`

El dream usage **es** tu API. Todo lo que viene después es implementar lo que este código promete.

### Cómo escribir un buen dream usage

1. **Sé específico**: usa nombres reales, datos reales, valores concretos
2. **Muestra el flujo completo**: importar → configurar → ejecutar → ver resultado
3. **No hagas trampa**: si algo se siente raro de escribir, tu API tiene un problema
4. **Máximo 10-15 líneas**: si necesitas más, tu librería hace demasiado (o necesitas dividirla)

:::exercise{title="Dream usage" difficulty="2"}

Escribe el **dream usage** de tu librería. Máximo 15 líneas de código.

El código no tiene que funcionar — es lo que **deseas** que exista. Incluye:

1. Los imports
2. La configuración inicial (si la hay)
3. La operación principal
4. Ver el resultado

Léelo en voz alta. ¿Tiene sentido? ¿Un compañero podría entender qué hace sin que le expliques?

:::

---

## 5. De la idea a la estructura

Ahora traduce tu dream usage a una estructura de paquete. ¿Dónde vive cada cosa?

### Mapeo

Tu dream usage te dice qué clases y funciones necesitas. Ahora agrúpalas:

```
mi_libreria/
├── __init__.py          ← exporta lo que aparece en tus imports
├── validador.py         ← clase ValidadorCSV
├── esquema.py           ← clase Esquema
└── reporte.py           ← clase Reporte (o lo que retorna .validar())
```

El `__init__.py` exporta exactamente lo que tu dream usage importa:

```python
# mi_libreria/__init__.py
from .validador import ValidadorCSV
from .esquema import Esquema
```

### Reglas para la estructura

- **Un módulo por concepto**: si `validador.py` crece mucho, divídelo
- **El `__init__.py` exporta lo público**: todo lo demás es interno
- **Los tests van aparte**: `tests/test_validador.py`, `tests/test_esquema.py`
- **La estructura refleja los sustantivos**: cada sustantivo importante tiene su módulo

### Empieza a pensar en código: firmas y docstrings

No necesitas implementar nada. Pero **escribir las firmas** (nombre + parámetros + docstring) te obliga a pensar en la interfaz:

```python
# esquema.py — solo las firmas, sin implementación

class Esquema:
    """Define las reglas de validación para un archivo CSV."""

    def columna(self, nombre, tipo=str, obligatoria=False, min=None, max=None, patron=None):
        """Agrega una regla de validación para una columna.

        Args:
            nombre: Nombre de la columna en el CSV.
            tipo: Tipo de datos esperado (str, int, float).
            obligatoria: Si True, la columna no puede tener valores vacíos.
            min: Valor mínimo (solo para tipos numéricos).
            max: Valor máximo (solo para tipos numéricos).
            patron: Expresión regular que deben cumplir los valores.
        """
        pass  # implementación después

    def reglas(self):
        """Retorna la lista de reglas definidas."""
        pass
```

Esto es un **sketch** — como un boceto antes de pintar. No funciona, pero define la **forma** del código.

:::exercise{title="Estructura y sketches" difficulty="2"}

Para tu librería:

1. Dibuja la **estructura del paquete** (árbol de directorios y archivos)
2. Escribe las **firmas con docstrings** de las 3-4 funciones/clases más importantes
3. Escribe el `__init__.py` — ¿qué exportas?

No implementes nada. Solo la forma.

:::

---

## 6. El documento de diseño

Todo lo que trabajaste en las secciones anteriores se formaliza en un **documento de diseño**. Es un archivo markdown que describe tu librería **antes de escribirla**.

### Estructura del documento

```markdown
# Nombre de tu librería

## 1. Problema
[Una oración: qué problema recurrente resuelve esta librería]

## 2. Quantum
[Una oración: la funcionalidad mínima que ya sería útil sola]

## 3. Vocabulario

| Sustantivo | En Python | Descripción |
|------------|-----------|-------------|
| ... | clase / dict / valor | ... |

| Verbo | En Python | Descripción |
|-------|-----------|-------------|
| ... | función / método | ... |

## 4. Dream usage

```python
[5-15 líneas de código que muestran el uso ideal]
```

## 5. Estructura del paquete

```
mi_libreria/
├── __init__.py
├── ...
└── ...
```

## 6. Sketches

```python
[Firmas de funciones/clases con docstrings, sin implementación]
```

## 7. Lo que NO hace
[Lista explícita de qué está fuera del alcance — esto es tan importante como lo que sí hace]
```

### ¿Por qué un documento de diseño?

1. **Te obliga a pensar antes de codear** — el error más caro es implementar la solución equivocada
2. **Es comunicable** — un compañero puede leerlo y darte feedback antes de que escribas 500 líneas
3. **Es un contrato contigo mismo** — cuando implementes, sabes exactamente qué construir
4. **Es evaluable** — puedes revisar si el diseño tiene sentido sin ejecutar nada

> **El documento de diseño es tu entregable para este módulo.** Créalo como un archivo markdown en tu directorio de estudiante.

---

## Ejemplo completo: librería de conversión de unidades

Para que veas cómo se ve un documento de diseño terminado, aquí hay un ejemplo:

### Problema

Convertir entre unidades del mismo tipo (temperatura, distancia, peso) de forma consistente y extensible.

### Quantum

Convertir un valor numérico entre dos unidades del mismo tipo: `convertir(100, "celsius", "fahrenheit")`.

### Vocabulario

| Sustantivo | En Python | Descripción |
|------------|-----------|-------------|
| Valor con unidad | tupla `(100, "celsius")` | Un número con su unidad |
| Tipo de unidad | string `"temperatura"` | Categoría (temp, distancia, peso) |
| Tabla de conversiones | dict interno | Factores/funciones entre unidades |

| Verbo | En Python | Descripción |
|-------|-----------|-------------|
| Convertir | función `convertir(valor, origen, destino)` | Operación principal |
| Listar unidades | función `unidades_disponibles(tipo)` | Ver qué unidades existen |
| Registrar unidad | función `registrar(tipo, nombre, a_base, de_base)` | Agregar unidades custom |

### Dream usage

```python
from conversor import convertir, unidades_disponibles

# Uso básico
resultado = convertir(100, "celsius", "fahrenheit")
print(resultado)  # 212.0

# Ver qué hay disponible
print(unidades_disponibles("temperatura"))
# ["celsius", "fahrenheit", "kelvin"]

# Conversión encadenada
en_kelvin = convertir(72, "fahrenheit", "kelvin")
print(en_kelvin)  # 295.37
```

### Estructura

```
conversor/
├── __init__.py          # exporta convertir, unidades_disponibles
├── motor.py             # lógica de conversión
└── unidades/
    ├── __init__.py
    ├── temperatura.py   # definiciones de celsius, fahrenheit, kelvin
    ├── distancia.py     # km, millas, metros, pies
    └── peso.py          # kg, libras, onzas
```

### Sketches

```python
# motor.py
def convertir(valor, origen, destino):
    """Convierte un valor numérico de una unidad a otra.

    Args:
        valor: Número a convertir.
        origen: Unidad de origen (ej: "celsius").
        destino: Unidad de destino (ej: "fahrenheit").

    Returns:
        float: El valor convertido.

    Raises:
        ValueError: Si las unidades no son del mismo tipo.
        KeyError: Si la unidad no existe.
    """
    pass

def unidades_disponibles(tipo=None):
    """Lista las unidades disponibles.

    Args:
        tipo: Si se especifica, filtra por tipo ("temperatura", "distancia", "peso").
              Si es None, retorna todas.

    Returns:
        list[str]: Nombres de las unidades disponibles.
    """
    pass
```

### Lo que NO hace

- No maneja conversiones entre tipos diferentes (celsius a kilómetros no tiene sentido)
- No formatea resultados (no agrega símbolos como "°F")
- No hace conversiones de moneda (necesitarían tasas de cambio en tiempo real)
- No parsea strings como "100 grados celsius" — recibe números y strings de unidad por separado

---

:::exercise{title="Tu documento de diseño" difficulty="3"}

Escribe el documento de diseño completo para tu librería siguiendo la estructura de la sección 6.

**Antes de empezar**, revisa:
- ¿Tu quantum es realmente la cosa más pequeña útil?
- ¿Tu dream usage se lee naturalmente?
- ¿Tus nombres siguen el principio de menor sorpresa?

**Entrega**: un archivo `.md` en tu directorio de estudiante con el documento completo.

:::

:::prompt{title="Revisión de diseño entre compañeros" for="Un compañero"}

Lee el documento de diseño de tu compañero y responde:

1. **¿Entiendes el problema?** Lee solo la sección "Problema". ¿Podrías explicarlo con tus propias palabras?
2. **¿El dream usage tiene sentido?** Sin leer nada más, ¿puedes entender qué hace el código?
3. **¿Los nombres son claros?** ¿Algún nombre te confunde o te sorprende?
4. **¿Falta algo en "Lo que NO hace"?** ¿Hay algo que esperarías que hiciera pero no está?
5. **¿Lo usarías?** Honestamente, ¿resolverías tu problema con esta librería?

Sé específico. "Está bien" no es feedback útil. "El nombre `procesar` no me dice qué hace" sí lo es.

:::
