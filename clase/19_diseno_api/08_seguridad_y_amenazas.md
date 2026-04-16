---
title: "Seguridad y amenazas"
---

# Seguridad y amenazas

Una API puede estar bien documentada, bien modelada y bien testeada, y aun así ser insegura.

La seguridad no entra al final como un sticker. Tiene que influir en el diseño:

- qué expones
- quién puede llamar
- qué límites pones
- cómo piensas en abuso

---

## La analogía: no basta con tener menú claro

Un restaurante puede tener un menú impecable y aun así fallar si:

- cualquiera entra a la cocina
- no verificas quién recoge una orden
- aceptas cambios de cuenta de cualquiera

En APIs pasa igual. Un contrato claro no sustituye controles.

---

## Threat modeling

Threat modeling es una disciplina simple en espíritu:

1. dibuja el sistema
2. identifica activos valiosos
3. imagina cómo podrían abusarlo
4. piensa mitigaciones

Para el chatbot, activos importantes podrían ser:

- prompts privados
- conversaciones
- API keys
- créditos de uso
- datos de fine-tuning

---

## Preguntas mínimas

Cuando miras una API, pregunta:

- ¿qué datos serían costosos si se filtraran?
- ¿qué operaciones serían peligrosas si cualquiera pudiera ejecutarlas?
- ¿dónde entra tráfico no confiable?
- ¿qué pasa si un cliente manda requests maliciosas o excesivas?

---

## OWASP API risks, versión curso

Sin convertir esto en una materia completa de seguridad, hay riesgos que sí debes conocer:

Elegimos estos cinco porque aparecen una y otra vez en APIs modernas con datos de usuario, múltiples consumidores y servicios HTTP expuestos públicamente.

### 1. Broken object authorization

El usuario A puede ver el recurso del usuario B solo cambiando un ID.

### 2. Excessive data exposure

La API devuelve más información de la necesaria.

### 3. Lack of rate limiting

Abuso, scraping o agotamiento de recursos.

### 4. Security misconfiguration

Headers, CORS, debug mode, defaults peligrosos.

### 5. Unsafe consumption of APIs

Tu sistema también consume APIs ajenas. Si confías ciegamente en sus respuestas, heredas sus fallas.

---

## Authentication vs authorization

No son lo mismo.

- **Authentication**: quién eres
- **Authorization**: qué puedes hacer

Ejemplo:

- token válido = autenticado
- intentar leer conversación ajena = autorización fallida

Confundir ambas cosas es fuente clásica de bugs graves.

---

## Dónde van los controles

### En el borde

- auth inicial
- rate limiting
- TLS
- bloqueo básico

### En el servicio

- autorización de dominio
- validación de ownership
- protección contra acceso indebido a objetos

---

## Conexión con la arquitectura del LLM

Supón este endpoint:

```http
GET /v1/conversations/{id}
```

El bug típico no es de HTTP ni de OpenAPI. Es este:

- el usuario está autenticado
- pero el servicio no verifica que esa conversación le pertenezca

Resultado: fuga de datos.

Eso es un problema de diseño de seguridad, no solo de implementación.

---

## Regla práctica

**Piensa como diseñador de abuso, no solo como diseñador de features.**

Cada endpoint debería hacerte pensar:

- ¿qué pasa si me llaman demasiado?
- ¿qué pasa si cambian un ID?
- ¿qué pasa si repiten la request?
- ¿qué pasa si intentan leer más de lo debido?

---

:::exercise{title="Haz un mini threat model"}
Para una API de chatbot con:

- `POST /v1/chat`
- `GET /v1/conversations/{id}`
- `POST /v1/fine-tuning/jobs`

haz una tabla con tres columnas:

1. activo o recurso
2. amenaza plausible
3. mitigación inicial

Incluye al menos:

- una amenaza de autorización
- una amenaza de rate limiting
- una amenaza de exposición excesiva de datos
:::
