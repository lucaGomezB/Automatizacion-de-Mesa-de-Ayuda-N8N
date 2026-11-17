# Proposal: Mejorar la legibilidad del capitulo de resultados y de los anexos (M-03, B-01, B-03)

## Why

La devolucion de tercera instancia del tribunal (16-11-2026, sobre `v1.5.2`, 6,7/10) registra que la tesis crecio en extension y perdio legibilidad (**M-03**): paso de 120 a 164 paginas y el cuerpo, de ~43.600 a ~51.900 palabras (+19 %); el capitulo 8 rotula cifras como primaria, complementaria, sensibilidad, cota de alcance, vigente o superada y "el lector no encuentra en un solo lugar que se concluye"; el Anexo J transcribe un memo interno con una columna de estado ("vigente (nuevo)") en el registro de una bitacora; y quedan 85 oraciones de mas de 60 palabras (N-07, parcial). Ademas, los nombres de sector siguen sin tilde en la prosa y en la fuente del cuerpo, mezclados con formas acentuadas (**B-01**, cierre de N-15), y las tablas del Anexo J tienen texto superpuesto en la columna de procedencia y rutas espaciadas letra por letra (**B-03**). La seccion 7 de la devolucion pide atender M-03 (punto 8) y B-01 a B-03 (punto 10) antes de la defensa.

Este change es de **forma**: reorganiza, parte y tipografia. Se aplica **despues** de `c-235` (retiro de la validacion fuera de muestra), `c-236` (balance neto como cota superior) y `c-237` (declaracion de IA del Anexo I.2), sobre el texto ya reducido, y **no cambia ninguna cifra ni ninguna conclusion**.

## What Changes

