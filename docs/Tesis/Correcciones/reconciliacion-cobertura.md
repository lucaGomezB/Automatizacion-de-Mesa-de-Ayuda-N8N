# Reconciliacion de cobertura — nueva auditoria vs changes C-76..C-80

> Herramienta de trabajo. Cruza los hallazgos de la re-auditoria
> `docs/Tesis/Correcciones/auditoria-capitulos.md` (105 hallazgos, commit `d7df92c`)
> contra los cinco changes ACTIVOS que cubren el dictamen CONEAU original
> (`C-76`..`C-80`, todos 0 tareas, sin aplicar).
>
> Objetivo: determinar que hallazgos ya estan cubiertos, cuales quedan parcialmente
> cubiertos y cuales son NUEVOS (no cubiertos por ningun change), para decidir si se
> amplian los changes existentes o se abren changes nuevos.
>
> Metodo: inventario de cada change (proposal + design + tasks + specs) y de la
> auditoria, cruzados por tema/archivo/seccion. Estado: 2026-10-19.

---

## 1. Veredicto de sintesis

Los cinco changes existentes fueron construidos sobre el **plan de auditoria del
dictamen** (32 items, 4 bloques) y sobre el **registro `dictamen-correcciones.md`**.
La nueva auditoria **reutiliza el mismo sistema de codigos criticos** (`C-01`..
`C-28`) para los hallazgos ya documentados, y agrega un cuerpo nuevo de hallazgos
`A` (altos), `M` (medios) y `B` (bajos) por capitulo.

Resultado del cruce sobre los hallazgos enumerados (48 A/M/B + los C nombrados):

| Clasificacion | Cantidad | Significado |
|---|---|---|
| CUBIERTO | ~24 A/M/B + 25 C | Existe tarea concreta en algun change que resuelve el hallazgo |
| PARCIAL | ~20 A/M/B + 3 C | El change toca el tema pero no aborda el hallazgo puntual |
| NUEVO | ~22 A/M/B | Ningun change lo cubre |

Tras revisar el informe completo (55 paginas), el **nucleo critico queda cerrado**: los
**28 criticos C-01..C-28 tienen owner** (25 CUBIERTO, 3 PARCIAL). Lo que sigue faltando
es el cuerpo de hallazgos **A/M/B** de la re-auditoria.

Conclusion: **C-76..C-80 cubren bien el nucleo probatorio/estadistico/bibliografico/
legal/formal del dictamen, pero NO cubren un conjunto significativo de hallazgos
nuevos de la re-auditoria**, concentrados en:

- **Capitulo 2 (Marco Teorico)**: profundidad del eje de LLM, formula de exactitud, Whisper, PostgreSQL.
- **Capitulo 4 (Metodologia)**: formula del tamaño muestral, informe de cobertura, potencia estadistica, criterios de exclusion, ubicacion de Scrumban, analistas del corpus.
- **Capitulo 6 (Implementacion)**: pruebas e2e de N8N inexistentes, recuento de la suite frontend, afirmacion Kubernetes.
- **Capitulo 5**: parametros de inferencia sin procedimiento, Tabla 5 incompleta.
- **Capitulos 7/8**: baseline TF-IDF+SVM sin procedimiento, ausencia de hipotesis alternativas, ejemplos textuales de errores, costos sin fuente, Shapiro-Wilk.
- **Citas/Tablas**: Tabla 1 sin fuentes (A-26), citas huerfanas nuevas (SEPyME, APA 2017), n8n como "codigo abierto" (A-27).

Ademas se detectaron **conflictos internos entre changes** (seccion 5) que hay que
resolver antes de aplicar.

---

## 2. Matriz de cobertura hallazgo -> change

### Hallazgos ALTOS (A-01..A-27)

