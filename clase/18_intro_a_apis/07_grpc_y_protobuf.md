---
title: "gRPC y Protocol Buffers"
---

# gRPC y Protocol Buffers

Hasta ahora, toda la comunicación que vimos usa JSON sobre HTTP/1.1. Funciona perfecto para APIs públicas: es legible, fácil de depurar con curl, y cualquier lenguaje lo entiende. Pero hay un contexto donde JSON es **demasiado lento y pesado**: la comunicación interna entre servicios que se hablan millones de veces por segundo.

## La analogía del restaurante

Piénsalo así:

- **REST/JSON** = el mesero habla con el cliente en español. Oraciones completas, amables, con contexto. *"Aquí tiene su filete término medio con guarnición de papas y ensalada."* Perfecto para la interacción humana.

- **gRPC/Protobuf** = el intercomunicador interno cocina-a-cocina en código. *"F3-TM-PP-EN."* Nadie fuera de la cocina entiende qué significa, pero los cocineros sí, y es **10 veces más rápido** que deletrear todo en español.

Entre servicios internos no necesitas la ceremonia del lenguaje natural. Necesitas **velocidad** y **precisión**.

---

## Por qué gRPC?

Cuando tienes un chatbot que recibe 1000 requests/segundo, y cada request necesita consultar al modelo de inferencia, la comunicación interna se vuelve el cuello de botella:

```
                    1000 req/s
Usuario ──REST──▶ API Server ──???──▶ GPU Server
                                       │
                  Si ??? = REST/JSON:   │
                  - Serializar JSON     │ ~500 bytes por request
                  - Parsear JSON        │ ~0.5ms overhead
                  - HTTP/1.1 overhead   │ una conexión por request
                                       │
                  Si ??? = gRPC/Proto:  │
                  - Serializar binario  │ ~80 bytes por request
                  - Parsear binario     │ ~0.05ms overhead
                  - HTTP/2 multiplexed  │ todo en una conexión
```

A 1000 req/s, esos microsegundos se acumulan.

---

## Protocol Buffers: el formato binario

Protocol Buffers (protobuf) es un formato de serialización binaria creado por Google. En lugar de escribir JSON a mano, defines un **esquema** en un archivo `.proto`:

```protobuf
syntax = "proto3";

message InferRequest {
  string model_id   = 1;    // "llama-7b"
  repeated int32 tokens = 2; // [15043, 318, 257, ...]
  int32 max_tokens   = 3;    // 512
  float temperature  = 4;    // 0.7
}

message InferResponse {
  repeated int32 output_tokens = 1;
  float latency_ms             = 2;
  int32 tokens_generated       = 3;
}
```

Los números `= 1`, `= 2`, etc. son **identificadores de campo**, no valores. Protobuf usa estos números (no los nombres) en la codificación binaria.

### Binario vs JSON: comparación de tamaños

El mismo request de inferencia en ambos formatos:

```
JSON (texto, ~480 bytes):
┌──────────────────────────────────────────────────────────┐
│ {                                                        │
│   "model_id": "llama-7b",                                │
│   "tokens": [15043, 318, 257, 1263, 640, ...],           │
│   "max_tokens": 512,                                     │
│   "temperature": 0.7                                     │
│ }                                                        │
│                                                          │
│ Incluye:                                                 │
│   - Nombres de campos repetidos en cada mensaje          │
│   - Llaves, comillas, comas, espacios                    │
│   - Números como texto ("512" = 3 bytes, no 2)           │
└──────────────────────────────────────────────────────────┘

Protobuf (binario, ~82 bytes):
┌──────────────────────────────────────────────────────────┐
│ 0a 07 6c 6c 61 6d 61 2d 37 62 12 14 a3 75 9e 02         │
│ 81 02 88 06 c0 09 ... 18 80 04 25 33 33 33 3f           │
│                                                          │
│ Incluye:                                                 │
│   - Números de campo (1 byte cada uno)                   │
│   - Valores en representación binaria nativa             │
│   - Sin nombres, sin delimitadores de texto              │
│   - Varint encoding para enteros                         │
└──────────────────────────────────────────────────────────┘

Reducción: ~83% menos bytes
```

