## 0. Safety net y preparación

- [x] 0.1 Correr la suite existente y capturar baseline (esperado: 81 passed / 1 skipped). Si algo falla → reportar como falla preexistente, no arreglar.
- [x] 0.2 Crear el helper de carga del workflow en `Gestion_Incidentes/tests/test_n8n_workflow.py`: función que abre `Automatizacion_Mesa_de_Ayuda.json` (ruta anclada a la raíz del repo) y devuelve `nodes` indexados por `type` y por `name`.
- [x] 0.3 Confirmar contra el JSON actual los nombres exactos de los 2 nodos `code`, los 2 `if` y los `httpRequest` (ya inventariados en design.md) para que los tests busquen por `type`/`name`, no por índice.

## 1. Test de ausencia de placeholders (Anexo H — limpieza)

- [x] 1.1 RED: test `test_code_nodes_no_placeholder` que afirma que ningún nodo `code` contiene `myNewField = 1`. Debe fallar contra el JSON actual.
- [x] 1.2 GREEN: reescribir la lógica de ambos nodos `code` en el JSON eliminando el placeholder (lógica real se completa en grupos 3 y 4). Test pasa.
- [x] 1.3 TRIANGULATE: agregar caso que verifica que cada nodo `code` tiene un cuerpo `jsCode` no vacío y con `return`.
- [x] 1.4 REFACTOR: extraer en el test una constante con los nombres de los nodos `code`; correr suite → verde.

## 2. Test de estructura: nodo de normalización (spec: estructura unificada)

- [x] 2.1 RED: test `test_normalizer_node_exists` que afirma la presencia de un nodo de normalización (por `name`) entre los triggers y la clasificación. Falla (no existe).
- [x] 2.2 GREEN: agregar el nodo de normalización al JSON, cableado correo→normalización y telefonía→normalización. Test pasa.
- [x] 2.3 RED: test `test_normalizer_emits_unified_shape` que valida que el `jsCode` del normalizador produce exactamente `id`, `timestamp`, `canal_origen`, `descripcion`. Falla si falta alguno.
- [x] 2.4 GREEN: implementar el `jsCode` de normalización (timestamp ISO-8601 ms; `canal_origen ∈ {correo, web, telefonia}`). Test pasa.
- [x] 2.5 TRIANGULATE: casos por canal — entrada de correo → `canal_origen = "correo"`; entrada telefónica → `canal_origen = "telefonia"`; entrada web simulada → `canal_origen = "web"`.
- [x] 2.6 REFACTOR: limpiar duplicación en los asserts de forma; suite → verde.

## 3. Validación de entrada del canal de correo (spec: validación de correo según Anexo H)

- [x] 3.1 RED: test que afirma que el `jsCode` del nodo `code` de correo valida `descripcion` no vacía y ≥10 caracteres y emite un flag de validez. Falla.
- [x] 3.2 GREEN: implementar la validación de correo en el `jsCode`. Test pasa.
- [x] 3.3 TRIANGULATE: caso válido (≥10 chars → válido) y caso inválido (vacío / <10 chars → inválido + ruteo a pedir datos).
- [x] 3.4 REFACTOR: nombrar claramente el flag de validez; suite → verde.

## 4. Validación de la respuesta de clasificación — 5 pasos Anexo H §H.3 (spec: validación de clasificación)

- [x] 4.1 RED: test que afirma que el `jsCode` del nodo `code` de telefonía parsea JSON y rechaza JSON malformado fijando `confianza = 0.0` + revisión. Falla.
- [x] 4.2 GREEN: implementar parseo JSON + manejo de malformado. Test pasa.
- [x] 4.3 TRIANGULATE: presencia de campos `categoría` y `confianza`; categoría en el set exacto case-sensitive (`"sistemas"` minúscula → rechazo); confianza en `[0.0, 1.0]` (`1.5` → rechazo).
- [x] 4.4 TRIANGULATE: respuesta válida `{"categoría": "Sistemas", "confianza": 0.95}` → aceptada, conserva categoría y confianza.
- [x] 4.5 REFACTOR: factorizar los 5 pasos en una secuencia legible dentro del `jsCode`; suite → verde.

## 5. Ruteo por umbral de confianza en los nodos IF (spec: ruteo por umbral)

- [x] 5.1 RED: test `test_if_nodes_have_conditions` que afirma que ambos nodos `if` tienen al menos una condición no vacía. Falla (condiciones vacías hoy).
- [x] 5.2 GREEN: configurar la condición `confianza >= 0.70` en ambos nodos `if`. Test pasa.
- [x] 5.3 TRIANGULATE: assert de umbral inclusivo (0.70 → rama creación), por encima (0.85 → creación), por debajo (0.60 → revisión humana).
- [x] 5.4 REFACTOR: centralizar el valor del umbral en una constante de test (0.70); suite → verde.

## 6. Persistencia vía backend FastAPI (spec: persistencia + contrato de payload)

