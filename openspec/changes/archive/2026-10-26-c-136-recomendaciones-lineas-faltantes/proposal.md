## Why

El dictamen CONEAU 2026-10-22 sobre la release v1.1.0/v1.1.1 (`auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`, seccion 8 y recomendacion B11) observa que el capitulo de recomendaciones (`sections/10-recomendaciones.tex`, seccion 11 del PDF) anuncia como prioritarias tres lineas -calibracion del gate de confianza, clasificador supervisado con corpus propio y correccion de la medicion de intervencion humana- pero solo desarrolla la segunda: las otras dos, que atacan precisamente los defectos de fondo del dictamen (veredicto, puntos 1 y 2; sub-hipotesis de intervencion "no contrastada por ausencia de registro primario"), no tienen subseccion. Ademas, la subseccion de aprendizaje activo propone priorizar "casos clasificados con baja confianza", lo que contradice el hallazgo de que la confianza declarada no discrimina aciertos de errores. Cerrar B11 alinea lo que la tesis diagnostica (capitulos 7 y 8, tal como los dejan c-130 y c-131) con lo que propone, y convierte en plan concreto lo que las correcciones de fondo dejan abierto. Es un change documental: no toca codigo, numeros canonicos ni bibliografia.

## What Changes

- **Nueva subseccion "Calibracion del gate de confianza"** (`\label{subsec:calibracion-gate}`), ubicada antes de la del clasificador supervisado. Diagnostico coherente con el analisis por etapa de c-130/c-131 (el gate de 0,70 solo aplica a la etapa Gemini y a la de reserva; la confianza autodeclarada de Gemini se concentra en su rango efectivo 0,85-1,00 y no discrimina aciertos de errores; la etapa deterministica se gobierna por su propio score de correctitud) y propuesta en cuatro componentes: conjunto de validacion propio disjunto del corpus de evaluacion; senales independientes del puntaje (ambiguedad lexica entre categorias candidatas, margen entre la primera y la segunda categoria, desacuerdo entre etapas, revision por muestreo de casos de alta confianza); recalibracion posterior del puntaje, declarando que corrige su nivel pero no crea capacidad de discriminacion; y umbral del gate derivado de una curva cobertura-precision con ajuste fuera de la muestra, como el punto de operacion de la etapa deterministica (`docs/deterministic_calibration.md`).
- **Nueva subseccion "Correccion de la medicion de intervencion humana"** (`\label{subsec:medicion-intervencion}`), a continuacion de la del clasificador supervisado. Protocolo de registro primario por caso (ocurrencia y origen de la intervencion, consigna de tiempo de inicio y fin, resultado y operador seudonimizado), almacenado en `clasificacion_log` o en una tabla dedicada; definicion operacional alineada con las dos formas rotuladas de la variable en `tab:variables` (capitulo 4) y aplicada igual en ambos brazos, de modo que la sub-hipotesis de intervencion pueda contrastarse en replicaciones; el mismo registro mide las derivaciones erroneas y su costo en tiempo, insumos del balance neto que introduce c-132.
- **Aprendizaje activo condicionado** (`subsec:aprendizaje-activo`): deja de priorizar por baja confianza; selecciona por las senales independientes de `subsec:calibracion-gate` y condiciona el uso de la confianza a una recalibracion validada. Se retira la premisa de que la intervencion "ocurre en los casos derivados a revision", incompatible con un gate que no derivo ningun caso.
- **Estudios de replicacion ampliados** (`subsec:estudios-replicacion`): medir la exactitud del flujo manual sobre el mismo corpus con etiquetadores distintos de los operadores del brazo manual (enlace con c-132 y con la sexta limitacion) y emplear asignacion muestral no proporcional, con sobremuestreo de clases minoritarias y ponderacion por la distribucion del universo (enlace con c-134).
- **Parrafo de priorizacion coherente**: los dos parrafos introductorios se funden en uno por niveles (lineas prioritarias, lineas que fortalecen la evidencia, extensiones funcionales), con `\autoref` a la subseccion de cada linea prioritaria. Se corrige la remision al analisis de errores, que hoy apunta a `subsec:calibracion` en lugar de `subsec:analisis-errores`.
- **Referencias anticipadas sin destino** (extension de alcance, D7, sujeta a confirmacion): los capitulos 5 y 6 remiten a `sec:recomendaciones` por la calibracion de los parametros de inferencia, la autenticacion unica corporativa (SSO), el prefijo configurable del numero de incidente y la migracion a Kubernetes, que hoy no figuran en el capitulo. Se absorben en la subseccion de calibracion (parametros) y en el nivel de extensiones del parrafo de priorizacion.
- **Compensacion de paginas dentro del capitulo**: condensar las subsecciones del agente conversacional telefonico (330 palabras) y de la base de conocimientos (273 palabras), preservando los elementos que el dictamen valoro y los que exigen los requisitos vigentes del spec.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agregan requisitos sobre el capitulo de recomendaciones: subseccion de calibracion del gate de confianza, subseccion de correccion de la medicion de intervencion humana, aprendizaje activo condicionado a la calibracion, replicaciones con exactitud del flujo manual y asignacion no proporcional, coherencia del parrafo de priorizacion con las subsecciones, destino de las referencias anticipadas al capitulo y presupuesto de paginas acotado y declarado.

