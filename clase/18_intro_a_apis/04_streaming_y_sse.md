---
title: "Streaming y Server-Sent Events"
---

# Streaming y Server-Sent Events

## El problema: 5 segundos de nada

Imagina que le pides a un LLM que te escriba un ensayo. El modelo tarda 5 segundos en generar toda la respuesta. Con REST clásico, ves **nada** durante 5 segundos y luego — boom — todo el texto de golpe.

```
SIN streaming (REST clásico):

  Tiempo ──────────────────────────────────────────────────►

  Cliente   │── POST ──►│                                │◄── 200 OK + texto completo ──│
            │           │         5 seg de NADA           │                              │
  Pantalla  │           │  [                            ] │  [Todo el texto de golpe]    │
            t=0        t=0                               t=5s                           t=5s


CON streaming (SSE):

  Tiempo ──────────────────────────────────────────────────►

  Cliente   │── POST ──►│                                                                │
            │           │                                                                │
  Servidor  │           ├─ tok ─┬─ tok ─┬─ tok ─┬─ tok ─┬─ ... ─┬─ tok ─┤  [DONE]      │
            │           │ 50ms  │ 80ms  │ 40ms  │ 60ms  │       │       │               │
  Pantalla  │           │ [H]   │ [Ho]  │ [Hol] │[Hola] │       │       │ [texto final] │
            t=0        t=0    t=50ms  t=130ms t=170ms  t=230ms        t=5s
```

**Latencia percibida**: 5 segundos de **NADA** vs **50 milisegundos** hasta el primer token.

El texto final es el mismo. El tiempo total es el mismo. Pero la **experiencia** es completamente distinta.

---

## Analogía del restaurante

```
SIN streaming:                          CON streaming:

  ┌──────────────────────┐               ┌──────────────────────┐
  │      COCINA           │               │      COCINA           │
  │                       │               │                       │
  │  Prepara TODO el      │               │  Prepara plato 1...   │
  │  banquete completo    │               │   ¡Listo! → envía     │
  │  (entrada + sopa +    │               │  Prepara plato 2...   │
  │   plato fuerte +      │               │   ¡Listo! → envía     │
  │   postre)             │               │  Prepara plato 3...   │
  │                       │               │   ¡Listo! → envía     │
  │  ¡Todo listo!         │               │  ...                  │
  └───────┬───────────────┘               └───────┬───────────────┘
          │                                       │ │ │ │
          │ (40 min después)                      │ │ │ │  (cada plato
          ▼                                       ▼ ▼ ▼ ▼   conforme sale)
  ┌──────────────────────┐               ┌──────────────────────┐
  │      COMEDOR          │               │      COMEDOR          │
  │                       │               │                       │
  │  Esperas 40 min       │               │  Comes la entrada     │
  │  con hambre...        │               │  mientras preparan    │
  │                       │               │  el siguiente plato   │
  │  Todo llega de golpe  │               │                       │
  └──────────────────────┘               └──────────────────────┘

  Tiempo total: 40 min                   Tiempo total: 40 min
  Tiempo sin comer: 40 min               Tiempo sin comer: 8 min
```

---

## TTFT: Time To First Token

En el mundo de los LLMs, hay una métrica clave para la experiencia del usuario:

```
TTFT = Time To First Token
     = tiempo desde que envías la petición
       hasta que recibes el PRIMER fragmento de respuesta

                    TTFT
                 ◄────────►
  ┌──────────────┐         ┌──────────────────────────────┐
  │   Petición   │         │ Primer token    Último token │
  │   enviada    │         │      ▼               ▼      │
  └──────┬───────┘         └──────┬───────────────┬──────┘
         │                        │               │
  ───────┼────────────────────────┼───────────────┼──────► t
        t=0                   t=TTFT          t=T_total

  Sin streaming:  TTFT = T_total  (no ves nada hasta el final)
  Con streaming:  TTFT ≈ 50-200ms (casi instantáneo)
```

¿Por qué importa? Estudios de UX muestran que los usuarios perciben una interfaz como "rápida" si responde en menos de **200ms**. Con streaming, el TTFT cae dentro de ese umbral incluso si la respuesta total tarda 30 segundos.

---

## El protocolo SSE: qué viaja por el cable

Server-Sent Events (SSE) es sorprendentemente simple. Es HTTP normal con un `Content-Type` especial:

