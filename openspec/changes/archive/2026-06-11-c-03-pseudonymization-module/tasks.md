> **GOBERNANZA ALTO (Ley 25.326).** No iniciar estas tareas hasta el **OK final** del revisor sobre los artefactos revisados (`proposal.md` + `design.md`). Las 4 decisiones de privacidad ya están aprobadas (ver "Decisiones de gobernanza aprobadas" del proposal). Strict TDD: cada unidad se construye RED → GREEN → TRIANGULATE → REFACTOR; cada paso ejecuta la suite.

## 0. Pre-requisitos y dependencias (antes de escribir tests)

- [x] 0.1 Safety net: ejecutar la suite existente del backend (`pytest` en `Gestion_Incidentes/`) y capturar baseline "N tests passing". Si algo falla, reportar como fallo preexistente y NO continuar.
- [x] 0.2 Agregar `cryptography` a `Gestion_Incidentes/requirements.txt` e instalarla; confirmar `pytest`/`pytest-asyncio`/`aiosqlite` presentes y que el resto de patrones usa solo `re` (stdlib).
- [x] 0.3 Generar una clave Fernet de prueba (`Fernet.generate_key()`) para usar en el entorno de tests vía settings override; documentar el comando de generación.

## 1. Función `pseudonymize` — esqueleto y contrato de resultado (RED inicial)

- [x] 1.1 RED: crear `tests/test_pseudonymizer.py` con `test_pseudonymize_texto_sin_pii_devuelve_texto_intacto_y_conteos_en_cero` que importe `pseudonymize` de `app.utils.pseudonymizer`, invoque con texto sin PII y verifique texto idéntico + conteos por categoría en cero → FALLA por import inexistente.
- [x] 1.2 GREEN: crear `app/utils/pseudonymizer.py` con la firma `pseudonymize(text: str, internal_domains: list[str]) -> PseudonymizationResult` (dataclass/NamedTuple con `texto: str` y `conteos: dict[str,int]`) devolviendo el texto sin cambios y conteos en cero → el test PASA.
- [x] 1.3 TRIANGULATE: `test_pseudonymize_es_determinista` (misma entrada → mismo texto y mismos conteos) → PASA sin cambios.

## 2. Patrón EMAIL → `[EMAIL]`

- [x] 2.1 RED: `test_pseudonymize_reemplaza_email_simple` (`"...juan.perez@empresa.com"` → contiene `[EMAIL]`, no el original, conteo `email` == 1).
- [x] 2.2 GREEN: regex de email compilada a nivel de módulo + `re.subn` → `[EMAIL]` y conteo; el test PASA.
- [x] 2.3 TRIANGULATE: `test_pseudonymize_reemplaza_multiples_emails` (dos emails → ambos reemplazados, conteo == 2) + caso borde con subdominio/`+tag`.
- [x] 2.4 REFACTOR: extraer etiqueta y patrón a constantes nombradas; re-ejecutar (verde).

## 3. Patrón TELEFONO → `[TELEFONO]`

- [x] 3.1 RED: `test_pseudonymize_reemplaza_telefono_con_prefijo_internacional` (`"+54 261 555-1234"` → `[TELEFONO]`, sin dígitos originales).
- [x] 3.2 GREEN: regex de teléfono (formatos AR: con/sin `+54`, con/sin paréntesis de área, separadores espacio/guion) + conteo → el test PASA.
- [x] 3.3 TRIANGULATE: `test_pseudonymize_reemplaza_telefono_local_sin_prefijo` (`"2615551234"` y `"261 555 1234"`) + caso borde que NO capture un número corto no telefónico (ej. código de error `13`).
- [x] 3.4 REFACTOR: consolidar patrón; re-ejecutar (verde).

## 4. Patrón HOST → `[HOST]` (dominios por settings + fallback heurístico)

- [x] 4.1 RED: `test_pseudonymize_reemplaza_host_fallback_prefijo_servidor` (`"srv-correo01"` con `internal_domains=[]` → `[HOST]`).
- [x] 4.2 GREEN: regex de fallback heurístico (`srv-*`, `pc-*`, sufijo `*.local`, `localhost`) + conteo → el test PASA.
- [x] 4.3 TRIANGULATE: `test_pseudonymize_reemplaza_host_sufijo_local` (`"pc-recepcion.local"`) + caso borde que NO capture palabras comunes con guion que no son hosts.
- [x] 4.4 TRIANGULATE: `test_pseudonymize_reemplaza_host_de_dominio_corporativo_configurado` (`pseudonymize("Falla en mail.corp.empresa.com", ["corp.empresa.com"])` → `[HOST]`); construir el patrón de dominios dinámicamente desde `internal_domains` (escapando los dominios) y combinarlo con el fallback.
- [x] 4.5 REFACTOR: consolidar la construcción de dominios + fallback; re-ejecutar (verde).

## 5. Patrón PERSONA → `[PERSONA]` y lista de exclusión

