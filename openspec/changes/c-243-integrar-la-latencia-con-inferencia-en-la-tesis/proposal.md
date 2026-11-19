# Proposal: Integrar la latencia con inferencia en la tesis

## Why

Dos corridas pagas acotadas de la sonda de latencia del tramo compartido con inferencia real incluida ya existen y estan versionadas: la corrida original (TASK B, commit `bbc5865`, release `v1.6.0`) y la corrida ampliada (`2026-11-18`). El ejemplar todavia afirma que «la latencia con inferencia no se midio» y que el backend no tiene cuello de botella en el punto de convergencia: ambas cosas son verdaderas solo para el camino deterministico de costo cero. El manuscrito omite una medicion propia y queda expuesto a una pregunta directa en la defensa.

## What Changes

- **Nueva subseccion** `subsec:latencia-con-inferencia` en `07-resultados.tex`, despues de `subsec:carga-concurrente`, con la tabla `tab:carga-inferencia` de **8 filas (2 capas x 4 niveles)** que combina DOS corridas de la sonda segun la decision editorial de los autores (**opcion A**):
  - **Niveles 1 y 5** desde la corrida ampliada `evaluation/evidence/load_test_inferencia_ampliada_2026-11-18.json` (60 solicitudes por nivel, 3 repeticiones, 2 capas; n = 90 escalados por nivel y capa; Gemini real; tope USD 1,25).
  - **Niveles 10 y 20** desde la corrida original `evaluation/evidence/load_test_inferencia_2026-11-17.json` (20 solicitudes por nivel, 1 repeticion; n = 10 escalados por nivel y capa).
  - **Cada fila rotula su corrida de origen y su n escalado** en una columna «Corrida/n». Columnas: capa, corrida/n, concurrencia, p50, p95, p99, throughput, tasa de error, escalados, cociente de inferencia y veredicto del nivel. `tab:carga-multicanal` sigue siendo la evidencia **primaria** de capacidad; la sonda es **ancilar** y nunca un resultado de capacidad.
- **Tres veredictos con su condicion.**
  - **Backend `no sostenida`** por la degradacion relativa por inferencia **solo en el nivel 1** (r = 5,05 frente a T = 4); el nivel 5 ahora **cumple** (r = 3,74, contra 5,0 en la corrida original). El techo absoluto de 5000 ms (p95 maximo 3424,2 ms), la tolerancia de throughput y la tasa de error cero se cumplen en los cuatro niveles. **NO es saturacion del backend.**
  - **N8N `no sostenida`** por el techo absoluto de p95 en los niveles 5 (corrida ampliada, 7545,7 ms), 10 (8352,7 ms) y 20 (10183,6 ms); el nivel 1 cumple (2919,8 ms). El cociente de degradacion por inferencia se mantiene dentro de T = 4 (2,35; 1,70; 1,58; 1,22), la tasa de error es cero y el throughput no decrece.
  - **Global `no sostenida`** (el de la peor capa).
