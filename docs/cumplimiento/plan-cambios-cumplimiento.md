# Plan de changes de cumplimiento (propuesta para revision)

Proyecto: Automatizacion de Mesa de Ayuda N8N (tesis UTN-FRM 2026)
Fecha: 2026-10-01
Estado: APROBADO Y TOTALMENTE EJECUTADO (2026-10-19) — los seis changes del plan (C-61..C-66) quedaron IMPLEMENTADOS Y ARCHIVADOS; no quedan changes planificados.
Insumos: `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` y `docs/cumplimiento/marco-legal-ar-2026.md`.

## 1. Objetivo y encuadre

Alinear el sistema, lo mas posible, con **ISO/IEC 27001:2022 + 27002:2022**, **ISO/IEC 27701** (privacidad), **NIST CSF 2.0** y el **marco legal argentino vigente 2026** (Ley 25.326 + AAIP), para **fortalecer la defensa de la tesis**.

Regla de lenguaje: se usa "alineado con" y "controles mapeados a". NO se declara "certificado" ni "compliant". No hay auditoria de certificacion.

Regla de trabajo: **todos los cambios de tesis van exclusivamente en `docs/Tesis/v9 (IA)`**.

### 1.1 Presupuesto de paginas (LIMITE DURO: 100 paginas de cuerpo)

Restriccion de la tesis: **el cuerpo no puede superar las 100 paginas**; los **anexos no cuentan** para ese limite.

Estado medido: la tesis compilada (`docs/Tesis/v9 (IA)/paper/main.pdf`) tiene **74 paginas**. Margen disponible: **~26 paginas** (menos cualquier otro agregado previsto).

Regla de reparto:
- **Cuerpo (sintesis, objetivo 6-10 paginas)**: marco adoptado (ISO 27001/27002, 27701, NIST CSF 2.0, Ley 25.326), metodo del gap assessment, estado actual resumido, **brechas principales** y hoja de ruta. Cada change aprobado se describe en 1-2 parrafos.
- **Anexos (sin limite)**: mapeo ISO 27002 completo, mapeo NIST CSF, informe legal, gap assessment detallado, plan de changes, evidencia.
- Todo lo **organizacional (O)** va a narrativa/anexo, nunca ocupa cuerpo con detalle.

Consecuencia: **no** se agrega un capitulo extenso de cumplimiento. Se agrega una **seccion compacta** (o un capitulo corto) y el detalle se anexa.

### 1.2 Tres categorias de control (para no mezclar alcance)

- **(T) Tecnico-implementable en el repositorio**: codigo, configuracion, CI. Es lo que un change puede cerrar.
- **(D) Documental del proyecto**: politicas, clasificacion, planes, procedimientos. Cierra con documentos versionados.
- **(O) Organizacional, fuera del repositorio**: seleccion de personal, formacion, sanciones, controles fisicos, contratos. NO se implementa: se documenta como responsabilidad de la organizacion adoptante y como narrativa de tesis.

## 2. Estructura propuesta de changes (6)

