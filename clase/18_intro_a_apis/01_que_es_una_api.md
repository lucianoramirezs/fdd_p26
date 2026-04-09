---
title: "¿Qué es una API?"
---

# ¿Qué es una API?

En la sección 16, la cocina del restaurante era el cómputo. Construiste modelos de ejecución: secuencial, concurrente, paralelo. El cocinero, los fogones, el horno, los cuchillos --- todo sucedía dentro de la cocina.

Pero un restaurante no es solo una cocina. Hay un **comedor** lleno de clientes, y hay un problema fundamental: **¿cómo llega la orden del cliente a la cocina?**

---

## La pieza faltante: el mesero

```
┌──────────────────────────────────┐     ┌──────────────────────────────────┐
│           COMEDOR                │     │            COCINA                │
│                                  │     │                                  │
│  ┌────────┐  ┌────────┐         │     │  ┌─────────┐  ┌─────────┐       │
│  │Cliente │  │Cliente │         │     │  │Cocinero │  │Cocinero │       │
│  │   A    │  │   B    │         │     │  │  θ₁     │  │  θ₂     │       │
│  └───┬────┘  └───┬────┘         │     │  └─────────┘  └─────────┘       │
│      │           │              │     │       ▲              ▲           │
│      │           │              │     │       │              │           │
│      ▼           ▼              │     │       │              │           │
│  ┌───────────────────────────┐  │     │  ┌────┴──────────────┴────┐      │
│  │                           │  │     │  │                        │      │
│  │       M E S E R O         │──┼─────┼─▶│   TABLERO DE ÓRDENES  │      │
│  │                           │  │     │  │                        │      │
│  │  - Toma la orden          │  │     │  └────────────────────────┘      │
│  │  - La traduce al formato  │  │     │                                  │
│  │    que la cocina entiende │  │     │  La cocina no sabe quién         │
│  │  - Trae el plato de      │  │     │  pidió qué. Solo ve órdenes      │
│  │    vuelta al cliente      │  │     │  en un formato estándar.         │
│  └───────────────────────────┘  │     │                                  │
│                                  │     │                                  │
└──────────────────────────────────┘     └──────────────────────────────────┘

              EL MESERO ES LA API.
```

El mesero no cocina. El cliente no entra a la cocina. Hay un **contrato** entre ambos lados:

1. El **menú** define qué se puede pedir (la especificación de la API)
2. La **comanda** tiene un formato estándar (el protocolo)
3. El mesero traduce entre el lenguaje del cliente y el de la cocina (el cliente HTTP)
4. El plato sale en un formato predecible (la respuesta)

---

## Definición formal

**API** = *Application Programming Interface* = la interfaz que un sistema expone para que otros sistemas interactúen con él, sin necesidad de conocer su implementación interna.

```
                 ┌──────────────────┐
                 │                  │
  Sistema A ────▶│       API        │────▶ Sistema B
  (cliente)      │                  │      (servidor)
                 │  - Qué puedes    │
  "No sé cómo   │    pedir         │      "No me importa
   funciona B    │  - En qué        │       quién pide.
   por dentro"   │    formato       │       Solo proceso
                 │  - Qué recibes   │       órdenes válidas."
                 │    de vuelta     │
                 └──────────────────┘
```

La palabra clave es **contrato**. La API define:

- **Qué operaciones** están disponibles (endpoints, métodos)
- **Qué datos** necesita cada operación (parámetros, body)
- **Qué respuesta** devuelve (formato, códigos de estado)
- **Qué errores** pueden ocurrir (y cómo se reportan)

Lo que la API **no** expone:

- Cómo funciona internamente el sistema
- Qué base de datos usa
- En qué lenguaje está implementado
- Cuántos servidores hay detrás

---

## La analogía extendida: del restaurante al LLM

En la sección 16, la tabla de correspondencia cubría la cocina. Ahora la extendemos al comedor:

| En el restaurante | En APIs | Ejemplo LLM |
|---|---|---|
| Menú | API specification | Documentación de endpoints |
| Mesero | Cliente HTTP | `requests`, SDK de Anthropic |
| Orden (lo que dice el cliente) | Request | `POST /v1/messages` |
| Plato servido | Response | JSON con la respuesta del LLM |
| Comanda (formato escrito de la orden) | Protocolo | HTTP, gRPC, WebSocket |
| Idioma del restaurante | Formato de datos | JSON, XML, Protobuf |
| Timbre de "listo" | Webhook / callback | Notificación de fine-tuning completado |
| Intercomunicador cocina-cocina | gRPC interno | Model serving entre servicios |
| "¿Ya está mi orden?" (el cliente pregunta) | Polling | Revisar status de un job |
| Buzzer vibratorio en la mesa | WebSocket | Chat en tiempo real |