Esa diferencia multiplicada por millones de requests al día es **enorme** en ancho de banda y tiempo de CPU para serializar/deserializar.

---

## HTTP/2: multiplexación

gRPC usa HTTP/2 en lugar de HTTP/1.1. La diferencia fundamental es cómo manejan múltiples requests en una conexión:

```
HTTP/1.1 — secuencial (head-of-line blocking)
═══════════════════════════════════════════════

Conexión TCP 1:
  ──▶ request 1 ──▶ ◀── response 1 ◀── ──▶ request 2 ──▶ ◀── response 2 ◀──
  (tienes que esperar la respuesta antes de enviar el siguiente)

Conexión TCP 2 (abres otra para "paralelizar"):
  ──▶ request 3 ──▶ ◀── response 3 ◀── ──▶ request 4 ──▶ ◀── response 4 ◀──

  Resultado: necesitas N conexiones TCP para N requests en paralelo
             (browsers limitan a ~6 conexiones por dominio)


HTTP/2 — multiplexado (streams intercalados)
═══════════════════════════════════════════════

UNA conexión TCP:
  ──▶ [req1-frame1] [req2-frame1] [req3-frame1]  ──▶
  ◀── [res1-frame1] [res2-frame1]                 ◀──
  ──▶ [req1-frame2]                               ──▶
  ◀── [res3-frame1] [res1-frame2] [res2-frame2]   ◀──

  Resultado: UNA conexión maneja TODOS los requests en paralelo
             Frames de distintos streams se intercalan libremente
```

Esto es especialmente valioso para servicios internos que intercambian miles de mensajes pequeños por segundo.

---

## Los cuatro tipos de RPC

gRPC soporta cuatro patrones de comunicación:

```
1. UNARY (el clásico: 1 request → 1 response)
┌────────┐                    ┌────────┐
│ Cliente │── InferRequest ──▶│Servidor│
│        │◀── InferResponse ──│        │
└────────┘                    └────────┘

2. SERVER STREAMING (1 request → stream de responses)
┌────────┐                    ┌────────┐
│ Cliente │── GenerateReq ───▶│Servidor│
│        │◀── Token 1 ────── │        │
│        │◀── Token 2 ────── │        │
│        │◀── Token 3 ────── │        │
│        │◀── [FIN] ──────── │        │
└────────┘                    └────────┘
  Caso de uso: streaming de tokens del LLM (alternativa a SSE)

3. CLIENT STREAMING (stream de requests → 1 response)
┌────────┐                    ┌────────┐
│ Cliente │── Chunk 1 ───────▶│Servidor│
│        │── Chunk 2 ───────▶│        │
│        │── Chunk 3 ───────▶│        │
│        │── [FIN] ─────────▶│        │
│        │◀── UploadResult ──│        │
└────────┘                    └────────┘
  Caso de uso: subir un dataset grande en chunks

4. BIDIRECTIONAL STREAMING (stream ↔ stream)
┌────────┐                    ┌────────┐
│ Cliente │── Msg 1 ─────────▶│Servidor│
│        │◀── Resp 1 ─────── │        │
│        │── Msg 2 ─────────▶│        │
│        │── Msg 3 ─────────▶│        │
│        │◀── Resp 2 ─────── │        │
│        │◀── Resp 3 ─────── │        │
└────────┘                    └────────┘
  Caso de uso: chat interactivo con el modelo
```

Compara esto con REST donde solo tienes el patrón 1 (unary), y SSE donde solo tienes el patrón 2 (server streaming). gRPC te da los cuatro nativamente.

---

## Arquitectura de model serving con gRPC

Así se ve la comunicación interna en un sistema de inferencia real:

