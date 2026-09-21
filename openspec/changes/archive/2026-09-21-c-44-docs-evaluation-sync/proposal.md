## Why

Una auditoria de solo lectura detecto drift documental alrededor del flujo de evaluacion y del script de exportacion de OpenAPI. La guia operativa (§8.1) indica una invocacion que no resuelve (`cd evaluation; python run_evaluation.py`), §8.3 ordena ejecutar `evaluation/generate_corpus.py`, un archivo que NO existe porque C-27 lo elimino permanentemente, y ni la guia ni `evaluation/README.md` documentan el gate de corrida paga que el runner exige (`PaidRunNotConfirmedError`, `--confirm-paid`, `EVALUATION_CONFIRM_PAID`). En paralelo, `App/Backend/scripts/export_openapi.py` es funcionalmente incorrecto: sus dummies no incluyen `JWT_SECRET_KEY`, que `Settings` exige sin default, por lo que el script falla al ejecutarse en un entorno limpio aunque su docstring promete lo contrario; ademas su docstring conserva rutas obsoletas (`Gestion_Incidentes`) y un ejemplo de `--output` inconsistente con su default real. El resultado es deuda de exactitud: quien sigue la guia falla, y el script que la guia manda ejecutar no corre.

## What Changes

- Corregir `docs/operational-guide.md` §8.1 para usar la invocacion real desde la raiz del repo: `PYTHONPATH=App/Backend python -m evaluation.run_evaluation`.
- Eliminar §8.3 (regeneracion del corpus sintetico) y reemplazarla por un puntero al procedimiento real de carga del corpus en `docs/como_cargar_datos_corpus.md`; NO se toca `docs/anexo_f_corpus.md`, que registra la eliminacion como hecho historico correcto.
- Documentar el gate de corrida paga (`--confirm-paid` / `EVALUATION_CONFIRM_PAID=1`, estimacion de costo, codigo de salida 2) en `docs/operational-guide.md` §8 y en `evaluation/README.md`, junto al comando de corrida y a la configuracion de `GEMINI_API_KEY`.
- Arreglar `App/Backend/scripts/export_openapi.py`: agregar `JWT_SECRET_KEY` a `_DUMMIES` para que el script instancie `Settings` sin entorno real, y corregir el docstring (rutas `Gestion_Incidentes` → `App/Backend`, ejemplo `--output` alineado con el default real).
- Agregar una red de seguridad: tests estructurales sobre la documentacion y el script, mas un test funcional que ejecuta el script en un subproceso con `JWT_SECRET_KEY` ausente y exige exit code 0 y OpenAPI 3.1 valido.
- Change acotado: NO se toca el runtime de evaluacion (se documenta el gate, no se cambia), ni `docs/anexo_f_corpus.md`, ni `docs/Tesis/**`, ni otros scripts.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-documentation`: el requisito "Anexo G — Guía operativa" suma que la seccion 8 use la invocacion correcta del runner, no referencie `generate_corpus.py`, apunte al procedimiento real del corpus y documente el gate de corrida paga; el requisito "Especificación OpenAPI 3.1 estática generada desde la app" se refuerza para exigir que el script de generacion corra con dummies suficientes para instanciar `Settings` (incluida `JWT_SECRET_KEY`) y que su uso documentado referencie rutas post-reestructuracion.
- `evaluation-framework`: el requisito "Runner de evaluación sobre el corpus" suma que el gate de confirmacion de corrida paga quede documentado junto al comando de corrida.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `docs/operational-guide.md` (§8.1, §8.3, gate) | Modified | Invocacion correcta, eliminacion del generador inexistente, documentacion del gate pago |
| `evaluation/README.md` (comando de corrida y `GEMINI_API_KEY`) | Modified | Documentacion del gate `--confirm-paid` / `EVALUATION_CONFIRM_PAID` |
| `App/Backend/scripts/export_openapi.py` (`_DUMMIES`, docstring) | Modified | Dummy `JWT_SECRET_KEY`; rutas y ejemplo de `--output` corregidos |
| `App/Backend/tests/test_docs_evaluation_sync.py` | New | Tests estructurales y funcional (subproceso del script) |
| `docs/anexo_f_corpus.md` | Out of scope | Historico correcto; no se modifica |
| `docs/Tesis/**`, otros scripts, runtime de evaluacion | Out of scope | Sin cambios |

Sin cambios en API, esquema de datos, dependencias de runtime ni infraestructura. El comportamiento del runner de evaluacion no cambia: solo se documenta su gate existente.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Reemplazar §8.1/§8.3 por una invocacion que tampoco resuelve | Low | La invocacion correcta ya esta verificada en `evaluation/README.md:70-75` y `docs/como_cargar_datos_corpus.md:189` |
| Tocar `docs/anexo_f_corpus.md` por confusion con el corpus | Low | Declarado fuera de alcance; registra la eliminacion como historia y es correcto |
| Test funcional fragil por `.env` descubrible en el repo | Med | El test corre en subproceso con entorno depurado y cwd sin `.env`; apunta a un output temporal |
| Test estructural acoplado a prosa | Med | Asserts solo sobre tokens estables (`PYTHONPATH=App/Backend`, `confirm-paid`, `EVALUATION_CONFIRM_PAID`, `JWT_SECRET_KEY`), no sobre oraciones |
| Desliz de alcance hacia el runtime de evaluacion | Low | Non-Goal explicito: se documenta el gate, no se modifica su logica |

## Rollback Plan

Revertir el commit de documentacion, script y test. No hay cambios de runtime, esquema ni infraestructura, por lo que no existe estado que restaurar.

## Success Criteria

- [ ] `docs/operational-guide.md` §8 usa `PYTHONPATH=App/Backend python -m evaluation.run_evaluation` y no contiene `generate_corpus.py`.
- [ ] `docs/operational-guide.md` y `evaluation/README.md` documentan el gate `--confirm-paid` / `EVALUATION_CONFIRM_PAID`.
- [ ] `App/Backend/scripts/export_openapi.py` declara `JWT_SECRET_KEY` en sus dummies y no contiene `Gestion_Incidentes`.
- [ ] El test funcional ejecuta el script con `JWT_SECRET_KEY` ausente y obtiene exit code 0 con OpenAPI 3.1 valido.
- [ ] `cd App/Backend; pytest -m "not integration" -q` no reporta regresiones.
- [ ] `openspec validate --strict --changes c-44-docs-evaluation-sync` pasa.
