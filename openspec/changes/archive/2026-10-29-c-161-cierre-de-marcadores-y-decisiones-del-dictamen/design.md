## Context

Ver `proposal.md - Why`. Este change cierra los items abiertos del dictamen CONEAU del 2026-10-28 (`auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`) y dos decisiones del autor: la naturaleza del Anexo I (OQ1-B), la fuente unica de la Figura 2 (drawio frente a Mermaid), las ocho consultas a los autores (Q1-Q8) que hoy viven como marcadores `% PENDIENTE AUTORES`, el versionado de tres sidecars sin PII y la correccion de tres afirmaciones sobre Nginx. Las respuestas de los autores a Q1-Q8 estan en la sesion del 2026-10-28; las preguntas, en `docs/Tesis/Correcciones/preguntas-para-lucas-dictamen-2026-10-28.md`.

Se aplica despues de la familia c-158..c-160 (archivada el 2026-10-29). Las referencias `archivo:linea` remiten al arbol posterior a c-160; el apply las relocaliza por contenido.

### Verificacion previa contra el repositorio (2026-10-29)

**Marcadores `% PENDIENTE AUTORES`.** Hoy existen cinco en `04-marco-metodologico.tex` (lineas 63 a 67: Q1 a Q5) y uno en `12-anexos.tex` (linea 97: Q7). Total: seis marcadores; Q6 y Q8 no tienen marcador (no cambian el texto) pero si entradas PENDIENTE en el registro (lineas 3103 a 3110 de `dictamen-correcciones.md`). El requisito vivo "Procedencia de los datos del brazo automatizado declarada en el protocolo de pruebas" EXIGE que cada dato faltante quede en un marcador y listado como consulta; por eso cerrarlos exige MODIFICAR ese requisito (D8).

