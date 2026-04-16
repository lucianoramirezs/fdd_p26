---
title: "Pruebas de APIs"
---

# Pruebas de APIs

Diseñar un contrato no basta. Hay que **protegerlo**.

Sin pruebas, cada cambio de implementación corre el riesgo de convertir una API correcta en una API que "casi" se parece a lo prometido. Y en APIs, "casi" suele significar bugs de integración.

---

## La analogía: probar cocina, menú y servicio

Un restaurante serio no prueba solo que la cocina funciona.

También prueba:

- que el menú diga la verdad
- que el mesero tome bien la orden
- que el plato correcto llegue a la mesa

En APIs, esas capas se parecen a:

- tests de contrato
- tests de componente
- tests de integración
- tests end-to-end

---

## La pirámide, sin fanatismo

```
              /\
             /  \        E2E
            /----\
           /      \      Integracion
          /--------\
         /          \    Componente
        /------------\
       /              \  Contrato / unitarios del borde
      /________________\
```

La idea no es memorizar una figura. Es entender costo y señal:

- abajo: rápidas, frecuentes, baratas
- arriba: más realistas, pero más lentas y frágiles

---

## Contract testing

Pregunta principal:

> “¿Lo que entrega el producer sigue respetando el contrato que el consumer espera?”

Ejemplo:

- contrato dice que `output_text` es `string`
- backend devuelve `null`

Tal vez el endpoint respondió `200`, pero ya rompiste el acuerdo.

Contract testing sirve especialmente cuando:

- varios consumers dependen del mismo producer
- el contrato está en OpenAPI o schema verificable
- quieres detectar drift temprano

### Dos sabores útiles

- **provider-driven**: el producer valida que su implementación siga cumpliendo el contrato publicado
- **consumer-driven**: consumidores concretos expresan qué parte del contrato realmente usan y esperan

Para este curso, la idea más importante es la primera: si tienes contrato verificable, puedes poner una alarma automática contra drift.

---

## Component testing

Aquí pruebas el servicio en una capa más integrada, pero todavía controlada.

Ejemplo:

- levantas el controlador del chatbot
- mockeas el cliente del LLM
- verificas que `POST /v1/chat` responde bien para entradas válidas e inválidas

Te importa comportamiento del componente, no toda la plataforma.

---

## Integration testing

Aquí sí revisas la interacción entre piezas reales o casi reales:

- servicio + base de datos
- servicio + cola
- servicio + dependencia HTTP stubbeada

Busca responder:

> “¿Estas partes hablan bien entre sí?”

---

## End-to-end

El test más caro responde:

> “¿El sistema completo hace lo correcto desde la perspectiva del usuario?”

Ejemplo del chatbot:

1. el frontend manda prompt
2. backend valida contrato
3. se llama al modelo
4. se guarda conversación
5. se devuelve response renderizable

Útil, sí. Pero no quieres que toda la estrategia dependa solo de E2E.

---

## Qué protege cada capa

| Capa | Qué detecta bien | Qué no detecta tan bien |
|---|---|---|
| Contrato | drift de shape y tipos | bugs profundos de integración |
| Componente | reglas del endpoint | fallas de infraestructura real |
| Integración | problemas entre dependencias | UX final |
| E2E | flujo completo | diagnóstico preciso |

---

## Un mismo request visto en las cuatro capas

Tomemos `POST /v1/chat`:

```
1. Contrato
   "La response tiene id:string y output_text:string?"

2. Componente
   "El handler valida input, maneja errores y arma la response correcta?"

3. Integracion
   "Se guarda la conversacion y el cliente del modelo responde como esperamos?"

4. E2E
   "Desde el punto de vista del usuario, el prompt entra y la respuesta aparece?"
```

Observa la diferencia:

- las capas bajas aíslan mejor el problema
- las capas altas te muestran el comportamiento completo

Por eso "solo E2E" suele ser una mala estrategia: ves que algo falló, pero no sabes rápido dónde.

---

## Relación con evolución

Versionar bien sin pruebas es wishful thinking.

Si quieres:

- agregar campos opcionales
- deprecar viejos
- mover implementación interna

necesitas pruebas que te digan si el consumer aún está seguro.

---

## Conexión con la arquitectura del LLM

Para `POST /v1/chat`, una estrategia razonable sería:

1. **Contrato**: response cumple schema
2. **Componente**: endpoint maneja errores y parámetros
3. **Integración**: persistencia de conversación + cliente del modelo
4. **E2E**: flujo completo desde UI o cliente HTTP

Eso protege tanto el shape externo como el comportamiento del sistema.

---

> **Verifica en el notebook:** Revisa `clase/19_diseno_api/code/03_contract_testing.ipynb` para validar responses contra schema, comparar capas de prueba y ver un ejemplo pequeño de drift detectado automáticamente.

---

:::exercise{title="Diseña la estrategia de prueba mínima"}
Para la API del chatbot con estos endpoints:

- `POST /v1/chat`
- `GET /v1/conversations/{id}`
- `GET /v1/usage`

propón:

1. un test de contrato
2. un test de componente
3. un test de integración
4. un test E2E

Después responde: si solo pudieras automatizar dos de esas cuatro capas hoy, ¿cuáles eliges y por qué?
:::
