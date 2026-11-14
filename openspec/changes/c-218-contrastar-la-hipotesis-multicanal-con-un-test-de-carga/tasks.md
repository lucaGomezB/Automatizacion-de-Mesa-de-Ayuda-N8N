# Tasks: Contrastar la hipótesis multicanal con un test de carga

Convenciones: `T/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`; `S/` = `scripts/load_test/`. El change es ADITIVO: no cambia ningún número canónico de `3.1`-`3.28`, ni el clasificador, ni el corpus, ni la referencia, ni el gate, ni `docker-compose.yml`/`n8n/workflow.json`. NO se emite ninguna llamada paga (Gemini ni Twilio). `CHANGES.md` lo reconcilia el orquestador, fuera de estas tareas. La sección nueva del memo es la `3.29` (la `3.28` la ocupó c-217). TDD estricto sobre la lógica pura del arnés.

## 0. Preparación, prerregistro del criterio y red de seguridad

- [ ] 0.1 Confirmar el estado: `openspec validate c-218-contrastar-la-hipotesis-multicanal-con-un-test-de-carga --strict --no-interactive` en verde y `openspec status --change c-218-… --json` con `proposal`/`specs`/`design`/`tasks` presentes. Verificación: sin errores de validación.
- [ ] 0.2 Congelar en el commit de la propuesta las constantes del criterio (design D6): niveles `1/5/10/20`, 40 solicitudes/nivel, 3 repeticiones, techo `p95 ≤ 5000 ms`, tolerancia de throughput `10 %`, tasa de error `0`, control de escalado `p95(20)/p95(1) ≤ 20`. Verificación: las constantes figuran en `S/README.md` y en el reporte; ninguna se ajusta después de ver resultados.
- [ ] 0.3 Red de seguridad antes de tocar nada: `python -m pytest scripts/dry_run -q` y `python -m pytest scripts/corpus_ingest -q` desde la raíz; registrar el conteo base. Verificación: línea base anotada; las fallas preexistentes (si las hay) NO se corrigen aquí.

## 1. Arnés de carga (TDD)

- [ ] 1.1 RED — escribir la prueba de las funciones puras de métricas (`S/test_load_test.py`): `percentiles(latencias, [50, 95, 99])`, `throughput(n, segundos)`, `tasa_error(ok, total)` y `evaluar_criterio(niveles, constantes)` con casos conocidos (por ejemplo latencias `[100, 200, 300, 400]` → p50 `250`; un nivel con error → «no sostenida»; corrida incompleta → «no concluyente»). Verificación: `python -m pytest scripts/load_test/test_load_test.py -q` falla porque el módulo no existe.
- [ ] 1.2 GREEN — implementar el mínimo de `S/load_test.py` (percentiles por interpolación, throughput, tasa de error y `evaluar_criterio` de tres vías) para pasar 1.1. Verificación: la prueba pasa.
- [ ] 1.3 TRIANGULATE — agregar casos de borde: lista vacía, un único elemento, empates de percentil, todos los niveles OK («sostenida»), violación de throughput > 10 % («no sostenida»), techo de p95 excedido. Verificación: todos los casos pasan y el veredicto coincide con el cálculo manual.
- [ ] 1.4 RED/GREEN — prueba y luego implementación del armado de solicitudes: `payload(caso, origen_message_id)` produce un `IncidenteCreate` válido (descripción ≥ 10, `canal_origen_id` web = 2, `origen_message_id` único) y del cliente concurrente (disparo de N solicitudes con un pool de concurrencia fija, captura de latencia de cliente y del `latencia_e2e_ms` de la respuesta). Verificación: la prueba pasa con un servidor falso; `origen_message_id` es único por solicitud.
- [ ] 1.5 RED/GREEN — prueba y luego implementación del reporte: `escribir_reporte(...)` emite JSON y Markdown deterministas (LF, UTF-8 sin BOM) con commit, fecha UTC, versión de N8N, perfil, hash del fixture, constantes, métricas por nivel y veredicto; sin secretos. Verificación: dos corridas sobre las mismas métricas producen salidas idénticas byte a byte y la prueba comprueba la ausencia de la contraseña, el token y las claves.
- [ ] 1.6 REFACTOR — extraer constantes, mejorar nombres y eliminar duplicación sin cambiar comportamiento. Verificación: la suite de `S/` sigue en verde tras cada paso.
- [ ] 1.7 Crear `S/fixture_descripciones.json` con descripciones determinísticas por sector y la verificación de no escalada (`GET /api/v1/clasificaciones/incidente/{id}` etapa `deterministic`). Verificación: el fixture valida (≥ 10 caracteres por descripción) y el arnés aborta de forma ruidosa si un caso escaló.
- [ ] 1.8 Crear `S/compose.load-test.yml` (override de costo cero sobre `backend-corpus`: `GEMINI_API_KEY` ficticia, `COST_GUARD_BUDGET_USD=0`) y la afirmación previa dentro del contenedor. Verificación: el arnés aborta con código distinto de cero si la clave no es la ficticia o el presupuesto no es cero.
- [ ] 1.9 Documentar `S/README.md` (comando, meta del `Makefile`, entorno desechable, exclusiones de correo/telefonía, constantes). Verificación: un operador puede ejecutar el arnés siguiendo el README.

