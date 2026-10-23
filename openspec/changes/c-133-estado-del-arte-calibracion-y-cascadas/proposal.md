## Why

El dictamen CONEAU del 22-10-2026 sobre la release `v1.1.0` (aplicable por igual a `v1.1.1`; `auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`) senala que el estado del arte "no releva literatura sobre calibracion de la confianza autodeclarada por LLM en tareas de clasificacion ni sobre cascadas hibridas reglas-modelo, que son exactamente los dos ejes del hallazgo mas original del trabajo" (seccion 4); que la unica cita que sostiene el concepto de calibracion, Xuan et al. (2025, MMLU-ProX), no trata el tema (seccion 5 y verificacion externa: "ninguna fuente de la bibliografia trata la calibracion de la confianza"); descuenta esa ausencia en el criterio 3 de la rubrica; y en la recomendacion A4 pide reemplazar a Xuan et al. como fuente de calibracion "por obras que efectivamente estudien la calibracion de la confianza declarada por modelos de lenguaje en tareas de clasificacion, verificadas en texto completo antes de citarlas". A4 es una de las cuatro observaciones que condicionan la aprobacion plena.

Este change es dueno de incorporar las fuentes NUEVAS que efectivamente traten calibracion y cascadas, por una extension declarada del protocolo de revision; la reescritura y retirada de atribuciones existentes (incluida la frase de Xuan et al.) es de `c-134`. Conviene aplicarlo antes de `c-134` (que retira la cita erronea) y de `c-131` (que redacta la linea de recomendacion sobre calibracion del gate), porque ambos consumen estas fuentes.

## What Changes

