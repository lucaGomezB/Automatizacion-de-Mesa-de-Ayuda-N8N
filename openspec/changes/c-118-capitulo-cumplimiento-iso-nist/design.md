# Design — c-118 — Capitulo de cumplimiento ISO/IEC 27001-27002 y NIST CSF 2.0

## Context

Ver `proposal.md` para la motivacion. Estado relevante:

- La tesis compila en EXACTAMENTE 100 paginas (`pdfinfo main.pdf | grep Pages`), que es
  el tope duro. El requisito vigente del spec mide el total del PDF (portada, indices,
  glosario, cuerpo, referencias y anexos) y exige <= 100. Por lo tanto, cualquier
  adicion neta rompe el gate: el capitulo nuevo DEBE ser net-zero en paginas.
- `11-aspectos-legales.tex` es un solo archivo con un `\section` de nivel capitulo
  (clase `article`) y cinco `\subsection`: 11.1 marco normativo, 11.2 principios,
  11.3 transferencia internacional y pseudonimizacion, 11.4 seguridad tecnica,
  11.5 consentimiento/derechos/supervision humana. `main.tex` lo incluye como capitulo 7.
- El gap assessment (`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`)
  contiene: §2 resumen ejecutivo, §3 mapeo ISO 27002 (93 controles en 4 temas), §4
  perfil NIST CSF 2.0 (6 funciones con madurez 0-4), §5 brechas priorizadas y §6
  clasificacion documental/tecnico/organizacional. Es la entrada primaria.
- C-61..C-66 (archivados) implementaron los controles 5.1, 5.2, 5.9, 5.12, 5.13,
  5.24-5.27, 5.31, 8.26, 8.20, 8.22, 8.2, 8.31, 5.14, 5.15-5.18, 8.5, 8.24, 8.8,
  8.28, 8.29, 5.19-5.23, 8.13, 8.14, 5.29, 5.30, 5.33, 5.34, 8.12, 8.15.
- El spec `tesis-document` ya exige (requisito "Presupuesto de paginas preservado")
  total <= 100 y (requisito "Integridad de referencias cruzadas") cero referencias
  indefinidas y cero remisiones duras ("Capitulo N" en prosa).

## Goals / Non-Goals

**Goals:**

- Incorporar a la tesis el mapeo ISO/IEC 27001:2022 + 27002:2022 y NIST CSF 2.0, con
  estado actual, brechas y hoja de ruta, en lenguaje de alineacion.
- Mantener el PDF en <= 100 paginas absorbiendo/reemplazando contenido existente.
- Preservar el contenido cientifico, los numeros canonicos, las 8 figuras, las tablas
  con fuente y todas las correcciones c-102..c-117.

**Non-Goals:**

- NO certificar ni declarar conformidad. NO hay auditoria de certificacion.
- NO duplicar la narrativa juridica del Capitulo 11; el capitulo de cumplimiento la
  referencia, no la repite.
- NO agregar figuras nuevas (el conteo se mantiene en 8) ni tablas sin linea de fuente.
- NO editar `docs/Tesis/Correcciones/numeros-canonicos.md`, `CHANGES.md` ni
  `dictamen-correcciones.md`.
- NO implementar controles nuevos (los changes C-61..C-66 ya estan archivados).

## Decisions

### D1 — Ubicacion: nuevo `\section` de nivel capitulo anexado a `11-aspectos-legales.tex`

Se agrega un segundo `\section{Cumplimiento normativo y alineacion con estandares}` al
final de `11-aspectos-legales.tex` (antes del `\newpage`), de modo que quede como
capitulo inmediatamente posterior al legal (hoy capitulo 7) y empuje Resultados a 8.

