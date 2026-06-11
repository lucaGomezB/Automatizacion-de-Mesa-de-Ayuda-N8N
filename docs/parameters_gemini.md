# Parámetros de Configuración: Gemini 2.5 Flash

## Invocación de API

Versión de cliente: `google-genai >= 1.0` (SDK nuevo; reemplaza al deprecado `google-generativeai`)

```python
import asyncio

from google import genai
from google.genai import types as genai_types

client = genai.Client(api_key=GEMINI_API_KEY)

config = genai_types.GenerateContentConfig(
    temperature=0.3,
    top_p=0.9,
    max_output_tokens=100,
    candidate_count=1,
    response_mime_type="application/json",
    thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
    safety_settings=[
        genai_types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
        genai_types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
        genai_types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
        genai_types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
    ],
)

response = await asyncio.wait_for(
    client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt + descripcion_incidente,
        config=config,
    ),
    timeout=10,
)
```

> Implementación real: `Gestion_Incidentes/app/classifiers/gemini_classifier.py`.
> El timeout se garantiza con `asyncio.wait_for` (el SDK nuevo no acepta
> `request_options={"timeout": ...}` por llamada); `TimeoutError` activa el fallback.

## Justificación de Parámetros

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| temperature | 0.3 | Reduce variabilidad; mejora consistencia en clasificación determinística |
| top_p | 0.9 | Nucleus sampling permite variantes léxicas rioplatenses |
| max_tokens | 100 | Suficiente para JSON (~15 tokens) + margen de error |
| candidate_count | 1 | Única respuesta candidata; optimiza latencia |
| response_mime_type | application/json | Modo JSON de la API: impide fences Markdown (```json) que el validador del Anexo H rechaza |
| thinking_config | thinking_budget=0 | Gemini 2.5 Flash razona por defecto y esos tokens cuentan contra max_output_tokens, truncando el JSON; presupuesto 0 = respuesta directa y menor latencia |
| safety_settings | BLOCK_NONE en las 4 categorías de daño | Permite terminología técnica de incidentes (ej. "se cayó", "atasco", "corte de red") |
| timeout | 10s | Límite máximo; fallback a revisión humana si excede |

## Validación de Respuesta

La respuesta DEBE:
1. Ser JSON válido (`json.loads()` sin error)
2. Contener exactamente dos claves: `"categoría"` y `"confianza"`
3. `"categoría"` debe ser string en `{Sistemas, Operaciones, Soporte Técnico}`
4. `"confianza"` debe ser número en [0.0, 1.0]

Si FALLA cualquier validación:
- Registrar excepción
- Asignar confianza = 0.0
- Marcar incidente para revisión humana

## Calibración y Ajuste

El umbral de 0.7 para activar revisión humana fue determinado empíricamente.
Para futuras iteraciones, considerar:
- Curva de calibración (confianza reportada vs exactitud real)
- Análisis de distribución de confianzas
- Ajuste de umbral si cambia versión del modelo

## Historial de Cambios

- v1.2 (Jun 2026): `response_mime_type="application/json"` + `thinking_budget=0`. Causa: en verificación funcional, Gemini 2.5 Flash devolvió solo "```json" (truncado por tokens de thinking dentro de max_output_tokens=100 + fence Markdown), forzando fallback con confianza=0.0. Parámetros calibrados sin cambios.
- v1.1 (Jun 2026): Migración al SDK `google-genai` (cliente async `client.aio`, timeout vía `asyncio.wait_for`). Parámetros de inferencia sin cambios.
- v1.0 (Mar 2026): Parámetros iniciales validados con corpus de 200 casos