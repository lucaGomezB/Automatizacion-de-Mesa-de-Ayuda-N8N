# Design — c-72-unificar-clasificacion-telefonica

## Context

Ver `proposal.md` — Intent y evidencia medida. Estado actual relevante:

- `IncidenteService._resolve_classification` (`App/Backend/app/services/incidente_service.py`): si `payload.clasificacion` viene, construye el resultado con `_result_from_precalculated` (etapa `precalculada`) y NO invoca al clasificador. Solo telefonia puebla ese campo (el `AI Agent` de n8n lo produce).
- `n8n/workflow.json` cablea el webhook telefonico -> `AI Agent` (`@n8n/n8n-nodes-langchain.agent` + `Google Gemini Chat Model`) -> validacion -> `Entrada valida` -> `HTTP POST a MESA-AYUDAS`. El body del POST incluye `clasificacion`. La guarda `n8n_gemini` se reserva antes del agente (`Guard permite?`).
- La cascada del backend (`HybridClassifier`) es la fuente de verdad para correo/web y queda endurecida por c-71 (piso de precision 0.90, `min_matches >= 2`, no-match/empate escalan).
- `docs/prompt_gemini.txt` es el prompt de Gemini del backend; el `AI Agent` de n8n tiene su propio prompt (divergente).
- Los cinco strings canonicos estan LOCKED; `evaluation/corpus.py::_a_float` es intocable; no hay migracion (el esquema persistente no cambia).

## Goals / Non-Goals

**Goals**

- Un unico camino de clasificacion (cascada del backend) para correo, web y telefonia.
- Eliminar el atajo precalculado de telefonia y el prompt divergente de n8n.
- Trasladar el costo de la clasificacion telefonica de `n8n_gemini` a `backend_gemini` solo en escalacion.
- Corregir errores de frontera una sola vez, en el prompt compartido.

**Non-Goals**

- No re-calibrar el determinista (c-71).
- No cambiar los cinco strings canonicos, ni `_a_float`, ni el esquema persistente (sin migracion).
- No resolver el backfill de incidentes historicos (OQ4).

## Decisions

### D1: Telefonia clasifica por la cascada del backend

Para telefonia, `_resolve_classification` MUST resolver por `self._classifier.classify(texto_pseudonimizado)`, ignorando cualquier `clasificacion` precalculada del canal. La descripcion que entra a la cascada es la pseudonimizada (el borde de pseudonimizacion se preserva). Alternativa: mantener el atajo para telefonia y solo alinear el prompt — descartada porque conserva dos clasificadores, dos prompts y el costo Gemini siempre. Alternativa: clasificar telefonia en n8n con el prompt compartido — descartada porque duplica la cascada determinista en n8n y mantiene el costo.

### D2: Retiro del atajo precalculado

El workflow telefonico MUST NOT enviar `clasificacion` al backend. El backend MUST NOT usar una `clasificacion` precalculada de telefonia para omitir la cascada. Decision de alcance del contrato: el campo `clasificacion` de `IncidenteCreate` se conserva por compatibilidad pero deja de tener efecto para el canal telefonico; su eliminacion total del schema queda como ajuste posterior si el autor lo decide (no bloquea). Alternativa: eliminar el campo ya — descartada por ser un cambio de contrato de API mas amplio que el alcance (afecta OpenAPI y consumidores).

### D3: Reestructuracion del workflow de n8n

La rama `AI Agent` de telefonia se retira de la ruta de clasificacion o se reduce a un rol que NO determina el sector persistido. La decision exacta (retirar vs sub-caso) es OQ1 del autor. El diseno garantiza que, en cualquiera de los dos casos, el sector persistido provenga del backend y que el POST no transporte `clasificacion`. Si se conserva una invocacion reducida, MUST quedar explicitamente acotada y sujeta a la guarda de costo. El bucle de refinamiento (2 intentos) es OQ3: si no se conserva, se preserva un camino terminal con `requiere_revision_humana=true`.

### D4: Reglas de frontera en el prompt compartido

