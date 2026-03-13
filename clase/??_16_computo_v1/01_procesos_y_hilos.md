---
title: "Procesos, Hilos y el GIL"
---

# Procesos, Hilos y el GIL

Antes de hablar de concurrencia o paralelismo, necesitamos tener claro qué es lo que se ejecuta. Todo modelo de ejecución opera sobre procesos y hilos. En este archivo los definimos con precisión — en los tres lenguajes que usaremos en todo el módulo: la analogía, el cómputo y las matemáticas.

---

## La analogía: el restaurante

Usaremos un restaurante como modelo del sistema computacional. Esta analogía se define **una sola vez aquí** y se referenciará en todos los archivos del módulo sin redefinirla.

### Tabla de correspondencia completa

| Analogía (cocina) | Cómputo (OS/Python) | Matemáticas |
|---|---|---|
| **Restaurante** | Computadora | — |
| **Fogón / quemador** | CPU core | c ∈ Cores, \|Cores\| = P |
| **Despensa / refrigerador** | RAM (espacio de memoria) | Mem: Addr → Value |
| **Horno, cafetera, tostadora** | Dispositivo I/O (disco, red, GPU) | IO = {disk, net, gpu, ...} |
| **Pared sellada entre estaciones** | Aislamiento de memoria entre procesos | Mem(pᵢ) ∩ Mem(pⱼ) = ∅ |
| **Estación de cocina** (tiene su propia despensa) | Proceso | p ∈ Proc |
| **Cocinero** (trabaja dentro de una estación) | Hilo | θ ∈ Thread(p) |
| **Despensa compartida entre cocineros** | Heap compartido dentro del proceso | ∀ θₐ, θᵦ ∈ Thread(p): comparten Mem(p) |
| **Chef jefe / tablero de órdenes** | Scheduler del OS | sched: Thread → Core × Time |
| **Timbre de turno** (cada N segundos) | Quantum de scheduling | q ∈ ℝ⁺ |
| **Cambiar al cocinero en el fogón** | Context switch | overhead δ_ctx > 0 por switch |
| **Mensajero entre estaciones** | IPC (pipe, queue, socket) | msg: Proc × Proc → Data |
| **El único juego de cuchillos** (Python) | GIL | ver sección GIL más abajo |
| **Ticket de orden** | Tarea | τᵢ ∈ Task |
| **Cocinero trabajando activamente** (corta, mezcla, emplata) | CPU execution | exec(τᵢ) ⊆ T |
| **Orden esperando en el horno / timer** | I/O wait | wait(τᵢ) ⊆ T |

---

## Proceso

Un **proceso** es un programa en ejecución con su propio espacio de memoria aislado.

**En la cocina:** una estación de trabajo con su propia despensa, utensilios y área de trabajo. Ninguna otra estación puede meter la mano en su refrigerador.

**En cómputo:** el OS crea un proceso cuando lanzas un programa. Tiene su propio heap, stack, descriptores de archivo y variables de entorno. La comunicación con otros procesos requiere mecanismos explícitos (IPC).

**Formalmente:**
```
Proc = conjunto de procesos en ejecución
p ∈ Proc
Mem(p) = espacio de direcciones del proceso p

Aislamiento:  ∀ pᵢ, pⱼ ∈ Proc, i ≠ j:  Mem(pᵢ) ∩ Mem(pⱼ) = ∅
```

---

## Hilo (Thread)

Un **hilo** es una unidad de ejecución dentro de un proceso. Múltiples hilos del mismo proceso comparten su memoria.

**En la cocina:** cocineros que trabajan en la misma estación. Todos usan la misma despensa — si uno mueve un ingrediente, los demás lo ven.

**En cómputo:** un proceso puede tener H ≥ 1 hilos. Todos comparten el heap del proceso pero tienen su propio stack y contador de programa. El OS los puede asignar a distintos cores.

**Formalmente:**
```
Thread(p) = conjunto de hilos del proceso p
θ ∈ Thread(p)

Memoria compartida:  ∀ θₐ, θᵦ ∈ Thread(p):  ambos acceden a Mem(p)
```

### Diagrama de memoria

```
┌─────────────────────────────┐    ┌─────────────────────────────┐
│        Proceso A            │    │        Proceso B            │
│  ┌──────────────────────┐   │    │  ┌──────────────────────┐   │
│  │    Heap de A         │   │    │  │    Heap de B         │   │
│  │  (variables, objetos)│   │    │  │  (variables, objetos)│   │
│  └──────────────────────┘   │    │  └──────────────────────┘   │
│  ┌────────┐  ┌────────┐     │    │  ┌────────┐  ┌────────┐     │
│  │Hilo θ₁ │  │Hilo θ₂ │     │    │  │Hilo θ₃ │  │Hilo θ₄ │     │
│  │stack   │  │stack   │     │    │  │stack   │  │stack   │     │
│  └────────┘  └────────┘     │    │  └────────┘  └────────┘     │
│  θ₁ y θ₂ comparten Heap A  │    │  θ₃ y θ₄ comparten Heap B  │
└─────────────────────────────┘    └─────────────────────────────┘
       Mem(A) ∩ Mem(B) = ∅
```

