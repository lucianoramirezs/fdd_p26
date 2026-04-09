---
title: "SOAP y protocolos legado"
---

## La analogia del restaurante: SOAP

Recuerda nuestro restaurante de la seccion 16. Hasta ahora has visto
formas relativamente sencillas de pedir tu comida: REST es como llenar
una comanda normal, SSE es el chef narrando lo que cocina, WebSocket es
una conversacion abierta con el mesero.

SOAP es otra cosa.

**SOAP es un formulario en triplicado, sellado por el gerente, con acuse
de recibo.** Para pedir un cafe necesitas llenar 3 paginas. Cada pagina
tiene secciones obligatorias: encabezado con tu identificacion, cuerpo
con la solicitud, y un sobre que envuelve todo. Si falta un campo, el
gerente rechaza tu solicitud.

```
  RESTAURANTE REST              RESTAURANTE SOAP
  ================              =================

  "Un cafe, por favor"          FORMULARIO DE SOLICITUD
                                +--------------------------+
  -> Cafe servido               | SOBRE (Envelope)         |
                                |  +---------------------+ |
                                |  | ENCABEZADO (Header)  | |
                                |  | - ID cliente: #4521  | |
                                |  | - Autorizacion: OK   | |
                                |  | - Timestamp: 14:32   | |
                                |  +---------------------+ |
                                |  | CUERPO (Body)        | |
                                |  | - Accion: PedirCafe  | |
                                |  | - Tipo: Americano    | |
                                |  | - Tamano: Grande     | |
                                |  +---------------------+ |
                                +--------------------------+
                                       |
                                       v
                                ACUSE DE RECIBO
                                +--------------------------+
                                | SOBRE (Envelope)         |
                                |  +---------------------+ |
                                |  | CUERPO (Body)       | |
                                |  | - Status: ACEPTADO  | |
                                |  | - Folio: CF-99812   | |
                                |  | - ETA: 5 min        | |
                                |  +---------------------+ |
                                +--------------------------+
```

Exagerado? Si. Pero cuando manejas transferencias bancarias de millones
de pesos, ese formalismo tiene sentido.


## Contexto historico

SOAP no aparecio de la nada. Fue parte de una evolucion:

```
  1998        1999         2001-2005           2006-2010        2010s
   |           |              |                   |               |
   v           v              v                   v               v
 XML-RPC --> SOAP 1.0 --> WS-* explosion --> REST backlash --> REST domina
   |           |              |                   |               |
   |       Microsoft +    WS-Security        Roy Fielding     JSON + HTTP
   |       IBM lanzan     WS-Reliability     publica tesis    se vuelven
   |       la spec        WS-Transaction     sobre REST       el estandar
   |                      WS-Addressing                       de facto
   |                      WS-Policy
   |                      WS-Federation
   |                      WS-Trust
   |                      WS-...
   |                          |
   |                    "WS-Death Star"
   |                    (tantos estandares
   |                     que nadie podia
   |                     implementarlos
   |                     todos)
```

La era WS-* fue un periodo donde los comites de estandarizacion crearon
decenas de especificaciones adicionales sobre SOAP. El resultado fue una
complejidad que ahuyento a la mayoria de los desarrolladores.


## Estructura del sobre SOAP

Un mensaje SOAP tiene una estructura rigida en XML:

```xml
<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
               xmlns:llm="http://api.example.com/llm">

  <soap:Header>
    <auth:ApiKey xmlns:auth="http://api.example.com/auth">
      sk-abc123...
    </auth:ApiKey>
  </soap:Header>

  <soap:Body>
    <llm:CreateMessage>
      <llm:Model>claude-3</llm:Model>
      <llm:Messages>
        <llm:Message role="user">Hola</llm:Message>
      </llm:Messages>
    </llm:CreateMessage>
  </soap:Body>

</soap:Envelope>
```