**Nginx (Q8).** La tesis afirma en tres pasajes que el despliegue de la campana "no incluyo el proxy": `05-arquitectura.tex:8` (`subsec:vision-general`), `11-aspectos-legales.tex:24` (`subsec:seguridad-tecnica`) y `12-anexos.tex:11` (Anexo A, diagrama de despliegue). La afirmacion NO es uniformemente incorrecta y hay que distinguir dos despliegues: (i) la medicion telefonica del 5 y 6 de octubre (c-70) corrio sobre el perfil Compose aislado `corpus` (`postgres-corpus`, `backend-corpus`, `n8n-corpus`), que NO incluye el proxy inverso Nginx — hay un test que lo garantiza (`test_base_services_are_not_part_of_the_corpus_profile`), Nginx es un servicio base que proxya al backend base y el corpus usa su propio tunel a `backend-corpus:8000`; (ii) la ingesta del brazo automatico del 2 de octubre (correo y formulario web, c-68) es anterior a c-70 y corrio sobre el stack base, que SI incluye Nginx con certificado autofirmado (el harness lee por defecto `https://localhost` con `--insecure`, D5 de Q4; Engram #1143 registra el webhook base `localhost:5678`). Por eso la correccion no es "la campana incluyo Nginx" sino distinguir por despliegue (autor: opcion a). Dos requisitos vivos prescriben el texto que hay que ajustar: "Coherencia técnica entre la tesis y el sistema implementado" (scenario "Perímetro de seguridad consistente") y "Declaracion acotada del endurecimiento tecnico" (scenario "TLS declarado sin sobreafirmar"); ajustarlos exige MODIFICAR ambos (D6).

**Figura 2 y drawio.** `fig:arquitectura` (`05-arquitectura.tex:41-45`) incluye `arquitectura_sistema.png` desde la fuente Mermaid `docs/diagrams/arquitectura_sistema.md`. El `Diagrama de Capas.drawio` y su `.png` viven en `docs/diagrams/` y no estan referenciados por ninguna fuente `.tex`; solo los mencionan el registro del dictamen (`dictamen-correcciones.md:3188`, como dato pendiente de los autores) y la pregunta a Lucas (`preguntas-para-lucas...md:27`). El autor eligio conservar el Mermaid como fuente unica (Figura 2 = A) y retirar el drawio.

**Sidecars (Q7).** Los tres sidecars existen en `data/` (200, 4 y 81 filas respectivamente; `corpus_resultados_n8n.json` tiene 4 filas locales frente a los 119 casos de la corrida completa) y estan ignorados por `.gitignore:66`. Referencias que los describen como no versionados: `data/README.md:20-21`, `docs/como_cargar_datos_corpus.md:20,235,239`, `scripts/corpus_ingest/README.md:73,106` y `knowledge-base/09_decisiones_y_supuestos.md:47`.

**Fechas telefonicas (Q1).** `01-introduccion.tex:76` (subseccion 1.8, `subsec:alcance-delimitaciones`) dice "las corridas del 2, el 6 y el 7 de octubre"; `04-marco-metodologico.tex:68` dice "concluida el 6-10-2026"; `docs/diagrams/cronograma.md:44` tiene el hito "Corrida de telefonía (06/10/2026)"; la leyenda de la figura telefonica de resultados (`07-resultados.tex:38` o `:68`) no fecha la corrida. Con Q1 confirmada (5 y 6 de octubre), los cuatro pasajes pasan a "el 5 y 6 de octubre".

## Goals / Non-Goals

**Goals:**
- Cerrar Q1-Q8 con la respuesta verificada o con "no consta", sin inventar ningun dato y sin dejar marcadores en la fuente.
- Dejar el Anexo I autoexplicativo como autoevaluacion de control de calidad interno (OQ1-B) sin cambiar los hechos que c-160 ya declaro.
- Fijar el Mermaid `arquitectura_sistema.md` como fuente unica de `fig:arquitectura` y retirar el drawio del arbol activo.
- Versionar los sidecars completos sin PII (200 y 81 filas) y coherentizar el `README` y las referencias; el de N8N queda excluido por OQ2.
- Corregir las tres afirmaciones de Nginx para que la tesis coincida con el despliegue real.
- Registrar todo en `dictamen-correcciones.md` y abrir la FASE 49 en `CHANGES.md`.

**Non-Goals:**
- Regenerar el PNG de `fig:arquitectura` ni tocar las Figuras 1, 4, 5 (ya tratadas por c-159).
- A6 del dictamen (hallazgo `reportante_email`/`reportante_telefono`): fuera de alcance.
- Q5/OQ4 de c-158 (AI Agent de N8N) y Q6/Q8 sin marcador mas alla de su registro.
- Cambiar cifras: ningun valor del memo canonico cambia.
- Tocar `App/`, `n8n/`, `evaluation/`, `openspec/config.yaml`, los cinco identificadores canonicos de sector o el arbol congelado `docs/Tesis/v9 (IA)/`.
- Etiquetar una release (la publica el orquestador).

## Decisions

### D1. Respuesta de cada consulta y destino del texto

| Q | Respuesta verificada | Destino |
|---|---|---|
| Q1 | Corrida telefonica el 5-10 (25 casos) y el 6-10 (56 casos); ~2 h y ~3 h (5 h total); horas de reloj exactas no constan | 1.8, 4.5, leyenda de la figura telefonica y cronograma pasan a "5 y 6 de octubre" |
| Q2 | Imagen/flujo desplegado para los 56 casos del 6-10: **no consta** (la fecha de despliegue no esta en git) | Texto de 4.5 declara "no consta"; registro lo cierra con ese estado |
| Q3 | Recito el autor Luca Gomez, con lectura **parafraseada**, softphone VoIP en la computadora SF20GM7; el autor confirma que hubo repeticiones (su lista exacta queda como OQ1) | 4.5 nombra al autor y el modo de lectura; el texto declara que hubo repeticiones sin apoyarse en el sidecar como prueba (el sidecar consolida una fila por `case_id` y no evidencia repeticiones) |
| Q4 | Luca corrio `scripts/corpus_ingest/ingest_via_n8n.py` el 2-10 (commits 69b5328, 1d32538, 3840246, 24ab238, todos de lucaGomezB); flags por defecto `--source json` + `--insecure`; `--base-url` por defecto `https://localhost` (nginx); host SMTP en `scripts/corpus_ingest/ingest.env` (gitignored) => **no consta** | 4.5 agrega el autor, los flags y el base-url; el host SMTP se declara "no consta" |
| Q5 | El nodo IMAP declara `everyMinute` (postProcessAction read, UNSEEN + SINCE 24h, trackLastMessageId); el intervalo efectivo no se midio (n8n 2.11.2) => **no consta** | 4.5 conserva "configurado para sondear" y agrega que el intervalo efectivo no se midio |
| Q6 | La reasociacion de la `cache_meta` de `hybrid-v3` al hash del corpus del 19-10 no esta documentada => no consta | Solo registro; `evaluation/evidence/README.md` ya advierte del desajuste; no cambia la tesis |
| Q7 | Los registros primarios (base operativa, respaldo del 9-10, ejecuciones de N8N) **no se conservan en el repositorio** | Anexo F lo declara; los sidecars se versionan (D4) |
| Q8 | Nginx: la medicion telefonica (5-6/10) corrio sobre el perfil aislado `corpus` SIN proxy; la ingesta del 2-10 corrio sobre el stack base CON Nginx | Distinguir ambos despliegues en los tres pasajes (D6) |

Criterio: la respuesta "no consta" se escribe tal cual en el texto cuando el dato es material para el lector; cuando no lo es (Q6), alcanza con cerrarlo en el registro. Ninguna respuesta se deduce de un valor que el repositorio no respalde.

### D2. OQ1-B: el Anexo I como autoevaluacion de control de calidad interno

El primer parrafo de `sec:anexo-trazabilidad` (`12-anexos.tex:183`) ya declara que los dictamenes son revisiones evaluativas previas a la defensa, solicitadas por los autores, con el perfil `Prompt2.docx` aplicado mediante un modelo de lenguaje, no vinculantes y conservados en `auditorias/`. c-161 **agrega** el angulo de autoevaluacion: que constituyen un control de calidad interno frente a criterios de la CONEAU, pedido por los propios autores, y no una revision por pares. No se quita ninguna de las declaraciones de c-160 ni se cambian los hechos.

Alternativas: (a) dejarlo como esta en c-160 - RECHAZADA: el autor pidio reforzar el encuadre; (b) presentarlo como revision externa - RECHAZADA: induciria a suponer un evaluador humano independiente, que el repositorio no respalda.

### D3. Figura 2: Mermaid como fuente unica; retiro del drawio

`fig:arquitectura` se genera desde `docs/diagrams/arquitectura_sistema.md` (cinco capas, tres canales). El `Diagrama de Capas.drawio` (y su `.png`) es obsoleto (N8N 1.62, Gemini 2.5, sin frontend) y no alimenta ninguna figura de la tesis. Se **archiva** en `docs/diagrams/archive/` (o se retira) para no perder el original, y se actualizan la mencion del registro (`dictamen-correcciones.md:3188`) y la pregunta a Lucas para que no lo presenten como fuente vigente.

Alternativas: (a) actualizar el drawio - RECHAZADA por el autor (Figura 2 = A); (b) borrarlo sin archivar - RECHAZADA: se pierde el original sin necesidad. El PNG de la figura NO se regenera (sin `mmdc` en el alcance).

### D4. Versionado de los sidecars sin PII

Se reemplaza la regla `.gitignore` (`data/corpus_resultados*.json`) por una que versiona los sidecars COMPLETOS (`corpus_resultados.json` 200 filas y `corpus_resultados_telefonia.json` 81 filas) y excluye por defecto el resto, en particular el de N8N. Se verifica que ninguno de los versionados contiene descripciones (solo `case_id`, `canal`, `incidente_id`, `sector` o equivalentes, marcas temporales y latencias). `data/README.md` los mueve de "artefactos de corrida no versionados" a "versionados, por que" (y declara el de N8N como excluido por OQ2). Se coherentizan `docs/como_cargar_datos_corpus.md`, `scripts/corpus_ingest/README.md` y `knowledge-base/09_decisiones_y_supuestos.md`.

**Caveat (BLOQUEANTE para el `git add`)**: `data/corpus_resultados_n8n.json` local tiene 4 filas frente a los 119 casos de la corrida del 2-10. No se commitea ese sidecar hasta resolver cual artefacto es autoritativo (OQ2); si el autor no aporta el artefacto completo, se versionan solo los sidecars completos (200 y 81 filas) y el de N8N queda declarado sin versionar. El change no decide de forma implicita.

### D5. Q4/Q5/Q7 textuales

- 4.5: el apartado de procedencia agrega quien corrio el harness (Luca), los flags por defecto (`--source json`, `--insecure`), el `--base-url` por defecto `https://localhost` a traves de Nginx, y declara que el host SMTP del arnes vive en `scripts/corpus_ingest/ingest.env` (gitignored), por lo que **no consta**.
- 4.5: el disparador IMAP conserva "configurado para sondear el buzon una vez por minuto" (configuracion declarada) y agrega que el intervalo efectivo no se midio en n8n 2.11.2 => **no consta**.
- Anexo F (`12-anexos.tex:96`): los registros primarios se declaran **no conservados en el repositorio** (hoy dice "no estan versionados"), a la espera de una eventual exportacion de los autores (OQ3).

### D6. Correccion Nginx (distinguir los dos despliegues)

Los tres pasajes pasan a distinguir: (i) la medicion telefonica del 5 y 6 de octubre corrio sobre el perfil Compose aislado `corpus`, que **no incluye** el proxy inverso Nginx (test-guarded: `test_base_services_are_not_part_of_the_corpus_profile`), con su propio tunel a `backend-corpus`; (ii) la ingesta del brazo automatico del 2 de octubre corrio sobre el stack base, que **si incluye** Nginx con certificado autofirmado de referencia (de alli el `--insecure` del harness). Se conserva que la terminacion TLS 1.2/1.3 esta verificada (automaticamente) solo sobre el despliegue de referencia, no sobre las instancias de la campana, y que las mediciones **no dependen de TLS**. El matiz deja de ser "no incluyo el proxy" (incorrecto para el 2-10) o "si incluyo el proxy" (incorrecto para telefonia): pasa a ser una distincion por despliegue. Esto MODIFICA los dos requisitos vivos (D8). La Tabla 18 del capitulo 10 no cambia: su afirmacion sobre TLS es compatible.

### D7. Registro y roadmap

`dictamen-correcciones.md`: seccion nueva "## Dictamen v10 / v1.2.5 (2026-10-28) - c-161" que cierra las consultas Q1-Q8 (lineas 3103-3110) con su estado, registra la correccion Nginx, la decision de la Figura 2 y el versionado de los sidecars, sin reescribir las entradas provisionales previas. `CHANGES.md`: FASE 49 con el bloque de c-161 (Scope, Verificacion, Rollback, Dependencias y Leer antes) y actualizacion de los conteos del pie.

### D8. Estrategia del delta de especificacion

Se usa MODIFIED donde un requisito vivo prescribe el texto que este change cambia, para que el spec no quede contradictorio al archivar:
- "Naturaleza de los dictamenes declarada en el Anexo I" (encuadre de autoevaluacion).
- "Procedencia de los datos del brazo automatizado declarada en el protocolo de pruebas" (los datos faltantes pasan de marcadores a "no consta").
- "Descripcion exacta del tiempo telefonico y de la fuente del cronograma" (fechas 5 y 6 de octubre).
- "Figura de arquitectura del sistema de cinco capas y tres canales desde fuente versionada" (fuente unica; retiro del drawio).
- "Declaracion acotada del endurecimiento tecnico" y "Coherencia técnica entre la tesis y el sistema implementado" (distinguir los dos despliegues: telefonia en perfil aislado sin Nginx; ingesta del 2-10 en stack base con Nginx).

Todo lo demas va como ADDED: el cierre verificado de Q1-Q8 en `tesis-document` y el versionado de los sidecars en `corpus-n8n-ingest`.

### D9. Presupuesto de paginas

El cambio es de texto acotado: autores, flags, "no consta", tres correcciones Nginx y el encuadre del Anexo I. Impacto previsto neutro (0 a +1 pagina sobre las 109 posteriores a c-160). Se mide con `abspage@last` o `pdftotext` y se registra en el libro mayor conforme al requisito "Presupuesto de paginas preservado". Si supera +1, se compacta el encuadre del Anexo I sin retirar contenido.

## Risks / Trade-offs

- [Escribir un dato no confirmado como cierto] -> Toda respuesta no verificable se declara "no consta"; las cifras provienen de la sesion del autor o del repositorio.
- [Dejar la tesis contradiciendo el repo por Nginx] -> Correccion en los tres pasajes y en los dos requisitos vivos, distinguiendo los dos despliegues (telefonia sin proxy; ingesta del 2-10 con proxy); verificacion con `grep` de "no incluyo el proxy" y de la distincion por despliegue.
- [Equiparar "Nginx corriendo" con "la campana uso Nginx"] -> El perfil `corpus` excluye Nginx (test-guarded); la tesis distingue por despliegue en lugar de afirmar de forma uniforme.
- [Perder el drawio original] -> Se archiva bajo `docs/diagrams/archive/` en lugar de borrarlo.
- [Commitear un sidecar con PII o incompleto] -> Verificacion PII-free previa y pregunta abierta OQ2 antes de `git add` del sidecar de N8N.
- [Contradiccion con c-158..c-160] -> Localizacion por contenido; no se revierten sus ediciones; coherencia final del Anexo I y del registro.
- [Superar el tope de paginas] -> D9; el exceso se registra y se defiende, sin presentarlo como cumplimiento.
- [Falso positivo del escaneo de secretos en el registro] -> Evitar en la prosa nueva la palabra "capitulo" sin tilde seguida de coma o dos puntos y un nombre de archivo (patron conocido de gitleaks); usar "seccion".

## Migration Plan

1. Verificacion previa sobre el arbol posterior a c-160 (presencia de cada marcador, de las tres frases Nginx, del drawio y de los sidecars; linea base de compilacion y paginas).
2. Grupos 2 a 6 de `tasks.md` (Q1-Q8, OQ1-B, Figura 2/drawio, sidecars, Nginx).
3. Cierre: render, compilacion Docker si el cierre lo exige, `verify_citations.py`, registro, `CHANGES.md`, verificaciones finales y `openspec validate --strict`.

Rollback: `git checkout --` de las fuentes `.tex`, del render, del registro, de `.gitignore`, de `data/README.md` y de `CHANGES.md` tocados; restaurar el drawio desde el archivo. Ninguno tiene efecto en runtime.

## Open Questions

- **OQ1 (repeticiones telefonicas, Q3).** El sidecar de telefonia contiene R126 y R002 como repeticiones; la lista exacta de las 81 llamadas recitadas queda por confirmar. El texto describe el modo de lectura y la existencia de repeticiones sin fijar la lista. Diferible.
- **OQ2 (sidecar autoritativo, Q7) - BLOQUEANTE del `git add` de ese archivo.** `data/corpus_resultados_n8n.json` local tiene 4 filas frente a 119 de la corrida del 2-10. Confirmar cual artefacto es autoritativo antes de commitearlo; si no, versionar solo los sidecars completos (200 y 81 filas). No cambia el resto del change.
- **OQ3 (exportacion de registros primarios, Q7).** Si el autor exporta una version pseudonimizada de la base operativa, el respaldo del 9-10 o las ejecuciones de N8N, se versionaria y el Anexo F se ajustaria. Sin export disponible, la tesis declara "no se conservan en el repositorio".
