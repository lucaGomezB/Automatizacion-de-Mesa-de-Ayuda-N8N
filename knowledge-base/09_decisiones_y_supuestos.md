# Decisiones y Supuestos

## Decisiones documentadas

### DD-01 — N8N como orquestador
**Decisión**: N8N 1.62 autoalojado en Docker. **Alternativas**: Zapier, Make, Power Automate (solo SaaS — descartadas por soberanía de datos), Apache Airflow (orientado a batch, excesivo para flujo reactivo). **Justificación**: despliegue autoalojado, código fuente disponible, sin costo por ejecución, webhooks nativos. **Trade-off**: punto único de coordinación; su disponibilidad condiciona el sistema.

### DD-02 — Orquestación sobre coreografía
**Decisión**: lógica de control centralizada en N8N. **Justificación**: trazabilidad auditiva de cada ejecución, prioritaria en este dominio (Hohpe & Woolf, 2003). **Trade-off**: menor robustez ante fallos parciales que un esquema de eventos distribuido.

### DD-03 — Clasificador híbrido en 2 etapas
**Decisión**: reglas determinísticas (umbral 0,90) antes que Gemini. **Alternativas**: LLM puro (mayor costo/latencia), clasificador supervisado propio (requiere corpus de entrenamiento que no existía). **Justificación**: ~62 % de casos resueltos sin inferencia externa; mejor relación exactitud/latencia/costo (hipótesis subsidiaria confirmada). **Trade-off**: mantenimiento del diccionario de keywords.

### DD-04 — Gemini 2.5 Flash con parámetros conservadores
**Decisión**: temperature 0,3, top_p 0,9, max_tokens 100, timeout 10 s, candidate_count 1. **Justificación**: clasificación requiere consistencia, no creatividad; JSON de salida ~15 tokens; el timeout limita la latencia del peor caso. Calibrados empíricamente (Anexo H). **Trade-off**: dependencia de proveedor externo y de la versión vigente del modelo (limitación §8.3).

### DD-05 — PostgreSQL relacional
**Decisión**: PostgreSQL 15.5. **Justificación**: dominio naturalmente relacional (FK con integridad declarativa), propiedades ACID, MVCC para carga mixta. **Alternativas**: NoSQL — descartada por estructura fija del dominio.

### DD-06 — FastAPI + Pydantic
**Decisión**: FastAPI 0.115 sobre Uvicorn. **Justificación**: validación de esquemas nativa, OpenAPI 3.1 automática, rendimiento, DI integrada.

### DD-07 — Umbralización doble (0,90 / 0,70)
**Decisión**: ≥ 0,90 decide la etapa determinística sola; < 0,70 exige revisión humana. **Justificación**: balance entre autonomía del sistema y supervisión humana significativa (human in the loop, §11.5).

### DD-08 — asyncpg en lugar de psycopg2 (divergencia respecto a la tesis)
**Decisión**: el código usa `asyncpg` + SQLAlchemy async; la tesis (§5.4) menciona `psycopg2-binary`. **Justificación de la divergencia**: E/S no bloqueante coherente con el event loop de FastAPI/uvicorn. **Implicancia**: los relationships no cargados NO pueden lazy-loadearse en contexto async (`MissingGreenlet`) — usar siempre `selectinload` explícito en queries que alimentan serialización (patrón `_CLASIFICACION_LOAD_OPTIONS`).

### DD-09 — `foreign_keys` explícito en relationships dobles
**Decisión**: `clasificacion_log` tiene dos FK a `sector.id` (predicho/validado); ambos lados de cada relationship declaran `foreign_keys`. **Contexto**: sin esto, SQLAlchemy lanza `AmbiguousForeignKeysError` en la primera query (bug corregido en PR #6).

### DD-10 — Clasificación dentro de POST /incidentes
**Decisión actual del código**: no existe `POST /api/v1/clasificar` independiente; la clasificación es parte de la creación. **Tensión**: la tesis y el workflow N8N (C-04) asumen el endpoint separado. Resolución pendiente — ver IN-01 en [10_preguntas_abiertas.md](10_preguntas_abiertas.md).

### DD-11 — Errores con CORS garantizado
**Decisión**: middleware ASGI propio (`_InternalErrorMiddleware`) dentro de CORSMiddleware + handlers a prueba de crasheos. **Contexto**: un 500 sin `Access-Control-Allow-Origin` es ilegible para el frontend (bug corregido en PR #6/#7).

## Supuestos inferidos

### SU-01 — El corpus de 200 casos existe fuera del repo
**Origen**: tesis Anexo F; `data/corpus_evaluacion_pseudonimizado.csv` no esta en git.
**Estado (2026-07-02)**: corpus real NO existe. Se construira corpus simulado en C-17 (evaluation-corpus-simulado) con distribucion 82/64/54.

### SU-02 — Las metricas de la tesis son resultados esperados a reproducir
**Origen**: el capitulo 7 reporta resultados completos. Framework de evaluacion (C-08) completado y archivado.
**Estado (2026-07-02)**: framework implementado (evaluation/ con 20 archivos). Corpus pendiente (C-17). Metricas de tesis (92%, F1=0.919) NO son reproducibles sin el corpus. La corrida provisoria con FakeClassifier da 63% — no comparable.

### SU-03 — N8N corre en la misma red Docker que la API
**Origen**: docker-compose del repo + §6.1. **Riesgo**: URLs de webhook mal configuradas entre contenedores. **Validación**: probar `notify_n8n` en C-02 con ambos contenedores arriba.

### SU-04 — La casilla de correo y la cuenta Twilio existen y son configurables
**Origen**: §5.2, §6.4. **Riesgo**: C-05 no puede probarse end-to-end sin credenciales reales.
**Estado (2026-07-02)**: el trigger de correo usa Microsoft Outlook (Graph API), NO IMAP como dice la tesis. Sin credenciales Outlook/Twilio no se puede probar end-to-end. Twilio requiere ademas script TwiML (C-16).

### SU-05 — El despliegue productivo en Kubernetes es aspiracional
**Origen**: §6.1 menciona K8s 1.30, pero no hay manifiestos en el repo. **Riesgo**: bajo (la validación corre sobre Compose). **Validación**: decidir si K8s entra en alcance de C-10.
