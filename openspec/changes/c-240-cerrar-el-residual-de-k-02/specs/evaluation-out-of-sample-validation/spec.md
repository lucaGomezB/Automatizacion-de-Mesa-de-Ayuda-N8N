## ADDED Requirements

### Requirement: OOS-027 — Retiro del corpus independiente del repositorio publico (default K-02)

La disposicion del corpus independiente publicado (`evaluation/data/campana/corpus_independiente.json` y `corpus_independiente_arbitrado.json`) SHALL seguir el default alineado a K-02: retirar los archivos del repositorio publico, salvo que los autores registren en `dictamen-correcciones.md` la decision de que los textos son descripciones genericas de incidentes sin datos de terceros (conservacion + rotulado OOS-026). Si la rama es el retiro, la eliminacion SHALL registrarse como decision de autores, SHALL ir en un commit propio separado del commit de contenido del change, y SHALL ajustar para dejar la suite verde: `evaluation/tests/test_linea_de_base.py`, `evaluation/tests/test_calibracion_gate.py`, `evaluation/monitoreo/test_monitor_deriva.py` y las sumas SHA-256 de `evaluation/data/campana/analisis/SHA256SUMS.txt` y de las tablas del README de campana. El change MUST NOT alterar los bytes de ningun archivo de datos en la rama de conservacion, y MUST NOT borrar archivos sin la decision registrada.

#### Scenario: Retiro en commit separado

- **WHEN** los autores eligen la rama de retiro (default)
- **THEN** los archivos del corpus independiente se eliminan en un commit propio
- **AND** el commit ajusta las tres pruebas y las sumas SHA-256

#### Scenario: Suite verde tras el retiro

- **WHEN** se ejecuta la suite de `evaluation/` tras el retiro
- **THEN** pasa, incluidas `test_linea_de_base.py`, `test_calibracion_gate.py` y `monitoreo/test_monitor_deriva.py`

#### Scenario: Conservacion con rotulado

- **WHEN** los autores registran la decision de conservacion (textos genericos sin datos de terceros)
- **THEN** los archivos se conservan sin alterar bytes y rotulados segun OOS-026
- **AND** las sumas SHA-256 siguen coincidiendo

#### Scenario: Sin borrado sin decision

- **WHEN** no hay decision registrada de los autores
- **THEN** ningun archivo se elimina y la tarea queda bloqueada esperando la decision