- [x] 5.1 RED: `test_pseudonymize_reemplaza_nombre_y_apellido` (`"el usuario Juan Pérez reportó..."` → `[PERSONA]`, sin `Juan Pérez`, conteo `persona` >= 1).
- [x] 5.2 GREEN: regex heurística de nombres propios (palabras capitalizadas con tildes y `ñ`) aplicada DESPUÉS de email/telefono/host → el test PASA.
- [x] 5.3 TRIANGULATE: `test_pseudonymize_categorias_dominio_no_se_marcan_como_persona` (`"Sistemas"`, `"Operaciones"`, `"Soporte Técnico"` NO se convierten en `[PERSONA]`) → implementar lista de exclusión mínima.
- [x] 5.4 TRIANGULATE: nombre simple y con tildes/`ñ` (ej. `"Núñez"`), confirmando recall sobre nombres reales.
- [x] 5.5 REFACTOR: extraer lista de exclusión y patrón a constantes documentadas; re-ejecutar (verde).

## 6. Orden de aplicación libre de colisiones + conteos agregados

- [x] 6.1 RED: `test_pseudonymize_email_no_se_fragmenta_como_persona` (email que contiene un nombre → solo `[EMAIL]`, sin `[PERSONA]` parcial).
- [x] 6.2 GREEN: fijar orden email → telefono → host → persona; el patrón de persona excluye etiquetas `[MAYÚSCULAS]` ya insertadas → el test PASA.
- [x] 6.3 TRIANGULATE: `test_pseudonymize_combinacion_todas_las_categorias` (nombre + email + teléfono + host simultáneos → cada etiqueta presente, ningún dato original, conteos correctos por categoría).
- [x] 6.4 REFACTOR: cuerpo de `pseudonymize` como secuencia legible de `re.subn` acumulando conteos; re-ejecutar (verde).

## 7. Cifrado at-rest: `EncryptedText` TypeDecorator (Fernet)

- [x] 7.1 RED: crear `tests/test_encryption.py` con `test_encrypted_text_round_trip` que, con una clave Fernet de prueba inyectada vía settings override, verifique que `process_bind_param` produce un ciphertext distinto del original y que `process_result_value` lo descifra al original → FALLA (módulo inexistente).
- [x] 7.2 GREEN: crear `app/utils/encryption.py` con `class EncryptedText(TypeDecorator)` (`impl = Text`, `cache_ok = True`, `process_bind_param` cifra, `process_result_value` descifra) y resolución perezosa de la clave Fernet desde settings → el test PASA.
- [x] 7.3 TRIANGULATE: `test_encrypted_text_none_se_preserva` (None → None en ambos sentidos) + `test_encrypted_text_ciphertext_no_contiene_plaintext` (el ciphertext no contiene la subcadena original).
- [x] 7.4 REFACTOR: aislar el acceso a la clave en un helper `_get_fernet()`; confirmar que el módulo no importa de capas superiores; re-ejecutar (verde).

## 8. Settings nuevos

- [x] 8.1 RED: `test_settings_pseudonymization` que verifique que `Settings` expone `pseudonymization_internal_domains: list[str]` (default `[]`) y `pseudonymization_encryption_key: str` (obligatoria) → FALLA.
- [x] 8.2 GREEN: agregar ambos campos a `app/config/settings.py` siguiendo el estilo existente (comentarios con ejemplo `.env`, lista tipada, clave obligatoria sin default) → el test PASA.
- [x] 8.3 REFACTOR: documentar la generación de la clave en el comentario del campo; (opcional) crear `Gestion_Incidentes/.env.example` con `PSEUDONYMIZATION_ENCRYPTION_KEY` y `PSEUDONYMIZATION_INTERNAL_DOMAINS`.

## 9. Modelo: doble representación

- [x] 9.1 RED: `test_incidente_tiene_doble_representacion` (instanciar `Incidente` con `descripcion_original` y `descripcion_pseudonimizada`; verificar que ambos atributos existen y que `descripcion_original` usa el tipo `EncryptedText`) → FALLA.
- [x] 9.2 GREEN: en `app/models/incidente.py` reemplazar la columna `descripcion` por `descripcion_pseudonimizada: Mapped[str]` (`Text`, claro) y `descripcion_original: Mapped[str]` (`EncryptedText`); corregir el docstring obsoleto ("pseudonimizada por N8N") → el test PASA.
- [x] 9.3 REFACTOR: revisar índices/`__table_args__`; re-ejecutar (verde).

## 10. Migración Alembic 002 (doble representación + backfill + drop)

