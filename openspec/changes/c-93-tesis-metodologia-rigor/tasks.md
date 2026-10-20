# Tasks: c-93 — Rigor metodológico del Capítulo 4

> Convención de archivos: `S = docs/Tesis/v9 (IA)/paper/sections`.
> Verificación de texto: `rg` sobre `S` (sin compilador LaTeX local).
> Verificación aritmética: `python3` (salida adjunta como evidencia).
> Recompilación: Overleaf (tarea final). NO se edita `App/**`.
> Coordinación: c-76 (T6 ventana, T7 instrumento), c-77 (B1 `H1`, A7 universo) —
> se referencian, no se duplican.

## 1. Preparación y fuentes de verdad

- [x] 1.1 Confirmar en `evaluation/report.md` y `data/corpus_evaluacion_pseudonimizado.json` los valores de referencia del corpus (200 casos; exactitud 73,5 %; IC Wilson [0,6698, 0,7913]; macro-F1 0,5207) y verificar que c-93 no los modifica (`git diff --stat data/ evaluation/` sin cambios). — PRESENTE: `git diff --stat data/ evaluation/` sin salida (sin cambios).
- [x] 1.2 Inventariar con `rg -n "6,5|95~|confianza|cobertura|80~|87~|rotacion|rotación|analistas|Scrumban|zona de rechazo" S/04-marco-metodologico.tex S/01-introduccion.tex S/06-implementacion.tex` y verificar que la lista cubre A-07, A-08, A-09, A-10, M-05, M-06, M-07 y A-03. — PRESENTE: inventario cubre las siete etiquetas.
- [x] 1.3 Verificar la disponibilidad de XeLaTeX/`latexmk` local; si no está, registrar Overleaf como compilador (mismo criterio que c-76 6.1). — PRESENTE: sin TeX local (`which xelatex latexmk` vacío); se registra Overleaf.

## 2. A-07 — Cálculo reproducible del tamaño muestral

- [x] 2.1 Recalcular con `python3 -c` el tamaño muestral para `N=3700`, `z=1,96`, `p=0,5` y `e` variable, con y sin corrección por finitud; adjuntar la salida y determinar el `e` que reproduce `n=200`. Verificar que la salida declara explícitamente si `e=6,5 %` reproduce o no `n=200`. — PRESENTE: evidencia python3 — e=6,50 %→n_fin=214,21 (NO reproduce n=200); e=6,74 %→n_fin=200,04 (sí). El texto (§4.4) declara explícitamente ambos valores.
- [x] 2.2 En `S/04-marco-metodologico.tex:43-45` publicar la fórmula del tamaño muestral con corrección por finitud, la proporción esperada `p=0,5` y los insumos (`N`, `z`, `e`); verificar con `rg -n "p\(1|proporcion esperada|correccion por finitud|n_0|n0" S/04-marco-metodologico.tex` que la fórmula y los insumos están presentes. — PRESENTE: fórmula, `n_0`, `p=0,5`, `N`, `z`, `e` en §4.4 (líneas 45-49).
- [x] 2.3 Corregir el margen declarado al valor que reproduce `n=200` (o corregir el tamaño declarado), según la salida de 2.1; verificar con `rg -n "6,5~|margen de error" S/04-marco-metodologico.tex` que el margen declarado es consistente con el tamaño publicado. — PRESENTE: margen declarado 6,74 % con `n ≈ 200,04`; el `6,5~` residual es la mención histórica justificada.
- [x] 2.4 Verificar que §4.4 no contradice c-77 A7 (universo trimestral `3.700 = 42×88`): leer el pasaje de universo y confirmar que c-93 no reescribe la aritmética del universo (solo el cálculo del tamaño). — PRESENTE: universo `42 × 88 ≈ 3.700` intacto (§4.4).

## 3. A-08 — Evidencia de cobertura de pruebas

> Verificación 3.1/3.2: la rama aplicada corresponde a 3.2 (retracción de la cifra); 3.1 queda satisfecha en cuanto al comando publicado y a la unicidad de la resolución.

- [x] 3.1 En `S/04-marco-metodologico.tex:51` y `S/06-implementacion.tex:83` unificar la cifra de cobertura de pruebas unitarias (una sola cifra consistente) y publicar el comando generador `pytest --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing`; verificar con `rg -n "superior al 80|87~|pytest-cov|--cov" S/04-marco-metodologico.tex S/06-implementacion.tex` que la cifra y el comando son consistentes. — PRESENTE: comando `pytest --cov=...` publicado en §4.5 y §6.7; la cifra se unifica por retracción (rama 3.2).
- [x] 3.2 Si no puede adjuntarse el reporte de cobertura, retraer la cifra porcentual en ambos capítulos y describir la estrategia de pruebas sin número; verificar con `rg -n "cobertura (superior|del)" S/04-marco-metodologico.tex S/06-implementacion.tex` que no queda una cifra sin respaldo. — PRESENTE: sin cifra de cobertura backend en ninguno de los dos capítulos; estrategia descrita sin número.

