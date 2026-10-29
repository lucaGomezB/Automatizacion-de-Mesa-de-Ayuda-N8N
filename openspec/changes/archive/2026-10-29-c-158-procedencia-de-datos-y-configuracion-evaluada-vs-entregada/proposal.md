## Why

El dictamen CONEAU del 2026-10-28 sobre la tesis v10 / release `v1.2.5` (`auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`, veredicto puntos 1 y 2, recomendaciones A.1 y A.2) condiciona la aprobacion plena a dos omisiones de metodo verificadas contra el repositorio: (1) la tesis presenta como una sola "campana automatizada" tres corridas distintas, con configuraciones distintas del clasificador (tiempos de correo y formulario del 2-10-2026, tiempos de telefonia concluidos el 6-10-2026 y clasificacion fuera de linea `hybrid-v3` del 7-10-2026), sin describir el procedimiento de inyeccion ni el recalculo del tiempo telefonico del 19-10-2026 que muestra la Figura 10; y (2) describe la version entregada (`v1.2.5`) como si fuera la evaluada y, a la vez, declara las dependencias de la evaluada (commit `d6bb474`) como si fueran las entregadas. Ninguna de las dos exige nuevas mediciones: se resuelven declarando lo que el repositorio ya documenta y consultando a los autores lo que no consta.

## What Changes

- **A1 - Procedencia de los datos del brazo automatizado.** Nuevo apartado "Procedencia de los datos del brazo automatizado" en la Seccion 4.5 (`04-marco-metodologico.tex:61`) que declara: (a) la corrida de correo y formulario del 2-10-2026 (c-68, 119 casos: 66 y 53), inyectada por el arnes `scripts/corpus_ingest/ingest_via_n8n.py` (mensajes SMTP nuevos y envios al webhook, con la descripcion pseudonimizada), con el clasificador `hybrid-v1` (89 patrones, prompt sin reglas de frontera, cortocircuito por confianza >= 0,90) y la configuracion declarada del disparador IMAP (`everyMinute`); (b) la corrida telefonica concluida el 6-10-2026 (c-70, 81 casos), con llamadas desde el softphone de navegador en las que una persona recita la descripcion pseudonimizada, grabacion acotada a 45 s y entorno de medicion aislado, y sin configuracion unica asignable (25 casos ya medidos el 5-10 con el agente LLM de N8N; c-71 y c-72 contemporaneos; siempre anterior a c-74); (c) la corrida de clasificacion `hybrid-v3` del 7-10-2026 22:22 UTC como ejecucion fuera de linea del framework, con su archivo de evidencia y el hash del corpus; (d) el recalculo del 19-10-2026 (c-77) y su motivo. Lo que no consta se marca con comentarios `% PENDIENTE AUTORES` y se lista en el registro de correcciones; nunca se redacta como hecho.
- Recordatorio breve de esa procedencia al abrir la Seccion 8 (`07-resultados.tex`, tras el parrafo introductorio, sin alterar su enumeracion).
- Correcciones conexas: Seccion 1.8 (`01-introduccion.tex:76`, "desde el 24-09-2026" pasa a fechar el modelo y las corridas reales); Seccion 9.1 (`08-discusion.tex:10`, la reduccion de tiempo deja de apoyarse en el 65,5 % de cortocircuito de la configuracion posterior); Seccion 6.4 (`06-implementacion.tex:52`, el tiempo telefonico se describe como grabacion mas latencia hasta la persistencia); leyenda de la Figura 10 (`12-anexos.tex:21`, fuente del hito del 19-10 frente a la confirmacion del 9-10); Anexo F (`12-anexos.tex:66-68`: predicciones en `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, registros primarios "no versionados", linea fuera de margen corregida).
- **A2 - Configuracion evaluada frente a entregada.** Tabla nueva en el Anexo B (`tab:configuracion-evaluada-entregada`) con dos columnas verificadas con `git show` (commit `d6bb474` frente a tag `v1.2.5`): dependencias (FastAPI, Uvicorn, SQLAlchemy, google-genai, pytest, pytest-cov, React), flujo N8N, reintentos del alta (c-140), disparador de revision por directorio (c-82), prueba de humo E2E y verificacion de TLS (c-140), y la fila de lo que no cambia. Remisiones a la tabla desde 5.4, 6.1, 6.2, 6.3, 6.5, 6.7, 7.4 (Seguridad tecnica) y el Anexo H, de modo que ningun pasaje presente esas capacidades como rasgos de la version evaluada.
- Anexo B: se precisa "commit definitivo" (patron de dos commits: el tag identifica el commit de la release y un commit posterior consigna su hash).
- `Gomez2026_repositorio` (`Bibliography_base.bib:810-817`) pasa de "Version 1.2.2" / `urldate` 2026-10-26 a "Version 1.2.5" / 2026-10-28.
- Cierre: render, recompilacion con Docker, `verify_citations.py`, Anexo I (parrafo del dictamen del 28-10), registro de correcciones (seccion nueva con trazabilidad y consultas a los autores), memo de conteos tecnicos, cronograma fuente (anclas sin regenerar la figura) y `CHANGES.md`.
- Sin cambios de numeros canonicos, de los cinco identificadores de sector, de `App/`, de `openspec/config.yaml` ni de `docs/Tesis/v9 (IA)/`.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-document`: se agregan los requisitos de procedencia de los datos del brazo automatizado (4.5, 8, 1.8, 9.1, 6.4, Figura 10), de la tabla de configuracion evaluada frente a entregada con sus remisiones, de la precision del commit de referencia del Anexo B y de la trazabilidad de A1 y A2 con las consultas a los autores; se modifican "Trazabilidad del corpus real en el anexo de validacion" (las predicciones pasan a la evidencia versionada y se declaran los registros primarios) y "Coherencia de la version bibliografica con la release publicada" (de `v1.2.2` a la release que consigna el Anexo B, `v1.2.5`, con su `urldate`).

## Impact

- **Fuentes de la tesis (v10)**: `docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex`, `04-marco-metodologico.tex`, `05-arquitectura.tex`, `06-implementacion.tex`, `07-resultados.tex`, `08-discusion.tex`, `11-aspectos-legales.tex`, `12-anexos.tex`; `docs/Tesis/v10 (IA)/Bibliography_base.bib`.
- **Derivados**: `docs/Tesis/v10 (IA)/tesis_para_agente.md`, `docs/Tesis/v10 (IA)/paper/main.pdf` y artefactos de compilacion.
- **Registros**: `docs/Tesis/Correcciones/dictamen-correcciones.md`, `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`, `docs/diagrams/cronograma.md` (solo tablas de texto; el bloque Mermaid y `cronograma.png` no cambian), `CHANGES.md`.
- **Paginas**: prevision +1 a +2 sobre las 106 actuales (cuerpo +0 a +1), con compensaciones de forma; se registra en el libro mayor.
- **Coordinacion**: c-159 (A3 y A4) se aplica despues y usa la etiqueta `tab:configuracion-evaluada-entregada` desde las leyendas de las Figuras 1 y 4. Las observaciones B5-B13 quedan para un change posterior.
- **Gobernanza**: MEDIO (declaracion metodologica en el nucleo del diseno; requiere confirmacion de los autores para cerrar los marcadores pendientes). Sin impacto en API, datos, dependencias ni runtime.
