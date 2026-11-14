# Brazo «Gemini solo» frente al hibrido: contraste de la hipotesis de eficiencia (c-215)

Las cifras de este analisis son aditivas: no reemplazan ningun numero canonico de la tesis ni el clasificador de produccion. Comparan al hibrido congelado con el brazo «Gemini solo» (una sola corrida, temperatura 0,3), pareado caso a caso.

## Veredicto prerregistrado (bloque primario: fuera de muestra)

**no concluyente**: la no inferioridad en exactitud es indeterminada con el ahorro cumplido.

- Margen de no inferioridad: 0.05; ahorro material si el limite superior del IC de las razones de costo y de llamadas es menor que 0.9.
- Componente de exactitud: indeterminado; componente de eficiencia: cumplido; tasa de fallos del brazo: 0.000.

## Control de deriva (casos que H ya escalo)

- Dentro de la muestra: concordancia con la prediccion cacheada de H 64/69 = 0.9275 [0.8413; 0.9687] (umbral 0.9); casos que H escalo: 69; excluidos por fallo tecnico: 0.
- Fuera de muestra: concordancia con la prediccion cacheada de H 34/34 = 1.0000 [0.8985; 1.0000] (umbral 0.9); casos que H escalo: 34; excluidos por fallo tecnico: 0.
- Pooled (ambos bloques): concordancia con la prediccion cacheada de H 98/103 = 0.9515 [0.8914; 0.9791] (umbral 0.9); casos que H escalo: 103; excluidos por fallo tecnico: 0.

La concordancia se calcula sin los casos que H escalo y cuyo registro vigente del brazo es un fallo tecnico (sin respuesta del modelo): no hay prediccion nueva que comparar.

Lectura: sin senal de inestabilidad entre la nueva corrida y la cache de H en los casos que H ya escalo (este control no separa deriva del modelo de azar de muestreo a temperatura 0,3).

## Desviaciones del prerregistro

Fecha de la desviacion: 2026-11-13. El ejecutor se extendio con el reintento de los fallos tecnicos del proveedor (indisponibilidad o transporte, sin respuesta del modelo). Definicion estricta: registro en fallback con error de indisponibilidad o transporte y sin tokens (sin respuesta del modelo); las respuestas invalidas del modelo NO son fallos tecnicos.

- Casos cuyo primer registro fue un fallo tecnico: 112 (dentro de la muestra: 112; fuera de muestra: 0).
- Casos reintentados por fallo tecnico: 112 (dentro de la muestra: 112; fuera de muestra: 0).
- Casos que siguen fallidos: 0 (dentro de la muestra: 0; fuera de muestra: 0).
- Llamadas con respuesta del modelo: 303 (tope 400); intentos sin respuesta: 112; intentos totales: 415 (cinturon 600).

La decision de reintentar los fallos tecnicos se tomo DESPUES de ver los resultados del bloque primario y del bloque secundario contaminado: es una amenaza a la validez que se declara.
No cambian la regla de decision, el margen de no inferioridad, el umbral de eficiencia, el tope de fallos ni el bloque primario.
Contabilidad del tope: el tope de 400 se aplica a las llamadas que obtuvieron respuesta del modelo; los intentos que fallaron antes de obtener respuesta se cuentan y se informan aparte, y un cinturon de seguridad acota los intentos totales en 600.
El bloque primario (fuera de muestra) no tuvo fallos tecnicos: su veredicto se obtuvo sin reintentos y no depende de ellos.

## Procedencia de la corrida

Modelo gemini-3.6-flash, temperatura 0.3, google-genai 2.34.0, commit f7b1582, generada el 2026-11-13T16:55:34.554737+00:00; una sola corrida (mas el reintento de fallos tecnicos declarado abajo); intentos acumulados en el cache: 415 (tope prerregistrado de respuestas: 400). Precios (USD por millon de tokens de entrada/salida, parametro declarado): {"introductorio": {"entrada": 0.75, "salida": 3.75}, "estandar": {"entrada": 1.5, "salida": 7.5}}.

## Fuera de muestra (primario, referencia consenso E3/E4)

Casos: 103.

| Brazo | Exactitud estricta (Wilson) | Exactitud laxa (Wilson) | Macro-F1 |
|---|---|---|---|
| Hibrido (H) | 87/103 = 0.8447 [0.7625; 0.9021] | 90/103 = 0.8738 [0.7960; 0.9247] | 0.7447 |
| Gemini solo (L) | 90/103 = 0.8738 [0.7960; 0.9247] | 93/103 = 0.9029 [0.8304; 0.9464] | 0.7665 |

| | L acierta | L falla |
|---|---|---|
| H acierta | 84 | 3 |
| H falla | 6 | 10 |

- McNemar exacta bilateral: p = 0.5078 (corregida por continuidad: p = 0.5050; criterio de stats.py: exacto). Una diferencia no significativa se lee «no se detecto diferencia», nunca «equivalentes».
- Diferencia de exactitudes (H - L): -0.0291, IC 95 % bootstrap pareado [-0.0874; 0.0291] (10000 remuestreos, semilla 20261021).