- [x] 6.1 RED: test `test_http_node_targets_incidentes_endpoint` que afirma que existe un `httpRequest` cuyo destino contiene `/api/v1/incidentes` con método POST. Falla (hoy apunta a "MTM-SRU" genérico).
- [x] 6.2 GREEN: ajustar el/los nodos `httpRequest` de persistencia a `POST /api/v1/incidentes`. Test pasa.
- [x] 6.3 RED: test `test_http_payload_matches_incidente_create` que valida que el cuerpo enviado contiene `descripcion` y `prioridad` y NO contiene campos ajenos al schema `IncidenteCreate`. Falla.
- [x] 6.4 GREEN: mapear la estructura unificada al payload `IncidenteCreate` en el nodo previo al HTTP. Test pasa.
- [x] 6.5 TRIANGULATE: caso de `descripcion` en límites (10 y 5000 chars) válido; payload sin campos extra.
- [x] 6.6 REFACTOR: documentar en comentario del `jsCode` el mapeo unificado→IncidenteCreate; suite → verde.

## 7. Garantía de pseudonimización en tránsito (spec: descripción pseudonimizada)

- [x] 7.1 Verificar (lectura, no edición de backend) en qué punto se pseudonimiza la descripción; si la PII llega en claro a N8N→backend, registrar el hallazgo en design.md (Open Questions) y elevar — NO resolver en C-04.
- [x] 7.2 RED: test `test_payload_has_no_obvious_pii` que, sobre un caso simulado con email/teléfono, afirma que el `descripcion` mapeado no contiene la PII en claro. Falla si el flujo la deja pasar.
- [x] 7.3 GREEN: asegurar que el flujo no emita PII en claro en `descripcion` (según la decisión confirmada en 7.1: pseudonimización aguas arriba o delegada al backend). Test pasa o queda `xfail` documentado con el gap si la pseudonimización es responsabilidad confirmada del backend.
- [x] 7.4 REFACTOR: documentar la decisión final de pseudonimización en la guía; suite → verde.

## 8. Verificación funcional manual (entorno de pruebas)

- [x] 8.1 Importar `Automatizacion_Mesa_de_Ayuda.json` en una instancia N8N 1.62 de pruebas (Docker), con el backend FastAPI + PostgreSQL levantados.
  <!-- Verificado 2026-06-11: docker-compose.yml (raíz) levanta postgres:15.5+redis:7.2+backend FastAPI+n8n:latest. `n8n import:workflow` OK: 1 workflow importado, 17 nodos, active=false. Alcance: n8n:latest ya que 1.62.0 no está en Docker Hub. Triggers Outlook/Twilio no activos (C-05). -->
- [x] 8.2 Ejecutar un caso de correo de prueba y observar `201 Created` del backend con incidente clasificado.
  <!-- Verificado 2026-06-11: POST /api/v1/incidentes con payload correo → 201 Created, incidente id=1, sector=Sistemas, confianza=0.9999 (deterministic), requiere_revision_humana=false. Persistido en PostgreSQL (tabla incidente). -->
- [x] 8.3 Ejecutar un caso de telefonía de prueba (transcripción simulada) y observar el ruteo correcto por confianza.
  <!-- Verificado 2026-06-11: 3 payloads ejecutados: (1) Sistemas confianza=0.9999→créación directa, (2) Operaciones confianza=0.9999→creación directa, (3) Soporte Técnico det_confianza=0.667→Gemini escalado→fallback (API key revocada)→confianza=0.0→requiere_revision_humana=true. Ruteo IF correcto. GEMINI_API_KEY del .env reportada como leaked: el fallback funciona según spec pero la API key necesita renovación para validar el path Gemini completo. -->
- [x] 8.4 Confirmar que `active` permanece en `false` en el JSON versionado (no se activa en producción).
- [x] 8.5 Registrar los resultados de la verificación manual en la guía.

## 9. Documentación

- [x] 9.1 Crear `docs/n8n-workflow-guide.md`: descripción de cada nodo, el contrato `POST /api/v1/incidentes`, la discrepancia tesis(2 endpoints) vs implementación(1 endpoint) y cómo importar/probar el flujo.
- [x] 9.2 Documentar la decisión de pseudonimización (dónde ocurre) y el ruteo por umbral 0.70.
- [x] 9.3 Anotar las Open Questions resueltas durante el apply (endpoint, pseudonimización, ruteo workflow vs backend) para alimentar el Anexo E de la tesis (C-10).

## 10. Cierre

- [x] 10.1 Correr la suite completa: todos los tests nuevos verdes + baseline sin regresiones (≥ 81 passed previos + nuevos).
- [x] 10.2 `openspec validate --strict` del change sin errores.
- [x] 10.3 Elevar al usuario las decisiones de governance MEDIO pendientes de confirmación (Decisión 1 y 2 de design.md) antes de archivar.