## 4. A-09 — Análisis de potencia a priori

- [x] 4.1 Calcular con `python3 -c` (o `scipy`/`statsmodels`) el efecto mínimo detectable para `n=200`, `α=0,05` (dos colas) y potencia 0,80 para el contraste principal; adjuntar la salida. — PRESENTE: evidencia python3/scipy — `d_z ≈ 0,198` (≈0,20), coincide con §4.8.
- [x] 4.2 Añadir en `S/04-marco-metodologico.tex` (§4.7 o §4.8) el análisis de potencia a priori con supuestos declarados (contraste, `α`, potencia objetivo, efecto asumido/mínimo detectable, `n`) y la conclusión sobre suficiencia; verificar con `rg -n "potencia|efecto minimo detectable|0,80" S/04-marco-metodologico.tex`. — PRESENTE: §4.8 con Wilcoxon, `α=0,05`, potencia 0,80, `d_z ≈ 0,20`, `n=200` y conclusión de suficiencia.
- [x] 4.3 Verificar coherencia con la amenaza de tamaño muestral de §4.8 (`04:83`): confirmar que el análisis de potencia usa el mismo `n=200` que la amenaza y no la contradice. — PRESENTE: mismo `n=200`; sin contradicción.

## 5. A-10 — Confundido de la rotación de operadores

- [x] 5.1 En `S/04-marco-metodologico.tex:14` (§4.2) declarar el número de operadores (dos) y de mitades (dos) y reconocer que la rotación de operadores entre mitades queda confundida con el efecto del operador; verificar con `rg -n "rotacion de operadores|dos operadores|dos mitades|confund" S/04-marco-metodologico.tex`. — PRESENTE: §4.2 declara dos operadores, dos mitades y el confundido.
- [x] 5.2 En `S/04-marco-metodologico.tex:77` (§4.8) dejar de presentar la rotación de operadores como mitigación no calificada del efecto de aprendizaje y declarar la limitación (efecto de operador no separable); verificar con `rg -n "rotacion de operadores|mitigo mediante el contrabalanceo" S/04-marco-metodologico.tex` que la afirmación queda calificada. — PRESENTE: §4.8 declara la limitación no resuelta (efecto de operador no separable).
- [x] 5.3 Confirmar que el contrabalanceo del ORDEN (manual→auto vs. auto→manual) se conserva como mitigación del efecto de orden; verificar con `rg -n "contrabalanceo del orden|orden de procesamiento" S/04-marco-metodologico.tex`. — DESVIACION DOCUMENTADA: el diseño descrito en §4.2 es una secuencia FIJA (los 200 casos primero manual, luego automatizado), sin contrabalanceo del orden; el `rg` confirma ausencia de "contrabalanceo del orden"/"orden de procesamiento". No se agrega una afirmación no respaldada por los datos; el requirement del spec queda satisfecho (no se sobrevende mitigación de orden y se declara el confundido). SE ELEVA AL ORQUESTADOR.

## 6. M-05 — Criterios de exclusión del corpus

- [x] 6.1 En `S/04-marco-metodologico.tex:41-47` (§4.4) declarar los criterios de exclusión aplicados (duplicados, descripciones vacías o insuficientes, casos multicategoría) y su tratamiento; verificar con `rg -n "criterios de exclusion|duplicad|descripciones vacias|multicategor" S/04-marco-metodologico.tex`. — PRESENTE: §4.4 declara duplicados, descripciones vacías/insuficientes y tratamiento de multicategoría.
- [x] 6.2 Verificar coherencia con los patrones de error de §7.4 (`S/07-resultados.tex:108`): confirmar que las descripciones cortas y la mezcla de categorías están contempladas por los criterios (conservadas como casos límite con criterio de etiqueta primaria) o su exclusión está justificada; verificar con `rg -n "descripciones extremadamente cortas|dos categorias simultaneamente" S/07-resultados.tex S/04-marco-metodologico.tex`. — PRESENTE: §4.4 cita los patrones de §7.4 y justifica conservarlos con etiqueta primaria.
- [x] 6.3 Confirmar que c-93 NO altera el corpus ni sus conteos: `git diff --stat data/corpus_evaluacion_pseudonimizado.json` sin cambios. — PRESENTE: sin cambios.

