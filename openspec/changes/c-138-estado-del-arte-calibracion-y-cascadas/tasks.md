> Gobernanza LOW (documental, aditivo, reversible). Decisiones en `design.md` (D1-D11). Rutas `sections/...` relativas a `docs/Tesis/v10 (IA)/paper/`.
> Modo de ejecucion: Strict TDD no aplica (cambio documental sin test runner para prosa ni `.bib`, mismo criterio que c-110); las compuertas son la verificacion por fuente, `verify_citations.py`, la compilacion, los `grep` de cada tarea y el conteo de paginas.
> Orden: los bloques 1-6 y 8 no tienen dependencias duras; el bloque 7 requiere `c-130` y `c-131` aplicados. NO se edita la oracion de Xuan et al. (`c-139`) ni la del umbral de 0,70 (`c-130`), ni `tab:trabajos-academicos`/`tab:comparativa` (`c-135`).

## 1. Linea base y prerrequisitos (solo lectura)

- [ ] 1.1 Confirmar rama `ramagonzalo` y arbol limpio (`git status --porcelain` vacio) y registrar la linea base: paginas del PDF (`pdfinfo main.pdf | grep Pages` en el contenedor `texlive-thesis`, o en el host `pdftotext main.pdf - | tr -cd '\f' | wc -c`; esperado 101), `grep -c "^@" "docs/Tesis/v10 (IA)/Bibliography_base.bib"` (esperado 59) y `python "docs/Tesis/v10 (IA)/verify_citations.py"` (esperado PASS)
- [ ] 1.2 Registrar la holgura de la ultima pagina de los capitulos 2, 3 y 9 y de la bibliografia (paginas localizadas en `main.toc`; lineas hasta el ultimo texto con `pdftotext -f N -l N -layout main.pdf -`) y compararla con la de `design.md` (Context); si difiere por cambios de otros changes, recalcular el impacto esperado de D8
- [ ] 1.3 Registrar el estado de los changes vecinos: (a) presencia de la oracion de Xuan et al. en 2.5 (`grep -n "xuan2025mmluprox" sections/02-marco-teorico.tex`); (b) si `c-130` esta aplicado (terminologia de puntaje de correctitud y confianza por etapa en los capitulos 2, 5 y 6); (c) si `c-131` esta aplicado (`grep -n -i "invertida\|anti-calibr" sections/07-resultados.tex` sin coincidencias); (d) si alguna clave del registro de D3 ya existe (`grep -n "Guo2017_calibration\|Zhao2021_calibrate_before_use\|Tian2023_verbalized_confidence\|Xiong2024_confidence_elicitation\|Varshney2022_model_cascading\|Chen2024_frugalgpt" "docs/Tesis/v10 (IA)/Bibliography_base.bib"`), en cuyo caso se reutiliza

## 2. Busqueda de la extension C1-C2 (D1)

- [ ] 2.1 Fijar `FECHA_CORTE_C` (fecha de ejecucion, posterior al 21-10-2026) y ejecutar C1 y C2, con las cadenas exactas de D1, en Scopus, IEEE Xplore, ACM Digital Library, ACL Anthology, Google Scholar y arXiv; para las bases por suscripcion registrar los trabajos examinados e incorporados (convencion de la bitacora c-110); verificar que cada par base-cadena tiene fecha y resultado
- [ ] 2.2 Aplicar los criterios del grupo C y la regla de seleccion de D1; registrar las excluidas con su motivo (al menos Kadavath et al. 2022, preprint no arbitrado, y la version arXiv de FrugalGPT, sustituida por la de TMLR); si un resultado es mas proximo al escenario de la tesis que una fuente nucleo, sustituirla segun D2 y verificar la sustituta en el bloque 3
- [ ] 2.3 Revisar los resultados contra dos condiciones: (a) un trabajo arbitrado que evalue una cascada de reglas y LLM con confianza verbalizada sobre tickets de soporte en espanol (si existe, no enunciar la vacancia de 3.x); (b) un trabajo arbitrado 2023-2026 que evalue Gemini sobre tickets en espanol (si existe, DETENER la aplicacion y reportarlo al orquestador: afecta la vacancia A4, fuera de alcance)
- [ ] 2.4 Extender `docs/Tesis/Correcciones/bitacora-busqueda-c-110.md`: encabezado con la extension c-138 y `FECHA_CORTE_C`; seccion "Grupo C" con cadenas C1-C2, criterios, regla de seleccion y tabla base/cadenas/fecha/resultado; verificar con `git diff` que no cambia ningun registro de los grupos A y B