---

## I/O-bound vs CPU-bound

Esta distinción es fundamental para todo el módulo. Anticipamos aquí la notación formal que se definirá completamente en `02_secuencial.md`:

**CPU-bound** — la tarea requiere trabajo continuo del procesador; no usa dispositivos externos:
```
CPU-bound  ≡  wait(τᵢ) = ∅
```
*En la cocina:* trabajo puro de cuchillo — cortar, mezclar, batir. El cocinero no puede alejarse.

Ejemplos en el chatbot: ejecutar el modelo de lenguaje localmente, comprimir datos, calcular embeddings.

**I/O-bound** — la tarea delega trabajo a dispositivos externos y espera su respuesta:
```
I/O-bound  ≡  wait(τᵢ) ≠ ∅
```
*En la cocina:* poner algo en el horno o la cafetera. El cocinero puede alejarse mientras el dispositivo trabaja.

Ejemplos en el chatbot: consultar la base de datos del usuario, llamar a la API del LLM, leer de disco.

> Esta distinción determina **qué modelo de ejecución conviene usar** — es la pregunta más importante a responder antes de elegir entre asyncio, threading o multiprocessing.

---

## Context Switch y Quantum

El **scheduler** del OS asigna CPU cores a hilos. Para dar la ilusión de que múltiples hilos avanzan simultáneamente en un solo core, el scheduler usa **time-slicing**: cada hilo tiene un **quantum** de tiempo q (típicamente 1–100ms), y al agotarse el scheduler ejecuta un **context switch**.

**En la cocina:** el chef jefe pone un timbre. Cuando suena, el cocinero en el fogón debe soltar exactamente lo que está haciendo, anotar su estado ("estaba en el paso 3 de la salsa"), y el siguiente cocinero toma su lugar.

**Formalmente:**
```
q ∈ ℝ⁺          quantum de scheduling (duración máxima de un turno)
δ_ctx > 0        overhead de context switch (guardar/restaurar estado)
```

> **Implicación importante:** si se hacen demasiados context switches, el overhead δ_ctx × N_switches puede superar el trabajo útil realizado. Esto importa cuando veamos el Modelo 3 (concurrent sin async).

---

## El GIL — Global Interpreter Lock

El GIL es una restricción **específica de CPython** (la implementación estándar de Python). Es la razón por la que threading en Python no produce paralelismo real para tareas CPU-bound.

**En la cocina:** hay un único juego de cuchillos de chef en toda la estación. Cualquier cocinero que quiera trabajar activamente debe tomar los cuchillos. Solo uno puede tenerlos a la vez.

**Formalmente:**
```
GIL constraint:
∀ t: |{θ ∈ Thread(p) | θ ejecuta bytecode Python en t}| ≤ 1

En cualquier instante, a lo mucho UN hilo por proceso puede ejecutar
bytecode Python — sin importar cuántos cores físicos tenga la máquina.
```

**La excepción crítica:** durante `wait(τᵢ)` (espera de I/O), el GIL se libera:
```
Durante wait(τᵢ): el hilo θᵢ suelta el GIL
→ otro hilo θⱼ puede tomarlo y ejecutar
→ por eso threading SÍ funciona para I/O-bound
→ por eso threading NO funciona para CPU-bound
```

**En la cocina:** mientras una orden está en el horno (I/O wait), el cocinero suelta los cuchillos. Otro cocinero puede tomarlos y trabajar. Pero si la tarea es pure-knife work (CPU-bound), el cocinero nunca suelta los cuchillos, y los demás esperan sin poder hacer nada útil.

| Tipo de tarea | GIL durante ejecución | Threading ayuda |
|---|---|---|
| CPU-bound (wait = ∅) | Nunca se libera | No — serializa los hilos |
| I/O-bound (wait ≠ ∅) | Se libera durante el wait | Sí — otro hilo avanza |

---

## El chatbot v0: nuestro servidor como proceso

Nuestro chatbot es un programa Python. Cuando lo ejecutamos:

```
python servidor_chatbot.py
```

El OS crea un **proceso** con su propio Mem(p). Por defecto tiene un hilo principal (el event loop, o el hilo de ejecución secuencial). Las peticiones de los usuarios son **tareas** τᵢ que el servidor debe procesar.

Cada petición de chatbot involucra:
- Consultar historial del usuario en la BD → **I/O-bound** (wait ≠ ∅)
- Llamar a la API del LLM en la nube → **I/O-bound** (wait ≠ ∅)
- (Si modelo local) ejecutar inferencia → **CPU-bound** (wait = ∅)

Esto determinará qué modelos de ejecución son apropiados para cada parte. Lo veremos en detalle en los archivos siguientes.

---

:::exercise{title="Reflexión previa al código"}
Antes de abrir el notebook, responde: si tu chatbot recibe 10 peticiones simultáneas y cada una tarda 2 segundos en completarse, ¿cuánto tiempo espera el último usuario con un servidor secuencial? ¿Qué necesitarías cambiar para que todos esperen aproximadamente 2 segundos?
:::
