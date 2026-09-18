# Endurecimiento de secretos

Runbook operativo para detectar, triar y remediar la exposicion de secretos en
este repositorio publico (`lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N`).

Este documento es el procedimiento; el contrato verificable vive en
`openspec/specs/secret-hygiene/spec.md`. La automatizacion de las protecciones
configurables por API es `scripts/security/configure_github_secret_scanning.sh`.

## 1. Funciones de escaneo de GitHub: configurables por API vs solo-UI

GitHub expone el estado de las funciones de escaneo en
`GET /repos/{owner}/{repo}` bajo `security_and_analysis`. De las cuatro
funciones relevantes, solo dos se pueden habilitar por API REST:

| Funcion | Clave en `security_and_analysis` | Configurable por API REST | Disponible en este repo |
|---------|----------------------------------|---------------------------|-------------------------|
| Secret scanning | `secret_scanning.status` | Si | Si (gratis en repo publico) |
| Push protection | `secret_scanning_push_protection.status` | Si | Si (gratis en repo publico) |
| Patrones no-proveedor | `secret_scanning_non_provider_patterns.status` | NO | NO (requiere plan pago) |
| Verificaciones de validez | `secret_scanning_validity_checks.status` | NO | NO (requiere plan pago) |

Verificacion del estado actual:

```bash
gh api repos/{owner}/{repo} --jq '.security_and_analysis'
```

Las dos funciones restantes **no estan disponibles en este repositorio** (plan
gratuito, repo publico de usuario personal). No es solo que no sean
configurables por API: los toggles tampoco existen en la UI. GitHub gatea estas
capacidades detras de **GitHub Secret Protection** (GitHub Team o Enterprise,
plan pago). Enviarlas por API REST no da error: la API las **ignora en
silencio**, por lo que un script que las incluya puede reportar un exito falso.
Por eso `configure_github_secret_scanning.sh` no las envia: las imprime como
pasos manuales con la advertencia de disponibilidad.

> **Verificado (2026-09-18)**: el intento de setear ambas por API se repitio con
> y sin el header `X-GitHub-Api-Version: 2026-03-10` y en ambos casos GitHub
> devolvio los campos en `disabled`. La UI
> (`Settings > Security and quality > Advanced Security`) no muestra los toggles
> "Non-provider patterns" ni "Validity checks". La documentacion de GitHub indica
> que las validity checks para patrones partner requieren GitHub Team/Enterprise
> con Secret Protection. Conclusion: no intentar habilitarlas; si en el futuro se
> pasa a un plan pago, hacerlo por UI y verificar con el comando de estado.

### Habilitar por API las dos configurables

```bash
# Idempotente: lee el estado y solo escribe lo que falta.
bash scripts/security/configure_github_secret_scanning.sh

# Solo mostrar que haria, sin escribir:
bash scripts/security/configure_github_secret_scanning.sh --dry-run
```

El script resuelve el repositorio con `gh repo view` o acepta `--repo owner/name`,
y usa el binario de `GH_BIN` (default `gh`) para poder testearse sin red.

### Patrones no-proveedor y verificaciones de validez (no disponibles)

Estas dos funciones requieren **GitHub Secret Protection** (plan pago, GitHub
Team o Enterprise). En un repo publico de usuario personal con plan gratuito los
toggles no existen en la UI y la API REST los ignora en silencio. No hay accion
posible en el plan actual.

Si en el futuro se migra a un plan con Secret Protection:

1. Entrar a `https://github.com/{owner}/{repo}/settings/security_analysis`
   (barra lateral: **Security and quality > Advanced Security**).
2. En **Secret Protection**, activar **Non-provider patterns** y **Validity
   checks**, y guardar.
3. Confirmar con `gh api repos/{owner}/{repo} --jq '.security_and_analysis'` que
   ambas figuran en `enabled`.

## 2. Proteccion de push

La **push protection** es la barrera del lado del servidor: si un push contiene
un secreto detectado, GitHub lo rechaza antes de que entre al repositorio. Es el
backstop de la deteccion local, porque el hook pre-commit se puede saltear con
`git commit --no-verify`.

- Se habilita por API con el script (ver seccion 1) o desde **Settings > Code
  security and analysis > Push protection**.
- Cuando bloquea un push, GitHub devuelve el detalle del secreto detectado y
  ofrece opciones para permitirlo de forma consciente (con justificacion) o
  corregirlo.
- La accion correcta ante un bloqueo es **corregir y rotar**, no forzar el push.
  Si el secreto ya fue expuesto, seguir el procedimiento de la seccion 5.

## 3. Triaje y resolucion de alertas (`state` / `resolution`)

Listar las alertas abiertas:

