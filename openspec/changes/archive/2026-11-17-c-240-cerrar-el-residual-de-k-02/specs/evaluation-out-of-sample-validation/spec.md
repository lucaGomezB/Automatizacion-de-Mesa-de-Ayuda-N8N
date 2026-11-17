## ADDED Requirements

### Requirement: OOS-027 — Retiro del corpus independiente del repositorio publico (decision de autores)

La disposicion del corpus independiente publicado (`evaluation/data/campana/corpus_independiente.json` y `corpus_independiente_arbitrado.json`) SHALL ser el RETIRO del repositorio publico, alineado con la decision de los autores registrada en `docs/Tesis/Correcciones/dictamen-correcciones.md` y con «Si la autorizacion no existe, retirar los textos del repositorio publico y de la tesis». La eliminacion SHALL ir en un commit propio separado del commit de contenido del change, y SHALL ajustar para dejar la suite verde: `evaluation/tests/test_linea_de_base.py`, `evaluation/tests/test_calibracion_gate.py`, `evaluation/monitoreo/test_monitor_deriva.py` y las sumas SHA-256 de `evaluation/data/campana/analisis/SHA256SUMS.txt` y de las tablas del README de campana. Los bytes de los archivos retirados MAY conservarse en un archivo PRIVADO fuera del repositorio (no versionado), con sus SHA-256 citados en la tesis como trazabilidad; el repositorio publico MUST NOT volver a alojarlos como evidencia vigente. El change MUST NOT borrar archivos sin la decision registrada de los autores.

#### Scenario: Retiro en commit separado

- **WHEN** la decision registrada es retirar
- **THEN** los archivos del corpus independiente se eliminan en un commit propio
- **AND** el commit ajusta las tres pruebas y las sumas SHA-256

#### Scenario: Suite verde tras el retiro

- **WHEN** se ejecuta la suite de `evaluation/` tras el retiro
- **THEN** pasa, incluidas `test_linea_de_base.py`, `test_calibracion_gate.py` y `monitoreo/test_monitor_deriva.py`

#### Scenario: Trazabilidad sin publicacion

- **WHEN** los autores conservan los bytes en un archivo privado
- **THEN** el archivo privado queda fuera del repositorio (no versionado)
- **AND** la tesis cita los SHA-256 como trazabilidad sin publicar el contenido

#### Scenario: Sin borrado sin decision

- **WHEN** no hay decision registrada de los autores
- **THEN** ningun archivo se elimina y la tarea queda bloqueada esperando la decision
