---
title: "HTTP: el protocolo base"
---

# HTTP: el protocolo base

En el restaurante de la sección 16, definimos la cocina (cómputo) y en `01_que_es_una_api.md` introdujimos al mesero (la API). Ahora definimos el **idioma** que hablan mesero y cocina entre sí. Ese idioma es HTTP --- *Hypertext Transfer Protocol*.

HTTP es el protocolo de comunicación más importante de la web. Todo lo que veremos en este módulo --- REST, SSE, WebSocket, GraphQL --- se construye sobre HTTP o empieza con un handshake HTTP. Entenderlo bien es entender los cimientos.

---

## Anatomía de una petición HTTP

Cada vez que tu chatbot llama al LLM, viaja un **request** HTTP por la red. Veamos su estructura exacta usando una llamada real a la API de Anthropic:

```
┌─────────────────────────────────────────────────────────────────┐
│                        HTTP REQUEST                             │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ LÍNEA DE PETICIÓN (request line)                         │  │
│  │                                                           │  │
│  │   POST /v1/messages HTTP/1.1                              │  │
│  │   ─┬──  ─────┬──────  ──┬───                              │  │
│  │    │         │          │                                  │  │
│  │    │         │          └── versión del protocolo          │  │
│  │    │         └── ruta del recurso (endpoint)               │  │
│  │    └── método (qué quieres hacer)                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ HEADERS (metadatos de la petición)                        │  │
│  │                                                           │  │
│  │   Host: api.anthropic.com                                 │  │
│  │   Content-Type: application/json                          │  │
│  │   x-api-key: sk-ant-api03-xxxxx                          │  │
│  │   anthropic-version: 2023-06-01                           │  │
│  │   Accept: application/json                                │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ── línea en blanco (separa headers del body) ──                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ BODY (datos que envías)                                   │  │
│  │                                                           │  │
│  │   {                                                       │  │
│  │     "model": "claude-sonnet-4-20250514",                          │  │
│  │     "max_tokens": 1024,                                   │  │
│  │     "messages": [                                         │  │
│  │       {                                                   │  │
│  │         "role": "user",                                   │  │
│  │         "content": "¿Qué es una API?"                     │  │
│  │       }                                                   │  │
│  │     ]                                                     │  │
│  │   }                                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

Tres partes, siempre en este orden:

1. **Línea de petición** --- método + ruta + versión
2. **Headers** --- metadatos clave-valor
3. **Body** --- datos (opcional, no todos los métodos lo usan)

### ¿Qué significa cada header del ejemplo?

```
Host: api.anthropic.com           ← A qué servidor va la petición.
                                    Un mismo IP puede servir múltiples
                                    dominios; Host le dice cuál quieres.

Content-Type: application/json    ← "Los datos que te envío están en
                                    formato JSON." Sin esto, el servidor
                                    no sabe cómo interpretar el body.

x-api-key: sk-ant-api03-xxxxx    ← Tu clave de autenticación. Es como
                                    tu número de reservación: sin ella,
                                    el servidor te responde 401.
                                    El prefijo "x-" indica header custom
                                    (no estándar de HTTP).

anthropic-version: 2023-06-01    ← Versión de la API que quieres usar.
                                    Las APIs evolucionan; este header
                                    garantiza que tu código no se rompa
                                    cuando el proveedor cambia el formato
                                    de respuesta.

Accept: application/json          ← "Quiero que me respondas en JSON."
                                    Es la contraparte de Content-Type:
                                    uno dice qué formato ENVÍAS,
                                    el otro qué formato QUIERES RECIBIR.