- **Extension del protocolo de revision (`03-estado-del-arte.tex` + bitacora):** dos cadenas nuevas, C1 (calibracion y estimacion de confianza en modelos de lenguaje y clasificadores) y C2 (cascadas, enrutamiento y esquemas hibridos con criterio de costo-exactitud), sobre las mismas seis bases, con criterios de inclusion y exclusion propios del grupo C (arbitraje obligatorio; sin restriccion temporal para trabajos de referencia, como B1) y una fecha de corte propia, declarada igual en el texto y en la bitacora. La bitacora `docs/Tesis/Correcciones/bitacora-busqueda-c-110.md` se extiende in situ (Grupo C) con la verificacion de cada fuente y una tabla de correspondencia afirmacion-fuente. Las cadenas A1-A4 y B1 y su fecha de corte (21-10-2026) no cambian.
- **Seis fuentes nucleo, verificadas una por una** (pre-verificadas en esta fase; re-verificacion obligatoria al aplicar): Guo et al. (2017, ICML, PMLR 70); Zhao et al. (2021, ICML, PMLR 139); Tian et al. (2023, EMNLP); Xiong et al. (2024, ICLR); Varshney y Baral (2022, EMNLP); Chen, Zaharia y Zou (2024, FrugalGPT, TMLR). Se declara una reserva verificada solo para sustitucion. Kadavath et al. (2022) queda excluida por no arbitrada.
- **`02-marco-teorico.tex` (seccion 2.5):** fundamentacion de la calibracion con fuentes que la tratan (concepto, medicion con diagramas de fiabilidad y ECE, calibracion posterior, confianza verbalizada de LLM consultados como servicio) y del esquema hibrido como cascada. Se inserta a continuacion de la oracion que define calibracion; NO se toca la oracion de Xuan et al. (la retira `c-134`) ni la del umbral de 0,70 (la reescribe `c-125`).
- **`03-estado-del-arte.tex`:** subseccion nueva "Calibracion de la confianza y cascadas de modelos" (`\label{subsec:calibracion-cascadas}`) entre 3.3 y 3.4, con los hallazgos de la literatura y, solo si la busqueda C1-C2 lo confirma, una vacancia acotada al alcance revisado; la oracion introductoria del capitulo pasa a enumerar cuatro areas.
- **`08-discusion.tex` (Comparacion con la literatura):** un parrafo que lee el hallazgo de calibracion (tal como lo reformula `c-126` por etapa) y el esquema hibrido a la luz de esa literatura, sin numeros nuevos y sin reintroducir la lectura de "calibracion invertida" del clasificador en su conjunto.
- **`Bibliography_base.bib`:** seis entradas en un bloque aditivo comentado (patron c-110/c-113), con DOI o URL oficial; `verify_citations.py` PASS (59 -> 65 entradas). Ninguna entrada existente se modifica.
- **Numeros:** ninguno propio nuevo; cifras de terceros solo si se citan textualmente con pagina.
- **Paginas:** impacto cuantificado con presupuesto de lineas por insercion (+2 paginas esperadas, +3 en el peor caso) y contingencia declarada; la verificacion final del tope es de `c-136`.
- **Registradas fuera del alcance por defecto:** ITSM-BERT (SBBD 2026) y Alsac et al. (UBMK 2025), senaladas por el dictamen y verificadas en esta fase, no son capturadas por C1-C2; su incorporacion queda como pregunta abierta (`design.md`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agregan requisitos para (1) la extension declarada y trazable del protocolo de revision (C1-C2) consistente con la bitacora; (2) la verificacion individual de cada fuente nueva (existencia, metadatos y contenido) con registro de correspondencia afirmacion-fuente; (3) la fundamentacion de la calibracion de la confianza en fuentes que la tratan; (4) la cobertura del estado del arte sobre calibracion y cascadas, con vacancia acotada; (5) la lectura del hallazgo de calibracion y del esquema hibrido en la discusion sin numeros nuevos; (6) la higiene bibliografica de las entradas nuevas; y (7) la medicion y el registro del impacto en paginas.

## Impact

- Edita: `docs/Tesis/v10 (IA)/paper/sections/{02-marco-teorico,03-estado-del-arte,08-discusion}.tex`, `docs/Tesis/v10 (IA)/Bibliography_base.bib` y `docs/Tesis/Correcciones/bitacora-busqueda-c-110.md`.
- No toca: codigo de aplicacion, `evaluation/`, `docs/Tesis/Correcciones/numeros-canonicos.md`, `07-resultados.tex` (`c-126`), `tab:trabajos-academicos` y `tab:comparativa` (`c-130`), las atribuciones existentes a Xuan, Lai, Zhang, Mayor-Rocher, Revina, Paket/Colavito y Touvron (`c-134`), la oracion del umbral de 0,70 (`c-125`), `10-recomendaciones.tex` (`c-131`), tags, version y renders (`c-136`).
- Interfaces: `c-134` retira la oracion de Xuan et al. en 2.5 y puede reutilizar las claves de este change (en particular la de Zhao et al. 2021 para la sensibilidad al prompt); `c-131` y `c-126` pueden citar estas fuentes (p. ej. Guo et al. 2017 para el ECE) con las claves fijadas en `design.md`; `c-125` fija la terminologia de confianza por etapa que usa el parrafo de discusion; `c-136` arbitra el tope de paginas de la familia.
- Dependencias: los bloques de protocolo, verificacion, bibliografia, 2.5 y 3.x no tienen dependencias duras; el parrafo de discusion requiere `c-125` y `c-126` aplicados.
- Paginas: +2 esperadas (capitulo 3, cuya ultima pagina esta llena, y bibliografia, con unas 10 lineas libres), +0/+1 en el capitulo 9; el capitulo 2 absorbe su agregado (unas 15 lineas libres en su ultima pagina).
- Gobernanza: LOW (documental, aditivo y reversible).

## Rollback

Revertir los cinco archivos con `git checkout <commit-previo> -- <ruta>` y recompilar. Si `c-134` ya retiro la oracion de Xuan et al., revertir solo este change dejaria el concepto de calibracion sin fuente: en ese caso el rollback debe conservar la fundamentacion de 2.5 y su entrada bibliografica, o revertirse junto con la retirada de `c-134`. Si `c-131` o `c-126` ya citan claves de este change, revertir tambien esas citas o conservar las entradas (de lo contrario `verify_citations.py` reporta citas huerfanas).

## Success Criteria

- [ ] El parrafo de protocolo declara C1-C2, los criterios del grupo C y la fecha de corte de la extension, y la bitacora es consistente con el texto (bases, cadenas, criterios, fecha y claves incorporadas).
- [ ] Cada fuente incorporada tiene registradas su existencia (DOI o pagina oficial), el cotejo de metadatos y la correspondencia afirmacion-fuente con seccion o pagina; ninguna afirmacion excede lo que la fuente sostiene.
- [ ] La seccion 2.5 fundamenta la calibracion en al menos dos fuentes que la tratan, ninguna de ellas Xuan et al. (2025).
- [ ] El capitulo 3 contiene la subseccion de calibracion y cascadas; toda vacancia que enuncie esta acotada al alcance C1-C2 y a su fecha de corte.
- [ ] La discusion contiene el parrafo de contraste, sin numeros nuevos y coherente con la formulacion por etapa del capitulo de resultados.
- [ ] `verify_citations.py` PASS, Biber sin advertencias de claves duplicadas, PDF compilado sin errores ni referencias indefinidas.
- [ ] El conteo de paginas antes y despues queda registrado y el aumento atribuible a este change no supera +3 paginas.