| ID | Nombre (kebab) | Alcance | Controles ISO/NIST | Governance | Depende de | Prioridad |
|----|----------------|---------|--------------------|-----------|------------|-----------|
| C-61 | `compliance-gobernanza` | (D) Politica de seguridad de la informacion; clasificacion y etiquetado de la informacion; roles y responsabilidades de seguridad (incl. responsable de datos); plan de respuesta a incidentes de seguridad; procedimiento de reporte de eventos; inventario de activos y registro de requisitos legales; modelado de amenazas; politica de privacidad en runtime; registro de bases (ROPA). | 5.1, 5.2, 5.9, 5.12, 5.13, 5.24-5.27, 5.31, 8.26 | MEDIO | — | 1 |
| C-62 | `hardening-infra-red` | (T) Quitar publicacion de puertos `5433`/`6379`/`5678` al host; contrasena en Redis; segmentacion de red Docker; restringir acceso a la UI de N8N; endurecer nginx; separar entornos dev/test/prod. | 8.20, 8.22, 8.2, 8.31, 5.14 | ALTO | — | 2 |
| C-63 | `identidad-accesos-claves` | (T) MFA para cuentas de operacion/administracion; politica de contrasenas; bloqueo por intentos fallidos; expiracion/rotacion/revocacion de JWT (refresh o lista de revocacion); revision periodica de accesos; gestion de claves (secret manager/KMS, rotacion de Fernet y del secreto JWT, CA real). | 5.15, 5.16, 5.17, 5.18, 8.2, 8.5, 8.24 | CRITICO | C-61 (parametros de politica) | 4 |
| C-64 | `vulnerabilidades-supply-chain` | (T) Dependabot; `pip-audit`/`npm audit` en CI; escaneo de imagenes (trivy); SBOM; SAST (bandit/semgrep); pinning estricto de dependencias; (D) evaluacion de seguridad y clausulas con proveedores (Twilio, Gemini, Microsoft, N8N). | 8.8, 8.28, 8.29, 5.19-5.23 | MEDIO | — | 5 |
| C-65 | `backup-continuidad` | (T+D) Cifrado del backup; copia offsite; automatizacion; prueba de restauracion periodica; RTO/RPO; plan de continuidad; redundancia basica. | 8.13, 8.14, 5.29, 5.30, 5.33 | ALTO | — | 6 |
| C-66 | `privacidad-transferencias` | (T+D) Quitar/seudonimizar el numero llamante en logs (`cost_guard/guard.py:236,252`); cifrar o justificar por minimizacion el contacto del directorio (`models/empleado.py:16-18`); instrumento de transferencia internacional para Gemini/Twilio (clausulas modelo o consentimiento); consentimiento e informacion al titular; procedimiento ARCO con plazos; retencion de logs. **Se alinea con C-53.** | 5.34, 8.12, 8.15, 5.31 | ALTO | — (C-66 alinea con C-53; C-67 cerrado NO REALIZADO; C-66 IMPLEMENTADO Y ARCHIVADO 2026-10-19) | 3 |

Notas:
- La **prioridad** es sugerida por valor para la defensa y relacion riesgo/esfuerzo; es ajustable.
- C-62 y C-66 tienen hallazgos de **bajo esfuerzo y alto impacto**; C-61 es documental y estructura el capitulo. (C-62 quedo ARCHIVADO el 2026-10-08; C-66 quedo IMPLEMENTADO Y ARCHIVADO el 2026-10-19.)
- Los controles del tema Personas (6.x) y Fisico (7.x), y los organizacionales (5.2, 5.18, 6.5, 8.1, 8.4), se documentan como **(O)** en la tesis, no como change.

**Estado (2026-10-19):** `C-66 privacidad-transferencias` quedó **IMPLEMENTADO Y ARCHIVADO** (2026-10-19, 36/36; `openspec/changes/archive/2026-10-19-c-66-privacidad-transferencias`). Governance ALTO. Entregó la pseudonimización del número llamante en los logs del guarda de costo con una clave HMAC **dedicada** (`cost_guard_caller_hmac_key`, independiente de la clave de pseudonimización Fernet), la superficie de privacidad en runtime (`/privacidad`), el procedimiento ARCO con plazos, la política de retención de logs, la justificación por minimización del directorio y el instrumento de transferencia internacional (documentado, no firmado); corrigió dos inconsistencias documentales. Cierra los controles 5.34, 8.12, 8.15 y 5.31. Specs sincronizadas: `privacy-runtime-surface` creada (capability nueva) y `runtime-cost-guard`, `security-governance-docs` y `employee-directory` modificadas. Con C-64 y C-65 también **IMPLEMENTADOS Y ARCHIVADOS** (2026-10-19; ver el cierre del plan más abajo), el plan queda **TOTALMENTE EJECUTADO**: los seis changes (C-61..C-66) están implementados y archivados y **no queda ningún change planificado**.

