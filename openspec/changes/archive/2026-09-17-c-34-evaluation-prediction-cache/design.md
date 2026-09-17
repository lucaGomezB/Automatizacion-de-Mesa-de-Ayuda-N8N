## Context

`evaluation/run_evaluation.py` expone `main_con_corpus_real()` como punto de entrada testeable. Esta funcion siempre llama a `evaluar_corpus(corpus, classifier)`, que itera sobre todos los casos e invoca `classifier.classify()` uno a uno. Con el corpus real (~200 casos) y HybridClassifier, cada llamada puede incurrir en un costo de inferencia Gemini. El archivo `predicciones.json` ya se escribe al final de cada corrida via `guardar_predicciones()`, pero no se lee en corridas posteriores. El punto de entrada CLI es `main()` en el mismo modulo (invocado como `python -m evaluation.run_evaluation`).

Ver proposal.md para la motivacion completa.

## Goals / Non-Goals

**Goals:**
- Evitar llamadas al clasificador cuando el corpus y la config no cambiaron (cache hit).
- Invalidar el cache automaticamente ante cualquier cambio en el corpus o la version del clasificador.
- Proveer un flag de opt-out (`--force` / `--no-cache`) para corridas incondicionales.
- Mantener el contrato existente de `evaluar_corpus()` y `main_con_corpus_real()` sin ruptura de tests.
- Fijar la version de la imagen N8N para evitar roturas silenciosas en `docker compose pull`.
- Limpiar `App/Backend/.env.example` de variables Twilio que el backend no usa.

**Non-Goals:**
- Cache distribuido o persistencia fuera del sistema de archivos local.
- Cache parcial (reanudacion a mitad de corpus); la granularidad es corpus completo.
- Implementar la integracion de doble transcripcion Twilio en el backend (A3, diferido).
- Cambiar la logica del clasificador hibrido o sus parametros.

## Decisions

### D1 — Identificacion del corpus: hash SHA-256 del archivo JSON

**Decision**: calcular `hashlib.sha256` del contenido binario del archivo de corpus y almacenarlo en `cache_meta.corpus_hash`.

**Razon**: el hash detecta cualquier cambio de contenido (inclusion de nuevos casos, edicion de descripciones, cambio de etiquetas) sin necesidad de parsear el JSON. Es O(tamanio del archivo), determinista y portable.

**Alternativa descartada**: hash del contenido parseado (lista de casos). Requiere serializar de vuelta a bytes con orden de claves garantizado; mas fragil y no detecta cambios en campos que el parser ignora.

**Alternativa descartada**: comparar solo `corpus_count`. No detecta cambios en el contenido de los casos (editados pero misma cantidad).

### D2 — Clave de version del clasificador: string constante por tipo

**Decision**: `classifier_version` se obtiene del atributo `CACHE_VERSION` del clasificador si existe, o del nombre del tipo (`type(classifier).__name__`) como fallback. Para FakeClassifier el valor sera `"FakeClassifier"`. Para HybridClassifier se espera que defina `CACHE_VERSION = "hybrid-v1"` (o similar).

**Razon**: evitar acoplamiento entre el runner de evaluacion y los internos del clasificador. El clasificador declara su propia version de cache; si no la declara, el nombre del tipo es un proxy razonable que cambia si se renombra la clase.

**Alternativa descartada**: leer la version del modelo Gemini desde config. Introduce una dependencia del runner al modulo `app.config`, lo que rompe el aislamiento del modulo de evaluacion.

**Alternativa descartada**: hash de los pesos/parametros del clasificador. Impracticable para clasificadores que llaman a APIs externas.

### D3 — Formato de `predicciones.json`: campo `cache_meta` de nivel superior

**Decision**: el JSON pasa de ser un arreglo plano a ser un objeto con dos claves: `cache_meta` (metadata) y `predictions` (el arreglo actual).

**Razon**: compatibilidad hacia atras — si `cache_meta` esta ausente (archivos generados por versiones anteriores), el runner lo trata como invalido y re-ejecuta, sin romper. El campo `predictions` mantiene la misma estructura que el arreglo anterior, por lo que `cargar_predicciones()` solo necesita adaptarse para leer desde `data["predictions"]`.

