# Tasks: Incorporar los resultados de la campaña a la tesis

> Change GATEADO. Ninguna tarea de los grupos 1 a 9 se ejecuta sin la tarea 0 en verde.
> Líneas verificadas el 2026-10-30 sobre `docs/enmiendas-c-165-a-c-169`; reverificar
> cada `archivo:línea` con `grep -n` antes de editar (ramas posteriores pueden
> desplazarlas). Ramas de desenlace: ver `design.md`, "D-condicional".

## 0. Gate de campaña (mecánico; no escribe en `CHANGES.md`)

- [ ] 0.1 `openspec list --json` no lista c-165, c-166, c-167 ni c-168 como activos, y existen `openspec/changes/archive/*-c-165-*`, `*-c-166-*`, `*-c-167-*` y `*-c-168-*`. Si falla: detener
- [ ] 0.2 Existen y tienen README con SHA-256 coincidente (`sha256sum`): `evaluation/data/campana/doble_etiquetado.csv`, `plan_campana.csv`, `intervenciones.csv`, `plantilla_etiquetado.csv` y `predicciones_in_sample.json` —estas dos últimas las produce `python -m evaluation.preparar_entradas_analisis` (helper de c-170), que las ensambla desde `doble_etiquetado.csv` + `brazo_manual.csv` y desde la copia congelada de v9 respectivamente— y `analisis/` con las salidas de c-167 (kappa, exactitud manual, McNemar, intervención, orden, fuera de muestra). `predicciones_independiente.json` es opcional: si falta, rama (d) "sin corpus independiente declarado". Si falta cualquier otro: detener
- [ ] 0.3 `evaluation/data/campana/registro_sujetos.csv` presente; verificar que `E1`, `E2`, `O1`, `O2`, los analistas originales y los autores no se solapan. Solape operadores-referencia → rama (a) "no medida: operadores no independientes"; solape de etiquetadores con analistas originales o autores → "limitación declarada" en 4.4, 4.8 y 08
- [ ] 0.4 `pytest evaluation/` en verde. Si falla: detener y reportar
- [ ] 0.5 Anotar en el design de la sesión de apply la rama de cada ítem (a)-(e) según las salidas de c-167

## 1. Memo canónico (`docs/Tesis/Correcciones/numeros-canonicos.md`)

- [ ] 1.1 Crear la sección `3.N` siguiente libre (hoy 3.14) "Campaña de medición (c-165 a c-169)" con fecha, commit de configuración, `n` y SHA-256 de las tablas primarias
- [ ] 1.2 Registrar el kappa nuevo (`E1`/`E2`, `n`, `p_o`, `p_e`, PABAK, IC asintótico FCE 1969, IC bootstrap `B = 2000` semilla `20261021`, rótulo Landis-Koch, si el IC abarca dos categorías) o "IC no estimable" con su causa
- [ ] 1.3 Cerrar la entrada "IC del coeficiente kappa — no computable" (`:198-209`) con la nota "no estimable; superado por la entrada 3.N del kappa de la campaña" y dejar el `0,87` con estado `vigente (sin IC)`
- [ ] 1.4 Registrar exactitud estricta y laxa del brazo manual por operador (Wilson) y agregada (bootstrap por caso), discordantes excluidos, McNemar y la exactitud de v9 contra la referencia nueva como entrada propia (no reemplaza el `73,5 %`); o la entrada "no medida: operadores no independientes"
- [ ] 1.5 Registrar la tasa manual derivada (`1 - exactitud estricta`) y `a*` recalculada, estado `condicional` al costo por derivación errónea (solo si 1.4 es positiva)
- [ ] 1.6 Registrar `tasa_intervencion_humana` (casos: `n`, estimación, ambos límites de Wilson, desglose por origen y cambio de sector, veredicto frente a `0,15`: compatible si LS < 0,15, refutada si estimación ≥ 0,15, no concluyente si estimación < 0,15 ≤ LS; tiempo: bootstrap del cociente o "no estimable" con la cobertura) o "no contrastada: registro incompleto"
- [ ] 1.7 Registrar efectos de orden de condición (entre grupos independientes) y de posición (estadístico, tamaño de grupos o pares, MDE que informe c-167 para cada análisis, sin valores fijados a priori) o "limitación residual"; métricas fuera de muestra por etapa o "sin corpus independiente declarado"
- [ ] 1.8 Cada entrada con procedencia `archivo:línea` en `evaluation/data/campana/analisis/`, comando reproducible de solo lectura, método y estado; verificar que cada línea citada existe
- [ ] 1.9 Verificar por diff que ningún valor previo del memo cambió de valor ni de estado (salvo la nota de cierre de 1.3) y actualizar la cabecera del memo

## 2. Marco metodológico (`04-marco-metodologico.tex`)

