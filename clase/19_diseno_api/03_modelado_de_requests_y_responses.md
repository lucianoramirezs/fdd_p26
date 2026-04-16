---
title: "Modelado de requests y responses"
---

# Modelado de requests y responses

Una API durable no se rompe solo por cambiar endpoints. Muchas veces se rompe por decisiones pequeñas en el **shape** del request o de la response.

Diseñar una API es modelar intercambios:

- qué entra
- qué sale
- qué errores viven al costado
- qué partes pueden crecer sin romper consumidores

---

## La analogía: la comanda bien escrita

Una comanda mala en un restaurante genera caos:

- platillos ambiguos
- cantidades poco claras
- notas perdidas
- errores imposibles de rastrear

Una comanda buena separa campos:

```
mesa: 7
platillo: tacos_al_pastor
cantidad: 2
sin_cebolla: true
bebida: agua
```

Eso mismo buscamos en un request.

---

## Resources vs RPC

Dos estilos comunes:

### Resource-oriented

```http
GET /v1/conversations/42
POST /v1/conversations
GET /v1/fine-tuning/jobs/abc
```

Ventaja:

- se lee como modelo de dominio
- se integra bien con HTTP

### RPC-style

```http
POST /v1/chat:generate
POST /v1/model:embed
POST /v1/fine-tuning:start
```

Ventaja:

- más natural cuando la operación es acción pura

Regla práctica:

- si modelas entidades estables, piensa en recursos
- si modelas una operación computacional fuerte, RPC puede ser más claro

### El costo de mezclar sin criterio

Mezclar recursos y RPC no es un pecado. El problema es mezclar **sin convención**.

Ejemplo confuso:

```http
GET  /v1/conversations/42
POST /v1/sendMessage
POST /v1/jobs/startFineTune
GET  /v1/getUsage
```

Aquí el consumer tiene que aprender cuatro estilos distintos a la vez.

Regla práctica:

- puedes usar un diseño híbrido
- pero cada familia de endpoints debe seguir una lógica clara
- la inconsistencia cuesta más a medida que crecen los consumers

---

## Paginación

Colecciones grandes necesitan frontera.

Malo:

```http
GET /v1/logs
```

Respuesta:

- 100,000 elementos
- lenta
- cara
- difícil de consumir

Mejor:

```http
GET /v1/logs?limit=50&cursor=abc123
```

Response:

```json
{
  "data": [...],
  "next_cursor": "def456"
}
```

### Offset vs cursor

| Estrategia | Ventaja | Riesgo |
|---|---|---|
| `offset` | simple de entender | inestable cuando cambian los datos |
| `cursor` | más estable para feeds grandes | menos intuitivo para humanos |

### Por qué `offset` puede salir mal

Imagina este flujo:

1. pides `GET /logs?offset=0&limit=3`
2. recibes `[A, B, C]`
3. entra un log nuevo al inicio de la colección
4. pides `GET /logs?offset=3&limit=3`

Ahora podrías:

- repetir un elemento
- saltarte uno

Con cursor, en cambio, la página siguiente se ancla a una posición lógica del feed, no a un número absoluto fácilmente desplazable.

---

## Filtering y sorting

Los filtros deben ser predecibles y composables.

```http
GET /v1/fine-tuning/jobs?status=running&sort=-created_at
```

Reglas sanas:

- usa nombres explícitos
- evita semánticas mágicas
- documenta enums válidos

---

## Error envelopes

Si cada endpoint falla con un shape distinto, el consumer vive en caos.

Mejor:

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Demasiadas peticiones por minuto",
    "retry_after_seconds": 30
  }
}
```

Eso permite:

- UI consistente
- logging consistente
- retries mejor informados

---

## Idempotencia

Hay operaciones que deben poder repetirse sin crear efectos dobles.

Ejemplo clásico:

```http
POST /v1/payments
Idempotency-Key: 8f4e...
```

En un sistema LLM, un caso parecido podría ser:

- crear un job de fine-tuning
- registrar una compra de créditos

Si el cliente reintenta por timeout, no quieres dos jobs ni dos cobros.

### Qué pasa si la ignoras

Sin idempotencia, un simple retry automático puede producir:

- dos entrenamientos idénticos
- dos compras de créditos
- dos correos o notificaciones

El bug no viene de "hacer dos clicks". Viene de no diseñar la operación para un mundo con retries, timeouts y redes imperfectas.

---

## Forma durable de una response

Malo:

```json
{
  "text": "Hola"
}
```

Tal vez hoy basta. Pero mañana quizá quieras:

- metadata
- usage
- finish reason
- trace id

Más durable:

```json
{
  "id": "msg_001",
  "output_text": "Hola",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 12
  },
  "meta": {
    "model": "chat-mini",
    "trace_id": "tr_123"
  }
}
```

La idea no es inflar responses. Es dejar espacio para crecer con coherencia.

---

## Additive vs breaking

Al modelar shapes, piensa desde el inicio qué cambios suelen ser seguros:

### Normalmente aditivo

- agregar campo opcional
- agregar nuevo status code documentado
- agregar valor de enum si el consumer lo tolera

### Normalmente breaking

- renombrar campo
- cambiar tipo
- quitar campo usado
- cambiar semántica silenciosamente

### La condición que hace seguro lo aditivo

Decir que "agregar un campo opcional no rompe" solo es razonable si el consumer está diseñado como **tolerant reader**:

- lee lo que conoce
- ignora campos desconocidos

Si el consumer valida de forma rígida o asume que la response tiene exactamente N campos, incluso un cambio aditivo puede romperlo.

```
Producer sano: puede agregar sin borrar
Consumer sano: tolera campos nuevos
```

Esa combinación es la base práctica de mucha compatibilidad hacia adelante.

---

## Conexión con la arquitectura del LLM

Para el chatbot, estos objetos suelen merecer diseño cuidadoso:

- `ChatRequest`
- `ChatResponse`
- `Conversation`
- `FineTuningJob`
- `ApiError`

Si esos shapes están bien modelados, los consumers cambian menos y los tests detectan mejor cualquier drift.

---

> **Verifica en el notebook:** Revisa `clase/19_diseno_api/code/02_modelado_y_versionado.ipynb` para comparar responses frágiles vs durables, y ver qué cambios son aditivos y cuáles rompen clientes.

---

:::exercise{title="Rediseña una response frágil"}
Supón que hoy tu backend devuelve:

```json
{
  "reply": "Hola",
  "tokens": 22
}
```

Diseña una versión más durable que permita crecer hacia:

1. múltiples outputs
2. metadata del modelo
3. errores consistentes
4. trazabilidad

Explica qué parte de tu rediseño busca claridad humana y qué parte busca compatibilidad futura.
:::
