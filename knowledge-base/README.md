# Automatización de Mesa de Ayuda N8N — Base de Conocimiento

KB generada por ingesta desde `docs/Tesis/tesis_para_agente.md` (tesis completa UTN-FRM 2026), `docs/parameters_gemini.md`, `docs/prompt_gemini.txt`, `ANEXO_H_Prompt_Gemini_Especificacion.md` y verificación contra el código real del repositorio.

## Índice de Archivos

| Archivo | Contenido |
|---|---|
| [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito, objetivos por actor, alcance v1.0, métricas de éxito |
| [02_descripcion_general.md](02_descripcion_general.md) | Stack, arquitectura de 5 capas, integraciones, API REST |
| [03_actores_y_roles.md](03_actores_y_roles.md) | Actores, RBAC objetivo, human in the loop |
| [04_modelo_de_datos.md](04_modelo_de_datos.md) | 5 entidades, ERD, seed data, retención |
| [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | RN-CL, RN-VA, RN-RH, RN-PR (Ley 25.326), RN-RE, RN-EX |
| [06_funcionalidades.md](06_funcionalidades.md) | 15 US por épica con estado y referencia a changes |
| [07_flujos_principales.md](07_flujos_principales.md) | 5 flujos E2E con casos de error |
| [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Patrones, estructura real, seguridad, env vars |
| [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | 11 decisiones + 5 supuestos |
| [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | 6 inconsistencias tesis↔código + preguntas priorizadas |
| [11_evaluacion_experimental.md](11_evaluacion_experimental.md) | Corpus, métricas, resultados esperados (alimenta C-08) |

## Quick Start para Desarrolladores

1. Entender el dominio → [01](01_vision_y_objetivos.md), [03](03_actores_y_roles.md)
2. Entender los datos → [04](04_modelo_de_datos.md)
3. Entender las reglas → [05](05_reglas_de_negocio.md)
4. Entender la arquitectura → [02](02_descripcion_general.md), [08](08_arquitectura_propuesta.md)
5. Implementar → [07](07_flujos_principales.md), [06](06_funcionalidades.md), `CHANGES.md` (roadmap de 10 changes)
6. Antes de codificar → [10](10_preguntas_abiertas.md)

## Resumen Ejecutivo

Sistema de registro automático de incidentes para mesa de ayuda mediana: tres canales de entrada (correo, web, teléfono) convergen vía N8N en una API FastAPI que clasifica cada incidente con un pipeline híbrido (reglas determinísticas ≥0,90 → Gemini 2.5 Flash → fallback) hacia Sistemas, Operaciones o Soporte Técnico, persiste en PostgreSQL con trazabilidad completa y deriva los casos de confianza <0,70 a revisión humana. Resultados validados: 92 % exactitud, F1 macro 0,919, −89 % de tiempo de registro, 9,5 % de intervención humana. Backend y frontend están completos; faltan: webhook N8N (C-02), pseudonimización Ley 25.326 (C-03), workflow N8N real (C-04/05), tests de integración (C-06/07), evaluación (C-08), CI/CD (C-09) y anexos (C-10).
