---
title: "Cómputo Distribuido — Introducción Conceptual y Síntesis"
---

# Cómputo Distribuido — Introducción Conceptual y Síntesis

Los modelos M1–M5 operan dentro de una sola máquina. El cómputo distribuido rompe esa frontera: múltiples máquinas físicamente separadas cooperan para resolver un problema. Este archivo es conceptual — la implementación real (Ray, Dask, sistemas de mensajería) es tema de un módulo posterior.

---

## Modelo 6 — Distribuido (M6)

### Definición

```
M6 — Distribuido:
N ≥ 2 nodos   (máquinas físicamente separadas)

Para todo nᵢ, nⱼ ∈ Nodos, i ≠ j:
  (1) Mem(nᵢ) ∩ Mem(nⱼ) = ∅        no hay memoria compartida entre nodos
  (2) δᵢⱼ > 0                        latencia de red no despreciable
  (3) ∄ reloj global                  no existe un reloj único y sincronizado
```

*En la cocina:* N restaurantes en ciudades distintas — cada uno con su propia despensa, su propia cocina y sus propios relojes. La comunicación entre restaurantes es por mensajero físico: tarda tiempo real en llegar.

### Las tres diferencias con el modelo paralelo

| Eje | Paralelo (M5) | Distribuido (M6) |
|-----|--------------|-----------------|
| **Ubicación** | Misma máquina física, mismo OS | Máquinas físicamente separadas |
| **Latencia de comunicación** | IPC del OS (pipe, queue): δ ≈ μs a ms | Red (HTTP, gRPC, TCP): δ ≈ ms a segundos |
| **Reloj** | Reloj de hardware compartido en la misma placa | No hay reloj global — relojes locales independientes |

> **Nota importante:** en Python, `multiprocessing` ya usa procesos con memoria aislada (`Mem(pᵢ) ∩ Mem(pⱼ) = ∅`). La diferencia entre paralelo y distribuido NO es "memoria compartida vs no" — es **latencia de comunicación y ubicación física**. Los procesos de multiprocessing en la misma máquina se comunican con latencia de μs vía IPC del OS. Los nodos distribuidos se comunican por red con latencia de ms a segundos.

### La analogía mapeada formalmente

```
Ciudad separada      ↔  nodo físico    ↔  nᵢ ∈ Nodos
Despensa propia      ↔  RAM del nodo   ↔  Mem(nᵢ), aislada
Mensajero entre ciudades  ↔  mensaje de red  ↔  msg: nᵢ → nⱼ
Tiempo de viaje del mensajero  ↔  latencia de red  ↔  δᵢⱼ > 0
Relojes de pared distintos  ↔  sin reloj global  ↔  ∄ t_global
```

---

## El problema del reloj global

En una sola máquina, existe un reloj de hardware que todos los procesos comparten. El OS puede ordenar eventos con precisión de nanosegundos.

En un sistema distribuido, cada nodo tiene su propio reloj de hardware — y estos relojes **divergen** inevitablemente por:

```
- Osciladores de cuarzo con frecuencias ligeramente distintas
- Temperatura y voltaje afectan la velocidad del reloj
- NTP (Network Time Protocol) sincroniza aproximadamente, con error de ms
```

### El problema concreto con el chatbot v4

Imagina el chatbot desplegado en dos servidores: uno en CDMX y uno en GDL.

```
Servidor CDMX (reloj local: 10:00:00.001):
  Petición de usuario_A llega
  timestamp_local = "10:00:00.001"

Servidor GDL (reloj local: 10:00:00.000 — 1ms adelantado):
  Petición de usuario_B llega
  timestamp_local = "10:00:00.000"

¿Cuál llegó primero?
  Por timestamps locales: usuario_B (GDL) parece anterior
  Por realidad física: puede haber llegado después
```

No podemos saber cuál llegó primero solo comparando timestamps locales de servidores distintos. Esto importa para: ordenamiento de transacciones, consistencia de historial, debugging de eventos distribuidos.

### La solución conceptual: Relojes Lógicos

Sin reloj global, los sistemas distribuidos usan **relojes lógicos** para ordenar eventos causalmente:

- **Relojes de Lamport:** cada nodo mantiene un contador entero. Al enviar un mensaje, incluye su contador. Al recibir, el receptor actualiza su contador al máximo + 1. Garantiza: si A causó B, entonces timestamp(A) < timestamp(B).

- **Relojes Vectoriales:** cada nodo mantiene un vector de contadores (uno por nodo). Permiten detectar concurrencia real entre eventos: dos eventos son concurrentes si ninguno causó al otro.

Ambas son soluciones al problema de ordenar eventos sin reloj global — sin implementación en este módulo.

---

## Chatbot v4 — el sistema distribuido

El chatbot creció de proceso único a sistema de múltiples máquinas:

```
                 Internet
    Usuarios ────────────→ Balanceador de carga (nginx)
                              │           │
                     ┌────────┴──┐   ┌────┴────────┐
                     │ Servidor  │   │  Servidor   │
                     │  CDMX     │   │   GDL       │
                     │ (v3: M5b) │   │  (v3: M5b)  │
                     └────┬──────┘   └──────┬──────┘
                          │                 │
                     ┌────┴─────────────────┴────┐
                     │     Cola de mensajes       │
                     │  (Redis / RabbitMQ)        │
                     └────────────────────────────┘
                          │
                     ┌────┴────────────────────┐
                     │    Workers LLM          │
                     │  (GPUs en la nube)      │
                     └─────────────────────────┘
```

