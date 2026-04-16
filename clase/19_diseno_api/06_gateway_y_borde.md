---
title: "Gateway y borde"
---

# Gateway y borde

Hasta ahora hablamos del contrato del servicio. Pero una API pública no vive sola. Antes de tocar tu backend, el tráfico suele pasar por una frontera: el **borde**.

Ahí aparecen preguntas nuevas:

- ¿quién entra?
- ¿cuánto puede pedir?
- ¿a qué servicio se enruta?
- ¿qué observabilidad capturamos?

---

## La analogía: la recepción del edificio

El backend del chatbot es como una oficina dentro de un edificio.

La recepción del edificio no hace el trabajo de la oficina, pero sí controla:

- identidad
- acceso
- flujo
- registro de entradas

```
Usuario externo
     │
     ▼
┌───────────────┐
│   RECEPCION   │  = gateway / edge
│ - identifica  │
│ - filtra       │
│ - limita       │
│ - enruta       │
└───────┬───────┘
        ▼
   API del chatbot
```

---

## Proxy, load balancer y gateway

No son lo mismo.

| Componente | Rol principal |
|---|---|
| Proxy | reenviar tráfico |
| Load balancer | repartir tráfico entre instancias |
| API gateway | enrutar y además aplicar políticas de API |

En muchas arquitecturas reales, un gateway también hace parte del trabajo de proxy y balanceo, pero su valor adicional está en las **políticas**.

### Tradeoff real

| Opción | Cuándo basta | Qué problema crea si se te queda corta |
|---|---|---|
| Proxy | una o pocas rutas simples | no resuelve auth, rate limiting ni gobernanza |
| Load balancer | distribuir tráfico entre instancias | balancea, pero no te da semántica de API |
| API gateway | varias APIs públicas con políticas comunes | puede sobrecomplicar si tu caso aún es muy pequeño |

Regla práctica:

- usa la solución más simple que cubra tus necesidades reales
- pero no ignores señales de que ya necesitas políticas de API en un lugar central

---

## Qué suele vivir en el borde

- autenticación inicial
- rate limiting
- routing por path o host
- logging y tracing
- terminación TLS
- respuestas uniformes para ciertos errores

### Lo que no conviene meter indiscriminadamente

- lógica de negocio profunda
- transformaciones monstruosas
- acoplamiento excesivo con cada backend

Cuando el gateway intenta convertirse en "el cerebro del sistema", empiezan los problemas.

---

## Rate limiting

Una API del chatbot puede ser cara:

- tokens
- inferencia
- GPU

Entonces el borde protege contra abuso:

```http
429 Too Many Requests
Retry-After: 30
```

Eso no reemplaza la lógica interna del servicio, pero baja presión y hace el sistema operable.

---

## Routing

Ejemplos de routing en el edge:

```text
/v1/chat        -> chatbot-service
/v1/usage       -> usage-service
/v1/admin/*     -> admin-service
api.curso.com   -> public-api
internal.curso  -> internal-tools
```

El gateway se vuelve el punto donde la superficie pública se organiza.

---

## Auth handoff

El gateway puede:

- verificar token
- rechazar peticiones inválidas
- pasar identidad ya validada al backend

Eso reduce trabajo repetido en cada servicio. Pero el backend aún debe tomar decisiones de autorización relevantes para su dominio.

Aquí solo estamos viendo la frontera operacional. En `08_seguridad_y_amenazas.md` retomamos esta distinción para mostrar por qué autenticación en el borde no resuelve por sí sola problemas como acceso indebido a objetos.

---

## Conexión con la arquitectura del LLM

En el chatbot, una separación sana podría verse así:

```
Gateway:
- TLS
- auth inicial
- rate limit
- request id
- logging de borde

Servicio:
- valida schema
- aplica reglas de negocio
- llama al modelo
- decide permisos de dominio
```

Ese reparto evita que el servicio quede ciego ante tráfico externo, pero también evita inflar el gateway con demasiada lógica.

---

## Error común: usar gateway para todo

Síntomas:

- reglas de negocio duplicadas en el borde
- transformaciones difíciles de mantener
- debugging opaco

Costo real:

- cada cambio de negocio toca infraestructura y servicio
- se vuelve difícil saber si el bug vive en el edge o en el backend
- el gateway empieza a parecer ESB disfrazado

Regla práctica:

**El gateway debe gobernar el tráfico. El servicio debe gobernar el dominio.**

---

> **Verifica en el notebook:** Revisa `clase/19_diseno_api/code/04_gateway_y_release_signals.ipynb` para simular routing, rate limiting y separación entre señales del borde y señales del servicio.

---

:::exercise{title="Separa responsabilidades entre gateway y servicio"}
Para una API pública de chatbot define qué pondrías en:

1. gateway
2. servicio backend

Considera:

- autenticación
- autorización
- rate limiting
- validación de payload
- logging
- retries
- selección de modelo

Justifica cada decisión en una frase.
:::
