# Diagrama de Secuencia — Flujo Extremo a Extremo de un Incidente

Ilustra el flujo completo desde la recepción del incidente en un canal de entrada
hasta la confirmación al usuario o la derivación a revisión humana, en la
configuración entregada (release `v1.2.5`). El disparador por reportante no
identificado en el directorio es el change c-82 (13-10-2026), posterior a la
campaña de medición.

Procedencia: `n8n/workflow.json`, `App/Backend/app/routes/incidentes.py`,
`App/Backend/app/services/incidente_service.py` y
`App/Backend/app/classifiers/hybrid.py`.

```mermaid
sequenceDiagram
    autonumber

    participant Canal as Canal de Entrada<br/>(Correo IMAP / Web / Telefonía)
    participant N8N as N8N 2.11.2
    participant BE as Backend FastAPI<br/>POST /api/v1/incidentes
    participant CLAS as Clasificador Híbrido<br/>(determinístico, Gemini, reserva)
    participant PG as PostgreSQL<br/>(incidente + clasificacion_log)
    participant GEMINI as Google Gemini API
    participant OP as Operador Humano<br/>PATCH /clasificaciones/{id}/validar

    %% ── Ingreso del incidente ──────────────────────────────────────────────
    alt Correo o formulario web
        Canal->>N8N: Correo IMAP o envío al webhook incidente-web
    else Telefonía
        Canal->>BE: Llamada Twilio: transcripción y pseudonimización en el backend
        BE->>N8N: Handoff al webhook telefonia-handoff
    end
    Note over N8N: Valida campos requeridos.<br/>Si faltan datos, solicita reintento.
    N8N->>BE: POST /api/v1/incidentes<br/>{ descripcion, prioridad, canal_origen_id }

    %% ── Alta del incidente ─────────────────────────────────────────────────
    BE->>PG: Resolver reportante en el directorio<br/>(c-82, desde el 13-10-2026, posterior a la campaña)
    BE->>BE: Pseudonimizar descripción<br/>[EMAIL]/[TELEFONO]/[HOST]/[PERSONA]
    BE->>PG: INSERT incidente (descripcion_original cifrada,<br/>descripcion_pseudonimizada, estado="nuevo")

    %% ── Pipeline de clasificación ──────────────────────────────────────────
    BE->>CLAS: clasificar(descripcion_pseudonimizada)

    alt Señal dominante y score_correctitud ≥ 0,5166
        CLAS-->>BE: { sector, confianza, etapa="deterministic" }<br/>sin revisión por su confianza
    else Gemini requerido
        CLAS->>GEMINI: Prompt con descripción pseudonimizada
        GEMINI-->>CLAS: JSON { "categoría": "...", "confianza": 0.xx }
        Note over CLAS: Valida JSON: campos, categoría exacta,<br/>confianza en [0.0, 1.0].
        CLAS-->>BE: { sector, confianza, etapa="gemini" }<br/>revisión si confianza es menor que 0,70
    else Reserva: timeout, indisponibilidad, salida inválida o guarda de costo
        CLAS-->>BE: { etapa="reserva", confianza=0,0 }<br/>revisión siempre
    end

    %% ── Persistencia del resultado ─────────────────────────────────────────
    Note over BE: requiere_revision_humana = condición del clasificador<br/>OR reportante no identificado
    BE->>PG: UPDATE incidente + INSERT clasificacion_log<br/>(misma transacción)

    %% ── Respuesta al canal ─────────────────────────────────────────────────
    BE-->>N8N: HTTP 201 { id, sector, sectores_adicionales,<br/>requiere_revision_humana }
    alt requiere_revision_humana = false
        N8N-->>Canal: Confirmación: incidente asignado al sector
    else requiere_revision_humana = true
        N8N-->>Canal: Aviso: incidente derivado a revisión humana
    end

    %% ── Ciclo de revisión humana (cuando aplica) ───────────────────────────
    opt Revisión humana pendiente
        OP->>BE: GET /api/v1/clasificaciones/revision-pendiente
        BE-->>OP: [ { log_id, incidente_id, descripcion_pseudonimizada, ... } ]
        OP->>BE: PATCH /api/v1/clasificaciones/{log_id}/validar<br/>{ sector_id_validado }
        BE->>PG: UPDATE clasificacion_log SET sector_id_validado = ?<br/>WHERE id = log_id
        BE-->>OP: HTTP 200 { log actualizado }
        Note over PG: El log validado queda como insumo previsto<br/>para aprendizaje activo (trabajo futuro).
    end
```

## Notas

- **Doble representación**: `descripcion_original` se cifra at-rest con Fernet (Ley 25.326);
  `descripcion_pseudonimizada` es la única que consume el clasificador y la API.
- **Alcance por etapa**: la etapa determinística cortocircuita con señal dominante y
  `score_correctitud` ≥ 0,5166 y no deriva a revisión por su confianza; el umbral de 0,70
  rige solo sobre la salida de Gemini; la reserva fija confianza 0,0 y revisión siempre.
- **Disparador por directorio**: el backend deriva además a revisión cuando el reportante
  no se identifica en el directorio (c-82, desde el 13-10-2026, posterior a la campaña de
  medición), combinado por OR con la condición del clasificador.
- **Etapas del clasificador**: `deterministic` → `gemini` → reserva (error, timeout o guarda de costo).
- **N8N** actúa exclusivamente como orquestador de canales; toda la lógica de clasificación
  y persistencia reside en el backend FastAPI.
