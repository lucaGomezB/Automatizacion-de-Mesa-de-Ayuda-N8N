# Runbook — Corrección de la codificación del canal de correo en N8N (c-182)

Procedimiento de la corrección de la CAUSA del mojibake de las descripciones de
correo electrónico: la imagen N8N derivada que propaga el charset en la
decodificación de las partes `quoted-printable` de `@n8n/imap`.

> **La aplicación es MANUAL, CONTROLADA y GATEADA.** Construir la imagen
> derivada, recrear los servicios `n8n`/`n8n-corpus` y ejecutar la verificación
> contra el stack real **requieren aprobación explícita del usuario**. La fase de
> apply de este change deja la imagen SIN construir y el stack SIN tocar.
>
> Este procedimiento corrige la FUENTE (que los correos nuevos no se corrompan).
> La reparación de las filas ya corrompidas (`c-181`) es un procedimiento aparte:
> ver [`runbook-reparacion-encoding-descripciones.md`](runbook-reparacion-encoding-descripciones.md).

---

## 1. Causa raíz

El trigger IMAP de N8N, a través del paquete `@n8n/imap@0.16.0` incluido en la
imagen pinneda `n8nio/n8n:2.11.2`, **descarta el charset al decodificar las
partes `quoted-printable`** y las re-codifica como si fueran latin-1:

- `imap-simple.js` llama `PartData.fromData(data, encoding)` SIN el tercer
  argumento `charset`.
- `PartData.fromData` deriva a `QuotedPrintablePartData(data, charset)`; con
  `charset` `undefined` toma la rama `qp.decode(data)`, cuyos code units son los
  bytes latin-1, y `Buffer.from(decoded)` los re-codifica a UTF-8.
- Resultado: `Reunión` se persiste como `ReuniÃ³n` (el byte lead `C3` de `ó`
  queda como `Ã`, y `B1` como `±`).

Condiciones de aparición:

- **Solo el canal `correo electrónico`.** Los canales web y telefonía no pasan
  por `@n8n/imap`.
- **Solo los cuerpos con líneas de más de 78 bytes.** Esos cuerpos viajan como
  `quoted-printable`; los `8bit`/`base64` no dependen del charset en esa rama.

---

## 2. El parche exacto

El fix es de UNA línea en el paquete vendored:

```diff
--- a/usr/local/lib/node_modules/n8n/node_modules/.pnpm/@n8n+imap@file+packages+@n8n+imap/node_modules/@n8n/imap/dist/imap-simple.js
+++ b/usr/local/lib/node_modules/n8n/node_modules/.pnpm/@n8n+imap@file+packages+@n8n+imap/node_modules/@n8n/imap/dist/imap-simple.js
@@ -83,7 +83,7 @@
                 }
                 const data = result.parts[0].body;
                 const encoding = part.encoding.toUpperCase();
-                resolve(part_data_1.PartData.fromData(data, encoding));
+                resolve(part_data_1.PartData.fromData(data, encoding, part.params?.charset));
             };
             const fetchOnError = (error) => {
```

Así la rama `quoted-printable` entra por `utf8.decode(qp.decode(data))` cuando el
charset declarado es UTF-8 y produce el string correcto.

Artefactos versionados:

- `docker/n8n/Dockerfile` — `FROM n8nio/n8n:2.11.2`, copia y aplica el parche,
  restaura el usuario `node`.
- `docker/n8n/imap-simple-fromdata-charset.patch` — el diff unificado de arriba.
- `docker/n8n/apply-unified-patch.mjs` — aplicador mínimo (la imagen base no
  trae `patch` ni `python3`; solo `node`).

**Guarda de build:** el Dockerfile falla (exit no-cero) si (1) el archivo objetivo
no existe, o (2) la sustitución exacta no aplica. Nunca se produce una imagen sin
el parche en silencio. Un cambio de la versión base de N8N obliga a re-verificar
la ruta y la firma.