| Codigo | Hallazgo (resumen) | Change / tarea | Estado |
|---|---|---|---|
| A-01 | §1.2 proyecta 3.700 desde 42/dia; la aritmetica no cierra (C-13) | c-77 A7.1 (`3.700 = 42x88`; dias del trimestre) | CUBIERTO |
| A-02 | §1.2 (200 h) y §8.1 (180 h) no derivables de los insumos | c-77 A4 (footnote, real ~48,1 h; 01:18; 08:14; 09:24) | CUBIERTO |
| A-03 | §1.6 tercer criterio del umbral 85 % confunde test de tiempos con exactitud; no hay "zona de rechazo" | c-77 B1 solo reformula H1 | PARCIAL |
| A-04 | §2.4 (eje LLM) en cuatro parrafos; sin prompting/calibracion/alucinacion/idioma/evaluacion LLM | — | NUEVO |
| A-05 | §2.7 define exactitud con formula binaria y la corrige al lado | — | NUEVO |
| A-06 | §2.2 atribuye ITIL Service Operation (2011) a la OGC; corresponde a TSO/Cabinet Office | c-78 B3 (3.6) toca el `.bib`, no el cuerpo §2.2 | PARCIAL |
| A-07 | §4.4 declara 95 %/6,5 % con correccion por finitud sin publicar calculo; N=3.700 da 219, no 200 | — | NUEVO |
| A-08 | §4.5 (">80 %") y §6.7 (87 %) de cobertura sin informe ni comando | — | NUEVO |
| A-09 | Sin analisis de potencia a priori | — | NUEVO |
| A-10 | §4.2 rotacion de operadores no separable del efecto de operador | c-76 T6/T7 (ventana/instrumento) no aborda el confound | PARCIAL |
| A-11 | §6.7 declara pruebas e2e que validan N8N; no existen | — | NUEVO |
| A-12 | §6.7 declara 89 pruebas frontend / 98,6 %; el repo cuenta 68 | — | NUEVO |
| A-13 | §6.4 latencia telefonica 12-15 s no atribuible (C-17); sin n/dispersion | c-77 Grupo E (tiempo telefonico) no aborda §6.4 | PARCIAL |
| A-14 | §7.1 y Tabla 6 repiten 89,0 % en media y mediana | c-76 2.1 (reemplaza por 75,9 % real) | CUBIERTO |
| A-15 | Sin estadistico ni p de Shapiro-Wilk (§4.7) | — | NUEVO |
| A-16 | Sin tiempos desagregados por canal | c-77 E5.1 (tabla por canal) + c-80 F2 (boxplot por canal) | CUBIERTO |
| A-17 | Figura 1 a mano alzada; no representa las 5 capas ni nombra componentes | c-80 F2 (6.1, 6.9) | CUBIERTO |
| A-18 | Tabla 3 con nota interna "N8N 1.62 no en Docker Hub" | c-80 F6 (2.1, 2.2) | CUBIERTO |
| A-19 | §5.6 "seis entidades" vs Anexo C "cinco tablas" | No reproduce (STALE): el `.tex` dice "siete" en cuerpo y anexo desde `8466cbe`; coincide con el modelo real (7 principales) | CUBIERTO (stale) |
| A-20 | §8.1 interpreta y no interroga; sin hipotesis alternativa | c-80 F7 baja valorativos, no agrega hipotesis rival | PARCIAL |
| A-21 | §8.3 baseline TF-IDF+SVM (78 %, F1 0,764) en una sola oracion, sin procedimiento ni codigo | — | NUEVO |
| A-22 | §8.1 "garantia metodologica" justo lo que el repo no permite verificar (C-01) | c-80 F7 (5.5) | CUBIERTO |
| A-23 | §9.2 generaliza superioridad de LLM sobre clasificadores supervisados (C-24) | c-78 B1 (tension) + c-80 F7 (parcial) | PARCIAL |
| A-24 | §9.1 repite TLS 1.3 como logro (C-20) | c-77 C5 (09:10) | CUBIERTO |
| A-25 | §9.1 introduce interpretacion estadistica nueva (Wilcoxon) en conclusiones | c-77 A1 (quita W=0) + c-80 F7 (parcial) | PARCIAL |
| A-26 | Tabla 1 (Cap 3) compara seis comerciales sin una sola cita ni fecha de consulta; fila "Propuesta" autoevaluada | — | NUEVO |
| A-27 | §1.7 y §6.1 incluyen n8n en "codigo abierto" (sin matiz de licencia) | — | NUEVO |

### Hallazgos MEDIOS (M-01..M-18)

