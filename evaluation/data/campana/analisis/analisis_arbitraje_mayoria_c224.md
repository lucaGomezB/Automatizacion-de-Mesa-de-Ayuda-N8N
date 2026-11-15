# Acotacion del arbitraje por mayoria (c-224)

Solo lectura, offline y determinista; sin red ni Gemini. Registro aditivo: no reemplaza ningun valor de las secciones 3.1 a 3.34.

## Coincidencia estructural

- La regla vigente coincide con la mayoria de {E3, E4, E5} en 200 de 206 casos.
- Identidad: 142 + 58 = 200.

## Casos sin mayoria

- I033: E3=Soporte Tecnico Software; E4=Sistemas; E5=Soporte Tecnico Hardware; prediccion=Sistemas; referencia=Soporte Tecnico Hardware.
- I042: E3=Seguridad Informatica; E4=Sistemas; E5=Bases de Datos; prediccion=Soporte Tecnico Software; referencia=Bases de Datos.
- I056: E3=Soporte Tecnico Software; E4=Sistemas; E5=Seguridad Informatica; prediccion=Soporte Tecnico Software; referencia=Seguridad Informatica.
- I130: E3=Soporte Tecnico Software; E4=Sistemas; E5=Seguridad Informatica; prediccion=Sistemas; referencia=Seguridad Informatica.
- I194: E3=Bases de Datos; E4=Sistemas; E5=Soporte Tecnico Hardware; prediccion=Sistemas; referencia=Soporte Tecnico Hardware.
- I198: E3=Sistemas; E4=Soporte Tecnico Software; E5=Seguridad Informatica; prediccion=Soporte Tecnico Software; referencia=Seguridad Informatica.

## Rango de exactitud

- Minimo vigente: 142/206 (0,6893).
- Maximo con reasignacion: 147/206 (0,7136).
- Casos reasignables: I033, I056, I130, I194, I198.
- Casos no reasignables: I042.

## Metricas por clase bajo extremos

| Clase | Precision vigente | Sensibilidad vigente | F1 vigente | Precision maximo | Sensibilidad maximo | F1 maximo |
|---|---|---|---|---|---|---|
| Bases de Datos | 0,7778 | 0,8750 | 0,8235 | 0,7778 | 0,8750 | 0,8235 |
| Seguridad Informatica | 0,6452 | 0,6250 | 0,6349 | 0,6452 | 0,6897 | 0,6667 |
| Sistemas | 0,7045 | 0,5082 | 0,5905 | 0,7727 | 0,5312 | 0,6296 |
| Soporte Tecnico Hardware | 0,7857 | 0,8627 | 0,8224 | 0,7857 | 0,8980 | 0,8381 |
| Soporte Tecnico Software | 0,5789 | 0,7174 | 0,6408 | 0,6140 | 0,7292 | 0,6667 |

- Macro-F1 vigente: 0,7024.
- Macro-F1 maximo: 0,7249.

## Anclajes verificados

- Coincidencia: 200/206.
- Sin mayoria: 6 casos.
- Arbitrados: 64.
- Exactitud estricta: 142/206.
- Maximo: 147/206.