El mismo parche aplica con `patch` estándar para revisión en una máquina de
desarrollo (comando verificado en el apply de c-182):

```bash
# Extraer el archivo de la imagen pinneada (read-only, no construye nada)
REL='usr/local/lib/node_modules/n8n/node_modules/.pnpm/@n8n+imap@file+packages+@n8n+imap/node_modules/@n8n/imap/dist/imap-simple.js'
mkdir -p "/tmp/c182/$REL"
docker run --rm --entrypoint sh n8nio/n8n:2.11.2 -c "cat /$REL" > "/tmp/c182/$REL"
# Aplicar en seco (GNU patch) contra el arbol extraido
cd /tmp/c182 && patch -p1 --dry-run < /ruta/al/repo/docker/n8n/imap-simple-fromdata-charset.patch
```

---

## 3. Cómo construir la imagen derivada

La imagen se construye a partir del `docker-compose.yml`: los servicios `n8n` y
`n8n-corpus` usan `build:` con el MISMO contexto `./docker/n8n` (una sola
construcción; la imagen operativa y la del corpus no divergen).

```bash
# (Requiere aprobación explícita del usuario; toca el stack)
docker compose build n8n n8n-corpus
```

Confirmar DENTRO de la imagen que el parche quedó aplicado:

```bash
IMG=$(docker compose images -q n8n | head -n1)
docker run --rm --entrypoint sh "$IMG" -c \
  "grep -n 'part.params?.charset' /usr/local/lib/node_modules/n8n/node_modules/.pnpm/@n8n+imap@file+packages+@n8n+imap/node_modules/@n8n/imap/dist/imap-simple.js"
```

Esperado: una línea que contiene `part.params?.charset`. Si no aparece, abortar:
la imagen no lleva el fix.

Dos notas para un checkout de Windows (verificadas el 2026-11-12):

- **Fin de línea del contexto de build.** El parche se aplica por coincidencia
  exacta de línea. Con `core.autocrlf=true` los archivos de `docker/n8n/` se
  extraían en CRLF y el build abortaba con
  `apply-unified-patch: ERROR: target line not found exactly once (matches=0)`.
  `.gitattributes` fija ahora `docker/n8n/* text eol=lf`. En un clon anterior a
  esa regla hay que re-extraer los archivos una vez (borrar los tres archivos
  de `docker/n8n/` y correr `git checkout -- docker/n8n`) y confirmar con
  `git ls-files --eol docker/n8n` que la columna `w/` dice `lf`. Verificado: tras
  ese paso `docker compose build n8n` termina con rc=0.
- **Git Bash.** El `grep` de arriba recibe una ruta absoluta del contenedor; en
  Git Bash hay que anteponer `MSYS_NO_PATHCONV=1` para que no la reescriba como
  `C:/Program Files/Git/...`.

---

## 4. Verificación reproducible

Objetivo (D6): enviar por el flujo REAL un correo con un cuerpo acentuado de MÁS
de 78 bytes y comprobar que la `descripcion_pseudonimizada` almacenada NO presenta
la firma del mojibake (`Ã`) y SÍ conserva los acentos. El detector es la
autoridad de la firma: `es_mojibake` de
`App/Backend/scripts/reparar_encoding_descripciones.py` (`c-181`).

### 4.1 Recrear el servicio con la imagen derivada (gated)

```bash
docker compose up -d --force-recreate n8n
docker compose ps        # el stack debe quedar sano
```

### 4.2 Enviar el correo de prueba

Enviar al buzón que consume la credencial IMAP del trigger un correo cuyo CUERPO
sea acentuado y supere los 78 bytes en alguna línea, por ejemplo:

```
Reunión del área de sistemas: la señal de red falla y la conexión del equipo
no responde; revisar la gestión del sector.
```

Registrar el `Message-ID` del correo enviado (es la clave de correlación
`origen_message_id`).

### 4.3 Comprobar la descripción almacenada (reutiliza `es_mojibake`)