```

En el restaurante: los headers son las instrucciones que le das al mesero **además** de tu orden. "Soy vegetariano" (`Accept`), "aquí está mi reservación" (`x-api-key`), "quiero el menú de primavera" (`anthropic-version`).

---

## Anatomía de una respuesta HTTP

El servidor procesa tu petición y devuelve una **response**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        HTTP RESPONSE                            │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ LÍNEA DE ESTADO (status line)                             │  │
│  │                                                           │  │
│  │   HTTP/1.1 200 OK                                         │  │
│  │   ──┬───── ─┬─ ─┬                                        │  │
│  │     │       │   │                                         │  │
│  │     │       │   └── frase descriptiva (para humanos)      │  │
│  │     │       └── código de estado (para máquinas)          │  │
│  │     └── versión del protocolo                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ HEADERS                                                   │  │
│  │                                                           │  │
│  │   Content-Type: application/json                          │  │
│  │   x-request-id: req_01ABC...                             │  │
│  │   x-ratelimit-limit: 1000                                │  │
│  │   x-ratelimit-remaining: 999                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ── línea en blanco ──                                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ BODY                                                      │  │
│  │                                                           │  │
│  │   {                                                       │  │
│  │     "id": "msg_01XFDUDYJgAACzvnptvVoYEL",                │  │
│  │     "type": "message",                                    │  │
│  │     "role": "assistant",                                  │  │
│  │     "content": [                                          │  │
│  │       {                                                   │  │
│  │         "type": "text",                                   │  │
│  │         "text": "Una API es..."                           │  │
│  │       }                                                   │  │
│  │     ],                                                    │  │
│  │     "model": "claude-sonnet-4-20250514",                          │  │
│  │     "usage": {                                            │  │
│  │       "input_tokens": 14,                                 │  │
│  │       "output_tokens": 52                                 │  │
│  │     }                                                     │  │
│  │   }                                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Métodos HTTP

HTTP define un conjunto de **métodos** (también llamados verbos) que indican la intención de la petición. Cada método tiene una semántica clara:

| Método | En el restaurante | En APIs | Ejemplo LLM | Body |
|--------|-------------------|---------|-------------|------|
| **GET** | "¿Qué platillos tienen hoy?" | Leer un recurso | Obtener lista de modelos | No |
| **POST** | "Quiero ordenar este platillo" | Crear un recurso nuevo | Enviar mensaje al LLM | Si |
| **PUT** | "Cambie toda mi orden por esta otra" | Reemplazar un recurso completo | Actualizar configuración de assistant | Si |
| **PATCH** | "Agregue salsa extra a mi orden" | Modificar parte de un recurso | Cambiar nombre de un fine-tune | Si |
| **DELETE** | "Cancele mi orden" | Eliminar un recurso | Borrar una API key | No |

### Propiedades de los métodos

```
                    Idempotente         Seguro
                  (repetir no          (no modifica
                   cambia nada)         el estado)
                  ┌───────────┐       ┌───────────┐
  GET ────────────│    SI     │───────│    SI     │
  POST ───────────│    NO     │───────│    NO     │
  PUT ────────────│    SI     │───────│    NO     │
  PATCH ──────────│    NO*    │───────│    NO     │
  DELETE ─────────│    SI     │───────│    NO     │
                  └───────────┘       └───────────┘

  * PATCH puede ser idempotente dependiendo de la implementación
```

**Idempotente** significa que hacer la misma petición 1 vez o 100 veces produce el mismo resultado. `GET /models` siempre devuelve la misma lista. `DELETE /key/123` borra la key la primera vez; las siguientes no cambian nada (ya está borrada). Pero `POST /v1/messages` envía un mensaje nuevo cada vez.

---

## Códigos de estado HTTP

El código de estado es un número de tres digitos que indica el resultado de la petición. Los primeros digitos definen la categoría:

```
  1xx ── Informacional (raro en APIs)
  2xx ── Exito
  3xx ── Redirección
  4xx ── Error del cliente (TU culpa)
  5xx ── Error del servidor (SU culpa)