- **Cautela del cociente:** la razon no es monotona; en el nivel 20 ambos subconjuntos estan dominados por la cola (p95 deterministico del backend 1782,9 ms), por lo que el cociente **subestima** la contribucion de la inferencia. Se interpreta como comparacion pareada en niveles bajos, no como contribucion marginal a alta concurrencia.
- **Correccion de las afirmaciones** de `07-resultados.tex:336,343`, `08-discusion.tex:10` y `09-conclusiones.tex:6` para distinguir camino deterministico de camino con inferencia incluida, sin retirar la vigencia del veredicto de capacidad. Una oracion de remision en `04-marco-metodologico.tex` la ancla.
- **Limites declarados (siete), con el n y las repeticiones de cada fila.** Una sonda de dos corridas complementarias, no una serie: niveles 1 y 5 con 3 repeticiones y n = 90 escalados por subconjunto, niveles 10 y 20 con 1 repeticion y n = 10; una sola maquina; entorno desechable; el gasto solo consta en la corrida ampliada y su procedencia es `tokens_calculado`, no facturacion del proveedor; deriva posible de proveedor y modelo; no comparable con c-218 (120 solicitudes por nivel) ni extrapolable a produccion.
- **Registro aditivo** en `numeros-canonicos.md`: seccion nueva posterior a la ultima vigente, con las 8 filas rotuladas por corrida de origen, las constantes de **ambas** corridas, valores en estado `condicional` y nota de remision en la `3.29` sin editarla.
- **Tabla en el cuerpo, sin anexo:** 8 filas por 11 columnas entran con `\footnotesize`; la nota cita ambas evidencias. Se sigue el precedente de `tab:carga-multicanal`.
- **Release** posterior: recompilacion, derivados, hash del Anexo B y tag. No se ejecuta en este change.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-document`: ADDED «Reporte de la sonda acotada de latencia con inferencia incluida». MODIFIED «Declaracion del contraste de capacidad de la integracion multicanal» y «Estado declarado de las hipotesis subsidiarias», para separar la evidencia deterministica de capacidad de la sonda con inferencia.
- `tesis-numeros-canonicos`: ADDED «Registro aditivo de la sonda de latencia con inferencia incluida», con estado `condicional` y sin tocar las cifras canonicas de capacidad.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `07-resultados.tex` | Modificado | Subseccion y tabla combinada de dos corridas; dos correcciones |
| `08-discusion.tex` | Modificado | Veredicto deterministico y remision a la sonda |
| `09-conclusiones.tex` | Modificado | «Sin cuello de botella» acotado al camino deterministico |
| `04-marco-metodologico.tex` | Modificado | Una oracion de remision |
| `numeros-canonicos.md` | Aditivo | Seccion nueva con las 8 filas por corrida de origen y nota en `3.29` |
| `dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad |
| `00-portada.tex`, `12-anexos.tex`, `Bibliography_base.bib` | Modificado | Solo en la release: version y hash |

La **enmienda 8** (seccion 8 de `tasks.md`) amplia el Impact: agrega `App/Backend/app/classifiers/{gemini_classifier.py,provider.py}` y `App/Backend/tests/classifiers/` (instrumentacion aditiva `usage_metadata`), `scripts/load_test/` (arnes y prerregistros de la sonda ampliada) y `evaluation/evidence/load_test_inferencia*`. Sin cambios en `n8n/` (el flujo no se toca) ni en la spec `multichannel-load-contrast`; el camino de costo cero del arnes permanece intacto.

## Governance and Approval

- **Gobernanza ALTA:** cambia un veredicto publicado. Requiere aprobacion de los autores y, si afecta la version defendida, del director, antes de escribir cualquier `.tex`.
- **G1 (resuelto):** los autores autorizan informar el veredicto del backend como violacion de una condicion RELATIVA (degradacion por inferencia: `p95 escalado / p95 deterministico > T = 4`), de forma explicita NO como saturacion del backend. El techo absoluto de p95, la tolerancia de throughput y la tasa de error cero se mantienen como cumplidos.
- **G2 (resuelto):** la corrida ampliada ya se ejecuto y la decision editorial es la **opcion A**: informar la tabla combinada de 8 filas (niveles 1 y 5 desde la corrida ampliada; niveles 10 y 20 desde la original), cada fila con su corrida de origen y su n escalado. La suficiencia quedo respondida.
- **G3 (resuelto):** la corrida ampliada registro la instantanea del modelo devuelta por la API `gemini-3.6-flash`; el uso fue de 274920 tokens de entrada, 6648 de salida y 281568 totales; el costo es USD 0,23112 calculado desde tokens con el precio declarado de la tesis (`gasto_origen = tokens_calculado`, no es facturacion del proveedor).
- **G4 (resuelto):** la version de release es `v1.6.1`.
- **Dependencia dura:** se aplica despues de `c-242`, que toca `08-discusion.tex` y `09-conclusiones.tex`; anclajes re-localizados por texto.
- **Release (no ejecutada en este change):** bump a `v1.6.1`, recompilacion, derivados, hash del Anexo B y tag anotado. Nada se commitea ni se taguea sin OK expreso.

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Leer la sonda como capacidad o como refutacion de c-218 | Alta | Primacia declarada de `tab:carga-multicanal` y prohibicion de extrapolar |
| Leer «no sostenida» en el backend como saturacion | Alta | Declarar la condicion relativa y el techo absoluto cumplido |
| Mezclar dos corridas de distinta potencia sin rotularlas | Alta | Columna «Corrida/n» por fila y nota de la tabla con ambas fuentes |
| Sobrevalorar el n por fila (90 y 10) | Alta | Siete limites literales en texto y memo, con n y repeticiones por fila |
| Conflicto de anclajes con `c-242` | Media | Aplicar despues; re-localizar por texto |
| Deriva del modelo entre corridas y defensa | Media | Declararla; la evidencia fija la instantanea devuelta por la API |

