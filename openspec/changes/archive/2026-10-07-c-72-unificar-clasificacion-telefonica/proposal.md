# Proposal: Unificar la clasificacion telefonica en la cascada del backend (c-72)

## Intent

Hoy la clasificacion ocurre en DOS lugares: correo/web usan la cascada del backend (`HybridClassifier`: determinista primero, Gemini solo si la confianza es insuficiente, revision humana), mientras que telefonia usa el `AI Agent` de n8n (Gemini SIEMPRE) y entrega una `clasificacion` precalculada que el backend persiste sin correr la cascada (`IncidenteService._resolve_classification`). Consecuencias: dos clasificadores, dos prompts divergentes, telefonia siempre paga Gemini (sin atajo determinista) y errores de frontera que se corrigen por separado.

Evidencia medida: sobre el corpus de 200 casos, telefonia escala a Gemini 55.6% y los casos cortocircuitados tienen exactitud estricta 0.47 (c-71). En el subconjunto telefonico medido (25 casos) la pertenencia multietiqueta fue 92% pero el sector primario estricto solo 56%; casos de frontera: R002 "acceder al sistema" -> IA dijo `Sistemas` vs corpus `Soporte Tecnico Software`; R038 "error de digitalizacion" -> IA dijo `Soporte Tecnico Software` vs corpus `Soporte Tecnico Hardware`.

Objetivo: UN SOLO camino de clasificacion para los tres canales. Telefonia gana el atajo determinista (mas barato, menos Gemini), un unico prompt y la correccion de frontera aplicada una vez para todos.

## Scope

### In Scope

- El handoff telefonico DEJA de enviar la `clasificacion` precalculada; el backend clasifica telefonia como correo/web.
- Retirar/ajustar la rama `AI Agent` de telefonia en `n8n/workflow.json` y su reserva `n8n_gemini` / bucle de refinamiento (o justificar un rol reducido).
- Agregar reglas de frontera al prompt COMPARTIDO `docs/prompt_gemini.txt` (beneficia a los tres canales).
- Actualizar Anexo H / docs y la narrativa de tesis.
- Evaluar el beneficio determinista-primero para telefonia sobre el corpus.

### Out of Scope

- No se cambian los cinco strings canonicos ni el esquema persistente (sin migracion).
- No se re-calibra el determinista: eso es c-71 (prerequisito).
- No se toca `evaluation/corpus.py::_a_float`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `sector-assignment`: un unico camino de clasificacion para los tres canales; sin atajo precalculado para telefonia.
- `classification-resilience`: la resiliencia telefonica pasa a la cascada del backend; escalamiento y fallback vigentes.
- `n8n-workflow`: el POST no envia clasificacion precalculada; el `AI Agent` no determina el sector persistido.
- `runtime-cost-guard`: la clasificacion telefonica deja de reservar `n8n_gemini`; la escalacion reserva `backend_gemini`.
- `sector-taxonomy`: reglas de desambiguacion de frontera en el prompt compartido.
- `telefonia-stt-intake`: la clasificacion telefonica es propiedad del backend sobre la descripcion pseudonimizada.

## Approach

1. Backend: para telefonia, `_resolve_classification` MUST resolver por la cascada, ignorando cualquier `clasificacion` precalculada del canal.
2. n8n: el POST deja de incluir `clasificacion`; la rama `AI Agent` se retira o se reduce a un rol que NO determina el sector persistido.
3. Prompt: `docs/prompt_gemini.txt` incorpora reglas de frontera (acceder/iniciar sesion -> Software; digitalizar/escaner/impresora -> Hardware; servidor/red/SMTP/VM -> Sistemas).
4. Cost guard: sin reserva `n8n_gemini` por clasificar telefonia; `backend_gemini` se reserva solo si la cascada escala.
5. Evaluacion: medir cobertura del atajo determinista y F1 estricto en telefonia sobre el corpus.
6. Docs: Anexo H y narrativa alineados al camino unico.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `App/Backend/app/services/incidente_service.py` | Modified | `_resolve_classification` clasifica telefonia por cascada |
| `App/Backend/app/schemas/incidente.py` | Modified | `clasificacion` precalculada deja de usarse para telefonia |
| `App/Backend/app/classifiers/` | Unchanged | La cascada de c-71 se reutiliza tal cual |
| `n8n/workflow.json` | Modified | POST sin clasificacion; rama `AI Agent` retirada/reducida |
| `docs/prompt_gemini.txt` | Modified | Reglas de frontera compartidas |
| `docs/anexo_h_prompt_gemini.md`, `docs/Tesis/` | Modified | Documentacion y narrativa |
| `evaluation/` | Modified | Medicion determinista-primero en telefonia |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| El atajo determinista telefonico sea debil y escale mas de lo previsto | Med | Gate de c-71 (piso de precision 0.90, `min_matches >= 2`); medir antes de cerrar |
| La reestructuracion del workflow deje ramas terminales sin salida | Med | Tests estructurales de alcanzabilidad; OQ del autor |
| Perdida del bucle de refinamiento degrade casos que hoy se recuperan | Med | OQ explicita; conservar un camino terminal con revision humana |
| Cambio de contrato (`clasificacion`) rompa consumidores | Baja | Solo se ignora para telefonia; tests de contrato/API |
| Incidentes telefonicos ya creados con sector precalculado | Baja | OQ de backfill; documentar, no mutar en este change |

## Rollback Plan

Revertir el commit restaura el POST con `clasificacion` precalculada, la rama `AI Agent` y el prompt anterior. Sin migraciones ni cambios de esquema persistente: el rollback es de codigo, workflow y prompt, y no requiere pasos de datos. Los incidentes creados durante la vigencia del change conservan su sector.

## Dependencies

- **c-71** (`hardening-clasificador-determinista`), PREREQUISITO: el atajo determinista debe estar endurecido (hoy telefonia cortocircuitaria ~44% con ~47% de exactitud estricta). NO unificar antes de que c-71 aterrice.
- Corpus `data/corpus_evaluacion_pseudonimizado.json` (200 casos, no trackeado).

## Open Questions (autor)

- **OQ1**: reestructuracion exacta del workflow: eliminar el `AI Agent` por completo para telefonia, o conservarlo solo para un sub-caso.
- **OQ2**: implicancias de costo: desaparece la reserva `n8n_gemini` para telefonia y aplica `backend_gemini` en escalacion. Confirmar aceptable.
- **OQ3**: si el bucle de refinamiento (2 intentos) debe preservarse en algun lugar.
- **OQ4**: backfill necesario para incidentes telefonicos ya creados con sector precalculado.
- **OQ5**: redaccion final de las reglas de frontera del prompt compartido (matices de dominio del autor).

## Success Criteria

- [ ] Telefonia se clasifica por la cascada del backend; no se persiste una clasificacion precalculada de telefonia.
- [ ] El POST de n8n no envia `clasificacion` y la rama `AI Agent` no determina el sector persistido.
- [ ] El prompt compartido contiene reglas de frontera para los tres canales y no hay prompt divergente.
- [ ] La clasificacion telefonica no reserva `n8n_gemini`; la escalacion reserva `backend_gemini`.
- [ ] Beneficio determinista-primero de telefonia medido sobre el corpus y documentado.
- [ ] `openspec validate c-72-unificar-clasificacion-telefonica --strict` pasa; tests TDD y estructurales en verde.