```

### Los que verás constantemente

| Código | Significado | En el restaurante | Cuándo lo ves en APIs LLM |
|--------|-------------|-------------------|--------------------------|
| **200** OK | Todo bien, aquí está tu respuesta | "Aqui tiene su plato, buen provecho" | Respuesta exitosa del LLM |
| **201** Created | Se creó un recurso nuevo | "Nueva orden registrada, en un momento sale" | Fine-tune job creado |
| **204** No Content | Hecho, pero no hay nada que devolver | "Listo, su orden fue cancelada" | API key eliminada |
| **400** Bad Request | Tu petición no tiene sentido | "No entiendo su pedido --- ¿'pasta con helado de atun'?" | JSON malformado, campo faltante |
| **401** Unauthorized | No te identificaste | "No tiene reservación, no puedo dejarlo pasar" | Falta API key o es inválida |
| **403** Forbidden | Te identificaste pero no tienes permiso | "Tiene reservación pero no para la zona VIP" | API key válida pero sin permiso para ese modelo |
| **404** Not Found | Ese recurso no existe | "Ese platillo no existe en nuestro menú" | Endpoint incorrecto, modelo inexistente |
| **405** Method Not Allowed | El recurso existe pero no acepta ese método | "No puede cancelar un plato que ya se sirvió" | GET a un endpoint que solo acepta POST |
| **413** Payload Too Large | Enviaste demasiados datos | "Esa orden es demasiado grande, no cabe en la comanda" | Contexto excede el limite de tokens |
| **422** Unprocessable Entity | La sintaxis está bien pero la semántica no | "Entiendo las palabras pero no se puede: 'filete término -3'" | `max_tokens: -1`, `model: "no-existe"` |
| **429** Too Many Requests | Estás pidiendo demasiado rápido | "Está pidiendo demasiado rápido, espere un momento" | Rate limit --- muy común con APIs de LLM |
| **500** Internal Server Error | Algo se rompió en el servidor | "Se cayó la cocina, disculpe" | Bug en el servidor del proveedor |
| **502** Bad Gateway | El proxy/gateway recibió basura del servidor real | "El intercomunicador con la cocina falla" | Load balancer no puede contactar el backend |
| **503** Service Unavailable | Servidor sobrecargado o en mantenimiento | "Estamos llenos, no aceptamos más clientes" | Servidor del LLM sobrecargado |

### El código que nunca esperarías

HTTP tiene un easter egg oficial: el código **418 I'm a teapot**. Fue definido en el [RFC 2324](https://datatracker.ietf.org/doc/html/rfc2324) como parte del *Hyper Text Coffee Pot Control Protocol* (HTCPCP) --- una broma del April Fools de 1998.

```
  418 I'm a teapot

  "Me pides que prepare café, pero soy una tetera."

  El servidor se rehúsa a preparar café porque es,
  permanente y orgullosamente, una tetera.
```

No es solo una curiosidad --- el 418 se usa en la práctica como respuesta genérica de "no voy a hacer eso" en servicios que quieren rechazar peticiones sin dar información específica (anti-bot, honeypots). Google lo devuelve en [google.com/teapot](https://www.google.com/teapot).

### Cómo manejar errores en Python

```python
import requests

response = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers={"x-api-key": API_KEY, "content-type": "application/json",
             "anthropic-version": "2023-06-01"},
    json={"model": "claude-sonnet-4-20250514", "max_tokens": 1024,
          "messages": [{"role": "user", "content": "Hola"}]}
)

if response.status_code == 200:
    data = response.json()
    print(data["content"][0]["text"])
elif response.status_code == 429:
    retry_after = response.headers.get("retry-after", 60)
    print(f"Rate limit. Reintenta en {retry_after}s")
elif response.status_code == 401:
    print("API key inválida")
else:
    print(f"Error {response.status_code}: {response.text}")
