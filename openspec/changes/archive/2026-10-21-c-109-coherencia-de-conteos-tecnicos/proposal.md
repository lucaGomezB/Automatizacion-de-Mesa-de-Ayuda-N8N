## Why

El dictamen CONEAU 2026-10-20 (recomendación obligatoria 6) detectó cuatro
discrepancias internas de conteo y de nombre en la tesis v9: "seis" frente a
"siete" entidades, "cinco" frente a "siete" etapas del flujo, "26 operativos más
3 notas" frente a "29 operativos", y `google-genai` frente a
`google-generativeai`. Son contradicciones internas verificables por un jurado
adversarial y deben cerrarse antes de la defensa. El cambio PRIMERO fija el
conteo verdadero desde el código y la configuración, y DESPUÉS alinea el texto.

## What Changes

- **Fijar los conteos verdaderos desde el sistema (fuente de verdad).**
  - Entidades principales del modelo de datos: **siete** (Tabla `tab:entidades`
    y diagrama ER; el ORM confirma `directorio_empleado`).
  - Etapas funcionales del flujo N8N: **siete** (agrupación derivada de
    `n8n/workflow.json`).
  - Nodos del flujo: **29 operativos + 3 notas adhesivas = 32 totales**
    (`n8n/workflow.json`).
  - Paquete del SDK de Google: **`google-genai`** (SDK unificado,
    `App/Backend/requirements.txt`); `google-generativeai` es el SDK deprecado y
    MUST NOT citarse como el usado.
- **Alinear el texto** de `05-arquitectura.tex`, `06-implementacion.tex` y
  `12-anexos.tex` (y las tablas afectadas) a esos conteos únicos.
- **Registrar el conteo canónico** en `docs/Tesis/Correcciones/` para que las
  ramas posteriores no vuelvan a divergir.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `tesis-document`: se agregan requisitos de coherencia de los conteos técnicos
  internos (entidades, etapas y nodos del flujo) y del nombre canónico del SDK de
  Google, con sus escenarios de verificación sobre el PDF compilado.

## Impact

- **Documento**: `docs/Tesis/v9 (IA)/paper/sections/05-arquitectura.tex`
  (`siete entidades`, `google-genai`), `06-implementacion.tex` (entidades,
  etapas, nodos, SDK), `12-anexos.tex` (etapas, nodos, SDK).
- **Sin cambios de código**: solo se lee el sistema como fuente de verdad.
- **Compilación**: `main.pdf` debe seguir compilando (103 páginas, ±0) con la
  imagen `texlive-thesis`.
- **Dependencia de secuencia**: comparte archivos con las ramas de contenido de
  la tesis (c-104/c-105/c-106/c-107/c-108/c-110); ver `design.md`.
