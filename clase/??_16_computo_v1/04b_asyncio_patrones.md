---
title: "asyncio — Patrones Avanzados y Anti-patrones"
---

# asyncio — Patrones Avanzados y Anti-patrones

`04a_asyncio_fundamentos.md` cubrió `gather` como la forma básica de M4. Este archivo completa la familia de mecanismos de sincronización y documenta los errores más comunes — cada uno con su consecuencia formal.

---

## asyncio.create_task — "lanzar y continuar"

### En los tres lenguajes

**Analogía:**

El cocinero recibe dos órdenes. La primera requiere el horno. El cocinero:

1. Prepara la orden A y la **pone en el horno** → equivale a `create_task(tarea_A())`
2. **Mientras el horno trabaja**, prepara la ensalada de la orden B → trabajo independiente
3. Cuando necesita emplatar, **verifica que A esté lista** → `await tarea_A_obj`

La ensalada se preparó "gratis" — el tiempo del horno se aprovechó completamente.

**Formal:**

```
t₁: τᵢ = create_task(fn_A)    # τᵢ se registra en el event loop → empieza en background
    [t₁, t₂]: τⱼ (trabajo independiente) ejecuta
               exec(τⱼ) ∩ wait(τᵢ) ≠ ∅   ← espera de A explotada ✓
t₂: await τᵢ                  # punto de sincronización — necesitamos result(τᵢ)
    Si τᵢ ya terminó: continúa sin espera
    Si τᵢ aún espera: el event loop bloquea τⱼ hasta que τᵢ complete
```

`t₂` es el **punto de dependencia de datos**: el momento donde el código necesita el resultado de τᵢ para continuar. La posición del `await` es una decisión de diseño, no un detalle técnico.

**Código:**

```python
async def preparar_mesa():
    # ① Lanzar τᵢ: empieza en background inmediatamente
    tarea_A = asyncio.create_task(calentar_en_horno("orden_A"))

    # ② Trabajo independiente: se ejecuta MIENTRAS τᵢ espera en el horno
    ensalada = preparar_ensalada()       # exec(τⱼ) — no requiere await
    guarnicion = preparar_guarnicion()   # exec(τⱼ) — no requiere await

    # ③ Punto de dependencia: aquí necesitamos el resultado de A
    plato_A = await tarea_A    # si ya terminó → sin espera; si no → espera mínima

    # ④ Emplatar con todo listo
    return emplatar(plato_A, ensalada, guarnicion)
```

### create_task vs gather: cuándo usar cada uno

```python
# gather — barrera: espera TODOS, recibe lista de resultados en orden
resultados = await asyncio.gather(fn_A(), fn_B(), fn_C())
# resultados[0]=A, resultados[1]=B, resultados[2]=C (siempre en orden)

# create_task — flexible: await en el punto de dependencia exacto
tarea_A = asyncio.create_task(fn_A())
tarea_B = asyncio.create_task(fn_B())
# ... trabajo intermedio ...
resultado_A = await tarea_A    # cuando necesito A
# ... más trabajo ...
resultado_B = await tarea_B    # cuando necesito B
```

`gather` es una barrera: el código no continúa hasta que **todos** terminan. `create_task + await` es más fino: el await ocurre exactamente donde se necesita cada resultado. La concurrencia producida es la misma — la diferencia es el control de flujo.

---

## asyncio.as_completed — procesar conforme llegan

Cuando tienes N tareas y quieres procesar cada resultado **tan pronto como esté disponible** (no esperar el más lento para obtener el más rápido):

```python
import asyncio

tareas = [
    asyncio.create_task(buscar_en_fuente("wikipedia", query)),
    asyncio.create_task(buscar_en_fuente("arxiv", query)),
    asyncio.create_task(buscar_en_fuente("github", query)),
]

# Procesa resultados conforme llegan — no en orden de creación
async for tarea in asyncio.as_completed(tareas):
    resultado = await tarea    # await aquí nunca bloquea — ya terminó
    procesar_parcialmente(resultado)
    print(f"  resultado recibido: {resultado[:50]}...")
```

**En la analogía:** el chef no espera a que todos los platos de la mesa estén listos para llevarlos — lleva cada plato al comensal tan pronto como sale del horno.

