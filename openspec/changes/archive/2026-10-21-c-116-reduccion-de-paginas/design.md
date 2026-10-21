## Context

Ver `proposal.md — Why`. Estado medido el 2026-10-21 sobre
`docs/Tesis/v9 (IA)/paper/main.pdf`:

- **Baseline**: `pdfinfo main.pdf | grep Pages` -> `Pages: 104`.
- Tope vigente: 100 páginas. Brecha: **4 páginas**.
- Distribución por sección (índices de `main.toc`): glosario p.10; Cap1 11-17;
  Cap2 18-25; Cap3 26-30; Cap4 31-39; Cap5 40-50; Cap6 51-60; Cap7 (legal)
  61-65; Cap8 66-73; Cap9 74-81; Cap10 82-84; Cap11 85-89; Referencias 90-95;
  Anexos 96-103.
- Restricciones: no tocar contenido científico, cifras, figuras/tablas requeridas
  (8 figuras de c-80, 9 tablas con fuente), referencias ni correcciones c-102..c-115.

**Divergencia declarada (ambigüedad resuelta)**: `docs/cumplimiento/plan-cambios-cumplimiento.md`
§1.1 fija el tope sobre el CUERPO ("los anexos no cuentan"). El pedido de este
change fija el tope sobre el TOTAL (portada e índices incluidos). Se adopta el
criterio más estricto: **total del PDF <= 100** vía `pdfinfo`, que subsume el tope
del cuerpo. El conteo se mide siempre sobre `main.pdf`. **Confirmado por el autor el
2026-10-21: el total debe ser <= 100.**

## Goals / Non-Goals

**Goals:**
- Reducir el total de 104 a <= 100 páginas (-4 o más) sin pérdida de contenido científico.
- Dejar una regla explícita de qué es removible (forma) y qué no (fondo).
- Verificar con compilación real: 0 referencias indefinidas, 0 fatales.

**Non-Goals:**
- Reescribir capítulos, corregir cifras o completar los changes c-112..c-115.
- Reducir por debajo de 100 si la reducción exige sacrificar contenido requerido.
- Editar `Bibliography_base.bib` o `App/**`. Crear el tag (eso es c-111).

## Decisions

### D1. Métrica única: `pdfinfo | grep Pages` sobre el total
Se mide el documento completo, no el cuerpo. Alternativa (medir solo el cuerpo
<= 100) fue descartada por ser la interpretación laxa y por no cubrir el pedido.
Consecuencia: los anexos (8 páginas) son palanca legítima.

### D2. Palancas de forma, no de fondo
Solo se admite eliminar redundancia y ajustar formato: (a) pasajes duplicados
residuales (el par 1.1/2.1 y 8.1/9.1 ya fueron deduplicados por c-80 F5; se
re-audita lo restante, incluido resumen vs introducción y planillas vs anexos);
(b) leyendas de figura/tabla sobre-extendidas (19 `\caption`), moviendo el detalle
a la prosa; (c) listas redundantes (`itemize`/`enumerate` del Anexo A y H);
(d) tamaño del glosario (ya en 2 columnas `\small`; no ampliar la lista de siglas
y ajustar `\setlength`); (e) espaciado vertical alrededor de figuras flotantes;
(f) compactación de anexos descriptivos. Alternativa (recortar capítulos
científicos) descartada por violar el fondo.

### D3. Presupuesto por sección (suma 4,5 páginas >= 4)

| Sección | Palanca principal | Ahorro objetivo |
|---|---|---|
| Glosario (p.10) | ajuste de interlineado/columnas, sin perder entradas usadas | 0,3 pág. |
| Cap1 Introducción | redundancia resumen/introducción y listas | 0,3 pág. |
| Cap2 Marco teórico | prosa duplicada con Cap1 (post c-110) | 0,3 pág. |
| Cap3 Estado del arte | leyendas y prosa redundante | 0,2 pág. |
| Cap4 Marco metodológico | listas y prosa redundante | 0,3 pág. |
| Cap5 Arquitectura | espaciado de figuras + listas redundantes | 0,5 pág. |
| Cap6 Implementación | leyendas sobre-extendidas + prosa duplicada con Cap5 | 0,3 pág. |
| Cap7 Legal | prosa redundante | 0,2 pág. |
| Cap8 Resultados | leyendas de figuras/tablas + duplicación con Cap9 | 0,4 pág. |
| Cap9 Discusión | duplicación residual con Cap8/Conclusiones | 0,4 pág. |
| Cap10-11 Conclusiones/Recomendaciones | prosa redundante | 0,3 pág. |
| Anexos (96-103) | compactación de Anexo A/H (prosa + listas) | 1,2 pág. |
| **Total** | | **4,5 pág.** |

El presupuesto apunta a 4,5 para dejar 0,5 de reserva ante variabilidad de
compaginación; se ejecuta por secciones y se mide acumulado.

### D4. Regla de no pérdida de contenido científico (invariante)
No se elimina ni altera: afirmaciones, argumentos, interpretaciones, análisis;
las 8 figuras de c-80 y las 9 tablas (con su línea de fuente); los números
canónicos; las referencias; ninguna corrección de c-102..c-115. Un candidato de
recorte que toque cualquiera de estos elementos se descarta y se busca otra palanca.

### D5. Verificación
Compilar con la imagen `texlive-thesis` (`latexmk main.tex`), luego verificar
`pdfinfo main.pdf | grep Pages <= 100` y `rg -c "undefined reference|multiply defined label" main.log` = 0. Registrar conteo y resultado como evidencia.

### D6. Governance y reversibilidad
**Governance: HIGH** (dominio "eliminación de contenido": riesgo de quitar algo
que debía permanecer). Se propone y se mide antes de dar por cerrada cada sección.
**Reversibilidad: alta** — todos los `.tex` están versionados en git; un `git
revert` del commit del change restituye el estado de 104 páginas. No hay datos ni
estado externo afectados; no se toca `.bib` ni `App/**`.

## Risks / Trade-offs

- [Una palanca toca contenido científico] -> aplicar D4: cada recorte se contrasta
  contra la lista de invariantes antes de ejecutarlo; ante duda, se descarta.
- [El ahorro medido no alcanza 4 páginas] -> el presupuesto (4,5) tiene reserva y
  palancas de anexos de mayor rendimiento; se reasigna entre secciones, sin bajar
  nunca de D4.
- [La reducción reintroduce un valor retirado] -> verificación `rg` de los valores
  retirados (9,5 %, 3.700, "Operaciones", W=0) tras cada sección.
- [Variabilidad de compaginación] -> medir el total tras cada bloque; el objetivo
  se fija sobre el PDF, no sobre líneas de fuente.

## Migration Plan

1. Medir baseline (`pdfinfo`) y registrar 104.
2. Aplicar el presupuesto sección por sección (D3), midiendo el acumulado.
3. Recompilar y verificar D5.
4. Si `Pages > 100`, ampliar la palanca de anexos/leyendas hasta cumplir, sin violar D4.
5. Rollback: `git revert` del commit del change (restaura las 104 páginas).

## Open Questions

(none)