Observa que el **mesero** no es un concepto nuevo --- es lo que faltaba entre la sección 16 (la cocina) y el mundo exterior. Cada paradigma de API que veremos en este módulo es una **forma diferente de mesero**.

---

## Historia: cómo llegamos aquí

Las APIs no nacieron con la web. La idea de "interfaz entre sistemas" es tan vieja como la programación misma:

```
 1960s         1970s-80s         1990s           2000s           2010s          2020s
   │               │               │               │               │              │
   ▼               ▼               ▼               ▼               ▼              ▼
┌──────┐     ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   ┌──────────┐
│Library│     │ IPC/RPC  │    │ CORBA    │    │ SOAP/XML │    │REST/JSON │   │gRPC      │
│ APIs  │     │          │    │ DCOM     │    │ WSDL     │    │ GraphQL  │   │ SSE      │
│       │     │ sockets  │    │          │    │          │    │          │   │ WebSocket│
│"llama │     │"procesos │    │"objetos  │    │"XML      │    │"simple   │   │"streaming│
│ esta  │     │ hablan   │    │ remotos" │    │ pesado"  │    │ y ligero"│   │ y        │
│función│     │ entre sí"│    │          │    │          │    │          │   │ bidirec- │
│local" │     │          │    │          │    │          │    │          │   │ cional"  │
└──────┘     └──────────┘    └──────────┘    └──────────┘    └──────────┘   └──────────┘
   │               │               │               │               │              │
   │               │               │               │               │              │
   ▼               ▼               ▼               ▼               ▼              ▼
 math.sin()    Unix pipes      Enterprise     Bancos,          Twitter,       ChatGPT,
 printf()      socket()        Java/C++       gobiernos        GitHub,        Claude,
                                               SAP              Stripe         Gemini
```

### Cada era resolvió un problema y creó otro

| Era | Innovación | Problema que resolvió | Problema que creó |
|-----|-----------|----------------------|-------------------|
| **Library APIs** | Funciones reutilizables | No reescribir código | Solo funciona en el mismo proceso |
| **IPC/RPC** | Comunicación entre procesos | Procesos aislados necesitan hablar | Acoplamiento fuerte, difícil de escalar |
| **CORBA/DCOM** | Objetos distribuidos | Transparencia de ubicación | Complejidad monstruosa, vendor lock-in |
| **SOAP/XML** | Estándar de mensajería web | Interoperabilidad entre lenguajes | XML verboso, contratos rígidos, lento |
| **REST/JSON** | Simplicidad sobre HTTP | Fácil de entender, ligero, stateless | Over-fetching, under-fetching, sin tipos |
| **gRPC/GraphQL** | Eficiencia y flexibilidad | Consultas precisas, streaming, binario | Mayor complejidad inicial |

Hoy, en 2026, **REST con JSON sigue siendo el estándar dominante** para APIs públicas. Es lo que usan Anthropic, OpenAI, Google, GitHub, Stripe, y prácticamente cualquier servicio web. Pero no es el único paradigma --- y entender cuándo usar cada uno es parte de la ingeniería de datos.

---

## Anatomía de una llamada API al LLM

Cuando tu chatbot de la sección 16 llama al LLM (Escenario A: API remota), esto es lo que pasa por debajo:

```
Tu código Python                          Servidor del LLM
═══════════════                          ══════════════════

import anthropic
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Hola"
    }]
)
      │                                         │
      │  ┌────────────────────────────────┐     │
      │  │ HTTP Request (lo que viaja)    │     │
      │  │                                │     │
      │  │ POST /v1/messages HTTP/1.1     │     │
      │  │ Host: api.anthropic.com        │     │
      │  │ x-api-key: sk-ant-...         │     │
      │  │ Content-Type: application/json │     │
      │  │                                │     │
      │  │ {"model": "claude-sonnet-4-20250514", │     │
      │  │  "max_tokens": 1024,           │     │
      │  │  "messages": [{"role": "user", │     │
      │  │    "content": "Hola"}]}        │     │
      └──┤                                ├────▶│
         └────────────────────────────────┘     │
                                                │
                                    ┌───────────┤  inferencia
                                    │ GPU       │  (~1500ms)
                                    │ cluster   │
                                    └───────────┤
                                                │
      ┌──────────────────────────────────┐      │
      │ HTTP Response (lo que regresa)   │      │
      │                                  │      │
      │ HTTP/1.1 200 OK                  │      │
      │ Content-Type: application/json   │      │
      │                                  │      │
      │ {"id": "msg_01...",              │      │
      │  "content": [{"type": "text",    │      │
      │    "text": "¡Hola! ¿En qué..."}]│      │
      │  "model": "claude-sonnet-4-20250514",   │      │
      │  "usage": {"input_tokens": 10,   │      │
      │    "output_tokens": 25}}         │      │
◀─────┤                                  │──────┘
      └──────────────────────────────────┘
```

