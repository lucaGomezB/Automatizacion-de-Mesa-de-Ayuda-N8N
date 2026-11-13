# Tasks: Atender el dictamen CONEAU sobre v1.3.0 (recomendaciones 1 a 6)

Convenciones: `C/` = `docs/Tesis/Correcciones/`; `S/` = `docs/Tesis/v10 (IA)/paper/sections/`;
`A/` = `evaluation/data/campana/analisis/`; `R/` = `docs/campana-medicion/`. Todo cálculo es
de solo lectura sobre artefactos versionados. NO se edita `App/`, `n8n/`, `data/*`,
`evaluation/*.py` del paquete (solo se importan), los corpus, los scripts de c-191 y c-205 ni
el change c-206. Ninguna cifra entra al texto sin estar antes en el memo con procedencia. En
la prosa usar "sección N (`archivo.tex`)" (gitleaks). Sin commit, push, PR, tag ni release
salvo indicación expresa del usuario. Strict TDD: prueba primero, en rojo, antes del código.

## 0. Preparación

- [x] 0.1 Confirmar el estado: rama `change/c-207-atender-el-dictamen-coneau-v1-3-0` (apilada sobre c-205), `openspec validate c-207-atender-el-dictamen-coneau-v1-3-0 --strict` pasa y el dictamen no versionado `auditorias/Dictamen_Tesis_v10_v1.3.0_CONEAU_2026-11-13.md` sigue intacto. Verificación: los comandos sin error.
- [ ] 0.2 Red de seguridad: correr `cd evaluation; python -m pytest -q` y `cd evaluation/data/campana/analisis; python -m pytest test_analisis_fuera_de_muestra_c205.py -q`; registrar el número de pruebas en verde. Verificación: todo en verde; si algo falla, detenerse y reportarlo como falla previa. (Registro: `evaluation` 1173 pasan y 24 fallan antes de tocar nada, por `Settings` sin variables de entorno en `tests/test_sensibilidad_ajustes.py` y `tests/test_sensibilidad_corpus.py`; el de c-205, 8 en verde. Falla previa reportada a los autores; sin corregir.)

## 1. Script de análisis c-207 (TDD; `A/analisis_dictamen_c207.py`)

- [x] 1.1 (RED) Escribir `A/test_analisis_dictamen_c207.py` con una prueba de la reducción relativa sobre un caso sintético (razón constante: el IC degenera en el valor puntual) que importe el módulo inexistente; verificar que falla por módulo ausente.
- [x] 1.2 (GREEN) Implementar el bloque `ic_reduccion_tiempo` (D2): `R = 1 − media(aut)/media(man)`, bootstrap percentil por pares con `SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP`, más el IC de la diferencia de medias en segundos. Verificación: la prueba de 1.1 pasa.
- [x] 1.3 (TRIANGULATE) Agregar pruebas: el valor puntual sobre los 200 pares del corpus versionado redondea a `0,7116`; dos corridas dan el mismo IC; pares con distinta longitud o vacíos se rechazan. Verificación: en verde.
- [x] 1.4 (RED/GREEN) Bloque `acuerdo_e3_e4` (D3): prueba sobre una planilla sintética mínima y prueba de que la cuenta de concordantes sobre `doble_etiquetado_independiente.csv` es `103` de `150`; implementar con `kappa_cohen` (IC asintótico y bootstrap) y fallar sin escribir salidas si no coincide con el n efectivo de c-191. Verificación: en verde.
- [x] 1.5 (RED/GREEN) Bloque `balance_neto_referencia_comun` (D4), paso de verificación: prueba que exige declarar la referencia de `e_aut` (`53/200`, etiquetado original) y de `e_man` (`26/151`, consenso `E1`/`E2`) tal como los usa el texto, y el campo `asimetria_confirmada`. Implementar leyendo los artefactos (`predicciones_in_sample.json`, `brazo_manual.csv`, `corpus_campana.json` o la fuente que use `evaluation/analisis_campana.py`). Verificación: en verde.
- [x] 1.6 (RED/GREEN, solo si 1.5 confirma la asimetría) Recálculo con referencia común: `e_aut` y `e_man` contra el consenso `E1`/`E2` con sus conteos (se espera `28/138` y `26/151`), `B` y `a*` para 5, 10 y 15 minutos con `N = 2.646` y `Δt = 43,82 s`, e IC bootstrap por caso de `e_aut − e_man` y de `B`; si es computable, la segunda referencia común (original) para el brazo manual. Pruebas: caso sintético con `e_aut = e_man` da `B` = ahorro bruto; caso sintético con signo conocido. Verificación: en verde; los límites no igualables (unidad por caso frente a por derivación, `Δt` de otra campaña) figuran en el bloque.
- [x] 1.7 (REFACTOR) Ordenar el script (constantes, funciones puras, escritura al final) sin cambiar salidas; correr las pruebas tras cada paso. Verificación: en verde.
- [x] 1.8 Generar `A/analisis_dictamen_c207.{json,md}` (UTF-8 sin BOM, LF) con los SHA-256 de las entradas; correr dos veces y comparar byte a byte; `git status` sin otros archivos modificados. Verificación: hashes estables.
- [x] 1.9 Documentar el script en `A/README.md` (entradas, comando, método, semilla, remuestras). Verificación: sección nueva con comando reproducible.

