# Proposal: Atender el dictamen CONEAU sobre v1.2.10 (observaciones de fondo A1-A5)

## Why

El dictamen CONEAU del 2026-11-08 sobre la release `v1.2.10`
(`auditorias/Dictamen_Tesis_v10_v1.2.10_CONEAU_2026-11-08.md`) aprueba con observaciones:
la lectura cruzada del texto con los artefactos de la campaña complementaria muestra que
dos de sus resultados centrales no significan lo que la tesis dice (la tasa de
intervención del 73,5 % y el "efecto de condición"), que la fiabilidad de la referencia
de verdad quedó cuestionada por la propia campaña (kappa 0,5569) sin discusión, que la
independencia de los analistas originales está mal declarada, que la exactitud agregada
del brazo manual está mal rotulada (125/151 derivaciones, no 125/138 casos) y que la
trazabilidad de la versión entregada tiene tres defectos (hash del PDF del tag, imagen
derivada de N8N no declarada, portada anterior a los datos). Ninguna observación exige
mediciones nuevas: todas se cierran escribiendo lo que los artefactos del repositorio
muestran, y son condición para la defensa (recomendaciones A).

## What Changes

- **A1 — Mecanismo de derivación e hipótesis 2**: verificar en el backend y en la
  documentación de despliegue de la campaña qué condición activó
  `requiere_revision_humana` en los 147 casos (hipótesis del dictamen: la regla del
  reportante no identificado, c-82; patrón 66/66 correo, 81/81 telefonía, 0/53 web);
  reescribir 8.3 (`07-resultados.tex`, párrafos del gate y de la sub-hipótesis 2)
  distinguiendo **derivación por confianza** (0 casos) de **derivación por reportante**
  (147 casos, por canal); reformular el estado de la sub-hipótesis 2: la tasa bruta
  (147/200) no es compatible con la cota de 0,15 pero mide la configuración de la
  prueba, y la medida pertinente (intervenciones que cambian la derivación, 25/200 =
  12,5 %, IC de Wilson [8,6 %; 17,8 %]) es **no concluyente** según la regla de tres
  vías declarada; propagar a 1.4 (`01-introduccion.tex`), resumen y abstract, 9.1
  (`08-discusion.tex:8`), Tabla 18 (filas del objetivo general y del OE4,
  `09-conclusiones.tex`) y 11.3 (`10-recomendaciones.tex`); completar la columna de la
  campaña de la Tabla 19 y corregir la celda "la misma configuración evaluada";
  desambiguar en el resumen el paréntesis que coincide con la exactitud (147/200).
- **A2 — Orden ejecutado**: describir en 4.2, 4.5 y 4.6 (`04-marco-metodologico.tex`)
  que el brazo manual precedió al automatizado en los 200 casos (manual 5-11 09:20-18:49
  −03; automatizado 5-11 23:47 UTC a 6-11 22:45 UTC) y que los grupos `brazo_primero`
  se intercalaron en una misma ventana; retirar en 8.7 el efecto de condición como
  evidencia sobre el orden; conservar el efecto de posición (Spearman, significativo
  para `O2`); mantener el efecto de orden como amenaza no resuelta en 4.7 y 9.1.
- **A3 — Referencia de verdad y analistas**: llevar al resumen y abstract ambos kappa con
  su naturaleza (0,87 sin intervalo y sin tabla conservada; 0,5569 [0,4725; 0,6413] con
  tabla conservada) y la concordancia del consenso nuevo con la referencia original
  (116/138, 84,1 %); agregar en 9.4 una limitación sobre la fiabilidad de la referencia;
  matizar la segunda contribución de 10.2 (`09-conclusiones.tex:51`); corregir en 4.4
  (`04-marco-metodologico.tex`, "ajenos al equipo de autores") que uno de los dos
  analistas originales (`T1`) es autor y operó el brazo manual de 2026-10, y llevarlo a
  4.7 y 9.4.
- **A4 — Denominador del brazo manual**: escribir 0,8278 como 125 de 151 derivaciones
  (80 de `O1` y 71 de `O2`) sobre 138 casos únicos y 0,8609 como 130 de 151; expresar
  la comparación con el brazo automatizado (110 de 138 casos) en la misma unidad o
  declarar la diferencia de unidad; corregir el memo (`numeros-canonicos.md`, fila de la
  agregada). `e_man` = 0,1722 y los `a*` de 9.6 se conservan porque la definición por
  derivación no cambia (solo su rótulo).