- [ ] 2.1 4.2 (`04:12-16`): definir la denominación distintiva de la campaña nueva; conservar en `04:14` el confundido de la campaña 2026-10 y agregar el contrabalanceo de condición del plan (`posicion`, `mitad`, `brazo_primero`)
- [ ] 2.2 4.3 `tab:variables` (`04:25`, fila `04:34`): fuente de la intervención (export y vocabulario de origen), sin cambiar las dos formas rotuladas
- [ ] 2.3 4.4 (`04:43-55`): doble etiquetado nuevo (`E1`/`E2`, planilla única, tabla con SHA-256, referencia = consenso `E1 = E2`); en `04:55` conservar que los analistas 2026-10 fueron también operadores y declarar la independencia de la campaña de medición (o el solape)
- [ ] 2.4 4.5 (`04:57-63`): protocolo de la campaña de medición (plan, operadores `O1`/`O2`, instrumentación de intervención de c-165, configuración del Anexo B); acotar "sin intervención humana" de `04:61` a la captura 2026-10
- [ ] 2.5 4.6 (`04:65-69`): exactitud manual y `tasa_intervencion_humana` como métricas; reescribir "no se midió, por ausencia de registro primario" de `04:67` según la rama de (b)
- [ ] 2.6 4.7 (`04:71-77`): IC del kappa (FCE 1969 y bootstrap), Wilson, bootstrap por caso, McNemar (manual frente a v9 sobre la referencia nueva), efecto de condición entre grupos independientes y de posición con el MDE de c-167, regla de tres vías frente a `0,15`
- [ ] 2.7 4.8 (`04:79-89`): primera amenaza (`04:83`) con efecto de orden estimado o limitación residual; segunda (`04:85`) con `0,87` sin IC, kappa nuevo con IC y dependencia resuelta o declarada; revisar el cardinal "cuatro amenazas" (`04:81`)

## 3. Resultados (`07-resultados.tex`)

- [ ] 3.1 Crear `subsec:resultados-campana-medicion` (ubicación: tras `subsec:analisis-errores`, o donde decidan los autores manteniendo el orden del párrafo introductorio) con (e) kappa, (a) exactitud manual y McNemar, (c) orden y (d) fuera de muestra, cada uno con su rama
- [ ] 3.2 `07:157-161` (`subsec:reduccion-intervencion`): título según el estado de (b) (rótulo conservado), tasa con IC y veredicto o "no contrastada: registro incompleto"; conservar el hallazgo del gate de la campaña 2026-10
- [ ] 3.3 `07:6`: actualizar "seis apartados" al número real y enumerar la subsección nueva en orden
- [ ] 3.4 Declarar en la subsección nueva que sus valores no reemplazan los canónicos vigentes y que los tiempos de la campaña solo alimentan el efecto de orden

## 4. Discusión y conclusiones (`08-discusion.tex`, `09-conclusiones.tex`)

- [ ] 4.1 `08:20`: conservar "No se dispuso de un corpus independiente" para 2026-10 y agregar el resultado fuera de muestra o "sin corpus independiente declarado"
- [ ] 4.2 `08:22`: reemplazar "se descartaría con un diseño contrabalanceado" por el efecto de orden estimado o la limitación residual
- [ ] 4.3 `08:54` ("Sexto"): limitación de la campaña 2026-10, resuelta por la campaña de medición o declarada; `08:56` ("Séptimo"): agregar el resultado fuera de muestra si existe
- [ ] 4.4 `08:58` ("Octavo"): retirar si (b) quedó contrastada o reescribir como "registro incompleto"; renumerar los ordinales y actualizar el cardinal "ocho limitaciones" (`08:42`)
- [ ] 4.5 `08:70-97` (`subsec:balance-neto`, `tab:balance-neto`): conservar la grilla; agregar la tasa manual medida y `a*` recalculada con balance condicional al costo (o la rama "no medida"); reescribir `08:97`
- [ ] 4.6 `09:6`: retirar "---sin medir la intervención humana---" y el estado "no contrastada... por ausencia de registro primario" según (b)
- [ ] 4.7 `09:22-28` (`tab:cumplimiento-objetivos`): objetivo general con el estado de (b); objetivo 4 "Alcanzado" solo con (a) medida y (b) contrastada; objetivos 1, 3 y 6 sin cambio de grado
- [ ] 4.8 `09:35-43`: prosa coherente con la tabla (`09:41`: exactitud manual y McNemar frente a v9, o rama negativa; `09:39` sin cambio); la rama "no concluyente" de (b) no se presenta como confirmación ni refutación

## 5. Recomendaciones (`10-recomendaciones.tex`)

- [ ] 5.1 `10:6`: priorización con la tercera línea solo si (b) "registro incompleto"; clasificar todas las subsecciones
- [ ] 5.2 `10:16-18` (`subsec:medicion-intervencion`): si (b) contrastada, retitular (p. ej. "Medición continua de la intervención humana en operación"), remitir a `subsec:reduccion-intervencion` y recomendar la continuidad en operación; si no, conservar el protocolo. Rótulo y posición conservados
- [ ] 5.3 `10:42-44` (`subsec:corpus-independiente`): si (d) evaluada, retitular como replicación sobre corpus adicionales y remitir a resultados; si no, conservar. Rótulo conservado
- [ ] 5.4 `10:46-48` (`subsec:estudios-replicacion`): exactitud manual declarada realizada si (a) medida; cronometraje de reasignaciones como pendiente

