## Why

El dictamen CONEAU v1.3.0 (2026-11-13) califica el documento en **7,83/105** y concentra el
riesgo en cuatro observaciones corregibles: referencia de verdad frágil (criterio 4, peso 20),
lectura del human-in-the-loop (criterios 4/5), cierre de R4 (criterios 7/8) y repetición/forma
(criterio 8, peso 5). El criterio 4 exige evidencia nueva, no redacción; por eso L2 es un
análisis de sensibilidad con lo ya recolectado, sin campo y sin cambiar números canónicos.

## What Changes

| Palanca | Criterio | Impacto esperado | Esfuerzo | ¿Paga o campo? |
|---|---|---|---|---|
| **L2** Ruido de referencia | 4 (peso 20) | 7 → 7,5/8; +0,10 a +0,20 final | Medio (1–2 días) | No; solo artefactos versionados |
| **L3** Reencuadre del human-in-the-loop | 5 (peso 15) y 4 | +0,25 a +0,5 en el 5; +0,03 a +0,07 final | Bajo | No por defecto; corrida paga solo con autorización del dueño |
| **L4** Verificación de R4 | 7/8 | ~0 (ya está hecho); cierra trazabilidad | Bajo | No |
| **L5** Repetición y forma | 8 (peso 5) | 7 → 7,5; +0,02 a +0,05 final | Bajo | No |

- **L2 (aditiva).** Monte Carlo de etiquetas calibrado al acuerdo `E3`/`E4` (`p_o = 0,6867`;
  kappa `0,6055`) sobre los `206` casos arbitrados, más cotas y los `6` casos de tres vías.
  Artefacto reproducible en `evaluation/data/campana/analisis/analisis_ruido_referencia_c216.*`
  y sección 3.27 del memo. No altera `0,6893/206`, `0,7024` ni ningún valor vigente.
- **L3 (honestidad).** "La revisión humana por confianza no actuó" pasa a "el human-in-the-loop
  actuó por una señal independiente de la confianza (regla del reportante: `147`
  intervenciones, `25` cambios, `17,0 %`); lo que no discriminó fue la confianza (AUROC
  `0,5168` `[0,3796; 0,6528]`)". La evaluación de la configuración entregada es **decisión del
  dueño**; sin autorización se declara como limitación.
- **L4 (verificación, no reescritura).** R4 ya está resuelto en el capítulo legal y en el
  registro (`E3`/`E4`/`E5`: información verbal 2026-11-12, firma 2026-11-13). Se verifica la
  consistencia y se corrige el README de campaña (dice 8 filas; el registro tiene 11).
- **L5 (forma).** `0,8447/103` y `0,6893/206` en prosa una sola vez fuera de resultados, con
  remisión a `tab:fuera-de-muestra`; capítulo 11 con `0` oraciones de más de `60` palabras y
  párrafos de a lo sumo `2000` caracteres. Sin cambios de cifras ni citas.

**No objetivos:** no se toca `App/`, `n8n/`, el clasificador, la configuración, los corpus ni
`data/`; no hay trabajo de campo ni corrida paga sin autorización; no se corrige aquí el
requisito histórico de `tesis-dictamen-v1-3-0` que aún declara el arbitraje diferido (c-206 ya
cambió el texto y su propia spec).

## Capabilities

### New Capabilities
- `evaluation-reference-noise-sensitivity`: método, entradas, salidas y reproducibilidad del
  análisis de ruido de referencia, sin cambiar valores canónicos.

### Modified Capabilities
- `tesis-numeros-canonicos`: registro aditivo (sección 3.27) con fuente, comando y SHA-256.
- `tesis-document`: subsección de resultados y método; reencuadre del human-in-the-loop;
  repetición y oraciones/parrafos acotados.
- `tesis-dictamen-v1-3-0`: consentimiento de `E3`, `E4` y `E5` consistente con el registro
  firmado (R4 verificado).

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `evaluation/data/campana/analisis/` | Nuevo | Script de solo lectura, JSON/MD y SHA-256 |
| `docs/Tesis/v10 (IA)/paper/sections/{04,07,08,09,10,11}-*.tex` | Modificado | Método, resultados, discusión, reencuadre y forma |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Modificado | Sección 3.27 aditiva |
| `evaluation/data/campana/README.md` | Modificado | Conteo de sujetos y consistencia de consentimiento |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Modificado | Libro mayor y trazabilidad |

## Risks and rollback

- La simulación se lee como verdad latente → rotularla como sensibilidad e informar cotas.
- Crecimiento de páginas → L5 compensa; tope neto `+2`, registrado.
- Reencuadre percibido como defensa interesada → conservar el AUROC `0,5168` y el veredicto
  negativo.
- Rollback: `git revert` de `.tex`, script, artefactos nuevos y sección del memo; no hay
  migración de datos ni cambio de configuración.

## Success Criteria

- [ ] El script reproduce `142/206` y `0,7024` antes de simular, es determinista y no usa red.
- [ ] La tesis informa la distribución, las cotas y los `6` casos de tres vías sin cambiar
      números canónicos.
- [ ] Las afirmaciones distinguen la regla del reportante de la señal de confianza.
- [ ] Capítulo legal, registro y README coinciden (11 sujetos; fechas 2026-11-12/13).
- [ ] `sent_c197.py` da `0` oraciones `> 60` palabras en el capítulo 11; repeticiones en prosa
      dentro del límite; PDF compila y crece a lo sumo 2 páginas.