```

---

## Anatomía de una URL

Cada petición HTTP se dirige a una URL. Entender sus partes es fundamental:

```
  https://api.anthropic.com:443/v1/messages?model=claude-sonnet-4-20250514#usage
  ──┬──   ───────┬─────────  ─┬─ ─────┬────  ──────────┬───────────  ──┬──
    │            │            │       │               │               │
 scheme        host         port    path           query          fragment
    │            │            │       │               │               │
    │            │            │       │               │               └─ ancla local
    │            │            │       │               │                  (no se envía
    │            │            │       │               │                   al servidor)
    │            │            │       │               │
    │            │            │       │               └─ parámetros clave=valor
    │            │            │       │                  separados por &
    │            │            │       │
    │            │            │       └─ ruta al recurso
    │            │            │          (como un path en el filesystem)
    │            │            │
    │            │            └─ puerto (443 = HTTPS, 80 = HTTP)
    │            │               se omite cuando es el default
    │            │
    │            └─ servidor destino
    │               (se resuelve a IP via DNS)
    │
    └─ protocolo de transporte
       http = sin encriptar (NUNCA para APIs con datos sensibles)
       https = encriptado con TLS
```

### Ejemplos reales

```
GET  https://api.anthropic.com/v1/models
     └── listar modelos disponibles

POST https://api.anthropic.com/v1/messages
     └── enviar mensaje al LLM

GET  https://api.anthropic.com/v1/messages/msg_01ABC
     └── obtener un mensaje específico por ID

POST https://api.openai.com/v1/fine_tuning/jobs
     └── crear un job de fine-tuning

GET  https://api.openai.com/v1/fine_tuning/jobs/ft-123/events?limit=10
     └── obtener los últimos 10 eventos del job ft-123
```

---

## Headers: los metadatos de la comunicación

Los headers son pares clave-valor que acompañan a cada request y response. No son los datos en sí, sino **metadatos sobre la comunicación**:

| Header | Dirección | En el restaurante | Ejemplo |
|--------|-----------|-------------------|---------|
| `Content-Type` | Request y Response | "Esta orden está escrita en español" | `application/json` |
| `Accept` | Request | "Quiero la respuesta en español, no en francés" | `application/json` |
| `Authorization` | Request | "Aquí está mi reservación" | `Bearer sk-...` |
| `x-api-key` | Request | "Mi número de cliente frecuente" | `sk-ant-api03-...` |
| `anthropic-version` | Request | "Quiero el menú de primavera 2023" | `2023-06-01` |
| `Content-Length` | Request y Response | "Mi orden tiene 3 renglones" | `256` (bytes) |
| `x-ratelimit-remaining` | Response | "Le quedan 5 órdenes más esta hora" | `999` |
| `retry-after` | Response | "Vuelva en 30 segundos" | `30` |
| `x-request-id` | Response | "Su número de ticket es 4827" | `req_01ABC...` |

### Headers en Python con requests

```python
headers = {
    "Content-Type": "application/json",
    "x-api-key": "sk-ant-api03-xxxxx",
    "anthropic-version": "2023-06-01",
    "Accept": "application/json",
}

response = requests.post(url, headers=headers, json=body)

# Inspeccionar headers de la respuesta
print(response.headers["content-type"])
print(response.headers.get("x-ratelimit-remaining"))
print(response.headers.get("x-request-id"))
```

---

## HTTPS y TLS: por qué importa la encriptación

HTTP transmite todo en **texto plano**. Cualquier nodo intermedio (tu ISP, el WiFi del café, un proxy corporativo) puede leer tus peticiones --- incluyendo tu API key.

**HTTPS** = HTTP + TLS (Transport Layer Security). TLS encripta toda la comunicación entre cliente y servidor:

```
Sin TLS (HTTP):

  Tu código ────── "x-api-key: sk-ant-..." ──────▶ Servidor
                          │
                     ┌────┴────┐
                     │  ISP,   │
                     │  WiFi,  │  ◀── puede leer TODO
                     │  proxy  │
                     └─────────┘


Con TLS (HTTPS):

  Tu código ────── [datos encriptados] ──────▶ Servidor
                          │
                     ┌────┴────┐
                     │  ISP,   │
                     │  WiFi,  │  ◀── ve basura ilegible
                     │  proxy  │
                     └─────────┘
