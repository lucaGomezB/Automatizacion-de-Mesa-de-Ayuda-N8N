# Tasks — c-109 — Coherencia de conteos tecnicos

> Governance MEDIO. Fase de propose: NO se edita ningun `.tex`. La alineacion se
> ejecuta en apply. Las decisiones y su reversibilidad estan en `design.md`.

## 0. Prerrequisitos (fijar el conteo desde el sistema, solo lectura)

- [ ] 0.1 Contar las entidades principales del modelo de datos: leer la Tabla
  `tab:entidades` (`05-arquitectura.tex:90-110`) y `App/Backend/app/models/`.
  Registrar el valor canonico (siete) y la lista de las siete.
- [ ] 0.2 Contar los nodos de `n8n/workflow.json` por tipo
  (`python3 -c` sobre `nodes`): registrar total (32), `stickyNote` (3) y
  operativos (29).
- [ ] 0.3 Fijar el numero de etapas funcionales del flujo (siete) a partir de la
  agrupacion del Anexo (`12-anexos.tex:45`) y las conexiones del export.
- [ ] 0.4 Confirmar el paquete del SDK en `App/Backend/requirements.txt`
  (`google-genai>=2.20.0,<3`) y registrar que `google-generativeai` es deprecado.
- [ ] 0.5 Registrar el conteo canonico en `docs/Tesis/Correcciones/` (memo, D5).
- [ ] 0.6 Registrar el conteo de paginas de partida (`main.pdf` = 103) y la fecha
  de verificacion; confirmar con `git status` que el arbol esta limpio.

## 1. Entidades: unificar a siete (D1)

- [ ] 1.1 `06-implementacion.tex:72`: eliminar "con sus seis entidades"; describir
  el entregable de la iteracion sin un conteo stale del modelo final.
- [ ] 1.2 Confirmar que `05:88`, `05:117` y `12:25,29` mantienen "siete entidades"
  (INTOCABLES).
- [ ] 1.3 Buscar `seis entidades` en `sections/*.tex` y confirmar cero ocurrencias.

## 2. Etapas del flujo: unificar a siete (D2)

- [ ] 2.1 `06:32`: reemplazar "organizados en cinco etapas logicas" por
  "organizados en siete etapas funcionales" (o rotular las cinco como patron por
  canal, sin presentarlas como el total).
- [ ] 2.2 `06:34`: alinear el encabezado del enumerado a siete etapas funcionales
  o rotular el patron por canal.
- [ ] 2.3 `06:73`: rotular "cinco etapas" como patron por canal, no como total.
- [ ] 2.4 Confirmar que `12:45` mantiene "siete etapas" (ya canonico).
- [ ] 2.5 Verificar que NO se tocan las etapas del pipeline de clasificacion
  (`05:78` "dos etapas", `05:82` "tres etapas").

## 3. Nodos del flujo: 29 operativos + 3 notas = 32 (D3)

- [ ] 3.1 `06:32`: reemplazar "29 nodos (26 operativos mas 3 notas adhesivas)" por
  "32 nodos (29 operativos mas 3 notas adhesivas)".
- [ ] 3.2 `12:45`: explicitar que los 29 nodos operativos mas 3 notas suman 32
  totales.
- [ ] 3.3 Buscar `26 operativos` en `sections/*.tex` y confirmar cero ocurrencias.

## 4. SDK de Google: unificar a `google-genai` (D4)

- [ ] 4.1 `12:88`: reemplazar la API `google-generativeai` 0.8 por el SDK
  `google-genai` (`>=2.20.0`).
- [ ] 4.2 `12:105`: reemplazar la fila "API & `google-generativeai` 0.8" por
  "SDK & `google-genai` `>=2.20.0`".
- [ ] 4.3 `12:108`: alinear la linea de fuente al SDK `google-genai`.
- [ ] 4.4 `05:74` y `06:10`: alinear la version declarada ">=2.0" a ">=2.20.0".
- [ ] 4.5 Buscar `google-generativeai` en `sections/*.tex` y confirmar cero
  ocurrencias como SDK usado.

## 5. Verificacion de coherencia

- [ ] 5.1 Buscar en `sections/*.tex`: `seis entidades`, `cinco etapas`,
  `26 operativos`, `google-generativeai`; confirmar que no quedan como vigentes.
- [ ] 5.2 Confirmar que `05-arquitectura.tex` mantiene "siete entidades" y
  `12-anexos.tex` mantiene "siete etapas".
- [ ] 5.3 Confirmar que ningun archivo fuera de `docs/Tesis/v9 (IA)/paper/` fue
  tocado, salvo el memo de conteos de `docs/Tesis/Correcciones/`.

## 6. Compilacion y presupuesto de paginas

- [ ] 6.1 Compilar con la imagen local:
  `docker run --rm -v "<repo>/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`.
- [ ] 6.2 Confirmar cero errores fatales y registrar el conteo de paginas. El plan
  exige <= 100; c-109 parte de 103 y MUST NOT aumentar el conteo.
- [ ] 6.3 Verificar que no quedan referencias indefinidas nuevas ni etiquetas rotas.

## 7. Verificacion del change (OpenSpec)

- [ ] 7.1 Ejecutar `openspec validate c-109-coherencia-de-conteos-tecnicos --strict`.
- [ ] 7.2 Ejecutar `openspec status --change c-109-coherencia-de-conteos-tecnicos --json`
  y confirmar `isPlanningComplete: true`.
- [ ] 7.3 Confirmar que NO se edito `n8n/workflow.json`, `requirements.txt`,
  `CHANGES.md` ni `Bibliography_base.bib`.
