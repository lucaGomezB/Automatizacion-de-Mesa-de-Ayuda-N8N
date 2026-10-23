## Why

El dictamen CONEAU del 22-10-2026 sobre la release `v1.1.0` (`auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`, aplicable por igual a `v1.1.1`) aprueba la tesis con observaciones y su cuarta observacion de fondo (VEREDICTO punto 4, recomendacion A4) condiciona la aprobacion plena: todas las fuentes existen, pero lo que el texto les atribuye no coincide con lo que sostienen en al menos siete puntos, entre ellos la unica cita del concepto de calibracion (Xuan et al., 2025, un benchmark de rendimiento multilingue que no trata calibracion). Se suman vacios de cobertura (B15: normas ISO/IEC y NIST CSF 2.0 del capitulo de cumplimiento, decreto reglamentario de la Ley 25.326 y referencias metodologicas primarias de Wilcoxon, potencia y bootstrap) y metadatos incompletos o discordantes (B16). Todo es corregible con redaccion, edicion del `.bib` y un ajuste minimo de `verify_citations.py`, sin nuevas mediciones; cerrarlo antes del reexamen levanta la observacion 4 y los descuentos de los criterios 3 y 9 de la rubrica.

## What Changes

- **A4 - Correspondencia texto-fuente (barrido por clave, no solo por la linea senalada):**
  - Xuan et al. (2025) deja de citarse como fuente de calibracion (`02-marco-teorico.tex:46`); su aporte real (caida de rendimiento en los idiomas de menos recursos) se reubica en `02:50`. El hueco de fundamentacion de la calibracion queda declarado para c-133, dueno de las fuentes nuevas de calibracion (interfaz en `design.md` D1).
  - Lai et al. (2023), Ahuja et al. (2023), Zhang et al. (2023), Grandury et al. (2025) y Mayor-Rocher et al. (2026): reescritura de `02:44`, `02:50` y del agrupamiento de citas de `03-estado-del-arte.tex:56` conforme a lo que cada obra sostiene.
  - La frase del "desplazamiento hacia LLM" (`03:32`) se invierte conforme a Paket et al. (2024) y Colavito et al. (2025), que encuentran que los modelos tipo BERT igualan o superan a los LLM generativos.
  - Revina et al. (2020): lo atribuido sobre modelos preentrenados pasa a ser una razon de diseno de los autores, no un hallazgo (`03:30`, `08:28`, `08:32`).
  - Touvron et al. (2023) deja de sostener la competitividad de los LLM locales en clasificacion (`10-recomendaciones.tex:12`).
  - Idiomas de los corpus (`01-introduccion.tex:66`): se retira "aleman o portugues" y la afirmacion se ancla en la tabla de trabajos relevados; por el mismo tema, `08-discusion.tex:34` deja de mencionar el aleman sin fuente y cita a quienes senalan la menor cobertura de los idiomas distintos del ingles.
  - Paramesh y Shreedhara (2019): las cifras de 10.000 tickets y 87 % se localizan con pagina o, si no son verificables, se reformulan conforme al resumen en sus cinco sitios (`01:48`, `03:28`, `03:44`, `08:28`, `08:30`). El dictamen nombra la obra "Paramesh y Ramya"; Crossref confirma la autoria que ya consigna el `.bib` (Paramesh y Shreedhara).