```bash
# 1) Extraer la descripcion almacenada del incidente de prueba
docker compose exec -T postgres psql -U mesa -d mesa_de_ayuda -At \
  -c "SELECT descripcion_pseudonimizada FROM incidente \
      WHERE origen_message_id LIKE '%<message-id>%' ORDER BY id DESC LIMIT 1;" \
  > /tmp/c182/desc.txt

# 2) Correr el detector reutilizable de c-181
cd App/Backend
python3 - <<'PY'
from pathlib import Path
from scripts.reparar_encoding_descripciones import es_mojibake

valor = Path("/tmp/c182/desc.txt").read_text(encoding="utf-8").strip("\n")
print("descripcion:", valor)
print("es_mojibake:", es_mojibake(valor))
print("contiene 'Ã':", "\u00c3" in valor)
PY
```

Esperado sobre la imagen CORREGIDA:

```
es_mojibake: False
contiene 'Ã': False
```

y la descripción conserva `Reunión`, `área`, `señal`, `conexión`.

### 4.4 Control contra la imagen pinneada

Para confirmar que el procedimiento DETECTA el defecto, repetir 4.1–4.3 contra la
imagen upstream SIN el parche (ver el rollback de §5). Esperado sobre la imagen
PINNEADA:

```
es_mojibake: True
contiene 'Ã': True
```

Ese contraste (limpio con el parche, mojibake sin el parche) es la evidencia de
que la corrección es la causa de la mejora y de que el procedimiento es válido.

### 4.5 Defensa en profundidad del harness (offline)

La ruta del corpus no depende de la rama defectuosa: `build_email_message`
construye el correo con `Content-Transfer-Encoding: base64`. La suite offline lo
verifica:

```bash
cd scripts/corpus_ingest && python3 -m pytest test_ingest_via_n8n.py -q
```

Cubre el header `base64`, el round-trip exacto del cuerpo acentuado (sin `Ã`) y la
preservación del `Message-ID` determinista.

### 4.6 Evidencia de la corrida ejecutada (2026-11-07)

- Imagen derivada construida: `mesa_local-n8n:latest`
  `sha256:15ad6534288a9a99b7eb359aa9c9a424bc8720efd51197044b1620029e983106`
  (`docker compose build n8n`, rc=0).
- Servicio `n8n` recreado con la imagen derivada (`docker compose up -d n8n`);
  contenedor `Up`.
- Parche presente en el contenedor: `imap-simple.js:86` =
  `resolve(part_data_1.PartData.fromData(data, encoding, part.params?.charset));`.
- Verificacion a nivel CODIGO (dentro del contenedor, sobre el decoder parcheado):
  - `PartData.fromData('=C3=B1','QUOTED-PRINTABLE','UTF-8').toString()` -> `"ñ"`.
  - `PartData.fromData('=C3=B1','QUOTED-PRINTABLE').toString()` -> `"Ã±"` (bug).
  Confirmado: con el charset declarado la decodificacion es correcta; sin el, mojibake.
- Harness (defensa en profundidad): `test_ingest_via_n8n.py` -> 146 passed.
- PENDIENTE (gated): la verificacion end-to-end de 4.2-4.4 (enviar un correo real)
  NO se ejecuto para no escribir un incidente de prueba en la base de evidencia
  `mesa_de_ayuda_campana`; debe correrse sobre un destino descartable (perfil
  `corpus`) o con limpieza posterior.

---

## 5. Rollback

Un único cambio revierte a la imagen upstream, **sin migración ni restauración de
datos**:

1. En `docker-compose.yml`, revertir los servicios `n8n` y `n8n-corpus` de
   `build:` a `image: n8nio/n8n:2.11.2`.
2. Recrear los servicios:

```bash
docker compose up -d --force-recreate --no-deps n8n
docker compose --profile corpus up -d --force-recreate --no-deps n8n-corpus   # si aplica
docker compose ps
```

