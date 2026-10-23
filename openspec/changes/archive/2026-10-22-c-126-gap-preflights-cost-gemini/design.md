## Context

Ver `proposal.md` — Why. El spec vivo `openspec/specs/local-bootstrap/spec.md` describe 7 requisitos. Dos gates cableados en `scripts/up.sh` (`check_cost_preflight`, `check_gemini_preflight`, invocados desde `main` tras `check_env_file` y antes de `ensure_certificates`) y en `scripts/up.ps1` (`Invoke-CostPreflight`, `Invoke-GeminiPreflight`, invocados tras `Test-EnvPreflight` y antes de `Invoke-EnsureCertificates`) no estan representados. Este change es DOC-ONLY: no modifica codigo. El change c-125 dejo estos gates explicitamente fuera de su alcance y como pregunta abierta; este change la resuelve.

## Goals / Non-Goals

**Goals:**

- Expresar como delta (`## ADDED Requirements`) los dos gates existentes, con su contrato real observable: que verifican, que su fallo bloquea el arranque con exit code distinto de cero, que no leen ni imprimen secretos y su bypass ruidoso.
- Preservar la equivalencia multiplataforma ya declarada por la capacidad.

**Non-Goals:**

- No modificar el comportamiento de los scripts ni de los verificadores.
- No tocar los 7 requisitos existentes (se auditan, no se editan).
- No mover los gates a otra capacidad (`cost-readiness`, `n8n-workflow`); se especifican donde se ejecutan, en el arranque local.

## Decisions

**Decision 1: ADDED, no MODIFIED.** Los gates no estan representados hoy: no se modifica el contenido de un requisito existente, se agrega comportamiento no especificado. Corresponde `## ADDED Requirements`.

**Decision 2: Dos requisitos, uno por gate.** Cada gate verifica artefactos distintos y tiene su propio bypass (`UP_SKIP_COST_PREFLIGHT` frente a `UP_SKIP_GEMINI_PREFLIGHT`); separarlos mantiene requisitos testeables e independientes. Alternativa descartada: un unico requisito "preflights de preparacion", que mezclaria dos contratos con bypass distintos y perderia trazabilidad de fallos.

**Decision 3: Comportamiento observable, no nombres internos.** El spec referencia los verificadores por su ruta estable (`scripts/preflight/cost_readiness.py`, `scripts/preflight/gemini_readiness.py`) porque su exit code ES el contrato del gate; no describe funciones internas ni el formato exacto del resumen. Asi el requisito sobrevive a refactors internos que no cambien el comportamiento.

**Decision 4: Se documentan ambos bypass.** El codigo implementa `UP_SKIP_COST_PREFLIGHT=1` y `UP_SKIP_GEMINI_PREFLIGHT=1`, ambos ruidosos. Se especifican los dos para no dejar comportamiento real sin representar; el warning explicito es parte del contrato, no un detalle de implementacion.

**Decision 5: Los 7 requisitos existentes no se tocan.** Verificados contra los scripts; el nuevo par no contradice ninguno. Mapa de relacion:

| Requisito existente | Relacion con los nuevos gates |
|---|---|
| Preflight de entorno con fallo ruidoso | Complementario y no solapado: valida PRESENCIA/VALOR de secretos en `App/Backend/.env`; los nuevos gates validan ARTEFACTOS del repositorio (workflow + compose) sin leer secretos |
| Generacion automatica de certificados TLS cuando faltan | Orden: los gates corren ANTES de `ensure_certificates` |
| Arranque del stack y espera de salud acotada | Los gates corren antes de tocar Docker |
| Verificacion de salud y salida de acceso | Sin relacion directa |
| Recordatorio manual de configuracion de N8N | Sin relacion directa |
| Equivalencia multiplataforma y alias opcional | Los gates se agregan al flujo equivalente de `up.sh` + `up.ps1` |
| Credenciales de desarrollo local parametrizadas por entorno | Sin relacion directa |

## Risks / Trade-offs

- [Acoplar el spec al nombre exacto del verificador] -> El contrato es el exit code y la ruta estable; renombrar el script requeriria actualizar el requisito, igual que hoy ocurre con `generate-certs.sh`. Mitigacion: el nombre se cita como interfaz estable, no como detalle interno.
- [Documentar el bypass podria invitar a su uso] -> El requisito lo define como unico y ruidoso; el warning explicito y la advertencia de guardas rotas son parte del contrato.
- [Deriva futura entre spec y scripts] -> Mitigado por la re-verificacion como tarea del change y por las pruebas existentes de los verificadores (`scripts/preflight/test_cost_readiness.py`, `scripts/preflight/test_gemini_readiness.py`) y del cableado de entorno y costo en `scripts/tests/test_up_preflight.sh`; el cableado del gate Gemini en `up.sh` no tiene prueba de integracion dedicada y queda cubierto por la verificacion manual del task 1.4.

## Migration Plan

1. Al archivar el change, aplicar el delta al spec vivo (`openspec archive`), o adelantarlo via sincronizacion del spec.
2. Verificar el spec vivo con `openspec validate local-bootstrap --strict`.
3. Rollback: revertir el commit de sincronizacion del spec; sin efecto sobre el codigo.
