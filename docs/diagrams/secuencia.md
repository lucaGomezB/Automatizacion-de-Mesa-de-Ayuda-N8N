# Diagrama de Secuencia — Flujo Extremo a Extremo de un Incidente

Ilustra el flujo completo desde la recepción del incidente en un canal de entrada
hasta la confirmación al usuario o la derivación a revisión humana.

```mermaid
sequenceDiagram
    autonumber

    participant Canal as Canal de Entrada<br/>(Outlook / Twilio)
    participant N8N as N8N Workflow
    participant BE as Backend FastAPI<br/>POST /api/v1/incidentes
    participant CLAS as Clasificador Híbrido<br/>(determinístico + Gemini)
    participant PG as PostgreSQL<br/>(incidente + clasificacion_log)
    participant GEMINI as Google Gemini API
    participant OP as Operador Humano<br/>PATCH /clasificaciones/{id}/validar

    %% ── Ingreso del incidente ──────────────────────────────────────────────
    Canal->>N8N: Evento (correo / transcripción de llamada)
    Note over N8N: Valida campos requeridos.<br/>Si faltan datos, solicita reintento.
    N8N->>BE: POST /api/v1/incidentes<br/>{ descripcion, prioridad, canal_origen_id }

    %% ── Pipeline de clasificación ──────────────────────────────────────────
    BE->>BE: Pseudonimizar descripción<br/>[EMAIL]/[TELEFONO]/[HOST]/[PERSONA]
    BE->>CLAS: clasificar(descripcion_pseudonimizada)

    alt Filtro determinístico alcanza confianza ≥ 0.90
        CLAS-->>BE: { categoria, confianza, etapa="deterministic" }
    else Gemini requerido
        CLAS->>GEMINI: Prompt con descripción pseudonimizada
        GEMINI-->>CLAS: JSON { "categoría": "...", "confianza": 0.xx }
        Note over CLAS: Valida JSON: campos, categoría exacta,<br/>confianza en [0.0, 1.0].
        CLAS-->>BE: { categoria, confianza, etapa="gemini" }
    end

    %% ── Persistencia ───────────────────────────────────────────────────────
    BE->>PG: INSERT incidente (descripcion_original cifrada,<br/>descripcion_pseudonimizada, sector_id, estado="nuevo")
    BE->>PG: INSERT clasificacion_log (incidente_id, sector_id_predicho,<br/>confianza, etapa, requiere_revision_humana)

    %% ── Respuesta al canal ─────────────────────────────────────────────────
    alt Confianza ≥ 0.70
        BE-->>N8N: HTTP 201 { incidente_id, sector, confianza, requiere_revision_humana=false }
        N8N-->>Canal: Confirmación: incidente #{id} asignado a {sector}
    else Confianza < 0.70 o fallo de Gemini
        BE-->>N8N: HTTP 201 { incidente_id, sector=null, requiere_revision_humana=true }
        N8N-->>Canal: Aviso: incidente #{id} derivado a revisión humana
    end

    %% ── Ciclo de revisión humana (cuando aplica) ───────────────────────────
    opt Revisión humana pendiente
        OP->>BE: GET /api/v1/clasificaciones/revision-pendiente
        BE-->>OP: [ { log_id, incidente_id, descripcion_pseudonimizada, ... } ]
        OP->>BE: PATCH /api/v1/clasificaciones/{log_id}/validar<br/>{ sector_id_validado }
        BE->>PG: UPDATE clasificacion_log SET sector_id_validado = ?<br/>WHERE id = log_id
        BE-->>OP: HTTP 200 { log actualizado }
        Note over PG: El log validado pasa a formar parte<br/>del corpus de evaluación etiquetado.
    end
```

## Notas

- **Doble representación**: `descripcion_original` se cifra at-rest con Fernet (Ley 25.326);
  `descripcion_pseudonimizada` es la única que consume el clasificador y la API.
- **Umbral de confianza**: ≥ 0.70 para clasificación automática; < 0.70 deriva a revisión humana.
- **Etapas del clasificador**: `deterministic` (reglas, umbral ≥ 0.90) → `gemini` (LLM) → `fallback` (error).
- **N8N** actúa exclusivamente como orquestador de canales; toda la lógica de clasificación
  y persistencia reside en el backend FastAPI.
