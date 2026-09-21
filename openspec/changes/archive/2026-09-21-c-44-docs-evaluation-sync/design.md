## Context

Ver `proposal.md — Why`. Restricciones que moldean el enfoque:

- Change mayoritariamente documental mas una correccion puntual de script; sin cambios de runtime, esquema ni infraestructura.
- Strict TDD activo: primero la red de seguridad (RED), luego la correccion de docs y script (GREEN). El bug del script se reproduce con un test funcional real.
- Precedente de patron: `App/Backend/tests/test_docs_bootstrap_sync.py` y `test_docs_restructure_sync.py`, con lectura de documentos por path relativo a la raiz (`Path(__file__).resolve().parents[3]`), helper de seccion por encabezado y asserts sobre tokens estables.
- El script `App/Backend/scripts/export_openapi.py` setea su propio `sys.path` y sus dummies ANTES de importar `app.config.settings`; por eso el bug solo se reproduce de forma fiable en un subproceso con el entorno depurado.
- Los requisitos que gobiernan son `project-documentation` (requisitos "Especificación OpenAPI 3.1 estática generada desde la app" y "Anexo G — Guía operativa") y `evaluation-framework` (requisito "Runner de evaluación sobre el corpus").

Hechos verificados en el repo (no asumidos): `evaluation/generate_corpus.py` no existe; `docs/operational-guide.md` §8.1 usa `cd evaluation; python run_evaluation.py` y §8.3 invoca el generador inexistente; `evaluation/README.md:70-75` y `docs/como_cargar_datos_corpus.md:189` documentan la invocacion correcta `PYTHONPATH=App/Backend python -m evaluation.run_evaluation`; `evaluation/run_evaluation.py` define `CONFIRM_PAID_ENV_VAR = "EVALUATION_CONFIRM_PAID"`, lanza `PaidRunNotConfirmedError` y sale con codigo 2; `App/Backend/app/config/settings.py:116` exige `jwt_secret_key` sin default; los `_DUMMIES` del script no lo incluyen; `.github/workflows/ci.yml:47` define `JWT_SECRET_KEY` y por eso CI no detecta el bug.

## Goals / Non-Goals

**Goals:**

- Corregir la seccion 8 de la guia operativa para que su comando funcione y su procedimiento de corpus sea real.
- Documentar el gate de corrida paga en los dos lugares donde vive el flujo: guia operativa §8 y `evaluation/README.md`.
- Hacer que `export_openapi.py` corra en un entorno limpio y que su docstring deje de mentir sobre rutas y ejemplo de salida.
- Dejar una red de seguridad que falle si la documentacion o el script vuelven a desincronizarse.

**Non-Goals:**

- No se modifica la logica del gate de corrida paga: se documenta su comportamiento existente.
- No se toca `docs/anexo_f_corpus.md` (registra la eliminacion del corpus sintetico como historia correcta) ni `docs/Tesis/**`.
- No se toca §9 (dry-run), que ya esta correcto.
- No se agregan ni modifican scripts distintos de `export_openapi.py`.

## Decisions

### D1 — Modulo de test nuevo, `App/Backend/tests/test_docs_evaluation_sync.py`

**Decision:** crear un modulo nuevo para esta sincronia en lugar de diluir los casos en los modulos de c-42/c-43.

**Rationale:** c-42 cubre el contrato de bootstrap y c-43 la reestructuracion de rutas; este change cubre la sincronia del flujo de evaluacion y del script OpenAPI. Separar por intencion preserva la trazabilidad y el rollback selectivo. El nuevo modulo reutiliza el mismo patron (`parents[3]`, helper de lectura, helper de seccion por encabezado, asserts por tokens).

**Alternativas consideradas:** extender `test_docs_restructure_sync.py` — mezcla concerns y complica el rollback de c-44.

### D2 — Asserts estructurales sobre tokens estables y control negativo

**Decision:** los tests estructurales assertan presencia de `PYTHONPATH=App/Backend python -m evaluation.run_evaluation`, ausencia de `generate_corpus.py`, presencia de `confirm-paid` y `EVALUATION_CONFIRM_PAID` en guia y README, presencia de `JWT_SECRET_KEY` en `_DUMMIES` del script, y ausencia de `Gestion_Incidentes` en el script.

**Rationale:** tokens que las specs ya nombran y que no deberian cambiar; un assert sobre oraciones convierte cualquier mejora de redaccion en falso rojo. La seccion 8 se aisla por su encabezado para no pasar de forma trivial por otras menciones del documento.

**Alternativas consideradas:** snapshot de archivos completos — fragil y no expresa intencion.

### D3 — Test funcional del script por subproceso con entorno depurado

**Decision:** el test funcional ejecuta `App/Backend/scripts/export_openapi.py` en un subproceso con `JWT_SECRET_KEY` eliminado del entorno y `cwd` en un directorio temporal sin `.env` descubrible, con `--output` a un archivo temporal, y exige exit code 0 y JSON OpenAPI 3.1 valido con `paths` no vacio.

