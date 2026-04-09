---
title: "Polling y Webhooks"
---

# Polling y Webhooks

Hasta ahora todos los patrones que vimos son *sincrónicos* en espíritu: mandas una petición y recibes una respuesta (aunque sea en streaming). Pero hay procesos que tardan **minutos u horas** — entrenar un modelo, procesar un video, ejecutar un pipeline de datos. No puedes mantener una conexión abierta durante dos horas. Entonces, **cómo te enteras de que terminó?**

Dos estrategias fundamentales: **polling** (tú preguntas) y **webhooks** (te avisan).

## La analogía del restaurante

Imagina que pediste un platillo que tarda 30 minutos en prepararse.

**Polling** — tú preguntas repetidamente:

```
Tú:      "¿Ya está mi comida?"
Mesero:  "No."
         [2 minutos después]
Tú:      "¿Ya?"
Mesero:  "No."
         [2 minutos después]
Tú:      "¿Ya?"
Mesero:  "No."
         [2 minutos después]
Tú:      "¿Yaaaa?"
Mesero:  "...Sí. Aquí tiene."
```

Hiciste 15 preguntas. Solo 1 fue útil.

**Webhook** — dejas tu número y te avisan:

```
Tú:      "Cuando esté listo, llamen a este número: 555-1234"
Mesero:  "Perfecto."
         [30 minutos después]
*ring ring*
Mesero:  "Su orden está lista, puede pasar a recogerla."
```

Cero preguntas desperdiciadas. Una sola notificación.

---

## Short Polling

La forma más simple: un loop que hace GET cada N segundos.

```
Cliente                              Servidor
  │                                     │
  │──── GET /jobs/42/status ───────────▶│
  │◀─── 200 {"status": "pending"} ─────│
  │                                     │
  │  [espera 10 segundos]               │
  │                                     │
  │──── GET /jobs/42/status ───────────▶│
  │◀─── 200 {"status": "pending"} ─────│
  │                                     │
  │  [espera 10 segundos]               │
  │                                     │
  │──── GET /jobs/42/status ───────────▶│
  │◀─── 200 {"status": "pending"} ─────│
  │                                     │
  │  ... (repite 117 veces más) ...     │
  │                                     │
  │──── GET /jobs/42/status ───────────▶│
  │◀─── 200 {"status": "completed"} ───│
  │                                     │
```

**Problema**: la gran mayoría de las respuestas son `"pending"` — tráfico desperdiciado.

## Long Polling

Una mejora: el servidor **no responde inmediatamente** si no hay novedades. Mantiene la conexión abierta hasta que haya datos o expire un timeout.

```
Cliente                              Servidor
  │                                     │
  │──── GET /jobs/42/status ───────────▶│
  │          (el servidor espera...)     │
  │          (30 seg timeout...)         │
  │◀─── 200 {"status": "pending"} ─────│  ← timeout, no hubo cambio
  │                                     │
  │──── GET /jobs/42/status ───────────▶│
  │          (el servidor espera...)     │
  │          (15 seg después: listo!)    │
  │◀─── 200 {"status": "completed"} ───│  ← responde de inmediato
  │                                     │
```

Menos requests que short polling, pero sigue siendo el cliente quien inicia la conversación.

## El costo del polling

Si un proceso tarda $\Delta t$ segundos y haces polling cada $i$ segundos:

$$N_{requests} = \left\lceil \frac{\Delta t}{i} \right\rceil$$

Ejemplo: fine-tuning que tarda 2 horas (7200s), polling cada 60s:

$$N_{requests} = \left\lceil \frac{7200}{60} \right\rceil = 120 \text{ requests}$$

De esos 120 requests, **119 son inútiles**. Solo el último te dio información nueva.

---

## Ejemplo real: fine-tuning de un LLM

Este es el caso de uso perfecto para comparar ambos enfoques. El fine-tuning tarda horas — no puedes mantener una conexión abierta.

### Lado izquierdo: Polling

```
t=0min    POST /fine-tune {model, dataset}
          ◀── 201 {job_id: "ft-abc"}

t=1min    GET /fine-tune/ft-abc/status ──▶ {"status": "queued"}
t=2min    GET /fine-tune/ft-abc/status ──▶ {"status": "queued"}
t=3min    GET /fine-tune/ft-abc/status ──▶ {"status": "running", "epoch": 1}
t=4min    GET /fine-tune/ft-abc/status ──▶ {"status": "running", "epoch": 1}
  .                    .                            .
  .                    .                            .
  .                    .                            .
t=119min  GET /fine-tune/ft-abc/status ──▶ {"status": "running", "epoch": 9}
t=120min  GET /fine-tune/ft-abc/status ──▶ {"status": "completed"}

Total: 1 POST + 120 GETs = 121 requests
Requests útiles: 2 (el POST y el último GET)
Desperdicio: 98.3%
```