```
┌───────────────────────────────────────────────────────────────────────┐
│                 INFRAESTRUCTURA DE INFERENCIA LLM                     │
│                                                                       │
│  ┌──────────────┐      gRPC (InferRequest)     ┌──────────────────┐  │
│  │              │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ▶│                  │  │
│  │   Chatbot    │                               │   Load Balancer  │  │
│  │   Server     │      gRPC (InferResponse)     │   (Envoy)        │  │
│  │   (Python)   │ ◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│                  │  │
│  │              │                               │                  │  │
│  └──────────────┘                               └────────┬─────────┘  │
│                                                          │            │
│                                              ┌───────────┼──────┐    │
│                                              │           │      │    │
│                                              ▼           ▼      ▼    │
│                                         ┌────────┐ ┌────────┐ ┌───┐ │
│                                         │GPU Pod │ │GPU Pod │ │...│ │
│                                         │   1    │ │   2    │ │   │ │
│                                         │(Triton)│ │(vLLM)  │ │   │ │
│                                         └────────┘ └────────┘ └───┘ │
│                                                                       │
│  Protobuf:                          vs  JSON equivalente:             │
│  ┌────────────────────────┐         ┌────────────────────────────┐    │
│  │ message InferRequest { │         │ {                          │    │
│  │   string model_id = 1; │         │   "model_id": "llama-7b", │    │
│  │   repeated int32       │         │   "tokens": [15043, ...], │    │
│  │     tokens = 2;        │         │   "max_tokens": 512,      │    │
│  │   int32 max_tokens = 3;│         │   "temperature": 0.7      │    │
│  │   float temperature= 4;│         │ }                          │    │
│  │ }                      │         │                            │    │
│  │ ~82 bytes, tipado      │         │ ~480 bytes, sin tipos      │    │
│  └────────────────────────┘         └────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────┘
```

El chatbot server habla REST/JSON con el mundo exterior (usuarios, frontend). Pero internamente, la comunicación con los GPU pods usa gRPC/Protobuf por eficiencia.

---

## REST vs gRPC: comparación

| Aspecto | REST | gRPC |
|---------|------|------|
| **Formato** | JSON (texto) | Protobuf (binario) |
| **Transporte** | HTTP/1.1 | HTTP/2 |
| **Contrato** | OpenAPI (opcional) | `.proto` (obligatorio) |
| **Streaming** | Limitado (SSE unidireccional) | Nativo (4 tipos) |
| **Tamaño payload** | Grande (~500 bytes) | Compacto (~80 bytes) |
| **Serialización** | Lenta (parse texto) | Rápida (decode binario) |
| **Debugging** | Facil (`curl`, browser) | Dificil (binario, necesitas `grpcurl`) |
| **Browser** | Nativo | Requiere proxy (gRPC-Web) |
| **Code generation** | Opcional | Automática desde `.proto` |
| **Caso ideal** | APIs publicas | Servicios internos |

### Cuándo REST sigue siendo mejor

No todo debe ser gRPC. REST gana cuando:

```
¿Quién consume tu API?
│
├── Usuarios externos / browsers / apps móviles
│   └──▶ REST
│        - Cualquier lenguaje tiene un cliente HTTP
│        - curl para debugging
│        - JSON legible para humanos
│        - Cacheable por CDN
│
├── Desarrolladores terceros (API pública)
│   └──▶ REST
│        - Documentación con OpenAPI/Swagger
│        - No necesitan instalar protoc
│        - Ejemplos con curl en el README
│
└── Tus propios microservicios internos
    │
    ├── Volumen alto (>1000 req/s) ──▶ gRPC
    ├── Necesitas streaming ─────────▶ gRPC
    ├── Tipado estricto importa ─────▶ gRPC
    └── Volumen bajo, equipo pequeño ▶ REST (más simple)
```

---

## Definiendo un servicio gRPC

Un archivo `.proto` define tanto los mensajes como el servicio:

