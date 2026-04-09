---
title: "WebSockets"
---

# WebSockets

## Del mesero al intercomunicador

Hasta ahora en el restaurante:

- **REST** = llamas al mesero cada vez que necesitas algo. Él va a la cocina, vuelve con la respuesta, y se olvida de ti.
- **SSE** = el mesero se queda junto a tu mesa y te va sirviendo plato por plato. Pero tú no puedes hablarle — solo escuchas.

**WebSocket** = instalas un **intercomunicador** entre tu mesa y la cocina. Una conexión permanente, mensajes en **ambas direcciones**, sin necesidad de llamar al mesero cada vez.

```
  REST (request-response):

    [Cliente] ──petición──►  [Servidor]
    [Cliente] ◄──respuesta── [Servidor]
    (conexión se cierra)

    [Cliente] ──petición──►  [Servidor]
    [Cliente] ◄──respuesta── [Servidor]
    (conexión se cierra)

    Cada interacción = nueva conexión


  WebSocket (persistente, bidireccional):

    [Cliente] ═══════════════ [Servidor]
                 ──msg──►
               ◄──msg──
                 ──msg──►
                 ──msg──►
               ◄──msg──
               ◄──msg──
                 ──msg──►

    Una sola conexión, mensajes en ambas direcciones
```

---

## El handshake de upgrade

WebSocket empieza como HTTP y luego **cambia de protocolo**. Este momento se llama el "upgrade handshake":

```
  Cliente                                         Servidor
    │                                               │
    │──── GET /ws HTTP/1.1 ──────────────────────► │
    │     Host: chat.example.com                    │
    │     Upgrade: websocket              ◄─────── │  "¿Podemos cambiar
    │     Connection: Upgrade                       │   a WebSocket?"
    │     Sec-WebSocket-Key: dGhlIHNhbX...          │
    │     Sec-WebSocket-Version: 13                 │
    │                                               │
    │◄─── HTTP/1.1 101 Switching Protocols ──────── │
    │     Upgrade: websocket                        │  "Sí, cambiamos."
    │     Connection: Upgrade                       │
    │     Sec-WebSocket-Accept: s3pPLMBi...         │
    │                                               │
    │═══════════════════════════════════════════════ │
    │         YA NO ES HTTP                         │
    │      Protocolo WebSocket (frames binarios)    │
    │                                               │
    │◄──── frame: "Bienvenido al chat" ──────────── │
    │───── frame: "Hola, soy usuario X" ──────────► │
    │◄──── frame: "Usuario Y dice: ..." ─────────── │
    │                                               │
```

Puntos clave:
1. **Empieza como HTTP** — el request inicial es un GET normal.
2. El header `Upgrade: websocket` pide el cambio de protocolo.
3. El servidor responde con **101 Switching Protocols** (no 200 OK).
4. A partir de ese momento, **ya no es HTTP**. Son frames binarios en una conexión TCP persistente.

---

## Arquitectura de un chat con LLM

¿Por qué no conectar el browser directamente al API del LLM por WebSocket? Porque necesitas un servidor intermedio. Este diagrama muestra la arquitectura completa:

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                     ARQUITECTURA CHAT + LLM                        │
  │                                                                    │
  │   ┌──────────┐    WebSocket     ┌──────────────┐   REST+SSE    ┌──────────┐
  │   │          │ ◄══════════════► │              │ ────────────► │          │
  │   │ Browser  │    conexion ①    │  Chat Server │  conexion ③   │ LLM API  │
  │   │ (UI)     │                  │              │ ◄──────────── │          │
  │   │          │                  │              │  conexion ④   │          │
  │   └──────────┘                  └──────┬───────┘  (SSE tokens) └──────────┘
  │                                        │                                   │
  │                                        │                                   │
  │                                 ┌──────┴───────┐                          │
  │                                 │              │                          │
  │                                 │  Base de     │                          │
  │                                 │  Datos       │                          │
  │                                 │  (historial) │                          │
  │                                 │              │                          │
  │                                 └──────────────┘                          │
  │                                                                           │
  └───────────────────────────────────────────────────────────────────────────┘

  Conexión ①  : WebSocket (bidireccional) entre browser y chat server
  Conexión ③④ : REST + SSE entre chat server y LLM API