## 2. Registro canónico (`C/`)

- [x] 2.1 Agregar la sección 3.21 de `C/numeros-canonicos.md` con cada cifra del JSON de c-207 (procedencia con clave, comando y estado) y la entrada de upsert del encabezado. Verificación: toda cifra con archivo, clave y comando; diff limitado a 3.21, al encabezado y, si D4 lo exige, a la marca de lectura superada de la sección 3.11 con remisión a 3.21.
- [x] 2.2 (No aplica: 1.5 confirmó la asimetría) Si 1.5 NO confirma la asimetría, registrarlo en 3.21 y en `C/dictamen-correcciones.md` con la evidencia, y saltar 3.5. Verificación: el hallazgo queda escrito con su fuente.

## 3. Prosa de la tesis (`S/`)

- [x] 3.1 Rec. 6, sección 7 (`07-resultados.tex`, comparación de tiempos): informar el IC al 95 % de la reducción del `71,2 %` con método, semilla y `B`, rotulado como cota superior de una muestra por conveniencia; agregarlo a la nota de `tab:tiempos`. Verificación: valores iguales a 3.21; el cuarto objetivo (sección 1, `01-introduccion.tex`) sin cambios.
- [x] 3.2 Rec. 1, sección 7 (`07-resultados.tex`, validación fuera de muestra): agregar `tab:fuera-de-muestra` según D3 y la declaración de que el arbitraje de los `47` discordantes no se ejecutó y queda diferido; ajustar el párrafo de c-205 para que remita a la tabla sin perder advertencias. Verificación: cada celda coincide con 3.19, 3.20 o 3.21; no se informa resultado de arbitraje.
- [x] 3.3 Rec. 2, sección 10 (`09-conclusiones.tex`): reemplazar la frase de barreras legales (tercera contribución) por la formulación condicionada al instrumento de transferencia con remisión a la sección 11 (`11-aspectos-legales.tex`); retirar «reduce el costo de inferencia» y decir lo medido (131 de 200 casos resueltos por la etapa determinística; eficiencia no contrastada); acotar la generalización regional y la frase de GPU y licencias según D5, sin hechos externos nuevos sin cita. Verificación: las tres frases objetadas ya no figuran.
- [x] 3.4 Rec. 3, sección 10 (`09-conclusiones.tex`): párrafo y fila del objetivo 2 de `tab:cumplimiento-objetivos` con la validación fuera de muestra (`0,8447` sobre n efectivo `103`, peor caso `0,5800`, arbitraje diferido); el estado sigue «No alcanzado». Verificación: cifras iguales al memo.
- [x] 3.5 Rec. 5, sección 8 (`08-discusion.tex`, `subsec:balance-neto`): si 1.5 confirmó la asimetría, declarar la referencia de cada tasa, informar el balance con referencia común y su IC desde 3.21, conservar `tab:balance-neto` como sensibilidad y declarar los límites no igualables; enunciar el signo solo si el IC lo fija. Verificación: valores iguales a 3.21; ninguna tasa sin referencia declarada.
- [x] 3.6 Rec. 2, sección 0 (`00-resumen.tex`): reemplazar «viabilidad técnica y económica» por la lectura condicional en el resumen y en el *abstract*, en paralelo; unificar la lectura del balance neto con 3.5 en `00-resumen.tex`, `08-discusion.tex` (incluida la frase «Quedan sostenidas la viabilidad técnica [...] y la económica») y `09-conclusiones.tex` (párrafo inicial). Contar palabras de resumen y *abstract*. Verificación: ambos ≤ 250 palabras; la misma lectura en los tres capítulos.
- [x] 3.7 Rec. 4, sección 11 (`11-aspectos-legales.tex`, consentimiento y derechos): agregar que `E3` y `E4` fueron informados verbalmente el 10 de noviembre de 2026 y que su confirmación escrita está pendiente; no tocar `R/confirmacion-posterior-consentimiento.md`. Verificación: el texto no afirma firma ni fecha de confirmación de `E3`/`E4`.
- [x] 3.8 Revisión de las secciones tocadas: tildes correctas, español técnico neutro, sin prosa de control de versiones nueva, etiquetas y `\autoref` existentes. Verificación: `python "docs/Tesis/v10 (IA)/revision_tildes.py"` sin hallazgos nuevos en los archivos tocados y cada `\ref`/`\autoref` nuevo apunta a un `\label` existente.