## Rollback Plan

Revertir los cinco `.tex`, retirar la seccion del memo y la entrada del registro, y recompilar. La evidencia y el arnes permanecen: el rollback retira la integracion editorial, no las dos corridas.

## Dependencies

- `c-242` aplicado y aprobado por el director.
- Evidencia y prerregistros ya versionados en `evaluation/evidence/` y `scripts/load_test/`.
- Decisiones de autores: G1, G2 (opcion A), G3 y G4 resueltas.

## Success Criteria

- [ ] La tabla combinada coincide cifra por cifra con los DOS JSON, verificado por un test de solo lectura que valida tambien la corrida de origen y el n por fila.
- [ ] `tab:carga-multicanal` sigue siendo la evidencia primaria de capacidad.
- [ ] Las afirmaciones corregidas distinguen ambos caminos y los siete limites figuran en texto y memo.
- [ ] `openspec validate … --strict` y la recompilacion cierran sin errores ni referencias indefinidas.

## Evidencia: tabla combinada de las dos corridas (opcion A)

Valores recomputados desde el JSON de cada corrida; `tab:carga-inferencia` los reproduce cifra por cifra. Cociente `r` a dos decimales (la corrida ampliada afina su precision).

| Capa | Corrida/n | Conc. | p50 | p95 | p99 | sol./s | Error | Esc. | r | Veredicto del nivel |
|---|---|---|---|---|---|---|---|---|---|---|
| Backend | ampl. 90 | 1 | 1007,6 | 2089,3 | 2330,6 | 0,93 | 0,0000 | 90/180 | 5,05 | no cumple (inferencia) |
| Backend | ampl. 90 | 5 | 1221,9 | 2708,4 | 3968,1 | 3,50 | 0,0000 | 90/180 | 3,74 | cumple |
| Backend | orig. 10 | 10 | 1182,9 | 2759,6 | 2763,9 | 6,03 | 0,0000 | 10/20 | 3,55 | cumple |
| Backend | orig. 10 | 20 | 2185,3 | 3424,2 | 3445,8 | 5,76 | 0,0000 | 10/20 | 1,93 | cumple |
| N8N | ampl. 90 | 1 | 1757,9 | 2919,8 | 5033,4 | 0,56 | 0,0000 | 90/180 | 2,35 | cumple |
| N8N | ampl. 90 | 5 | 4307,7 | 7545,7 | 8684,4 | 1,07 | 0,0000 | 90/180 | 1,70 | no cumple (techo) |
| N8N | orig. 10 | 10 | 4519,8 | 8352,7 | 8596,7 | 1,83 | 0,0000 | 10/20 | 1,58 | no cumple (techo) |
| N8N | orig. 10 | 20 | 8378,2 | 10183,6 | 10197,6 | 1,96 | 0,0000 | 10/20 | 1,22 | no cumple (techo) |

- **Constantes de la corrida ampliada:** niveles 1 y 5; 60 solicitudes por nivel; 3 repeticiones; techo de p95 de 5000 ms; tolerancia de throughput de 0,10; tasa de error 0; T = 4; tope USD 1,25; mezcla escalada esperada 0,5.
- **Constantes de la corrida original:** niveles 1/5/10/20; 20 solicitudes por nivel; 1 repeticion; techo de p95 de 5000 ms; tolerancia de throughput de 0,10; tasa de error 0; T = 4; tope USD 1,00; mezcla escalada esperada 0,5.
- **G3:** `model_version` devuelta por la API `gemini-3.6-flash`; tokens de la API (origen `api`): 274920 de entrada, 6648 de salida, 281568 totales; costo calculado desde tokens con el precio declarado de la tesis (escenario `introductorio`) = USD 0,23112; procedencia del gasto `tokens_calculado` (no es facturacion del proveedor).
- **Alcance:** la tabla combinada afina la precision de `r` en los niveles 1 y 5 y registra el gasto y la instantanea del modelo; **no** cambia la evidencia primaria de capacidad (`tab:carga-multicanal`) ni invierte el veredicto global.
- **Trazabilidad:** la corrida ampliada se ejecuto con el arbol de trabajo instrumentado sobre el commit base `d0592d3` (la evidencia registra ese commit base); la instrumentacion aditiva que produce esa evidencia se commiteo en `2159e02`. La corrida original se ejecuto sobre `bbc5865`.
