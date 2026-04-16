---
title: "OpenAPI y contratos"
---

# OpenAPI y contratos

Si la API es el menú del restaurante, OpenAPI es la versión **formal, verificable y compartible** de ese menú.

## Definición puntual

**OpenAPI** es una **especificación estándar** para describir una API HTTP de forma estructurada y legible por máquinas.

En concreto, OpenAPI permite declarar:

- qué rutas existen
- qué métodos HTTP soporta cada ruta
- qué parámetros y bodies acepta
- qué responses puede devolver
- qué schemas tienen esos datos

Normalmente se escribe en **YAML** o **JSON**, y funciona como un contrato que pueden usar:

- personas, para leer la API
- herramientas, para validarla
- clientes y servidores, para generar código o documentación

Definición corta para recordar:

> **OpenAPI = el formato estándar para escribir el contrato de una API HTTP.**

---

## Dos definiciones más que necesitas

### ¿Qué es un schema?

Un **schema** es una descripción formal de la forma permitida de unos datos.

Por ejemplo, un schema puede decir:

- este campo existe
- este campo es obligatorio
- este valor debe ser `string`
- este número debe estar entre ciertos límites

Si OpenAPI describe la API completa, el schema describe la **forma de cada pieza de datos** dentro de esa API.

### ¿Qué relación tiene con JSON Schema?

Cuando OpenAPI describe request y response bodies, lo hace con schemas **basados en JSON Schema**.

Eso importa porque explica por qué herramientas como `jsonschema` sirven para validar payloads del contrato en el notebook y en CI.

Definición corta:

> **OpenAPI describe endpoints; los schemas describen los datos que viajan por esos endpoints.**

---

No solo le dice a una persona qué pedir. También le dice a máquinas:

- qué endpoints existen
- qué parámetros esperan
- qué shape tiene cada request
- qué shape tiene cada response
- qué errores pueden ocurrir

---

## La analogía: menú legible por humanos y por robots

Un menú normal sirve para humanos. Un contrato OpenAPI sirve para:

- frontend
- backend
- tests
- validadores
- documentación
- herramientas de codegen

```
                 CONTRATO OPENAPI

    humano lo lee        maquina lo valida
          │                     │
          ▼                     ▼
   "POST /v1/chat"       schema request/response
   "body requerido"      required / optional
   "200 devuelve..."     tipos, enums, examples
   "429 posible"         validacion automatica
```

---

## Qué resuelve OpenAPI

### 1. Ambigüedad

Sin contrato:

- frontend asume que `max_tokens` es opcional
- backend asume que es obligatorio

Con contrato:

- ambos lo ven explícito

### 2. Drift

Sin contrato:

- el código cambia
- la documentación se queda vieja

Con contrato:

- el contrato se vuelve un artefacto central

### 3. Validación

Puedes revisar si un payload cumple el contrato antes de desplegar.

---

## Ejemplo mínimo

```yaml
openapi: 3.1.0
info:
  title: Chatbot API
  version: 1.0.0
paths:
  /v1/chat:
    post:
      summary: Crear una respuesta del chatbot
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatRequest'
      responses:
        '200':
          description: Respuesta generada correctamente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'
components:
  schemas:
    ChatRequest:
      type: object
      required: [model, messages]
      properties:
        model:
          type: string
        messages:
          type: array
    ChatResponse:
      type: object
      required: [id, output_text]
      properties:
        id:
          type: string
        output_text:
          type: string
```

Ese YAML ya contiene más verdad operativa que muchas wikis enteras.

---

## Schema, example y validation no son lo mismo

Tres piezas suelen mezclarse, pero cumplen roles diferentes:

| Pieza | Para qué sirve |
|---|---|
| `schema` | Define la forma permitida |
| `example` | Enseña un caso concreto |
| `validation` | Revisa si una instancia cumple el schema |

### Error común

Poner un ejemplo bonito y asumir que ya existe contrato.

No. Un ejemplo ayuda al humano. El schema protege al sistema.

---

## Qué partes debe cubrir un buen contrato

Para cada endpoint importante, el contrato debe responder:

1. ¿Qué operación existe?
2. ¿Qué parámetros acepta?
3. ¿Qué body espera?
4. ¿Qué devuelve si sale bien?
5. ¿Qué errores devuelve si sale mal?
6. ¿Qué campos son obligatorios y cuáles opcionales?
7. ¿Qué enums, formatos y restricciones existen?

```
Contrato incompleto = bugs desplazados al runtime
Contrato explícito  = errores detectados antes
```

---

## Ejemplos y errores

Una buena API no solo documenta el `200 OK`.

También necesita hacer explícitos:

- `400` input inválido
- `401` no autenticado
- `403` autenticado pero sin permisos
- `404` recurso inexistente
- `429` rate limit
- `500` error inesperado

Ejemplo de envelope:

```json
{
  "error": {
    "type": "validation_error",
    "message": "messages debe contener al menos un elemento",
    "field": "messages"
  }
}
```

---

## OpenAPI no reemplaza diseño

OpenAPI ayuda muchísimo, pero no decide por ti:

- si conviene modelar recursos o RPC
- cómo versionar
- qué tan granular debe ser una operación
- qué garantías de compatibilidad das

Piensa así:

```
Buen diseño + OpenAPI = contrato fuerte
Mal diseño + OpenAPI  = mal diseño bien documentado
```

---

## Codegen: la promesa y el límite

Del contrato pueden salir:

- clientes
- stubs
- documentación navegable
- validadores

`codegen` significa precisamente eso: **generación automática de código** a partir del contrato.

Eso ahorra tiempo, pero no elimina criterio arquitectónico. Si el contrato está mal pensado, el codegen solo acelera el problema.

---

## Conexión con la arquitectura del LLM

Imagina que el frontend del chatbot depende de:

- `POST /v1/chat`
- `GET /v1/conversations/{id}`
- `GET /v1/usage`

Si esos contratos están en OpenAPI:

- frontend puede alinear expectativas
- backend puede validar respuestas
- tests pueden detectar drift
- futuros consumers, como un dashboard, arrancan más rápido

---

> **Verifica en el notebook:** Revisa `clase/19_diseno_api/code/01_openapi_y_validacion.ipynb` para construir un contrato pequeño, cargarlo en Python y validar payloads correctos e incorrectos.

---

:::exercise{title="Diseña el contrato mínimo del chatbot"}
Especifica, en OpenAPI o pseudoyaml, el endpoint `POST /v1/chat`.

Incluye:

1. Campos obligatorios del request
2. Un campo opcional
3. La respuesta `200`
4. Al menos dos errores posibles
5. Un ejemplo de payload válido y uno inválido

Después responde: ¿qué ambigüedades te obligó a resolver el simple hecho de escribir el contrato?
:::
