---
title: "Diseño de APIs"
---

# Diseño de APIs

En la sección 18 aprendiste a **hablar** por APIs: HTTP, REST, SSE, WebSocket, gRPC, GraphQL, polling y webhooks. Ya sabes qué protocolos existen y cuándo usar cada uno.

Ahora viene la pregunta más difícil: **¿cómo diseñas una API para que sobreviva cambios, tráfico, errores y equipos distintos?**

En otras palabras: ya no basta con que la flecha funcione. Tiene que ser una flecha **durable**.

## La arquitectura completa del chatbot — ahora con diseño explícito

En la sección 18 abrimos las flechas. En esta sección las anotamos con sus presiones de diseño:

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│                     ARQUITECTURA DE UN CHATBOT LLM                                 │
│                     (ahora vista como superficie de contratos)                      │
│                                                                                    │
│  ┌──────────┐   ① WebSocket   ┌──────────┐   ② REST/SSE   ┌─────────────────────┐ │
│  │ Usuario  │◀══════════════▶ │ Frontend │ ─────────────▶ │ API del chatbot      │ │
│  │ browser  │  tiempo real    │ React    │ contrato JSON  │                     │ │
│  └──────────┘                 └──────────┘                │ - OpenAPI            │ │
│                                                           │ - versionado         │ │
│                                                           │ - tests de contrato  │ │
│                                                           └─────────┬───────────┘ │
│                                                                     │             │
│                                      ③ REST + SSE hacia LLM         │             │
│                                      ④ gateway en el borde          │             │
│                                      ⑤ métricas y releases          │             │
│                                                                     ▼             │
│                                                           ┌─────────────────────┐ │
│                                                           │ Gateway / borde      │ │
│                                                           │ auth, rate limit,    │ │
│                                                           │ logs, tracing        │ │
│                                                           └─────────┬───────────┘ │
│                                                                     │             │
│                                                            ⑥ gRPC   │             │
│                                                            interno   ▼             │
│                                                           ┌─────────────────────┐ │
│                                                           │ Model server /       │ │
│                                                           │ servicios internos   │ │
│                                                           └─────────────────────┘ │
│                                                                                    │
│  Preguntas nuevas:                                                                  │
│  - ¿Quién es dueño de cada contrato?                                                │
│  - ¿Qué cambios rompen clientes y cuáles no?                                        │
│  - ¿Cómo verificas que el contrato siga vivo?                                       │
│  - ¿Qué controles van en el borde y cuáles dentro del servicio?                     │
└────────────────────────────────────────────────────────────────────────────────────┘
```

## Progresión del módulo

Cada archivo introduce una nueva presión de diseño en la arquitectura del chatbot:

| Archivo | Presión principal | Pregunta que responde |
|---------|-------------------|-----------------------|
| `01_por_que_disenar_apis` | Contrato y ownership | ¿Por qué una API bien diseñada importa más que “solo funcione”? |
| `02_openapi_y_contratos` | Especificación | ¿Cómo haces explícito el contrato para humanos y máquinas? |
| `03_modelado_de_requests_y_responses` | Forma del intercambio | ¿Qué shape hace a una API durable y fácil de consumir? |
| `04_versionado_y_evolucion` | Cambio | ¿Cómo evolucionas sin romper clientes? |
| `05_pruebas_de_apis` | Verificación | ¿Qué pruebas protegen el contrato? |
| `06_gateway_y_borde` | Tráfico externo | ¿Qué responsabilidades van en el edge? |
| `07_observabilidad_y_releases` | Operación | ¿Cómo liberas cambios sin miedo? |
| `08_seguridad_y_amenazas` | Riesgo | ¿Qué puede salir mal y cómo lo limitas? |
| `09_sintesis_y_arbol_de_decision` | Síntesis | ¿Cómo combinas contrato, pruebas, borde y releases en un sistema real? |

## Contenido

| Archivo | Tema | Notebook | Tiempo est. |
|---------|------|----------|-------------|
| [Por qué diseñar APIs](./01_por_que_disenar_apis.md) | API-first, contrato, producer/consumer, north-south vs east-west | -- | ~15 min |
| [OpenAPI y contratos](./02_openapi_y_contratos.md) | OpenAPI, schemas, ejemplos, validación, codegen mental | [01_openapi_y_validacion](./code/01_openapi_y_validacion.ipynb) | ~20 min + ~30 min |
| [Modelado de requests y responses](./03_modelado_de_requests_y_responses.md) | resources vs RPC, paginación, errores, idempotencia, envelopes | [02_modelado_y_versionado](./code/02_modelado_y_versionado.ipynb) | ~20 min + ~30 min |
| [Versionado y evolución](./04_versionado_y_evolucion.md) | cambios breaking, compatibilidad, deprecación, APIs como seams | [02_modelado_y_versionado](./code/02_modelado_y_versionado.ipynb) | ~20 min + ~20 min |
| [Pruebas de APIs](./05_pruebas_de_apis.md) | contract, component, integration y E2E | [03_contract_testing](./code/03_contract_testing.ipynb) | ~20 min + ~30 min |
| [Gateway y borde](./06_gateway_y_borde.md) | proxy vs load balancer vs gateway, rate limiting, auth handoff | [04_gateway_y_release_signals](./code/04_gateway_y_release_signals.ipynb) | ~18 min + ~25 min |
| [Observabilidad y releases](./07_observabilidad_y_releases.md) | deployment vs release, canary, blue-green, métricas | [04_gateway_y_release_signals](./code/04_gateway_y_release_signals.ipynb) | ~18 min + ~25 min |
| [Seguridad y amenazas](./08_seguridad_y_amenazas.md) | threat modeling, OWASP API risks, auth/authz overview | -- | ~18 min |
| [Síntesis y árbol de decisión](./09_sintesis_y_arbol_de_decision.md) | framework final, gráficos y decisiones de diseño | [05_benchmarks_y_graficas](./code/05_benchmarks_y_graficas.ipynb) | ~15 min + ~20 min |

## Notebooks

| Notebook | Tema | Tiempo est. |
|----------|------|-------------|
| [01 -- OpenAPI y validación](./code/01_openapi_y_validacion.ipynb) | Construir un contrato OpenAPI pequeño y validar payloads | ~30 min |
| [02 -- Modelado y versionado](./code/02_modelado_y_versionado.ipynb) | Comparar diseños buenos/malos y detectar cambios breaking | ~30 min |
| [03 -- Contract testing](./code/03_contract_testing.ipynb) | Verificar respuestas contra contrato y aislar capas de prueba | ~30 min |
| [04 -- Gateway y release signals](./code/04_gateway_y_release_signals.ipynb) | Simular rate limiting, canary, error rate y p95 | ~25 min |
| [05 -- Benchmarks y gráficas](./code/05_benchmarks_y_graficas.ipynb) | Reproducir las gráficas de síntesis del módulo | ~20 min |

[![Open NB01 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/19_diseno_api/code/01_openapi_y_validacion.ipynb)
[![Open NB02 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/19_diseno_api/code/02_modelado_y_versionado.ipynb)
[![Open NB03 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/19_diseno_api/code/03_contract_testing.ipynb)
[![Open NB04 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/19_diseno_api/code/04_gateway_y_release_signals.ipynb)
[![Open NB05 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/19_diseno_api/code/05_benchmarks_y_graficas.ipynb)

## Qué cambia respecto a la sección 18

En la sección 18 la pregunta era:

> “¿Qué protocolo conviene para esta flecha?”

En la sección 19 la pregunta es:

> “Ya elegiste una flecha. ¿Cómo haces para que siga funcionando dentro de seis meses, con más clientes, más tráfico y más cambios?”

## Prerrequisitos

- Haber completado `18_intro_a_apis`
- Saber leer JSON y requests HTTP
- Python 3.10+
- `pyyaml`, `jsonschema`, `matplotlib`, `numpy` instalados

```bash
pip install pyyaml jsonschema matplotlib numpy
```