**Cuándo usar:** cuando las tareas tienen duraciones variables y quieres minimizar latencia del primer resultado, o cuando cada resultado puede procesarse independientemente.

---

## asyncio.wait con FIRST_COMPLETED — reaccionar al primero

```python
tareas = {asyncio.create_task(fn()) for fn in [fuente_a, fuente_b, fuente_c]}

# Espera hasta que UNA tarea complete
completadas, pendientes = await asyncio.wait(
    tareas,
    return_when=asyncio.FIRST_COMPLETED
)

# Cancela las que no terminaron
for t in pendientes:
    t.cancel()

resultado = completadas.pop().result()
```

**Cuándo usar:** búsqueda en múltiples fuentes donde solo necesitas la primera respuesta, timeout con cancelación, race entre alternativas.

---

## asyncio.Queue — productor-consumidor

La Queue es el **ticket rail de la cocina**: los pedidos entran por un lado, los cocineros los toman del otro. Desacopla la velocidad de producción de la velocidad de consumo.

```python
import asyncio

async def productor(queue: asyncio.Queue, items: list):
    """Genera trabajo y lo pone en la queue"""
    for item in items:
        await queue.put(item)
        print(f"  productor: puso {item} (qsize={queue.qsize()})")
        await asyncio.sleep(0.1)   # simula llegada de peticiones
    await queue.put(None)          # sentinel: indica fin de trabajo

async def consumidor(queue: asyncio.Queue, nombre: str):
    """Toma trabajo de la queue y lo procesa"""
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        print(f"  {nombre}: procesando {item}")
        await asyncio.sleep(0.3)   # simula I/O de procesamiento
        queue.task_done()

async def pipeline(items: list, n_workers: int = 2):
    queue = asyncio.Queue(maxsize=5)   # buffer limitado
    await asyncio.gather(
        productor(queue, items),
        *[consumidor(queue, f"worker-{i}") for i in range(n_workers)]
    )

# asyncio.run(pipeline(list(range(10)), n_workers=3))
```

**Propiedades formales:**

```
Queue = (Workers, Q_buffer)
maxsize > 0: put() hace await si Q lleno → backpressure natural
get() hace await si Q vacío → workers no consumen CPU en espera activa
```

**Cuándo usar:** procesamiento de streaming, rate limiting, separar responsabilidades de producción y consumo.

---

## Anti-patrones con consecuencias formales

### 1. time.sleep en función async

```python
# ❌ Anti-patrón
async def tarea():
    time.sleep(2)       # bloquea el hilo del OS → event loop congelado

# Consecuencia formal:
# ∀ τₖ ≠ τᵢ, ∀ t ∈ sleep_interval:  τₖ ∉ ExecutingAt(t)
# El event loop no puede ejecutar NADA durante el time.sleep
# M4 colapsa a M1 o peor
```

```python
# ✓ Correcto
async def tarea():
    await asyncio.sleep(2)   # libera event loop → otras coroutines ejecutan
```

### 2. Código CPU-bound en coroutine

```python
# ❌ Anti-patrón
async def calcular_embedding(texto: str) -> list:
    # Esto es CPU-bound: no tiene await, no libera el event loop
    vector = modelo_local.encode(texto)   # puede tardar 500ms
    return vector

# Consecuencia formal:
# ∀ t ∈ [inicio_encode, fin_encode]:  ExecutingAt(t) = {τᵢ}
# Ninguna otra coroutine puede ejecutar durante esos 500ms
# El chatbot deja de atender a todos los usuarios mientras calcula UN embedding
```

```python
# ✓ Correcto: delegar a un executor
async def calcular_embedding(texto: str) -> list:
    loop = asyncio.get_event_loop()
    # run_in_executor descarga el trabajo a un hilo (o proceso) separado
    # el event loop queda libre para otras coroutines
    vector = await loop.run_in_executor(None, modelo_local.encode, texto)
    return vector
```

Para tareas CPU-bound intensas, usa `ProcessPoolExecutor` en lugar de `None` (ThreadPoolExecutor) para escapar el GIL:

```python
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor(max_workers=4)

async def calcular_embedding(texto: str) -> list:
    loop = asyncio.get_event_loop()
    vector = await loop.run_in_executor(executor, modelo_local.encode, texto)
    return vector
```

