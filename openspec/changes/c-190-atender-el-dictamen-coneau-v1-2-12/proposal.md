# Proposal: Atender el dictamen CONEAU sobre v1.2.12 (A1-A3, B1-B4, C1-C2 e inventario)

## Why

El dictamen CONEAU del 2026-11-09 sobre la release `v1.2.12`
(`auditorias/Dictamen_Tesis_v10_v1.2.12_CONEAU_2026-11-09.md`, tag sobre `7937efd`)
aprueba con observaciones y califica el documento escrito con 8,83. Las tres observaciones
de fondo tienen un origen común: una corrección bien hecha en c-187/c-188 que no se propagó
a todas sus consecuencias. El estado "no concluyente" de la segunda sub-hipótesis depende de
contar como "sin acción manual" a los 53 casos web que nadie revisó (sobre los 147 revisados,
25/147 = 17,0 %, IC [11,8 %; 23,9 %], que con la regla de tres vías declarada la refuta); la
sección 4.2 declara un enmascaramiento de los operadores que es imposible si uno de ellos es
autor (como dicen 4.4, 4.8 y 9.3); y la nota al pie de la Tabla 19 afirma que entre `cda7712`
y `v1.2.12` "solo `docker-compose.yml` difiere", cuando `git diff --stat` muestra 24 archivos
(ninguno de los pines). Ninguna observación exige mediciones nuevas: todas se cierran
escribiendo lo que los artefactos muestran. Las A son condición para la defensa; las B y C,
junto con el inventario de 30 correcciones puntuales, cierran el resto del dictamen en el
mismo change para que la release `v1.2.13` no deje residuos.

## What Changes

- **A1 — Sub-hipótesis 2 según el denominador de los casos revisables** (resumen y
  abstract, 1.4, 4.7, 8.3, 9.1, 10 párrafo inicial, Tabla 18 filas del objetivo general y
  del OE4, síntesis del OE4, 11.3; inventario 1 y 2): declarar que la revisión humana de la
  campaña complementaria alcanzó solo correo y telefonía por la regla del reportante y que
  los 53 casos web no tuvieron revisión; adoptar una lectura única (decisión de los autores,
  design D1) y sostenerla en todo el documento; informar en 8.3, como dato y sin lectura
  causal, el cotejo con el consenso nuevo: 11 de las 85 confirmaciones con consenso
  confirmaron un sector incorrecto, y de los 25 cambios 13 tienen consenso (9 correcciones,
  1 empeoramiento, 3 de error a error).
- **A2 — Enmascaramiento de los operadores** (4.2, 4.8, 7.5, 9.1; inventario 3 y 4):
  reconciliar la protección contra el efecto Hawthorne con la condición de autor de `T1`
  (decisión de los autores tras verificar `registro_sujetos.csv`, design D2).
- **A3 — Nota de la Tabla 19** (`12-anexos.tex:78`; inventario 5): reemplazar "solo
  `docker-compose.yml` difiere" por la afirmación verificable (no cambian
  `requirements.txt`, `package-lock.json`, `n8n/workflow.json` ni `settings.py`; sí cambian
  `docker-compose.yml`, `docker/n8n/`, el control de costo y TwiML del backend, pruebas y
  frontend que no intervienen en la clasificación).
- **B1 — Canal telefónico** (5.2, 6.4, 6.6 etapa 4, Tabla 19, Anexo H, 9.5, Figura de
  despliegue; inventario 6-9): una sola descripción (Twilio graba y notifica; el backend
  transcribe con la Gemini API); declarar `gemini-3.5-transcribe` y su exclusión del costo;
  transcripción en el diagrama de despliegue y leyenda con las cuatro redes.
- **B2 — Procedencia de cifras de la campaña** (8.3, 8.7; inventario 10-12): denominador
  de la proporción de tiempo (tiempos de `corpus_campana.json`), origen de la salida en vivo
  telefónica (`sector_predicho` del export), predicción que usa el McNemar, definición del
  conjunto laxo del brazo manual (consenso + unión de adicionales de E1 y E2) y MDE del
  Spearman (0,2834 frente a 0,264 con la fórmula del código).
- **B3 — Rótulos y matiz** (4.5, 2.4, 5.5, 6.3, 7.5, `componentes.png`, `secuencia.png`;
  inventario 13-15): "posterior a la campaña 2026-10" en texto y dentro de los PNG
  regenerados; matizar el "clasificador congelado … métricas comparables" de 4.5.
- **B4 — Formulaciones** (1.6, resumen y abstract, Tabla 18; inventario 16-18): retirar
  "validación rigurosa … doble etiquetado independiente"; "respaldan" por "confirman";
  "reintentos idempotentes de la configuración entregada".
