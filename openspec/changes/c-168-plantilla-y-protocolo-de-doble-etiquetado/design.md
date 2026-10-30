# Design: Plantilla y protocolo de doble etiquetado

## Context

El corpus solo conserva el consenso `sector_asignado`/`sectores_adicionales`; no hay
etiquetas por etiquetador, por lo que la tabla primaria de acuerdo no existe
(`docs/Tesis/Correcciones/numeros-canonicos.md:198-209`). Los dos analistas originales
resolvieron sus discrepancias por consenso y son los mismos que operaron el brazo manual
(`docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex:55`). La revision
pre-apply (`docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md`, T1 y T2) pidio
un esquema unico de planilla con dueno c-168, un validador unico y un protocolo que no
reutilice a esos sujetos. El etiquetado real corre fuera del repositorio; aqui solo se
entrega el enabler offline.

Hechos del codigo que condicionan el diseno:

- `evaluation/corpus.py:52-58` define `SECTORES_CANONICOS` (tupla de las cinco cadenas) y
  `CATEGORIAS_VALIDAS`.
- `cargar_corpus(path)` (`evaluation/corpus.py:183`) devuelve una `List[CasoEvaluacion]`
  (no un objeto con `metadata`) y, si `metadata.total_casos` esta desincronizado, lo
  normaliza reescribiendo el archivo. Ya valida la regla "el principal no se repite en
  los adicionales" para el consenso.
- El fixture `evaluation/tests/fixtures/corpus_fixture.json` tiene ids `1..9` (sin
  prefijo), el corpus real `R001..R200`, y el corpus independiente de c-166 usara `I...`.
- `evaluation/data/README.md` hoy afirma que no se trackea ningun CSV en esa carpeta.
- La suite corre con `pytest` desde `evaluation/` (`evaluation/pytest.ini`,
  `testpaths = tests`; job de CI con `working-directory: evaluation`).

## Goals / Non-Goals

**Goals:**
- Fijar el esquema UNICO de la planilla etiquetador x caso (C1) y el validador UNICO,
  adoptados por c-165, c-166 y c-167.
- Entregar plantilla, validador offline con CLI, README de versionado de la tabla
  primaria y runbook de sujetos/cegado/codebook.

**Non-Goals:**
- Ejecutar el etiquetado o recolectar datos de campo (fuera del repo).
- Calcular kappa, IC o exactitud del brazo manual (eso es c-167).
- Kappa de Fleiss o mas de dos etiquetadores (fuera de alcance, declarado).
- Importar automaticamente tablas parciales recuperadas (no hay codigo de importacion).

## Decisions

### D1. Capability reutilizada
c-168 AGREGA ECM-008, ECM-009 y ECM-010 a `evaluation-campaign-instrumentation` (c-165
crea ECM-001..003; c-166 agrega ECM-004..007). Se descarta una capability propia para no
fragmentar el instrumento de campana. Orden de archivo seguro: c-165 -> c-166 -> c-168.
Orden de aplicacion recomendado: c-168 antes de la tarea 1.x de c-165, porque el
instrumento del brazo manual adopta este esquema y este validador.

### D2. Esquema unico C1, formato largo (tidy)
Una fila por `(id_caso, id_etiquetador, tarea)`, columnas en orden: `id_caso`,
`id_etiquetador`, `tarea`, `sector_etiquetado`, `sectores_adicionales_etiquetados`,
`inicio`, `timestamp`. CSV UTF-8, separador `,`, encabezado obligatorio. Se descarta la variante
JSON de la version anterior: una sola representacion evita dos fuentes de verdad. El
formato largo encaja con validacion por registro y con el consumo de c-167.

### D2b. Columna `inicio` y significado de `timestamp` (extension del orquestador)
`inicio` (ISO-8601 con zona) va antes de `timestamp`, y `timestamp` pasa a significar el
FIN de la clasificacion del caso. Para `brazo_manual` `inicio` es obligatorio y
`inicio <= timestamp` (regla (j), exit code 19): c-167 estima el efecto de orden sobre el
tiempo del operador con `duracion_s = timestamp - inicio`, y sin `inicio` no hay
variable respuesta. Para `doble_etiquetado` `inicio` es opcional y puede ir vacio; si se
informa, la regla (g) valida su formato y la regla (j) exige `inicio <= timestamp`
(decision de este change, para no admitir duraciones negativas en ninguna tarea). La
igualdad `inicio = timestamp` se admite (duracion cero) y su tratamiento analitico queda
en c-167.