`docs/prompt_gemini.txt` incorpora reglas de desambiguacion de frontera, unico prompt de clasificacion del sistema. Reglas minimas (redaccion final: OQ5): acceder/iniciar sesion/abrir una aplicacion o sistema operativo -> `Soporte Tecnico Software`; digitalizar/escaner/impresora/periferico/error de digitalizacion -> `Soporte Tecnico Hardware`; servidor/red/SMTP/VM -> `Sistemas`. Las reglas usan los cinco strings canonicos sin tildes y no introducen sectores nuevos.

### D5: Traslado de la superficie de costo

La clasificacion telefonica MUST NOT reservar `n8n_gemini`. Cuando la cascada del backend escala a la etapa semantica para telefonia, la reserva corresponde a `backend_gemini` conforme al enforcement vigente. Si el workflow conserva una invocacion reducida a un modelo, esa invocacion MUST quedar sujeta a la guarda y acotada. Alternativa: mantener la reserva `n8n_gemini` — descartada porque el canal deja de invocar al agente como clasificador.

### D6: Medicion del beneficio determinista-primero en telefonia

Se mide, OFFLINE sobre el corpus y sin invocar Gemini, la fraccion de casos telefonicos que cortocircuitan, la exactitud estricta del subconjunto cortocircuitado y la cobertura del vocabulario. Reutiliza el corpus y `evaluation/metrics.py`; MUST NOT tocar `_a_float`. El delta de F1 hibrido se reporta cuando haya cuota de Gemini (dependencia de c-71 OQ5).

### D7: Documentacion y narrativa

Anexo H (`docs/anexo_h_prompt_gemini.md`) y la narrativa de tesis se actualizan al camino unico. No es un cambio de esquema ni de contrato de API.

### D8: TDD y tests estructurales

Todo cambio de codigo con RED-GREEN-TRIANGULATE-REFACTOR y safety net por tarea. Tests estructurales del workflow: el POST no incluye `clasificacion`, la rama `AI Agent` no determina el sector, no hay ramas terminales sin salida, y el prompt compartido contiene las reglas de frontera. Tests de contrato: telefonia usa la cascada.

### D9: Gobernanza

ALTO. Cambia la arquitectura de clasificacion documentada en la tesis, afloja/elimina una rama del workflow y mueve el costo de `n8n_gemini` a `backend_gemini`. Las decisiones de reestructuracion y costo quedan como OQ para el autor.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|--------|------------|
| El atajo determinista telefonico escala mas de lo previsto | Gate c-71 (piso de precision 0.90); medir (D6) antes de cerrar |
| Reestructuracion del workflow deja ramas sin salida | Tests estructurales de alcanzabilidad; OQ1 |
| Perder el refinamiento degrada casos recuperables | OQ3; camino terminal con revision humana |
| El atajo precalculado se mantiene por compatibilidad y se usa por error | Test de contrato: telefonia MUST resolver por cascada |
| Backfill de historicos | OQ4; no mutar datos en este change |
| Tocar strings canonicos o `_a_float` | Prohibido; tests estructurales lo verifican |

## Migration Plan

1. Backend: `_resolve_classification` clasifica telefonia por cascada (TDD).
2. n8n: quitar `clasificacion` del POST; retirar/reducir la rama `AI Agent` (tests estructurales).
3. Prompt compartido: reglas de frontera.
4. Cost guard: quitar la reserva `n8n_gemini` por clasificar telefonia.
5. Evaluacion: medir el beneficio determinista-primero en telefonia.
6. Docs: Anexo H y narrativa.

Rollback: revertir el commit restaura POST, workflow, prompt y reserva; sin migraciones ni pasos de datos.

## Open Questions

Las siguientes OQ las resuelve el autor (ver proposal.md). Ninguna bloquea la escritura de artefactos; cada una gatea tareas marcadas en `tasks.md` §0:

- **OQ1**: retirar el `AI Agent` vs conservarlo para un sub-caso (gatea D3 y §2).
- **OQ2**: confirmar el traslado de `n8n_gemini` a `backend_gemini` (gatea D5 y §4).
- **OQ3**: preservar o no el bucle de refinamiento (gatea D3 y §2).
- **OQ4**: backfill de incidentes telefonicos historicos (gatea §6).
- **OQ5**: redaccion final de las reglas de frontera (gatea D4 y §3).