| Codigo | Hallazgo (resumen) | Change / tarea | Estado |
|---|---|---|---|
| M-01 | §1.1 cita huerfana: SEPyME define "empresa mediana" | — | NUEVO |
| M-02 | §1.7 afirma uso de corpus EN/DE/PT sin referencia (premisa de la contribucion) | c-78 B2 agrega refs multilingues, no el §1.7 | PARCIAL |
| M-03 | §2.5 Whisper detallado sin correlato en el artefacto (usa Twilio) | — | NUEVO |
| M-04 | §2.6 justifica PostgreSQL sin considerar alternativas concretas | — | NUEVO |
| M-05 | Sin criterios de exclusion de incidentes del corpus | — | NUEVO |
| M-06 | §4.9 Scrumban es gestion de proyecto, no metodologia | — | NUEVO |
| M-07 | No se declaran los dos analistas etiquetadores del corpus | — | NUEVO |
| M-08 | §6.8 ejemplo hipotetico presentado como "caso concreto"; sin captura | c-80 F2 (6.6) captura; el texto no | PARCIAL |
| M-09 | §6.1 "migracion a Kubernetes 1.30" sin manifiesto | — | NUEVO |
| M-10 | §7.4 tipifica 16 errores sin un solo ejemplo textual | — | NUEVO |
| M-11 | Cap 7 sin figuras (boxplot, heatmap, curva de calibracion) | c-80 F2 (boxplot, matriz) + c-77 A6 (calibracion) | PARCIAL |
| M-12 | §5.4 parametros de inferencia "optimizados" sin procedimiento | — | NUEVO |
| M-13 | Tabla 5 (3 puntos de entrada) incompleta vs API real | — | NUEVO |
| M-14 | Sin captura del frontend ni del panel de administracion | c-80 F2 (6.5, 6.6) | CUBIERTO |
| M-15 | §8.2 compara solo con trabajos 2019/2020 | c-78 B2 (refs 2023-2026) | CUBIERTO |
| M-16 | §8.4 costos (50-100 USD/mes; 0,02 USD/invocacion) sin fuente | — | NUEVO |
| M-17 | §9.1/§9.2 repiten literalmente las cifras del Cap 7 | c-80 F5 + F7 (parcial) | PARCIAL |
| M-18 | "seis de cada diez" sobre el 62 % no respaldado (C-03) | c-76 T4 (10.3) | CUBIERTO |

### Hallazgos BAJOS (B-01..B-03)

| Codigo | Hallazgo (resumen) | Change / tarea | Estado |
|---|---|---|---|
| B-01 | §1.2/§1.8 alterna "organizacion mediana" y "unica organizacion" sin nombrarla | — | NUEVO |
| B-02 | Jurafsky y Martin (2023) citado como Pearson | c-78 B3 (3.7) | CUBIERTO |
| B-03 | §9.2 registro valorativo ("hallazgo mas valioso") | c-80 F7 (5.6) | PARCIAL |

### Hallazgos CRITICOS (C-01..C-28)

Verificados contra el informe completo `auditorias/Auditoria_Tesis_Gomez_Bustos_Sevilla_040802026.pdf`
(55 paginas, seccion 4 "Hallazgos criticos", 28 criticos en 5 bloques). Los 28 criticos
estan mapeados a C-76..C-80:

| Codigo | Hallazgo (informe completo) | Change / tarea | Estado |
|---|---|---|---|
| C-01 | El repo declara la campana experimental como trabajo futuro; corpus sintetico | c-76 A1/P1/T1 | CUBIERTO |
| C-02 | La unica corrida documentada arroja 63,0 % (no 92 %); F1 0,5936 | c-76 2.3/2.4 (numeros reales) | CUBIERTO |
| C-03 | Distribucion de etapas del pipeline no coincide; etapa fallback no documentada | c-76 T4 | CUBIERTO |
| C-04 | No existe ningun dato de tiempo en el repositorio | c-76 T5/P1 | CUBIERTO |
| C-05 | La medicion anti-Hawthorne es incompatible con la ventana temporal | c-76 T6 | CUBIERTO |
| C-06 | Tres relatos incompatibles del instrumento de medicion manual | c-76 T7 | CUBIERTO |
| C-07 | El estadistico W=0 es incompatible con la definicion usada (SciPy) | c-77 A1 | CUBIERTO |
| C-08 | La formula del tamaño del efecto es incorrecta y su rango declarado falso | c-77 A2 | CUBIERTO |
| C-09 | "Varianza casi diez veces menor" describe el desvio, no la varianza | c-77 A3 | CUBIERTO |
| C-10 | Proyeccion de "180 horas-persona liberadas" aritmeticamente imposible | c-77 A4 | CUBIERTO |
| C-11 | Intervencion humana: definida como proporcion de tiempo, medida como casos | c-77 A5 | CUBIERTO |
| C-12 | El clasificador esta severamente descalibrado y no se advierte | c-77 A6 | CUBIERTO |
| C-13 | El universo trimestral de 3.700 no es compatible con 42/dia | c-77 A7 | CUBIERTO |
| C-14 | La pregunta sobre exactitud humana nunca se responde | c-77 B1 | CUBIERTO |
| C-15 | Coincidencia no explicada: preliminar 2m45s = experimental 165,3 s | c-77 B2 | CUBIERTO |
| C-16 | La compuerta de confianza (§6.3) se ejecuta antes del clasificador | c-77 C1/C2 | CUBIERTO |
| C-17 | El agente telefonico no tiene modelo de lenguaje conectado | c-77 C1/C2 (+ c-76 A-13) | PARCIAL |
| C-18 | El canal de origen nunca llega al backend (POST de 2 campos; Switch mal) | ARTEFACTO ya corregido por c-29 (commit ef656ac, 2026-09-17); texto: c-77 C3 | CUBIERTO (hallazgo stale) |
| C-19 | No existe mecanismo de reintento pese a que §6.5 lo declara | c-77 C4 | CUBIERTO |
| C-20 | TLS 1.3 y Nginx no existen en el despliegue publicado | c-77 C5 | CUBIERTO |
| C-21 | Los autores catalogaron 27 brechas y decidieron no cerrar seis | c-77 C6 (anexar registro) | PARCIAL |
| C-22 | El prompt clasifica en cuatro sectores, no en tres | c-77 C7 | CUBIERTO |
| C-23 | El Anexo B declara un tag `v1.0.0` inexistente | c-77 C8 | CUBIERTO |
| C-24 | Misatribucion verificada de Revina, Buza y Meister (2020) | c-78 B1 | CUBIERTO |
| C-25 | Rangos de Kappa atribuidos a Cohen; lectura "sustancial" vs "casi perfecto" | c-78 B3 | CUBIERTO |
| C-26 | Bibliografia sin actualizacion: 0 articulos arbitrados post-2020 | c-78 B2 | CUBIERTO |
| C-27 | El rango 88-94 % del §8.2 carece de cita | c-78 B2 | CUBIERTO |
| C-28 | Tres errores sustantivos en el marco normativo del Cap. 11 | c-79 L1-L4 | CUBIERTO |

**Conclusion critica**: los 28 criticos estan cubiertos (26 CUBIERTO, 2 PARCIAL). El
nucleo critico del dictamen ya tiene owner. Los PARCIAL son:

- **C-17** (agente sin modelo): c-77 C1/C2 confirma el flujo real, pero la afirmacion de
  latencia 12-15 s de §6.4 queda colgada (ver A-13, NUEVO en N3).
- **C-21** (27 brechas / registro de decisiones): c-77 C6 lo anexa; conviene confirmar que
  las cuatro brechas que el informe dice que siguen afirmativas quedan cubiertas.

**C-18 quedo RESUELTO (hallazgo stale).** La auditoria (PDF del 2026-08-04, sobre el commit
`d7df92c` del 2026-07-02) describia el flujo **previo** a c-29. Verificado en el HEAD actual
y con `git show ef656ac^:n8n/workflow.json`:

- El nodo `HTTP POST a MESA-AYUDAS` (`n8n/workflow.json:101`) envia **seis** campos,
  incluido `canal_origen_id` (no dos).
- El Switch `Rutear por canal de origen` (`n8n/workflow.json:384`) esta en modo `rules`
  con tres reglas de igualdad de cadena (`web`/`correo`/`telefonia`), no en modo
  expression.
