## Why

La tesis declara como hipótesis subsidiaria que integrar los tres canales (correo, web, telefonía) en un único flujo «no introduce cuellos de botella adicionales» (`01-introduccion.tex:38`), pero nunca midió la capacidad bajo carga concurrente. El dictamen CONEAU sobre `v1.3.0` descuenta en el criterio 1 (peso 15) las «hipótesis subsidiarias sin contraste» y lo repite en la discusión y las conclusiones. Contrastar la dimensión medible (capacidad concurrente) con un test de carga reproducible y de costo cero es la palanca de mayor rendimiento por costo para subir ese criterio sin gasto ni evidencia paga.

## What Changes

- **Arnés de carga reproducible** (`scripts/load_test/`): dispara solicitudes concurrentes contra el tramo compartido (backend `POST /api/v1/incidentes/` y webhook web de N8N) en niveles 1/5/10/20 y mide p50/p95, throughput y tasa de error.
- **Entorno desechable y costo cero**: perfil `corpus` aislado (base `mesa_de_ayuda_corpus`, nunca la operativa) + override con `GEMINI_API_KEY` ficticia y `COST_GUARD_BUDGET_USD=0`; descripciones determinísticas. Cero llamadas pagas, cero Twilio.
- **Criterio de decisión prerregistrado** de tres vías («sostenida»/«no sostenida»/«no concluyente») sobre la ausencia de cuello de botella, fijado antes de correr.
- **Prosa de la tesis** en `01`, `04`, `08` y `09`: la subsidiaria multicanal pasa de «no contrastada» a «contrastada» en su dimensión de capacidad, con el resultado medido y sus límites declarados (complejidad percibida sigue sin instrumento).
- **Registro aditivo**: sección nueva `3.29` en `numeros-canonicos.md` (sin tocar `3.1`-`3.28`) y una entrada en `dictamen-correcciones.md`.

## Capabilities

### New Capabilities

- `multichannel-load-contrast`: arnés de carga de costo cero sobre el tramo compartido multicanal, con niveles de concurrencia, métricas (p50/p95, throughput, tasa de error), criterio de decisión prerregistrado y reporte de evidencia versionado.

### Modified Capabilities

- `tesis-document`: la subsidiaria de integración multicanal pasa de «no contrastada» a «contrastada» en la dimensión de capacidad, con el resultado y los límites declarados.
- `tesis-numeros-canonicos`: se registra la sección canónica del contraste de carga, aditiva.
- `tesis-dictamen-v1-3-0`: el criterio 1 deja de descontar una subsidiaria multicanal sin contraste.

## Impact

- **Código nuevo**: `scripts/load_test/` (arnés, fixture determinística, pruebas offline, override de compose de costo cero). No se toca `App/**`, `docker-compose.yml` ni `n8n/workflow.json`.
- **Documentos editados**: secciones `01/04/08/09` de `docs/Tesis/v10 (IA)/paper/sections/`, `numeros-canonicos.md` y `dictamen-correcciones.md`.
- **Evidencia**: reporte JSON+MD versionado en `evaluation/evidence/`.
- **Costo**: cero. Ninguna llamada paga; el clasificador determinístico resuelve el fixture y la guarda deniega cualquier escalada.
- **Gobernanza**: MEDIUM. No toca el clasificador, el corpus, la referencia, el gate ni ningún valor canónico de `3.1`-`3.28`.

## Success Criteria

- [ ] `openspec validate c-218-… --strict --no-interactive` en verde.
- [ ] El arnés corre el tramo compartido en 1/5/10/20 concurrentes y emite p50/p95, throughput y tasa de error por nivel.
- [ ] El criterio de tres vías y sus constantes están fijados en `design.md` antes de correr, sin reajuste.
- [ ] El reporte de evidencia es determinista, sin secretos y declara commit, fecha UTC y versión de N8N.
- [ ] Las secciones `01/04/08/09` declaran la subsidiaria multicanal como contrastada en capacidad, sin afirmar lo que no se midió.
- [ ] La sección `3.29` es aditiva y ningún valor de `3.1`-`3.28` cambia.
- [ ] Costo cero verificado: ninguna llamada a Gemini ni a Twilio.
