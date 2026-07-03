# C-22: Tesis — Dashboard de Analitica y Politica de Conservacion

## Por que

El usuario definio una nueva funcionalidad mayor: un dashboard de analitica con graficos de tendencias que permita identificar problemas recurrentes y atacar causas raiz (ej: 20 auriculares rotos en una semana → problema de calidad del proveedor). Esto requiere documentarse en la tesis como evolucion del sistema, junto con dos decisiones de diseno derivadas: conservacion indefinida de incidentes y bloqueo de escritura sobre incidentes cerrados.

## Que cambia en la tesis

### Capitulo 6 (Implementacion) — Nueva seccion 6.8

**Dashboard de Analitica**: descripcion de la funcionalidad, componentes (ReCharts), endpoints de estadisticas, filtros por dia/mes, exportacion de graficos.

### Capitulo 10 (Recomendaciones y Trabajo Futuro) — Modificar

Reemplazar la recomendacion "paneles de monitoreo avanzados con visualizacion en tiempo real" por la descripcion del dashboard YA implementado. Agregar como trabajo futuro: alertas automaticas basadas en umbrales de tendencias.

### Capitulo 11 (Aspectos Legales) — Modificar §11.2

Reemplazar la politica de retencion con eliminacion (90 dias / 1 ano) por una politica de **conservacion indefinida con bloqueo de escritura**:
- Incidentes abiertos/en proceso: lectura y escritura completas
- Incidentes cerrados: solo lectura. No se pueden editar ni eliminar desde la UI. Permanecen como registro auditable permanente.
- Justificacion: el valor estadistico de los datos historicos para analisis de tendencias supera el costo de almacenamiento. La pseudonimizacion y el cifrado en reposo garantizan la proteccion de datos personales incluso en conservacion prolongada.

### Anexos — Actualizar

- Anexo C (esquema BD): sin cambios (el modelo ya soporta conservacion indefinida)
- Anexo G (documentacion operativa): agregar seccion sobre el dashboard

## Gobernanza

MEDIUM — cambios documentales en LaTeX.

## Dependencias

C-23 (implementacion del dashboard) — la tesis documenta lo que C-23 construye.
