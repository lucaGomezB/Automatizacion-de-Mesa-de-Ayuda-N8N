# Runbook de retencion del directorio de empleados

> **Control mapeado**: ISO/IEC 27002:2022 5.34 (Privacidad y proteccion de PII) y 8.10
> (Eliminacion de informacion), en **alineacion con** ISO/IEC 27701 y los articulos 4 y 16
> de la Ley 25.326; NIST CSF 2.0 PR, GV. Requisito DIR-007 / DIR-015.
> **Estado**: v1 — elaborado en el change `c-153` (governance HIGH).
> **Alcance**: operacion MANUAL de la retencion del directorio: la purga por vencimiento y la
> alerta de acumulacion. NO define infraestructura de planificacion.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria. La ejecucion real es responsabilidad de la organizacion adoptante.

## 1. Proposito

Describir como un `administrador_directorio` opera la **retencion** del directorio de
empleados: cuando corresponde purgar, como se detecta la acumulacion de bajas vencidas y como
se ejecuta la **purga manual**. Cierra el hueco operativo de la retencion sin introducir
automatizacion de la purga.

## 2. Regla de retencion

- La relacion laboral se CONSERVA mientras esta activa mas **1 año**.
- La desactivacion NO es borrado: marca `activo=false` y sella `fecha_baja` (instante UTC).
- El vencimiento se evalua como **`fecha_baja + 1 año`** (funcion pura `retencion_vencida`,
  con ajuste del 29-feb a 28-feb).
- El **borrado fisico** ocurre SOLO por vencimiento del plazo o por una solicitud ARCO de
  supresion; nunca es el camino operativo por defecto.

## 3. Alerta de acumulacion (solo conteo, sin PII)

La alerta informa cuantas filas desactivadas superaron `fecha_baja + 1 año` y **aun no fueron
purgadas**, para que el administrador decida la purga.

```bash
cd App/Backend
python -m scripts.alertar_directorio
```

- La alerta reporta **solo el conteo agregado**. NO expone email, telefono, nombre ni los ids
  de las filas.
- Cuando el conteo es mayor que cero se emite el evento estructurado
  `directorio_retencion_alerta` (campo `vencidos_sin_purgar`).
- Si el conteo es cero no se emite alerta.

## 4. Purga MANUAL

La purga por vencimiento es IDEMPOTENTE y se dispara por una **invocacion humana explicita**:

Opción A — API (rol `administrador_directorio`):

```bash
POST /api/v1/directorio/purga
```

Opción B — script CLI:

```bash
cd App/Backend
python -m scripts.purgar_directorio
```

La purga conserva activos y bajas recientes; una segunda corrida no vuelve a borrar. Deja un
registro de auditoria con el conteo y los **ids** (identificadores internos, NO datos
personales), sin email, telefono ni nombre en claro.

## 5. Procedimiento operativo

1. Ejecutar la **alerta** (`python -m scripts.alertar_directorio`).
2. Si el conteo es mayor que cero, verificar que las bajas vencidas corresponden al plazo y
   que no hay una solicitud ARCO pendiente.
3. Ejecutar la **purga manual** (API o script).
4. Confirmar el conteo purgado en el evento de auditoria.
5. Registrar la corrida en el registro operativo de la organizacion adoptante.

## 6. Sin automatizacion de la purga

NO existe **cron**, **scheduler** ni **worker** que dispare la purga o la alerta por si solo.
La unica via es la invocacion humana explicita descrita arriba. Esta ausencia es una decision
de diseno (DIR-007/DIR-015) y esta verificada por
`App/Backend/tests/test_directorio_purga_no_automatica.py` (que ademas prohibe importar
bibliotecas de planificacion en el codigo de produccion).

## 7. Relacion con ARCO y auditoria

- El borrado por retencion (vencimiento) es distinto del borrado ARCO de supresion; ver
  `procedimiento-arco-directorio.md`.
- La retencion de los registros de auditoria del directorio se define en
  `politica-retencion-logs.md` (clase "Auditoria del directorio") y esta alineada con el
  ciclo de vida del directorio.

## 8. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.34/8.10, ISO/IEC 27701 y la Ley 25.326.
No constituye certificacion ni auditoria. La ejecucion real del procedimiento es
responsabilidad de la organizacion adoptante.
