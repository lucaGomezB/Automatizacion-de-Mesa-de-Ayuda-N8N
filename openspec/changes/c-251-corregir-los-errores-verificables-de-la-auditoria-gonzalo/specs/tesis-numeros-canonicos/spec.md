## ADDED Requirements

### Requirement: Dirección correcta de la asimetría de alcance (E4 de c-251)

La Discusión (`08-discusion.tex:22`) SHALL separar el componente de INSTRUMENTO del de ALCANCE al
enumerar la primera explicación rival de la reducción de tiempo, y MUST NOT fundirlos bajo un único
"favorece al segundo". El componente de INSTRUMENTO (cronómetro humano en vivo, que infla el manual)
sí favorece al automatizado; el de ALCANCE es conservador: el brazo manual mide clasificación pura
(alcance ESTRECHO, sub-contado) y el automatizado mide de extremo a extremo (alcance AMPLIO), de modo
que la línea base manual queda sub-estimada y la reducción reportada es una COTA INFERIOR que
SUB-ESTIMA la ventaja del automatizado (lo "perjudica" en el número declarado). Esta lectura SHALL
ser consistente con la octava amenaza (`04-marco-metodologico.tex:131`: "la dirección y la magnitud
de esa diferencia de alcance no se estimaron").

#### Scenario: Instrumento y alcance separados

- **WHEN** se lee `08-discusion.tex:22`
- **THEN** la asimetría de instrumento y la de alcance se enuncian por separado, sin un "favorece al segundo" que las unifique

#### Scenario: Dirección del alcance correcta

- **WHEN** se lee el pasaje de la asimetría de alcance
- **THEN** declara que la asimetría de alcance es conservadora (sub-estima la ventaja del automatizado, reducción reportada como cota inferior), y remite a la octava amenaza (`04:131`)

#### Scenario: Sin cifra nueva de la cotización del alcance

- **WHEN** se ejecuta `rg -n "cota inferior|sub-estima|subestima|magnitud.*alcance" "docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex"`
- **THEN** no aparece un número nuevo que cuantifique la asimetría de alcance; la dirección se declara y la magnitud queda "no estimada"

### Requirement: Re-etiquetado de la sensibilidad de -10 s en el Anexo K (E5 de c-251)

El Anexo K (`12-anexos.tex:354`) y los pasajes que lo enlazan (`04-marco-metodologico.tex:16`,
`08-discusion.tex:22/24`) SHALL re-etiquetar los descuentos del análisis de sensibilidad sin presentar
el `-10 s` como "redondeo". El `-5 s` SHALL etiquetarse como cota de redondeo: el redondeo es hacia
arriba a múltiplos de 5 s (199/200 valores múltiplos de 5 s) y la inflación máxima por caso es menor
que 5 s. El `-10 s` SHALL etiquetarse como el escenario que el tribunal pidió cuantificar cuando la
descripción aún incluía el componente "carga ~10 s" (retirado por C-02), no como descuento por
redondeo. Los valores 56,6 s / 51,6 s y 68,6 % / 65,6 % SHALL permanecer sin cambio; solo cambian la
etiqueta y su justificación.

#### Scenario: -5 s etiquetado como cota de redondeo

- **WHEN** se lee `12-anexos.tex:354` y `04-marco-metodologico.tex:16`
- **THEN** el `-5 s` se justifica por el redondeo hacia arriba a múltiplos de 5 s, con inflación máxima por caso menor que 5 s

#### Scenario: -10 s no etiquetado como redondeo

- **WHEN** se lee `12-anexos.tex:354`, `04-marco-metodologico.tex:16` y `08-discusion.tex`
- **THEN** el `-10 s` NO se presenta como descuento por redondeo; se etiqueta como el escenario solicitado por el tribunal sobre la "carga ~10 s" ya retirada (C-02)

#### Scenario: Valores de la sensibilidad sin cambio

- **WHEN** se ejecuta `rg -n "56,6|51,6|68,6|65,6" "docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex" "docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex"`
- **THEN** los valores de la sensibilidad permanecen idénticos (5 s → 56,6 s / 68,6 %; 10 s → 51,6 s / 65,6 %), y solo cambian la etiqueta y la justificación