El SDK de Python (`anthropic.Anthropic()`) es el **mesero**: toma tu orden en Python, la traduce a una petición HTTP con JSON, la envía al servidor, espera la respuesta, y te la devuelve como un objeto Python.

---

## Tipos de APIs que cubriremos

No todos los meseros trabajan igual. A lo largo de este módulo veremos paradigmas distintos, cada uno optimizado para un caso de uso diferente:

```
               Complejidad de implementación ──────────────▶

    Simple                                              Complejo
      │                                                    │
      ▼                                                    ▼
  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
  │  REST  │   │  SSE   │   │  Web   │   │GraphQL │   │  gRPC  │
  │        │   │        │   │Socket  │   │        │   │        │
  │request │   │server  │   │ bidi-  │   │consulta│   │binario │
  │   ↓    │   │push    │   │reccio- │   │flexible│   │rápido  │
  │response│   │stream  │   │nal     │   │        │   │        │
  └────────┘   └────────┘   └────────┘   └────────┘   └────────┘
      │             │            │            │             │
      ▼             ▼            ▼            ▼             ▼
   "Dame la      "Dame la     "Hablemos    "Dame solo   "Necesito
    respuesta     respuesta    los dos      los campos    máxima
    completa"     token por    al mismo     que me        velocidad
                  token"       tiempo"      interesan"    entre
                                                          servicios"
      │             │            │            │             │
      ▼             ▼            ▼            ▼             ▼
   consultar     streaming   chat en      dashboard    inferencia
   historial,    de LLM,     tiempo       admin,       GPU,
   crear chat    fine-tune    real         analytics    model
                 progress                               serving
```

### La pregunta de diseño

Para cada flecha en la arquitectura del chatbot, la pregunta es:

1. **¿Quién inicia la comunicación?** Solo el cliente, solo el servidor, o ambos
2. **¿Cuántas respuestas hay?** Una sola, un stream continuo, o múltiples intercambios
3. **¿Qué tan pesados son los datos?** Texto JSON ligero vs binario masivo
4. **¿Se necesita en tiempo real?** Latencia de segundos vs milisegundos

```
                        ¿Quién inicia?
                   Solo cliente    Ambos
                   ┌──────────┬──────────┐
  ¿Cuántas         │          │          │
  respuestas?      │          │          │
                   │          │          │
  Una ─────────────│  REST    │    --    │
                   │          │          │
  Stream ──────────│  SSE     │WebSocket │
                   │          │          │
  Flexible query ──│ GraphQL  │    --    │
                   │          │          │
  Binario rápido ──│  gRPC    │  gRPC   │
                   │          │ (stream) │
                   └──────────┴──────────┘
```

En los siguientes archivos, abrimos cada una de estas cajas. Empezamos por lo más fundamental: HTTP, el protocolo que subyace a REST, SSE y GraphQL.

---

> **Verifica en el notebook:** Notebook 01 --- Sección 1 contiene una exploración interactiva de APIs públicas con `requests`, donde puedes ver la anatomía de las peticiones y respuestas en vivo.

---

:::exercise{title="Mapea las flechas del chatbot"}
Vuelve al diagrama de arquitectura del chatbot en `00_index.md`. Para cada flecha numerada (1-9):

1. Identifica **quién es el cliente** y **quién es el servidor**
2. ¿La comunicación es unidireccional o bidireccional?
3. ¿Se necesita una respuesta inmediata, o puede ser asíncrona?
4. Usando la tabla de analogía del restaurante, ¿qué tipo de "mesero" sería cada flecha?

Ejemplo para la flecha ④ (Server-LLM API):
- Cliente: tu API server. Servidor: Anthropic.
- Unidireccional con stream de respuesta (request -> stream de tokens).
- Se necesita lo antes posible (el usuario espera).
- Mesero que trae el plato bocado por bocado (SSE streaming).
:::