```
Petición del cliente (HTTP normal):

  POST /v1/messages HTTP/1.1
  Host: api.anthropic.com
  x-api-key: sk-ant-...
  Content-Type: application/json

  {"model": "claude-sonnet-4-20250514", "stream": true, "messages": [...]}


Respuesta del servidor (SSE):

  HTTP/1.1 200 OK
  Content-Type: text/event-stream        ◄── Este header lo define todo
  Cache-Control: no-cache
  Connection: keep-alive

  data: {"type":"message_start","message":{"id":"msg_01","model":"claude-sonnet-4-20250514"}}

  data: {"type":"content_block_start","content_block":{"type":"text","text":""}}

  data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Hol"}}

  data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"a"}}

  data: {"type":"content_block_delta","delta":{"type":"text_delta","text":","}}

  data: {"type":"content_block_delta","delta":{"type":"text_delta","text":" ¿"}}

  data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"cómo"}}

  data: {"type":"content_block_delta","delta":{"type":"text_delta","text":" estás?"}}

  data: {"type":"content_block_stop"}

  data: {"type":"message_stop"}
```

Observa el formato:
- Cada evento empieza con `data: ` seguido de JSON.
- Los eventos se separan con una **línea en blanco**.
- No hay delimitador de cierre — el servidor simplemente deja de enviar.

---

## Cómo funciona SSE: una conexión, muchos eventos

```
  Cliente                                      Servidor
    │                                            │
    │──── POST /v1/messages ──────────────────►  │
    │     {"stream": true, ...}                  │
    │                                            │
    │◄─── HTTP 200 OK ───────────────────────    │
    │     Content-Type: text/event-stream        │
    │                                            │
    │◄─── data: {"type":"message_start"} ────    │  ─┐
    │                                            │   │
    │◄─── data: {"delta":"Hol"} ─────────────    │   │
    │                                            │   │  Conexión HTTP
    │◄─── data: {"delta":"a"} ───────────────    │   │  ABIERTA todo
    │                                            │   │  este tiempo
    │◄─── data: {"delta":", ¿cómo"} ────────    │   │
    │                                            │   │
    │◄─── data: {"delta":" estás?"} ────────    │   │
    │                                            │   │
    │◄─── data: {"type":"message_stop"} ─────    │  ─┘
    │                                            │
    │     (conexión se cierra)                   │
    │                                            │
```

Puntos clave:
- **Una sola petición HTTP** abre la conexión.
- La conexión se mantiene abierta — el servidor envía datos cuando quiere.
- Es **unidireccional**: solo el servidor envía. El cliente no puede enviar más datos por la misma conexión.
- Cuando el servidor termina, cierra la conexión.

---

## SSE vs REST clásico

```
REST clásico:                                SSE:

  Cliente        Servidor                     Cliente        Servidor
    │               │                           │               │
    │── request ──► │                           │── request ──► │
    │               │ (procesando...)           │               │ (procesando...)
    │               │                           │◄── evento 1 ──│
    │               │                           │◄── evento 2 ──│
    │               │                           │◄── evento 3 ──│
    │◄── response ──│                           │◄── evento N ──│
    │               │                           │  (conexión    │
    │ (conexión     │                           │   se cierra)  │
    │  se cierra)   │                           │               │

  Datos: TODO al final                        Datos: incrementales
  Conexiones: 1 por request                   Conexiones: 1 (larga)
  Latencia percibida: alta                    Latencia percibida: baja
```

---

## Código: streaming con un LLM

```python
# ──────────────────────────────────────────────
# Sin streaming: esperas T_total completo
# ──────────────────────────────────────────────
import time

t0 = time.time()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explica qué es una API"}]
)
t_total = time.time() - t0
print(response.content[0].text)
# TTFT = t_total (no ves nada hasta aquí)


# ──────────────────────────────────────────────
# Con streaming: cada token al instante
# ──────────────────────────────────────────────
t0 = time.time()
first_token = True

with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explica qué es una API"}]
) as stream:
    for text in stream.text_stream:
        if first_token:
            ttft = time.time() - t0
            print(f"\n[TTFT: {ttft:.3f}s]")
            first_token = False
        print(text, end="", flush=True)

t_total = time.time() - t0
print(f"\n[Total: {t_total:.3f}s]")
# TTFT ~ 0.1s, T_total ~ 5s
```