- Alternativa descartada: un archivo nuevo `sections/13-cumplimiento-normativo.tex`.
  El prefijo `13-` colisiona con la convencion de numeracion del spec ("el capitulo
  final es 12 (Anexos)") y agrega un `\input` a `main.tex`. La renumeracion por
  `\section` anexado es segura porque el spec ya prohibe remisiones duras ("Capitulo N"
  en prosa) y exige `\autoref` con `\label`.
- Alternativa descartada: un `\subsection` dentro del Capitulo 11. Menos visible en el
  indice para la defensa; el plan (§5.7) pide "nuevo capitulo/seccion".
- El nuevo `\section` lleva `\label{sec:cumplimiento}` para las remisiones internas.

### D2 — Estructura del capitulo y de la tabla de mapeo

Cinco `\subsection`, apoyados en tablas densas (mas informacion por unidad de pagina
que la prosa):

1. `Marco de referencia adoptado` (`\label{subsec:cumplimiento-marco}`): un parrafo que
   declara los estandares adoptados (ISO/IEC 27001:2022 + 27002:2022, NIST CSF 2.0,
   ISO/IEC 27701, Ley 25.326) y la regla de lenguaje. Declara que es una evaluacion de
   alineacion, no una certificacion.
2. `Estado de alineacion con ISO/IEC 27002:2022` (`\label{subsec:cumplimiento-iso}`):
   Tabla `tab:cumplimiento-iso` con columnas `Tema | Controles | Estado | Evidencia /
   brecha principal`. Se agrupan los controles por tema (Organizacional 5.x, Personas
   6.x, Fisico 7.x, Tecnologico 8.x); NO se reproducen los 93 controles uno por uno.
   Estados: "alineado", "parcial", "brecha", "no aplicable al repositorio".
3. `Perfil de alineacion con NIST CSF 2.0` (`\label{subsec:cumplimiento-nist}`): Tabla
   `tab:cumplimiento-nist` con las seis funciones (GV, ID, PR, DE, RS, RC), una
   subcategoria representativa y la madurez 0-4 del gap assessment §4.
4. `Brechas principales y hoja de ruta` (`\label{subsec:cumplimiento-brechas}`): lista
   que cruza cada brecha priorizada (§5) con su estado: cerrada por C-61..C-66 o
   residual. Las brechas organizacionales (personas 6.x, fisicos 7.x, revision
   independiente, segregacion operativa) se declaran responsabilidad de la organizacion
   adoptante.
5. `Alineacion con el marco legal` (`\label{subsec:cumplimiento-legal}`): dos o tres
   oraciones que remiten al Capitulo 11 (`\autoref{subsec:marco-normativo}`,
   `\autoref{subsec:transferencia-internacional}`) sin repetir su contenido.

Cada tabla lleva linea de fuente APA 7 ("Fuente: elaboracion propia a partir del
gap assessment ..."), conforme al requisito de fuentes del spec.

### D3 — Estrategia de neutralidad de paginas (absorcion/reemplazo)

El capitulo nuevo es ~2 paginas; el tope es net-zero. El presupuesto se cierra asi:

- **Reemplazo primario**: se ELIMINA la prosa de `11.4 Seguridad tecnica` (TLS, Fernet,
  respaldos, control de acceso, auditoria) y su evidencia de control se pliega a la
  Tabla `tab:cumplimiento-iso` (tema Tecnologico). La subseccion se reduce a 2-3
  oraciones de remision a la tabla. El mismo contenido tecnico pasa de prosa a filas
  de tabla, que ocupan menos alto.
- **Absorcion de evidencia dispersa**: el resumen ejecutivo (§2), el mapeo (§3), el
  perfil NIST (§4) y las brechas (§5) del gap assessment se condensan EN las tablas
  del capitulo. NO se copia el detalle completo: el gap assessment y el plan siguen
  viviendo como artefactos versionados del repositorio (`docs/cumplimiento/`), a los
  que el capitulo remite.
- **Condensacion de respaldo** (solo si la medicion excede 100): ajustar la prosa
  redundante de `11.2`/`11.3` y del Anexo `12.7 Documentacion operativa`, que en parte
  reitera documentos del repositorio. NUNCA se retiran hechos juridicos exigidos por el
  spec (Twilio previo a la pseudonimizacion, art. 12, plazos ARCO, base de licitud),
  numeros canonicos, figuras ni lineas de fuente de tablas.
- **Regla de medicion**: tras CADA edicion se compila y se mide `pdfinfo main.pdf |
  grep Pages`. La edicion solo se acepta si el total queda <= 100 y las referencias
  indefinidas siguen en 0. Si una edicion excede, se revierte y se refuerza la
  condensacion.
- **Disparo de alerta**: si aun con las tres palancas no se alcanza net-zero, se
  detiene y se escala al autor (no se elimina contenido cientifico para hacer lugar).

### D4 — Regla de lenguaje

Vocabulario obligatorio: "alineado con", "controles mapeados a", "grado de alineacion",
"brecha identificada". Vocabulario prohibido: "certificado", "certificacion obtenida",
"compliant", "conforme", "cumple ISO/NIST". El capitulo incluye una frase explicita:
la evaluacion identifica alineacion y brechas; no constituye certificacion ni auditoria.

### D5 — Secuenciacion

c-118 se aplica DESPUES de c-102..c-117 (no puede retirar ninguna de sus correcciones)
y ANTES de c-111 (el tag `v1.0.0` debe capturar la fuente final). `c-80` es un change
separado y anterior; no se toca.

## Risks / Trade-offs

- **[El capitulo excede el tope de 100 paginas]** → Medicion `pdfinfo` tras cada
  edicion; reemplazo primario de 11.4; condensacion de respaldo; escala al autor si no
  alcanza. No se recorta contenido cientifico.
- **[La renumeracion rompe remisiones internas]** → Solo remisiones via `\label` +
  `\autoref`; verificacion de 0 referencias indefinidas en el log de compilacion.
- **[Lenguaje de certificacion por descuido]** → Grep de terminos prohibidos en la
  verificacion del spec; frase de descargo explicita.
- **[Inconsistencia con el Capitulo 11]** → Remision explicita a las subsecciones
  legales; reutilizar las mismas cifras (Twilio, art. 12, plazos ARCO).
- **[Duplicacion con el gap assessment]** → El capitulo remite a
  `docs/cumplimiento/`; no reproduce el detalle de los 93 controles.

## Migration Plan

1. Aplicar DESPUES de c-102..c-117 y ANTES de c-111.
2. Registrar el conteo de paginas de partida.
3. Redactar el `\section` y las dos tablas; reemplazar 11.4 por la remision.
4. Compilar con la imagen `texlive-thesis`; medir paginas y referencias indefinidas.
5. Rollback: `git checkout -- "docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex"`
   revierte el capitulo completo; el PDF se regenera recompilando. El change no toca
   codigo, CI ni datos, por lo que el rollback es de un solo archivo.

## Open Questions

None. Las tres ambiguedades (ubicacion, insumo del tope, alcance del detalle) se
resolvieron en D1, D3 y D2 respectivamente.
