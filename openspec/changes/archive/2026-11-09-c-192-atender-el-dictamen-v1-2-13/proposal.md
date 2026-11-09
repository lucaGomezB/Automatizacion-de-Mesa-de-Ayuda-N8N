# Proposal: Atender el dictamen CONEAU sobre v1.2.13 (cuatro observaciones, item 12 y residuales)

## Why

El dictamen CONEAU del 2026-11-09 sobre la release `v1.2.13` `Gonzalo` lo tiene; el archivo
todavia no esta en `auditorias/`; califica el documento escrito con 9,00 y deja cuatro
observaciones nuevas, el item 12 del inventario anterior y residuales menores. Ninguna exige
mediciones nuevas: todas se cierran reescribiendo lo que los artefactos ya muestran. La mas
critica es de proceso: el PDF del tag `v1.2.13` imprime el hash de la release previa
(`7937efd`, v1.2.12) porque el commit de contenido conservo el hash viejo y el commit del hash
lo reemplazo despues. Dejar esa correccion sin atender entrega un PDF con una referencia
verificable equivocada. La release `v1.2.14` cierra el resto del dictamen sin residuos nuevos.

## What Changes

- **Regla de hash de release (Anexo B, critica)**: el commit de contenido SHALL llevar una
  oracion de reemplazo (patron c-188) que declare que el hash completo de `v1.2.14` se
  consigna en el commit que sigue al tag; el PDF etiquetado MUST NOT imprimir el hash de la
  release previa. El commit posterior reemplaza la oracion por el hash real del commit de
  contenido.
- **Item 12 - MDE del Spearman**: en 8.7, `numeros-canonicos.md` (3.16) y el registro, el MDE
  pasa de 0,2834 a 0,276. La formula vigente multiplica el denominador por la ARE de Wilcoxon
  (0,864), que no corresponde a una correlacion de rangos; el valor correcto usa la eficiencia
  de Spearman frente a Pearson bajo normalidad (9/pi^2 ≈ 0,912):
  `tanh((z_{0,975} + z_{0,80}) / sqrt(107 * 0,912)) = 0,276`.
- **Segunda sub-hipotesis**: se conserva el veredicto "refutada" (estimacion 17,0 % >= 15 %)
  y se agrega el matiz explicito: el IC de Wilson [11,8 %; 23,9 %] contiene 0,15 y la prueba
  binomial da p = 0,28, de modo que la evidencia es compatible con un valor cercano al umbral
  ("no se puede descartar 0,15"). Se corrigen dos errores de 8.3 (el "122 (61,0 %)" es 122/200,
  no 122/147; son 83,0 % de los 147 revisados) y la celda del OE4 de la Tabla 18
  (`09-conclusiones.tex`), que hoy se contradice. El matiz se propaga solo donde se enuncia el
  veredicto (8.3 y, opcionalmente, 9.1); no alarga el resumen ni el abstract (tope 250).
- **1.6 - atribucion del kappa**: se separan los dos pares. El acuerdo moderado (0,5569,
  `p_o = 0,69`; `p_e = 0,30`) es el doble etiquetado `E1`/`E2`; el par analista externo +
  analista autor tiene acuerdo 0,87 y no tiene intervalo (su tabla primaria no se conservo).
- **Conjunto laxo del brazo manual**: 8.7 dice "union de los sectores adicionales de ambos
  etiquetadores"; el codigo (`evaluation/campana.py`, `construir_referencia`) usa la
  interseccion. Se corrige "union" por "interseccion" (es lo que da 130/151; la union daria
  137).
- **Residuales menores**: 6.3 "telefonia (trigger de Twilio)" se alinea con 6.4 ("callback de
  grabacion de Twilio"); la oracion de Xiong en 3.1 se atenua como en 2.5 y 9.2 ("predecir las
  fallas sigue siendo un desafio"); se desarrolla `VIS` en su primer uso (7) o se agrega al
  glosario, con uso garantizado; `FrugalGPT` conserva la entrada TMLR con la URL de OpenReview
  `cSimKw5p6R` o se agrega el preprint arXiv `2305.05176` como respaldo, con decision
  registrada; el exceso de 118 paginas sobre el tope de 100 se registra como residual
  declarado, sin reduccion en este change.
- **Registro, Anexo I y release**: seccion nueva en `dictamen-correcciones.md`, quinta tabla
  de trazabilidad en el Anexo I si corresponde, tag `v1.2.14` con el patron de hash de D1.

## Out of Scope

- La evidencia del nivel pago y el consentimiento de los cuatro participantes de la campana
  complementaria: van a un `v1.2.15` posterior. No se editan las secciones 7 ni 11 por esos
  motivos.
- Nuevas mediciones, corridas del clasificador o re-analisis de la campana. Los unicos
  calculos admitidos son aritmetica sobre artefactos ya publicados (recomputo del MDE, IC de
  Wilson y prueba binomial de 25/147, lectura de `construir_referencia`).
- Cambios en `App/`, `n8n/`, `evaluation/` (codigo o artefactos), figuras o datos de campana.
- Reduccion del PDF al tope de 100 paginas.
- Versionado del archivo del dictamen mientras Gonzalo no lo entregue (residual declarado).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: se modifica el requisito del estado de la segunda sub-hipotesis (agrega el
  matiz del intervalo y la binomial; fija ambos denominadores del 122) y se agregan requisitos
  para la regla de hash de release del Anexo B, el MDE del Spearman con la eficiencia 9/pi^2
  (0,912), la atribucion separada del kappa de 1.6, el conjunto laxo por interseccion, los
  residuales menores y la trazabilidad del dictamen del 9-11 sobre v1.2.13.

## Impact

- `docs/Tesis/v10 (IA)/paper/sections/{00-resumen,00-glosario,01-introduccion,03-estado-del-arte,06-implementacion,07-resultados,09-conclusiones,12-anexos}.tex`.
- `docs/Tesis/Correcciones/{dictamen-correcciones,numeros-canonicos}.md`;
  `docs/Tesis/v10 (IA)/paper/compilacion.md` y `tesis_para_agente.md` regenerados.
- Versionado diferido de `auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md` cuando
  Gonzalo lo entregue (tarea no bloqueante).
- Lectura sin edicion de `evaluation/campana.py` (`construir_referencia`), `evaluation/stats.py`
  (`efecto_minimo_detectable`) y `evaluation/doble_etiquetado.py`.
- Gobernanza: MEDIUM (correcciones documentales que tocan el veredicto de una sub-hipotesis y
  texto de proceso de release). Sin codigo de aplicacion ni datos.
