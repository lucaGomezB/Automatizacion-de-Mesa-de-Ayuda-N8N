# Design: c-95 — Rigor de Resultados y Discusión, y límites del Capítulo 9

## Context

Ver `proposal.md`. El estado actual relevante:

- `04-marco-metodologico.tex:63` afirma que Shapiro-Wilk rechazó la normalidad
  "en ambos grupos con valores \(p < 0{,}01\)" sin reportar \(W\) ni \(p\).
- `07-resultados.tex:30` presenta Wilcoxon; `07-resultados.tex:90-110` tipifica
  los 16 errores sin citar ningún texto de incidente.
- `08-discusion.tex:6-16` (§8.1) interpreta cuatro aspectos y no interroga los
  resultados; `08-discusion.tex:38` (§8.3) enuncia el baseline TF-IDF+SVM en una
  frase; `08-discusion.tex:46` (§8.4) da costos sin fuente.
- `09-conclusiones.tex:16` (§9.1) introduce la lectura de \(W=0\); `:22` (§9.2)
  afirma la superioridad general de los LLM sobre clasificadores supervisados.
- El corpus real está en `data/corpus_evaluacion_pseudonimizado.json`; las
  predicciones en `evaluation/predicciones.json`; el reporte en
  `evaluation/report.md`.

Restricciones duras: este change es solo documentación y artefactos de apoyo; no
toca `App/**` ni `evaluation/stats.py`; no duplica c-76 (números reales), c-77
(calibración y eliminación de \(W=0\)), c-78 (atribución y evidencia contraria) ni
c-80 (deduplicación 8.1/9.1 y rebaja de juicios de valor).

## Goals / Non-Goals

**Goals:**

- Reportar Shapiro-Wilk de forma completa y trazable.
- Convertir §8.1 en una discusión que interrogue los resultados con
  explicaciones rivales y analice la confusión de Sistemas.
- Resolver la falta de trazabilidad del baseline TF-IDF+SVM mediante un alcance
  explícito y honesto.
- Publicar ejemplos textuales anonimizados de errores.
- Sustentar o acotar los costos de §8.4.
- Retirar del Capítulo 9 la interpretación estadística nueva y la afirmación
  general no sostenida.

**Non-Goals:**

- No re-medir el corpus ni cambiar sus valores numéricos.
- No reimplementar el baseline TF-IDF+SVM ni crear código de evaluación nuevo.
- No corregir los números de c-76, la calibración de c-77, la atribución de
  c-78 ni la forma de c-80.
- No tocar `App/**` ni la implementación del clasificador.

## Decisions

### D1 — Shapiro-Wilk: reporte completo y recálculo post-c-77

Se reportan \(W\) y \(p\) para tres conjuntos: tiempos manuales, tiempos
automatizados y diferencias pareadas. Se usa `scipy.stats.shapiro` sobre el
corpus real. El cálculo se ejecuta después de c-77 (E3), porque esa corrección
altera los tiempos telefónicos y, por lo tanto, los estadísticos.

Valores de referencia calculados en planificación sobre el corpus previo a E3
(no copiar sin recalcular):

| Conjunto | n | W | p |
|---|---|---|---|
| Manual | 200 | 0,803099 | 3,71e-15 |
| Automatizado | 200 | 0,838744 | 1,26e-13 |
| Diferencias | 200 | 0,834311 | 7,91e-14 |

La tesis reporta \(W\) con tres decimales y \(p\) en notación científica con dos
decimales significativos. `evaluation/report.md` agrega una sección "Normalidad"
con la tabla, el comando reproducible y el hash SHA-256 del corpus usado.

Alternativas consideradas: (a) reportar solo \(p<0{,}01\) — insuficiente para
A-15; (b) reportar solo los grupos y no las diferencias — deja incompleta la
justificación del contraste pareado; (c) agregar una función a
`evaluation/stats.py` — se descarta para no colisionar con c-77 y porque el
cálculo es una llamada directa a SciPy documentada en el reporte.

### D2 — §8.1: lectura crítica con explicaciones rivales

Se agregan tres párrafos al final de §8.1, sin crear una subsección nueva (para
no renumerar 8.2–8.5 ni duplicar la reescritura de c-80 F5):

