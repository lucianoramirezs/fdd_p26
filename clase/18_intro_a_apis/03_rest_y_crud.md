---
title: "REST y CRUD"
---

# REST y CRUD

## La analogía: REST = el menú numerado

Vuelve al restaurante de la sección 16. Ahora no estás en la cocina — estás en el **comedor**.

REST es **el menú numerado del restaurante**:

- Cada **recurso** tiene una dirección (URL): `/mesas/7`, `/ordenes/42`.
- Cada **acción** tiene un verbo (método HTTP): `GET`, `POST`, `PUT`, `DELETE`.
- El menú **no recuerda quién eres** — cada vez que llamas al mesero, tienes que decirle tu mesa y tu orden desde cero (**stateless**).

```
+-----------------------------------------------------------+
|                    MENÚ DEL RESTAURANTE                   |
|                     (Interfaz REST)                       |
+-----------------------------------------------------------+
|                                                           |
|   RECURSO: /ordenes                                       |
|   ┌─────────────────────────────────────────────────┐     |
|   │  POST   → Crear nueva orden                    │     |
|   │  GET    → Ver todas las órdenes                │     |
|   └─────────────────────────────────────────────────┘     |
|                                                           |
|   RECURSO: /ordenes/{id}                                  |
|   ┌─────────────────────────────────────────────────┐     |
|   │  GET    → Ver una orden específica              │     |
|   │  PUT    → Reemplazar toda la orden              │     |
|   │  PATCH  → Cambiar un detalle (guarnición)       │     |
|   │  DELETE → Cancelar la orden                     │     |
|   └─────────────────────────────────────────────────┘     |
|                                                           |
+-----------------------------------------------------------+
```

---

## Los cinco principios REST

REST no es un protocolo ni una librería. Es un **estilo arquitectónico** definido por Roy Fielding en su tesis doctoral (2000). Cinco restricciones lo definen:

```
+--------------------+----------------------------------------+-----------------------------+
| Principio          | Qué significa                          | En el restaurante           |
+--------------------+----------------------------------------+-----------------------------+
| Orientado a        | Todo se modela como un recurso         | Mesas, órdenes, platillos   |
| recursos           | con una URL única                      | — cada uno tiene un número  |
+--------------------+----------------------------------------+-----------------------------+
| Stateless          | Cada petición contiene TODA            | El mesero no recuerda       |
|                    | la información necesaria               | tu cara — muestra tu ticket |
+--------------------+----------------------------------------+-----------------------------+
| Interfaz           | Mismos verbos HTTP para todo:          | El menú tiene las mismas    |
| uniforme           | GET, POST, PUT, PATCH, DELETE          | secciones en todo el mundo  |
+--------------------+----------------------------------------+-----------------------------+
| Cliente-Servidor   | El que pide y el que cocina            | Comedor y cocina son        |
|                    | son independientes                     | mundos separados            |
+--------------------+----------------------------------------+-----------------------------+
| Sistema en         | Puede haber intermediarios             | El expedidor entre mesero   |
| capas              | (cache, balanceador, proxy)            | y cocina                    |
+--------------------+----------------------------------------+-----------------------------+
```

---

## CRUD → HTTP: la tabla central

CRUD (Create, Read, Update, Delete) es el modelo de operaciones de datos. HTTP le da un verbo a cada una.

```
+---------+--------+-------------------------+-----------------------------+
| CRUD    | HTTP   | Restaurante             | API de LLM                  |
+---------+--------+-------------------------+-----------------------------+
| Create  | POST   | "Nueva orden de tacos"  | Crear mensaje/conversación  |
+---------+--------+-------------------------+-----------------------------+
| Read    | GET    | "¿Qué pedí en mesa 7?"  | Leer conversación existente |
+---------+--------+-------------------------+-----------------------------+
| Update  | PUT /  | "Cambia la guarnición   | Editar configuración del    |
|         | PATCH  |  de arroz a ensalada"   |  modelo o parámetros        |
+---------+--------+-------------------------+-----------------------------+
| Delete  | DELETE | "Cancela mi orden"      | Borrar conversación/thread  |
+---------+--------+-------------------------+-----------------------------+
```

Nota que `PUT` reemplaza **todo** el recurso y `PATCH` modifica **una parte**. En el restaurante: `PUT` es "quiero otra orden completamente distinta", `PATCH` es "solo cambia la bebida".

---

## Un API de LLM como ejemplo REST

Cuando usas un SDK para hablar con un LLM, parece magia. Pero debajo hay HTTP puro. Veamos ambas capas:

```python
# Lo que escribes (SDK)
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hola"}]
)
```

```python
# Lo que viaja por la red (HTTP)
# POST https://api.anthropic.com/v1/messages
# Headers: x-api-key: sk-ant-..., content-type: application/json
# Body: {"model": "...", "messages": [...]}
```

```
+------------------+                              +------------------+
|   Tu programa    |    POST /v1/messages         |   Servidor LLM   |
|   (cliente)      | ──────────────────────────►  |   (API REST)     |
|                  |                              |                  |
|                  |    200 OK + JSON response    |                  |
|                  | ◄──────────────────────────  |                  |
+------------------+                              +------------------+

        SDK = envoltorio amigable          HTTP = lo que realmente pasa
```

El SDK esconde tres cosas: (1) construir la URL, (2) serializar a JSON, (3) manejar headers de autenticación. Pero **debajo siempre hay HTTP**.

---

## Diseño de recursos: jerarquía de endpoints

