## Context

Ver `proposal.md` — Why. Hechos del repositorio que condicionan el enfoque (verificados 2026-11-13):

- **El tramo compartido es el punto de convergencia.** Los tres canales (correo, web, telefonía) desembocan en `POST /api/v1/incidentes/` del backend; N8N orquesta y llama a ese endpoint. La latencia end-to-end ya está instrumentada: `latencia_e2e_ms = persistido_en - ingresado_en`, expuesta en el detalle y en el listado (`e2e-timing-instrumentation`).
- **El perfil `corpus` es el entorno desechable.** `postgres-corpus` (host 5434, base `mesa_de_ayuda_corpus`), `backend-corpus` (host 8001) y `n8n-corpus` (host 5679, webhook web `incidente-web`). Nunca toca la base operativa `mesa_de_ayuda`.
- **El patrón de costo cero ya existe.** `scripts/dry_run/compose.dry-run.yml` inyecta `GEMINI_API_KEY` ficticia y `COST_GUARD_BUDGET_USD=0` (dos capas independientes); el `dry-run-harness` formaliza el guardarraíl y aborta si detecta clave real o presupuesto distinto de cero.
- **El camino determinístico resuelve el fixture.** `HybridClassifier` cortocircuita cuando `score_correctitud >= deterministic_score_threshold` (0,5166); con descripciones inequívocas no escala a Gemini. La clasificación resuelve sin inferencia paga.
- **El canal web sella `ingresado_en` en el borde del trigger** (`new Date().toISOString()`), de modo que la latencia del servidor incluye el trabajo del pipeline.
- **Precedente de integración en la tesis:** c-217 (archivado 2026-11-13) registró la sección `3.28` del memo; la sección nueva es la `3.29`.

## Goals / Non-Goals

**Goals:**

- Medir la capacidad del tramo compartido bajo concurrencia creciente (1/5/10/20) con latencia (p50/p95), throughput y tasa de error, de forma reproducible y de costo cero.
- Emitir un veredicto de tres vías bajo un criterio fijado antes de observar datos, para contrastar la dimensión medible de la subsidiaria multicanal (¿introduce cuellos de botella?).
- Registrar el resultado de forma aditiva (`numeros-canonicos.md` `3.29`) y llevar la prosa de `01/04/08/09` al estado «contrastada en su dimensión de capacidad», con los límites declarados.

**Non-Goals:**

- Medir el camino pago (Gemini) bajo carga: el arnés corre el camino determinístico; la latencia con inferencia paga no se mide (ver D2 y D8).
- Instrumentar la complejidad operativa percibida: queda declarada como no medida.
- Probar producción, escalar horizontalmente ni comparar hardware: medición en una sola máquina y perfil desechable.
- Cambiar el clasificador, el corpus, la referencia, el gate, `docker-compose.yml` o `n8n/workflow.json`.

## Decisions

### D1 — Dos capas de carga: convergencia del backend y orquestación N8N

**Elegido:** cargar dos capas por separado. (a) `POST /api/v1/incidentes/` (punto de convergencia, con `Bearer`), que aísla la capacidad del backend (reglas + una escritura a PostgreSQL). (b) `POST /webhook/incidente-web` del N8N del corpus, que ejercita N8N -> backend y revela si el orquestador agrega un cuello de botella.

**Por qué:** la hipótesis es sobre la *integración* de canales, que converge en el backend; medir solo N8N mezclaría el overhead del orquestador con el del backend, y medir solo el backend no probaría el camino real de entrada. Dos capas separan las dos contribuciones.

**Alternativas rechazadas:** (i) cargar los tres canales reales — correo usa sondado IMAP por minuto (no apto para concurrencia) y telefonía es paga; (ii) cargar solo el webhook web — no aísla el backend.

**Exclusión declarada:** correo y telefonía quedan fuera de la inyección concurrente por sondado y por costo; se documenta que la convergencia es agnóstica al canal, de modo que la medición sobre el punto de convergencia cubre a los tres.

