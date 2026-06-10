# Visión y Objetivos

## Propósito del sistema

Automatizar el registro inicial de incidentes de una mesa de ayuda empresarial mediana, integrando orquestación de flujos (N8N), procesamiento de lenguaje natural (FastAPI + Gemini 2.5 Flash) y persistencia relacional (PostgreSQL), de modo que cada incidente reportado por correo, formulario web o llamada telefónica sea clasificado y registrado automáticamente con supervisión humana solo en casos de baja confianza.

Contexto: organización mediana del sector servicios (Mendoza, Argentina), ~120 usuarios internos, ~42 incidentes diarios, registro manual previo de 165,3 s promedio por incidente con ~15 % de derivación errónea. Trabajo Final de Carrera UTN-FRM (Gómez, Bustos, Sevilla, 2026), director Prof. Alberto Cortez.

## Objetivos por actor

| Actor | Objetivo principal | Objetivos secundarios |
|---|---|---|
| Usuario interno | Reportar un incidente en segundos por el canal que prefiera | Recibir confirmación con número de ticket; corregir datos antes de persistir |
| Operador de mesa de ayuda | Dejar de cargar tickets manualmente | Revisar solo la cola de baja confianza (< 0,70) |
| Sector responsable (Sistemas / Operaciones / Soporte Técnico) | Recibir tickets bien derivados | Corregir clasificaciones erróneas (validación → corpus) |
| Organización | Liberar ~200 horas-persona/trimestre | Trazabilidad completa; cumplimiento Ley 25.326 |
| Equipo de investigación | Validar empíricamente la hipótesis | Corpus etiquetado de 200 casos; métricas reproducibles |

## Alcance v1.0

- Recepción de incidentes por 3 canales paralelos: correo electrónico (IMAP), formulario web (webhook/frontend React) y llamada telefónica (Twilio + transcripción automática).
- Clasificación automática híbrida en 2 etapas (reglas determinísticas → Gemini 2.5 Flash) hacia 3 sectores: **Sistemas**, **Operaciones**, **Soporte Técnico**.
- Registro persistente en PostgreSQL con trazabilidad de cada decisión del clasificador (`clasificacion_log`).
- Cola de revisión humana FIFO para casos con confianza < 0,70 (human in the loop).
- Pseudonimización de datos personales antes de transmitir a Gemini (Ley 25.326).
- Evaluación experimental sobre corpus de 200 casos con métricas estándar.

## Fuera de alcance

- Resolución técnica de los incidentes (permanece humana).
- Integración con sistemas externos de inventario.
- Modelos de aprendizaje supervisado entrenados con corpus propio.
- Paneles de monitoreo en tiempo real (Prometheus/Grafana — línea futura).
- Automatización de la etapa de resolución.
- Canales de mensajería instantánea (Slack/Teams — línea futura).

## Métricas de éxito

| Métrica | Objetivo (tesis) | Resultado reportado |
|---|---|---|
| Exactitud global de clasificación | ≥ 85 % | **92 %** (IC 95 % Wilson [87,2 ; 95,2]) |
| F1 macro promediado | ≥ 0,85 | **0,919** |
| Tiempo medio de registro | Reducción significativa | 165,3 s → **18,2 s** (−89 %, Wilcoxon p < 0,001) |
| Intervención humana | Reducción sustancial | 100 % → **9,5 %** |
| Resolución en etapa determinística | Maximizar (costo/latencia) | **~62 %** de los casos sin invocar Gemini |