Un API REST bien diseñado se lee como un árbol de recursos. Aquí el de una plataforma LLM:

```
/v1
├── /models
│   ├── GET  /v1/models              → Listar modelos disponibles
│   └── GET  /v1/models/{id}         → Detalle de un modelo
│
├── /messages
│   └── POST /v1/messages            → Crear un mensaje (inference)
│
├── /fine-tuning
│   ├── GET  /v1/fine-tuning/jobs           → Listar trabajos
│   ├── POST /v1/fine-tuning/jobs           → Crear trabajo de fine-tuning
│   ├── GET  /v1/fine-tuning/jobs/{id}      → Estado de un trabajo
│   └── POST /v1/fine-tuning/jobs/{id}/cancel → Cancelar trabajo
│
└── /usage
    └── GET  /v1/usage               → Consultar consumo de tokens
```

Observa las convenciones:

- **Sustantivos** en las URLs, nunca verbos (`/messages`, no `/sendMessage`).
- **Plural** para colecciones (`/models`), singular implícito con ID (`/models/claude-3`).
- **Jerarquía** natural: `/fine-tuning/jobs/{id}` — un job pertenece a fine-tuning.
- **Versionado** con prefijo `/v1` — permite evolucionar sin romper clientes.

---

## JSON: el formato que ganó

Las APIs REST pueden usar cualquier formato, pero JSON ganó la batalla. Compáralo con XML:

```
JSON (97 bytes):                        XML (184 bytes):
{                                       <?xml version="1.0"?>
  "model": "claude-sonnet-4-20250514",             <request>
  "messages": [                           <model>claude-sonnet-4-20250514</model>
    {                                     <messages>
      "role": "user",                       <message>
      "content": "Hola"                      <role>user</role>
    }                                         <content>Hola</content>
  ]                                         </message>
}                                         </messages>
                                        </request>
```

```
+-----------+------------------+------------------+
| Criterio  | JSON             | XML              |
+-----------+------------------+------------------+
| Tamaño    | Compacto         | Verboso          |
| Parseo    | Nativo en JS     | Requiere parser  |
| Tipos     | string, number,  | Todo es texto    |
|           | bool, null,      |                  |
|           | array, object    |                  |
| Esquema   | JSON Schema      | XSD (complejo)   |
| Adopción  | ~95% de APIs     | Legacy/enterprise|
+-----------+------------------+------------------+
```

JSON ganó porque es **más ligero** y **nativo** en los navegadores web (JavaScript Object Notation). Hoy prácticamente todo API nuevo usa JSON.

---

## Los límites de REST

REST es excelente para operaciones CRUD simples. Pero tiene limitaciones que motivan otros protocolos:

```
+---------------------------+-----------------------------------+------------------+
| Limitación de REST        | Problema concreto                 | Solución         |
+---------------------------+-----------------------------------+------------------+
| Sin push del servidor     | El cliente tiene que preguntar    | SSE              |
|                           | "¿ya hay respuesta?" una y otra   | (archivo 04)     |
|                           | vez (polling)                     |                  |
+---------------------------+-----------------------------------+------------------+
| Sin bidireccionalidad     | No puedes enviar y recibir       | WebSocket        |
|                           | simultáneamente en la misma      | (archivo 05)     |
|                           | conexión                         |                  |
+---------------------------+-----------------------------------+------------------+
| Over-fetching             | Pides /user y te devuelve 47     | GraphQL          |
|                           | campos cuando solo necesitas 3   | (archivo 08)     |
+---------------------------+-----------------------------------+------------------+
| Overhead de texto         | Headers HTTP + JSON en cada      | gRPC + protobuf  |
|                           | request — lento para servicios   | (archivo 07)     |
|                           | internos de alto volumen         |                  |
+---------------------------+-----------------------------------+------------------+
```

```
Flujo REST clásico (request-response):

  Cliente                    Servidor
    │                          │
    │──── POST /messages ────► │
    │                          │  ... servidor piensa 5 seg ...
    │◄─── 200 OK + body ───── │
    │                          │
    │  (silencio total         │
    │   durante 5 segundos)    │
    │                          │

¿Y si quisieras ver la respuesta MIENTRAS se genera?
→ Necesitas streaming (archivo 04)
```

---

> **Verifica en el notebook:** Revisa `clase/18_intro_a_apis/code/01_rest_y_json.ipynb` donde hacemos peticiones REST reales a APIs públicas y analizamos las respuestas JSON.

---

:::exercise{title="Diseña los endpoints REST de un servicio de streaming de música"}

Diseña la API REST para un servicio de streaming de música (estilo Spotify). Debe cubrir al menos estos recursos: usuarios, playlists, canciones y artistas.

Para cada endpoint indica:

1. **Método HTTP** (GET, POST, PUT, PATCH, DELETE)
2. **URL** con el patrón de recurso
3. **Qué hace** (una línea)
4. **Ejemplo de body** (para POST/PUT/PATCH) o **ejemplo de respuesta** (para GET)

Requisitos mínimos:
- Al menos **12 endpoints**
- Incluye relaciones: una playlist tiene canciones, un artista tiene álbumes
- Incluye un endpoint de **búsqueda** (`/search?q=...`)
- Sigue las convenciones REST: sustantivos plurales, jerarquía lógica, versionado

Pregunta extra: ¿qué limitación de REST encontrarías si quisieras mostrar el progreso de una canción en tiempo real a todos los seguidores de un usuario? ¿Qué protocolo usarías en su lugar?

:::
