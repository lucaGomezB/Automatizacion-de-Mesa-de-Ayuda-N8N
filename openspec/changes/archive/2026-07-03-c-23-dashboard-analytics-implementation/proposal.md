# C-23: Dashboard de Analitica — Implementacion Completa

## Por que

El sistema actual permite crear, listar, clasificar y validar incidentes, pero no ofrece visibilidad agregada sobre tendencias. Un operador no puede responder preguntas como: "¿cuantos incidentes de Soporte Tecnico hubo este mes?", "¿hay un pico de fallas de hardware los lunes?", o "¿que categoria crecio mas en el ultimo trimestre?". Sin esta visibilidad, problemas sistemicos (lotes defectuosos, fallas recurrentes de infraestructura) pasan desapercibidos.

El usuario definio que quiere: dashboard con graficos ReCharts, filtros por dia/mes, exportacion de graficos, conservacion indefinida de incidentes (cancelando C-21), y bloqueo de escritura sobre incidentes cerrados.

## Que cambia

### Backend — Nuevo endpoint de estadisticas

**`GET /api/v1/estadisticas/tendencias`**

Parametros: `agrupar_por` (dia|mes), `desde`, `hasta`, `sector_id` (opcional)

Respuesta:
```json
{
  "periodo": {"desde": "2026-01-01", "hasta": "2026-06-30", "agrupar_por": "mes"},
  "total_incidentes": 3700,
  "series": [
    {"periodo": "2026-01", "total": 310, "por_sector": {"Sistemas": 127, "Operaciones": 99, "Soporte Tecnico": 84}},
    ...
  ],
  "distribucion_sectores": {"Sistemas": 1517, "Operaciones": 1184, "Soporte Tecnico": 999},
  "distribucion_estados": {"nuevo": 150, "en proceso": 400, "cerrado": 3000, ...}
}
```

**`GET /api/v1/estadisticas/resumen`**

Respuesta: totales, promedio diario, top sectores, tasa de revision humana.

### Backend — Endpoints de vistas ya existentes (verificar/mejorar)

`GET /api/v1/incidentes/` ya soporta filtros `?estado=abierto`, `?sector_id=X`. Verificar que `?estado=cerrado` funcione correctamente. Agregar `?usuario_id=X` si no existe (requiere relacion incidente→usuario — posiblemente nuevo campo).

### Backend — Bloqueo de escritura en incidentes cerrados

En `PATCH /api/v1/incidentes/{id}`: si el incidente esta en estado "cerrado" (`es_terminal=true` en la tabla estado), devolver `409 Conflict` con mensaje "Los incidentes cerrados son de solo lectura". Esto aplica tanto a edicion de campos como a cambio de estado.

En `DELETE` (si existe): bloquear completamente incidentes cerrados.

### Frontend — Nueva pagina `/dashboard`

Componentes ReCharts:
- `TendenciaChart`: grafico de lineas/barras con incidentes por dia o mes
- `SectorPieChart`: distribucion por sector (torta/donut)
- `EstadoBarChart`: barras apiladas por estado
- Filtros: toggle dia/mes, date range picker (dos inputs de fecha)
- Boton "Exportar" que guarda el grafico como PNG (html2canvas o recharts-to-png)

### Frontend — Actualizar vista de tickets

- En `TicketDetailDialog`: si el incidente esta cerrado, ocultar botones de edicion y mostrar badge "Solo lectura — Cerrado"
- En `TicketsTable`: los incidentes cerrados no muestran boton de editar/eliminar

### Frontend — Navegacion

Agregar link "Dashboard" en el Header, visible para usuarios autenticados.

### Base de datos

Sin cambios de schema. La conservacion indefinida ya es el comportamiento por defecto (nunca se implemento DELETE automatico).

## Archivos a crear/modificar

| Archivo | Accion |
|---|---|
| `Gestion_Incidentes/app/routes/estadisticas.py` | Nuevo: endpoints de tendencias y resumen |
| `Gestion_Incidentes/app/services/estadisticas_service.py` | Nuevo: queries de agregacion |
| `Gestion_Incidentes/app/schemas/estadisticas.py` | Nuevo: schemas de respuesta |
| `Gestion_Incidentes/app/routes/incidentes.py` | Modificar: bloqueo 409 en PATCH para cerrados |
| `Gestion_Incidentes/app/routes/__init__.py` | Modificar: registrar estadisticas_router |
| `Frontend/src/pages/Dashboard/index.tsx` | Nuevo: pagina principal del dashboard |
| `Frontend/src/pages/Dashboard/TendenciaChart.tsx` | Nuevo: grafico de tendencias |
| `Frontend/src/pages/Dashboard/SectorPieChart.tsx` | Nuevo: distribucion por sector |
| `Frontend/src/pages/Dashboard/EstadoBarChart.tsx` | Nuevo: barras por estado |
| `Frontend/src/pages/Dashboard/FiltrosDashboard.tsx` | Nuevo: controles de filtro |
| `Frontend/src/services/estadisticasService.ts` | Nuevo: llamadas a la API |
| `Frontend/src/hooks/useEstadisticas.ts` | Nuevo: React Query hook |
| `Frontend/package.json` | Agregar: recharts, html2canvas |
| `Frontend/src/components/layout/Header.tsx` | Modificar: link Dashboard |
| `Frontend/src/main.tsx` | Modificar: ruta /dashboard |
| `Frontend/src/pages/Administracion/TicketDetailDialog.tsx` | Modificar: solo lectura en cerrados |
| `Frontend/src/pages/Administracion/TicketsTable.tsx` | Modificar: ocultar acciones en cerrados |

## Dependencias npm a agregar

```json
"recharts": "^2.12.0",
"html2canvas": "^1.4.1"
```

## Gobernanza

MEDIUM — feature nueva, sin impacto en datos existentes. El bloqueo de escritura es un cambio de comportamiento en el endpoint PATCH.

## Dependencias

C-15 (JWT Auth) — el dashboard requiere autenticacion.

**NOTA C-24**: Los paths en este archivo referencian `Gestion_Incidentes/` y `Frontend/` (directorios antiguos). Antes de aplicar C-23, actualizar todas las referencias a `App/Backend/` y `App/Frontend/` respectivamente (ver C-24-restructure-app-directory).
