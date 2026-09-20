# Contrato de medición de latencia end-to-end (C-39)

Este documento define, de forma auditable y reproducible, cómo el sistema mide la
latencia END-TO-END por incidente: desde que el mensaje **ingresa al sistema**
hasta que su **persistencia queda confirmada** en la base de datos. Es la fuente
para derivar `tiempo_automatizado_s` del corpus de la tesis (Capítulo 7).

## 1. Definiciones

| Concepto | Campo | Definición |
|----------|-------|------------|
| Ingreso | `ingresado_en` | Instante en que el mensaje ingresa al sistema, capturado en el **borde del trigger** del canal (N8N) y enviado en el payload de alta. |
| Persistencia confirmada | `persistido_en` | Instante en que finalizan las escrituras del incidente y su log de clasificación, sellado **una sola vez** dentro de la transacción de alta, inmediatamente antes del commit. |
| Latencia derivada | `latencia_e2e_ms` | `persistido_en - ingresado_en` expresada en milisegundos. Es **derivada**, no se persiste como columna. |
| Anomalía | `latencia_anomala` | `true` cuando la latencia derivada es negativa (medición inválida). |

Ambos instantes se almacenan como `TIMESTAMPTZ` (UTC) y se exponen en
`IncidenteRead`. La latencia **no** se denormaliza: se deriva en la capa de
lectura para no duplicar la fuente de verdad.

## 2. Unidades

`latencia_e2e_ms` se expresa en **milisegundos** (entero). Para el corpus:
`tiempo_automatizado_s = latencia_e2e_ms / 1000`. El cableado de
`tiempo_automatizado_s` es un consumidor futuro, fuera de C-39.

## 3. Validación del instante de ingreso

- Se acepta solo **ISO-8601 con zona horaria explícita** (`Z` u offset). Un valor
  **naive** (sin zona) se rechaza con error de validación: enmascararía errores
  del emisor y contaminaría la medición.
- El valor se **normaliza a UTC** antes de persistir.
- Se rechaza un valor posterior al ahora del servidor más allá de una
  **tolerancia configurable** (`TIMING_FUTURE_TOLERANCE_SECONDS`, por defecto
  **30 s**). La tolerancia absorbe el skew de relojes entre contenedores sin
  encubrir datos inválidos.
- El campo es **nullable**: los clientes API directos y las filas legacy pueden
  no proveerlo, y su ausencia no bloquea el alta.

## 4. Política de latencia negativa

Una latencia negativa (por ejemplo, un ingreso futuro dentro de la tolerancia o
una desalineación de relojes) **NUNCA** se reporta como medición válida:

- `latencia_e2e_ms` se expone como **nulo** (no como un valor negativo).
- `latencia_anomala` queda en **`true`** para su diagnóstico.
- El caso queda **excluido del corpus y del análisis**. Nunca se acepta en
  silencio ni se recorta (`clamp`) a cero, porque fabricaría un valor inexistente.

## 5. Caveats por canal (comparabilidad)

El análisis de latencias **debe reportarse por canal**: los puntos de ingreso no
son homogéneos y mezclarlos rompería la comparabilidad.

- **Correo**: el ingreso es el instante en que el **poller de Outlook recoge el
  mensaje**, NO la llegada al buzón. La latencia **excluye la espera previa a la
  recogida** (hasta ~60 s por `everyMinute`), por lo que **sub-mide** respecto de
  la llegada real al buzón y no es comparable caso a caso con web/telefonía.
- **Telefonía**: el ingreso es la **recepción del resumen post-llamada de Twilio**
  (`call-summary.complete`). La latencia **NO incluye la duración de la llamada ni
  la generación del resumen en Twilio**; la hipótesis de medir desde el inicio de
  la llamada (Voice Insights) queda diferida a Fase 2.
- **Web**: el ingreso es el **instante de recepción del webhook**; exacto.

El sello de telefonía se captura **antes del `AI Agent`**, de modo que la latencia
del canal incluye el tiempo del agente pago (el costo dominante).

## 6. Exclusion de replays idempotentes

Un reintento con el mismo `origen_message_id` devuelve el incidente existente
**sin re-medir**: `ingresado_en` y `persistido_en` conservan los valores del alta
original y no se crea una segunda fila ni una segunda latencia. La exclusión es
**por construcción** (la medición vive en la fila), no requiere una marca
adicional en el workflow.

## 7. Precisión y límites

- `persistido_en` es el último instante de escritura de la transacción; el
  round-trip del commit a PostgreSQL **no** queda incluido. Se acota como
  despreciable frente a latencias de segundos. La confirmación fuerte la aporta el
  `201`: el backend commitea antes de emitir la respuesta.
- `updated_at` **no** se usa como instante de persistencia confirmada: se
  recalcula en cada UPDATE (revisión humana, cambio de estado), por lo que
  destruiría la medición.

## 8. Migración y despliegue

La migración Alembic `006_add_timing_instrumentation.py` (`down_revision = "005"`)
agrega `ingresado_en` y `persistido_en` como columnas `TIMESTAMPTZ` **nullable**,
sin backfill y sin índices; su `downgrade` dropea ambas. No se fabrican instantes
de ingreso para filas históricas: el dato no existe y fabricarlo violaría la
honestidad de la medición.

Orden de despliegue: aplicar la migración y desplegar el backend tolerante
(schema nullable + sello del servicio) **antes** de que N8N empiece a enviar
`ingresado_en`.
