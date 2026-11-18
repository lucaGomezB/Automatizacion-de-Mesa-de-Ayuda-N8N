# Proposal: Integrar la latencia con inferencia en la tesis

## Why

La corrida paga acotada TASK B (commit `bbc5865`, release `v1.6.0`) ya midio la latencia del tramo compartido con inferencia real incluida. El ejemplar todavia afirma que «la latencia con inferencia no se midio» y que el backend no tiene cuello de botella en el punto de convergencia: ambas cosas son verdaderas solo para el camino deterministico de costo cero. El manuscrito omite una medicion propia y queda expuesto a una pregunta directa en la defensa.

## What Changes

- **Nueva subseccion** `subsec:latencia-con-inferencia` en `07-resultados.tex`, despues de `subsec:carga-concurrente`, con `tab:carga-inferencia` desde `evaluation/evidence/load_test_inferencia_2026-11-17.json`. Columnas: capa, concurrencia, p50/p95/p99, throughput, tasa de error, fraccion escalada, cociente de inferencia y veredicto del nivel. `tab:carga-multicanal` sigue siendo la evidencia **primaria** de capacidad; la sonda es **ancilar**, de una sola corrida y nunca un resultado de capacidad.
- **Dos veredictos con su condicion.** Backend `no sostenida` por la degradacion relativa por inferencia en los niveles 1 y 5 (11,3 y 5,0 frente a T = 4), con techo absoluto y throughput cumplidos; N8N `no sostenida` por el techo absoluto de p95 en 10 y 20 (8352,7 y 10183,6 ms), con el cociente dentro de T = 4. Ambas capas: 0 errores.
- **Correccion de las afirmaciones** de `07-resultados.tex:336,343`, `08-discusion.tex:10` y `09-conclusiones.tex:6` para distinguir camino deterministico de camino con inferencia incluida, sin retirar la vigencia del veredicto de capacidad. Una oracion de remision en `04-marco-metodologico.tex` la ancla.
- **Limites declarados:** una corrida, n = 10 por subconjunto, una sola maquina, entorno desechable, gasto no registrado en la evidencia, deriva posible de proveedor y modelo, no comparable con c-218 (120 solicitudes por nivel) y no extrapolable a produccion.
- **Registro aditivo** en `numeros-canonicos.md`: seccion nueva posterior a la ultima vigente, valores en estado `condicional` y nota de remision en la `3.29` sin editarla.
- **Tabla en el cuerpo, sin anexo:** 8 filas por 10 columnas entran con `\footnotesize`; la nota cita la evidencia. Se sigue el precedente de `tab:carga-multicanal`.
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
| `07-resultados.tex` | Modificado | Subseccion y tabla nuevas; dos correcciones |
| `08-discusion.tex` | Modificado | Veredicto deterministico y remision a la sonda |
| `09-conclusiones.tex` | Modificado | «Sin cuello de botella» acotado al camino deterministico |
| `04-marco-metodologico.tex` | Modificado | Una oracion de remision |
| `numeros-canonicos.md` | Aditivo | Seccion nueva y nota en `3.29` |
| `dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad |
| `00-portada.tex`, `12-anexos.tex`, `Bibliography_base.bib` | Modificado | Solo en la release: version y hash |

Sin cambios en `App/`, `n8n/`, `evaluation/`, `data/`, `scripts/load_test/` (el arnes y la guarda de costo cero no se tocan) ni en la spec `multichannel-load-contrast`.

## Governance and Approval

- **Gobernanza ALTA:** cambia un veredicto publicado. Requiere aprobacion de los autores y, si afecta la version defendida, del director, antes de escribir cualquier `.tex`.
- **G1 (confirmado):** los autores autorizan informar el veredicto del backend como violacion de una condicion RELATIVA (degradacion por inferencia: `p95 escalado / p95 deterministico > T = 4`), de forma explicita NO como saturacion del backend. El techo absoluto de p95, la tolerancia de throughput y la tasa de error cero se mantienen como cumplidos.
- **G2 y G3 (abiertas):** la suficiencia de una corrida con n = 10 por subconjunto y el gasto/instantanea del modelo siguen sin respuesta; una investigacion aparte esta en curso (se evaluan una corrida acotada de repeticion y un plan de instrumentacion). El change no debe afirmar el gasto ni la instantanea del modelo como medidos hasta que se registren.
- **G4 (resuelto):** la version de release es `v1.6.1` (corrige la propuesta previa).
- **Dependencia dura:** se aplica despues de `c-242`, que toca `08-discusion.tex` y `09-conclusiones.tex`; anclajes re-localizados por texto.
- **Release (no ejecutada en este change):** bump a `v1.6.1`, recompilacion, derivados, hash del Anexo B y tag anotado. Nada se commitea ni se taguea sin OK expreso.

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Leer la sonda como capacidad o como refutacion de c-218 | Alta | Primacia declarada de `tab:carga-multicanal` y prohibicion de extrapolar |
| Leer «no sostenida» en el backend como saturacion | Alta | Declarar la condicion relativa y el techo absoluto cumplido |
| Sobrevalorar una corrida unica con n = 10 | Alta | Siete limites literales en texto y memo |
| Conflicto de anclajes con `c-242` | Media | Aplicar despues; re-localizar por texto |
| Gasto y version del modelo no registrados | Media | Declararlo; no estimarlo como medido |

## Rollback Plan

Revertir los cinco `.tex`, retirar la seccion del memo y la entrada del registro, y recompilar. La evidencia y el arnes permanecen: el rollback retira la integracion editorial, no la corrida.

## Dependencies

- `c-242` aplicado y aprobado por el director.
- Evidencia y prerregistro ya versionados en `evaluation/evidence/` y `scripts/load_test/`.
- Decisiones de autores: G1 y G4 resueltas; G2 (suficiencia de una corrida) y G3 (gasto/instantanea del modelo) abiertas, con una investigacion aparte en curso.

## Success Criteria

- [ ] La tabla coincide cifra por cifra con el JSON, verificado por un test de solo lectura.
- [ ] `tab:carga-multicanal` sigue siendo la evidencia primaria de capacidad.
- [ ] Las afirmaciones corregidas distinguen ambos caminos y los siete limites figuran en texto y memo.
- [ ] `openspec validate … --strict` y la recompilacion cierran sin errores ni referencias indefinidas.
