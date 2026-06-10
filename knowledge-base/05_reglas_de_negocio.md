# Reglas de Negocio

Cada regla tiene código único `RN-{DOMINIO}-{NN}`. Fuente: tesis §5.5, §11, Anexo H, y código en `Gestion_Incidentes/app/`.

## Dominio: Clasificación (RN-CL)

- **RN-CL-01**: Todo incidente se clasifica en exactamente uno de tres sectores: `"Sistemas"`, `"Operaciones"`, `"Soporte Técnico"` — strings exactos, case-sensitive, en español.
- **RN-CL-02**: El clasificador es híbrido en 2 etapas: primero el filtro determinístico (regex + diccionarios); si su confianza ≥ **0,90**, se decide sin invocar Gemini. — *Razón: ~62 % de los casos se resuelven sin costo ni latencia de inferencia externa.*
- **RN-CL-03**: Si la etapa determinística no alcanza 0,90, se consulta Gemini 2.5 Flash con prompt estructurado en español rioplatense (`docs/prompt_gemini.txt`), parámetros: temperature 0,3 · top_p 0,9 · max_output_tokens 100 · candidate_count 1 · timeout 10 s.
- **RN-CL-04**: La respuesta de Gemini debe ser JSON estricto con `"categoría"` (uno de los 3 strings) y `"confianza"` (float [0,1]).
- **RN-CL-05**: Si confianza final < **0,70** → `requiere_revision_humana = true` y el caso entra a la cola FIFO de revisión.
- **RN-CL-06**: Ante cualquier fallo (timeout, JSON inválido, categoría desconocida, confianza fuera de rango): etapa = `"fallback"`, confianza = **0,0**, revisión humana obligatoria. Nunca se descarta un incidente por fallo del clasificador.
- **RN-CL-07**: Toda decisión se registra en `clasificacion_log` con etapa, confianza y respuesta cruda — trazabilidad total, sin excepciones.

## Dominio: Validación de respuesta Gemini (RN-VA) — orden obligatorio (Anexo H)

- **RN-VA-01**: Paso 1 — verificar sintaxis JSON (`json.loads()`).
- **RN-VA-02**: Paso 2 — verificar presencia de ambos campos `"categoría"` y `"confianza"`.
- **RN-VA-03**: Paso 3 — verificar que la categoría coincida exactamente con uno de los 3 strings válidos.
- **RN-VA-04**: Paso 4 — verificar que la confianza sea float ∈ [0,0 ; 1,0].
- **RN-VA-05**: Paso 5 — ante cualquier falla: log de la excepción, confianza = 0,0, escalar a revisión humana.

## Dominio: Revisión humana (RN-RH)

- **RN-RH-01**: La cola de revisión contiene registros con `requiere_revision_humana = true` **y** `sector_id_validado IS NULL`.
- **RN-RH-02**: Orden FIFO estricto (created_at ascendente) — ningún incidente espera indefinidamente.
- **RN-RH-03**: La validación humana asigna `sector_id_validado`; el sector debe existir (verificación previa contra catálogo).
- **RN-RH-04**: La validación es el cierre del ciclo: el registro sale de la cola y se convierte en etiqueta de verdad del corpus de evaluación.
- **RN-RH-05**: El sector receptor puede corregir cualquier derivación, no solo las de baja confianza (supervisión humana significativa, §11.5).

## Dominio: Privacidad y datos personales (RN-PR) — Ley 25.326

- **RN-PR-01**: **Pseudonimizar antes de transmitir a Gemini**: nombres propios → `[PERSONA]`, emails → `[EMAIL]`, teléfonos → `[TELEFONO]`, hosts internos → `[HOST]`, identificadores corporativos → etiqueta genérica. Se ejecuta en el módulo Python local, con regex + tests unitarios dedicados. *(Pendiente: change C-03 — governance ALTO.)*
- **RN-PR-02**: Minimización: no almacenar identificadores personales más allá del usuario corporativo; descartar datos incidentales (direcciones, DNI, datos financieros).
- **RN-PR-03**: Finalidad: los datos solo se usan para registro y derivación de incidentes.
- **RN-PR-04**: Retención: 90 días registros operativos · 1 año incidentes resueltos · 30 días logs N8N. Luego anonimizar o eliminar.
- **RN-PR-05**: Derechos ARCO: acceso ≤ 10 días corridos; rectificación/supresión ≤ 5 días corridos.
- **RN-PR-06**: El usuario puede revisar y corregir el contenido del incidente antes de su persistencia definitiva (principio de exactitud).

## Dominio: Registro e identidad (RN-RE)

- **RN-RE-01**: Estructura normalizada de entrada (N8N): identificador único, timestamp con precisión de ms, canal de origen, descripción textual completa.
- **RN-RE-02**: Identificadores de incidente legibles, generados por secuencia con prefijo configurable; se comunican al usuario al registrar.
- **RN-RE-03**: El usuario recibe confirmación post-registro por el canal correspondiente.

## Dominio: Excepciones globales

- **RN-EX-01**: Errores HTTP siguen el cuerpo estándar `{"error": {"code", "message", "details?"}}` (en `core/error_handlers.py`).
- **RN-EX-02**: Timeout o indisponibilidad de Gemini → 503 hacia clientes (N8N puede reintentar con backoff); dentro del pipeline de clasificación se degrada a fallback (RN-CL-06), nunca falla la creación del incidente.
- **RN-EX-03**: Toda respuesta de error debe portar headers CORS (middleware de seguridad `_InternalErrorMiddleware` en `main.py`).