**Propiedades del sistema:**

```
Cada servidor: Mem(CDMX) ∩ Mem(GDL) = ∅  ← sin memoria compartida
Comunicación: δ_CDMX↔GDL > 0             ← latencia de red real
Escalado: agregar servidores aumenta capacidad sin límite de cores
```

El balanceador de carga distribuye peticiones entre instancias. Las colas de mensajes desacoplan los servidores de los workers GPU. Cada componente escala independientemente.

**Scope de este módulo:** entender conceptualmente qué es M6 y por qué es diferente de M5. La implementación real (Ray, Dask, Celery, Kafka) requiere infraestructura específica y es tema de un módulo posterior.

---

## La evolución del chatbot: v1 → v4

```
Chatbot v1 — Secuencial (M1)
  Un usuario a la vez
  T_total = N × T_usuario
  Latencia con 100 usuarios: 200s
  ↓ problema: CPU idle durante I/O

Chatbot v2 — Concurrent + Async (M4)
  N usuarios simultáneos con asyncio
  T_total ≈ T_max_usuario
  Latencia con 100 usuarios: ~2s
  ↓ problema: inferencia local bloquea el event loop

Chatbot v3 — Parallel + Async (M5b)
  asyncio para I/O + ProcessPoolExecutor para inferencia
  Speedup de inferencia ≈ P (limitado por Amdahl)
  ↓ límite: una máquina tiene P cores finitos

Chatbot v4 — Distribuido (M6)
  Múltiples servidores + balanceador + cola de mensajes
  Escalado horizontal: agregar máquinas sin límite de cores
  Desafíos: consistencia, latencia de red, ausencia de reloj global
```

---

## Síntesis final: los 6 modelos

| Modelo | Condición formal clave | Analogía | Caso de uso Python | Librería principal |
|--------|----------------------|----------|-------------------|-------------------|
| **M1** Secuencial | end(τᵢ) ≤ start(τⱼ) | Cocinero: una orden completa antes de la siguiente | Script de procesamiento simple | (ninguna) |
| **M2** Async no concurrent | wait ≠ ∅ pero exec(τⱼ) ∩ wait(τᵢ) = ∅ | Horno activo, cocinero parado frente a él | `await fn1(); await fn2()` | asyncio (mal usado) |
| **M3** Concurrent no async | Solapamiento, wait = ∅, P=1 | Dos tickets activos, todo es trabajo de cuchillo | threading con CPU-bound | `threading` (ineficiente) |
| **M4** Concurrent + async | exec(τⱼ) ∩ wait(τᵢ) ≠ ∅, H=1 | Cocinero con lista de pendientes, aprovecha el horno | Servidor I/O-bound, chatbot v2 | `asyncio` |
| **M5a** Paralelo puro | ∃t: exec(τᵢ) ∩ exec(τⱼ) ≠ ∅, wait=∅ | Dos estaciones CPU-bound trabajando a la vez | Procesamiento numérico masivo | `ProcessPoolExecutor`, `joblib` |
| **M5b** Paralelo + async | ∃t: exec(τᵢ) ∩ exec(τⱼ) ≠ ∅, wait≠∅ | Dos estaciones con hornos, coordinadas | Chatbot v3, server con inferencia local | `asyncio` + `ProcessPoolExecutor` |
| **M6** Distribuido | N≥2 nodos, Mem(nᵢ) ∩ Mem(nⱼ) = ∅, δᵢⱼ>0, ∄ reloj global | N restaurantes en ciudades distintas | Chatbot v4 escalado horizontal | Ray, Dask, Celery (fuera de alcance) |

### La jerarquía

```
Distribuido ⊇ Paralelo ⊇ Concurrente    (jerarquía de alcance)
Asíncrono: ortogonal — se combina con cualquier nivel

Dentro de Python:
  Concurrente (M3, M4): mismo proceso o mismo OS
  Paralelo (M5): múltiples procesos, misma máquina
  Distribuido (M6): múltiples máquinas, red de por medio
```

---

:::exercise{title="Reflexión de cierre"}
Regresa al ejercicio de `01_procesos_y_hilos.md`: "si tu chatbot recibe 10 peticiones simultáneas y cada una tarda 2 segundos, ¿cuánto tiempo espera el último usuario?"

Ahora responde para los 4 modelos:

1. **v1 (M1):** latencia del usuario 10
2. **v2 (M4):** latencia del usuario 10 (las peticiones son I/O-bound con ~1.95s de wait)
3. **v3 (M5b):** si la inferencia tarda 1.8s y tienes P=4 cores, ¿cuál es el speedup esperado?
4. **v4 (M6):** si tienes 3 servidores v3 con el balanceador, ¿cuántos usuarios concurrentes puedes manejar antes de degradar?

Justifica cada respuesta con las definiciones formales del módulo.
:::