## 3. Verificacion de las fuentes (D3, D4)

- [ ] 3.1 Fuentes con DOI (Tian et al. 2023: `10.18653/v1/2023.emnlp-main.330`; Varshney y Baral 2022: `10.18653/v1/2022.emnlp-main.756`): `curl -sI https://doi.org/<doi>` devuelve 302 hacia aclanthology.org y `curl -s https://api.crossref.org/works/<doi>` coincide en titulo, autores, sede, ano y paginas (5433-5442; 11007-11021)
- [ ] 3.2 Fuentes sin DOI: Guo et al. 2017 y Zhao et al. 2021 (pagina PMLR con respuesta 200 y metadatos `citation_*`: PMLR 70:1321-1330 y PMLR 139:12697-12706); Xiong et al. 2024 (foro `https://openreview.net/forum?id=gjeQKFxFpZ` segun MLAnthology y encabezado "Published as a conference paper at ICLR 2024" del PDF); Chen et al. 2024 (listado y `.bib` oficiales en `https://jmlr.org/tmlr/papers/bib/cSimKw5p6R.bib`: TMLR, 2024, ISSN 2835-8856)
- [ ] 3.3 Leer el texto completo de cada fuente y completar en la bitacora la tabla de correspondencia afirmacion-fuente (afirmacion, seccion o pagina) limitada al mapa de D4; toda afirmacion no hallada se reformula o la fuente se sustituye desde la reserva, repitiendo 3.1-3.3 para la sustituta
- [ ] 3.4 FrugalGPT en TMLR: si el PDF de OpenReview exige verificacion anti-bot, NO evadirla; pedir al usuario la descarga o, si no es posible, registrar en la bitacora que el contenido se verifico sobre arXiv:2305.05176v1 y limitar la atribucion al concepto de cascada con funcion de puntaje y umbral
- [ ] 3.5 Registrar en la bitacora la tabla de verificacion por fuente (clave, DOI o URL, resultado de la resolucion, cotejo de metadatos, fecha) y verificar que hay exactamente una fila por fuente incorporada

## 4. Bibliografia (D10)

- [ ] 4.1 Agregar el bloque comentado "CALIBRACION DE LA CONFIANZA Y CASCADAS DE MODELOS" a continuacion del bloque HITL de c-110, con las claves fijadas en D3 y los tipos de D10 (omitir las que ya existan segun 1.3d); verificar `grep -c "^@" "docs/Tesis/v10 (IA)/Bibliography_base.bib"` = 59 + entradas nuevas (65 si se agregan las seis)
- [ ] 4.2 Verificar unicidad: para cada clave nueva, `grep -c "{<clave>," "docs/Tesis/v10 (IA)/Bibliography_base.bib"` = 1
- [ ] 4.3 Verificar que el diff de `Bibliography_base.bib` solo agrega lineas (`git diff --numstat` con 0 lineas borradas)

## 5. Marco teorico, seccion 2.5 (D5)

- [ ] 5.1 Insertar, inmediatamente despues de la oracion que empieza "La calibraci" (O2) en `sections/02-marco-teorico.tex`, las oraciones de fundamentacion: medicion con diagramas de fiabilidad y ECE y correccion posterior (`Guo2017_calibration`); confianza verbalizada de LLM consultados como servicio, sobreconfianza y dependencia de la elicitacion (`Xiong2024_confidence_elicitation`, `Tian2023_verbalized_confidence`); verificar con `git diff` que las oraciones O3 (Xuan et al.) y O4 (umbral) no cambian y que lo agregado no contiene `xuan2025mmluprox`
- [ ] 5.2 En la oracion que menciona "un esquema h.brido que combine ambas estrategias", agregar la nocion de cascada (el componente economico resuelve cuando su senal de fiabilidad alcanza un umbral y deriva el resto al mas costoso) con `Varshney2022_model_cascading` y `Chen2024_frugalgpt`; verificar `grep -c "Varshney2022_model_cascading" sections/02-marco-teorico.tex` >= 1
- [ ] 5.3 Verificar el presupuesto de D8 (agregado de 2.5 <= 8 lineas, estimado como caracteres agregados / 95) y que lo agregado no contiene cifras