**Estado (2026-10-19, cierre del plan):** `C-64 vulnerabilidades-supply-chain` quedó **IMPLEMENTADO Y ARCHIVADO** (2026-10-19, 33/33; `openspec/changes/archive/2026-10-19-c-64-vulnerabilidades-supply-chain`). Governance MEDIO. Entregó `.github/dependabot.yml`, el job `security-scan` en CI (pip-audit + bandit + npm audit), el pinning de imágenes Docker (nginx:1.31.7-alpine, ngrok/ngrok:3.39.8-debian), cotas superiores de dependencias y el documento de evaluación de seguridad de proveedores; cierra los controles 8.8, 8.28, 8.29 y 5.19-5.23 (trivy/SBOM evaluados y diferidos). `C-65 backup-continuidad` quedó **IMPLEMENTADO Y ARCHIVADO** (2026-10-19, 31/31; `openspec/changes/archive/2026-10-19-c-65-backup-continuidad`). Governance ALTO. Entregó el backup cifrado (openssl AES-256-CBC, `BACKUP_ENCRYPTION_PASSPHRASE`), el scheduler versionado (cron + systemd timer), la prueba de restauración reproducible, `docs/seguridad/plan-continuidad.md` (RTO/RPO 24h; offsite/redundancia como acción del adoptante), la corrección del gap assessment y el Purpose real para `backup-scripts`; cierra los controles 8.13, 8.14, 5.29, 5.30 y 5.33. Specs sincronizadas (commit previo al archive, `--skip-specs`): `supply-chain-security` y `continuity-planning` creadas (capabilities nuevas); `ci-pipeline`, `security-governance-docs` (SGD-001 + SGD-016) y `backup-scripts` (BACKUP-005..008) modificadas. Con esto el plan de cumplimiento queda **TOTALMENTE EJECUTADO**: los seis changes (C-61..C-66) están implementados y archivados; **no queda ningún change planificado**.

## 3. Orden recomendado

1. **C-61** (gobernanza documental): bajo esfuerzo, da estructura y el marco que los demas changes referencian.
2. **C-62** (hardening): quick win, alto impacto, acotado a `docker-compose.yml`/`nginx`.
3. **C-66** (privacidad/transferencias): alto valor legal y alinea C-53. **IMPLEMENTADO Y ARCHIVADO 2026-10-19 (36/36).**
4. **C-63** (identidad/accesos/claves): mayor esfuerzo, gobernanza CRITICO.
5. **C-64** (vulnerabilidades/supply chain). **IMPLEMENTADO Y ARCHIVADO 2026-10-19 (33/33).**
6. **C-65** (backup/continuidad). **IMPLEMENTADO Y ARCHIVADO 2026-10-19 (31/31).**

## 4. Relacion con C-53 / C-67 (notificacion del numero de incidente)

**Estado (2026-10-01):** `C-53` quedo **ARCHIVADO** con la parte ya implementada (correo/web/numero canonico, 12/12). El **SMS al llamante** se dividio a un change propio, **`C-67-notificacion-sms-llamante`** (0/24, governance ALTO), **bloqueado por OQ3** (entregabilidad de Twilio SMS a Argentina +54) **y por C-66**.

`C-67` tocaba dos brechas que C-66 definió (hoy implementadas y archivadas):
- Captura y cifrado del numero llamante (hoy crudo en logs, `cost_guard/guard.py:236,252`).
- Consentimiento e instrumento de transferencia internacional hacia Twilio (EE. UU., pais NO adecuado).

Recomendacion (aprobada): **C-66 define el tratamiento del llamante y el marco de consentimiento/transferencia; C-67 los consume**. C-67 no se inicia hasta resolver OQ3 y C-66.