### D2 — Costo cero por camino determinístico y guarda nula (decisión de dueño)

**Elegido:** fixture de descripciones determinísticas + `GEMINI_API_KEY` ficticia + `COST_GUARD_BUDGET_USD=0` sobre el perfil `corpus`. Ninguna solicitud escala; cualquier escalada accidental es denegada por la guarda y degradada con revisión humana, sin petición al proveedor. Cero llamadas a Gemini y a Twilio.

**Por qué:** el contraste debe ser reproducible por cualquier tribunal sin credenciales ni gasto. El costo de la inferencia no es el objeto de este contraste (ya lo mide c-217); el objeto es la capacidad del tramo.

**Alternativa considerada (decisión de dueño):** una corrida paga acotada que incluya una fracción de casos que escalen a Gemini, para medir la latencia con inferencia incluida. Costo estimado del orden de centavos a décimas de USD (el orden de magnitud de c-215: ~0,0007 USD/llamada); exigiría `GEMINI_API_KEY`, autorización de gasto (gobernanza MEDIUM) y un preregistro nuevo. Se difiere; ver Open Questions.

**Consecuencia declarada:** el veredicto mide el camino determinístico (sin inferencia paga). El límite se declara en la prosa y en el memo.

### D3 — Entorno desechable con override de costo cero

**Elegido:** levantar el perfil `corpus` (`docker compose --profile corpus …`) más un override nuevo `scripts/load_test/compose.load-test.yml` que inyecta la clave ficticia y el presupuesto nulo en `backend-corpus`. El arnés afirma dentro del contenedor que ambas capas están en efecto antes de enviar y aborta si no lo están.

**Por qué:** la base `mesa_de_ayuda_corpus` es descartable y ya está aislada de la operativa (c-70); el override replica el patrón de `compose.dry-run.yml` sin tocar artefactos versionados.

**Alternativa rechazada:** correr sobre el stack operativo `mesa_local` (como el dry-run) — escribiría carga en la base operativa; el perfil `corpus` es más seguro y ya existe.

### D4 — Fixture versionada de descripciones determinísticas

**Elegido:** `scripts/load_test/fixture_descripciones.json`, un conjunto fijo de descripciones (por ejemplo 30) con marcadores léxicos inequívocos por sector, cada una de longitud válida (≥ 10). El arnés rota las descripciones y asigna un `origen_message_id` único por solicitud. Verifica contra el registro de clasificación que ninguna escaló.

**Por qué:** el fixture fijo hace la corrida reproducible y garantiza el camino determinístico; el `origen_message_id` único evita la deduplicación idempotente y mantiene el conteo de respuestas 2xx alineado con el de solicitudes.

### D5 — Niveles de concurrencia y métricas

**Elegido:** niveles 1, 5, 10 y 20 concurrentes (configurables), 40 solicitudes por nivel y 3 repeticiones por nivel. Por nivel y por capa se registra: latencia de cliente (envío→respuesta) y `latencia_e2e_ms` del servidor, y se calcula p50, p95, p99, media, throughput (req/s) y tasa de error (no 2xx + timeouts, sin descartes silenciosos).

**Por qué:** cuatro niveles evidencian el crecimiento de latencia y la eventual saturación; las repeticiones amortiguan el ruido del entorno. La latencia de cliente es la métrica operativa; `latencia_e2e_ms` valida que el trabajo del pipeline se ejecutó.

### D6 — Criterio de decisión prerregistrado de tres vías

Constantes fijadas **antes** de la corrida (no se reajustan):

- Techo absoluto: `p95 ≤ 5000 ms` en todos los niveles (holgadamente por encima de la línea base de un único request y por debajo del timeout de ejecución de N8N de 300 s).
- Tolerancia de throughput: el throughput no decrece más del 10 % respecto del nivel anterior.
- Tasa de error: `0` en todos los niveles.
- Control de escalado (secundario): `p95(20) / p95(1) ≤ 20` (crecimiento a lo sumo lineal, sin colapso superlineal).