## 6. Estado del arte, capitulo 3 (D1, D6)

- [ ] 6.1 Extender el parrafo "Protocolo de revisi..." con C1-C2, los criterios del grupo C, la regla de seleccion y `FECHA_CORTE_C`, sin alterar A1-A4, B1 ni el corte del 21-10-2026; verificar que las cadenas C1 y C2 del texto coinciden con las de la bitacora salvo el formato LaTeX
- [ ] 6.2 Actualizar la oracion introductoria del capitulo para enumerar cuatro areas, incluida la calibracion de la confianza y las cascadas de modelos; verificar que la cantidad enunciada coincide con las areas que el capitulo revisa
- [ ] 6.3 Insertar `\subsection{...}\label{subsec:calibracion-cascadas}` entre el final de 3.3 y `\subsection{An.lisis comparativo y brecha identificada}`: un parrafo de calibracion (Guo, Zhao, Tian, Xiong) y uno de cascadas (Varshney y Baral, Chen et al.) dentro del mapa de D4, con cierre de vacancia acotada solo si 2.3(a) lo permite; verificar `grep -c "subsec:calibracion-cascadas" sections/03-estado-del-arte.tex` = 1 y que cada clave nueva aparece citada en el capitulo 2 o en el 3
- [ ] 6.4 Verificar que el diff de `sections/03-estado-del-arte.tex` no toca `tab:trabajos-academicos`, `tab:comparativa`, la oracion del "desplazamiento" hacia LLM ni la vacancia A4, y que el agregado del capitulo es <= 30 lineas

## 7. Discusion, seccion 9.2 (D7) - requiere c-130 y c-131 aplicados

- [ ] 7.1 Confirmar los prerrequisitos con 1.3(b) y 1.3(c); si alguno falta, dejar este bloque pendiente con el motivo registrado y continuar con el bloque 8 (el change no se archiva hasta completarlo)
- [ ] 7.2 Insertar el parrafo de contraste inmediatamente antes del parrafo que empieza "La novedad del aporte radica", con el contenido minimo de D7, la terminologia de `c-130` y remisiones a `\autoref{subsec:calibracion}` y `\autoref{subsec:calibracion-cascadas}`; presupuesto <= 7 lineas
- [ ] 7.3 Verificar que (a) toda cifra del parrafo figura en `docs/Tesis/Correcciones/numeros-canonicos.md` o es de terceros citada textualmente con pagina; (b) `grep -n -i "invertida\|anti-calibr" sections/08-discusion.tex` no devuelve coincidencias nuevas; (c) el parrafo no afirma contrastada la eficiencia del esquema hibrido

## 8. Compilacion y verificacion global

- [ ] 8.1 Ejecutar `python "docs/Tesis/v10 (IA)/verify_citations.py"` y verificar STATUS PASS con cero citas huerfanas y cero entradas sin usar
- [ ] 8.2 Compilar en el contenedor (`docker run --rm -v "$PWD/docs/Tesis/v10 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`) y verificar en `main.log` cero errores fatales y cero referencias o citas indefinidas, y en `main.blg` cero advertencias de claves duplicadas
- [ ] 8.3 Medir las paginas despues del change y registrar aqui el antes/despues y los capitulos que crecieron; si el aumento atribuible supera +3, aplicar la contingencia de D8 (reducir 9.2 a dos oraciones; retirar Tian et al. y luego Varshney y Baral, con sus citas y entradas) y recompilar
- [ ] 8.4 Confirmar con `git diff --stat` que solo cambiaron los cinco archivos del alcance (`02-marco-teorico.tex`, `03-estado-del-arte.tex`, `08-discusion.tex`, `Bibliography_base.bib`, `bitacora-busqueda-c-110.md`) y que no se tocaron `07-resultados.tex`, `numeros-canonicos.md` ni `evaluation/`
- [ ] 8.5 Verificar la consistencia final texto-bitacora (bases, cadenas, criterios, fecha de corte y claves incorporadas) y que cada clave nueva citada figura en la tabla de correspondencia afirmacion-fuente