**Estado (2026-10-19):** `C-67-notificacion-sms-llamante` quedó **CERRADO Y ARCHIVADO como NO REALIZADO** (0/24, nunca implementado; archivado con `--skip-specs`, de modo que los specs principales no se tocaron). Motivos: (1) el spike de OQ3 cerró el 2026-09-23 con veredicto GO-WITH-CONSTRAINTS (SMS best-effort, correo como canal primario), por lo que OQ3 ya no está abierta; (2) su dependencia dura `C-66 privacidad-transferencias` no existía al momento del cierre (se creó y archivó después, 2026-10-19); (3) la cadena "SMS" no aparece en la tesis (`docs/Tesis/v9 (IA)/paper/sections/`) ni en `knowledge-base/`, por lo que es backlog de completitud de software y no un entregable de la tesis.

**OQ3 (accion del autor):** configurar Twilio para SMS (registrar remitente) y hacer una prueba real de entrega a un movil argentino.

## 5. Correcciones de tesis en v9 (capitulo de cumplimiento)

Ademas de los changes, el trabajo de tesis (en v9) incluye:

1. **Plazos ARCO**: incorporar los plazos correctos y atribuidos — acceso: **10 dias corridos** (art. 14); rectificacion/actualizacion/supresion: **5 dias habiles** (art. 16). No atribuir a la ley vigente un derecho autonomo de "oposicion" (el acronimo ARCO es de practica comparada). Esto ademas fundamenta la brecha de "procedimiento ARCO con plazos no implementado".
2. **Pseudonimizacion vs. disociacion**: explicar que la ley regula "disociacion de datos" (art. 2) y como se relaciona con la pseudonimizacion implementada.
3. **Vigencia**: afirmar que la Ley 25.326 sigue vigente y que la reforma alineada al RGPD caduco; no afirmar una ley nueva.
4. **Notificacion de brechas**: reflejar que la ley vigente NO impone una obligacion general (los proyectos proponen 72 h); adoptar el estandar por prudencia.
5. **Transferencias internacionales**: explicar que EE. UU. no es pais adecuado y los mecanismos (clausulas modelo / consentimiento); la pseudonimizacion mitiga pero no sustituye el instrumento.
6. **Decisiones automatizadas**: citar Res. AAIP 4/2019 y art. 20; destacar el human-in-the-loop y la trazabilidad como salvaguarda.
7. **Nuevo capitulo/seccion de cumplimiento**: mapeo ISO 27001/27002 + NIST CSF 2.0, estado actual, brechas y hoja de ruta, con lenguaje de alineacion.
8. **(Opcional) Acentuacion**: los `.tex` de v8/v9 tienen acentuacion corrupta en algunos verbos (efecto de `acentuar_tesis.py`); revisar antes de compilar.

## 6. Fuera de alcance (narrativa de tesis, no changes)

Seleccion y formacion de personal (6.1, 6.3), sanciones (6.4), NDA (6.6), responsabilidades tras el cese (6.5), trabajo remoto y endpoints (6.7, 8.1), controles fisicos (7.x), revision independiente (5.35) y segregacion de funciones operativa (5.3). Competen a la organizacion adoptante; el repositorio no puede evidenciarlos.

## 7. Proximos pasos

1. Revision y aprobacion de esta estructura por el autor.
2. Para cada change aprobado: `/opsx:propose` (artefactos) → revision → `/opsx:apply` (con TDD) → `/opsx:archive`.
3. Redactar el capitulo de cumplimiento en v9 a partir de los informes y del avance de los changes.
4. Alinear C-53 con C-66 (cumplido: **C-66 IMPLEMENTADO Y ARCHIVADO 2026-10-19**, 36/36).
5. **Estado del plan: TOTALMENTE EJECUTADO (2026-10-19).** Los seis changes (C-61..C-66) quedaron implementados y archivados; **no quedan changes planificados**. El paso 2 ya no tiene changes pendientes; solo resta el paso 3 (redacción del capítulo de cumplimiento en v9).