```

¿Por qué el Chat Server en medio? Porque maneja responsabilidades que el LLM API no debería conocer:

```
  ┌─────────────────────────────────────────────────────┐
  │              Chat Server: responsabilidades          │
  │                                                     │
  │  ┌──────────────┐   ¿Quién eres? ¿Tienes permiso?  │
  │  │ Autenticación│   Verifica JWT, API key, sesión   │
  │  └──────────────┘                                   │
  │                                                     │
  │  ┌──────────────┐   Guarda mensajes, carga contexto │
  │  │ Historial    │   Arma el array de messages[]     │
  │  └──────────────┘                                   │
  │                                                     │
  │  ┌──────────────┐   ¿Cuántas peticiones por minuto? │
  │  │ Rate Limiting│   Evita abuso y controla costos   │
  │  └──────────────┘                                   │
  │                                                     │
  │  ┌──────────────┐   Si el LLM falla, reintenta      │
  │  │ Retry/Fallbk │   O cambia a otro modelo          │
  │  └──────────────┘                                   │
  │                                                     │
  │  ┌──────────────┐   Recibe SSE del LLM, reenvía    │
  │  │ Traducción   │   por WebSocket al browser        │
  │  │ de protocolo │                                   │
  │  └──────────────┘                                   │
  └─────────────────────────────────────────────────────┘
```

---

## Formato de mensajes: frames

Una vez establecida la conexión WebSocket, los datos viajan en **frames**:

```
  Frame WebSocket:
  ┌──────┬──────┬────────────┬──────────────────┐
  │ FIN  │ Op   │ Longitud   │ Payload          │
  │ (1b) │(4b)  │ (7-64 b)   │ (datos reales)   │
  └──────┴──────┴────────────┴──────────────────┘

  Opcodes:
  ┌──────────┬──────────────────────────────────┐
  │ 0x1      │ Frame de texto (UTF-8)           │
  │ 0x2      │ Frame binario                    │
  │ 0x8      │ Cierre de conexión               │
  │ 0x9      │ Ping  (¿sigues ahí?)             │
  │ 0xA      │ Pong  (sí, sigo aquí)            │
  └──────────┴──────────────────────────────────┘
```

Los frames de **ping/pong** son el mecanismo de keepalive — el servidor manda un ping periódicamente, y el cliente responde con un pong. Si no hay pong, la conexión se considera muerta.

---

## Ciclo de vida de una conexión

```
  ┌─────────┐                                    ┌─────────┐
  │ Cliente │                                    │Servidor │
  └────┬────┘                                    └────┬────┘
       │                                              │
       │──── HTTP GET + Upgrade: websocket ────────► │
       │◄─── 101 Switching Protocols ──────────────── │
       │                                              │
       │            ┌──── OPEN ────┐                  │
       │            │              │                  │
       │──── "Hola, necesito ayuda" ──────────────►  │
       │◄──── "Claro, ¿en qué te ayudo?" ──────────  │
       │──── "Explica WebSockets" ────────────────►  │
       │◄──── "WebSocket es un protocolo..." ──────   │
       │            │              │                  │
       │            │  (cada 30s)  │                  │
       │◄──── PING ─┘              │                  │
       │──── PONG ─────────────────┘                  │
       │                                              │
       │            │  (más mensajes...)              │
       │            │                                 │
       │──── CLOSE (código 1000, "bye") ──────────►  │
       │◄─── CLOSE (confirmación) ───────────────── │
       │                                              │
       │            ┌── CLOSED ──┐                    │
       └────────────┘            └────────────────────┘
