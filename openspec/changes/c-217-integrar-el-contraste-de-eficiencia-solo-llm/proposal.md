## Why

La tesis declara como hipótesis subsidiaria que el esquema híbrido (reglas + Gemini) es más eficiente que usar solo el modelo, pero nunca la midió. El dictamen CONEAU sobre `v1.3.0` lo penaliza en los criterios 1 (hipótesis subsidiarias sin contraste), 4 (sin línea de base frente al modelo solo) y 6 (resultados). El change `c-215` construyó, corrió y analizó el brazo «Gemini solo» con una regla de decisión prerregistrada y escribió la prosa, pero se cerró **sin fusionar**. Su rama precede a c-206/c-208 y al retargeteo de c-213 a la referencia arbitrada de 206 que hoy usa `main`. Integrarla resolviendo la deriva es la palanca de mayor rendimiento por costo para subir esos criterios sin evidencia nueva.

## What Changes

- **Fusionar el contenido de c-215 en `main`**: `evaluation/brazo_gemini_solo.py`, `analisis_brazo_gemini_solo_c215.py` (y pruebas), el caché versionado y sus salidas. Código ya escrito; sin gasto.
- **Resolver la deriva de referencia**: mantener los **103 casos de consenso `E3`/`E4`** como etapa previa y preregistrada del contraste de eficiencia, y presentar la **referencia arbitrada de 206** como el complemento de exactitud fuera de muestra. Sin corrida paga.
- **Prosa de la tesis** con el veredicto honesto (no concluyente) en `04`, `07`, `08`, `09`; `01` (enunciado) y `10` (trabajo futuro) se incluyen para no dejar contradicción interna.
- **Registro aditivo**: sección nueva `3.28` en `numeros-canonicos.md` (sin cambiar valores vigentes) y una entrada en `dictamen-correcciones.md`.

## Capabilities

### New Capabilities

- `gemini-solo-arm`: ejecutor y análisis del brazo «Gemini solo» frente al híbrido congelado, con la regla de decisión de tres vías prerregistrada para la hipótesis de eficiencia.

### Modified Capabilities

- `tesis-document`: la hipótesis de eficiencia pasa de «no contrastada» a «contrastada: no concluyente», con la relación de referencias (103 previa / 206 complemento) declarada.
- `tesis-numeros-canonicos`: se registra la sección canónica del contraste, aditiva.
- `tesis-dictamen-v1-3-0`: la respuesta al criterio 1 pasa de prohibir el ahorro de costo a exigir el veredicto honesto (ahorro medido, no inferioridad no establecida).

## Impact

- **Código fusionado (sin editar)**: `evaluation/brazo_gemini_solo.py`, su prueba, `evaluation/data/campana/analisis/analisis_brazo_gemini_solo_c215.py` y su prueba, el caché y las salidas.
- **Documentos editados**: las secciones `01/04/07/08/09/10` de `docs/Tesis/v10 (IA)/paper/sections/`, `numeros-canonicos.md` y `dictamen-correcciones.md`.
- **Costo**: cero. La corrida paga ya se hizo en c-215; no se emite ninguna llamada nueva.
- **Gobernanza**: MEDIUM. **No** toca L2-L5 (referencia, gate y forma), de c-216.

## Success Criteria

- [ ] `openspec validate c-217-… --strict --no-interactive` en verde.
- [ ] El código y las salidas de c-215 están en `main` sin re-correr el brazo (caché intacto).
- [ ] Las secciones 01/04/07/08/09/10 declaran la eficiencia como «contrastada: no concluyente» sin contradicciones.
- [ ] La sección 3.28 es aditiva y ningún valor de 3.1-3.27 cambia.
- [ ] El registro documenta la decisión de referencia (103 previa / 206 complemento) y su costo.