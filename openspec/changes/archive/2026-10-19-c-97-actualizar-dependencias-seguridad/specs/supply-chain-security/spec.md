## ADDED Requirements

### Requirement: Resolucion de excepciones de auditoria con correccion rompiente

El repositorio SHALL resolver las excepciones de la auditoria de dependencias del backend que solo sean corregibles mediante una actualizacion mayor rompiente, subiendo las dependencias afectadas de forma que la lista de excepciones de `scripts/security/pip_audit_exceptions.txt` contenga unicamente hallazgos SIN correccion publicada. Las dependencias afectadas SHALL subirse a versiones que resuelvan las advisories de `starlette` y de `pytest` registradas como seguimiento en c-64. Cuando la actualizacion mayor NO sea viable sin una rotura desproporcionada, la excepcion MAY mantenerse, pero el `design.md` del change MUST registrar la conclusion con evidencia y MUST dejar un seguimiento revisado.

#### Scenario: Las advisories de starlette y pytest quedan resueltas

- **WHEN** se corre `pip-audit -r App/Backend/requirements.txt` contra los pins actualizados
- **THEN** ninguna de las 7 advisories de `starlette` (PYSEC-2026-161/249/248/1943/1941/2281/2280) ni `PYSEC-2026-1845` de `pytest` figura como hallazgo exceptuado, porque `starlette` resuelve a una version al menos `1.3.1` y `pytest` a 9.x

#### Scenario: La lista de excepciones solo conserva hallazgos sin correccion publicada

- **WHEN** se inspecciona `scripts/security/pip_audit_exceptions.txt`
- **THEN** sus entradas por ID corresponden solo a `python-jose` y `ecdsa`, cada una con su motivo de "sin correccion publicada", y no quedan entradas de `starlette` ni de `pytest`

#### Scenario: La matriz de versiones y la compatibilidad quedan registradas

- **WHEN** se lee el `design.md` del change
- **THEN** registra las versiones objetivo exactas de `fastapi`, `starlette`, `pytest` y `pytest-asyncio`, la restriccion de compatibilidad que las vincula y el plan de rollback

#### Scenario: Fallback documentado cuando la actualizacion no es viable

- **WHEN** la actualizacion mayor resulta NO viable sin rotura desproporcionada
- **THEN** el `design.md` registra esa conclusion con evidencia y la excepcion permanece con un seguimiento revisado, sin declarar resuelta la advisory