### Eficiencia (H imputado con los tokens y la latencia de L en los casos que escalo)

- Llamadas: L = 103 (1.000 por caso); H = 34 (0.330 por caso); razon H/L = 0.3301 [0.2427; 0.4175].
- Tokens: L = 80011 de entrada y 1929 de salida; H = 26402 y 628. Casos con tokens supuestos (la API no los devolvio): 0.
- Costo estimado (introductorio): L = USD 0.0672; H = USD 0.0222.
- Costo estimado (estandar): L = USD 0.1345; H = USD 0.0443.
- Razon de costo H/L: 0.3295 [0.2421; 0.4176] (la razon no depende del escenario: ambos precios son proporcionales).
- Latencia media por caso: L = 1076.3 ms; H = 357.3 ms; diferencia L - H = 719.0 ms [605.6; 838.9]. Latencia de clasificacion del lado del cliente, medida desde la maquina de los autores; no es tiempo de extremo a extremo. Para el hibrido se imputa la latencia de Gemini del mismo caso donde escalo y 0 ms donde resolvieron las reglas (cota inferior: las reglas tardan milisegundos). No entra en la regla de decision.
- Casos que H escalo: 34; fallbacks o errores de L: 0 (0.000).

### Sensibilidad H* (hibrido recompuesto)

H*: prediccion cacheada de H donde las reglas resolvieron y prediccion NUEVA de L donde H escalo; aisla el enrutamiento del ruido o la deriva del modelo.

- Exactitud estricta de H*: 87/103; diferencia H* - L = -0.0291 [-0.0874; 0.0291]; McNemar p = 0.5078; regla aplicada a H*: no concluyente (no cambia el veredicto).

Regla prerregistrada aplicada a este bloque: exactitud indeterminado, eficiencia cumplido -> **no concluyente**.

## Dentro de la muestra (secundario; optimista para H, no es prueba limpia)

Casos: 200.

| Brazo | Exactitud estricta (Wilson) | Exactitud laxa (Wilson) | Macro-F1 |
|---|---|---|---|
| Hibrido (H) | 147/200 = 0.7350 [0.6698; 0.7913] | 179/200 = 0.8950 [0.8448; 0.9303] | 0.5207 |
| Gemini solo (L) | 136/200 = 0.6800 [0.6125; 0.7407] | 173/200 = 0.8650 [0.8107; 0.9055] | 0.4559 |

| | L acierta | L falla |
|---|---|---|
| H acierta | 124 | 23 |
| H falla | 12 | 41 |

- McNemar exacta bilateral: p = 0.0895 (corregida por continuidad: p = 0.0910; criterio de stats.py: corregido). Una diferencia no significativa se lee «no se detecto diferencia», nunca «equivalentes».
- Diferencia de exactitudes (H - L): 0.0550, IC 95 % bootstrap pareado [0.0000; 0.1150] (10000 remuestreos, semilla 20261021).

### Eficiencia (H imputado con los tokens y la latencia de L en los casos que escalo)

- Llamadas: L = 200 (1.000 por caso); H = 69 (0.345 por caso); razon H/L = 0.3450 [0.2800; 0.4100].
- Tokens: L = 153934 de entrada y 3812 de salida; H = 53177 y 1327. Casos con tokens supuestos (la API no los devolvio): 0.
- Costo estimado (introductorio): L = USD 0.1297; H = USD 0.0449.
- Costo estimado (estandar): L = USD 0.2595; H = USD 0.0897.
- Razon de costo H/L: 0.3457 [0.2806; 0.4120] (la razon no depende del escenario: ambos precios son proporcionales).
- Latencia media por caso: L = 1282.8 ms; H = 488.6 ms; diferencia L - H = 794.2 ms [706.3; 879.6]. Latencia de clasificacion del lado del cliente, medida desde la maquina de los autores; no es tiempo de extremo a extremo. Para el hibrido se imputa la latencia de Gemini del mismo caso donde escalo y 0 ms donde resolvieron las reglas (cota inferior: las reglas tardan milisegundos). No entra en la regla de decision.
- Casos que H escalo: 69; fallbacks o errores de L: 0 (0.000).

### Sensibilidad H* (hibrido recompuesto)

H*: prediccion cacheada de H donde las reglas resolvieron y prediccion NUEVA de L donde H escalo; aisla el enrutamiento del ruido o la deriva del modelo.

- Exactitud estricta de H*: 148/200; diferencia H* - L = 0.0600 [0.0100; 0.1150]; McNemar p = 0.0428; regla aplicada a H*: sostenida (no cambia el veredicto).

Regla prerregistrada aplicada a este bloque: exactitud no inferior, eficiencia cumplido -> **sostenida**. (informativo; solo decide el bloque primario)