### D3. Renombre de columna
La columna del etiquetador se llama `sector_etiquetado` (y
`sectores_adicionales_etiquetados`), no `sector_asignado`. `sector_asignado` queda
reservado al consenso del corpus. Con esto ECM-010 ("los etiquetadores no ven
`sector_asignado`") deja de ser ambiguo y c-167 no confunde etiqueta con referencia.

### D4. Cadenas canonicas importadas
El validador importa `SECTORES_CANONICOS`/`CATEGORIAS_VALIDAS` de `evaluation.corpus`.
MUST NOT declarar constantes propias con las cinco cadenas (la tarea 2.5 anterior
invitaba a duplicarlas). La spec enumera las cinco cadenas exactas solo como criterio de
aceptacion.

### D5. Separador interno `|`
`sectores_adicionales_etiquetados` es una lista separada por `|` (sin espacios
alrededor), vacia cuando no hay adicionales. `|` no aparece en ninguna cadena canonica y
no colisiona con el separador `,` del CSV, por lo que no requiere comillas.

### D6. Etiquetadores fijos y cobertura segun la tarea
- `tarea = doble_etiquetado`: el conjunto de `id_etiquetador` MUST tener exactamente dos
  alias distintos y cada uno MUST cubrir todos los casos del corpus. Un tercer alias
  falla (Fleiss queda fuera del alcance).
- `tarea = brazo_manual` (decision del orquestador): MUST aparecer AMBOS operadores
  `O1` y `O2`, cada uno con al menos un registro, y ningun tercero; cualquier otro alias
  (p. ej. `O3`) o la ausencia de uno de los dos falla por la regla (a) (codigo 10). Una
  planilla con un solo operador que cubra todos los casos FALLA, porque el diseno de la
  tesis tiene dos operadores y c-167 compara por operador. Cada `id_caso` del corpus
  MUST estar cubierto por AL MENOS UN operador; la cobertura doble NO es obligatoria.
  Rige como maximo un registro por `(id_caso, id_etiquetador)` (regla (c)).
Asi el brazo manual puede repartir los casos entre los dos operadores sin duplicar el
esfuerzo, y el doble etiquetado conserva la tabla completa que exige el kappa.

### D7. Lista negra de PII y forma del alias
La planilla MUST NOT contener columnas `nombre`, `email`, `correo`, `legajo`,
`telefono` ni `descripcion` (comparacion sin distinguir mayusculas). Ademas, como
defensa contra nombres cargados en `id_etiquetador`, el alias MUST tener la forma
`E<n>` para `doble_etiquetado` y `O<n>` para `brazo_manual` (decision de este change
dentro de la regla (h)).

### D8. Casos objetivo desde el corpus indicado
El conjunto de casos objetivo son los `id` de `cargar_corpus(ruta)` (una lista de
`CasoEvaluacion`), y `casos_objetivo = len(casos)`. Sirve igual para el corpus de ajuste
(`R...`), el independiente de c-166 (`I...`) y el fixture (`1..9`): el validador no
impone prefijos por regex, solo pertenencia al corpus. La funcion pura recibe
`corpus: Sequence[CasoEvaluacion]` ya cargado; solo el CLI llama a `cargar_corpus`.

### D9. Validador puro + CLI con exit codes por ofensa
`validar_doble_etiquetado(registros: Sequence[dict], corpus: Sequence[CasoEvaluacion],
tarea: str) -> ResultadoValidacion`, con `ResultadoValidacion` como dataclass inmutable
(`ofensas`: lista de `Ofensa(regla, id_caso, id_etiquetador, detalle)`; `resumen`:
`n_casos`, `n_registros`, `etiquetadores`; propiedad `valida`). El CLI
`python -m evaluation.doble_etiquetado --planilla RUTA --corpus RUTA --tarea TAREA` lee
el CSV con `csv.DictReader`, imprime las ofensas y sale con `0` si no hay ofensas, o con
el codigo de la primera regla ofendida en orden (a)-(j): (a) 10, (b) 11, (c) 12, (d) 13,
(e) 14, (f) 15, (g) 16, (h) 17, (i) 18, (j) 19; `2` para errores de uso o archivo ilegible. Los
codigos concretos se fijan aqui para que c-165/c-166 puedan encadenarlos en sus scripts.

### D10. Tabla primaria versionada con SHA-256
La planilla validada se versiona sin PII en `evaluation/data/campana/doble_etiquetado.csv`
junto a `evaluation/data/campana/README.md` (SHA-256, fecha, corpus y su hash, comando de
validacion, estado del cegado), patron `evaluation/evidence/`. `.gitattributes` fuerza LF
en esos CSV para que el hash coincida entre sistemas. Al aplicar c-168 el CSV aun no
existe: el README queda con el procedimiento y el test de integridad se omite (skip)
mientras el archivo no exista; cuando exista, el test exige que pase el validador y que
su SHA-256 coincida con el del README. Su conservacion es criterio de aceptacion de la
campana; la cita en `numeros-canonicos.md` la hace c-169 al incorporar resultados.

### D11. Consenso = coincidencia; discordancias no se resuelven para el kappa
El kappa de Cohen (c-167) se calcula sobre `sector_etiquetado` de E1 vs E2 sin
resolucion posterior de discordancias. La referencia para medir el brazo manual (c-167)
se define como los casos donde `sector_etiquetado` de E1 y E2 coinciden; los discordantes
quedan fuera de la referencia y se reporta cuantos son. Trade-off: la referencia queda
sesgada hacia casos mas faciles; c-167 debe reportar el n excluido.

### D12. Sin importador
Se elimina el importador de la version anterior (no tenia requisito ni formato de
entrada real). El runbook describe como transcribir a mano una tabla parcial recuperada
al esquema C1 y pasarla por el mismo validador.

### D13. Sujetos y cegado (C2)
E1/E2 MUST ser personas distintas entre si, distintas de los dos analistas originales,
de los autores de la tesis y de los operadores del brazo manual (`O*`). Cegado: no ven
`sector_asignado` ni `sectores_adicionales` del corpus, ni la prediccion del
clasificador, ni las etiquetas del par; reciben solo `id_caso` y la descripcion
pseudonimizada. El runbook mantiene `evaluation/data/campana/registro_sujetos.csv` sin
nombres, con columnas `alias, rol, persona` (`rol` en `etiquetador`, `operador`,
`analista_original`, `autor`; `persona` es un codigo seudonimo `P<n>` estable entre
roles, cuya correspondencia con identidades custodia el director fuera del repositorio).
c-167 lo consume para rechazar solapes, que se detectan por `persona` (misma persona con
roles incompatibles). La columna `persona` fue adoptada en el contrato compartido por el
orquestador y propagada a c-165 y c-167: sin un identificador estable entre roles el
solape no es detectable, porque los alias son especificos de cada rol.

### D14. Codebook
No existe en el repositorio un codebook conservado del etiquetado original (grep de
`codebook` sin resultados en `docs/` y `knowledge-base/`). El runbook arma un codebook
operativo con las fuentes ya versionadas y lo congela antes de etiquetar:
`openspec/specs/sector-taxonomy/spec.md` (TAX-001, vocabulario y alcance de `Sistemas`),
`docs/anexo_f_corpus.md` (verdad multietiqueta e invariantes),
`knowledge-base/05_reglas_de_negocio.md` (RN-CL-01) y el criterio de etiqueta primaria
para casos multicategoria de `04-marco-metodologico.tex:53`. MUST NOT usar como codebook
materiales del clasificador (`docs/prompt_gemini.txt`, mapa de keywords), porque
expondrian el criterio del sistema evaluado. Que este codebook sea "el mismo" que el
original no es verificable y se declara.

### D15. Limitacion declarada
Si por restricciones de campo no se consiguen etiquetadores nuevos, el README de la tabla
registra `estado_cegado: limitacion_declarada` con el motivo y los roles solapados, y
c-169 lo reporta asi. MUST NOT presentarse como cegado. Valor por defecto esperado:
`estado_cegado: cumplido`.

## Lo que NO cambia

- `docs/Tesis/v9 (IA)/` (congelada) y el texto de la tesis (lo actualiza c-169).
- Las cinco cadenas canonicas y `evaluation/corpus.py`.
- El corpus `data/corpus_evaluacion_pseudonimizado.json` y su hash.
- Los numeros canonicos (`kappa = 0,87` sin IC sigue vigente hasta la campana),
  `evaluation/predicciones.json` y `evaluation/report.md`.

## Risks / Trade-offs

- [No hay etiquetadores nuevos] -> limitacion declarada obligatoria (D15).
- [Referencia sesgada a casos faciles por excluir discordantes] -> c-167 reporta el n
  excluido (D11).
- [Brazo manual con cobertura simple: la exactitud manual por operador se estima sobre
  subconjuntos distintos de casos] -> el reparto de casos entre `O1` y `O2` lo fija el
  plan de campana de c-165/c-166; c-167 reporta la exactitud agregada y por operador con
  su n.
- [Codebook no identico al original] -> declarado (D14).
- [Solapamiento con c-167] -> aqui se define y valida la tabla; c-167 la consume; sin
  logica de kappa en este change.

## Migration Plan

Cambio aditivo (docs + modulo offline), sin migraciones de DB ni de esquema del corpus.
Rollback: eliminar plantilla, validador, tests, fixture, README de `campana/` y runbook,
y revertir las lineas agregadas a los README de carpeta y a `.gitattributes`.

## Open Questions

- Ninguna abierta en este change: la cobertura del brazo manual (D6) y la columna
  `persona` (D13) quedaron decididas por el orquestador.