1. **Explicaciones rivales de la reducción de tiempo.** Al menos:
   - asimetría del instrumento (el flujo manual se cronometra en vivo e incluye
     lectura, búsqueda y carga; el automatizado se mide por marcas del sistema);
   - simplificación de la tarea o mezcla de canales (el corpus agrega web, correo
     y telefonía con costos de entrada distintos);
   - novedad o efecto Hawthorne y aprendizaje del operador;
   - selección de los 200 casos y validez externa.
   Para cada una: evidencia disponible, qué la debilita y qué observación
   permitiría descartarla. Se declara explícitamente qué no puede descartarse con
   el diseño actual.
2. **Confusión de Sistemas.** Se usa la matriz 5x5 real y las métricas por clase:
   Sistemas tiene precisión 0,3684, sensibilidad 0,4375 y F1 0,4000; sus 16 casos
   se reparten entre Soporte Tecnico Software (5), Bases de Datos (2), Seguridad
   Informatica (2) y 7 aciertos. Se distingue ambigüedad léxica/taxonómica de
   falta de contexto en la descripción. Se menciona que Bases de Datos tiene
   \(n=1\), por lo que su F1 nulo no es estimable y no debe sobreinterpretarse.
3. **Qué se puede y qué no se puede concluir.** Se separa "consistente con la
   hipótesis" de "confirmación concluyente"; se remite a las amenazas a la
   validez de §4.8 sin repetirlas.

No se toca la frase "valida la hipótesis subsidiaria" ni "consecuencia deseable":
son de c-80 F7. No se repite la tensión bibliográfica de Revina et al.: es de
c-78 B1. La frontera es: c-95 interroga la validez interna y la interpretación
causal; c-78 aporta la evidencia externa contraria.

Alternativa considerada: crear una subsección 8.2 "Lectura crítica". Se descarta
porque desplaza la numeración y aumenta el riesgo de conflicto con c-80.

### D3 — Baseline TF-IDF+SVM: alcance honesto, no reconstrucción

No existen en el repositorio procedimiento, partición, \(n\), código ni fixtures
del baseline. Reconstruirlo excede el alcance de este change y podría producir
números distintos a 78 %/0,764, lo que exigiría otra discusión metodológica.

Decisión: se retira la cifra como resultado y se declara el chequeo como
exploratorio, no reproducible y no comparable; se elimina la afirmación de
ganancia sustantiva; se declara que una comparación sistemática contra
clasificadores supervisados sobre el corpus completo queda como trabajo futuro.
La limitación se redacta en §8.3 (quinto punto de "Limitaciones").

Alternativas consideradas: (a) documentar el baseline con una nueva partición y
publicar código — mayor rigor, pero fuera del alcance de "corregir el texto" y
con riesgo de abrir un frente experimental nuevo; (b) mantener la cifra con una
nota de "exploratorio" — deja un número no verificable en la tesis. Se elige (c)
retirar la cifra y acotar el alcance, que satisface A-21 sin inventar evidencia.

Consecuencia: §9.2 no puede apoyarse en ese contraste; ver D6.

### D4 — Ejemplos textuales anonimizados en §7.4

Se seleccionan 2–3 casos mal clasificados de `evaluation/predicciones.json`,
priorizando los que ilustren los tres patrones de la Tabla 9 (descripción corta,
mezcla de categorías, jerga local). Para cada uno se publica: descripción
anonymizada, sector asignado, sector predicho y confianza. Se verifica que el
texto no contenga nombres, correos, teléfonos, direcciones ni nombres internos de
sistemas. El corpus ya está pseudonimizado; aun así se hace una revisión manual y
un barrido con `rg` de patrones de PII antes de citar.

Formato: un párrafo con comillas textuales o una tabla pequeña; se prefiere un
párrafo para no agregar una tabla nueva al capítulo. No se altera la Tabla 9 ni
sus conteos.

Alternativa considerada: publicar los 16 casos. Se descarta por longitud y por
riesgo de reidentificación.

### D5 — Costos: fuente oficial y cota explícita

§8.4 se reescribe para que cada rubro tenga respaldo:

- **Inferencia:** citar la página oficial de precios de Gemini API
  (`https://ai.google.dev/gemini-api/docs/pricing`, consultada en la fecha de
  aplicación), indicar el modelo declarado en la tesis y los supuestos de tokens
  de entrada/salida por invocación. Si el valor resultante no es 0,02 USD, se
  reemplaza por el calculado; si el precio depende de la banda, se presenta como
  rango.