**Estructura de `cache_meta`**:
```json
{
  "cache_meta": {
    "corpus_hash": "<sha256-hex>",
    "corpus_count": 200,
    "classifier_version": "FakeClassifier",
    "generated_at": "2026-09-17T18:00:00Z"
  },
  "predictions": [ ... ]
}
```

**Alternativa descartada**: archivo separado `predicciones.cache.json`. Complica la gestion de dos archivos y el riesgo de inconsistencia entre ellos.

### D4 — Integracion del cache en `main_con_corpus_real()` sin alterar `evaluar_corpus()`

**Decision**: la logica de cache (verificar, cargar, invalidar) vive en `main_con_corpus_real()` como paso previo a la llamada de `evaluar_corpus()`. Las funciones `evaluar_corpus()`, `guardar_predicciones()` y `cargar_predicciones()` no cambian su firma ni comportamiento.

**Razon**: `evaluar_corpus()` es una funcion pura que los tests existentes usan directamente; no contaminarla con estado de cache preserva el diseno D1 original (inyeccion del clasificador). Los tests del cache pueden ejercer `main_con_corpus_real()` directamente con FakeClassifier.

### D5 — Flag CLI: `--force` / `--no-cache` via `argparse`

**Decision**: el punto de entrada `main()` se refactoriza para usar `argparse` con un argumento `--force` (alias `--no-cache`). El flag se pasa a `main_con_corpus_real()` como parametro `force: bool = False`.

**Razon**: `argparse` es stdlib, sin dependencias nuevas. El parametro `force` en la firma de `main_con_corpus_real()` permite testear el opt-out sin necesidad de manipular `sys.argv`.

### D6 — A2: Pin de imagen N8N a `n8nio/n8n:2.11.2`

**Decision**: reemplazar `n8nio/n8n:latest` por `n8nio/n8n:2.11.2` en `docker-compose.yml`. Actualizar el comentario de la linea para indicar la version fijada y la razon del pin.

**Razon**: la version 2.11.2 es la que esta deployada y validada con el workflow del proyecto. `latest` puede avanzar a una version incompatible sin aviso, rompiendo el workflow silenciosamente en el siguiente `docker compose pull`. El pin garantiza reproducibilidad del entorno.

**Nota**: el `openspec/config.yaml` registra `N8N 1.62` como version del stack. Ese valor se refiere a la version de la imagen disponible en el momento de la documentacion inicial; el valor correcto observado en produccion es 2.11.2. Actualizar `config.yaml` queda como tarea de mantenimiento separada.

### D7 — A4: Comentar variables Twilio en `.env.example` (opcion b)

**Decision**: comentar las cuatro variables `TWILIO_*` (lineas 36-39 de `App/Backend/.env.example`) en lugar de eliminarlas. Agregar un comentario explicativo que indique que esas credenciales pertenecen a la configuracion del trigger de N8N, no al backend FastAPI.

**Razon**: el archivo `.env.example` debe ser una referencia completa del entorno de despliegue. Eliminar completamente las variables podria confundir a operadores que intentan configurar el canal telefonico y no saben donde colocar las credenciales. Comentarlas con una nota directiva es mas informativo.

**Alternativa descartada**: eliminar completamente (opcion a). Pierde la documentacion de que existen esas variables y que pertenecen a N8N.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|--------|-----------|
| Hash SHA-256 del archivo JSON puede ser lento en corpus muy grandes (>10 MB) | El corpus de la tesis (~200 casos) es del orden de kilobytes; el overhead es despreciable. |
| `cargar_predicciones()` con el nuevo formato rompe si un caller externo espera arreglo plano | La funcion se actualiza para leer `data["predictions"]`; no hay callers externos conocidos fuera de la suite de evaluacion. |
| Pin de N8N a 2.11.2 puede quedar desactualizado si se decide actualizar la version | El pin debe revisarse manualmente al planificar upgrades de N8N; el comentario en docker-compose.yml lo documenta. |
| `CACHE_VERSION` ausente en HybridClassifier hace que la clave sea el nombre del tipo | Si la clase se renombra sin actualizar CACHE_VERSION, el cache se invalida innecesariamente (corrida extra paga). Mitigacion: agregar `CACHE_VERSION` a HybridClassifier como tarea de seguimiento. |

## Open Questions

Ninguna. Todas las decisiones necesarias para las specs, el enfoque y el desglose de tareas han sido resueltas arriba.
