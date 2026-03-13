---
title: "Concurrencia, Asincronía y los Modelos M2–M4"
---

# Concurrencia, Asincronía y los Modelos M2–M4

En `02_secuencial.md` establecimos el framework matemático completo y vimos M1. Ahora definimos dos propiedades nuevas — **concurrencia** y **asincronía** — y construimos los tres modelos que resultan de combinarlas. Son propiedades ortogonales: una puede existir sin la otra.

---

## Definiciones formales

Usamos el framework de `02_secuencial.md`: T, τᵢ, exec, wait, ExecutingAt, P.

### Concurrencia

```
Concurrencia:
∃ τᵢ, τⱼ ∈ Task, i ≠ j:
    [start(τᵢ), end(τᵢ)] ∩ [start(τⱼ), end(τⱼ)] ≠ ∅
```

Los **ciclos de vida** de al menos dos tareas se solapan. τⱼ empieza antes de que τᵢ termine.

*En la cocina:* el cocinero tiene más de un ticket activo al mismo tiempo. Hay dos órdenes "en progreso" aunque no las trabaje simultáneamente.

> **Concurrencia ≠ Paralelismo.** Concurrencia es solapamiento de ciclos de vida — puede ocurrir con P=1 mediante time-slicing. Paralelismo es ejecución física simultánea — requiere P≥2. La relación formal (Paralelo ⊃ Concurrente) se demuestra en `05_paralelismo.md`.

### Tarea async-capable (I/O-bound)

```
Tarea async-capable:  wait(τᵢ) ≠ ∅
```

La tarea tiene al menos un instante de espera a un dispositivo externo. Esto es idéntico a "I/O-bound" definido en `01_procesos_y_hilos.md`. La denominación "async-capable" enfatiza que **tiene la capacidad** de liberar la CPU durante sus esperas — si el sistema decide explotarlas.

*En la cocina:* una orden que pasa por el horno. El cocinero **podría** alejarse mientras espera — pero no tiene por qué hacerlo.

### Sistema asíncrono (explotación de esperas)

```
Sistema asíncrono:
∃ τᵢ, τⱼ ∈ Task, i ≠ j:
    exec(τⱼ) ∩ wait(τᵢ) ≠ ∅
```

Mientras τᵢ espera un dispositivo externo, el sistema asigna la CPU a τⱼ. Las esperas se **explotan** para avanzar otras tareas.

*En la cocina:* el cocinero, al poner una orden en el horno, **consulta su lista de pendientes** y toma la siguiente orden en lugar de esperar parado.

> **Distinción crítica:** una tarea puede ser async-capable (tener wait ≠ ∅) sin que el sistema los explote. La propiedad (2) es **capacidad**; la propiedad (3) es **uso de esa capacidad**. M2 demuestra exactamente este caso.

---

## La matriz de 4 combinaciones

```
                      SISTEMA ASÍNCRONO
                      (esperas explotadas)
                      NO                    SÍ
               ┌──────────────────┬──────────────────────┐
  CONCURRENTE  │                  │                       │
  (solapamiento│  M3              │  M4  ← destino       │
   ciclos vida)│  Concurrent      │  Concurrent           │
  SÍ           │  no async        │  + async (asyncio)    │
               ├──────────────────┼──────────────────────┤
  CONCURRENTE  │                  │                       │
  NO           │  M1              │  M2                   │
               │  Secuencial      │  Async no             │
               │  (02_secuencial) │  concurrent           │
               └──────────────────┴──────────────────────┘
```

M1 ya lo conocemos. Vemos M2, M3 y M4 en este archivo. M5 (paralelo) y M6 (distribuido) en los siguientes.

---

## Modelo 2 — Async no concurrent (M2)

### Qué es M2

M2 existe cuando el código tiene infraestructura asíncrona pero la **usa de forma secuencial**. Las tareas tienen wait(τᵢ) ≠ ∅ (son async-capable) pero el sistema no las explota: `exec(τⱼ) ∩ wait(τᵢ) = ∅` para todo i ≠ j.

