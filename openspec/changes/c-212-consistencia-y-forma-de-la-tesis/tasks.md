# Tasks: Consistencia y forma de la tesis (change c-212)

Convenciones: `T01/` = `docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex`; `T02/` = `02-marco-teorico.tex`; `T03/` = `03-estado-del-arte.tex`; `T04/` = `04-marco-metodologico.tex`; `T11/` = `11-aspectos-legales.tex`; `T12/` = `12-anexos.tex`; `TG/` = `00-glosario.tex`; `BIB/` = `docs/Tesis/v10 (IA)/Bibliography_base.bib`. "D-n" remite a `design.md`.

**Reglas para todos los grupos.** No commitear hasta el cierre, no pushear, no crear tags. No recompilar el PDF. No modificar `App/`, `n8n/`, `evaluation/`, `data/` ni las cifras canonicas. No tocar `07-resultados.tex`, `08-discusion.tex` ni `09-conclusiones.tex`. No tocar el parrafo de consentimiento E3/E4 de `T11/` (linea 38) ni `.engram/`. Gobernanza MEDIA: solo redaccion, estructura, glosario y bibliografia; ninguna afirmacion nueva sin respaldo.

## 1. Reconocimiento y red de seguridad

- [x] 1.1 Leer el dictamen v1.3.0 y registrar el estado base: `python3 "docs/Tesis/v10 (IA)/verify_citations.py"` debe reportar STATUS PASS con 0 huerfanas y 0 sin usar antes de editar. Aceptacion: PASS registrado como linea base.
- [x] 1.2 Verificar que los DOI de las entradas de 2025 y 2026 resuelven (xuan2025mmluprox, grandury2025laleaderboard, mayorrocher2026spanish, bernalbeltran2025mexicanspanish, ramonferrer2026tripletotext, liu2025tickit, colavito2025benchmarking). Aceptacion: los siete devuelven redireccion 302 al editor; se registra el resultado.
- [x] 1.3 Confirmar la pagina de la atribucion a Zanzotto contra el PDF del articulo. Aceptacion: `citation_firstpage` = 243; la cita usara `p.~243`.
- [x] 1.4 Confirmar que las etiquetas `tab:anexo-trazabilidad*` solo se referencian dentro del bloque del Anexo I y que `sec:anexo-trazabilidad` y `subsec:nota-versiones` se referencian desde otros archivos. Aceptacion: `rg` registrado; el plan de reduccion no rompe remisiones externas.

## 2. Regla de tres vias asimetrica (rec. 7)

- [x] 2.1 Declarar en `T01/`, en el enunciado de la segunda sub-hipotesis, que la regla es asimetrica y que la refutacion se decide con la estimacion puntual sin usar el intervalo, segun D1. Aceptacion: la oracion aparece junto a la definicion de las tres ramas.
- [x] 2.2 Declarar en `T04/`, en el parrafo del analisis de la campana complementaria, la misma asimetria, segun D1. Aceptacion: la oracion aparece junto a la definicion de las tres ramas y se conserva la constancia del denominador posterior.

## 3. Enunciado y veredicto separados y umbral unificado (rec. 8)

- [x] 3.1 Reescribir en `T01/` las sub-hipotesis para dejar solo enunciado, contraste y criterio de falsacion, con remision a resultados; retirar los veredictos y los resultados observados, segun D2. Aceptacion: no queda ninguna expresion de veredicto en el enunciado de las sub-hipotesis.
- [x] 3.2 Unificar en `T01/` la posicion sobre el umbral del 85 % como criterio de exito central del estudio, fijado a priori por los autores, sin atribuirlo a la literatura, segun D2. Aceptacion: desaparece "criterio de exito contingente" y la exclusion del umbral de la definicion del objetivo.

## 4. Objetivos primero y tercero (rec. 9)

- [x] 4.1 Reformular el primer objetivo especifico de `T01/` como comunicacion sincronica, segun D3. Aceptacion: el objetivo 1 no menciona comunicacion asincronica.
- [x] 4.2 Retirar del tercer objetivo especifico de `T01/` la clausula sobre la complejidad operativa percibida, segun D3. Aceptacion: el objetivo 3 queda medible y sin la clausula no medible.

## 5. Higiene de prosa de proceso y Anexo I (rec. 10)

