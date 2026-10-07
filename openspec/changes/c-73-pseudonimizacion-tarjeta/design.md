# Design: pseudonimizacion de numeros de tarjeta hablados

## Context

Ver `proposal.md` para la motivacion. Estado actual relevante:

- `App/Backend/app/utils/pseudonymizer.py` expone la funcion pura `pseudonymize(text, internal_domains) -> PseudonymizationResult` con 4 categorias y patrones compilados a nivel de modulo, aplicados en orden fijo: EMAIL -> TELEFONO -> HOST -> PERSONA.
- `PseudonymizationResult.conteos` es un `dict` con claves `email`, `telefono`, `host`, `persona`.
- El patron `_RE_TELEFONO` (lineas 73-89) exige 8+ digitos y su tramo final `\d{4,}` absorbe corridas contiguas largas; por eso consume parcialmente un numero de tarjeta de 16 digitos y deja un remanente en claro.
- Corpus: la unica corrida de 16+ digitos es R067 (WEB): `axm0102301239999320002302` (un nombre de DLL, 22 digitos, SIN la palabra "tarjeta"). R169 (telefonia) menciona "tarjeta" pero no contiene digitos.
- Convenciones: identificadores de dominio en espanol, strings canonicos sin tildes, funcion pura, TDD estricto.

## Goals / Non-Goals

### Goals

- Enmascarar numeros de tarjeta de 16 digitos (agrupados 4-4-4-4 o contiguos) como `[TARJETA]`.
- Activar la regla SOLO con contexto de "tarjeta" dentro de una ventana de proximidad.
- Extender `conteos` con la clave `tarjeta` y aplicar CARD antes de TELEFONO.
- Mantener la funcion pura y deterministica.

### Non-Goals

- Validacion de Luhn o longitud distinta de 16 (Amex 15, etc.).
- Corregir el falso positivo preexistente de TELEFONO sobre R067.
- Disparadores sin la palabra "tarjeta" ni NER/modelos.

## Decisions

### D1. Categoria CARD con etiqueta `[TARJETA]`

Se agrega `_LABEL_TARJETA = "[TARJETA]"` y la clave `"tarjeta"` en `conteos` (inicializada en 0). El autor confirmo la etiqueta en MAYUSCULAS, consistente con las 4 existentes.

**Alternativas rechazadas:** `[CARD]` (rompe la convencion en espanol del dominio); reutilizar `[TELEFONO]` (miente semanticamente y no distingue PII financiera).

### D2. Orden de aplicacion: EMAIL -> CARD -> TELEFONO -> HOST -> PERSONA

CARD debe correr ANTES de TELEFONO para que `_RE_TELEFONO` no consuma el numero de tarjeta primero. Se inserta inmediatamente antes de TELEFONO (EMAIL sigue primero por ser el patron mas especifico/estructurado).

**Alternativas rechazadas:** CARD despues de TELEFONO (el patron de telefono ya destruyo el numero, imposible recuperarlo); CARD al final (PERSONA/HOST no interfieren, pero deja a TELEFONO el trabajo sucio).

### D3. Disparador contextual con ventana de proximidad (decision clave)

La regla de tarjeta NO es global: se activa solo si existe una mencion de `tarjeta`/`tarjetas` (case-insensitive, word-boundary) y la corrida de 16 digitos aparece dentro de una ventana de proximidad **DESPUES** del disparador.

- **Ventana recomendada: 40 caracteres** (`_CARD_CONTEXT_WINDOW_CHARS = 40`), constante a nivel de modulo.
- Fundamento: cubre frases reales del corpus y del dominio: `"tarjeta numero "` (15), `"tarjeta es "` (11), `"tarjeta de credito es "` (~21), `"numero de tarjeta "` (~18). 40 da margen sin cruzar de oracion.
- Ventana medida desde el fin del disparador hasta el inicio del numero. La ventana es unidireccional (hacia adelante), alineada con los casos observados y con la recomendacion del autor.

**Por que contextual y no global:** la unica corrida de 16+ digitos del corpus es el DLL de R067, que NO debe censurarse. Una regla global de 16 digitos lo falsificaria. El disparador "tarjeta" es una senal barata y precisa en el dominio de mesa de ayuda.

**Alternativas rechazadas:**
- **Regla global de 16 digitos:** simple, pero rompe R067 (falso positivo real y medible).
- **Lookbehind de ancho variable en regex:** Python `re` NO soporta lookbehind de ancho variable, por lo que no es implementable directamente.
- **Validacion de Luhn:** reduciria falsos positivos pero agrega logica no regex, puede fallar con tarjetas de prueba/errores de dictado y no fue solicitada; el disparador contextual ya acota el universo.
- **Ventana simetrica (antes y despues):** cubriria "el numero ... de mi tarjeta", pero amplia la superficie de falsos positivos; se deja como mejora futura documentada.

### D4. Enfoque de regex: patron combinado disparador + numero

Como Python no permite lookbehind de ancho variable, se usa un unico patron que captura el disparador y el texto intermedio, y un grupo separado para el numero. La sustitucion preserva el prefijo y reemplaza solo el numero:

```
_RE_TARJETA = re.compile(
    r"(\btarjetas?\b.{0,40}?)"          # grupo 1: disparador + ventana (no DOTALL: no cruza \n)
    r"((?<!\d)\d{4}(?:[\s\-]\d{4}){3}(?!\d)   # 4-4-4-4 con espacio/guion
    r"|(?<!\d)\d{16}(?!\d))",            # 16 contiguos
    re.IGNORECASE,
)
```

Sustitucion con funcion: `lambda m: m.group(1) + _LABEL_TARJETA`; `subn` devuelve el conteo.

- `.{0,40}?` es lazy y, sin `re.DOTALL`, `.` no cruza saltos de linea: la ventana no se extiende entre oraciones.
- Los bordes `(?<!\d)` / `(?!\d)` evitan capturar una subcadena de 16 dentro de una corrida mayor (p. ej. los 22 digitos de R067, si algun dia tuviera contexto).
- `\btarjetas?\b` cubre singular y plural.

**Alternativas rechazadas:** dos pasadas (buscar disparadores y luego escanear cada slice) — mas indices y mas facil de romper; se prefiere un solo `subn` con funcion, que mantiene la pureza y simplifica el conteo.

### D5. Pureza y contrato

Sin I/O, sin settings, sin logging. La ventana es una constante de modulo (no se inyecta por parametro para no cambiar la firma). La funcion sigue deterministica y el resultado sigue siendo inmutable.

## Risks / Trade-offs

- **Falso negativo sin la palabra "tarjeta"** -> tradeoff aceptado y documentado; una regla global seria peor (R067). Mitigacion futura: ventana simetrica o trigger por sinonimos.
- **Ventana de 40 puede incluir un numero no relacionado** -> el disparador debe estar a <=40 chars; en la practica el numero sigue inmediatamente al disparador.
- **Cambio de contrato en `conteos`** -> los tests existentes que comparan el dict completo deben actualizarse (tarea explicita en tasks.md y delta MODIFIED).
- **Falso positivo preexistente de TELEFONO sobre R067** -> fuera de alcance; no se empeora.

## Migration Plan

Sin migraciones ni cambios de datos. El cambio es de codigo puro. Rollback = revertir el commit. No requiere backfill de incidentes ya persistidos.

## Open Questions

Ninguna. La etiqueta (`[TARJETA]`), el disparador y la ventana quedaron resueltos con el autor (ventana recomendada 40, ajustable en codigo).