**Veredicto:** «sostenida» si las tres condiciones primarias se cumplen en todos los niveles; «no sostenida» si algún nivel viola alguna; «no concluyente» si la corrida queda incompleta o el entorno reporta fallos ajenos a la carga.

**Por qué tres vías:** replica el rigor del contraste de eficiencia de c-217 (regla prerregistrada) y evita declarar un cuello de botella por ruido ambiental o declarar ausencia de cuello de botella por una corrida parcial.

### D7 — Evidencia versionada

**Elegido:** el arnés escribe `evaluation/evidence/load_test_multicanal_<YYYY-MM-DD>.json` y su resumen `.md` con commit, fecha UTC, versión de N8N, perfil, hash del fixture, constantes del criterio, métricas por nivel y veredicto. Salidas deterministas (LF, UTF-8 sin BOM), sin secretos.

### D8 — Anclas de prosa, numeración y gobernanza

- `01-introduccion.tex:38`: reemplazar «La de integración multicanal no se somete a un contraste formal» por el estado real (capacidad contrastada con el test de carga; complejidad percibida no medida).
- `04-marco-metodologico.tex`: agregar un párrafo con el protocolo del test (niveles, métricas, criterio, entorno, costo cero).
- `08-discusion.tex:10`: reemplazar «tampoco se contrastó: no se midió la capacidad bajo carga concurrente» por el resultado medido.
- `09-conclusiones.tex:6,39`: reemplazar «no se contrastó» y «no la contrastan: no se midieron la capacidad bajo carga concurrente ni la complejidad percibida» por el resultado medido, declarando que la complejidad percibida sigue sin instrumento.
- Memo: sección nueva `3.29`, aditiva; la `3.28` y anteriores intactas. `dictamen-correcciones.md`: entrada nueva.
- Gobernanza MEDIUM; costo cero.

## Risks / Trade-offs

- [El fixture escala a Gemini por una descripción mal elegida] → verificación de etapa determinística por corrida; aborto ruidoso si alguna escala.
- [El techo de 5 s es demasiado holgado y no detecta saturación] → el control secundario de escalado (`p95(20)/p95(1) ≤ 20`) y la curva por nivel caracterizan la saturación aunque el techo no se cruce; el memo registra las cifras crudas.
- [Ruido del entorno (una laptop con otros procesos) sesga el veredicto] → 3 repeticiones por nivel y veredicto «no concluyente» ante corridas inestables; el reporte conserva todas las repeticiones.
- [Se lee el resultado como validación en producción] → requisito explícito de declarar la medición en una sola máquina y el camino determinístico; prohibido extrapolar (delta `tesis-document`).
- [Sobreventa de la hipótesis: presentar la capacidad como contraste total] → el estado es «contrastada en su dimensión de capacidad» y declara la complejidad percibida no medida (deltas `tesis-document` y `tesis-dictamen-v1-3-0`).
- [Colisión de numeración del memo] → usar `3.29`; verificar que `3.28` y anteriores queden intactas.

## Migration Plan

1. Crear `scripts/load_test/` (arnés, fixture, override de compose, pruebas offline, README) sin tocar artefactos versionados del stack.
2. Levantar el perfil `corpus` con el override; afirmar clave ficticia y presupuesto nulo; correr los niveles; capturar el reporte.
3. Editar la prosa `01/04/08/09`, agregar la sección `3.29` y la entrada del registro.
4. `openspec validate … --strict`; pruebas offline del arnés.
5. Rollback: eliminar `scripts/load_test/` y revertir las ediciones de prosa y del memo; la corrida no es destructiva para la base operativa ni para artefactos versionados.

## Open Questions

- ¿Se ejecutará la corrida paga acotada (D2, alternativa) como change de seguimiento para medir la latencia con inferencia incluida? Queda diferida y sujeta a autorización de gasto; no cambia el alcance ni las specs de este change. Decisión de dueño.
- Las constantes del criterio (D6) quedan fijadas en este diseño; el dueño puede ajustarlas antes de la corrida, pero no después de ver los resultados.