```
M2 — Async no concurrent:
∀ τᵢ, τⱼ ∈ Task, i ≠ j:
    wait(τᵢ) ≠ ∅  (las esperas existen...)
    exec(τⱼ) ∩ wait(τᵢ) = ∅  (...pero nunca se explotan)
```

### El insight: congelamiento de flujo

```python
# M2 — await secuencial (incorrecto para concurrencia)
async def procesar_usuarios():
    await atender(usuario_1)   # ← flujo se CONGELA aquí
    await atender(usuario_2)   # usuario_2 no se crea hasta que usuario_1 termina
    await atender(usuario_3)   # ídem
```

`await atender(usuario_1)` congela el flujo: `usuario_2` nunca se crea hasta que `usuario_1` termina completamente. **No es un problema del event loop — es un problema de diseño del código.** El event loop existe y funciona, pero el programador no lo aprovecha.

Esto es **equivalente a código bloqueante** para el propósito de la concurrencia. El hecho de usar `async`/`await` no garantiza concurrencia.

### Diagrama de Gantt — M2

Tres tareas I/O-bound ejecutadas con `await` secuencial:

```
Tiempo →  0    1    2    3    4    5    6    7    8    9

τ₁:       [exec░░░░░░exec]
τ₂:                        [exec░░░░░░exec]
τ₃:                                       [exec░░░░░░exec]
CPU:      [████░░░░░░████] [████░░░░░░████] [████░░░░░░████]

████ = ejecución CPU activa   ░░░ = CPU idle (wait no explotado)
```

Idéntico a M1. Los ciclos de vida no se solapan. El async no produce ninguna mejora.

**Valor pedagógico de M2:** nos enseña que la sintaxis asíncrona no garantiza beneficio. Lo que importa es si las esperas se explotan o no.

---

## Modelo 3 — Concurrent no async (M3)

### Qué es M3

M3 tiene solapamiento de ciclos de vida (concurrencia) pero **todas las tareas son CPU-bound** — no hay esperas que explotar. La CPU se comparte por time-slicing.

```
M3 — Concurrent no async:
∃ τᵢ, τⱼ: [start(τᵢ), end(τᵢ)] ∩ [start(τⱼ), end(τⱼ)] ≠ ∅   (concurrencia)
∀ τᵢ ∈ Task: wait(τᵢ) = ∅   (todas CPU-bound, sin esperas)
P = 1 (un solo core activo — por construcción del modelo)
```

El scheduler divide el tiempo de CPU en **quanta** de duración q. Cada hilo recibe un quantum, luego cede el core al siguiente.

### READY ≠ WAIT

El scheduler del OS distingue dos estados de espera muy diferentes:

```
Estado READY:  el hilo quiere ejecutar, espera su turno de CPU
               → wait del scheduler, NO wait(τᵢ) de I/O
               → τᵢ sigue siendo CPU-bound, el OS simplemente lo pausó

Estado WAIT:   el hilo espera un dispositivo externo (I/O)
               → esto sí es wait(τᵢ) ≠ ∅ — es el wait de nuestro framework
               → el hilo voluntariamente cede la CPU
```

Un hilo en READY no ha terminado su CPU-work — fue interrumpido por el scheduler. Un hilo en WAIT no puede avanzar hasta que el dispositivo responda.

### Diagrama de Gantt — M3

Dos tareas CPU-bound con time-slicing (quantum q):

```
Tiempo →  0    q   2q   3q   4q   5q   6q   7q   8q

τ₁:       [████]   [████]   [████]   [████]
τ₂:            [████]   [████]   [████]   [████]
CPU:      [████████████████████████████████████████]

(sin overhead de context switch para simplificar)
Los ciclos de vida se solapan: start(τ₂) < end(τ₁) ✓
```

Los ciclos de vida se solapan (hay concurrencia), pero la CPU nunca está ociosa — no hay waits que explotar.

### El GIL y M3 en Python