### Lado derecho: Webhook

```
t=0min    POST /fine-tune
          {
            "model": "llama-7b",
            "dataset": "mis-datos",
            "webhook_url": "https://mi-servidor.com/hooks/ft"
          }
          ◀── 201 {job_id: "ft-abc"}

          [silencio total durante 2 horas]
          [tu código puede hacer otras cosas]
          [o puedes cerrar la laptop]

t=120min  POST https://mi-servidor.com/hooks/ft   ◀── el SERVIDOR te llama a TI
          {
            "event": "fine_tune.completed",
            "job_id": "ft-abc",
            "model_id": "ft:llama-7b:abc123",
            "metrics": {"loss": 0.0234}
          }

Total: 1 POST + 1 POST callback = 2 requests
Requests útiles: 2
Desperdicio: 0%
```

### Comparación visual lado a lado

```
         POLLING                                 WEBHOOK
         ═══════                                 ═══════

t=0   ──▶ POST crear job                    ──▶ POST crear job (con webhook_url)
      ◀── 201 OK                            ◀── 201 OK
t=1   ──▶ GET status  ◀── "queued"                │
t=2   ──▶ GET status  ◀── "queued"                │
t=3   ──▶ GET status  ◀── "running"               │
t=4   ──▶ GET status  ◀── "running"               │ (silencio)
 .         .               .                      │
 .         .               .                      │ (tu código hace
 .         .               .                      │  otras cosas)
t=60  ──▶ GET status  ◀── "running"               │
 .         .               .                      │
 .         .               .                      │
t=119 ──▶ GET status  ◀── "running"               │
t=120 ──▶ GET status  ◀── "completed" ✓    ◀── POST callback "completed" ✓

Requests:  121                               Requests: 2
```

---

## Mecánica de un Webhook

Un webhook no es magia — es simplemente **el servidor haciendo un POST a una URL que tú le diste**. Inviertes los roles: ahora el servidor es el *cliente* de tu URL.

```
┌──────────────┐                           ┌──────────────┐
│              │   1. Registro              │              │
│   Tu App     │──────────────────────────▶│   Servicio   │
│              │   "avísame en esta URL"    │   (GitHub,   │
│              │                            │    Stripe,   │
│              │   2. Almacena URL          │    OpenAI)   │
│              │        ┌──────────────┐    │              │
│              │        │ webhook_url: │    │              │
│              │        │ https://...  │    │              │
│              │        └──────────────┘    │              │
│              │                            │              │
│              │         [pasa el tiempo]   │              │
│              │                            │              │
│              │   3. Evento ocurre         │              │
│              │◀──────────────────────────│              │
│              │   POST a tu URL con        │              │
│              │   payload del evento       │              │
│              │                            │              │
│              │   4. Confirma recepción    │              │
│              │──────────────────────────▶│              │
│              │   200 OK                   │              │
└──────────────┘                           └──────────────┘
```

El paso 4 es crucial: si no respondes 200, el servicio **reintentará** el webhook (generalmente con backoff exponencial). Si sigues sin responder, eventualmente te marca como *endpoint muerto*.

## Seguridad en Webhooks

Cualquiera puede hacer un POST a tu URL. Necesitas verificar que realmente viene del servicio esperado.

```
Servicio (GitHub, Stripe, etc.)              Tu servidor
  │                                             │
  │  1. Calcula HMAC-SHA256(payload, secret)    │
  │  2. Adjunta firma en header                 │
  │                                             │
  │──── POST /hooks/payments ──────────────────▶│
  │     Header: X-Signature: sha256=a1b2c3...   │
  │     Body: {"event": "payment.completed"}     │
  │                                             │
  │                    3. Recalcula HMAC con     │
  │                       tu copia del secret    │
  │                    4. Compara firmas          │
  │                       ¿Match? → procesa      │
  │                       ¿No? → rechaza (403)   │
  │                                             │
  │◀─── 200 OK ────────────────────────────────│
  │                                             │
```

Además de la firma, protege contra **replay attacks** verificando el timestamp del evento. Si el timestamp tiene más de 5 minutos de antigüedad, rechaza el request.

---

## Backoff exponencial para polling

Si *debes* usar polling (porque no puedes recibir webhooks), al menos no seas agresivo. El **backoff exponencial** incrementa el intervalo entre requests:

```
Intento   Intervalo   Tiempo total
  1         1s            1s
  2         2s            3s
  3         4s            7s
  4         8s           15s
  5        16s           31s
  6        32s           63s      ← ~1 minuto
  7        60s (cap)    123s      ← se aplica tope
  8        60s          183s
  .         .             .
```

