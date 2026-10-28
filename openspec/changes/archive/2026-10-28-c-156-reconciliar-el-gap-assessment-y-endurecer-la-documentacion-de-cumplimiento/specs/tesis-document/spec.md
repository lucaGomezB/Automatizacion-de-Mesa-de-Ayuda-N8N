## ADDED Requirements

### Requirement: Estado real de MFA y rotacion de claves en el capitulo legal

El documento de tesis SHALL describir el estado de MFA y de rotacion de claves de forma consistente con el repositorio y con los changes archivados. La seccion de brechas y hoja de ruta MUST distinguir entre: (a) los controles implementados en el repositorio (MFA TOTP con desafio para cuentas privilegiadas en `App/Backend/app/routes/auth.py` y rotacion de secretos de C-63a/b/c, archivados el 2026-10-08); y (b) lo que permanece como accion de la organizacion adoptante (KMS/PAM, custodia de claves y operacion en produccion). El texto MUST NOT presentar MFA ni la rotacion de claves como residuales sin calificar. La correccion SHALL aplicarse a la version vigente v10 y a su gemelo v9, y MUST registrar que la fuente LaTeX cambio y que el PDF debe recompilarse para una release de correccion posterior a v1.2.3.

#### Scenario: La tesis distingue implementado de adoptante

- **WHEN** se lee la subseccion de brechas principales y hoja de ruta del capitulo legal
- **THEN** MFA y rotacion de claves figuran como implementadas en el repositorio y solo su operacion con KMS/PAM y custodia quedan como accion del adoptante

#### Scenario: No quedan residuales sin calificar

- **WHEN** se busca en el capitulo legal la afirmacion de que MFA y rotacion de claves siguen pendientes
- **THEN** no existe una afirmacion sin calificar que las presente como residuales del sistema

#### Scenario: La correccion alcanza ambas versiones

- **WHEN** se comparan las fuentes `v10` y `v9` de `11-aspectos-legales.tex`
- **THEN** ambas contienen la distincion entre implementado en el repositorio y accion del adoptante

#### Scenario: El rebuild queda registrado

- **WHEN** se revisa el registro de tareas y la release
- **THEN** figura que el PDF debe recompilarse y publicarse en una release de correccion posterior a v1.2.3
