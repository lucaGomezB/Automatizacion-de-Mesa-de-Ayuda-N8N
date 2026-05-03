# Parámetros de Configuración: Gemini 2.5 Flash

## Invocación de API

Versión de cliente: `google-generativeai >= 0.8`

```python
import google.generativeai as genai

model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content(
    prompt + descripcion_incidente,
    generation_config=genai.types.GenerationConfig(
        temperature=0.3,
        top_p=0.9,
        max_output_tokens=100,
        candidate_count=1,
    ),
    safety_settings=[{
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    }],
    request_options={"timeout": 10}
)
```

## Justificación de Parámetros

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| temperature | 0.3 | Reduce variabilidad; mejora consistencia en clasificación determinística |
| top_p | 0.9 | Nucleus sampling permite variantes léxicas rioplatenses |
| max_tokens | 100 | Suficiente para JSON (~15 tokens) + margen de error |
| candidate_count | 1 | Única respuesta candidata; optimiza latencia |
| safety_settings | BLOCK_NONE para HARASSMENT | Permite descripciones de incidentes (ej. "se cayó", "atasco") |
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

- v1.0 (Mar 2026): Parámetros iniciales validados con corpus de 200 casos