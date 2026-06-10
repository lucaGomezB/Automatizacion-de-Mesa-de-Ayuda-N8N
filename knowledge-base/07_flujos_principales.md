# Flujos Principales

## Flujo 1: Incidente por formulario web (implementado)

**Disparador**: usuario envía el formulario React. **Actor**: usuario interno.

1. Frontend valida y envía `POST /api/v1/incidentes` (Axios, timeout 20 s > timeout Gemini 10 s).
2. `IncidenteService` persiste el incidente (estado "nuevo") y dispara la clasificación híbrida.
3. `HybridClassifier`: etapa determinística → si confianza ≥ 0,90 decide; si no → pseudonimizar (pendiente C-03) → Gemini → validación de respuesta (RN-VA) → si todo falla, fallback.
4. Se escribe `clasificacion_log` (etapa, confianza, respuesta_raw); se asigna `sector_id` al incidente.
5. *(Pendiente C-02)* `notify_n8n()` fire-and-forget.
6. Respuesta 201 con ticket + sector + confianza → frontend muestra SuccessCard.

```
Usuario → React → POST /incidentes → Service → Classifier ─┬─ deterministic ≥0,90
                                        │                  ├─ gemini (pseudonimizado)
                                        │                  └─ fallback (conf=0,0)
                                        ▼
                                clasificacion_log + incidente.sector_id
                                        ▼
                        201 {id, sector, confianza} → SuccessCard
```

**Errores**: Gemini timeout → fallback, ticket se crea igual (RN-EX-02) · validación Pydantic falla → 422 · DB caída → 500 con CORS garantizado (RN-EX-03).

## Flujo 2: Incidente por correo (pendiente C-04/C-05)

**Disparador**: correo nuevo en casilla institucional. **Actor**: usuario interno.

1. Trigger IMAP de N8N detecta el mensaje.
2. Nodo JS valida campos requeridos (lógica Anexo H — hoy placeholder).
3. IF datos completos → nodo de normalización (RN-RE-01) → `POST /api/v1/incidentes`.
4. IF datos incompletos → respuesta automática solicitando lo faltante.
5. Notificación al usuario con número de ticket + log de auditoría (30 días).

## Flujo 3: Incidente telefónico (pendiente C-05)

**Disparador**: llamada al número virtual Twilio. **Actor**: usuario interno.

1. TwiML reproduce bienvenida (español rioplatense); graba hasta 45 s (fin con `#`).
2. Twilio transcribe y dispara webhook hacia N8N post-cuelgue.
3. Agente LangChain parsea la transcripción (sesión en Redis); validación Python de campos extraídos.
4. IF incidente creable → mismo pipeline del Flujo 2 paso 3; si no → loop de refinamiento del agente.
5. Latencia objetivo cuelgue→confirmación: 12-15 s.

## Flujo 4: Revisión y validación humana (implementado)

**Disparador**: clasificación con confianza < 0,70. **Actor**: operador / sector.

1. El registro entra a la cola (`requiere_revision_humana=true`, `sector_id_validado IS NULL`).
2. Operador abre Administración → cola FIFO (`GET /clasificaciones/revision-pendiente`).
3. Modal "Validación Humana": muestra predicción + confianza + etapa; operador elige sector correcto.
4. `PATCH /clasificaciones/{log_id}/validar` → verifica que el sector exista → asigna `sector_id_validado`.
5. El registro sale de la cola y se vuelve etiqueta de verdad del corpus (RN-RH-04).

## Flujo 5: Evaluación experimental (pendiente C-08)

1. Cargar corpus CSV de 200 casos (no versionado en git — pseudonimizado).
2. Clasificar cada caso; registrar categoría, confianza, etapa.
3. Calcular: exactitud global, matriz de confusión 3×3, precision/recall/F1 por clase, F1 macro, IC Wilson 95 %, Wilcoxon pareado para tiempos.
4. Emitir `evaluation/report.md` + notebook con visualizaciones.
