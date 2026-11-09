# Design: Acreditar el nivel pago de la Gemini API y el consentimiento de los cuatro participantes

## Context

Ver `proposal.md` para la motivacion. El CONEAU del 2026-11-09 sobre `v1.2.13`
(`auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md`) dejo dos puntos a cargo de los
autores: B4 ("Acreditar el nivel pago de la Gemini API con un comprobante de facturacion o con
la captura del proyecto; la guia de configuracion no lo prueba. Obtener de `E1`, `E2`, `O1` y
`O2` una constancia firmada de consentimiento, aunque sea posterior, y mencionarla en 7.5") y
el item 13 del inventario ("`11-aspectos-legales.tex:34`, 'en consonancia con el consentimiento
informado' sin registro -> retirar o respaldar con una constancia"). c-192 cerro el resto del
dictamen y remitio estos dos a `v1.2.15`; su design ya declaro que la evidencia vive en la
carpeta fisica del director.

**Estado de partida verificado al proponer** (solo lectura):

- 7 (`11-aspectos-legales.tex:16`, `subsec:transferencia-internacional`) dice: "El servicio de
  inferencia opero en el nivel pago de la Gemini API, con creditos prepagos
  (`\path{docs/gemini-api-key-setup.md}`); en ese nivel el proveedor no utiliza el contenido
  transferido para mejorar sus productos `\parencite{Google2026_gemini_api_pricing}`".
- 7 (`11-aspectos-legales.tex:34`, `subsec:consentimiento-derechos`) cierra con: "No se
  conservo un registro especifico del procedimiento de informacion y consentimiento de esos
  cuatro participantes: los runbooks de `\path{docs/campana-medicion/}` no lo consignan..."
  La frase "en consonancia con el consentimiento informado" ya fue retirada por c-192 (ahora
  dice "en consonancia con la pseudonimizacion").
- `evaluation/data/campana/README.md` (Sujetos) y `runbook-doble-etiquetado.md` (1.2) fijan los
  alias `E1`, `E2`, `O1`, `O2` y los codigos `P<n>`, con el director como custodio de la
  correspondencia alias-identidad fuera del repositorio.
- `docs/gemini-api-key-setup.md` existe (24-09-2026); es la fuente que el dictamen califica de
  debil.
- Anexo B (`12-anexos.tex`): el tag vigente que imprime el PDF todavia nombra `v1.2.13` en
  varios pasajes y el commit de contenido de `v1.2.14` conservo ese nombre mientras añadia la
  oracion de verificacion; el hash real se consigna en el commit posterior.

## Goals / Non-Goals

**Goals:**

- Que el nivel pago quede acreditado por un hecho operativo (comprobante de facturacion en
  custodia del director) y no por la guia de configuracion (D1).
- Que el consentimiento de los cuatro participantes quede declarado con su procedimiento real,
  sin nombres ni datos personales versionados (D2, D3).
- Que la plantilla de confirmacion y su registro entren al repositorio (D3).
- Que el registro, `CHANGES.md` y los artefactos generados queden actualizados (D4).
- Que `v1.2.15` cierre el ciclo con el patron de hash del Anexo B y no imprima un hash ajeno
  (D5), y que el PDF no supere las 118 paginas (D6).

**Non-Goals:**

- Ingresar al repositorio los originales firmados, el comprobante de facturacion, la
  correspondencia alias-identidad o cualquier dato personal (D7).
- Tocar `App/`, `n8n/`, `evaluation/`, `data/` o figuras.
- Reduccion del PDF por debajo de 118 paginas.

## Decisions

### D0 — Verificacion previa y existencia de la evidencia (bloqueante, solo lectura)

Antes de reescribir, confirmar con los autores y el director que EXISTEN fisicamente: (a) el
comprobante de facturacion o la captura del proyecto en el nivel pago de la Gemini API; (b) las
cuatro constancias firmadas de `E1`, `E2`, `O1` y `O2`. El texto solo declara lo que la evidencia
sostiene. **Si alguna no existe, el apply se detiene y se consulta a los autores**; no se
reconstruye ni se declara un procedimiento sin respaldo (regla heredada de c-192 D0). Ningun
documento fisico se digitaliza ni se versiona.

### D1 — Nivel pago acreditado por el registro de facturacion

En `11-aspectos-legales.tex:16` (oracion final de `subsec:transferencia-internacional`):

- Se conserva: "El servicio de inferencia opero en el nivel pago de la Gemini API, con creditos
  prepagos; en ese nivel el proveedor no utiliza el contenido transferido para mejorar sus
  productos `\parencite{Google2026_gemini_api_pricing}`".
- Se retira `(\path{docs/gemini-api-key-setup.md})`: la guia de configuracion MUST NOT quedar
  como prueba del nivel pago.
- Se agrega: "El comprobante de facturacion del nivel pago se conserva bajo custodia del
  director de la tesis y no se versiona porque contiene datos de la cuenta."

Alternativa descartada: citar la captura del proyecto en *Paid tier* desde el repo; contiene
datos de la cuenta y no se versiona, igual que el comprobante.

### D2 — Consentimiento: informacion verbal previa y confirmacion escrita posterior

En `11-aspectos-legales.tex:34` (`subsec:consentimiento-derechos`) se reemplaza la oracion de
ausencia de registro por:

> Los cuatro participantes fueron informados verbalmente, antes de realizar sus tareas, del
> proposito del estudio, del caracter pseudonimizado de los registros, de la voluntariedad de
> la participacion y del derecho a retirarse; con posterioridad a su participacion firmaron
> una confirmacion escrita de esa informacion y de su consentimiento. Los originales firmados
> se conservan en el expediente fisico del trabajo, bajo custodia del director de la tesis, y
> no se versionan porque contienen datos personales; el repositorio conserva la plantilla de la
> confirmacion y el registro de que fue obtenida para los cuatro participantes
> (`\path{docs/campana-medicion/confirmacion-posterior-consentimiento.md}`).

Se conserva el resto del parrafo (registros sin datos personales; correspondencia alias-identidad
fuera del repositorio, pseudonimizada; "en consonancia con la pseudonimizacion"). El texto MUST
NOT contener nombres reales ni la correspondencia alias-identidad: solo alias y codigos `P<n>`.

### D3 — Plantilla de confirmacion versionada

Se crea `docs/campana-medicion/confirmacion-posterior-consentimiento.md`, de una pagina:

- Marcadores de posicion (sin nombres) para `alias`, `rol`, `fecha de informacion verbal`,
  `fecha de confirmacion` y `custodia`.
- Los cuatro puntos: (1) informacion verbal previa a las tareas; (2) registros
  pseudonimizados; (3) autorizacion del uso de los registros producidos; (4) firma de la
  confirmacion con posterioridad a la participacion.
- Una tabla de registro `alias, rol, fecha_informacion_verbal, fecha_confirmacion, custodia`.
- La declaracion de que los originales firmados los conserva el director y que SOLO la
  plantilla y el registro entran al repositorio y a Engram.

Las fechas concretas son las que consigne el director; si una fecha no se registra, se consigna
"no registrada" y se declara la limitacion (no se inventan fechas).

### D4 — Registro y CHANGES

- `docs/Tesis/Correcciones/dictamen-correcciones.md`: seccion "Dictamen v10 / v1.2.13
  (2026-11-09) - c-193" con la matriz en el formato de c-192 (Rec | Observacion | Correccion |
  Archivo | Estado), cubriendo B4 y el item 13, la decision de custodia y el libro mayor de
  paginas. Si se opta por la matriz estricta de 7 columnas (encabezado "Fragmento verificable"),
  `verificar_matriz_trazabilidad.py` SHALL reportar 0 fallas.
- `CHANGES.md`: FASE 58 con el bloque de c-193, al estilo de la FASE 57.
- Anexo I (`12-anexos.tex`): actualizar la fila/cabecera de trazabilidad para declarar B4 y el
  item 13 cerrados por c-193 (solo si no agrega altura neta; ver D6).

### D5 — Release `v1.2.15` con el patron de hash del Anexo B (c-188)

Patron: el commit de contenido SHALL llevar en el Anexo B la oracion de verificacion
(`git rev-list -n1 v1.2.15`) en lugar del hash; el tag anotado `v1.2.15` apunta al commit de
contenido; el commit inmediatamente posterior reemplaza la oracion por el hash completo del
commit de contenido; los commits posteriores MUST NOT modificar las fuentes de la tesis. El PDF
compilado en el tag MUST NOT imprimir el hash de una release previa.

El Anexo B SHALL nombrar la release entregada como `v1.2.15` (corregir ademas el arrastre de
`v1.2.13` que persiste en la linea 44 y en las tablas de la seccion heredado de c-192). La
edicion del Anexo B es un artefacto de release y no agrega altura neta. Si el orquestador
prefiere limitar la edicion a la oracion de verificacion, se registra la decision y el residuo
(nombres `v1.2.13` en el Anexo B) queda declarado en el registro.

### D6 — Neutralidad de paginas

El PDF del tag `v1.2.15` MUST NOT superar las 118 paginas del tag `v1.2.14`. Las oraciones
nuevas pueden agregar una o dos lineas: si la compilacion supera 118, se recorta prosa en los
mismos parrafos tocados (o en el entorno cercano) y se recompila; si aun asi no se logra, se
detiene y se consulta. El resumen y el abstract MUST NOT superar 250 palabras (no se tocan en
este change).

### D7 — Frontera de datos personales

NUNCA entran al repositorio ni a Engram: los originales firmados, el comprobante de
facturacion, capturas de la consola de Google, la correspondencia alias-identidad y cualquier
nombre real. El repositorio conserva solo la plantilla, el registro (alias y `P<n>`) y las
oraciones de la tesis. Los prompts de Engram se redactan sin nombres reales.

## Risks / Trade-offs

- [La evidencia fisica no existe o no se puede confirmar] -> D0 bloquea el apply; no se declara
  un procedimiento sin respaldo.
- [El texto agrega lineas y supera 118 paginas] -> D6 recorta prosa en los parrafos tocados y
  recompila; si no alcanza, se consulta.
- [Una fecha de informacion o confirmacion no esta registrada] -> se consigna "no registrada" y
  se declara la limitacion; no se inventan fechas (D3).
- [El Anexo B hereda nombres de `v1.2.13` de c-192] -> D5 los corrige a `v1.2.15` o declara el
  residuo en el registro.
- [Gitleaks marca prosa con nombres de archivo o claves de cita] -> se usa "seccion N
  (`archivo.tex`)" y no se escriben claves que parezcan secretos.

## Migration Plan

Apply en el orden de `tasks.md`; compilacion en el entorno de registro (Docker `texlive-thesis`),
`verify_citations.py`, verificador de la matriz y `openspec validate --strict`. Release
(orquestador): rama `change/c-193-acreditar-el-nivel-pago-y-el-consentimiento`, commit de
contenido con la oracion de verificacion en el Anexo B, tag `v1.2.15`, commit del hash,
`engram sync --project`, PR contra `main` y archive. Rollback: revertir las fuentes y el
registro al commit previo; no hay datos ni codigo que revertir.

## Open Questions

- D0: confirmar con los autores/director que existen el comprobante de facturacion y las cuatro
  constancias firmadas (y la fecha de cada una). No bloquea el propose; si bloquea el apply.
- D4: matriz de la seccion c-193 en 5 columnas (como c-192) o 7 columnas verificables.
- D5: corregir todos los nombres `v1.2.13` del Anexo B a `v1.2.15` o solo la oracion de
  verificacion, declarando el residuo.
- D6: si la compilacion supera 118 paginas, donde recortar.