- **C1 — Forma** (inventario 19-25): "ocho limitaciones" en 9.3; anacoluto de 8.3; celda
  repetida del OE4; glosario (TI, URL, E2E, MDE, VIS, HS256, CA, y NB, LR, DT de la Tabla 1);
  portada con la fecha de la release; retirar `matriz_confusion.pdf`; Anexo B que nombre el
  resumen de compilación y el verificador que la Tabla 23 le atribuye; consentimiento de E1,
  E2, O1 y O2 en 7; presupuesto de páginas (118 frente al tope de 100) re-declarado.
- **C2 — Bibliografía** (inventario 26-30): Zanzotto (reformular o paginar), Xiong
  (atenuar), punto único de contacto con ITIL y no con Galup, precios de la Gemini API en
  lugar de Vertex AI y nivel de servicio (gratuito o pago) declarado en 7 con su consecuencia
  sobre los datos; URL de Zendesk, Vertex y Decreto 1558/2001; Ramya en IEEE CSITSS 2018;
  localizador de Kerby; edición de Efron y Tibshirani; FrugalGPT en TMLR.
- **Residuos sin recomendación propia**: requisitos nuevos de 11.3 (revisión de todos los
  canales y cotejo con referencia independiente), redondeo del balance laxo máximo
  (+138,0/+138,1), ausencia de repositorios regionales en el protocolo de revisión, ISBN de
  los libros.
- **Registro, Anexo I y release**: sección c-190 en `dictamen-correcciones.md` con matriz de
  7 columnas y verificador en 0 fallas; cuarta tabla de trazabilidad en el Anexo I; versionar
  el dictamen en el commit de contenido; tag `v1.2.13` y commit del hash (patrón D7-A de
  c-187).

## Out of Scope

- Nuevas mediciones, corridas del clasificador, revisión de los 53 casos web o re-análisis
  de la campaña. Los únicos cálculos admitidos son aritmética sobre conteos y artefactos ya
  publicados (intervalos de Wilson, cruces de `intervenciones.csv` con
  `doble_etiquetado.csv`, recómputo del MDE con la fórmula del código).
- Cambios en `App/`, `n8n/`, `evaluation/` (código o artefactos) y en valores canónicos
  existentes, salvo los que el design declara (MDE) con su fuente.
- Búsquedas nuevas en SciELO, Redalyc o JAIIO (el residuo se declara, design D9).
- Validación fuera de muestra (sigue declarada como negativo).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: se modifica el requisito del estado de la segunda sub-hipótesis (deja de
  fijar "no concluyente" con 25/200) y se agregan requisitos para el cotejo de las revisiones
  con el consenso, el enmascaramiento de los operadores, la nota de la Tabla 19, la
  descripción única del canal telefónico y del modelo de transcripción, la procedencia de las
  cifras de la campaña, los rótulos temporales, las formulaciones de 1.6/resumen/Tabla 18, la
  forma del documento, la fidelidad bibliográfica y el nivel de la Gemini API, la línea futura
  de 11.3, la trazabilidad del dictamen del 9-11 y la neutralidad de páginas y palabras.

## Impact

- `docs/Tesis/v10 (IA)/paper/sections/{00-portada,00-resumen,00-glosario,01-introduccion,02-marco-teorico,04-marco-metodologico,05-arquitectura,06-implementacion,07-resultados,08-discusion,09-conclusiones,10-recomendaciones,11-aspectos-legales,12-anexos}.tex`;
  `docs/Tesis/v10 (IA)/Bibliography_base.bib`; `paper/figures/{componentes,secuencia,despliegue}.png`
  regenerados desde `docs/diagrams/*.md`; retiro de `paper/figures/matriz_confusion.pdf`.
- `docs/Tesis/Correcciones/{dictamen-correcciones,numeros-canonicos,conteos-canonicos-tecnicos}.md`;
  `docs/Tesis/v10 (IA)/paper/compilacion.md` y `tesis_para_agente.md` regenerados.
- Versionado de `auditorias/Dictamen_Tesis_v10_v1.2.12_CONEAU_2026-11-09.md`.
- Lectura sin edición de `evaluation/data/campana/` (`intervenciones.csv`,
  `doble_etiquetado.csv`, `registro_sujetos.csv`, README), `evaluation/campana.py`,
  `analisis/resultados.json` y `App/Backend/app/config/settings.py` del tag.
- Gobernanza: MEDIUM (cambios documentales de la tesis que tocan el veredicto de una
  sub-hipótesis y la descripción ética del procedimiento). Las decisiones D1, D2, D4 y D7 del
  design son de los autores y se resuelven antes de los grupos correspondientes.
