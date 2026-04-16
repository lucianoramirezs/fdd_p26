---
title: "Observabilidad y releases"
---

# Observabilidad y releases

Diseñar bien una API no evita todos los errores. También necesitas desplegar cambios de forma segura.

Aquí aparece una distinción crucial:

- **deployment**: poner código nuevo en infraestructura
- **release**: exponer ese comportamiento a usuarios reales

No son lo mismo.

---

## La analogía: abrir una nueva cocina por etapas

Imagina que el restaurante abre una cocina nueva.

No empiezas sirviendo a todo el comedor de golpe. Primero:

1. pruebas con pocas mesas
2. observas tiempos y errores
3. aumentas volumen si todo va bien

Eso es exactamente la lógica de un rollout seguro.

---

## Canary

Mandas un porcentaje pequeño del tráfico a la versión nueva.

```
v1 -> 90%
v2 -> 10%
```

Si:

- sube error rate
- sube p95
- bajan conversiones

detienes o reviertes.

---

## Blue-green

Mantienes dos entornos:

- blue = actual
- green = nueva versión

Cuando green está lista, cambias el tráfico.

Ventaja:

- rollback simple

Costo:

- más infraestructura

### ¿Cuándo elegir cada uno?

| Estrategia | Conviene cuando... | Tradeoff principal |
|---|---|---|
| `canary` | quieres exponer poco tráfico y observar gradualmente | rollback y lectura de métricas más complejos |
| `blue-green` | quieres corte limpio y rollback rápido | requiere más capacidad duplicada |

---

## Qué señales mirar

No todo dashboard sirve. Para una API, estas señales suelen importar:

- tasa de errores
- latencia p50 / p95 / p99
- throughput
- saturación
- timeouts
- retries
- códigos 4xx y 5xx

Si el contrato cambia, también importa:

- tasa de fallos de validación
- errores de parsing en consumers

---

## Logs, metrics, traces

Tres lentes distintos:

| Tipo | Te ayuda a ver |
|---|---|
| Logs | eventos concretos |
| Metrics | comportamiento agregado |
| Traces | recorrido de una request |

No compiten. Se complementan.

---

## Request IDs y correlación

Si una request entra por gateway, pasa por backend y toca otros servicios, necesitas correlación.

```
request_id = req_abc123
trace_id   = tr_987
```

Sin eso, un incidente se vuelve arqueología.

---

## Error budget

Un **SLO** (*service level objective*) dice qué nivel de confiabilidad quieres prometer, por ejemplo:

- 99.5% de requests exitosas en 30 días

El **error budget** es el margen de falla que te puedes "gastar" sin violar ese objetivo.

Ejemplo:

- SLO = 99.5%
- error budget = 0.5% de requests pueden fallar dentro de la ventana

¿Por qué importa en releases?

Porque si la versión nueva empieza a consumir demasiado de ese presupuesto:

- sube la tasa de errores
- se acelera el burn del error budget
- conviene frenar el rollout antes de dañar más usuarios

Definición corta:

> **Error budget = cuánta falta de confiabilidad puedes tolerar antes de violar tu objetivo de servicio.**

---

## Release seguro de contrato

Cuando el cambio toca la API externa:

1. despliegas la implementación nueva
2. activas en porcentaje pequeño
3. observas errores del consumer
4. comparas latencia y parsing
5. escalas o reviertes

La observabilidad deja de ser "nice to have" y se vuelve condición para evolucionar.

---

## Conexión con la arquitectura del LLM

Ejemplo:

- nueva versión de `POST /v1/chat` agrega `usage`
- despliegas backend nuevo
- canary al 10%
- observas:
  - ¿subió p95?
  - ¿hay más `500`?
  - ¿algún consumer falla parseando?

Si todo sigue sano, subes 10% -> 25% -> 50% -> 100%.

---

## Regla práctica

**No liberes un cambio de API que no puedas observar.**

Si no puedes medir:

- error rate
- latencia
- comportamiento de consumers

entonces no estás desplegando con confianza, estás apostando.

---

> **Verifica en el notebook:** Revisa `clase/19_diseno_api/code/04_gateway_y_release_signals.ipynb` para simular un canary rollout, comparar error rates y dibujar curvas de latencia.

---

:::exercise{title="Diseña un rollout seguro"}
Quieres liberar una nueva versión del endpoint `POST /v1/chat` que cambia internamente el router de modelos.

Propón:

1. estrategia de rollout (`canary`, `blue-green` u otra)
2. tres métricas obligatorias
3. una condición para avanzar
4. una condición para rollback

Después responde: ¿qué diferencia hay entre “el código desplegó bien” y “la release fue exitosa”?
:::
