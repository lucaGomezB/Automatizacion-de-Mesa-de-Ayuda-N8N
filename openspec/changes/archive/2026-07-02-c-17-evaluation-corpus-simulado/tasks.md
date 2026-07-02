## Tasks: evaluation-corpus-simulado

### Fase 1: Infraestructura

- [x] 1.1 Crear directorio `evaluation/data/` si no existe
- [x] 1.2 Crear `evaluation/data/README.md` con documentacion del corpus

### Fase 2: Generacion del corpus

- [x] 2.1 Escribir `evaluation/generate_corpus.py` con templates y logica de generacion
- [x] 2.2 Ejecutar script y generar `evaluation/data/corpus_evaluacion.csv` con 200 casos
- [x] 2.3 Verificar distribucion: 82 Sistemas, 64 Operaciones, 54 Soporte Tecnico

### Fase 3: Validacion

- [x] 3.1 Ejecutar tests del framework de evaluacion para verificar que el corpus carga sin errores
- [x] 3.2 Escribir test de validacion especifico del corpus generado (distribucion, columnas, categorias)
- [x] 3.3 Verificar que `corpus.cargar_corpus()` carga los 200 casos sin excepciones