En Python con CPython, threading con tareas CPU-bound produce M3 — con un problema adicional:

```
GIL constraint: ∀ t: |{θ ∈ Thread(p) ejecutando bytecode en t}| ≤ 1
```

El GIL hace que `exec(τᵢ) ∩ exec(τⱼ) = ∅` incluso con múltiples hilos y múltiples cores. El resultado: **casi-M1 con overhead de context switch**. Los hilos se turnan por el GIL en lugar de por el scheduler del OS, y cada cambio tiene un costo δ_ctx > 0.

> **Resultado práctico:** usar `threading` para tareas CPU-bound en Python produce M3 degradado — concurrencia sin paralelismo ni asincronía. Es lo peor de todos los mundos para ese tipo de tarea. La solución para CPU-bound es `multiprocessing` (M5), que escapa del GIL creando procesos separados.

---

## Modelo 4 — Concurrent AND async (M4)

M4 es el destino de esta clase. Es el modelo que asyncio implementa.

### Definición formal

```
M4 — Concurrent + async:
∃ τᵢ, τⱼ: [start(τᵢ), end(τᵢ)] ∩ [start(τⱼ), end(τⱼ)] ≠ ∅   (concurrencia)
∃ τₖ ∈ Task: wait(τₖ) ≠ ∅                                      (hay esperas)
∃ i ≠ j: exec(τⱼ) ∩ wait(τᵢ) ≠ ∅                              (esperas explotadas)
P = 1, H = 1   (un core, un hilo — el event loop)
```

A diferencia de M3, aquí las tareas son I/O-bound: tienen `wait(τᵢ) ≠ ∅`. El sistema las **explota**.

### El event loop en la analogía

El event loop es la **lista de pendientes del cocinero**:

1. El cocinero toma el primer ticket y empieza a trabajar (exec)
2. Al llegar a una espera — la orden entra al horno (wait) — el cocinero **no se queda parado**
3. Consulta su lista: ¿hay otro ticket listo para trabajar?
4. Toma el siguiente y trabaja en él (exec de τⱼ durante wait de τᵢ)
5. Cuando el timer del horno avisa (I/O completado), τᵢ vuelve a la lista como READY
6. El cocinero la retoma cuando termina la tarea actual

Un solo cocinero (H=1), un solo fogón (P=1), máxima utilización de la cocina.

### Diagrama de Gantt — M4

Tres tareas I/O-bound con event loop:

```
Tiempo →  0    1    2    3    4    5    6    7    8    9   10

τ₁:       [exec░░░░░░░░░░░░exec]
τ₂:            [exec░░░░░░░░exec]
τ₃:                 [exec░░░░░░░░exec]
CPU:      [████████████] [████████████] [████]  (sin idle*)

(*CPU idle solo si TODAS las tareas esperan simultáneamente)
Explotan esperas: exec(τ₂) ∩ wait(τ₁) ≠ ∅ ✓
                  exec(τ₃) ∩ wait(τ₁) ≠ ∅ ✓
```

Comparar con M1/M2: con las mismas 3 tareas, M4 elimina casi todo el tiempo idle de la CPU.

### La imagen de los 6 modelos

![Gantt comparativo de los 6 modelos de ejecución](./images/gantt_modelos.png)

---

## Condición de carrera (Race Condition)

M3 y M4 comparten memoria del proceso entre hilos/coroutines. Esto introduce un riesgo: **condiciones de carrera**.

### El problema

```python
contador = 0  # compartido entre hilos

def incrementar():
    global contador
    for _ in range(100_000):
        contador += 1  # NO es atómico

# contador += 1 se compila en 3 instrucciones:
#   LOAD_GLOBAL contador
#   LOAD_CONST 1
#   BINARY_OP +
#   STORE_GLOBAL contador
# El scheduler puede interrumpir entre cualquiera de estas instrucciones
```

