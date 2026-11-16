## ADDED Requirements

### Requirement: OOS-026 — Rotulado de los artefactos retirados de la tesis

Los documentos del repositorio que describen los artefactos del corpus fuera de muestra (`evaluation/data/campana/README.md`, en las secciones del corpus independiente, de su corrida, del arbitraje y de la referencia in-sample de la validacion; `evaluation/data/canario/README.md`; `docs/operational-guide.md` en el pasaje del conjunto canario; `docs/campana-medicion/runbook-corpus-independiente.md`; `docs/campana-medicion/runbook-arbitraje-discordantes.md`; y `knowledge-base/11_evaluacion_experimental.md`) SHALL declarar que esos artefactos se retiraron de la tesis (c-235), que no constituyen evidencia de la tesis y que su procedencia no se acredita como registro primario de una organizacion. Toda afirmacion de procedencia de esos documentos ("del organismo", "compania financiera", fechas de ocurrencia, condiciones de etiquetado o de consentimiento) SHALL corregirse con lo que los autores confirmen por escrito o rotularse como no acreditada; MUST NOT reemplazarse por una procedencia nueva no confirmada. Por defecto los artefactos SHALL conservarse sin alterar ningun byte fijado por SHA-256, y el codigo y las pruebas MUST NOT cambiar. Si los autores deciden eliminarlos, la eliminacion SHALL registrarse como decision de autores, SHALL ir en un commit propio y SHALL dejar las pruebas de `evaluation/` y las sumas SHA-256 coherentes y en verde.

#### Scenario: Documentos rotulados

- **WHEN** se leen los documentos listados
- **THEN** cada uno declara que el material se retiro de la tesis, que no es evidencia y que su procedencia no esta acreditada
- **AND** ninguno afirma que los casos provienen del organismo o de una compania sin confirmacion registrada de los autores

#### Scenario: Bytes intactos por defecto

- **WHEN** se verifican `evaluation/data/campana/analisis/SHA256SUMS.txt`, `evaluation/data/canario/canario.SHA256SUMS.txt` y las sumas del README de campana
- **THEN** todas las sumas coinciden con los archivos versionados

#### Scenario: CI verde

- **WHEN** se ejecuta la suite de pruebas de `evaluation/`
- **THEN** pasa, incluidas `test_linea_de_base.py`, `test_calibracion_gate.py` y `monitoreo/test_monitor_deriva.py`

#### Scenario: Eliminacion solo por decision de autores

- **WHEN** los autores registran la decision de eliminar los artefactos
- **THEN** la eliminacion va en un commit propio con las pruebas y las sumas ajustadas
- **AND** la suite de `evaluation/` sigue en verde