- El backend acepta y persiste `canal_origen_id` (`IncidenteCreate.canal_origen_id:
  int | None`, `app/schemas/incidente.py:163`; `_resolve_canal`, `incidente_service.py:337,361`).
- Commit `ef656ac` (2026-09-17, c-29/c-30/c-32) introdujo exactamente esos dos fixes.

Residuo: **solo el texto de la tesis** (Tabla 4 usa `id_canal` en vez de `canal_origen_id`;
§5.3 describe dos llamadas en vez de una). Ya esta en **c-77 C3**. No requiere change nuevo
de software.

### Otras dimensiones transversales

| Dimension | Hallazgo | Change | Estado |
|---|---|---|---|
| Citas huerfanas (APA 2017 §11.5; SEPyME §1.1) | 2 citas sin entrada | c-78 maneja las fabricadas v7, no estas dos | NUEVO (M-01 + APA 2017) |
| Tablas: fuente APA 7 | Ninguna de las 9 tablas tiene linea de fuente | c-80 F4 (formato) no agrega fuente | PARCIAL |
| Figuras | 1 sola figura en 74 paginas | c-80 F2/F3 | CUBIERTO |
| Anexos A-G placeholder + Anexo H ausente | 7 anexos descriptivos; Anexo H no incorporado | c-80 F3 | CUBIERTO |
| Ortografia (52 ocurrencias; portada; acentuar_tesis.py) | diseño/desarrollo/completo/aquellos; portada sin tildes | c-80 F1 | CUBIERTO |
| Matriz de confusion / metricas por clase | Verificadas correctas | c-76 2.3/2.4 (reemplaza por 5x5 real) | CUBIERTO |
| Densidad de citas por capitulo (Cap 6: 1/1000; Cap 7: 0) | "muy desigual"; Cap 7 sin citas | c-78 no lo mide | NUEVO |

---

## 3. Hallazgos NUEVOS agrupados por change propuesto

Agrupados por afinidad de archivos y capitulo (evita colisiones de `.tex`):

### N1 — `c-92-tesis-marco-teorico-profundidad` (Cap 2)
- A-04 — profundizar §2.4 (prompting, calibracion de confianza, alucinacion, sensibilidad al idioma, evaluacion de LLM).
- A-05 — corregir §2.7 (definir exactitud multiclase directamente; retirar formula binaria).
- M-03 — retirar/reenmarcar §2.5 (Whisper no se usa; usar la transcripcion nativa de Twilio).
- M-04 — §2.6: justificar PostgreSQL contra alternativas concretas o reformular.
- M-02 (parcial) — §1.7/N2: sostener con cita la premisa sobre corpus EN/DE/PT.
- A-06 (parcial) — §2.2: alinear atribucion ITIL 2011 (TSO/Cabinet Office) en el cuerpo.

### N2 — `c-93-tesis-metodologia-rigor` (Cap 4)
- A-07 — §4.4: publicar calculo del tamaño muestral (200 vs 219) o corregir el margen.
- A-08 — §4.5/§6.7: publicar informe de cobertura + comando (o retirar el 80 %/87 %).
- A-09 — analisis de potencia a priori (§4.8).
- A-10 — §4.2: reconocer el confound operador/halves o rediseñar la afirmacion.
- M-05 — criterios de exclusion del corpus (duplicados, vacios, multicategoria).
- M-06 — §4.9: reubicar Scrumban fuera del capitulo metodologico.
- M-07 — declarar los dos analistas y su independencia.
- A-03 (parcial) — §1.6: reformular el tercer criterio del umbral 85 %.

### N3 — `c-94-tesis-implementacion-verificabilidad` (Caps 5-6)
- A-11 — §6.7: retirar la afirmacion de pruebas e2e de N8N (o implementarlas).
- A-12 — §6.7: corregir recuento/cobertura de la suite frontend (89/98,6 % -> 68/real).
- A-13 — §6.4: retirar/reformular la latencia 12-15 s (sin n ni procedimiento; C-17).
- M-09 — §6.1: retirar "Kubernetes 1.30" sin manifiesto.
- M-12 — §5.4: retirar "optimizados" sin procedimiento (o documentarlo).
- M-13 — Tabla 5: completar los puntos de entrada reales.
- M-08 (parcial) — §6.8: retirar el ejemplo hipotetico como "caso concreto".

