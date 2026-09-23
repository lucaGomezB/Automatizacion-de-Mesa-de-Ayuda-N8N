# Directorio de empleados (c-54)

Guia operativa del directorio interno de empleados de la mesa de ayuda. Define la
entidad de contacto, el modelo de roles, la resolucion de contactos, el manejo de
datos personales (Ley 25.326), el ciclo de vida y la visibilidad de incidentes por
rol a nivel API.

## 1. Entidad y campos (minimizacion)

El directorio vive en la tabla `directorio_empleado`, SEPARADA de la autenticacion
(`users`). Una cuenta puede existir sin empleado y viceversa.

Campos EXACTOS (no se almacena ningun otro dato personal):

| Campo        | Tipo           | Reglas                                                        |
|--------------|----------------|---------------------------------------------------------------|
| `id`         | int (PK)       | Autoincremental.                                              |
| `legajo`     | varchar(50)    | NOT NULL, UNIQUE. Clave de idempotencia del seed.             |
| `nombre`     | varchar(200)   | NOT NULL.                                                     |
| `email`      | varchar(254)   | NOT NULL, UNIQUE, indexado.                                   |
| `telefono`   | varchar(20)    | NULL, indexado, PUEDE repetirse (mesa de area/casilla).       |
| `sector_id`  | int (FK)       | FK a `sector`, NULL. Obligatorio para usuario_final/operador. |
| `rol`        | varchar(30)    | `usuario_final` / `operador` / `administrador_directorio`.    |
| `activo`     | bool           | Default `true`.                                               |
| `fecha_baja` | timestamptz    | NULL; instante de desactivacion (base de la retencion).       |
| `user_id`    | int (FK)       | FK nullable a `users`, ON DELETE SET NULL.                    |
| `created_at` | timestamptz    | Auditoria temporal.                                           |
| `updated_at` | timestamptz    | Auditoria temporal.                                           |

## 2. Roles

| Rol                      | Sector        | Puede gestionar el directorio | Ve incidentes          |
|--------------------------|---------------|-------------------------------|------------------------|
| `usuario_final`          | Obligatorio   | No                            | Solo su sector         |
| `operador`               | Obligatorio   | No (solo consulta)            | Solo su sector         |
| `administrador_directorio`| Nulo         | Si                            | Todos los sectores     |

El rol NO altera el resultado de clasificacion de incidentes.

## 3. Texto plano y minimizacion

El email y el telefono se almacenan en TEXTO PLANO (varchar). NO se aplica cifrado
de aplicacion ni indice ciego, y NO existe una clave `directory_blind_index_key`.
La razon (decision v8, cap. 11.2/11.4): auditabilidad directa y consultas SQL
operativas sin custodia de claves; el dato es personal pero NO sensible bajo Ley
25.326 art. 2. La proteccion se logra con:

- Minimizacion: solo los campos de la seccion 1.
- Control de acceso por rol (seccion 6).
- Auditoria de accesos y cambios.
- Ausencia de PII en logs y respuestas de error.

El cifrado Fernet del contenido del incidente (`descripcion_original`,
`caller_cifrado`) NO se modifica.

## 4. Resolucion de contactos (seam c-53)

`app/services/contact_resolution_service.py` expone un servicio IN-PROCESS (sin
borde HTTP ni token) con:

- `resolver_por_telefono(valor)` — normaliza a E.164 y compara por igualdad.
- `resolver_por_email(valor)` — normaliza a minusculas y compara por igualdad.
- `resolver_por_usuario(user_id)` — sigue el vinculo `user_id`.

Cada metodo devuelve un `ResultadoResolucion` con estado
`encontrado` / `no_encontrado` / `ambiguo`. Un resultado vacio NO es un error:
c-53 conserva su resolucion directa cuando no hay contacto. La resolucion no
envia notificaciones y registra trazabilidad (canal + resultado) sin PII.

AMBIGUEDAD: si un telefono o email normalizado corresponde a mas de un empleado
ACTIVO, el resultado es `ambiguo` y NO se elige un contacto arbitrariamente.

## 5. Ciclo de vida, retencion y ARCO

- Desactivacion: `activo=false` y se sella `fecha_baja` con el instante (UTC). La
  resolucion ignora inactivos. La reactivacion vuelve a hacer elegible al empleado
  y LIMPIA `fecha_baja`.
- Retencion: la fila se conserva mientras la relacion laboral este activa + 1 anio.
  Vencido `fecha_baja + 1 anio`, se ejecuta el borrado FISICO. La evaluacion del
  vencimiento es una funcion pura (`retencion_vencida`) y la purga es IDEMPOTENTE:
  conserva activos y bajas recientes, y registra el conteo sin PII.
- ARCO: ante una solicitud de supresion, un `administrador_directorio` ejecuta el
  borrado FISICO. No es el camino operativo por defecto.

Purga programada/operativa por retencion (espeja el seed dev-only):

```bash
cd App/Backend
python -m scripts.purgar_directorio
```

GOVERNANCE: la politica de retencion/ARCO es HIGH y requiere revision humana antes
de activar datos reales.

## 6. Visibilidad de incidentes por rol (API)

- `administrador_directorio`: ve TODOS los incidentes.
- `usuario_final` / `operador` con sector S: ve solo los incidentes de S.
- Cuenta sin empleado vinculado o sin sector: alcance VACIO (no ve incidentes por
  esta via).
- El acceso puntual a un incidente fuera de sector responde 404 (no revela su
  existencia).

DECISION DE IMPLEMENTACION (sector efectivo): el sector se deriva del directorio
via `user_id -> directorio_empleado.sector_id`. Una cuenta autenticada sin empleado
vinculado con sector obtiene un alcance VACIO.

El filtrado se aplica solo a nivel API/servicio. La representacion en el FRONTEND
queda DIFERIDA a un change posterior.

## 7. API de gestion

Prefijo `/api/v1/directorio`:

| Metodo | Ruta                        | Rol requerido                    |
|--------|-----------------------------|----------------------------------|
| POST   | `/empleados`                | `administrador_directorio`       |
| GET    | `/empleados`                | `operador` o `administrador`     |
| GET    | `/empleados/{id}`           | `operador` o `administrador`     |
| PATCH  | `/empleados/{id}`           | `administrador_directorio`       |
| DELETE | `/empleados/{id}`           | `administrador_directorio` (ARCO)|

Sin token valido: 401. Con token sin empleado vinculado: 403.

## 8. Seed dev-only

`App/Backend/scripts/seed_directorio.py` crea UN usuario sintetico por rol (sin PII
real, dominio `.test`), creando la cuenta `users` (login) y la fila
`directorio_empleado` enlazadas por `user_id`. Es idempotente por `legajo` y
resuelve el bootstrap del primer administrador.

```bash
cd App/Backend
python -m scripts.seed_directorio
```

Las contrasenas son de desarrollo y deben cambiarse antes de cualquier uso real.