## 4. Trazabilidad

- [x] 4.1 `C/dictamen-correcciones.md`: sección del dictamen v1.3.0 (2026-11-13) con el estado de cada recomendación (1 a 6 con archivo y change; 7 a 15 diferidas a un change posterior; rec. 4 parcial hasta la firma). Verificación: la sección existe y lista las 15.
- [x] 4.2 `CHANGES.md`: FASE 67 con la entrada `[C-207]` (estado, scope, dependencias c-205 y c-206, governance HIGH, «Leer antes»). Verificación: la entrada sigue el formato de la FASE 66.
- [x] 4.3 Regenerar `docs/Tesis/v10 (IA)/tesis_para_agente.md` con `build_tesis_para_agente.py` y correr `verify_citations.py`. Verificación: regeneración sin error; `verify_citations.py` PASS.

## 5. Tareas manuales y bloqueadas

- [x] 5.1 (MANUAL, autores) Adaptar el punto 1 de la plantilla de `R/confirmacion-posterior-consentimiento.md` para `E3`/`E4` (su tarea fue la validación fuera de muestra, no la campaña complementaria), recabar las firmas y completar `fecha_confirmacion` de `E3` y `E4`. Solo después, ajustar la frase de 3.7. Verificación: el registro sin «por completar»; el agente no completa esta tarea. — COMPLETADO 2026-11-13: el punto 1 cubre ahora la campaña, la validación fuera de muestra y el arbitraje; se agregó la fila de `E5` (rol `arbitro`, código `P<n>`, identidad solo en poder del director); `E3`, `E4` y `E5` quedan con información verbal 2026-11-12 y confirmación escrita 2026-11-13, sin «por completar». En `11-aspectos-legales.tex` se reemplazó el párrafo: fecha corregida, retirada la equivalencia «en los mismos términos» (no respaldada por el registro) y retirada la afirmación de confirmación pendiente, hoy falsa. Los originales firmados quedan en el expediente físico del director.
- [ ] 5.2 (MANUAL, autores) Decidir si se ejecuta c-206 antes de la defensa; por defecto el texto declara el arbitraje diferido. Verificación: decisión registrada en `C/dictamen-correcciones.md`.
- [ ] 5.3 (BLOQUEADA en esta máquina: sin `latexmk`/`xelatex`/`biber`) Recompilar `main.pdf` en el entorno de registro y regenerar `paper/compilacion.md` (páginas y palabras). Verificación: sin errores fatales; resumen y *abstract* ≤ 250 palabras. No marcar hecha sin la compilación real.

## 6. Validación

- [ ] 6.1 Correr `cd evaluation/data/campana/analisis; python -m pytest test_analisis_dictamen_c207.py test_analisis_fuera_de_muestra_c205.py -q` y `cd evaluation; python -m pytest -q`. Verificación: exit 0 y el mismo número de pruebas previas en verde que en 0.2.
- [x] 6.2 Correr `openspec validate c-207-atender-el-dictamen-coneau-v1-3-0 --strict --no-interactive`. Verificación: `is valid`.