- [x] 10.1 RED: test de migración (`tests/test_migration_002.py`) que, sobre la base de tests (SQLite), aplique `alembic upgrade head` y verifique que la tabla `incidente` tiene `descripcion_original` y `descripcion_pseudonimizada` y NO tiene `descripcion` → FALLA (migración inexistente).
- [x] 10.2 GREEN: crear `alembic/versions/002_doble_representacion.py` (`down_revision="001"`) que con `op.batch_alter_table` agregue ambas columnas nullable, backfillee filas existentes (reusando `pseudonymize` y el cifrado Fernet), las vuelva `NOT NULL` y dropee `descripcion`; implementar `downgrade` (recrear `descripcion` recuperando el texto original descifrado, eliminar las dos columnas) → el test PASA.
- [x] 10.3 TRIANGULATE: test de round-trip de migración con una fila preexistente (insertar un incidente con `descripcion`, migrar, verificar que `descripcion_pseudonimizada` quedó enmascarada y `descripcion_original` cifrada/descifrable) + verificar `downgrade` reversible.
- [x] 10.4 REFACTOR: extraer el backfill a una función legible dentro de la migración; documentar el requisito de `PSEUDONYMIZATION_ENCRYPTION_KEY` presente al migrar; re-ejecutar (verde).

## 11. Integración en el servicio (punto canónico) + auditoría DEBUG

- [x] 11.1 RED: `tests/test_pseudonymization_integration.py` con `test_create_and_classify_persiste_doble_representacion` (con `db_session` + classifier mock): al crear un incidente con PII, `descripcion_pseudonimizada` queda enmascarada y `descripcion_original` conserva (descifrado) el texto crudo → FALLA.
- [x] 11.2 GREEN: en `app/services/incidente_service.py` (`create_and_classify`) invocar `pseudonymize(payload.descripcion, settings.pseudonymization_internal_domains)` antes de persistir; poblar ambas columnas; pasar la pseudonimizada al `classifier.classify(...)` → el test PASA.
- [x] 11.3 TRIANGULATE: `test_gemini_recibe_descripcion_pseudonimizada` (mockeando el cliente Gemini, capturar el `contents`/prompt y verificar que contiene etiquetas y NO los datos originales).
- [x] 11.4 TRIANGULATE: `test_etapa_deterministica_opera_sobre_pseudonimizada` (el determinístico clasifica correctamente sobre texto pseudonimizado representativo; no accede a `descripcion_original`).
- [x] 11.5 TRIANGULATE: `test_log_debug_cobertura_sin_pii` (capturar logs; verificar que el evento DEBUG `pseudonimizacion_cobertura` contiene los conteos por categoría y NO el texto original ni el pseudonimizado completo).
- [x] 11.6 REFACTOR: confirmar que el clasificador NO re-pseudonimiza (sin llamada defensiva); actualizar docstrings de `GeminiClassifier`/`HybridClassifier` para reflejar el contrato (argumento = texto ya pseudonimizado); re-ejecutar (verde).

## 12. Schemas y endpoints: exponer solo la pseudonimizada

- [x] 12.1 RED: `test_incidente_read_expone_solo_pseudonimizada` (construir `IncidenteRead` desde un `Incidente` con ambas columnas; verificar que el campo de descripción expuesto es el pseudonimizado y que el original con PII NO aparece) → FALLA.
- [x] 12.2 GREEN: en `app/schemas/incidente.py`, `IncidenteRead` expone `descripcion_pseudonimizada` (renombrar/mapear el campo) y NO expone `descripcion_original`; ajustar `routes/incidentes.py` si el nombre del campo cambia → el test PASA.
- [x] 12.3 TRIANGULATE: `test_endpoint_detalle_no_expone_original` (test de cliente HTTP/TestClient: el detalle devuelve la pseudonimizada y ningún campo contiene el texto original con PII).
- [x] 12.4 REFACTOR: confirmar que `IncidenteListItem` sigue sin exponer descripción; re-ejecutar (verde).

## 13. Documentación y cierre

- [x] 13.1 Crear `docs/pseudonymization.md`: arquitectura de doble representación, categorías/etiquetas, orden de aplicación, dominios parametrizados + fallback, cifrado Fernet (generación y manejo de la clave, rotación manual como nota), límites del enfoque regex (falsos positivos/negativos), riesgo de reidentificación residual y mitigaciones (Ley 25.326, §11.3/§11.4/§11.5), auditoría DEBUG sin PII, y la restricción de que el acceso a la original cifrada queda fuera de la API.
- [x] 13.2 Ejecutar la suite completa (`pytest`) y `alembic upgrade head` en SQLite; confirmar baseline de 0.1 mantenido + nuevos tests verdes; registrar la tabla de evidencia TDD. Resultado: 81 passed, 1 skipped, 0 failed.
- [x] 13.3 Verificar dirección de dependencias: `app/utils/pseudonymizer.py` y `app/utils/encryption.py` NO importan de `classifiers/` ni `services/`. Verificado con inspección de imports.
- [x] 13.4 Resolver/registrar con el revisor las Open Questions residuales del design (`.env.example` vs docs; estrategia exacta de migración en SQLite; dato recuperado en el downgrade de 002). Resoluciones: `.env.example` ya existe (creado en Ola 1); batch_alter_table funciona en SQLite (validado por tests); downgrade recupera el texto original descifrado (implementado y testeado).