```

---

## WebSocket vs SSE: comparación detallada

```
+-------------------+----------------------------+----------------------------+
| Aspecto           | WebSocket                  | SSE                        |
+-------------------+----------------------------+----------------------------+
| Dirección         | Bidireccional              | Server → Client            |
|                   | (ambos envían y reciben)   | (solo el servidor envía)   |
+-------------------+----------------------------+----------------------------+
| Protocolo         | ws:// o wss://             | HTTP estándar              |
|                   | (upgrade desde HTTP)       | (Content-Type: text/       |
|                   |                            |  event-stream)             |
+-------------------+----------------------------+----------------------------+
| Reconexión        | Manual (tu código debe     | Automática (el navegador   |
|                   | detectar y reconectar)     | reconecta solo)            |
+-------------------+----------------------------+----------------------------+
| Formato           | Texto o binario            | Solo texto                 |
|                   | (cualquier cosa)           | (data: líneas)             |
+-------------------+----------------------------+----------------------------+
| Proxies/CDN       | Puede tener problemas      | Funciona sin problemas     |
|                   | (no es HTTP estándar)      | (es HTTP normal)           |
+-------------------+----------------------------+----------------------------+
| Overhead por msg  | 2-14 bytes (frame header)  | ~20+ bytes (data: ...\n\n)|
+-------------------+----------------------------+----------------------------+
| Caso LLM típico   | Chat UI interactivo        | Token streaming desde      |
|                   | (usuario escribe, modelo   | el LLM API                 |
|                   |  responde)                 |                            |
+-------------------+----------------------------+----------------------------+
```

---

## Costos de las conexiones persistentes

Cada conexión WebSocket abierta consume recursos en el servidor:

```
  Servidor con 10,000 conexiones WebSocket abiertas:

  ┌────────────────────────────────────────────────┐
  │                  MEMORIA                       │
  │                                                │
  │  Conexión 1:    ~50 KB (buffers + estado)      │
  │  Conexión 2:    ~50 KB                         │
  │  Conexión 3:    ~50 KB                         │
  │  ...                                           │
  │  Conexión 10K:  ~50 KB                         │
  │  ─────────────────────────────                 │
  │  Total:         ~500 MB solo en conexiones     │
  │                                                │
  │  + file descriptors del OS (límite: ulimit)    │
  │  + goroutines/threads/event handlers           │
  │  + heartbeat timers (ping/pong cada 30s)       │
  └────────────────────────────────────────────────┘

  Por eso:
  - Los servidores WebSocket tienen LÍMITES de conexiones
  - Se usan connection pools y load balancers
  - Las conexiones inactivas se cierran (timeout)
```

Esto no es un problema de REST: cada petición REST abre y cierra conexión, así que no acumula estado. Es el precio que pagas por la bidireccionalidad en tiempo real.

---

## Cuándo usar cada protocolo

```
  ¿Qué necesitas?
        │
        ├── Request simple, respuesta simple
        │   (CRUD, consultas, formularios)
        │   │
        │   └──► REST
        │
        ├── El servidor necesita enviar datos continuamente
        │   al cliente (streaming, feeds, notificaciones)
        │   │
        │   ├── ¿El cliente necesita enviar datos DESPUÉS
        │   │    de la petición inicial?
        │   │   │
        │   │   ├── NO  → SSE
        │   │   │         (token streaming, dashboards)
        │   │   │
        │   │   └── SI  → WebSocket
        │   │             (chat, juegos, colaboración)
        │   │
        │   └── ¿Necesitas transmitir datos binarios?
        │       │
        │       ├── NO  → SSE puede funcionar
        │       └── SI  → WebSocket (soporta frames binarios)
        │
        └── Microservicios internos, alto rendimiento,
            esquemas estrictos
            │
            └──► gRPC (archivo 07)
```

Ejemplos concretos:

```
+---------------------------+-------------+----------------------------------+
| Caso de uso               | Protocolo   | Por qué                         |
+---------------------------+-------------+----------------------------------+
| Obtener perfil de usuario | REST GET    | Un request, una respuesta        |
+---------------------------+-------------+----------------------------------+
| Streaming de tokens LLM   | SSE         | Server→client, HTTP estándar     |
+---------------------------+-------------+----------------------------------+
| Chat en tiempo real        | WebSocket   | Bidireccional, baja latencia     |
+---------------------------+-------------+----------------------------------+
| Editor colaborativo        | WebSocket   | Cambios simultáneos de múltiples |
|                           |             | usuarios                         |
+---------------------------+-------------+----------------------------------+
| Dashboard de métricas      | SSE         | Solo el servidor envía updates   |
+---------------------------+-------------+----------------------------------+
| Juego multijugador         | WebSocket   | Bidireccional + binario + rápido |
+---------------------------+-------------+----------------------------------+
```

---

## Ejemplo en Python

```python
import asyncio
import websockets

