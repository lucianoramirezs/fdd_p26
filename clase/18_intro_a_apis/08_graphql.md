---
title: "GraphQL"
---

# GraphQL

REST funciona increíblemente bien cuando cada recurso tiene un endpoint claro y los clientes necesitan datos predecibles. Pero hay un caso donde REST empieza a doler: cuando **distintos clientes necesitan datos distintos del mismo recurso**. Aquí es donde entra GraphQL.

## El problema con REST: over-fetching y under-fetching

### Over-fetching: recibes más de lo que necesitas

Imagina que tu dashboard de admin solo necesita el nombre y estado de cada modelo LLM:

```
GET /api/models/claude-3

Respuesta REST (20 campos, ~2KB):
┌──────────────────────────────────────────┐
│ {                                        │
│   "id": "claude-3",                      │  ← necesitas
│   "name": "Claude 3 Opus",               │  ← necesitas
│   "version": "2024.01",                  │
│   "parameters": 175000000000,            │
│   "architecture": "transformer",         │
│   "training_data_cutoff": "2024-04",     │
│   "context_window": 200000,              │
│   "status": "active",                    │  ← necesitas
│   "created_at": "2024-01-15T...",        │
│   "updated_at": "2024-03-20T...",        │
│   "pricing": {...},                      │
│   "capabilities": [...],                 │
│   "fine_tuning_supported": true,         │
│   "regions": [...],                      │
│   "rate_limits": {...},                  │
│   "deprecation_date": null,              │
│   "description": "...(500 chars)...",    │
│   "benchmarks": {...},                   │
│   "supported_languages": [...],          │
│   "documentation_url": "..."             │
│ }                                        │
└──────────────────────────────────────────┘

Necesitabas 3 campos. Recibiste 20.
Transferiste ~2KB. Necesitabas ~100 bytes.
```

### Under-fetching: necesitas más de lo que un endpoint te da

Ahora quieres mostrar una página con: info del modelo + uso del último mes + facturación:

```
Necesitas 3 requests REST separados:

Request 1:  GET /api/models/claude-3          → info del modelo
Request 2:  GET /api/models/claude-3/usage    → estadísticas de uso
Request 3:  GET /api/billing?model=claude-3   → datos de facturación

┌────────┐         ┌─────────┐
│Cliente │──GET──▶│Servidor │──▶ DB query 1 ──▶ Response 1 ──▶ │
│        │──GET──▶│         │──▶ DB query 2 ──▶ Response 2 ──▶ │ Render
│        │──GET──▶│         │──▶ DB query 3 ──▶ Response 3 ──▶ │
└────────┘         └─────────┘

3 round trips de red. 3 respuestas que parsear.
Latencia total = latencia_1 + latencia_2 + latencia_3
```

### Con GraphQL: 1 query, exactamente lo que necesitas

```
POST /graphql

{
  model(id: "claude-3") {
    name
    status
    usage(period: "2026-03") {
      totalRequests
      totalTokens
    }
    billing(period: "2026-03") {
      totalCost
      currency
    }
  }
}

Respuesta (~200 bytes):
{
  "data": {
    "model": {
      "name": "Claude 3 Opus",
      "status": "active",
      "usage": {
        "totalRequests": 1500000,
        "totalTokens": 890000000
      },
      "billing": {
        "totalCost": 4520.50,
        "currency": "USD"
      }
    }
  }
}

1 request. Exactamente los campos pedidos. Sin desperdicio.
```

---

## La analogía del restaurante

```
REST = Menú fijo
═══════════════
  "Quiero saber el precio del filete."

  Mesero: "El filete de res Angus certificado, importado de
           Argentina, madurado 28 días, cocido a la parrilla
           con sal de mar del Himalaya, acompañado de papas
           rostizadas con romero y ensalada mixta con vinagreta
           balsámica, cuesta $450 pesos."

  Tú solo querías el precio. Te dieron la biografía del filete.


GraphQL = "Solo dime lo que te pido"
════════════════════════════════════
  "Quiero nombre y precio del filete."

  Mesero: "Filete de res, $450."

  Exactamente lo que pediste. Nada más.
```

---

## Schema: el contrato de GraphQL

