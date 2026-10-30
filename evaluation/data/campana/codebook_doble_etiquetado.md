# Codebook congelado del doble etiquetado

Documento operativo unico para el etiquetado manual de la campana de medicion. Se
entrega a los etiquetadores `E1` y `E2`. Es identico para ambos y se congela antes
de etiquetar.

Cada seccion declara su fuente versionada.

## 1. Taxonomia canonica de sectores

Fuente: `openspec/specs/sector-taxonomy/spec.md`, requisito TAX-001.

Los sectores canonicos son exactamente las siguientes cadenas, sensibles a
mayusculas y sin tildes. Deben escribirse tal cual:

1. `Seguridad Informatica`
2. `Soporte Tecnico Hardware`
3. `Soporte Tecnico Software`
4. `Bases de Datos`
5. `Sistemas` — categoria propia, para un servidor en produccion o un sistema
   corporativo sin encuadre especifico de seguridad, hardware, software o datos.

Notas de la fuente:

- `Operaciones` no pertenece al vocabulario: se elimino por completo.
- Cualquier variante con tilde, en minusculas o con otra capitalizacion se
  rechaza: solo valen las cadenas exactas de la lista anterior.

## 2. Verdad multietiqueta

Fuente: `docs/anexo_f_corpus.md`.

La verdad de un caso es multietiqueta: su conjunto de sectores de verdad es
`{sector_asignado} ∪ sectores_adicionales`.

Invariantes:

1. Existe un unico sector principal (`sector_asignado`).
2. Los sectores adicionales (`sectores_adicionales`) no repiten al sector
   principal.
3. Todo valor, tanto del principal como de los adicionales, pertenece al conjunto
   canonico de la seccion 1.

## 3. Regla de negocio RN-CL-01

Fuente: `knowledge-base/05_reglas_de_negocio.md`, regla RN-CL-01.

Todo incidente se clasifica en exactamente un sector principal y, de forma
opcional, en sectores adicionales (verdad multietiqueta), siempre entre los cinco
sectores canonicos de la seccion 1.

## 4. Etiqueta primaria en casos multicategoria

Fuente: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex`, linea 53.

Los casos con pertenencia simultanea a mas de un sector (multicategoria) se
conservan y se les asigna una etiqueta primaria como sector responsable. Es decir,
cuando un caso admite mas de un sector, se le asigna un unico sector principal
responsable (la etiqueta primaria); los sectores restantes se registran como
adicionales.

## 5. Uso: como procede el etiquetador

Para cada caso, el etiquetador asigna:

1. Exactamente un sector principal: una de las cinco cadenas canonicas de la
   seccion 1.
2. Opcionalmente, sectores adicionales: una o mas de las cinco cadenas canonicas,
   separadas por `|` y sin espacios alrededor (`A|B`, nunca `A | B`). Si no hay
   adicionales, la lista se deja vacia. Los adicionales nunca repiten el sector
   principal.

Reglas de escritura:

- Usar las cadenas exactas, sensibles a mayusculas y sin tildes (seccion 1).
- No usar sectores fuera del conjunto canonico.
- Este codebook es el unico documento de criterio, esta congelado y es identico
  para los dos etiquetadores.

## 6. Congelado

El codebook se congela antes de etiquetar: una vez entregado, no se modifica. Si
se detecta un error, se documenta y se reinicia el etiquetado de ambos
etiquetadores.