Si dos hilos ejecutan `contador += 1` "simultáneamente", pueden leer el mismo valor antes de que el otro lo actualice — y uno de los incrementos se pierde. El resultado es **no determinista** y siempre menor que el esperado.

### La solución: Lock

```python
import threading

contador = 0
lock = threading.Lock()

def incrementar():
    global contador
    for _ in range(100_000):
        with lock:          # solo un hilo entra a la vez
            contador += 1  # ahora sí es efectivamente atómico
```

```
Lock:
∀ t: |{θ ∈ Thread(p) | θ tiene el lock en t}| ≤ 1
```

El lock garantiza exclusión mutua: mientras θₐ tiene el lock, θᵦ espera. El overhead existe — medir es siempre mejor que asumir — pero la correctitud es no negociable.

> **Nota en M4 / asyncio:** las coroutines en Python son cooperativas — ceden el control solo en los `await`. No hay context switch en mitad de una operación, por lo que `contador += 1` en una coroutine síncrona no tiene race condition. Pero si hay `await` entre el read y el write de una variable compartida, el problema reaparece.

---

## Chatbot v2: el problema planteado

El chatbot v1 (M1) tiene latencia inaceptable con múltiples usuarios. Con 100 usuarios simultáneos:

```
Chatbot v1 (M1): end(τ_u1) ≤ start(τ_u2) ≤ ... ≤ start(τ_u100)
Si cada petición tarda 2s:  Latencia(τ_u100) = 200s  ← completamente inaceptable
```

**El diagnóstico:** cada petición es I/O-bound:

```
τ_uᵢ: wait(τ_uᵢ) ≠ ∅

Desglose de una petición:
  exec: parsear petición, formatear respuesta     → pequeño
  wait: leer historial de BD                      → ~50ms
  wait: llamar API del LLM                        → ~1500ms
  wait: escribir respuesta a BD                   → ~20ms

Fracción de tiempo en wait ≈ 97%
```

**La solución correcta es M4:** como `wait(τᵢ) ≠ ∅` para todas las peticiones, el event loop puede ejecutar `exec(τⱼ)` mientras `τᵢ` espera. Con 100 usuarios:

```
M4 ideal (sin overhead):
  Latencia(τ_uᵢ) ≈ 2s  para todos los usuarios (la mayoría del tiempo es wait en paralelo)
  T_total ≈ 2s  (en lugar de 200s)
```

M4 en P=1 es óptimo para esta carga porque:
1. Las peticiones son I/O-bound — el cuello de botella es la red/BD, no la CPU
2. No hay overhead de procesos adicionales ni de sincronización de memoria compartida
3. Un solo hilo gestiona 100+ usuarios concurrentes con `asyncio`

**La implementación de M4 (chatbot v2 con asyncio) está en `04a_asyncio_fundamentos.md`.**

---

## Resumen: comparando M1–M4

| Modelo | Ciclos solapados | Esperas explotadas | CPU durante wait | Caso de uso |
|--------|-----------------|-------------------|-----------------|-------------|
| M1 | No | No | Idle | Tareas independientes simples |
| M2 | No | No (async sin gather) | Idle | Anti-patrón — evitar |
| M3 | Sí | No (CPU-bound) | Trabajando | CPU-bound con GIL → peor que M1 |
| M4 | Sí | Sí | Trabajando en otra tarea | I/O-bound concurrente ← correcto |

---

:::exercise{title="Clasificar modelos de ejecución"}
Para cada escenario, indica qué modelo (M1–M4) describe mejor la situación y justifica con las definiciones formales:

1. Un script que hace `requests.get(url1)`, luego `requests.get(url2)`, luego `requests.get(url3)` de forma bloqueante.
2. Un servidor asyncio que usa `await asyncio.gather(tarea1(), tarea2(), tarea3())` donde cada tarea hace una llamada HTTP.
3. Un programa con 4 hilos que calculan embeddings de texto (operación CPU-bound) en CPython.
4. Un servidor asyncio que usa `await tarea1(); await tarea2(); await tarea3()` en lugar de `gather`.
:::