- **Infraestructura:** citar una lista de precios pública de un proveedor
  identificado (por ejemplo, el precio on-demand de una instancia con 2 vCPU y
  4 GB, 730 h/mes) y declarar los rubros incluidos. Si solo se puede sostener un
  orden de magnitud, se presenta como cota (por ejemplo, "entre X e Y USD/mes
  según proveedor y respaldos") con supuestos explícitos, no como cotización.
- **Modelo:** la frase editada debe usar el identificador de modelo que la tesis
  declara como desplegado (`gemini-3.6-flash`); no se introduce un precio para un
  modelo que el documento ya no declara.

Alternativa considerada: mantener el rango 50–100 USD/mes y agregar una nota
genérica "según proveedor". Se descarta porque no es una fuente verificable.

### D6 — Capítulo 9: mover/eliminar, no reargumentar

- **§9.1:** se elimina la interpretación de \(W=0\) ("resultado poco frecuente",
  "interpretada con cautela") y cualquier estadístico inferencial nuevo. Si hace
  falta una referencia, se remite a §7.1/§8.1. c-77 A1 ya elimina \(W=0\); c-95
  opera después y verifica que no quede la interpretación residual.
- **§9.2:** se reescribe la afirmación general para acotarla: "en este corpus,
  este dominio y este contraste, el esquema híbrido alcanzó..." y se elimina
  "superiores a los de clasificadores supervisados clásicos" como conclusión
  general. Se declara que la comparación disponible es limitada (ver D3) y se
  remite a §8.2/§8.3, donde c-78 incorpora la tensión de evidencia contraria.
  No se duplica la discusión bibliográfica de c-78.

Alternativa considerada: mantener la afirmación y calificarla con "en este
estudio". Se descarta porque la única comparación cuantitativa no es verificable
tras D3; la acotación debe ser explícita y no solo adjetival.

### D7 — Orden de aplicación y matriz de conflicto

D-ORDER: aplicar c-95 **después** de c-76, c-77, c-78 y c-80. Motivos:

| Change | Archivo/sección compartida | Propiedad |
|---|---|---|
| c-76 | `07-resultados.tex` (tiempos, matriz, errores), `08-discusion.tex` (números), `09-conclusiones.tex` (cifras) | Números reales y distribución |
| c-77 | `04:63-71`, `07:30-36`, `09:16` | \(W=0\), convención, fórmula, calibración |
| c-78 | `08:20-24`, `08:22` | Revina y evidencia contraria |
| c-80 | `08:8-16`, `09:12,24` | Deduplicación 8.1/9.1 y rebaja de juicios |

c-95 no reescribe esas frases: agrega la interrogación crítica (D2), acota el
baseline (D3), agrega ejemplos (D4), sustenta costos (D5) y delimita Conclusiones
(D6). Antes de editar, verificar por contenido y no solo por número de línea,
porque las dependencias desplazan líneas.

## Risks / Trade-offs

- **Recalcular Shapiro antes de c-77 deja números obsoletos** → D1 exige
  recalcular después de E3 y registrar el hash del corpus; el reporte incluye la
  fecha y el comando.
- **La lectura crítica puede sonar a autoimpugnación excesiva** → se equilibra
  con lo que el diseño sí permite concluir (D2.3): reducción observada, magnitud
  y límites, sin negar el resultado.
- **Retirar el baseline debilita el contraste metodológico** → se declara como
  limitación y trabajo futuro; es preferible a mantener una cifra no verificable.
  Si el autor quiere recuperar el contraste, requiere un change experimental
  aparte con partición y código.
- **Los precios oficiales cambian** → se cita la fecha de consulta y se presenta
  el costo como orden de magnitud; no se usa como compromiso contractual.
- **Ejemplos textuales con PII** → revisión manual y barrido `rg` antes de citar;
  se prefiere descripción corta y se eliminan identificadores internos.
- **Conflictos con changes previos** → D-ORDER y verificación por contenido; no
  se editan las frases propiedad de c-76/c-77/c-78/c-80.

## Migration Plan

No hay migración de datos ni de infraestructura. Aplicación secuencial sobre
archivos `.tex` y `evaluation/report.md`; recompilación en Overleaf con XeLaTeX.
Rollback: `git checkout --` de los archivos afectados o `git revert` del commit.

## Open Questions

Ninguna que cambie el alcance o los specs. La única decisión diferible es si el
autor querrá en el futuro reproducir el baseline TF-IDF+SVM; se registra como
trabajo futuro y no bloquea este change.
