## 1. Test offline de integridad de las tablas SHA-256 (ECM-015) — RED

- [x] 1.1 En `evaluation/tests/test_campana.py`, escribir un test que lea `evaluation/data/campana/README.md`, ubique las tablas `| Archivo | SHA-256 |`, resuelva cada archivo relativo al directorio del README y compare el hash declarado con el real; verificar que FALLA nombrando `registro_sujetos.csv` (declara `f7a5653e...`, el real es `ab17eb2b...`). RED confirmado.
- [x] 1.2 Agregar los casos de borde del mismo test (triangulación): una fila con valor `pendiente` se omite, una fila cuyo archivo no existe se omite, y una fila con hash correcto pasa; verificar que los casos de omisión pasan y que el caso de hash correcto pasa en aislamiento.

## 2. Correcciones del README de campaña — GREEN

- [x] 2.1 En `evaluation/data/campana/README.md`, corregir el SHA-256 declarado de `registro_sujetos.csv` en la tabla "SHA-256 por archivo" a `ab17eb2b6e660b78d206d130c21fac06739ba5512d2ac37d09cf532c2a3d36da`; verificar que el test de 1.1 pasa y que `sha256sum evaluation/data/campana/registro_sujetos.csv` coincide con la fila.
- [x] 2.2 Normalizar la línea 113 a UNA sola línea con el `\r` ESCAPADO (`sed -i 's/\r$//' <archivo>`), sin CR literal ni salto intermedio, escribiendo con fin de línea LF; verificar con `sed -n '113p' evaluation/data/campana/README.md` que la oración queda completa en una línea y con `grep -c $'\r' evaluation/data/campana/README.md` que no hay bytes CR.

## 3. Verificación y control de alcance

- [x] 3.1 Correr el test offline en verde: `cd evaluation && pytest tests/test_campana.py -q`; confirmar que toda la suite del archivo pasa y que el test nuevo falla si se revierte la fila de `registro_sujetos.csv` al hash viejo (chequeo manual del poder de detección).
- [x] 3.2 Confirmar el alcance: `git status --short` muestra solo `evaluation/data/campana/README.md`, `evaluation/tests/test_campana.py` y los artefactos del change bajo `openspec/changes/c-199-.../`; ningún cambio en `App/`, `n8n/`, `auditorias/`, tesis ni otros artefactos de `evaluation/data/campana/`.
- [x] 3.3 Correr `openspec validate c-199-limpiar-residuos-del-remapeo-de-citas --strict` y confirmar que pasa.
