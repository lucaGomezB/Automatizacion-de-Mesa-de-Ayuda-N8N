# Clasificacion y etiquetado de la informacion

> **Control mapeado**: ISO/IEC 27002:2022 5.12 (Clasificacion de la informacion) y 5.13
> (Etiquetado de la informacion); NIST CSF 2.0 ID (Identify). Requisito SGD-003.
> **Estado**: v1 — aprobada por el autor el 2026-10-01 (governance MEDIO).
> **Alcance**: clasificacion de los datos y activos de informacion del sistema.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos citados;
> no constituye certificacion ni auditoria.

## 1. Proposito

Definir los niveles de clasificacion, los criterios objetivos para asignarlos, las reglas
de etiquetado y el tratamiento requerido por nivel, de modo que cada dato reciba medidas
proporcionales. Clasifica explicitamente los **datos personales (PII)** tratados por el
sistema y los **datos del directorio de empleados**.

## 2. Niveles de clasificacion

| Nivel | Criterio | Ejemplo estructural |
|-------|----------|---------------------|
| **N1 Publico** | Informacion pensada para difusion sin restriccion | Documentacion del repositorio publico; catalogo de sectores |
| **N2 Interno** | Uso interno; su divulgacion causa perjuicio operativo menor | Logs operativos sin PII; metricas de la guarda de costo |
| **N3 Confidencial (PII)** | Identifica o permite identificar a una persona | Directorio de empleados; numero llamante; correo/celular de contacto |
| **N4 Restringido** | PII sensible o que habilita reidentificacion directa | Descripcion original del incidente (cifrada); material de clave |

Nota: el sistema evita formar archivos que revelen datos sensibles del art. 2 de la Ley
25.326 (salud, origen etnico, etc.); si un incidente los contuviera, su descripcion
original cifrada se trata como N4 y su version pseudonimizada como N3.

## 3. Criterios de asignacion

1. Si el dato identifica o permite identificar a una persona por si solo o combinado con
   el directorio, es **N3** como minimo.
2. Si el dato es la copia reversible de un dato personal (texto original que puede
   reconstruirse), es **N4**.
3. Si el dato es una agregacion sin PII y su exposicion no genera riesgo individual, es
   **N2**.
4. Los datos publicos por diseno son **N1**.

## 4. Reglas de etiquetado

- Cada campo de modelo y cada activo de datos declara su nivel en este documento y en el
  inventario (`inventario-activos-informacion.md`).
- En reposo, el nivel **N3/N4** se etiqueta a nivel de esquema o de definicion de activo
  (nombre de tabla/columna y comentario en el modelo), no dentro del dato.
- En movimiento, todo activo N3/N4 viaja por canal cifrado (TLS en el borde) y no se
  incluye en logs ni en trazas.
- Los ejemplos y datos de prueba nunca contienen PII real (ver §7).

## 5. Tratamiento requerido por nivel

| Nivel | Cifrado at-rest | Pseudonimizacion | Acceso | Logs |
|-------|-----------------|------------------|--------|------|
| N1 | No requiere | No | Publico | Permitido |
| N2 | No requiere | No | Interno por rol | Permitido |
| N3 | Recomendado por minimizacion | Si aplica al dato personal | Por rol/sector | Prohibido incluir el valor |
| N4 | Obligatorio (cifrado reversible) | Si, para la copia expuesta a terceros | Minimo privilegio | Prohibido |

## 6. PII y datos del directorio

- **PII de llamantes y usuarios.** El numero llamante y los contactos se clasifican **N3**;
  su exposicion en logs crudos es una brecha de fuga de informacion (ISO 8.12, control
  mapeado al change C-66).
- **Descripcion del incidente.** La copia original se clasifica **N4** y vive cifrada con
  Fernet; solo la copia **pseudonimizada** (N3) cruza hacia N8N y Gemini
  (`docs/pseudonymization.md`).
- **Directorio de empleados.** Nombre, correo y celular se clasifican **N3**; el contacto
  del directorio hoy se almacena en texto plano (`models/empleado.py`), brecha mapeada al
  change C-66 (cifrado o justificacion por minimizacion).
- **Vinculo con las medidas existentes:** pseudonimizacion determinista, cifrado at-rest
  (Fernet) y minimizacion. La pseudonimizacion **no** equivale a la **disociacion** del
  art. 2 de la Ley 25.326: el original existe y es reidentificable con informacion
  adicional (ver `registro-actividades-tratamiento.md`, tratamiento T2).

## 7. Ejemplos sin PII real

Los ejemplos de este cuerpo documental son **estructurales o sinteticos** (por ejemplo,
"correo de contacto", "numero llamante", "campo `descripcion_original`"). No se incluye
ningun dato real de personas. Los corpus de prueba apuntan a contactos del propio grupo
(T1) bajo consentimiento documentado; no se usan datos ficticios que oculten esa condicion.

## 8. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.12/5.13 y NIST CSF 2.0 ID. No
constituye certificacion ni auditoria. Los controles organizacionales sobre el personal que
maneja informacion competen al adoptante (O).