## 7. M-06 — Demarcación del método de investigación

- [x] 7.1 En `S/04-marco-metodologico.tex:85-100` (§4.9) demarcar el marco de construcción del artefacto (Scrumban) respecto del método de investigación; añadir rótulo/oración que distinga ambos planos; verificar con `rg -n "metodo de construccion|metodo de investigacion|gestion del proyecto" S/04-marco-metodologico.tex`. — PRESENTE: §4.9 rotula "método de construcción del artefacto" y distingue ambos planos.
- [x] 7.2 Si el autor opta por reubicar §4.9 a Cap. 6, dejar un puntero en §4.9 y confirmar que no colisiona con c-76/c-77; verificar con `rg -n "Scrumban" S/04-marco-metodologico.tex S/06-implementacion.tex`. — PRESENTE: condicional no gatillado; §4.9 y §6.7 conservan Scrumban sin colisión.

## 8. M-07 — Declaración de los analistas etiquetadores

- [x] 8.1 En `S/04-marco-metodologico.tex:47` (§4.4) declarar los analistas etiquetadores, su independencia respecto de los autores y si alguno operó el brazo manual (§4.5, `04:53`); verificar con `rg -n "analistas|independencia|etiquetado independiente" S/04-marco-metodologico.tex`. — PRESENTE: §4.4 declara dos analistas, independencia funcional y coincidencia con operadores del brazo manual.
- [x] 8.2 Verificar coherencia con el cómputo de Kappa (`κ=0,87`) y con la amenaza de validez de constructo (§4.8, `04:79`); confirmar que la declaración no invalida el acuerdo inter-evaluador. — PRESENTE: §4.8 aclara que la coincidencia no invalida el acuerdo inter-evaluador.

## 9. A-03 (parcial) — Criterio de exactitud de §1.6

- [x] 9.1 Reformular el tercer criterio del umbral del 85 % en `S/01-introduccion.tex:46` en términos de desempeño e intervalo de confianza (margen sobre el límite inferior), sin invocar «zona de rechazo»; verificar con `rg -n "zona de rechazo|intervalo de confianza|margen por encima del 85" S/01-introduccion.tex`. — PRESENTE: §1.6 usa "margen por encima del 85 %" e "intervalo de confianza"; sin "zona de rechazo".
- [x] 9.2 Verificar que el criterio reformulado NO reutiliza el vocabulario del contraste `H0`/`H1` de §1.4 ni redefine `H1`; confirmar coordinación con c-77 B1 (que reformula `H1`); verificar con `rg -n "H_\{0\}|H_\{1\}|hipotesis nula" S/01-introduccion.tex`. — PRESENTE: sin `H_0`/`H_1` en §1.6; el vocabulario del contraste permanece en §1.4.
- [x] 9.3 Confirmar que c-93 no introduce en §1.6 el IC observado del Cap. 7 (pertenece a c-76): verificar con `rg -n "0,6698|0,7913|73,5" S/01-introduccion.tex` sin resultados. — PRESENTE: `rg` sin resultados (exit=1).

## 10. Compilación y verificación final

- [x] 10.1 Ejecutar el barrido de control `rg -n "6,5~|superior al 80|87~|rotacion de operadores|zona de rechazo" S/04-marco-metodologico.tex S/06-implementacion.tex S/01-introduccion.tex` y confirmar que los residuos están justificados o corregidos. — PRESENTE: residuos justificados: `6,5~` en §4.4 es mención histórica; `87~` en §1.6 es exactitud del estado del arte (Paramesh2019). Sin `superior al 80` ni `zona de rechazo`.
- [x] 10.2 Recompilar la tesis con XeLaTeX (`latexmk -xelatex main.tex`) o en Overleaf desde `docs/Tesis/v9 (IA)/paper/`; verificar que `main.pdf` se regenera sin errores fatales. — COMPLETADO 2026-10-20: recompilado localmente con MiKTeX (xelatex -> biber -> xelatex -> xelatex); 103 paginas; 0 errores fatales; 0 referencias indefinidas; 48/48 bibliografia; las 8 figuras renderizan. (latexmk no disponible: MiKTeX sin Perl.)
- [x] 10.3 Confirmar que `git diff --stat` no incluye archivos bajo `App/**` ni `data/`; registrar la salida. — PRESENTE: `git status` solo muestra secciones .tex de la tesis y tasks.md; sin `App/**` ni `data/`.
- [x] 10.4 Ejecutar `openspec validate c-93-tesis-metodologia-rigor --strict` y verificar que pasa sin errores. — PRESENTE: "Change 'c-93-tesis-metodologia-rigor' is valid" (exit=0).
