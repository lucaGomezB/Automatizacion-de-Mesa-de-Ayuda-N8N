## Context

Ver `proposal.md — Why`. Restricciones que moldean el enfoque:

- Change de documentación únicamente: sin tocar código de producción, scripts, `n8n/workflow.json` ni `docs/Tesis/**`.
- Strict TDD activo: red de seguridad estructural primero (RED), luego la edición de docs (GREEN).
- c-42 dejó el precedente y el patrón: `App/Backend/tests/test_docs_bootstrap_sync.py`, con lectura de docs por path relativo a la raíz (`Path(__file__).resolve().parents[3]`) y asserts sobre tokens estables.
- El requisito que gobierna estos documentos es `project-documentation` (`openspec/specs/project-documentation/spec.md`), cuyos requisitos "Anexo G — Guía operativa" y "README de despliegue local reproducible" se MODIFICAN y al que se le AGREGA "Consistencia de rutas post-reestructuracion".

Estructura real verificada en el repo (no asumida): `App/Backend/scripts/export_openapi.py` y `App/Backend/requirements.txt` existen; `evaluation/run_evaluation.py` espera que `PYTHONPATH` incluya `App/Backend/`. Inventario de ocurrencias obsoletas confirmado por grep en `docs/operational-guide.md` (43, 46, 372, 383), `docs/troubleshooting.md` (25, 27, 85, 152), `docs/como_cargar_datos_corpus.md` (189), `docs/diagrams/componentes.md` (3), `docs/parameters_gemini.md` (59), `docs/pseudonymization.md` (4), `docs/anexo_c_esquema_bd.md` (4, 5) y `docs/security-hardening.md` (179).

## Goals / Non-Goals

**Goals:**

- Corregir las rutas obsoletas a `App/Backend/` en los documentos vigentes, verificando cada destino contra el repo real.
- Completar la documentación de variables de entorno con `JWT_SECRET_KEY` en `README.md` y en `docs/operational-guide.md` sección 1.2.
- Dejar una red de seguridad que falle si la documentación vuelve a desincronizarse.

**Non-Goals:**

- No se reescribe la prosa completa de los documentos: se intervienen únicamente las líneas/rutas y bloques identificados.
- No se corrige el docstring de `App/Backend/scripts/export_openapi.py` (es un script, fuera de alcance), aunque contenga la ruta antigua.
- No se toca `docs/Tesis/**` ni se reescribe la narrativa histórica de `docs/security-hardening.md`.

## Decisions

### D1 — Módulo de test nuevo, `App/Backend/tests/test_docs_restructure_sync.py`

**Decisión:** crear un módulo nuevo que cubra esta sincronía, en lugar de diluir los casos en `test_docs_bootstrap_sync.py`.

**Rationale:** c-42 cubre el contrato de bootstrap (env preflight, gate de costo); este change cubre reestructuración de rutas y una omisión de variable. Mantener los módulos separados por intención preserva la trazabilidad de cada change y evita acoplar dos concerns. El nuevo módulo reutiliza el mismo patrón (`parents[3]`, helper de lectura, asserts por tokens).

**Alternativas consideradas:** extender `test_docs_bootstrap_sync.py` — mezcla dos changes en un módulo y dificulta el rollback selectivo.

### D2 — Asserts sobre tokens estables y control negativo del token obsoleto

**Decisión:** el test asserta presencia de `JWT_SECRET_KEY` (README y guía 1.2), presencia de `App/Backend/` en los documentos corregidos, y un control negativo que verifica que el conjunto de documentos en alcance ya NO contiene `Gestion_Incidentes/`. `docs/security-hardening.md` queda excluido del control negativo y se verifica por su anotación histórica.

**Rationale:** tokens que las specs ya nombran y que no deberían cambiar; un assert sobre oraciones completas convierte cualquier mejora de redacción en falso rojo. El control negativo es la garantía real de no regresión de la deuda.

**Alternativas consideradas:** snapshot del archivo entero — frágil y no expresa intención.

### D3 — Verificar cada reemplazo contra el repo antes de aplicarlo

**Decisión:** antes de sustituir, comprobar el destino real: `App/Backend/.env.example`, `App/Backend/requirements.txt`, `App/Backend/scripts/export_openapi.py` y `PYTHONPATH=App/Backend` para la evaluación. En particular, la línea 372 de la guía (`cd Gestion_Incidentes` para regenerar OpenAPI) pasa a `cd App/Backend`, y la línea 189 del corpus pasa a `PYTHONPATH=App/Backend`.

**Rationale:** un reemplazo ciego `Gestion_Incidentes/` → `App/Backend/` es correcto en la mayoría de los casos, pero asumir el resultado de un comando (`cd` + `python scripts/...`) sin verificar introduce el riesgo de documentar una ruta que no resuelve.

**Alternativas consideradas:** reemplazo global por sed — rechazado por el riesgo de tocar la narrativa histórica y la tesis.

### D4 — La narrativa histórica se anota, no se reescribe

**Decisión:** en `docs/security-hardening.md` línea 179 se conserva el hecho (el archivo estaba en `Gestion_Incidentes/.env`) y se agrega una aclaración parentética de que hoy el módulo vive en `App/Backend/`.

**Rationale:** el token allí es un hecho histórico verificado (blob y commits citados). Reescribirlo falsearía la evidencia. La spec nueva permite explícitamente la retención con anotación histórica.

**Alternativas consideradas:** reemplazar el token — borra un hecho documentado; dejarlo sin anotar — mantiene la ambigüedad que este change corrige.

### D5 — `JWT_SECRET_KEY` documentada como clave de firma HS256

**Decisión:** en ambos documentos se describe `JWT_SECRET_KEY` como la clave de firma HS256 y se incluye como generarla con `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

**Rationale:** el preflight ya la exige; documentarla con el mismo nivel de detalle que las demás variables mantiene la consistencia interna. La descripción concuerda con el uso real (HS256).

**Alternativas consideradas:** documentar solo el nombre sin comando de generación — deja al operador sin camino accionable.

## Risks / Trade-offs

- [Reemplazo que apunta a una ruta inexistente] → Tarea explícita de verificación contra el repo real antes de editar (D3).
- [Borrar el hecho histórico] → `security-hardening.md` se excluye del control negativo y se verifica por su anotación (D4).
- [Test acoplado a prosa] → Asserts solo sobre tokens estables; documentado en el docstring del test (D2).
- [Desliz de alcance hacia tesis] → Control negativo excluye `docs/Tesis/**`; declarado en Non-Goals.

## Migration Plan

Documentación y test; sin migración de datos ni esquema. Rollback: revertir el commit (borra el test y restaura los documentos). No hay estado de runtime que restaurar.

## Open Questions

- El docstring de `App/Backend/scripts/export_openapi.py` también usa `Gestion_Incidentes` en su ejemplo de uso, pero es un script y queda fuera de alcance por la restricción del change. Se registra como observación para un change futuro de scripts si corresponde.
- Queda por confirmar en el apply si `docs/diagrams/componentes.md` u otros requieren además ajustar texto circundante (no solo el token de ruta); el apply lo verificará leyendo cada línea.