## Impact

- Edita: `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` (unico archivo fuente de la tesis) y `docs/Tesis/Correcciones/dictamen-correcciones.md` (entrada de trazabilidad B11). La verificacion regenera los artefactos de compilacion versionados de `paper/` (`main.pdf`, `main.toc` y afines).
- No toca: codigo (`App/`, `n8n/`, `evaluation/`), `Bibliography_base.bib` (dueno: c-138), `docs/Tesis/Correcciones/numeros-canonicos.md`, figuras, otros capitulos, el Anexo H, tags ni el render `tesis_para_agente.md` (lo regenera c-141 una sola vez).
- Dentro del capitulo NO se editan: `subsec:clasificador-supervisado` (c-139 corrige la atribucion a Touvron et al. 2023), el primer parrafo de `subsec:panel-monitoreo` (requisito vigente "Future work -- organizational analytics expansion") ni `subsec:evaluacion-modelos-abiertos`.
- Presupuesto de paginas: el capitulo ocupa hoy 4 paginas completas (84 a 87 del PDF de 101 paginas; la 87 sin margen libre). Agregado bruto estimado de 430 a 520 palabras (+1,2 a +1,5 paginas de texto, a razon de unas 345 palabras por pagina); compensacion interna estimada de 260 a 290 palabras (-0,75 a -0,85 pagina); neto esperado +0,4 a +0,75 pagina de texto, que por el salto de pagina final del capitulo se traduce en +1 pagina del PDF (101 -> 102 si nada mas cambia). Limite duro del change: el capitulo no supera 5 paginas. La neutralidad estricta se declara inviable sin eliminar contenido valorado por el dictamen; el residuo se declara a c-141, que verifica y renegocia el tope global de la familia c-130..c-141.
- Dependencias: duras c-130 y c-131 (texto y rotulos del gate y de la calibracion por etapa que la nueva subseccion cita); blandas c-132, c-133, c-134 y c-138; secuenciales sobre el mismo archivo c-139 y c-137 (despues de c-136); integracion y release v1.2.0 en c-141.
- Contrato para los changes hermanos: los rotulos `subsec:calibracion-gate` y `subsec:medicion-intervencion` quedan fijados desde este change y pueden citarse por anticipado.
- Gobernanza: LOW (documental; sin codigo ni datos de usuarios).

## Rollback

`git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex" docs/Tesis/Correcciones/dictamen-correcciones.md` y recompilar el PDF. Si otros changes ya citan `subsec:calibracion-gate` o `subsec:medicion-intervencion`, revertir tambien esas referencias o conservar las subsecciones para no dejar referencias indefinidas. No hay tags involucrados: la release la publica c-141.

## Success Criteria

- [ ] Cada linea anunciada como prioritaria tiene subseccion propia con `\label` y el parrafo introductorio la referencia con `\autoref` (verificado por grep).
- [ ] La subseccion de aprendizaje activo no prioriza por baja confianza de forma incondicional y remite a `subsec:calibracion-gate`.
- [ ] Las referencias anticipadas a `sec:recomendaciones` desde los capitulos 5 y 6 encuentran su linea en el capitulo.
- [ ] Ningun numero nuevo fuera de `numeros-canonicos.md`, ninguna entrada nueva en `Bibliography_base.bib` y `verify_citations.py` en PASS.
- [ ] El PDF compila sin errores fatales ni referencias indefinidas; el capitulo ocupa a lo sumo 5 paginas y el delta medido queda registrado para c-141.