# ──────────────────────────────────────
# Servidor WebSocket mínimo
# ──────────────────────────────────────
async def handler(websocket):
    async for message in websocket:
        # Echo: devuelve lo que recibe, en mayúsculas
        response = f"Recibido: {message.upper()}"
        await websocket.send(response)

async def main_server():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # corre para siempre

# asyncio.run(main_server())


# ──────────────────────────────────────
# Cliente WebSocket mínimo
# ──────────────────────────────────────
async def main_client():
    async with websockets.connect("ws://localhost:8765") as ws:
        await ws.send("hola desde python")
        response = await ws.recv()
        print(response)  # "Recibido: HOLA DESDE PYTHON"

        await ws.send("¿cómo estás?")
        response = await ws.recv()
        print(response)  # "Recibido: ¿CÓMO ESTÁS?"

# asyncio.run(main_client())
```

Nota cómo el cliente y el servidor **ambos** envían y reciben. Eso es imposible con SSE.

---

## Conexión con la arquitectura LLM

En el diagrama maestro, WebSocket opera en la conexión **①** — entre el browser y el chat server:

```
  ┌─────────┐   ① WebSocket    ┌──────────────┐   ③ REST      ┌─────────────┐
  │ Browser │ ◄═══════════════►│  Chat Server │ ─────────────►│  LLM API    │
  │  (UI)   │   bidireccional  │              │   ④ SSE       │  (Inference)│
  └─────────┘                  └──────────────┘ ◄──────────── └─────────────┘

  ① Browser ↔ Chat Server : WebSocket
    - El usuario escribe mensajes
    - El servidor envía tokens del LLM

  ③ Chat Server → LLM API : REST (POST /v1/messages, stream=true)
  ④ LLM API → Chat Server : SSE (tokens incrementales)
```

El Chat Server actúa como **traductor de protocolos**: recibe SSE del LLM y lo reenvía como mensajes WebSocket al browser. Así cada tramo usa el protocolo óptimo para su caso.

---

> **Verifica en el notebook:** Revisa `clase/18_intro_a_apis/code/03_websockets.ipynb` donde implementamos un servidor y cliente WebSocket, y observamos el handshake y los frames en vivo.

---

:::exercise{title="Diseña el protocolo de mensajes para un editor de texto colaborativo"}

Diseña el protocolo de mensajes WebSocket para un editor de texto colaborativo (estilo Google Docs simplificado). Dos o más usuarios pueden editar el mismo documento simultáneamente.

**Parte 1: Tipos de mensaje**

Define al menos 6 tipos de mensaje que viajen por el WebSocket. Para cada uno indica:
1. Dirección (client→server, server→client, o ambas)
2. Formato JSON del payload
3. Ejemplo concreto

Sugerencias de tipos: `cursor_move`, `text_insert`, `text_delete`, `user_join`, `user_leave`, `sync_full`, `selection_change`.

**Parte 2: Diagrama de secuencia**

Dibuja (en ASCII) el diagrama de secuencia para este escenario:
1. Usuario A ya está editando el documento
2. Usuario B se conecta
3. Usuario B recibe el estado actual del documento
4. Usuario A escribe "hola" en la posición 42
5. Usuario B ve el cambio y mueve su cursor

**Parte 3: Preguntas de diseño**

1. ¿Qué pasa si Usuario A y Usuario B escriben en la misma posición al mismo tiempo? ¿Cómo resolverías el conflicto?
2. ¿Por qué WebSocket y no SSE para este caso?
3. Si el editor tiene 500 usuarios simultáneos en el mismo documento, cada uno generando ~10 mensajes por segundo, ¿cuántos mensajes por segundo debe procesar el servidor? ¿Cuántos mensajes por segundo recibe cada cliente?

:::
