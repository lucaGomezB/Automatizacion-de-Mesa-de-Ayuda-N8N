## Context

Ver `proposal.md` — Why. Hechos verificados en esta sesión:

- `sha256sum evaluation/data/campana/registro_sujetos.csv` =
  `ab17eb2b6e660b78d206d130c21fac06739ba5512d2ac37d09cf532c2a3d36da`; la tabla "SHA-256
  por archivo" declara `f7a5653e...`.
- Línea 113 actual: `...`sed -i 's/` + LF + `$//' <archivo>`...` — el `\r` escapado se
  perdió y la oración quedó partida. El archivo no contiene ningún byte CR (0x0D).
- Verificados los 21 hashes de la tabla "SHA-256 por archivo" más `intervenciones.csv` y
  `brazo_manual.csv`: el ÚNICO desviado es `registro_sujetos.csv`. Las tres filas
  `pendiente` corresponden a artefactos del corpus independiente que aún no existen.
- Existe un patrón previo: `evaluation/tests/test_doble_etiquetado.py` (`ECM-008`) ya valida
  el hash de la tabla primaria leyendo el campo `- sha256:` del README; esa es la sección
  `- campo: valor`, distinta de las tablas `| Archivo | SHA-256 |`.

## Goals / Non-Goals

**Goals:**
- Corregir el hash declarado de `registro_sujetos.csv` para que el README vuelva a cumplir
  ECM-002.
- Restaurar la línea 113 como una sola línea con el `\r` escapado.
- Agregar un test offline (ECM-015) que impida la recurrencia silenciosa.

**Non-Goals:**
- No tocar `App/`, `n8n/`, `auditorias/`, la tesis ni ningún otro SHA de commit.
- No remapear ni re-versionar artefactos; solo se corrige el texto declarado del README.
- No generalizar el test al resto del repo: solo el README de `evaluation/data/campana/`.

## Decisions

- **D1 — Incluir el test anti-recurrencia (SÍ, está en alcance).** Es barato y offline
  (solo `hashlib`, `pathlib`, `re`), y la deriva actual no fue detectada porque la tabla
  c-166 carecía de validación. `evaluation/tests/test_campana.py` es el lugar natural
  (ya aloja `test_los_artefactos_de_v9_conservan_su_sha256_tras_la_evaluacion` y es un
  test offline de campaña). Alternativa descartada: dejarlo sin test y solo corregir el
  texto — repite el problema y depende de revisión manual en un artefacto de evidencia.
- **D2 — Parser genérico de tablas `| Archivo | SHA-256 |`.** Un único parser cubre las
  tres tablas con ese encabezado (c-166, `intervenciones.csv`, `brazo_manual.csv`),
  leyendo el nombre desde la primera celda y resolviéndolo relativo al directorio del
  README. Alternativa descartada: un parser ad-hoc solo para la tabla c-166 —
  subprotegería las otras dos tablas de hash con idéntico riesgo.
- **D3 — Omitir `pendiente` y archivos ausentes.** Las filas `pendiente`
  (`corpus_independiente.json`, `predicciones_independiente.json`,
  `reporte_independiente.md`) no representan un hash y los archivos aún no están en el
  checkout; el test no debe fallar por ellos (coherente con `pytest.skip` del patrón
  ECM-008 cuando la tabla no existe).
- **D4 — La corrección de los residuos 1 y 2 es conformance a ECM-002, no cambio de
  spec.** El requirement nuevo (ECM-015) es solo la verificación offline; los dos
  arreglos entran como tareas, justificados por ECM-002 ("los datos de la campaña SHALL
  registrar su SHA-256 en un README") y por la política LF de `.gitattributes`. No se
  inventa un requirement para justificar la corrección.
- **D5 — Redacción de la línea 113.** Restaurarla como una sola línea con el `\r`
  ESCAPADO (`sed -i 's/\r$//' <archivo>`) y `newline="\n"`, que es a la vez Markdown
  válido (inline code sin salto) y el comando correcto para quitar un CR de Windows.

## Risks / Trade-offs

- [El test podría fallar en un futuro legítimo al declararse un hash nuevo en el README
  sin actualizar el archivo] → Es exactamente la falla deseada: obliga a mantener README y
  archivos sincronizados (el punto del change).
- [Edición manual del README con CRLF] → `.gitattributes` ya fija LF para `*.md` en esta
  carpeta; la corrección se escribe con `newline="\n"` para no reintroducir el problema.
- [Omitir archivos ausentes podría ocultar una fila mal escrita] → El test sí valida
  cualquier fila cuyo archivo exista; una fila `pendiente` no es un hash y su ausencia de
  archivo es el estado real hasta c-191.

## Migration Plan

1. Corregir la fila de `registro_sujetos.csv` y normalizar la línea 113 en el README.
2. Escribir el test (RED: fija el hash viejo y falla; GREEN: con el README corregido pasa).
3. `cd evaluation && pytest tests/test_campana.py` (offline) en verde.
4. Rollback: revertir los dos archivos; no hay migración de datos ni de runtime.