En GraphQL, el servidor define un **schema** — la descripción completa de qué datos existen y cómo se relacionan. Es como el menú completo del restaurante, pero tú eliges qué leer.

```graphql
# Tipos de datos
enum ModelStatus {
  ACTIVE
  DEPRECATED
  BETA
  OFFLINE
}

type Model {
  id: ID!
  name: String!
  version: String!
  parameters: Int!
  status: ModelStatus!
  contextWindow: Int!
  pricing: Pricing!
  usage(period: String!): UsageStats
}

type Pricing {
  inputPerToken: Float!
  outputPerToken: Float!
  currency: String!
}

type UsageStats {
  totalRequests: Int!
  totalTokens: Int!
  avgLatencyMs: Float!
}

# Puntos de entrada
type Query {
  models: [Model!]!
  model(id: ID!): Model
  usage(startDate: String!, endDate: String!): UsageStats!
}

type Mutation {
  createFineTuneJob(
    modelId: ID!
    datasetUrl: String!
    hyperparams: HyperparamsInput
  ): FineTuneJob!

  cancelFineTuneJob(jobId: ID!): FineTuneJob!
}
```

Los `!` significan *non-nullable* — el campo siempre tiene un valor. `[Model!]!` significa: la lista no es null, y ningún elemento dentro es null.

## Queries: pide exactamente lo que necesitas

```graphql
# Query simple: solo nombres y estados
query {
  models {
    name
    status
  }
}

# Respuesta:
# {
#   "data": {
#     "models": [
#       {"name": "Claude 3 Opus", "status": "ACTIVE"},
#       {"name": "Claude 3 Haiku", "status": "ACTIVE"},
#       {"name": "GPT-4", "status": "ACTIVE"}
#     ]
#   }
# }
```

Compara con REST, donde `GET /models` te retornaría **todos** los campos de cada modelo. En GraphQL, el cliente controla la forma de la respuesta.

```
REST:   El servidor decide qué campos enviar
        ┌──────────┐                    ┌──────────┐
        │ Cliente   │── GET /models ───▶│ Servidor │
        │ (recibe   │◀── TODOS los     │ (decide  │
        │  todo)    │    campos         │  la forma│
        └──────────┘                    └──────────┘

GraphQL: El cliente decide qué campos recibir
        ┌──────────┐                    ┌──────────┐
        │ Cliente   │── query {        │ Servidor │
        │ (pide lo  │   name, status   │ (retorna │
        │  que      │   } ────────────▶│  solo lo │
        │  quiere)  │◀── solo name    │  pedido) │
        │           │    y status      │          │
        └──────────┘                    └──────────┘
```

## Mutations: modificar datos

Las mutations son el equivalente de POST/PUT/DELETE en REST:

```graphql
mutation {
  createFineTuneJob(
    modelId: "claude-3"
    datasetUrl: "s3://mi-bucket/datos.jsonl"
    hyperparams: {
      epochs: 3
      learningRate: 0.0001
      batchSize: 32
    }
  ) {
    id
    status
    estimatedTime
  }
}

# Respuesta:
# {
#   "data": {
#     "createFineTuneJob": {
#       "id": "ft-abc123",
#       "status": "QUEUED",
#       "estimatedTime": "2h 30min"
#     }
#   }
# }
```

Nota que incluso en la mutation, tú decides qué campos de la respuesta quieres. No te fuerzan a recibir el objeto completo.

---

## GraphQL vs REST: comparación

```
                    REST                          GraphQL
                    ════                          ═══════

Endpoints:     GET /models                   POST /graphql
               GET /models/:id               (un solo endpoint)
               POST /models
               GET /models/:id/usage
               GET /billing
               (muchos endpoints)

Respuesta:     Fija por endpoint             Flexible por query
               (servidor decide)             (cliente decide)

Over-fetch:    Común                         Imposible
               (recibes todo)                (pides lo que quieres)

Under-fetch:   Común                         Imposible
               (múltiples requests)          (todo en 1 query)

Caching:       Simple                        Complejo
               (URL-based, CDN)              (no hay URLs únicas)

Versionado:    /api/v1/ → /api/v2/           Evolución del schema
               (breaking changes)            (agregar campos, deprecar)

Debugging:     curl + browser                Herramientas especiales
               (muy fácil)                   (GraphiQL, Apollo Studio)

Errores:       Status codes HTTP             Siempre 200, errores en body
               (404, 500, etc.)              {"errors": [...]}
```