### N4 — `c-95-tesis-resultados-discusion-rigor` (Caps 7-8)
- A-15 — §4.7/§7: reportar estadistico y p de Shapiro-Wilk.
- A-20 — §8.1: incorporar hipotesis alternativa / explicacion rival.
- A-21 — §8.3: documentar el baseline TF-IDF+SVM (procedimiento, particion, n, codigo).
- M-10 — §7.4: agregar ejemplos textuales anonimizados de errores.
- M-16 — §8.4: citar fuente de costos o acotar el alcance de la estimacion.
- A-23/A-25 (parcial) — acotar generalizaciones de §9 y la interpretacion estadistica.

### N5 — `c-96-tesis-citas-tablas-evidencia` (Cap 3 / transversal)
- A-26 — Tabla 1: agregar linea de fuente, citas y fecha de consulta; separar la fila "Propuesta".
- M-01 + APA 2017 — resolver las 2 citas huerfanas (SEPyME §1.1; APA 2017 §11.5).
- A-27 — §1.7/§6.1: corregir "n8n = codigo abierto" (licencia Sustainable Use).
- B-01 — §1.2/§1.8: nombrar/caracterizar la organizacion de forma consistente.
- Transversal tablas: linea de fuente APA 7 en las 9 tablas.
- Transversal citas: densidad por capitulo (Cap 6 y 7 sin citas).

> Alternativa: en lugar de 5 changes nuevos, **ampliar los existentes** (c-78 con N5,
> c-80 con la fuente de tablas, c-76/c-77 con N2/N4). El criterio de particion por
> capitulo minimiza colisiones de archivos pero multiplica changes; el criterio por
> "ownership de archivo" concentra.

---

## 4. Discrepancias y conflictos internos detectados

1. **c-80 usa numeros stale que c-76 reemplaza.** La tarea 6.8 de `c-80` grafica la
   matriz de confusion `[[76,4,2],[3,58,3],[2,2,50]]` (3x3 sintetica, 82/64/54). Debe
   usar la matriz **5x5 real** de c-76 (16/85/67/31/1; 147/200). La tarea 5.1 de c-80
   baja afirmaciones "fundadas en 89 % y 92 %", tambien stale (c-76 los pasa a 75,9 %
   y 73,5 %).
2. **c-80 introduce una entidad de mas.** El ER de c-80 (6.3/7.3) usa **7 entidades**;
   la auditoria y Tabla 4 describen **6**. Hay que fijar el numero real antes de
   graficar, o c-80 agrava A-19.
3. **c-78 no cubre A-26** (Tabla 1 sin citas) ni la densidad de citas por capitulo.
   Si no se crea N5, quedan sin owner.
4. **A-06 (ITIL 2011) tiene senal contradictoria.** `dictamen-correcciones.md`
   (re-verificacion 2026-10-10) afirma que `OGC2011_itil` "es correcto como esta
   escrito (ITIL 2011 fue OGC/TSO)"; la nueva auditoria (A-06) sostiene lo contrario
   (2011 = TSO/Cabinet Office; OGC = 2007). Verificar antes de tocar.
5. **A-03 se solapa con c-77 B1** pero no identico: B1 reformula H1; A-03 ataca el
   tercer criterio del §1.6. Falta una tarea explicita.
6. **M-18 y A-02 comparten la aritmetica de horas** (62 % / 180 h). c-76 T4 y c-77 A4
   deben coordinarse para no divergir.

---

## 5. Estado de la reconciliacion

- **Criticos**: cerrado. Los 28 criticos C-01..C-28 del informe completo tienen owner en
  C-76..C-80 (26 CUBIERTO, 2 PARCIAL: C-17 y C-21). No quedan criticos huerfanos.
- **A/M/B**: los ~22 hallazgos NUEVOS de la re-auditoria no tienen owner. Es el objeto de
  los changes N1..N5 (seccion 3).
- **C-18**: resuelto (hallazgo stale; el artefacto ya fue corregido por c-29). No requiere
  change de software. Residuo textual en c-77 C3.