```
  +--------------------------------------------------+
  | soap:Envelope                                     |
  |                                                   |
  |  +---------------------------------------------+ |
  |  | soap:Header          (opcional pero comun)   | |
  |  |                                              | |
  |  |  Autenticacion, routing, transacciones,      | |
  |  |  metadata del mensaje                        | |
  |  +---------------------------------------------+ |
  |                                                   |
  |  +---------------------------------------------+ |
  |  | soap:Body             (obligatorio)          | |
  |  |                                              | |
  |  |  La operacion que quieres ejecutar           | |
  |  |  + sus parametros                            | |
  |  |                                              | |
  |  |  +----------------------------------------+ | |
  |  |  | soap:Fault        (solo en errores)     | | |
  |  |  |  Codigo de error + descripcion          | | |
  |  |  +----------------------------------------+ | |
  |  +---------------------------------------------+ |
  +--------------------------------------------------+
```


## WSDL: el contrato maquina-legible

WSDL (Web Services Description Language) es un documento XML que
**describe completamente** un servicio SOAP: que operaciones expone, que
parametros acepta, que tipos de datos usa y donde esta el endpoint.

```
  +------------------+        +------------------+
  |   Servidor SOAP  | -----> |   Archivo WSDL   |
  |                  |        |                  |
  |  - ObtenerSaldo  |        |  "ObtenerSaldo   |
  |  - Transferir    |        |   acepta:        |
  |  - ConsultarTipo |        |     cuenta: str  |
  |                  |        |   retorna:       |
  +------------------+        |     saldo: float"|
                              +------------------+
                                      |
                                      v
                              +------------------+
                              | Cliente generado |
                              | automaticamente  |
                              |                  |
                              | client.ObtenerSaldo("123")
                              +------------------+
```

La idea era poderosa: un programa lee el WSDL y **genera
automaticamente** el codigo cliente. No necesitas leer documentacion
humana. En la practica, los WSDL eran tan complejos que las herramientas
de generacion fallaban frecuentemente.


## SOAP vs REST: la misma operacion

Veamos la misma llamada a un LLM en ambos formatos:

```
  SOAP (~800 bytes)                    REST (~200 bytes)
  ==================================   ===========================

  <?xml version="1.0"?>               POST /v1/messages
  <soap:Envelope                       Content-Type: application/json
    xmlns:soap="http://..."            Authorization: Bearer sk-...
    xmlns:llm="http://..."
    xmlns:auth="http://...">           {
                                         "model": "claude-3",
    <soap:Header>                        "messages": [
      <auth:ApiKey>                        {"role": "user",
        sk-abc123                           "content": "Hola"}
      </auth:ApiKey>                     ]
    </soap:Header>                     }

    <soap:Body>
      <llm:CreateMessage>
        <llm:Model>
          claude-3
        </llm:Model>
        <llm:Messages>
          <llm:Message role="user">
            Hola
          </llm:Message>
        </llm:Messages>
      </llm:CreateMessage>
    </soap:Body>

  </soap:Envelope>

  Resultado: ~800 bytes              Resultado: ~200 bytes
             XML verboso                        JSON conciso
             Tipado estricto                    Flexible
             Contrato formal                    Documentacion humana
```

4x mas datos para decir exactamente lo mismo.


## Por que SOAP perdio

```
  FACTOR                          SOAP              REST
  ----------------------------------------------------------------
  Bytes por request               ~800              ~200
  Curva de aprendizaje            Semanas           Horas
  Herramientas necesarias         IDE + generador   curl
  Formato de datos                Solo XML          JSON, XML, etc.
  Estandares adicionales          ~30 specs WS-*    HTTP ya existe
  Legibilidad humana              Baja              Alta
  Debugging                       Dificil           Facil (curl)
  ----------------------------------------------------------------
```

La explosion de estandares WS-* (conocida informalmente como el
"WS-Death Star") fue el golpe final. Cada problema tenia su propia
especificacion: seguridad (WS-Security), transacciones
(WS-AtomicTransaction), mensajeria confiable (WS-ReliableMessaging)...
La complejidad se volvio inmanejable para la mayoria de los equipos.


