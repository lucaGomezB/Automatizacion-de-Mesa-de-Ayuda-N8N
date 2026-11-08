## 1. Gate de verificacion previa (read-only)

- [x] 1.1 Confirmar la ausencia del valor en el cuerpo: `rg -n "0,5307|0,4407|0,6111|0,9388" "docs/Tesis/v10 (IA)/paper/sections/"` no devuelve coincidencias. Verificacion: salida vacia.
- [x] 1.2 Confirmar los valores fijos en el memo: leer `docs/Tesis/Correcciones/numeros-canonicos.md`, Seccion 3.14, rama (b') "estimable" (`0,5307`; IC `[0,4407; 0,6111]`, `B = 2000`, semilla `20261021`; cobertura `0,9388`; casos `147`/`138`; limitacion del denominador). Verificacion: coincidencia literal. NO se edita el memo.

## 2. Reporte del valor en resultados

- [x] 2.1 En `07-resultados.tex`, `subsec:reduccion-intervencion`, inmediatamente despues de la proporcion de casos y su desglose, agregar una oracion que reporte la proporcion del tiempo con estimacion `0{,}5307`, IC bootstrap `[0{,}4407; 0{,}6111]` (declarando `B = 2000` y la semilla `20261021`), cobertura `0{,}9388` y tamanos `147` con intervencion / `138` con duracion completa. Verificacion: `rg -n "0,5307"` sobre el archivo devuelve la oracion.
- [x] 2.2 Declarar en la misma oracion (o la siguiente) la limitacion del denominador (tiempo de registro automatizado mas duracion de la intervencion, no el tiempo total de atencion). Verificacion: la limitacion figura junto al valor.
- [x] 2.3 Verificar la cita literal contra el memo (coma decimal, sin redondeo) y que el valor aparece una sola vez en `sections/*.tex`. Verificacion: comparacion literal y `rg -c`.

## 3. Desambiguacion del anuncio metodologico

- [x] 3.1 En `04-marco-metodologico.tex` (parrafo de metricas, linea 69) precisar el denominador de la proporcion del tiempo y remitir con `\autoref{subsec:reduccion-intervencion}`. Verificacion: el parrafo remite y no enuncia ningun valor.
- [x] 3.2 Coordinar con c-184 (recorte de paginas): si c-184 ya reescribio ese parrafo, aplicar la clausula sobre el texto resultante sin reintroducir texto recortado. Verificacion: ausencia de conflicto de merge semantico.

## 4. Propiedades y verificacion

- [x] 4.1 Verificar que ningun valor canonico de la campana 2026-10 cambia (`61,6 s`, `17,76 s`, `73,5 %`, `0,6508`, kappa `0,87`). Verificacion: `rg` de control antes/despues, sin diferencias.
- [x] 4.2 Registrar el impacto de paginas del change (si agrega) para el cierre de release. Verificacion: conteo declarado en el registro de correcciones.
- [x] 4.3 `openspec validate c-185-reportar-la-proporcion-de-tiempo-de-la-campana --strict --no-interactive` en verde. Verificacion: salida sin errores.