```bash
gh api "repos/{owner}/{repo}/secret-scanning/alerts?state=open" \
  --jq '[.[] | {number, secret_type, state, resolution}]'
```

Cada alerta tiene `state` (`open` o `resolved`) y `resolution` (nulo mientras
este abierta). Al resolver una alerta hay que elegir una resolucion **veraz**:

| `resolution` | Cuando usarla |
|--------------|---------------|
| `revoked` | El secreto ya fue revocado en el proveedor. Es el caso normal tras rotar. |
| `false_positive` | La deteccion no corresponde a un secreto real. |
| `used_in_tests` | Es un valor de prueba deliberado, sin valor real. |
| `wont_fix` | Se decide conscientemente no actuar. Requiere justificacion. |

Reglas:

- Nunca dejar `resolution` en nulo cuando corresponde cerrar la alerta.
- Nunca descartar sin criterio: un descarte ciego oculta la causa raiz y
  degrada la auditabilidad.
- Una alerta cuyo secreto ya fue revocado se resuelve como `revoked`.

Resolver una alerta por numero es una operacion **opt-in con confirmacion
explicita** (cambia el estado de auditoria del repositorio):

```bash
bash scripts/security/configure_github_secret_scanning.sh \
  --resolve-alert 1 --resolution revoked --confirm
```

Sin `--confirm` el script se niega a escribir. Sin `--resolve-alert` solo lista
y reporta. Verificar el resultado:

```bash
gh api repos/{owner}/{repo}/secret-scanning/alerts/1 --jq '{state, resolution}'
```

## 4. Instalacion del hook pre-commit

El repositorio versiona el hook en `.githooks/pre-commit`. Bloquea:

1. Archivos `.env` en staging (las plantillas `.env.example`, `.env.sample` y
   `.env.template` estan permitidas).
2. Lineas agregadas que matcheen claves Google (`AIza...`/`AQ....`), claves
   privadas PEM, o asignaciones genericas `key`/`secret`/`token`/`password` con
   valores largos.
3. Si `gitleaks` esta instalado, corre ademas como capa extra opcional.

Activar el hook una sola vez por clon:

```bash
git config core.hooksPath .githooks
```

**Importante**: un clon nuevo NO tiene el hook activo hasta correr ese comando.
Sin esa configuracion la deteccion local no corre, y la unica barrera restante
es la push protection del lado de GitHub.

Para whitelistear un falso positivo legitimo, agregar el marcador
`gitleaks:allow` en la misma linea. El hook nunca imprime el valor del secreto
en su salida.

## 5. Procedimiento de rotacion de credenciales expuestas

Cuando una credencial se filtra, seguir los pasos en este orden:

1. **Revocar primero en el proveedor.** Invalidar la credencial expuesta en el
   panel del proveedor (Google, AWS, etc.). Mientras siga siendo valida, el
   riesgo continua, aunque ya no este en el arbol de trabajo.
2. **Rotar el valor.** Generar una credencial nueva y colocarla en el `.env`
   gitignorado (`App/Backend/.env`), que es el unico lugar donde viven los
   valores reales. Nunca editarla en un archivo versionado.
3. **Verificar que el arbol queda limpio.** Confirmar que no hay credenciales
   en archivos versionados y que el hook pre-commit esta activo (seccion 4).
4. **Triar y resolver la alerta.** Resolver la alerta de secret scanning con
   `resolution: revoked` (seccion 3).
5. **NO reescribir el historial de git.** Una vez que la credencial fue revocada
   en el proveedor, removerla del historial es **innecesario**: el valor ya no
   sirve para nadie. Reescribir el historial (`git filter-branch`,
   `git filter-repo`) es una operacion destructiva que rompe hashes y clones, y
   no aporta seguridad adicional sobre una credencial ya revocada.

### Caso de estudio: filtracion de la clave Google Gemini

- Un archivo `Gestion_Incidentes/.env` con una `GEMINI_API_KEY` real fue
  commiteado al historial (blob `be1ab368`, commits `0d430b5` y `eee5c84`).
- Google bloqueo la clave por estar expuesta ("leaked").
- La clave fue **revocada** en Google y su valor fue rotado. El archivo se
  removio del arbol en `02e845c`.
- La alerta de secret scanning numero `1` (`secret_type: google_api_key`) se
  resuelve como `revoked`, porque la clave ya no es valida. No se reescribio el
  historial de git.
- La rotacion de los defaults de desarrollo local se formalizo en `597c03e`
  (`POSTGRES_PASSWORD` y `N8N_BASIC_AUTH_PASSWORD` parametrizados por entorno,
  sin defaults adivinables) y el destrackeo de archivos de settings locales en
  `2784b1b`.

Este caso es la razon por la que el hook pre-commit existe: es la barrera
automatica para que no vuelva a pasar.