---

## Caso de uso: dashboard de administración de LLMs

Este es el caso donde GraphQL brilla. Un dashboard de admin tiene múltiples pantallas, cada una necesitando datos diferentes de las mismas entidades:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ADMIN DASHBOARD                               │
│                                                                   │
│  Pantalla 1: Lista de modelos                                    │
│  ┌─────────────────────────────────────┐                        │
│  │ query { models { name, status } }   │  ← 2 campos           │
│  └─────────────────────────────────────┘                        │
│                                                                   │
│  Pantalla 2: Detalle de modelo                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │ query { model(id: "x") { name, version, parameters,  │      │
│  │   status, pricing { inputPerToken, outputPerToken },  │      │
│  │   contextWindow } }                                    │      │
│  │                                              ← 8 campos      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  Pantalla 3: Monitoreo de uso                                    │
│  ┌───────────────────────────────────────────────────────┐      │
│  │ query { models { name, usage(period: "2026-03") {     │      │
│  │   totalRequests, totalTokens, avgLatencyMs } } }      │      │
│  │                                              ← 4 campos      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  Pantalla 4: Vista móvil (ancho de banda limitado)               │
│  ┌─────────────────────────────────────┐                        │
│  │ query { models { name, status } }   │  ← solo 2 campos      │
│  └─────────────────────────────────────┘  (ahorra datos)        │
│                                                                   │
│  Con REST necesitarías:                                          │
│  - 4 endpoints diferentes, o                                     │
│  - 1 endpoint que retorna TODO (over-fetch en pantallas 1,4), o │
│  - Query params: GET /models?fields=name,status (no estándar)   │
│                                                                   │
│  Con GraphQL: 1 endpoint, 4 queries distintas. Cada pantalla    │
│  pide exactamente lo que necesita.                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Limitaciones de GraphQL (seamos honestos)

GraphQL no es la solución universal. Tiene problemas reales:

### 1. El problema N+1

```
query {
  models {          ← 1 query a la tabla "models" (retorna 50 modelos)
    name
    usage {         ← 50 queries a la tabla "usage" (una por modelo)
      totalRequests
    }
  }
}

Sin optimización:
  SELECT * FROM models;                          -- 1 query
  SELECT * FROM usage WHERE model_id = 1;        -- +1
  SELECT * FROM usage WHERE model_id = 2;        -- +1
  ...                                            -- ...
  SELECT * FROM usage WHERE model_id = 50;       -- +1
                                                 ──────
                                                 51 queries!

Con DataLoader (batching):
  SELECT * FROM models;                          -- 1 query
  SELECT * FROM usage WHERE model_id IN (1..50); -- 1 query
                                                 ──────
                                                 2 queries
```

El problema N+1 no es exclusivo de GraphQL, pero la flexibilidad de las queries lo hace más probable. Solución: **DataLoader** (batching + caching).

### 2. Caching difícil

```
REST:    GET /models/claude-3  →  la URL es la cache key
         CDN puede cachear por URL
         Browser cache funciona automáticamente

GraphQL: POST /graphql         →  todas las queries van al mismo URL
         Body tiene la query   →  no puedes cachear por URL
         Necesitas cache a nivel de campo (Apollo, Relay)
         CDN no ayuda directamente
```

### 3. Seguridad: queries maliciosas

Un cliente malicioso puede escribir queries profundamente anidadas:

```graphql
# Query "bomba" — recursión profunda
query {
  models {
    relatedModels {
      relatedModels {
        relatedModels {
          relatedModels {
            # ... 20 niveles de profundidad
            # El servidor intenta resolver TODO
            # = Denial of Service
          }
        }
      }
    }
  }
}
```

Defensas necesarias:
- **Depth limiting**: rechazar queries con profundidad > N
- **Cost analysis**: asignar "peso" a cada campo, rechazar queries que excedan un presupuesto
- **Timeout**: cortar queries que tarden más de X segundos