| Bloque | Que cambia | Gobernanza |
|---|---|---|
| **A. Sintesis del capitulo 8** | Tabla unica de cifras primarias (`tab:sintesis-resultados`) y un parrafo "que se concluye" al abrir el capitulo, despues de los dos parrafos de apertura vigentes y antes de §8.1. Cada fila: cifra, `n`, intervalo, veredicto frente a la hipotesis u objetivo y seccion que la desarrolla. El resto del capitulo deja de repetir esas cifras fuera de su seccion de desarrollo y remite a la tabla. | MEDIA |
| **B. Anexo de sensibilidad y robustez** | Anexo nuevo **K** ("Lecturas de sensibilidad y robustez", `sec:anexo-sensibilidad`), al final de `12-anexos.tex` (no renumera A a J), que recibe las tablas y lecturas secundarias que sobreviven a `c-235`: rango de robustez de tiempos y descuentos de redondeo, sensibilidad al vocabulario ajustado (`subsec:sensibilidad-ajustes`) y las relecturas de la campana complementaria con otro brazo automatizado. En el cuerpo queda la cifra primaria y una remision. Vocabulario de rotulos reducido a tres terminos (primaria, secundaria, sensibilidad) definido una sola vez. | MEDIA |
| **C. Anexo J depurado** | Sin columna "Estado"; sin referencias al "memo" ni a sus secciones (las procedencias apuntan a artefactos versionados y a su comando); tablas con `\caption`/`\label`, columnas `>{\raggedright\arraybackslash}p{}` y claves y rutas partibles con `\path{}` (sin `\texttt{}` con `\_` ni rutas elididas con "..."). Criterio: 0 `Overfull \hbox` en el Anexo J y total del documento menor que 25. | MEDIA |
| **D. Oraciones largas** | 0 oraciones de mas de 60 palabras con `sent_c197.py` en todo `sections/`, mas revision manual de pies de tabla, notas, epigrafes y vinetas con `list_long_c197.py` (que si los incluye). Metodo: partir, nunca borrar contenido sustantivo. Se documenta la diferencia con el conteo del tribunal (85). | MEDIA |
| **E. Nombres de sector** | Par de macros en el preambulo: `\sectorcad{clave}` (cadena del sistema, monoespaciado, sin tilde, byte a byte con `App/Backend/app/constants.py`) y `\sectorprosa{clave}` (nombre en prosa, fuente del cuerpo, con tilde). Todas las menciones de sector en `sections/*.tex` pasan por una de las dos. | MEDIA |
| **F. Extension y verificacion** | Reduccion neta medible del cuerpo frente a `v1.5.2` con un metodo de conteo unico aplicado a ambas; foto de cifras antes/despues sin diferencias; `verify_citations.py` PASS; sin `\autoref`/`\ref` colgantes; compilacion de verificacion en un directorio temporal (la recompilacion versionada es de `c-239`). | MEDIA |

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: se MODIFICAN los requisitos de nomenclatura de sectores (las dos versiones hoy contradictorias pasan a una sola regla con macros), del Anexo de numeros canonicos (sin columna de estado ni referencias al memo, con formato que no desborda), de oraciones acotadas (de los capitulos 1, 4, 8 y 9 a todo el documento, con revision manual de pies y notas) y de la ubicacion del analisis de sensibilidad al ajuste (pasa al anexo K con remision desde el capitulo 8); y se AGREGAN los requisitos de tabla de sintesis del capitulo 8, anexo de sensibilidad y robustez con vocabulario minimo de rotulos, y reduccion medible de la extension.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` | Modificado | Tabla de sintesis y parrafo de conclusion; traslado de lecturas de sensibilidad; remisiones en lugar de cifras repetidas; oraciones partidas; sectores con macros |
| `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` | Modificado | Anexo J depurado; anexo K nuevo al final |
| `docs/Tesis/v10 (IA)/paper/sections/01`, `04`, `05`, `08`, `09`, `10` y demas `.tex` | Modificado | Oraciones partidas; sectores con macros; remisiones a las etiquetas trasladadas (que conservan su nombre) |
| `docs/Tesis/v10 (IA)/paper/preambles/preamble.tex` | Modificado | Macros `\sectorcad` y `\sectorprosa` |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Registro de c-238: lineas base y resultados de cada medicion, inventario de traslados y de oraciones partidas |
| `docs/Tesis/Correcciones/foto-cifras-c238-antes.txt` / `-despues.txt` | Nuevo | Foto de cifras para el cotejo |
| `docs/Tesis/v10 (IA)/tesis_para_agente.md` | Regenerado | Con `build_tesis_para_agente.py` |
| `CHANGES.md` | Aditivo | Entrada c-238 (o consolidada por `c-239`; ver design, Open Questions) |

Sin cambios en `App/`, `n8n/`, `evaluation/`, el corpus, las predicciones ni `numeros-canonicos.md` (salvo que el design lo exija; no lo exige). Cero llamadas a Gemini. Ninguna cifra ni conclusion cambia. La recompilacion versionada (`main.pdf`, `compilacion.md`), el bump de version y el tag son de `c-239`.

## Dependencies

- **Orden de aplicacion:** `c-235` -> `c-236` -> `c-237` -> **`c-238`** -> `c-239`. Este change se aplica sobre el texto ya reducido; los anclajes de linea del design son de `v1.5.2` y se re-localizan por texto al aplicar.
- **Orden de archivo:** `c-235` y `c-236` deben archivarse antes que `c-238`. Si alguno de ellos MODIFICA tambien el requisito "Anexo de números canónicos citados y cuerpo sin referencias internas al memo", el bloque MODIFIED de `c-238` debe reconciliarse con el texto resultante antes del archive (ver design, Riesgos).
- Los requisitos fuera de muestra que `c-235` retira (repeticion de `0,8447`/`0,6893`, sensibilidad a la referencia, arbitraje por mayoria, robustez de la brecha) no se tocan aqui.

## Success Criteria

- [ ] El capitulo 8 abre con `tab:sintesis-resultados` y un parrafo de conclusion; cada cifra primaria aparece en la tabla y en su seccion de desarrollo, y no se repite en prosa en otras secciones del capitulo.
- [ ] Existe el anexo K con las lecturas de sensibilidad y robustez trasladadas; el cuerpo conserva la cifra primaria y la remision; "cota de alcance" no aparece en el capitulo 8 y los rotulos se reducen al vocabulario definido.
- [ ] El Anexo J no tiene columna de estado ni la palabra "memo"; la compilacion de verificacion da 0 `Overfull \hbox` en el Anexo J y menos de 25 en total.
- [ ] `sent_c197.py` informa 0 oraciones de mas de 60 palabras (salvo la portada, que no es prosa) y `list_long_c197.py ... 60` solo lista filas de datos de tablas.
- [ ] Ninguna mencion de sector queda fuera de `\sectorcad`/`\sectorprosa` en prosa; las cadenas del sistema coinciden byte a byte con `constants.py`.
- [ ] El cuerpo se reduce segun la meta del design, medido con el mismo metodo en `v1.5.2` y al cierre.
- [ ] Foto de cifras antes/despues sin diferencias; `verify_citations.py` PASS; 0 referencias indefinidas en la compilacion de verificacion.
- [ ] `openspec validate c-238-mejorar-la-legibilidad-de-resultados-y-anexos --strict` pasa.