```

**Regla simple:** si la URL empieza con `http://` y estás enviando API keys o datos sensibles, **algo está mal**. Todas las APIs de LLM usan HTTPS exclusivamente.

No necesitas entender los detalles criptográficos (cifrados, certificados, cadenas de confianza). Lo que necesitas saber es:

1. HTTPS encripta la comunicación punto a punto
2. El costo de performance es mínimo (~1-2ms extra por TLS handshake)
3. Siempre usa HTTPS para APIs con autenticación

---

## Desglose de latencia de una petición HTTP

Cuando haces una petición HTTP, el tiempo total no es solo "el servidor piensa". Hay múltiples etapas, cada una con su costo:

```
  t₀          t₁         t₂         t₃         t₄             t₅          t₆
  │           │          │          │          │              │           │
  ├───────────┼──────────┼──────────┼──────────┼──────────────┼───────────┤
  │           │          │          │          │              │           │
  │  DNS      │   TCP    │   TLS    │  Enviar  │   Servidor   │  Recibir  │
  │  lookup   │  hand-   │  hand-   │  request │   procesa    │  response │
  │           │  shake   │  shake   │          │              │           │
  │  ~5ms     │  ~10ms   │  ~15ms   │  ~2ms    │   ~1500ms    │  ~5ms     │
  │           │          │          │          │              │           │
  │ ¿quién es │ SYN →    │ certifi- │ bytes    │ inferencia   │ bytes     │
  │ api.      │ SYN-ACK →│ cados,   │ del      │ del LLM,    │ de la     │
  │ anthropic │ ACK      │ claves   │ request  │ base de      │ respuesta │
  │ .com?     │          │ simétr.  │ viajan   │ datos, etc.  │ viajan    │
  └───────────┴──────────┴──────────┴──────────┴──────────────┴───────────┘
                                                      │
                                                      │ ← ~97% del tiempo
                                                      │    para APIs de LLM
```

$$T_{total} = T_{DNS} + T_{TCP} + T_{TLS} + T_{req} + T_{server} + T_{resp}$$

Para una llamada típica a un LLM:

$$T_{total} \approx 5 + 10 + 15 + 2 + 1500 + 5 = 1537\text{ms}$$

Observa que $T_{server}$ domina con ~97% del tiempo total. Esto tiene dos implicaciones:

1. **Optimizar DNS, TCP o TLS** (connection pooling, HTTP keep-alive) ayuda marginalmente
2. **La verdadera optimización** es no esperar a que $T_{server}$ termine completamente antes de empezar a procesar --- esto motiva el **streaming** (Sección 04)

### Connection pooling y keep-alive

En la práctica, no pagas DNS + TCP + TLS en cada petición. HTTP/1.1 mantiene conexiones abiertas (`keep-alive`) y las librerías como `requests.Session()` y `httpx.Client()` reutilizan conexiones:

```
Primera petición:
  DNS + TCP + TLS + request + server + response  =  ~1537ms

Siguientes peticiones (misma conexión):
  request + server + response  =  ~1507ms

  Ahorro: ~30ms por petición (2%)
```

```python
# SIN pooling (nueva conexión cada vez)
for prompt in prompts:
    response = requests.post(url, headers=h, json=body)  # DNS+TCP+TLS cada vez

# CON pooling (reutiliza conexión)
session = requests.Session()
session.headers.update(h)
for prompt in prompts:
    response = session.post(url, json=body)  # solo request+server+response
```

---

## HTTP/1.1 vs HTTP/2 vs HTTP/3

La evolución de HTTP ha mejorado la eficiencia del transporte:

```
HTTP/1.1 (1997)                 HTTP/2 (2015)               HTTP/3 (2022)
━━━━━━━━━━━━━━━                ━━━━━━━━━━━━━                ━━━━━━━━━━━━━

  ┌──────┐                       ┌──────┐                    ┌──────┐
  │req 1 │ ────▶ resp 1          │req 1 │─┐                  │req 1 │─┐
  └──────┘                       │req 2 │─┤ multiplexado     │req 2 │─┤ QUIC
  ┌──────┐  (espera)             │req 3 │─┘ (una conexión)   │req 3 │─┘ (UDP)
  │req 2 │ ────▶ resp 2          └──────┘                    └──────┘
  └──────┘                          │                           │
  ┌──────┐  (espera)                ▼                           ▼
  │req 3 │ ────▶ resp 3          ┌──────┐                    ┌──────┐
  └──────┘                       │resp 1│                    │resp 2│ ◀─ sin
                                 │resp 3│ ◀─ en cualquier   │resp 1│    head-of-
  Una petición a la vez          │resp 2│    orden           │resp 3│    line
  por conexión (head-of-line)    └──────┘                    └──────┘    blocking
```

Para APIs de LLM, HTTP/2 es el estándar actual. La mayoría de los proveedores (Anthropic, OpenAI) lo soportan. `httpx` usa HTTP/2 por defecto cuando está disponible; `requests` usa HTTP/1.1.

---

## Resumen visual: el flujo completo

```
Tu programa Python
       │
       │  1. Construir request
       │     - método: POST
       │     - URL: https://api.anthropic.com/v1/messages
       │     - headers: api-key, content-type, version
       │     - body: JSON con modelo, tokens, mensajes
       │
       ▼
┌─────────────┐
│  requests   │  ── serializar JSON, agregar headers
│  / httpx    │
└──────┬──────┘
       │
       │  2. Resolver DNS  (api.anthropic.com → 104.18.x.x)
       │  3. TCP handshake (SYN, SYN-ACK, ACK)
       │  4. TLS handshake (certificados, claves)
       │  5. Enviar bytes del request
       │
       ▼
┌─────────────┐
│  Servidor   │  ── autenticar, validar, procesar
│  Anthropic  │  ── inferencia en GPU (~1500ms)
└──────┬──────┘
       │
       │  6. Enviar bytes de la response
       │     - status: 200 OK
       │     - headers: content-type, rate-limit info
       │     - body: JSON con respuesta del LLM
       │
       ▼
┌─────────────┐
│  requests   │  ── deserializar JSON
│  / httpx    │
└──────┬──────┘
       │
       │  7. Tu código recibe un objeto Response
       │     response.status_code → 200
       │     response.json() → {"content": [...], "usage": {...}}
       │
       ▼
  Listo. Toda la magia de HTTP ocurrió entre los pasos 2-6,
  invisible para tu código gracias a la librería.
```

---

> **Verifica en el notebook:** Notebook 01 --- Sección 2 contiene ejercicios prácticos donde construyes peticiones HTTP manualmente con `requests`, inspeccionas headers, manejas errores por código de estado, y mides la latencia de cada etapa.

---

:::exercise{title="Anatomía de peticiones reales"}
Usando `requests` en Python (o `curl` en terminal), realiza las siguientes peticiones y para cada una documenta: método, URL, headers enviados, status code recibido, y headers de respuesta relevantes.

1. `GET https://httpbin.org/get` --- ¿Qué headers envía `requests` por defecto?
2. `POST https://httpbin.org/post` con body `{"curso": "fdd", "seccion": 18}` --- ¿Cómo se ve el body en la respuesta de httpbin?
3. `GET https://httpbin.org/status/429` --- ¿Qué status code recibes? ¿Hay un header `retry-after`?
4. `GET https://httpbin.org/delay/3` --- Mide el tiempo total con `time.time()`. ¿Cuánto tarda? ¿Dónde se va el tiempo según el desglose de latencia?

Bonus: repite la petición 4 pero usando `requests.Session()` dos veces seguidas. ¿La segunda es más rápida? ¿Por qué?
:::
