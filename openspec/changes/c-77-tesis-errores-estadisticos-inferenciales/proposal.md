# Proposal: c-77 — Errores estadístico-inferenciales y coherencia técnica de la tesis

## Why

El dictamen CONEAU y una auditoría contra el corpus real detectaron que los
capítulos 4, 7, 8 y 9 de la tesis (LaTeX) contienen errores
estadístico-inferenciales no cubiertos por c-76: convención y fórmula del tamaño
del efecto incoherentes (`W=0`, rango falso `[-1,+1]`), ausencia total de
calibración de la confianza, proyección de horas-persona aritméticamente
imposible y rótulos estadísticos erróneos. En paralelo persisten
desalineaciones técnicas con el sistema real (reintentos inexistentes, prompt de
5 sectores, tag inexistente). c-77 profundiza el tratamiento estadístico y la
coherencia técnica. c-76 cubre los números del corpus y el redondeo de tiempos;
c-77 NO los duplica.

## What Changes

### Grupo A — Estadística e inferencia

| Id | Corrección | Evidencia |
|----|-----------|-----------|
| A1 | Declarar la convención de `W` (scipy two-sided = `min(T+,T-)`), reportar `T+=19765` y `T-=335`, eliminar `W=0` | `07-resultados.tex:30,34`; `04:69` |
| A2 | Corregir fórmula a `r=(T+−T−)/(n(n+1)/2)` (`1−4W/(n(n+1))` si `W=T−`), rango real `[0,1]`, recalcular `r=0,9667` (no `1,00`) | `04:65,67`; `07:34` |
| A3 | `08:12` dice "varianza casi diez veces menor" comparando desvíos (38,7 vs 4,1 s); corregir a "desvío estándar" | `08-discusion.tex:12` |
| A4 | Proyección "180 h-persona/trimestre" imposible; mostrar cálculo en nota al pie y corregir (real ≈48,1 h) | `08:14`, `09:24`, `01:18` |
| A5 | Unificar "intervención humana": tiempo (`04:34`) vs casos (`07:86`, 9,5 %=19/200) | `04:34,57`; `07:86` |
| A6 | Reportar la curva de calibración confianza–exactitud y discutirla; la confianza está anti-calibrada (alta: 0,697; baja: 0,758) | `predicciones.json`; nuevo en cap. 7/8/6.3/11.5 |
| A7 | Reconciliar 42 inc/día con ~3.700/trimestre (3.700=42×88); declarar los días del trimestre | `01:18`; `04:43` |

### Grupo B — Pregunta de investigación

- **B1**: la sub-pregunta "exactitud comparable o superior a la del criterio
  humano" (`01:28`) nunca se mide — decisión del autor (OQ).
- **B2**: coincidencia no explicada entre el tiempo preliminar `2 min 45 s`
  (`01:18`) y la media experimental `165,3 s` (`07:10`); el corpus real promedia
  `61,6 s` — explicar la relación.

### Grupo C — Coherencia técnica

- **C1/C2**: verificado — el flujo real (clasificar → gate) y la remoción del
  agente LLM telefónico ya están alineados (c-72). Sin cambio.
- **C3**: verificado — el canal SÍ llega al backend (`canal_origen_id`, opcional).
  Solo alinear el nombre de campo stale en cap. 5. Sin defecto funcional.
- **C4**: C4: `06:60` declara reintento con backoff + cola; no existen en
  `n8n/workflow.json` ni en `App/Backend` — decisión del autor (OQ).
- **C5**: `nginx` + TLS 1.2/1.3 SÍ están en `docker-compose.yml:234` y
  `nginx/nginx.conf:70` (C-20). Reconciliar el condicional de la tesis (OQ).
- **C6**: cerrar los residuos de C-18 (IMAP `06:37`/`12:37`; catálogo de 3
  sectores) y anexar el log de decisiones
  (`docs/Tesis/Correcciones/dictamen-correcciones.md`).
- **C7**: el prompt usa 5 sectores (`docs/prompt_gemini.txt:5-25`) y la tesis
  declara 3 — unificar a 5 (reconciliar con c-27) — decisión del autor (OQ).
- **C8**: el tag `v1.0.0` (`12:19`) no existe (`git tag` vacío) — decisión del
  autor (OQ).

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `tesis-document`: rigor inferencial del tamaño del efecto, calibración de la
  confianza, aritmética metodológica verificable, rótulos de dispersión,
  coherencia técnica tesis–implementación y trazabilidad de la pregunta de
  investigación humana.
- `evaluation-framework`: convención y fórmula del rank-biserial, y reporte de
  la calibración de confianza.

## Impact

Solo documentación y artefactos (sin tocar `App/**` salvo decisión del autor):
`docs/Tesis/v9 (IA)/paper/sections/{01,04,05,06,07,08,09,11,12}*.tex`,
`main.pdf`, `evaluation/stats.py` (corrección de fórmula/efecto),
`evaluation/report.md`, `docs/prompt_gemini.txt`,
`docs/Tesis/Correcciones/dictamen-correcciones.md`.

## Rollback Plan

`git checkout --` sobre los `.tex`/docs afectados, o `git revert` del commit del
change. El cambio en `evaluation/stats.py` se revierte igual. Los artefactos OPSX
se descartan con el directorio del change.

## Success Criteria

- [ ] `W=0` y `r=1,00` desaparecen; se declara la convención y se reportan `T+`/`T−`.
- [ ] Fórmula corregida a `(T+−T−)/(n(n+1)/2)`, rango `[0,1]`, recalculo `0,9667`.
- [ ] Tabla/curva de calibración confianza–exactitud presente y discutida.
- [ ] 3.700 reconciliado con 42/día y días del trimestre declarados.
- [ ] Proyección de horas-persona con cálculo explícito y valor corregido.
- [ ] Sin "varianza" donde corresponde "desvío estándar"; intervención humana unificada.
- [ ] Sin prompt de "4 sectores" (queda en 5 canónicos) ni tag inexistente.
- [ ] Reintentos/Nginx/C6 resueltos por decisión documentada (OQ).
- [ ] `pdf` recompilado en Overleaf sin errores fatales.
- [ ] `openspec validate c-77-tesis-errores-estadisticos-inferenciales --strict` pasa.