- **B15 - Cobertura bibliografica:** ocho entradas nuevas, verificadas antes de agregarse: ISO/IEC 27001:2022, ISO/IEC 27002:2022, ISO/IEC 27701 en su edicion vigente (2025; la edicion 2019 que nombra el dictamen figura como retirada en la ficha oficial de ISO desde 2025-10-14), NIST CSF 2.0 (CSWP 29, DOI 10.6028/NIST.CSWP.29), Decreto 1558/2001 (InfoLEG), Wilcoxon (1945, *Biometrics Bulletin*), Cohen (1988) y Efron y Tibshirani (1993), citadas en `11-aspectos-legales.tex` y `04-marco-metodologico.tex`.
- **B16 - Metadatos:** `Paramesh2019_it_service_desk` (libro, subtitulo, editores y serie), `OGC2011_itil` (autor y nota coherentes con `02:16`), `Jurafsky2023_speech_language` (URL y version del borrador), anos con un criterio uniforme (ano de copyright, APA 7): Stallings y Brown pasa a 2018, Date a 2004 y Russell y Norvig se mantiene en 2021; `urldate` en las nueve entradas `@manual`/`@misc` con URL; sede de `liu2025tickit` (FSE Companion 2025); fecha de consulta no duplicada en las cinco `@online`; notas sin punto y coma (el estilo lo suprime al imprimir); y dos hallazgos del registro del compilador del mismo apartado del dictamen (seudonimo de FastAPI impreso como apellido, RGPD sin enlace).
- **`verify_citations.py`:** el rotulo "unique citation keys" pasa a informar el conteo global de claves unicas (hoy imprime la suma de claves unicas por archivo); cambio minimo con prueba unitaria previa (TDD).
- **Trazabilidad:** registro de cada correccion, su evidencia y las decisiones que se apartan de la letra del dictamen (ISO/IEC 27701:2025, ano de Russell y Norvig, autoria de Paramesh) en `docs/Tesis/Correcciones/dictamen-correcciones.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agregan requisitos de correspondencia texto-fuente para el eje de LLM, el estado del arte y las recomendaciones; de localizacion o reformulacion de las cifras de Paramesh y Shreedhara; de cobertura bibliografica de normas, marcos y metodos estadisticos; de metadatos coherentes con catalogos y editores; de rotulo correcto del verificador de citas; de cuantificacion del impacto en paginas; y de trazabilidad. Se modifican cuatro requisitos vigentes cuya redaccion contradice la correccion: atribucion de Revina et al. (2020), respaldo de la afirmacion sobre idiomas del corpus, atribucion editorial de ITIL 2011 y cobertura de las plataformas comerciales (fecha de consulta solo en `urldate`).

## Impact

- **Edita:** `docs/Tesis/v10 (IA)/paper/sections/{01-introduccion,02-marco-teorico,03-estado-del-arte,04-marco-metodologico,08-discusion,10-recomendaciones,11-aspectos-legales}.tex`, `docs/Tesis/v10 (IA)/Bibliography_base.bib`, `docs/Tesis/v10 (IA)/verify_citations.py` (y su prueba nueva co-ubicada `test_verify_citations.py`) y `docs/Tesis/Correcciones/dictamen-correcciones.md`.
- **No toca:** codigo de aplicacion (`App/`, `n8n/`), `evaluation/`, numeros canonicos (`docs/Tesis/Correcciones/numeros-canonicos.md`), figuras, `CHANGES.md`, el preambulo LaTeX, la version de `Gomez2026_repositorio` (c-136), las fuentes nuevas de calibracion y cascadas (c-133) ni la ortografia fuera de las frases reescritas (c-132). No crea ni mueve tags.
- **Paginas:** el PDF vigente tiene 101 paginas; la bibliografia ocupa las paginas 88-93 y su ultima pagina tiene unas 10 lineas libres; la ultima pagina del cuerpo (87) tiene unas 2. Las ocho entradas y los ajustes de metadatos agregan del orden de 29 lineas a la bibliografia (+1 pagina esperada, 101 -> 102); las reescrituras del cuerpo se compensan dentro de los mismos parrafos (cuerpo neutral). La compensacion tipografica de la bibliografia se entrega a c-136, que hace la verificacion final del presupuesto (`design.md` D13).
- **Dependencias y orden:** despues de c-125 (frase del gate en `02:46`), c-128 (`01:48`), c-129 (`04:71`, `04:91`) y c-130 (tabla `tab:trabajos-academicos`); secuencial respecto de c-133 en cualquier orden (interfaz idempotente en `02:46` y en el `.bib`); antes de c-132 y c-136.
- **Gobernanza:** LOW (documentacion y una utilidad de solo lectura), con puntos de confirmacion del usuario declarados en `design.md` (Open Questions).

## Rollback

Revertir los archivos editados con `git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections/" "docs/Tesis/v10 (IA)/Bibliography_base.bib" "docs/Tesis/v10 (IA)/verify_citations.py" docs/Tesis/Correcciones/dictamen-correcciones.md`, eliminar `docs/Tesis/v10 (IA)/test_verify_citations.py` y recompilar el PDF. El change no crea ni mueve tags; `v1.0.0`, `v1.0.1`, `v1.1.0` y `v1.1.1` no se tocan.

## Success Criteria

- [ ] Ninguna de las siete atribuciones observadas por el dictamen, ni las detectadas en el barrido por clave, afirma algo que su fuente no sostenga; cada frase reescrita tiene su evidencia registrada.
- [ ] Ninguna cita de `xuan2025mmluprox` sostiene la calibracion y el hueco queda declarado para c-133.
- [ ] Las cifras de Paramesh y Shreedhara (2019) tienen pagina o dejan de atribuirse.
- [ ] Las ocho entradas de B15 existen, fueron verificadas contra su fuente oficial y estan citadas; ninguna cita una edicion retirada.
- [ ] Los metadatos de B16 quedan corregidos y cada cambio de ano sigue el criterio declarado.
- [ ] `verify_citations.py` emite PASS con "N bibliography entries <-> N unique citation keys" y su prueba pasa.
- [ ] El PDF compila sin citas ni referencias indefinidas y Biber no emite WARN; el delta de paginas queda medido y entregado a c-136, con el cuerpo neutral.
- [ ] No cambian numeros canonicos, figuras, `evaluation/` ni tags.
