## Why

El commit `ed4b386` (merge del PR #86, remapeo de citas) agregó las filas E3/E4 a
`evaluation/data/campana/registro_sujetos.csv`, pero dejó DOS residuos en
`evaluation/data/campana/README.md`: (1) la fila de `registro_sujetos.csv` en la tabla
"SHA-256 por archivo" conserva el hash viejo, y (2) la línea del comando `sed` quedó
partida en dos porque su CR literal (0x0D) se reemplazó por un LF (0x0A). Ningún test
valida esa tabla, por eso CI siguió en verde. El README de la campaña es fuente de verdad
de la trazabilidad de la tesis: un hash falso es evidencia incorrecta para la auditoría.

## What Changes

- Corregir el SHA-256 declarado de `registro_sujetos.csv` en la tabla "SHA-256 por
  archivo" de `evaluation/data/campana/README.md`, de `f7a5653e...` al real
  `ab17eb2b6e660b78d206d130c21fac06739ba5512d2ac37d09cf532c2a3d36da`.
- Normalizar la línea 113 a UNA sola línea con el `\r` ESCAPADO
  (`sed -i 's/\r$//' <archivo>`), sin CR literal ni salto de línea intermedio.
- Agregar un test offline (TDD) que valide las tablas `| Archivo | SHA-256 |` del README
  contra los archivos reales: omite los valores `pendiente` y las filas de archivos
  ausentes, y falla si un hash declarado no coincide. Así la deriva no vuelve a pasar en
  silencio.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `evaluation-campaign-instrumentation`: se agrega un requirement de verificación offline
  de las tablas `| Archivo | SHA-256 |` del README de campaña (ECM-015). Los residuos 1 y
  2 no cambian comportamiento: son correcciones que hacen cumplir ECM-002 vigente (los
  datos de la campaña SHALL registrar su SHA-256 en un README); se registran como tareas,
  no como requirement nuevo.

## Impact

- Docs: `evaluation/data/campana/README.md` (una fila de hash y una línea partida).
- Test: `evaluation/tests/test_campana.py` (offline; sin red ni servicios).
- Spec: `openspec/specs/evaluation-campaign-instrumentation/spec.md` (vía delta ECM-015).
- Sin cambio de runtime, de datos ni de otros SHA-256: solo el texto declarado del README
  y un test nuevo. Fuera de alcance: la tesis (PDF/`.tex`), `auditorias/`, `App/`, `n8n/`
  y cualquier remapeo de otros SHAs de commit.
