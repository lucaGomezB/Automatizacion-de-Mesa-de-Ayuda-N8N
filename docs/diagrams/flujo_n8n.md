# Reconstruccion del flujo N8N — Anexo E

Diagrama esquematico reconstruido a partir de la exportacion versionada en
`n8n/workflow.json` (29 nodos operativos). Agrupa los nodos por etapa funcional.

> **Nota sobre el alcance**: no es una captura de la interfaz de N8N. Es una
> reconstruccion derivada del JSON exportado; la disposicion sobre el lienzo de la
> herramienta no coincide necesariamente con la de este esquema. Se mantiene en
> formato Mermaid (texto versionable) en lugar de una imagen binaria, para facilitar
> diffs en revisiones de codigo.

> **Figura dividida en tres partes** (observación N-11 del tribunal). La parte A abarca las
> etapas 1 a 3 (entrada, validación y envío al backend); la parte B, las etapas 4 a 6 (ruteo,
> revisión humana y respuesta); la parte C, la etapa 7 (aviso post-revisión). Los nodos de la
> sección «ver parte X» repiten, como referencia, nodos que se definen en otra parte; las
> conexiones entre partes se conservan.

### Parte A — Etapas 1 a 3

```mermaid
%%{init: {"fontFamily":"Arial, Helvetica, sans-serif","themeVariables":{"fontFamily":"Arial, Helvetica, sans-serif","fontSize":"16px"},"flowchart":{"useMaxWidth":false,"nodeSpacing":20,"rankSpacing":35,"padding":6,"wrappingWidth":170}}}%%
flowchart TB
    subgraph ENTRADA["Etapa 1 - Entrada (triggers)"]
        A1["Llega un email a Mesa de Ayuda"]
        A2["Llamada telefónica (webhook)"]
        A3["Webhook formulario web"]
        A4["notificación-clasificación (webhook)"]
    end

    subgraph VALIDACION["Etapa 2 - Validación y normalización"]
        B1["Se verifica que la información sea la necesaria"]
        B2["Sellar ingreso telefonía"]
        B3["Marcar canal web"]
        B4["Normalizar entrada del incidente"]
        B5["Entrada válida (IF)"]
    end

    subgraph ENVIO["Etapa 3 - Envío al backend"]
        C1["Login operador"]
        C2["HTTP POST a MESA-AYUDAS"]
    end

    subgraph SIGUE["Etapas 4 a 7 (ver partes B y C)"]
        D1["Es correo? (IF)"]
        E1["Requiere revision humana (IF)"]
        E6["Responder handoff telefonía"]
        F3["Registro de auditoría"]
        G2["Es aviso post-revisión? (IF)"]
    end

    A1 --> B1
    B1 --> B4
    B4 --> B5
    A2 --> B2
    A2 --> E6
    B2 --> B4
    A3 --> B3
    B3 --> B4
    A4 --> G2
    B5 --> C1
    B5 --> F3
    B5 --> D1
    C1 --> C2
    C2 --> E1
    C2 --> D1
    C2 --> F3

    G2 ~~~ D1
    F3 ~~~ E6
```

### Parte B — Etapas 4 a 6

```mermaid
%%{init: {"fontFamily":"Arial, Helvetica, sans-serif","themeVariables":{"fontFamily":"Arial, Helvetica, sans-serif","fontSize":"16px"},"flowchart":{"useMaxWidth":false,"nodeSpacing":20,"rankSpacing":35,"padding":6,"wrappingWidth":170}}}%%
flowchart TB
    subgraph PREV["Etapas 1 a 3 (ver parte A)"]
        A2["Llamada telefónica (webhook)"]
        B5["Entrada válida (IF)"]
        C2["HTTP POST a MESA-AYUDAS"]
    end

    subgraph RUTEO["Etapa 4 - Ruteo por canal de origen"]
        D1["Es correo? (IF)"]
        D2["Es web? (IF)"]
        D3["Rutear por canal de origen (SWITCH)"]
        D4["Web con incidente? (IF)"]
    end

    subgraph REVISION["Etapa 5 - Revisión humana"]
        E1["Requiere revision humana (IF)"]
        E2["Preparar destinatarios de revision"]
        E3["Notificar operador designado"]
        E4["Confirmar correo en revision? (IF)"]
        E5["Confirmación web revisión humana"]
        E6["Responder handoff telefonía"]
    end

    subgraph RESPUESTA["Etapa 6 - Respuesta y auditoría"]
        F1["Confirmacion web al usuario"]
        F2["Correo de confirmación al usuario"]
        F3["Registro de auditoría"]
        F4["Respuesta web de cierre"]
    end


    A2 --> E6
    B5 --> F3
    B5 --> D1
    C2 --> E1
    C2 --> D1
    C2 --> F3
    E1 --> E2
    E1 --> F3
    E1 --> D1
    E1 --> E4
    E1 --> D3
    E2 --> E3
    D3 --> F1
    D3 --> F2
    D1 --> D2
    D2 --> D4
    E4 --> F2
    D4 --> E5
    D4 --> F4
```

### Parte C — Etapa 7

```mermaid
%%{init: {"fontFamily":"Arial, Helvetica, sans-serif","themeVariables":{"fontFamily":"Arial, Helvetica, sans-serif","fontSize":"16px"},"flowchart":{"useMaxWidth":false,"nodeSpacing":20,"rankSpacing":35,"padding":6,"wrappingWidth":170}}}%%
flowchart TB
    subgraph PREV["Etapa 1 (ver parte A)"]
        A4["notificación-clasificación (webhook)"]
    end

    subgraph POST["Etapa 7 - Aviso post-revisión"]
        G1["Auditar notificación"]
        G2["Es aviso post-revisión? (IF)"]
        G3["Preparar destinatarios gestión"]
        G4["Notificar gestión post-revisión"]
    end

    A4 --> G2
    G2 --> G3
    G2 --> G1
    G3 --> G4
```