---
title: "Introducción a APIs"
---

# Introducción a APIs

En la sección 16 construiste el chatbot internamente. Entendiste procesos, hilos, el GIL, modelos secuenciales, concurrentes y paralelos. Tu cocina funciona. Pero falta algo fundamental: **¿cómo habla el mundo exterior con tu chatbot? ¿Y cómo habla tu chatbot con el LLM?**

La respuesta es APIs. Cada flecha en la arquitectura del chatbot — desde el usuario que escribe un mensaje hasta el servidor que consulta al LLM — es una llamada a una API usando algún protocolo. Este módulo descompone esas flechas: qué protocolos existen, cuándo usar cada uno, y cómo se conectan en un sistema real.

## La arquitectura completa del chatbot — con APIs explícitas

En la sección 16 tratamos las flechas como cajas negras. Ahora las abrimos:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA DE UN CHATBOT LLM                          │
│                    (cada flecha es una API)                                 │
│                                                                             │
│  ┌──────────┐  ① WebSocket    ┌──────────┐  ② REST      ┌──────────────┐  │
│  │          │ ◀═══════════▶   │          │ ────────────▶ │              │  │
│  │ Usuario  │  (chat en       │ Frontend │  ③ SSE       │  API Server  │  │
│  │ (browser)│   tiempo real)  │ (React)  │ ◀╌╌╌╌╌╌╌╌╌╌ │  (Python)    │  │
│  └──────────┘                 └──────────┘  (streaming)  └──────┬───────┘  │
│                                                                  │          │
│                                              ④ REST + SSE       │          │
│                                              ┌──────────────────┘          │
│                                              ▼                              │
│                                      ┌───────────────┐                     │
│                                      │   LLM API     │                     │
│                                      │ (Anthropic,   │                     │
│                                      │  OpenAI)      │                     │
│                                      └───────┬───────┘                     │
│                                              │                              │
│                                    ⑤ gRPC    │                              │
│                                    (interno) │                              │
│                                              ▼                              │
│                                      ┌───────────────┐                     │
│                                      │  GPU Cluster  │                     │
│                                      │  (inferencia) │                     │
│                                      └───────────────┘                     │
│                                                                             │
│  ┌──────────────┐  ⑥ REST (start job)    ┌──────────────┐                  │
│  │ Fine-tuning  │ ──────────────────────▶│              │                  │
│  │ pipeline     │  ⑦ Webhook (notify)    │  Training    │                  │
│  │              │ ◀╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌│  Service     │                  │
│  └──────────────┘                        └──────────────┘                  │
│                                                                             │
│  ┌──────────────┐  ⑧ GraphQL             ┌──────────────┐                  │
│  │ Admin        │ ◀═══════════════════▶  │  Analytics   │                  │
│  │ Dashboard    │  (consultas flexibles) │  Service     │                  │
│  └──────────────┘                        └──────────────┘                  │
│                                                                             │
│  ┌──────────────┐  ⑨ SOAP/XML            ┌──────────────┐                  │
│  │ Enterprise   │ ◀═══════════════════▶  │  Legacy      │                  │
│  │ ERP (SAP)    │  (sistema heredado)    │  Gateway     │                  │
│  └──────────────┘                        └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Progresión del módulo

Cada archivo cubre un paradigma diferente, motivado por una conexión real en la arquitectura del LLM:

| Archivo | Paradigma | Conexión en el LLM | Pregunta que responde |
|---------|-----------|--------------------|-----------------------|
| `01_que_es_una_api` | Concepto general | Todas las flechas | ¿Qué es una API y por qué existen? |
| `02_http_fundamentos` | HTTP | ② ④ ⑥ | ¿Cómo se estructura una petición/respuesta? |
| `03_rest` | REST | ② ④ | ¿Cómo organizar endpoints para el chatbot? |
| `04_streaming_y_sse` | SSE / Streaming | ③ | ¿Por qué el LLM responde token por token? |
| `05_websockets` | WebSocket | ① | ¿Cómo mantener chat en tiempo real? |

## Contenido

| Archivo | Tema | Notebook | Tiempo est. |
|---------|------|----------|-------------|
| [Qué es una API](./01_que_es_una_api.md) | Definición, historia, taxonomía, analogía restaurante | -- | ~15 min |
| [HTTP fundamentos](./02_http_fundamentos.md) | Protocolo HTTP, métodos, status codes, headers, latencia | [01_http_y_rest](./code/01_http_y_rest.ipynb) | ~20 min + ~30 min |
| [REST](./03_rest.md) | Arquitectura REST, endpoints, JSON, diseño de APIs | [02_rest_practica](./code/02_rest_practica.ipynb) | ~20 min + ~35 min |
| [Streaming y SSE](./04_streaming_y_sse.md) | Server-Sent Events, streaming de tokens LLM | [03_streaming_sse](./code/03_streaming_sse.ipynb) | ~15 min + ~30 min |
| [WebSockets](./05_websockets.md) | Protocolo WebSocket, chat bidireccional | [04_websockets](./code/04_websockets.ipynb) | ~15 min + ~25 min |

## Notebooks

| Notebook | Tema | Tiempo est. |
|----------|------|-------------|
| [01 -- HTTP y REST](./code/01_http_y_rest.ipynb) | Peticiones HTTP con `requests`, exploración de APIs reales | ~30 min |
| [02 -- REST practica](./code/02_rest_practica.ipynb) | Diseño y consumo de APIs REST, autenticación | ~35 min |
| [03 -- Streaming y SSE](./code/03_streaming_sse.ipynb) | Streaming de respuestas LLM token por token | ~30 min |
| [04 -- WebSockets](./code/04_websockets.ipynb) | Chat bidireccional con `websockets` | ~25 min |
| [05 -- Proyecto integrador](./code/05_proyecto_integrador.ipynb) | Cliente completo: REST + SSE + WebSocket | ~40 min |

[![Open NB01 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/18_intro_a_apis/code/01_http_y_rest.ipynb)
[![Open NB02 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/18_intro_a_apis/code/02_rest_practica.ipynb)
[![Open NB03 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/18_intro_a_apis/code/03_streaming_sse.ipynb)
[![Open NB04 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/18_intro_a_apis/code/04_websockets.ipynb)
[![Open NB05 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/fdd_p26/blob/main/clase/18_intro_a_apis/code/05_proyecto_integrador.ipynb)

## Prerrequisitos

- Secciones 15-16: modelos de ejecución completados (especialmente asyncio)
- Python 3.10+
- `requests`, `websockets`, `httpx` instalados

```bash
pip install requests websockets httpx
```
