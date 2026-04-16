---
title: "Por qué diseñar APIs"
---

# Por qué diseñar APIs

En la sección 18 vimos que una API es una interfaz entre sistemas. Pero en producción una API es algo más exigente: es un **contrato vivo** entre equipos, código, despliegues y tiempo.

Cuando un frontend, un pipeline de fine-tuning y un dashboard consumen la misma API del chatbot, ya no basta con que el endpoint "sirva". Tiene que ser **predecible**, **estable** y **evolucionable**.

---

## La analogía: el menú impreso

En la sección 18 el mesero era la API. Ahora agregamos algo nuevo: **el menú impreso**.

```
┌─────────────────────────────────────────────────────────────┐
│                  RESTAURANTE CON SUCURSALES                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Cliente A      Cliente B      Cliente C                    │
│     │              │              │                         │
│     ▼              ▼              ▼                         │
│  leen el mismo menú impreso:                                │
│                                                             │
│   - nombres consistentes                                   │
│   - precios claros                                         │
│   - combinaciones válidas                                  │
│   - reglas que no cambian cada noche                       │
│                                                             │
│  Si la cocina cambia algo sin actualizar el menú:          │
│   - el mesero promete algo que ya no existe                │
│   - los clientes se confunden                              │
│   - se rompe la operación                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

La API es el mesero. La **especificación** es el menú impreso. Diseñar APIs es decidir qué tan claro, durable y coherente será ese menú.

---

## Producer y consumer

Toda API tiene al menos dos lados:

- El **producer** expone operaciones y datos
- El **consumer** depende de que esos datos y operaciones sigan siendo ciertos

En el chatbot LLM:

| Consumer | Producer | Ejemplo |
|---|---|---|
| Frontend web | Backend del chatbot | `POST /v1/chat`, `GET /v1/conversations/{id}` |
| Backend del chatbot | API del LLM | `POST /v1/messages` |
| Dashboard interno | Servicio de usage | `GET /v1/usage` |

El diseño malo casi siempre nace de olvidar al consumer. Una API diseñada solo desde "lo que me conviene implementar hoy" envejece mal.

---

## API-first

**API-first** no significa "escribe YAML antes que código" por dogma. Significa algo más profundo:

1. Defines la superficie externa antes de amarrarte a la implementación
2. Piensas en consumidores concretos
3. Detectas ambigüedades antes de que se vuelvan bugs
4. Puedes discutir el contrato con producto, frontend y backend

```
Sin API-first:
implementacion -> endpoint improvisado -> cliente se adapta -> deuda

Con API-first:
problema -> contrato -> validacion con consumidores -> implementacion
```

---

## North-south vs east-west

No todas las APIs viven bajo la misma presión.

```
               INTERNET / CLIENTES
                      │
                      ▼
              north-south traffic
                      │
               API del chatbot
                / gateway edge
                      │
                      ▼
              east-west traffic
                      │
        model server / auth service / usage service
```

### North-south

Es el tráfico que entra desde afuera:

- navegadores
- apps móviles
- terceros

Presiones típicas:

- autenticación
- rate limiting
- versionado público
- backward compatibility fuerte

### East-west

Es el tráfico entre servicios internos.

Presiones típicas:

- latencia
- observabilidad
- retries
- compatibilidad entre equipos internos

La misma palabra "API" cubre ambos casos, pero no se diseñan exactamente igual.

---

## Qué hace durable a una API

Una API durable no es la más elegante en abstracto. Es la que reduce fricción cuando el sistema cambia.

Checklist mental:

- ¿Los nombres son consistentes?
- ¿Los errores tienen forma estable?
- ¿Se puede agregar información sin romper clientes?
- ¿Queda claro qué campos son obligatorios?
- ¿El contrato se puede validar automáticamente?
- ¿Está claro quién es dueño de esta interfaz?

---

## Conexión con la arquitectura del LLM

En la sección 18 mirábamos la flecha `frontend -> backend` y preguntábamos:

> “¿REST o WebSocket?”

Ahora la pregunta es distinta:

> “Si mañana agregamos un dashboard, una app móvil y un sistema de auditoría, ¿esta API sigue sirviendo o tenemos que romper todo?”

Ese cambio de pregunta es exactamente el paso de **usar** APIs a **diseñarlas**.

---

## Regla de oro

**Una API bien diseñada minimiza sorpresas para el consumer y maximiza libertad para el producer.**

Eso es lo que iremos construyendo en el resto del módulo:

- contrato explícito
- modelado durable
- evolución segura
- pruebas
- edge controls
- rollout con señales

---

:::exercise{title="Diagnostica una API frágil"}
Piensa en la API del backend de un chatbot con estos endpoints:

- `POST /sendMessage`
- `POST /getHistory`
- `POST /getUsage`

Responde:

1. ¿Qué problemas de diseño ves en estos nombres?
2. ¿Qué consumers distintos podrían sufrir con esta API?
3. ¿Qué parte del problema es de protocolo y qué parte es de contrato?
4. Reescribe la superficie inicial con una convención más durable.
:::