## 2. Entorno desechable y corrida

- [ ] 2.1 Levantar el perfil `corpus` con el override: `docker compose -f docker-compose.yml -f S/compose.load-test.yml --profile corpus up -d` (sin `-p`; nombre fijo). Verificación: `backend-corpus` (8001) y `n8n-corpus` (5679) sanos; la base `mesa_de_ayuda` no recibe escrituras.
- [ ] 2.2 Correr el arnés en los cuatro niveles sobre las dos capas y capturar el reporte: `python S/load_test.py --json-out evaluation/evidence/load_test_multicanal_<fecha>.json`. Verificación: el reporte incluye p50/p95/p99, throughput y tasa de error por nivel y capa, y el veredicto de tres vías.
- [ ] 2.3 Verificar costo cero: `0` escaladas (todas determinísticas), ninguna petición a Gemini y ninguna a Twilio. Verificación: la verificación de etapa del arnés pasa en todos los niveles y el log del backend no muestra llamadas al proveedor.
- [ ] 2.4 Verificar no destructividad: `git status` sin cambios en `docker-compose.yml`, `n8n/workflow.json` ni `App/**`. Verificación: `git diff --stat` solo muestra los archivos nuevos del change.

## 3. Prosa de la tesis sobre el texto vigente de `main`

- [ ] 3.1 `T/04-marco-metodologico.tex`: insertar el párrafo del protocolo del test de carga (niveles 1/5/10/20, métricas, criterio prerregistrado, entorno desechable de costo cero, exclusión de correo y telefonía). Verificación: el párrafo figura y no altera los párrafos vecinos.
- [ ] 3.2 `T/01-introduccion.tex:38`: reemplazar «La de integración multicanal no se somete a un contraste formal en este trabajo» por el estado real (capacidad contrastada con el test de carga; complejidad percibida no medida), sin mezclar el enunciado con el veredicto. Verificación: el enunciado declara la dimensión medida y remite al contraste.
- [ ] 3.3 `T/08-discusion.tex:10`: reemplazar «La hipótesis subsidiaria de integración multicanal tampoco se contrastó: no se midió la capacidad bajo carga concurrente» por el resultado medido con su veredicto y sus límites. Verificación: el pasaje declara «contrastada en su dimensión de capacidad» y no afirma que se midió la complejidad percibida.
- [ ] 3.4 `T/09-conclusiones.tex:6,39`: reemplazar «la de integración multicanal no se contrastó» y «no la contrastan: no se midieron la capacidad bajo carga concurrente ni la complejidad percibida» por el resultado medido, declarando que la complejidad percibida sigue sin instrumento. Verificación: ambos pasajes declaran el contraste de capacidad y su límite.
- [ ] 3.5 Verificar que no queda ninguna afirmación de la subsidiaria multicanal «sin contrastar» en `T/01`, `T/04`, `T/08` y `T/09`, ni sobreventa de la complejidad percibida. Verificación: `rg -n "no se contrastó|no se contrastaron|tampoco se contrastó|complejidad percibida"` sobre esas secciones solo devuelve el estado actualizado con su límite.

## 4. Registro aditivo

- [ ] 4.1 `C/numeros-canonicos.md`: agregar la sección `3.29` con el entorno, las constantes prerregistradas, las métricas por nivel de las dos capas, el veredicto y los límites, con procedencia por valor (ruta del reporte JSON) y estado. Verificación: la sección es la última, no cambia ningún valor de `3.1`-`3.28` y cada fila declara estado.
- [ ] 4.2 `C/dictamen-correcciones.md`: agregar una entrada de c-218 que documente el contraste de capacidad, el entorno desechable de costo cero, el veredicto y la decisión de no correr el camino pago. Verificación: la entrada existe, es aditiva y remite a `3.29`.
- [ ] 4.3 Verificar la coherencia memo↔prosa: cada cifra citada en `T/04`, `T/08` y `T/09` figura en `3.29` con su procedencia y estado. Verificación: muestreo de p50/p95, throughput, tasa de error y veredicto.

## 5. Validación y cierre

- [ ] 5.1 `openspec validate c-218-contrastar-la-hipotesis-multicanal-con-un-test-de-carga --strict --no-interactive` en verde. Verificación: sin errores ni advertencias.
- [ ] 5.2 Correr la suite offline del arnés: `python -m pytest scripts/load_test -q`. Verificación: todos los tests pasan sin red ni claves.
- [ ] 5.3 Confirmar costo cero y no destructividad: `git diff --stat` sin artefactos de corrida paga y sin cambios en `docker-compose.yml`/`n8n/workflow.json`/`App/**`. Verificación: solo se agregan `scripts/load_test/`, el reporte de evidencia y las ediciones de prosa/memo.
- [ ] 5.4 [AUTORES] Recompilar `main.pdf` y revisar la paginación del párrafo nuevo de metodología y de la tabla de carga. Verificación: compilación sin errores fatales ni referencias indefinidas.
