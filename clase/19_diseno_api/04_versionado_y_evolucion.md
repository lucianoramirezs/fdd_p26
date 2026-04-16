---
title: "Versionado y evolución"
---

# Versionado y evolución

Ninguna API útil se queda quieta. Cambian los modelos, cambian los consumers, cambian los equipos y cambian los requisitos del negocio.

La pregunta no es si tu API cambiará. La pregunta es:

**¿cómo cambias sin romper a quienes dependen de ella?**

---

## La analogía: remodelar el restaurante sin cerrarlo

Imagina que el restaurante sigue abierto mientras:

- cambias la cocina
- agregas un nuevo menú
- reubicas la caja
- entrenas a meseros nuevos

Si todo eso sucede de golpe y sin señalización, el cliente sufre.

Versionar es poner reglas para cambiar el sistema **sin convertir cada despliegue en una ruleta**.

---

## Cambio breaking vs non-breaking

### Non-breaking

El consumer viejo sigue funcionando.

Ejemplos:

- agregar un campo opcional a la response
- agregar un endpoint nuevo
- documentar un error adicional sin cambiar los anteriores

### Breaking

El consumer viejo deja de funcionar o cambia de significado.

Ejemplos:

- quitar un campo esperado
- cambiar `id: string` por `id: int`
- renombrar `output_text` a `text`
- hacer obligatorio un campo antes opcional

### Ojo: "agregar campo opcional" no es magia

Ese cambio suele ser compatible solo si el consumer:

- ignora campos desconocidos
- no valida la response de forma excesivamente rígida

Por eso la compatibilidad no depende solo del producer. También depende de cómo leen los datos los consumers.

---

## Estrategias de versionado

### En la URL

```http
/v1/chat
/v2/chat
```

Ventaja:

- visible
- fácil de razonar

Costo:

- puede duplicar superficies
- obliga a convivir con varias versiones al mismo tiempo
- aumenta trabajo de documentación y soporte

### En headers

```http
Accept: application/vnd.chatbot.v2+json
```

Ventaja:

- URL limpia

Costo:

- más difícil de descubrir y debuggear
- menos visible en logs, proxies y troubleshooting manual
- puede sorprender a caches o middleware mal configurados

En cursos introductorios y muchas APIs públicas, la versión en la URL suele ser la más fácil de enseñar y operar.

---

## Semantic versioning, con cuidado

La intuición de SemVer ayuda:

- MAJOR: cambio breaking
- MINOR: cambio compatible
- PATCH: fix sin cambio de contrato

Pero recuerda: una API no siempre mapea perfecto a una librería. El punto no es idolatrar SemVer; es hacer explícito **qué tipo de compatibilidad prometes**.

---

## Deprecación

Deprecar no es borrar mañana. Es declarar:

1. qué parte se volverá obsoleta
2. qué reemplazo existe
3. desde cuándo empieza la cuenta regresiva
4. cuándo se apagará

```
API madura:
anunciar -> convivir -> medir uso -> retirar

API inmadura:
romper -> avisar tarde -> apagar incendios
```

---

## APIs como seams para cambiar el sistema

Una buena API funciona como un **seam**: un punto de frontera que te deja cambiar la implementación detrás sin arrastrar a todos los consumers.

Ejemplo en el chatbot:

```
Frontend
   │
   ▼
POST /v1/chat
   │
   ├── hoy: llama a modelo A
   ├── mañana: llama a router de modelos
   └── después: llama a caché + modelo + filtros
```

Si el contrato externo sigue estable, el producer gana libertad interna.

---

## Compatibilidad práctica

Checklist antes de cambiar una API:

- ¿El consumer parsea estrictamente?
- ¿Hay apps móviles con versiones viejas?
- ¿Hay clientes externos fuera de tu control?
- ¿Los tests cubren el contrato?
- ¿Puedes medir quién usa aún el comportamiento viejo?

Sin visibilidad de consumers, versionar es adivinar.

---

## Tabla rápida

| Cambio | ¿Suele romper? |
|---|---|
| Agregar campo opcional | No |
| Quitar campo existente | Sí |
| Cambiar tipo de dato | Sí |
| Agregar endpoint nuevo | No |
| Cambiar semántica de un campo | Sí |
| Hacer obligatorio algo antes opcional | Sí |
| Agregar valor a enum | Depende del consumer |

### ¿Por qué un enum nuevo puede romper?

Porque muchos clientes implementan lógica como:

```python
if status == "queued":
    ...
elif status == "running":
    ...
elif status == "completed":
    ...
else:
    raise ValueError("status desconocido")
```

Si mañana agregas `paused`, el contrato cambió de forma aparentemente aditiva, pero el consumer puede caer en error.

Diseño más tolerante:

- tener caso `unknown` o `other`
- registrar el valor nuevo sin colapsar
- degradar funcionalidad en lugar de romper

---

## Conexión con la arquitectura del LLM

Imagina que hoy tu response es:

```json
{"output_text": "Hola"}
```

Y mañana quieres:

```json
{
  "output_text": "Hola",
  "usage": {"input_tokens": 10, "output_tokens": 12},
  "finish_reason": "stop"
}
```

Eso probablemente es aditivo.

Pero si cambias a:

```json
{
  "content": [{"type": "text", "text": "Hola"}]
}
```

el frontend viejo quizá ya no sepa leer la respuesta. Ahí aparece la necesidad de versionar o de introducir transición.

---

> **Verifica en el notebook:** Revisa `clase/19_diseno_api/code/02_modelado_y_versionado.ipynb` para ver ejemplos automáticos de cambios seguros vs breaking y cómo detectarlos con código.

---

:::exercise{title="Decide si necesitas v2"}
Supón que tu API actual tiene:

- `POST /v1/chat`
- response con `output_text: string`

Quieres migrar a una response con lista de bloques:

```json
{
  "content": [
    {"type": "text", "text": "Hola"}
  ]
}
```

Responde:

1. ¿Es cambio breaking o no?
2. ¿Podrías hacerlo aditivo? ¿Cómo?
3. ¿Necesitas `v2` o basta una etapa de transición?
4. ¿Qué pruebas y métricas revisarías antes de retirar el formato viejo?
:::