`--no-deps` limita la operación al servicio de N8N: sin esa bandera, como `n8n`
declara `depends_on: backend: service_healthy`, la recreación también espera o
toca al backend.

El stack vuelve a la imagen upstream. Este rollback también sirve como imagen de
CONTROL para la verificación de §4.4.

### 5.1 Evidencia del rollback verificado (2026-11-12)

Cierra la tarea 6.1 de `c-182`. Corrida sobre el stack local de desarrollo
(proyecto `mesa_local`, volumen `mesa_local_n8n_data`), solo con el servicio
`n8n` (`--no-deps`), sin disparar flujos ni enviar correo.

| Estado | Imagen | Versión | `healthz` | Flujos | Credenciales | Parche |
|---|---|---|---|---|---|---|
| Derivada | `mesa_local-n8n` | 2.11.2 | ok | 1 | 1 | presente (`imap-simple.js:86`) |
| Rollback | `n8nio/n8n:2.11.2` (`sha256:0d948060...`) | 2.11.2 | ok | 1 (idéntico) | 1 | ausente |
| Restaurada | `mesa_local-n8n` | 2.11.2 | ok | 1 (idéntico) | 1 | presente |

- **Sin migración ni restauración de datos:** el registro de arranque tras el
  rollback no contiene ninguna línea de migración; la huella de datos
  (`n8n list:workflow` y el conteo de credenciales) es idéntica en los tres
  estados.
- **Duración:** unos 12 s desde la recreación hasta `healthz` ok.
- **INFRA-008:** el estado de rollback (`image: n8nio/n8n:2.11.2` literal) y el
  estado derivado (línea `FROM` del Dockerfile, `c-189`) satisfacen ambos el pin
  que controla `test_n8n_image_stays_pinned`; esa prueba no se ejecutó en esta
  corrida.
- **Advertencia:** el volumen local tiene el flujo marcado como activo, así que
  N8N lo activa en cada arranque. Si el disparador IMAP tiene credenciales
  vigentes, puede leer el buzón mientras el servicio esté en pie. En una
  instancia con datos de evidencia la mitigación efectiva es **desactivar el
  flujo antes del rollback** o bien **detener también el servicio `n8n`**:
  detener únicamente el backend no alcanza, porque el disparador IMAP pertenece
  a N8N, que es un servicio independiente y lo activa por su cuenta en cada
  arranque.
- **Límite:** la verificación se hizo sobre el stack local, no sobre la
  instancia de campaña.

---

## 6. Evidencia a registrar

Por cada corrida de verificación (con y sin el parche):

- Fecha y hora.
- Digest de la imagen derivada (`docker inspect --format '{{.Id}}' <img>`).
- Comando exacto ejecutado y resultado de `es_mojibake` + valor de la descripción.
- Resultado del control contra la imagen pinneada.
- `git` hash del repositorio al momento de la corrida.

---

## 7. Filas legacy ya corruptas

La corrección de la fuente (este runbook) NO repara datos. Las filas corrompidas
por la versión anterior siguen reparándose con
`App/Backend/scripts/reparar_encoding_descripciones.py` (`c-181`), que permanece
disponible e idempotente. Ver
[`runbook-reparacion-encoding-descripciones.md`](runbook-reparacion-encoding-descripciones.md).

---

## 8. Referencias

- Dockerfile e imagen derivada: `docker/n8n/`.
- Parche: `docker/n8n/imap-simple-fromdata-charset.patch`.
- Aplicador: `docker/n8n/apply-unified-patch.mjs`.
- Servicios: `docker-compose.yml` (`n8n`, `n8n-corpus`).
- Defensa en profundidad del harness: `scripts/corpus_ingest/ingest_via_n8n.py`
  (`build_email_message`) y `scripts/corpus_ingest/test_ingest_via_n8n.py`.
- Detector de la firma y reparación de datos: `c-181`
  (`App/Backend/scripts/reparar_encoding_descripciones.py`,
  `docs/runbook-reparacion-encoding-descripciones.md`).
