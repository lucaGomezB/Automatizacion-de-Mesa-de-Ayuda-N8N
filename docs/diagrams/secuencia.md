# Diagrama de Secuencia — Flujo Extremo a Extremo de un Incidente

Ilustra el flujo completo desde la recepción del incidente en un canal de entrada
hasta la confirmación al usuario o la derivación a revisión humana, en la
configuración entregada (release `v1.2.5`). El disparador por reportante no
identificado en el directorio es el change c-82 (13-10-2026), posterior a la
campaña 2026-10.

Procedencia: `n8n/workflow.json`, `App/Backend/app/routes/incidentes.py`,
`App/Backend/app/services/incidente_service.py` y
`App/Backend/app/classifiers/hybrid.py`.

> **Figura dividida en dos partes** (observación N-11 del tribunal: legibilidad a tamaño de
> impresión). La parte A cubre el ingreso, el alta y la clasificación del incidente
> (mensajes 1 a 13); la parte B cubre la persistencia del resultado, la respuesta al canal y
> el ciclo de revisión humana (mensajes 14 a 22, numeración continuada). La configuración de
> tipografía y espaciado va embebida en el bloque (`%%{init}%%`).

### Parte A — Ingreso, alta y clasificación

```mermaid
%%{init: {"fontFamily":"Arial, Helvetica, sans-serif","themeVariables":{"fontFamily":"Arial, Helvetica, sans-serif","fontSize":"16px"},"sequence":{"useMaxWidth":false,"mirrorActors":false,"actorMargin":0,"width":120,"height":50,"messageFontSize":16,"noteFontSize":16,"actorFontSize":16,"actorFontFamily":"Arial, Helvetica, sans-serif","noteFontFamily":"Arial, Helvetica, sans-serif","messageFontFamily":"Arial, Helvetica, sans-serif","boxMargin":6,"messageMargin":24,"noteMargin":8,"wrap":false}}}%%
sequenceDiagram
    autonumber

    participant Canal as Canal de Entrada<br/>(Correo IMAP /<br/>Web / Telefonía)
    participant N8N as N8N 2.11.2
    participant BE as Backend FastAPI<br/>POST<br/>/api/v1/incidentes
    participant PG as PostgreSQL<br/>(incidente +<br/>clasificacion_log)
    participant CLAS as Clasificador Híbrido<br/>(determinístico,<br/>Gemini, reserva)
    participant GEMINI as Google<br/>Gemini API

    %% ── Ingreso del incidente ──
    alt Correo o formulario web
        Canal->>N8N: Correo IMAP o envío al<br/>webhook incidente-web
    else Telefonía
        Canal->>BE: Llamada Twilio: transcripción y<br/>pseudonimización en el backend
        BE->>N8N: Handoff al webhook<br/>telefonia-handoff
    end
    Note over N8N: Valida campos<br/>requeridos.<br/>Si faltan datos,<br/>solicita reintento.
    N8N->>BE: POST /api/v1/incidentes<br/>{ descripcion, prioridad,<br/>canal_origen_id }

    %% ── Alta del incidente ──
    BE->>PG: Resolver reportante en el<br/>directorio (desde el<br/>13-10-2026, posterior a la<br/>campaña 2026-10)
    BE->>BE: Pseudonimizar descripción<br/>[EMAIL]/[TELEFONO]/[HOST]/[PERSONA]
    BE->>PG: INSERT incidente<br/>(descripcion_original<br/>cifrada,<br/>descripcion_pseudonimizada,<br/>estado="nuevo")

    %% ── Pipeline de clasificación ──
    BE->>CLAS: clasificar(<br/>descripcion_pseudonimizada)

    alt Señal dominante y score_correctitud ≥ 0,5166
        CLAS-->>BE: { sector, confianza,<br/>etapa="deterministic" }<br/>sin revisión por su confianza
    else Gemini requerido
        CLAS->>GEMINI: Prompt con<br/>descripción<br/>pseudonimizada
        GEMINI-->>CLAS: JSON { "categoría":<br/>"...", "confianza":<br/>0.xx }
        Note over CLAS: Valida JSON: campos,<br/>categoría exacta,<br/>confianza en [0.0, 1.0].
        CLAS-->>BE: { sector, confianza,<br/>etapa="gemini" }<br/>revisión si confianza es<br/>menor que 0,70
    else Reserva: timeout, indisponibilidad, salida inválida o guarda de costo
        CLAS-->>BE: { etapa="reserva",<br/>confianza=0,0 }<br/>revisión siempre
    end
```

### Parte B — Persistencia, respuesta y revisión humana

```mermaid
%%{init: {"fontFamily":"Arial, Helvetica, sans-serif","themeVariables":{"fontFamily":"Arial, Helvetica, sans-serif","fontSize":"16px"},"sequence":{"useMaxWidth":false,"mirrorActors":false,"actorMargin":0,"width":120,"height":50,"messageFontSize":16,"noteFontSize":16,"actorFontSize":16,"actorFontFamily":"Arial, Helvetica, sans-serif","noteFontFamily":"Arial, Helvetica, sans-serif","messageFontFamily":"Arial, Helvetica, sans-serif","boxMargin":6,"messageMargin":24,"noteMargin":8,"wrap":false}}}%%
sequenceDiagram
    autonumber 14

    participant Canal as Canal de Entrada<br/>(Correo IMAP /<br/>Web / Telefonía)
    participant N8N as N8N 2.11.2
    participant BE as Backend FastAPI<br/>POST<br/>/api/v1/incidentes
    participant PG as PostgreSQL<br/>(incidente +<br/>clasificacion_log)
    participant OP as Operador Humano<br/>PATCH<br/>/clasificaciones/{id}/validar

    %% ── Persistencia del resultado ──
    Note over BE: requiere_revision_humana =<br/>condición del clasificador<br/>OR reportante no identificado
    BE->>PG: UPDATE incidente +<br/>INSERT clasificacion_log<br/>(misma transacción)

    %% ── Respuesta al canal ──
    BE-->>N8N: HTTP 201 { id, sector,<br/>sectores_adicionales,<br/>requiere_revision_humana }
    alt requiere_revision_humana<br/>= false
        N8N-->>Canal: Confirmación: incidente<br/>asignado al sector
    else requiere_revision_humana<br/>= true
        N8N-->>Canal: Aviso: incidente derivado<br/>a revisión humana
    end

    %% ── Ciclo de revisión humana (cuando aplica) ──
    opt Revisión humana pendiente
        OP->>BE: GET /api/v1/clasificaciones/<br/>revision-pendiente
        BE-->>OP: [ { log_id, incidente_id,<br/>descripcion_pseudonimizada, ... } ]
        OP->>BE: PATCH /api/v1/clasificaciones/<br/>{log_id}/validar<br/>{ sector_id_validado }
        BE->>PG: UPDATE clasificacion_log<br/>SET sector_id_validado = ?<br/>WHERE id = log_id
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
  no se identifica en el directorio (c-82, desde el 13-10-2026, posterior a la campaña
  2026-10), combinado por OR con la condición del clasificador.
- **Etapas del clasificador**: `deterministic` → `gemini` → reserva (error, timeout o guarda de costo).
- **N8N** actúa exclusivamente como orquestador de canales; toda la lógica de clasificación
  y persistencia reside en el backend FastAPI.