## Donde SOAP sigue vivo (importante)

No cometas el error de pensar que SOAP esta muerto. **Lo vas a
encontrar en el mundo real.** Estos sectores dependen de el:

```
  +-------------------+------------------------------------------+
  | SECTOR            | EJEMPLOS                                 |
  +-------------------+------------------------------------------+
  | Financiero        | SWIFT, APIs bancarias, procesadores      |
  |                   | de pagos legacy, sistemas de clearing    |
  +-------------------+------------------------------------------+
  | Salud             | HL7 v2, sistemas FHIR legacy,            |
  |                   | expedientes clinicos electronicos        |
  +-------------------+------------------------------------------+
  | Gobierno          | SAT (facturacion electronica),            |
  |                   | sistemas de adquisiciones, IMSS           |
  +-------------------+------------------------------------------+
  | Enterprise ERP    | SAP, Oracle EBS, integraciones            |
  |                   | corporativas legacy                      |
  +-------------------+------------------------------------------+
  | Telecomunicaciones| Provisionamiento de servicios,           |
  |                   | sistemas de facturacion                  |
  +-------------------+------------------------------------------+
```

Si trabajas en cualquiera de estos sectores (y en Mexico, el SAT es
practicamente inevitable), vas a tener que hablar SOAP en algun momento.


## SOAP en Python con zeep

Cuando te toque interactuar con un servicio SOAP, la libreria `zeep` es
tu mejor opcion en Python:

```python
from zeep import Client

# zeep lee el WSDL y genera el cliente automaticamente
client = Client("https://servicio.ejemplo.com/api?wsdl")

# llamas operaciones como si fueran metodos de Python
resultado = client.service.ObtenerSaldo(cuenta="123456")
print(resultado)
```

`zeep` hace exactamente lo que prometian las herramientas WSDL: lee el
contrato y genera un cliente usable. En la practica funciona bien para
la mayoria de los servicios SOAP que encontraras.

> **Verifica en el notebook:** `05_comparacion_protocolos.ipynb` tiene
> un ejemplo de como construir y parsear un sobre SOAP manualmente con
> `lxml`, para que entiendas que hay detras de la abstraccion de `zeep`.


## Conexion con arquitectura LLM

Esta es la **conexion** &#x2468; de nuestro diagrama maestro. SOAP no
aparece en los sistemas LLM modernos directamente. Pero aparece en las
**integraciones enterprise** que *llaman* a APIs de LLMs:

```
  +------------------+     SOAP      +------------------+     REST
  |  Sistema SAP     | ----------->  |  Middleware /     | ----------->
  |  (legacy)        |               |  Gateway          |
  +------------------+               +------------------+
                                            |
                                            | Traduce SOAP -> REST
                                            v
                                     +------------------+
                                     |  API del LLM     |
                                     |  (REST + SSE)    |
                                     +------------------+
```

El patron es comun: un sistema legacy habla SOAP, un middleware traduce
a REST, y el LLM responde en JSON. Si trabajas integrando LLMs en
empresas grandes, este es tu dia a dia.


:::exercise{title="Comparacion multi-protocolo"}

Toma la siguiente operacion: **crear un mensaje en un LLM** con modelo
`claude-3`, mensaje de usuario `"Explica que es una API"`, y
`max_tokens=500`.

Escribe la representacion de esta llamada en los 4 formatos:

1. **SOAP**: sobre completo con Envelope, Header (autenticacion) y Body
2. **REST**: metodo HTTP, URL, headers y body JSON
3. **GraphQL**: query o mutation con las variables necesarias
4. **gRPC**: definicion `.proto` del servicio y mensaje de request

Para cada uno, estima:
- Tamano aproximado del payload en bytes
- Numero de lineas de codigo necesarias para hacer la llamada en Python
- En que escenario elegirias ese formato sobre los otros

:::
