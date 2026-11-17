# evaluation/data/canario/

Conjunto canario fijo y versionado del monitoreo de la deriva (c-227), su linea de
base congelada y los reportes del job. Es una **senal operativa**: no mide de nuevo
la tesis, no cambia ningun numero canonico y no reemplaza ninguna medicion.

## Procedencia

**Insumo tecnico sin referencia acreditada** (c-235; decisión OQ6): su procedencia no se
acredita como registro primario de una organización. Proviene del corpus **independiente**
de la (hoy retirada) validación fuera de muestra
(`evaluation/data/campana/corpus_independiente.json`, retirado del repositorio público por
c-240); sus textos permanecen copiados en los artefactos del canario. Es disjunto del
corpus de ajuste de 200 casos. NO apto para ajustar, calibrar ni seleccionar el vocabulario,
el prompt ni el punto de operacion. Ids `I001..I103`.

## Composicion estable

- Casos: **103**.
- Sectores: Seguridad Informatica 21; Soporte Tecnico Hardware 40; Soporte Tecnico
  Software 24; Bases de Datos 13; Sistemas 5.
- Canales: Telefono 45; Correo 34; Formulario Web 24.

## Archivos

| Archivo | Rol |
|---|---|
| `canario.json` | Conjunto canario fijo (103 casos, ids `I*`). |
| `canario_predicciones.json` | Predicciones versionadas del clasificador sobre el canario (modo offline). |
| `canario_baseline.json` | Linea de base congelada: metricas, identidad y pisos. |
| `canario.SHA256SUMS.txt` | Huellas SHA-256 de los tres artefactos anteriores. |
| `reportes/` | Reportes fechados del job (`reporte_<fecha>.md`). |

## Linea de base y pisos (delta = 0.05)

| Metrica | Linea de base | Piso |
|---|---|---|
| exactitud estricta | 0.8446601941747572 | 0.7946601941747572 |
| F1 macro | 0.7446560846560847 | 0.6946560846560846 |

Identidad de la linea de base: proveedor `gemini`, modelo `gemini-3.6-flash`.
Los pisos viven en `Settings` (`monitoring_*_floor`) y son sobrescribibles por
entorno sin recompilar.

## Ejecutar el job

```bash
# Reproduccion offline por defecto (sin proveedor, sin costo):
PYTHONPATH=App/Backend python -m evaluation.monitoreo.monitor_deriva

# Corrida fresca (paga): solo bajo demanda y con confirmacion:
PYTHONPATH=App/Backend python -m evaluation.monitoreo.monitor_deriva --fresh --confirm-paid
```

Procedimiento operativo, cadencia, lectura de la deriva y fallback:
`docs/operational-guide.md` seccion 12.