## 6. Introducción, resumen y abstract

- [ ] 6.1 `01:34`: reemplazar el criterio de falsación por la regla de tres vías (compatible / refutada / no concluyente) y declarar el estado según (b), con tasa e IC o "registro incompleto"; remisión coherente con su destino
- [ ] 6.2 `00:13` y `00:29`: cláusula de estado de (b) con longitud igual o menor a la actual
- [ ] 6.3 `00:11` y `00:27`: conservar el `0,87` sin IC; no agregar el kappa nuevo salvo que sobre presupuesto
- [ ] 6.4 Si el balance neto cambia, `00:15` y `00:31` con tope de 34 (ES) y 31 (EN) palabras y sin aumentar el conteo previo
- [ ] 6.5 Aplicar el plan de recorte de `design.md` (margen actual ES 1, EN 5) y contar con la regla de c-106 hasta quedar en 250 o menos en ES y EN

## 7. Anexos, cronograma, legal y bibliografía

- [ ] 7.1 Anexo B `tab:configuracion-evaluada-entregada` (`12:38`): tercera columna "Configuración de la campaña de medición" y fila `classifier_version`, con valores verificados por `git show` y registrados en `conteos-canonicos-tecnicos.md`
- [ ] 7.2 `docs/diagrams/cronograma.md` y `fig:cronograma` (`12:14`, `12:22-23`): barra de la campaña de medición con la precisión de su evidencia; regenerar `figures/cronograma.png`
- [ ] 7.3 `11-aspectos-legales.tex:32`: sujetos de la campaña de medición (alias, consentimiento, seudonimización), sin datos personales
- [ ] 7.4 Anexo I `tab:anexo-trazabilidad-2810`: filas o celdas de los ítems del dictamen v1.2.5 cerrados por c-169
- [ ] 7.5 Bibliografía: agregar la entrada de Fleiss, Cohen y Everitt (1969) si la tesis la cita, con DOI

## 8. Registro y release

- [ ] 8.1 Compilar el PDF sin errores ni referencias indefinidas (`main.log` sin "undefined")
- [ ] 8.2 `python "docs/Tesis/v10 (IA)/verify_citations.py"` en PASS
- [ ] 8.3 `python "docs/Tesis/v10 (IA)/revision_tildes.py" --check` sin hallazgos nuevos
- [ ] 8.4 Recuento del resumen ES y EN con la regla de c-106 (≤ 250) y del párrafo de viabilidad (≤ 34 / ≤ 31); registrar ANTES/DESPUÉS
- [ ] 8.5 `pdfinfo main.pdf | grep Pages`: declarar el nuevo total frente al tope de 100 (hoy 112, exceso declarado) en la sección de presupuesto de páginas de `dictamen-correcciones.md`
- [ ] 8.6 Regenerar los renders con `python "docs/Tesis/v10 (IA)/build_tesis_para_agente.py"`
- [ ] 8.7 Actualizar las referencias de versión en Anexo A, Anexo B, 05, 06, 11 y la entrada `Gomez2026_repositorio` (patrón de `ea5e01a`)
- [ ] 8.8 Agregar la sección "c-169" a `docs/Tesis/Correcciones/dictamen-correcciones.md` (ítems (a)-(e), ramas, valores, conteos)
- [ ] 8.9 Etiquetar la release vX.Y.Z y consignar el hash en el Anexo B y `CHANGES.md` con un commit posterior (patrón de `756aabe`)
- [ ] 8.10 Al archivar, registrar c-169 en `CHANGES.md` (requisito "Coherencia del índice de changes con el archivo de changes" de project-documentation)

## 9. Cierre y verificación

- [ ] 9.1 `openspec validate c-169-incorporar-los-resultados-de-la-campana-a-la-tesis --strict --no-interactive` en verde
- [ ] 9.2 Propagación: `grep -nE "no medid|no contrastad|no estimable|no computable|no se midi" "docs/Tesis/v10 (IA)/paper/sections/"*.tex`; cada coincidencia debe estar en la lista de restos legítimos o ser un estado negativo declarado por la campaña de medición. Restos legítimos esperados: `04:63` (intervalo IMAP; dos coincidencias con el patrón amplio), `08:10` (latencia por etapa y carga concurrente), `09:25` (complejidad percibida), `09:39` (carga concurrente y complejidad percibida), las menciones de `Bases de Datos` no estimable (`04:45`, `04:77`, `07:130`, `07:146`, `08:32`, `09:24`) y `01:38` (subsidiarias no contrastadas). Toda mención de la campaña 2026-10 que se conserve (`04:14`, `04:55`, `04:67`, `08:20`, `08:54`) debe nombrar esa campaña
- [ ] 9.3 Verificar que el `0,87` no aparece con IC en `sections/*.tex` ni en el memo
- [ ] 9.4 Verificar que `61,6`, `17,76`, `W = 363`, `73,5`, `0,6508` y `0,87` no cambiaron (diff del PDF extraído o de `tesis_para_agente.md`)
- [ ] 9.5 Simular el archive sobre una copia de `openspec/` y confirmar que no aborta por escenarios descartados