- **Trazabilidad**: el informe completo quedo en `auditorias/` (PDF, no versionado). El
  texto extraido vive en `/tmp/opencode/auditoria_full.txt` (temporal).

---

## 6. Recomendacion (camino A confirmado por el autor)

1. **Crear cinco changes nuevos** N1..N5 (seccion 3), sin reabrir C-76..C-80.
2. **Corregir primero los conflictos internos** de la seccion 4 antes de aplicar:
   - c-80: figura 8 con la matriz 5x5 real (no la 3x3 sintetica) y afirmaciones con
     numeros de c-76 (75,9 %/73,5 %).
   - c-80: fijar el numero real de entidades del ER (6, no 7).
   - Decidir el owner de A-26 y de la densidad de citas (N5).
3. **C-18**: resuelto (artefacto corregido por c-29; residuo textual en c-77 C3). Solo
   queda **C-21** (anexar el registro de decisiones) como residual a confirmar en c-77 C6.
4. Actualizar `CHANGES.md` y `dictamen-correcciones.md` con el resultado del cruce y la
   FASE 31 (N1..N5).

---

## 7. Addendum (2026-10-19) — resultado del propose y matices de verificacion

Cambios creados (FASE 31), todos `openspec validate --strict` OK, planning 4/4:

| Change | Governance | Hallazgos |
|---|---|---|
| `c-92-tesis-marco-teorico-profundidad` | MEDIUM | A-04, A-05, M-03, M-04 (+ M-02/A-06 parciales) |
| `c-93-tesis-metodologia-rigor` | MEDIUM | A-07, A-08, A-09, A-10, M-05, M-06, M-07, A-03 |
| `c-94-tesis-implementacion-verificabilidad` | MEDIUM | A-11, A-12, A-13, M-08, M-09, M-12, M-13 |
| `c-95-tesis-resultados-discusion-rigor` | MEDIUM | A-15, A-20, A-21, M-10, M-16 (+ A-23/A-25 parciales) |
| `c-96-tesis-citas-tablas-evidencia` | BAJO | A-26, M-01 + APA 2017, A-27, B-01 |

`c-80` corregido: figura 8 pasa a derivar la matriz 5x5 real de `evaluation/report.md`
(no hardcodea), F7 usa 75,9 %/73,5 %, W=335/r=0,983.

### Matiz 1 — la tesis source esta stale, pero NO es identica al PDF auditado

Chequeo del `.tex` en HEAD: `92~` (14), `165,3` (8), `0,919` (12), `Operaciones` (26),
`tres sectores` (8), `W = 0` (4). La tesis fuente sigue con los numeros sinteticos: la
correccion es necesaria. PERO hay divergencia con el PDF auditado en un punto:

- **A-19 — VERIFICADO (2026-10-19): no reproduce, STALE.** El `.tex` dice "siete
  entidades" de forma consistente: §5.6 (`05-arquitectura.tex:79`), el pie del ER
  (`:106`) y el Anexo C (`12-anexos.tex:25`). `tab:entidades` lista las 7 principales
  (`incidente`, `sector`, `estado`, `canal_origen`, `clasificacion_log`, `users`,
  `directorio_empleado`), coincidentes con `App/Backend/app/models/`. El texto "siete"
  precede a esta sesion (commit `8466cbe`). La contradiccion "seis vs cinco" del informe
  auditado corresponde a una revision anterior (el PDF). Residuo menor: `06-implementacion.tex:72`
  dice "seis entidades" al describir la iteracion de Semanas 3-4 (posible dato historico
  legitimo); alinear o marcar como historico al aplicar c-93.

### Matiz 2 — el repositorio evoluciono desde el commit auditado

La auditoria es sobre `d7df92c` (2026-07-02). El HEAD actual tiene: **136** archivos
`test_*.py` en backend (el dictamen dice "22 suites"), **56** archivos de prueba frontend
con **340** ocurrencias `it(` (el dictamen dice 68), y `docs/openapi.json` con **33
rutas** (no 25). Los conteos del dictamen (A-11, A-12, M-13) son **stale respecto de
HEAD**: las tareas de `c-94` exigen re-medir en HEAD, no hardcodear.