- [x] 5.1 Retirar "Una version anterior de esta tesis la declaro refutada" de `T01/` y de `T04/`, segun D4. Aceptacion: la frase no existe en ninguno de los dos archivos.
- [x] 5.2 Retirar la ruta `docs/Tesis/Correcciones/bitacora-busqueda-c-110.md` de `T03/`, conservando el sentido de la trazabilidad, segun D4. Aceptacion: la ruta no existe en `T03/`.
- [x] 5.3 Reducir el Anexo I de `T12/` a la nota de versiones y un parrafo breve, eliminando las tablas de dictamenes y de la devolucion, conservando la etiqueta `sec:anexo-trazabilidad`, la etiqueta `subsec:nota-versiones` y la divulgacion de asistencia de un modelo de lenguaje, segun D4. Aceptacion: el Anexo I no reproduce los nueve dictamenes y las remisiones externas conservan su destino.

## 6. Fundamentos teoricos (rec. 11)

- [x] 6.1 Agregar a `T02/` las subsecciones de acuerdo entre anotadores y kappa, clasificacion multietiqueta y pruebas estadisticas empleadas, con claves ya presentes en `BIB/`, segun D5. Aceptacion: las tres subsecciones existen y solo citan claves existentes.
- [x] 6.2 Actualizar la frase introductoria de `T02/` que declara el numero de ejes tematicos, segun D5. Aceptacion: el conteo coincide con el numero de subsecciones.

## 7. Ubicacion del capitulo legal (rec. 12)

- [x] 7.1 Agregar al inicio de `T11/` una oracion que justifique su posicion entre implementacion y resultados, sin mover el capitulo ni tocar el parrafo de consentimiento E3/E4, segun D6. Aceptacion: la justificacion existe y el parrafo E3/E4 queda intacto.

## 8. Bibliografia (rec. 13)

- [x] 8.1 Actualizar `Gomez2026_repositorio` en `BIB/` a la version 1.3.0, segun D7. Aceptacion: la entrada declara 1.3.0.
- [x] 8.2 Convertir a `@inproceedings` las entradas `Radford2023_whisper`, `Guo2017_calibration` y `Zhao2021_calibrate_before_use`, segun D7. Aceptacion: las tres tienen `booktitle` y conservan volumen, paginas y URL.
- [x] 8.3 Agregar la pagina 243 a la atribucion de Zanzotto en `T02/`, segun D7. Aceptacion: la cita usa `p.~243`.
- [x] 8.4 Verificar que los DOI de 2025 y 2026 resuelven; si alguno no resuelve, reportarlo sin inventar uno nuevo, segun D7. Aceptacion: los siete DOI resuelven o quedan reportados.

## 9. Glosario (rec. 14)

- [x] 9.1 Agregar iPaaS, SaaS, kNN y CoT a `TG/`, conservando el orden alfabetico de cada columna, segun D8. Aceptacion: las cuatro entradas existen y cada columna permanece ordenada.
- [x] 9.2 Actualizar el comentario de cabecera de `TG/`, segun D8. Aceptacion: el comentario refleja las entradas agregadas.

## 10. Honestidad de la vacancia del corpus (bonus)

- [x] 10.1 Suavizar en `T01/` la afirmacion de que ningun trabajo declara un corpus en espanol, acotandola a la evidencia, segun D9. Aceptacion: el texto reconoce que el idioma no se informa en la mayoria de los trabajos y acota la ausencia al alcance revisado.

## 11. Verificacion final y registro

- [x] 11.1 Ejecutar `openspec validate c-212-consistencia-y-forma-de-la-tesis --strict`. Aceptacion: valido.
- [x] 11.2 Ejecutar `python3 "docs/Tesis/v10 (IA)/verify_citations.py"` desde la raiz. Aceptacion: STATUS PASS con 0 huerfanas y 0 sin usar.
- [x] 11.3 Revisar el diff y confirmar que no cambio ninguna cifra canonica y que no se tocaron `07-resultados.tex`, `08-discusion.tex` ni `09-conclusiones.tex`. Aceptacion: `git diff --exit-code` sobre esos tres archivos da 0 y la revision no muestra cambios de cifras.
- [x] 11.4 Verificacion de alcance, segun `git status --porcelain`: solo los `.tex` indicados, `BIB/` y los artefactos del change. Aceptacion: no se tocaron `App/`, `n8n/`, `evaluation/`, `data/`, `.engram/` ni `main.pdf`.
- [x] 11.5 Registrar el change en `CHANGES.md` con su fase, estado, scope, dependencias, gobernanza y "Leer antes". Aceptacion: `rg -n "c-212" CHANGES.md` devuelve coincidencias.