### 4. Complejidad para casos simples

```
CRUD simple (5 endpoints):
  REST:    5 rutas, sin schema adicional, curl para probar
  GraphQL: schema + resolvers + servidor GraphQL + cliente especial

Para un microservicio con 3 endpoints, GraphQL agrega complejidad
sin beneficio real.
```

---

## Cuándo NO usar GraphQL

```
¿Qué tipo de API estás construyendo?
│
├── CRUD simple con pocos endpoints
│   └──▶ REST (más simple, menos infraestructura)
│
├── API pública para desarrolladores externos
│   └──▶ REST (más familiar, mejor documentación con OpenAPI)
│
├── Comunicación interna de alta frecuencia
│   └──▶ gRPC (más eficiente, archivo 07)
│
├── Dashboard con múltiples vistas de los mismos datos
│   └──▶ GraphQL (evita over/under-fetching)
│
├── Aplicación con clientes diversos (web, mobile, TV)
│   └──▶ GraphQL (cada cliente pide lo que necesita)
│
└── API donde los datos están muy relacionados (grafos)
    └──▶ GraphQL (navegación natural de relaciones)
```

## Conexión con la arquitectura del LLM

Regresa al diagrama maestro del archivo `00_index.md`. GraphQL corresponde a la **conexión ⑧**:

```
┌──────────────┐  ⑧ GraphQL             ┌──────────────┐
│ Admin        │ ◀═══════════════════▶  │  Analytics   │
│ Dashboard    │  (consultas flexibles) │  Service     │
└──────────────┘                        └──────────────┘
```

El dashboard de administración necesita datos de modelos, uso, facturación, y fine-tuning — todo en diferentes combinaciones según la pantalla. GraphQL permite que el frontend pida exactamente lo que cada vista necesita, sin que el backend tenga que crear endpoints especializados para cada pantalla.

En contraste:
- Las **conexiones ②④** (usuario ↔ API) usan REST porque son simples y predecibles
- La **conexión ⑤** (API ↔ GPUs) usa gRPC porque necesita velocidad
- La **conexión ⑧** (dashboard ↔ analytics) usa GraphQL porque necesita flexibilidad

Cada protocolo tiene su lugar.

---

> **Verifica en el notebook:** En `04_websockets.ipynb` hay una sección final donde se comparan queries GraphQL con requests REST equivalentes, mostrando la diferencia en bytes transferidos y número de round-trips.

---

:::exercise{title="Escribe queries GraphQL para un sistema universitario"}
Imagina que el ITAM tiene una API GraphQL para consultar información académica. Dado el siguiente schema:

```graphql
type Estudiante {
  matricula: ID!
  nombre: String!
  carrera: String!
  semestre: Int!
  promedio: Float!
  materias: [Inscripcion!]!
}

type Materia {
  clave: ID!
  nombre: String!
  creditos: Int!
  departamento: String!
  profesor: Profesor!
  horario: String!
  inscritos: [Inscripcion!]!
}

type Profesor {
  id: ID!
  nombre: String!
  departamento: String!
  materias: [Materia!]!
}

type Inscripcion {
  estudiante: Estudiante!
  materia: Materia!
  calificacion: Float
  periodo: String!
}

type Query {
  estudiante(matricula: ID!): Estudiante
  materia(clave: ID!): Materia
  materias(departamento: String): [Materia!]!
  profesores(departamento: String): [Profesor!]!
}
```

Escribe las queries GraphQL para:

- **a)** Obtener solo el nombre y promedio de un estudiante con matrícula "199122".
- **b)** Obtener todas las materias del departamento "Estadistica" con solo nombre, creditos, y el nombre del profesor.
- **c)** Obtener el nombre del estudiante "199122", junto con el nombre y calificación de cada materia en la que está inscrito.
- **d)** Explica: si quisieras hacer las consultas (a), (b) y (c) con REST, cuántos endpoints y requests necesitarías? Identifica dónde ocurre over-fetching y under-fetching.
- **e)** La query `{ materias { inscritos { estudiante { materias { inscritos { estudiante { nombre } } } } } } }` es peligrosa. Explica por qué y qué mecanismo de defensa usarías.
:::