**Rationale:** el script setea sus dummies y su `sys.path` internamente antes del import, por lo que un import in-process no reproduce el fallo de `Settings` de forma fiable; un subproceso con entorno controlado es la unica via determinista. Es el RED real del bug: antes de agregar `JWT_SECRET_KEY` a `_DUMMIES`, el script falla con un error de validacion de `Settings`.

**Alternativas consideradas:** importar `generate_schema()` in-process con `monkeypatch.delenv` — pydantic-settings puede leer un `.env` del repo y enmascarar el fallo; ademas el modulo ya habria cacheado `Settings`. El subproceso evita ambas fugas.

### D4 — §8.3 se elimina y se reemplaza por un puntero al procedimiento real

**Decision:** eliminar la subseccion "Regenerar el corpus calibrado" y su comando inexistente, y reemplazarla por un puntero a `docs/como_cargar_datos_corpus.md`, que documenta como construir y colocar el corpus real.

**Rationale:** `evaluation/generate_corpus.py` fue eliminado permanentemente por C-27; conservar el comando documenta una capacidad inexistente. El procedimiento real ya esta escrito en `docs/como_cargar_datos_corpus.md`; duplicarlo en la guia crearia otra fuente de drift.

**Alternativas consideradas:** reescribir §8.3 con un generador nuevo — fuera de alcance (no se agregan scripts) y contrario a la decision de descartar el corpus sintetico.

### D5 — El gate de corrida paga se documenta en la guia y en el README de evaluacion

**Decision:** documentar `--confirm-paid` / `EVALUATION_CONFIRM_PAID=1`, el aborto con codigo 2 y la estimacion de costo tanto en `docs/operational-guide.md` §8 como en `evaluation/README.md`, junto al comando de corrida y a la configuracion de `GEMINI_API_KEY`.

**Rationale:** el README es la referencia operativa del framework y la guia es el documento operativo del proyecto; un operador puede llegar por cualquiera de los dos. El requisito de `project-documentation` cubre la guia y el de `evaluation-framework` cubre el README, sin duplicar el texto normativo.

**Alternativas consideradas:** documentarlo solo en el README — la guia quedaria ordenando una corrida paga sin advertir el gate.

### D6 — `JWT_SECRET_KEY` se agrega a los dummies con un valor dummy estable

**Decision:** agregar `JWT_SECRET_KEY` a `_DUMMIES` con un valor dummy (suficiente para instanciar `Settings`, sin ser un secreto real), en linea con el patron de CI.

**Rationale:** `Settings.jwt_secret_key` no tiene default; sin el dummy el script no puede instanciar la configuracion en un entorno limpio. El valor es irrelevante para exportar el esquema, que no firma tokens.

**Alternativas consideradas:** dar un default a `jwt_secret_key` en `Settings` — cambia codigo de produccion y debilita una guarda de seguridad; fuera de alcance.

### D7 — El docstring se corrige, no se reescribe

**Decision:** en `export_openapi.py` se corrigen las rutas `Gestion_Incidentes` → `App/Backend`, el ejemplo de `--output` (`../docs/openapi.json` → `../../docs/openapi.json`, consistente con el default real) y el comentario del `sys.path`; no se reescribe el resto del docstring.

**Rationale:** el resto del docstring (nota de versiones pinadas, comportamiento del import) es correcto y valioso. Intervenir solo las lineas erroneas minimiza el diff.

**Alternativas consideradas:** reescribir el docstring completo — diff innecesario y riesgo de perder advertencias utiles.

## Risks / Trade-offs

- [El test funcional descubre un `.env` del repo y enmascara el bug] → se corre en subproceso con `cwd` en directorio temporal y entorno depurado (D3).
- [Test estructural acoplado a prosa] → asserts solo sobre tokens estables; documentado en el docstring del modulo (D2).
- [Duplicar el procedimiento de corpus en la guia] → §8.3 apunta a `docs/como_cargar_datos_corpus.md` en lugar de reescribirlo (D4).
- [Desliz de alcance hacia `docs/anexo_f_corpus.md`] → declarado fuera de alcance en Non-Goals y en el control negativo del test.
- [El test funcional depende de las versiones pinadas de fastapi/pydantic] → el propio script ya advierte sobre el skew; el test solo valida `openapi` 3.1 y `paths` no vacio, no la igualdad byte a byte con `docs/openapi.json`.

## Migration Plan

Documentacion, script y test; sin migracion de datos ni esquema. Rollback: revertir el commit (borra el test, restaura la guia, el README y el docstring/dummies del script). No hay estado de runtime que restaurar.

## Open Questions

- Ninguna que cambie specs, enfoque o desglose de tareas. La ubicacion exacta del gate dentro de §8 (junto a 8.1 o como subseccion propia) se decide en apply leyendo la seccion completa; no altera el contrato de la spec.