La diferencia: `client.messages.create()` vs `client.messages.stream()`. El SDK esconde toda la complejidad de SSE — parsea los eventos, reconstruye los deltas y te da un iterador limpio.

---

## Características de SSE

```
+--------------------+--------------------------------------------+
| Característica     | Detalle                                    |
+--------------------+--------------------------------------------+
| Dirección          | Unidireccional: servidor → cliente         |
+--------------------+--------------------------------------------+
| Protocolo base     | HTTP estándar (no requiere upgrade)         |
+--------------------+--------------------------------------------+
| Reconexión         | Automática (el navegador reconecta solo)   |
+--------------------+--------------------------------------------+
| Formato            | Texto (data: ... + línea vacía)            |
+--------------------+--------------------------------------------+
| IDs de evento      | Opcional: id: campo para rastrear posición |
+--------------------+--------------------------------------------+
| Compatibilidad     | Funciona con proxies, CDNs, firewalls      |
|                    | (es HTTP normal)                           |
+--------------------+--------------------------------------------+
| Caso de uso ideal  | Token streaming de LLMs, feeds de noticias,|
|                    | dashboards de monitoreo                    |
+--------------------+--------------------------------------------+
```

---

## SSE vs WebSocket: anticipo rápido

¿Cuándo SSE y cuándo WebSocket? Regla simple:

```
¿Necesitas que el CLIENTE envíe datos
después de la petición inicial?
        │
        ├── NO  → SSE   (más simple, HTTP estándar)
        │                 Ejemplo: streaming de tokens de un LLM
        │
        └── SI  → WebSocket  (más complejo, protocolo distinto)
                              Ejemplo: chat interactivo con edición en vivo
```

SSE es más simple porque **no requiere cambio de protocolo**. Es HTTP normal con una conexión larga. WebSocket requiere un "upgrade" que cambia el protocolo por completo (más detalles en el archivo 05).

---

## Conexión con la arquitectura LLM

En el diagrama maestro de la arquitectura, SSE opera en las conexiones ③ y ④:

```
  ┌─────────┐         ┌──────────────┐         ┌─────────────┐
  │ Browser │ ──①──►  │  Chat Server │ ──③──►  │  LLM API    │
  │  (UI)   │ ◄──②──  │              │ ◄──④──  │  (Inference)│
  └─────────┘         └──────────────┘         └─────────────┘

  ①② = WebSocket (bidireccional, archivo 05)
  ③  = POST /v1/messages con stream=true (REST)
  ④  = Server-Sent Events (tokens incrementales)
```

El Chat Server hace una petición REST al LLM API con `stream: true`. El LLM API responde con SSE. El Chat Server recibe los tokens y los reenvía al browser por WebSocket. Dos protocolos distintos para dos tramos distintos.

---

> **Verifica en el notebook:** Revisa `clase/18_intro_a_apis/code/02_streaming_sse.ipynb` donde implementamos streaming real contra un LLM y medimos TTFT vs T_total.

---

:::exercise{title="Calcula el ahorro de ancho de banda de streaming vs buffered"}

Considera una respuesta de LLM de **2,000 tokens** que tarda **8 segundos** en generarse completamente. Cada token ocupa en promedio **5 bytes** de payload.

**Parte 1: Overhead por evento SSE**

Cada evento SSE tiene este formato:
```
data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"TOKEN"}}\n\n
```

Calcula:
1. El overhead fijo (en bytes) de cada evento SSE (todo menos el token).
2. El total de bytes transmitidos con SSE para los 2,000 tokens.
3. El total de bytes transmitidos con REST clásico (un solo JSON con todos los tokens).
4. ¿Cuál transmite más bytes en total? ¿Por qué el streaming sigue siendo preferible?

**Parte 2: Latencia percibida**

Supón que la generación es uniforme (250 tokens/segundo).
1. ¿Cuál es el TTFT con streaming?
2. ¿Cuál es el TTFT sin streaming?
3. Si el usuario empieza a leer a 200 palabras/minuto (~3.3 palabras/segundo, ~5 tokens/segundo), ¿en qué momento el buffer de texto en pantalla se vacía (el usuario alcanza al modelo)? ¿O nunca se vacía?

:::