Fórmula: $intervalo = \min(base \times 2^{intento}, cap)$

Con `base=1s` y `cap=60s`, después de 6 intentos ya estás en el tope. Mucho mejor que bombardear al servidor cada segundo durante dos horas.

### Pseudocódigo en Python

```python
import time
import requests

def poll_with_backoff(url, base=1, cap=60, max_attempts=200):
    for attempt in range(max_attempts):
        response = requests.get(url)
        data = response.json()

        if data["status"] == "completed":
            return data

        if data["status"] == "failed":
            raise Exception(f"Job falló: {data.get('error')}")

        wait = min(base * (2 ** attempt), cap)
        print(f"  Intento {attempt+1}: status={data['status']}, "
              f"esperando {wait}s...")
        time.sleep(wait)

    raise TimeoutError("Máximo de intentos alcanzado")
```

### Pseudocódigo del lado webhook

```python
from flask import Flask, request, abort
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "mi_secreto_compartido"

@app.route("/hooks/fine-tune", methods=["POST"])
def handle_webhook():
    # 1. Verificar firma
    signature = request.headers.get("X-Signature")
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, f"sha256={expected}"):
        abort(403)

    # 2. Procesar evento
    event = request.json
    if event["event"] == "fine_tune.completed":
        model_id = event["model_id"]
        print(f"Fine-tuning completado! Modelo: {model_id}")
        # Desplegar modelo, notificar equipo, etc.

    return "", 200
```

---

## Diagrama de decisión

Cuando necesitas saber cuándo terminó un proceso, elige tu estrategia:

```
¿Necesitas saber cuándo terminó algo?
│
├── ¿Puedes recibir HTTP? (tienes un servidor público)
│   │
│   ├── Sí ──────────────────────────▶ WEBHOOK
│   │                                   - Eficiente (0 requests desperdiciados)
│   │                                   - Requiere servidor público
│   │                                   - Requiere manejar seguridad
│   │
│   └── No (script local, notebook,
│       CI/CD, lambda sin URL pública)
│       │
│       └──────────────────────────▶ POLLING con backoff exponencial
│                                     - Simple de implementar
│                                     - No requiere servidor público
│                                     - Desperdicia requests (pero con
│                                       backoff es tolerable)
│
└── ¿Necesitas actualizaciones continuas (no solo "terminó")?
    │
    ├── Unidireccional (servidor → cliente)
    │   └──────────────────────────▶ SSE (archivos 04)
    │
    └── Bidireccional
        └──────────────────────────▶ WebSocket (archivo 05)
```

## Conexión con la arquitectura del LLM

Regresa al diagrama maestro del archivo `00_index.md`. Polling y webhooks corresponden a las **conexiones ⑥ y ⑦**:

```
┌──────────────┐  ⑥ REST (start job)    ┌──────────────┐
│ Fine-tuning  │ ──────────────────────▶│              │
│ pipeline     │  ⑦ Webhook (notify)    │  Training    │
│              │ ◀╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌│  Service     │
└──────────────┘                        └──────────────┘
```

- **⑥** es un POST REST normal para iniciar el job de fine-tuning
- **⑦** es el webhook de vuelta: el Training Service te avisa cuando terminó

Este patrón se repite en cualquier proceso asíncrono: procesamiento de video, generación de embeddings masivos, exports de datos, etc.

---

> **Verifica en el notebook:** En `05_proyecto_integrador.ipynb` puedes ver un ejemplo completo que combina polling con backoff exponencial para monitorear un job de procesamiento, y cómo registrar un webhook endpoint con Flask.

---

:::exercise{title="Diseña un sistema de notificaciones para un pipeline de datos"}
Tienes un pipeline de datos que:
1. Recibe un CSV con 10 millones de filas
2. Limpia los datos (~5 minutos)
3. Entrena un modelo (~30 minutos)
4. Genera predicciones (~10 minutos)
5. Exporta resultados a S3 (~2 minutos)

Diseña el sistema de notificación considerando:

- **a)** Dibuja un diagrama ASCII mostrando los componentes: el cliente que sube el CSV, el servidor del pipeline, y el mecanismo de notificación que elegiste (polling o webhook).
- **b)** Si el cliente es un notebook de Jupyter (no tiene URL pública), qué estrategia usarías? Implementa el pseudocódigo con backoff exponencial.
- **c)** Si el cliente es un microservicio en la nube (tiene URL pública), qué estrategia usarías? Diseña el payload del webhook para cada etapa (limpieza, entrenamiento, predicción, exportación).
- **d)** Calcula cuántos requests se desperdician si usas short polling cada 30 segundos vs backoff exponencial (base=2s, cap=120s) para los 47 minutos totales del pipeline.
:::