- **A5 — Trazabilidad de la versión entregada**: documentar en el Anexo B el patrón de
  release de dos commits y el procedimiento para verificar el hash del tag (opción
  recomendada en `design.md`, **decisión del usuario**); declarar la imagen derivada de
  N8N (`docker/n8n/Dockerfile`, `FROM n8nio/n8n:2.11.2` + parche IMAP, c-182) en la
  Tabla 19 y en 6.1 (`06-implementacion.tex`); fechar la portada en la fecha de la
  release (`00-portada.tex`).
- **B1, B2, B3 y B6** (tocan los mismos párrafos): declarar que la exactitud automatizada
  de la campaña (110/138) se calcula sobre la caché in-sample del 7-10 y no sobre la
  salida en vivo (difiere en 13 casos); corregir "2 y el 6 de octubre", el "65,5 %"
  fuera de lugar de 8.3, el denominador de la proporción de tiempo (191 casos) y el
  "únicamente" de 8.7; unificar el rótulo "campaña de medición" (Figuras 3 y 4, Tabla 5,
  Anexo B) en "campaña 2026-10" / "campaña complementaria"; llevar el kappa moderado y
  el efecto de posición al capítulo 10 y al resumen, agregar "dentro de la muestra" en
  10.2, dejar "5.000 casos" una sola vez y calificar la "cota pesimista" de 9.4.
- **Registro y Anexo I**: registrar el dictamen en `dictamen-correcciones.md`, agregar una
  tercera tabla de trazabilidad (dictamen del 8-11-2026) en el Anexo I y actualizar la
  frase "cinco dictámenes … entre el 20 y el 28 de octubre" a seis, hasta el 8-11.
- **Release**: recompilar, tag `v1.2.11` y commit del hash (tareas finales, a ejecutar
  por el orquestador).

## Out of Scope

- **B4** (definición de las métricas multietiqueta secundarias y "ejemplos balanceados"),
  **B5** (capturas de 6.8, frontend del diagrama de despliegue, matriz duplicada) y **B7**
  (versionar el registro de compilación y `verificar_matriz_trazabilidad.py`), y las
  recomendaciones **C1 a C5** (bibliografía, glosario y forma): quedan para un change
  posterior. Este change no edita esos párrafos salvo que una reescritura de A1-A5 los
  toque de forma incidental.
- Nuevas mediciones de campo, nuevas corridas del clasificador, cambios de valores
  canónicos (salvo el rótulo del denominador de A4), cambios de código en `App/`, `n8n/`
  o `evaluation/`. Si el usuario elige cambiar el patrón de release en A5, ese cambio se
  limita al procedimiento de release y se decide antes del apply.
- Cerrar la validación fuera de muestra (sigue declarada como negativo).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: se modifican cinco requisitos (tabla de configuración evaluada,
  entregada y de la campaña; exactitud del brazo manual de la campaña; tasa de
  intervención de la campaña; efecto de orden de la campaña; declaración de los
  analistas etiquetadores) y se agregan requisitos para el mecanismo de derivación y la
  sub-hipótesis 2, la fiabilidad de la referencia de verdad, la trazabilidad de la versión
  entregada (hash del tag, imagen derivada de N8N, portada), la consistencia interna de
  los párrafos tocados (B2, B3, B6), la trazabilidad del dictamen del 8-11 en el Anexo I y
  la neutralidad de páginas y palabras.
- `tesis-numeros-canonicos`: se agrega un requisito sobre la unidad del denominador de la
  exactitud agregada del brazo manual.

## Impact

- `docs/Tesis/v10 (IA)/paper/sections/{00-portada,00-resumen,01-introduccion,04-marco-metodologico,05-arquitectura,06-implementacion,07-resultados,08-discusion,09-conclusiones,10-recomendaciones,12-anexos}.tex`;
  `docs/Tesis/Correcciones/{numeros-canonicos,dictamen-correcciones}.md`; leyendas de las
  Figuras 3 y 4 (en `.tex`; `docs/diagrams/*.md` solo si cambia un rótulo dentro de la
  imagen); recompilación del PDF.
- Lectura (sin edición) de `App/Backend/app/services/incidente_service.py`, de las rutas
  que resuelven el reportante por canal, de `evaluation/data/campana/` y de
  `docs/campana-medicion/` para la verificación de A1.
- Gobernanza: LOW (documentación). A5 es MEDIUM solo si se elige cambiar el patrón de
  release. Tope de páginas: el change no debe agregar páginas netas (hoy 118); el resumen
  y el abstract deben respetar sus topes de 250 palabras.