### 3. Fire-and-forget sin tracking

```python
# ❌ Anti-patrón
async def servidor():
    for peticion in peticiones:
        asyncio.create_task(handle(peticion))   # sin guardar referencia
        # Si handle() lanza una excepción → silenciada completamente
        # No hay forma de saber qué falló ni cuándo

# Python puede advertir: "Task exception was never retrieved"
```

```python
# ✓ Correcto: guardar referencias y manejar excepciones
async def servidor():
    tareas = set()
    for peticion in peticiones:
        t = asyncio.create_task(handle(peticion))
        tareas.add(t)
        t.add_done_callback(tareas.discard)  # cleanup automático al terminar
        t.add_done_callback(log_si_error)    # logging de errores

def log_si_error(tarea):
    if not tarea.cancelled() and tarea.exception():
        print(f"ERROR en tarea: {tarea.exception()}")
```

### 4. await inmediato después de create_task

```python
# ❌ Anti-patrón (create_task es inútil aquí)
async def main():
    tarea = asyncio.create_task(fn_A())
    resultado = await tarea              # await INMEDIATO — ningún trabajo pudo ocurrir
    # Equivale exactamente a: resultado = await fn_A()
    # create_task solo añadió overhead sin beneficio
```

```python
# ✓ Correcto: trabajo intermedio entre create_task y await
async def main():
    tarea = asyncio.create_task(fn_A())
    resultado_B = await fn_B()           # trabajo independiente ocurre AQUÍ
    resultado_A = await tarea            # ahora el await tiene sentido
```

### 5. awaits secuenciales de tareas independientes

```python
# ❌ Anti-patrón
async def obtener_datos(user_id):
    historial = await consultar_bd(user_id)    # espera BD antes de empezar LLM
    contexto = await consultar_cache(user_id)  # espera caché antes de empezar LLM
    respuesta = await llamar_llm(historial, contexto)
    return respuesta
# Tiempo: T_bd + T_cache + T_llm
```

```python
# ✓ Correcto: tareas independientes en paralelo
async def obtener_datos(user_id):
    # BD y caché son independientes — lanzar juntas
    historial, contexto = await asyncio.gather(
        consultar_bd(user_id),
        consultar_cache(user_id)
    )
    # LLM depende de ambas — espera aquí es correcto
    respuesta = await llamar_llm(historial, contexto)
    return respuesta
# Tiempo: max(T_bd, T_cache) + T_llm  ← mejora real
```

---

## Tabla de resumen: cuándo usar cada mecanismo

| Mecanismo | Semántica | Cuándo usar | Anti-patrón relacionado |
|-----------|-----------|-------------|------------------------|
| `await fn()` | Ejecuta y espera, secuencial | Una tarea, o dependencia estricta | Usarlo en tareas independientes |
| `gather(*fns)` | Barrera: espera todas | N tareas independientes, necesitas todos los resultados | Usarlo cuando los resultados se necesitan en momentos distintos |
| `create_task + await` | Lanzar y esperar en punto de dependencia | Trabajo independiente entre lanzamiento y resultado | Await inmediato (inútil) o sin await (fire-and-forget) |
| `as_completed` | Iterar por orden de llegada | N tareas con duraciones variables, procesar parcialmente | Esperar el más lento para procesar el más rápido |
| `wait(FIRST_COMPLETED)` | El primero en terminar, cancelar el resto | Race entre alternativas, timeout | Dejar tareas canceladas sin cleanup |
| `Queue` | Desacoplar producción y consumo | Streaming, N productores / M consumidores | Queue sin sentinel (consumidores nunca terminan) |

---

:::exercise{title="Diagnosticar anti-patrones"}
Lee cada fragmento y determina: (1) qué anti-patrón es, (2) cuál es la consecuencia formal, (3) cómo corregirlo.

```python
# Fragmento A
async def buscar(query):
    r1 = await buscar_en_bd(query)
    r2 = await buscar_en_cache(query)
    r3 = await buscar_en_api(query)
    return [r1, r2, r3]

# Fragmento B
async def procesar():
    tarea = asyncio.create_task(calcular())
    resultado = await tarea
    return resultado

# Fragmento C
async def servidor():
    while True:
        peticion = await recibir_peticion()
        asyncio.create_task(handle(peticion))
```
:::