```protobuf
syntax = "proto3";

package inference;

// Mensajes
message InferRequest {
  string model_id         = 1;
  repeated int32 tokens   = 2;
  int32 max_tokens        = 3;
  float temperature       = 4;
}

message Token {
  int32 token_id  = 1;
  string text     = 2;
  float logprob   = 3;
}

message InferResponse {
  repeated Token tokens   = 1;
  float latency_ms        = 2;
}

// Servicio
service InferenceService {
  // Unary: una inferencia completa
  rpc Infer(InferRequest) returns (InferResponse);

  // Server streaming: token por token
  rpc InferStream(InferRequest) returns (stream Token);
}
```

De este archivo `.proto`, el compilador `protoc` genera automáticamente:
- Clases de datos en tu lenguaje (Python, Go, Java, etc.)
- Cliente y servidor stub con los métodos definidos
- Serialización/deserialización binaria

No escribes parsers de JSON ni validas tipos a mano. El contrato es **el archivo `.proto`**, y ambos lados lo respetan porque el código es generado.

---

## El flujo completo

```
                    DESARROLLO                          RUNTIME
                    ══════════                          ═══════

  1. Escribir         2. Compilar          3. Usar código generado
  ┌──────────┐      ┌──────────┐      ┌────────────────────────────┐
  │          │      │          │      │                            │
  │  .proto  │─────▶│  protoc  │─────▶│  inference_pb2.py          │
  │  (esquema│      │(compilador│     │  inference_pb2_grpc.py     │
  │  manual) │      │ de proto)│      │                            │
  │          │      │          │      │  # Servidor                │
  └──────────┘      └──────────┘      │  class InferenceServicer:  │
                                      │      def Infer(self, req): │
                                      │          tokens = model(   │
                                      │            req.tokens)     │
                                      │          return response   │
                                      │                            │
                                      │  # Cliente                 │
                                      │  stub = InferenceStub(ch)  │
                                      │  resp = stub.Infer(req)    │
                                      └────────────────────────────┘
```

## Conexión con la arquitectura del LLM

Regresa al diagrama maestro del archivo `00_index.md`. gRPC corresponde a la **conexión ⑤**:

```
┌───────────────┐                     ┌───────────────┐
│   LLM API     │                     │  GPU Cluster  │
│ (Anthropic,   │   ⑤ gRPC           │  (inferencia) │
│  OpenAI)      │──── (interno) ─────▶│               │
└───────────────┘                     └───────────────┘
```

Esta es la conexión que **nunca ves** como usuario de la API. Pero es la razón por la que la inferencia puede manejar miles de requests concurrentes con latencia mínima. Cuando haces `POST /v1/chat/completions`, internamente eso se traduce a un `rpc Infer()` en gRPC hacia el cluster de GPUs.

---

> **Verifica en el notebook:** En `04_websockets.ipynb` hay una sección que compara tiempos de serialización entre JSON y una simulación de formato binario, y muestra cómo se define un servicio gRPC simple con `grpcio`.

---

:::exercise{title="Diseña mensajes .proto para un sistema de e-commerce"}
Un sistema de e-commerce necesita comunicación interna entre sus microservicios. Diseña los mensajes Protocol Buffers para los siguientes casos:

- **a)** Define un mensaje `Order` con campos para: id, usuario, lista de productos (cada producto tiene id, nombre, cantidad y precio), total, estado (enum con valores PENDING, PAID, SHIPPED, DELIVERED, CANCELLED), y timestamp de creación.
- **b)** Define un mensaje `InventoryUpdate` que un servicio de pagos envía al servicio de inventario cuando se confirma una compra (debe decrementar stock de cada producto).
- **c)** Define un servicio `OrderService` con cuatro RPCs:
  1. `CreateOrder` (unary): recibe una lista de productos, retorna la orden creada
  2. `TrackOrder` (server streaming): recibe un order_id, retorna un stream de actualizaciones de estado
  3. `BulkCreateOrders` (client streaming): recibe un stream de ordenes, retorna un resumen
  4. `LiveDashboard` (bidireccional): recibe filtros del admin, retorna stream de ordenes en tiempo real
- **d)** Estima el tamaño en bytes de un `Order` con 3 productos en formato Protobuf vs JSON. Justifica tu estimación.
:::
