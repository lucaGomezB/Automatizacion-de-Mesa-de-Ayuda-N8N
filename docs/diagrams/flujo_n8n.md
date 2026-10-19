# Reconstruccion del flujo N8N — Anexo E

Diagrama esquematico reconstruido a partir de la exportacion versionada en
`n8n/workflow.json` (29 nodos operativos). Agrupa los nodos por etapa funcional.

> **Nota sobre el alcance**: no es una captura de la interfaz de N8N. Es una
> reconstruccion derivada del JSON exportado; la disposicion sobre el lienzo de la
> herramienta no coincide necesariamente con la de este esquema. Se mantiene en
> formato Mermaid (texto versionable) en lugar de una imagen binaria, para facilitar
> diffs en revisiones de codigo.

```mermaid
flowchart TB
    subgraph ENTRADA["Etapa 1 - Entrada (triggers)"]
        A1["Llega un email a Mesa de Ayuda"]
        A2["Llamada telefonica (webhook)"]
        A3["Webhook formulario web"]
        A4["notificacion-clasificacion (webhook)"]
    end

    subgraph VALIDACION["Etapa 2 - Validacion y normalizacion"]
        B1["Se verifica que la informacion sea la necesaria"]
        B2["Sellar ingreso telefonia"]
        B3["Marcar canal web"]
        B4["Normalizar entrada del incidente"]
        B5["Entrada valida (IF)"]
    end

    subgraph ENVIO["Etapa 3 - Envio al backend"]
        C1["Login operador"]
        C2["HTTP POST a MESA-AYUDAS"]
    end

    subgraph RUTEO["Etapa 4 - Ruteo por canal de origen"]
        D1["Es correo? (IF)"]
        D2["Es web? (IF)"]
        D3["Rutear por canal de origen (SWITCH)"]
        D4["Web con incidente? (IF)"]
    end

    subgraph REVISION["Etapa 5 - Revision humana"]
        E1["Requiere revision humana (IF)"]
        E2["Preparar destinatarios de revision"]
        E3["Notificar operador designado"]
        E4["Confirmar correo en revision? (IF)"]
        E5["Confirmacion web revision humana"]
        E6["Responder handoff telefonia"]
    end

    subgraph RESPUESTA["Etapa 6 - Respuesta y auditoria"]
        F1["Confirmacion web al usuario"]
        F2["Correo de confirmacion al usuario"]
        F3["Registro de auditoria"]
        F4["Respuesta web de cierre"]
    end

    subgraph POST["Etapa 7 - Aviso post-revision"]
        G1["Auditar notificacion"]
        G2["Es aviso post-revision? (IF)"]
        G3["Preparar destinatarios gestion"]
        G4["Notificar gestion post-revision"]
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
    G2 --> G3
    G2 --> G1
    G3 --> G4
    E4 --> F2
    D4 --> E5
    D4 --> F4
```