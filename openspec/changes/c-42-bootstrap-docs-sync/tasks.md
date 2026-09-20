## 1. RED — Red de seguridad estructural

- [ ] 1.1 Crear `App/Backend/tests/test_docs_bootstrap_sync.py` con un helper que localice la raiz del repo via `Path(__file__).resolve().parents[3]` (patron de `test_n8n_workflow.py`) y escriba un primer test que asserta que `README.md` contiene `JWT_SECRET_KEY`; ejecutar `cd App/Backend; pytest tests/test_docs_bootstrap_sync.py -q` y confirmar que FALLA (RED) porque el README aun no lo menciona
- [ ] 1.2 Agregar al mismo archivo el test que asserta que `README.md` contiene `UP_SKIP_COST_PREFLIGHT`; ejecutar el archivo y confirmar que ese caso tambien FALLA (RED)
- [ ] 1.3 Agregar el test que asserta que `docs/operational-guide.md` contiene `scripts/up.sh` (o `make up`) y `UP_SKIP_COST_PREFLIGHT`; ejecutar el archivo y confirmar RED

## 2. GREEN — README sincronizado con el bootstrap

- [ ] 2.1 Actualizar la seccion "Camino recomendado: un solo comando" de `README.md` (lineas 37-66) para que las condiciones de fallo nombren `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY` y `JWT_SECRET_KEY`; verificar releyendo la seccion que las tres variables aparecen
- [ ] 2.2 Documentar en esa misma seccion que el comando unico ejecuta el preflight de costo antes de tocar Docker, que un preflight fallido bloquea el arranque, y el bypass `UP_SKIP_COST_PREFLIGHT=1` con su advertencia audible; ejecutar `cd App/Backend; pytest tests/test_docs_bootstrap_sync.py -q` y confirmar que los tres tests de README pasan (GREEN)
- [ ] 2.3 Confirmar que la seccion mantiene intactos el comando unico como camino recomendado, la nota de certificado auto-firmado, la URL de salud HTTPS y los enlaces a `docs/operational-guide.md` y `docs/troubleshooting.md`; verificar con una lectura de la seccion

## 3. GREEN — Guia operativa sincronizada con el bootstrap

- [ ] 3.1 Editar la seccion 1.3 de `docs/operational-guide.md` (lineas 66-115) para presentar el comando unico (`bash scripts/up.sh` / `.\scripts\up.ps1` / `make up`) como camino recomendado, describiendo que genera certificados si faltan, levanta el stack y valida la salud; ejecutar `cd App/Backend; pytest tests/test_docs_bootstrap_sync.py -q` y confirmar GREEN
- [ ] 3.2 Documentar en la seccion 1.3 el preflight de costo, el bloqueo ante fallo y el bypass `UP_SKIP_COST_PREFLIGHT=1` con su advertencia audible; verificar que `UP_SKIP_COST_PREFLIGHT` aparece en la guia
- [ ] 3.3 Preservar en la seccion 1.3 el camino manual (`bash openssl/generate-certs.sh` / `.\openssl\generate-certs.ps1` y `docker compose up -d`) como alternativa, sin presentarlo como recomendado; verificar releyendo la seccion

## 4. TRIANGULATE — Cobertura de los escenarios de la spec

- [ ] 4.1 Agregar al test un caso que asserta que `docs/operational-guide.md` conserva `docker compose up -d` como alternativa manual; ejecutar y confirmar que pasa
- [ ] 4.2 Agregar al test un caso que asserta que `README.md` conserva `docker compose up -d` y la URL `https://localhost/api/v1/health`; ejecutar y confirmar que pasa
- [ ] 4.3 Agregar un caso negativo de control: assertar que `README.md` NO contiene una afirmacion que presente el camino manual como recomendado (por ejemplo la ausencia del token `camino manual recomendado`); ejecutar y confirmar que pasa

## 5. REFACTOR y verificacion final

- [ ] 5.1 Refactorizar el test extrayendo constantes de path y un helper de lectura reutilizable, dejando los asserts legibles; ejecutar `cd App/Backend; pytest tests/test_docs_bootstrap_sync.py -q` y confirmar que sigue GREEN
- [ ] 5.2 Ejecutar la suite offline completa `cd App/Backend; pytest -m "not integration" -q` y confirmar que no hay regresiones
- [ ] 5.3 Ejecutar `openspec validate --strict --changes c-42-bootstrap-docs-sync` y confirmar que pasa; actualizar el estado del change con `openspec status --change c-42-bootstrap-docs-sync`