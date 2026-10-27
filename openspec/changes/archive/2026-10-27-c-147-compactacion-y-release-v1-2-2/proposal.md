## Why

La release `v1.2.1` (PR #43) corrige la `v1.2.0` y publica el memo, pero no integra el cambio `c-146-completar-metricas-trabajos-previos` ni el `c-140-endurecimiento-tecnico-tls-reintentos-e2e`, que ya estan aplicados en esta rama y todavia no se fusionaron a `main`. Al integrarlos, la tesis supera el tope de paginas de la catedra: el borrador medía 111 paginas totales (cuerpo 102, anexos 9) frente a un limite de 100 sobre el TOTAL del PDF, y la compactacion de forma ya aplicada en el commit `8c0cf6d` lo llevo a 104 (cuerpo 96, anexos 8). El registro de la tesis consigna ademas una regla de tope equivocada: la seccion de presupuesto de paginas de `docs/Tesis/Correcciones/dictamen-correcciones.md` (G0.1) declara "cuerpo sin anexos <= 100" como decision del equipo, cuando la exigencia real es "TOTAL <= 100" de la catedra; y el spec abierto `Presupuesto de páginas preservado` declara un provisional "total <= 101" que ya no rige. Sin reconciliar la regla y sin cerrar las tareas pendientes de c-140, la release `v1.2.2` no es trazable ni defendible.

## What Changes

- **Parte A — Compactacion de paginas (YA APLICADA en `8c0cf6d`, se documenta como hecha).** El documento pasa de 111 a 104 paginas totales (cuerpo 102 -> 96, anexos 9 -> 8) con ediciones de forma, sin quitar contenido cientifico: `paper/main.tex` compacta el indice general y las listas de tablas y figuras en paginas compartidas y envuelve los anexos en `\small`; `paper/preambles/preamble.tex` ajusta el espaciado de la bibliografia; `paper/sections/06-implementacion.tex` reduce al 70 % de ancho las dos figuras de la seccion 6.8 (libera una pagina de solo flotantes). Un subagente habia retirado ademas un `lstlisting` (listado de codigo) del Anexo H dejando una referencia colgada; esa retirada se revirtio. El exceso de +4 paginas sobre el tope se sostiene y se defiende (techo practico de los autores del orden de 110-115). No se ejecuta nada nuevo en la fase propose.
- **Parte B — Reconciliacion de la regla de presupuesto de paginas (PENDIENTE).** Registrar la regla real en la seccion de presupuesto de paginas de `dictamen-correcciones.md` (G0.1): metrica = TOTAL del PDF; valor = 100; fuente = **catedra** (no decision del equipo); fecha; y el exceso honrado y defendido. Actualizar el libro mayor de paginas con la fila de la compactacion (104 / 96 / 8). Actualizar el requisito abierto `Presupuesto de páginas preservado` de `tesis-document`, que hoy declara un provisional "total <= 101".
- **Parte C — Cierre de las tareas pendientes de c-140 (PENDIENTE).** `c-140` esta en 70/73. Cerrar la tarea 3.8 (correr la red de seguridad completa de la regresion de backend) y la 3.9 (agregar la seccion "Politica de reintento del tramo de alta (c-140)" a `docs/n8n-workflow-guide.md`, requisito N8N-DOC-007). Registrar la tarea 3.10 (CP5, reimportacion del workflow en la instancia operativa) como ejecutada por el equipo, no por el agente.
- **Parte D — Release `v1.2.2` (PENDIENTE, patron C1/C2 de c-141/c-145).** Subir la version en `paper/sections/12-anexos.tex` y en `Bibliography_base.bib` (C1 = integrar y subir a `v1.2.2`; C2 = consignar el hash del tag). Recompilar en la imagen `texlive-thesis`, verificar el conteo de paginas y la ausencia de referencias fatales o indefinidas, crear el tag anotado `v1.2.2`, abrir un PR a `main` con **merge commit** (nunca squash ni rebase) y registrar el hash. Governance HIGH para las acciones publicas (tag, push, PR).
- **Parte E — Archivo (PENDIENTE, posterior a la release).** Cerrar la tarea 2.9 de c-141 (archivo de los changes de familia que sigan pendientes) y archivar `c-146` y `c-140`, de modo que sus delta specs se sincronicen a `openspec/specs/`.
- Sin cambios de codigo de aplicacion. La unica edicion de codigo posible es documental (la guia de N8N de la Parte C); no toca `App/`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se modifica el requisito `Presupuesto de páginas preservado` (metrica = total del PDF, tope = 100, fuente = catedra, exceso honrado y defendido, y prohibicion de quitar contenido o dejar referencias colgadas para cumplir el tope) y el requisito `Coherencia de la version bibliografica con la release publicada` (la version pasa a `1.2.2`); se agrega un requisito de publicacion de la release de integracion `v1.2.2` con el patron de dos commits C1/C2, la verificacion de compilacion y el merge commit.

## Impact

- **Integra:** `c-146-completar-metricas-trabajos-previos` (22/23) y `c-140-endurecimiento-tecnico-tls-reintentos-e2e` (70/73), ambos aplicados y aun no fusionados a `main`, mas la compactacion ya aplicada en `8c0cf6d`.
- **Edita (Parte B):** `docs/Tesis/Correcciones/dictamen-correcciones.md` (G0.1 y libro mayor de paginas).
- **Edita (Parte C):** `docs/n8n-workflow-guide.md` (seccion de politica de reintento) y `openspec/changes/c-140-.../tasks.md` (marcado de 3.8, 3.9 y 3.10).
- **Edita (Parte D):** `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (tag y hash del Anexo B), `docs/Tesis/v10 (IA)/Bibliography_base.bib` (`Gomez2026_repositorio` a `1.2.2`), los artefactos de compilacion versionados de `paper/` (`main.pdf`, `main.aux`, `main.bbl`, `main.toc`, `main.lof`, `main.lot`, etc.) y `docs/Tesis/Correcciones/dictamen-correcciones.md` (nota de trazabilidad).
- **Edita (Parte E):** movimientos de `openspec/changes/archive/` para `c-146` y `c-140` y la sincronizacion de sus delta specs; `CHANGES.md` (cierre de fase).
- **No toca:** `App/Backend/app/`, `App/Frontend/`, `n8n/workflow.json`, `data/`, los numeros canonicos `vigente` de `docs/Tesis/Correcciones/numeros-canonicos.md`, las cinco cadenas de categoria, ni los tags `v1.0.0`, `v1.0.1`, `v1.1.0`, `v1.1.1`, `v1.2.0` y `v1.2.1`.
- **Tags:** `v1.0.0` = `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`, `v1.0.1` = `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`, `v1.1.0` = `7103b649d8c4f51737ad6ad4095dad22c9406400`, `v1.1.1` = `4160d84286623b073d2904353e6f9163ae211de7`, `v1.2.0` = `a49d035c67b32ae17e633ec04b09ecdd2781aac6`, `v1.2.1` = `509ffff105c21fed0c07cbf9a46245ba6c53e0e1`. Se crea el tag anotado NUEVO `v1.2.2`.
- **Antecedente de la compactacion:** el borrador medido fue 111 total / 102 cuerpo / 9 anexos; la compactacion aplicada en `8c0cf6d` deja 104 total / 96 cuerpo / 8 anexos, exceso +4 defendido.
- **Gobernanza:** A (ya aplicada) HIGH por el dominio "eliminacion de contenido", mitigada por ser de forma; B MEDIO; C MEDIO; D HIGH (tag, push y PR son acciones publicas); E BAJO.

## Rollback

Antes de publicar el tag: `git revert` de los commits de la release (o `git checkout <commit-previo> -- <rutas>`) y recompilar; la compactacion de `8c0cf6d` y los cambios de contenido de c-146 y c-140 no se revierten desde aqui. Despues de publicar el tag y antes de la entrega: eliminar `v1.2.2` local y remoto (`git tag -d v1.2.2` y `git push origin :refs/tags/v1.2.2`) solo con confirmacion del usuario. Despues de la entrega al jurado, NO se borra ni se mueve ningun tag: se publica una release nueva (`v1.2.3`). Los tags previos no se tocan en ningun caso.

## Success Criteria

- [ ] El commit `8c0cf6d` queda documentado como la compactacion aplicada (111 -> 104), sin contenido cientifico removido ni referencias colgadas.
- [ ] La seccion de presupuesto de paginas de `dictamen-correcciones.md` (G0.1) declara la regla real: metrica = total del PDF, valor = 100, fuente = catedra, fecha, y el exceso honrado y defendido; el libro mayor tiene la fila 104 / 96 / 8.
- [ ] El requisito `Presupuesto de páginas preservado` del spec refleja la regla reconciliada y el exceso defendido, y prohibe quitar contenido o dejar referencias colgadas.
- [ ] Las tareas 3.8 y 3.9 de c-140 estan cerradas con evidencia y la 3.10 registrada como ejecutada por el equipo; c-140 queda archivado.
- [ ] El PDF de la release compila en `texlive-thesis` sin errores fatales ni referencias indefinidas, y su conteo de paginas totales cumple la regla registrada (100, con el exceso de 4 honrado y defendido).
- [ ] El tag anotado `v1.2.2` existe sobre el commit C1, esta publicado en `origin` y su hash figura en el Anexo B y en el registro; la integracion a `main` se hizo con merge commit.
- [ ] Los tags `v1.0.0` a `v1.2.1` siguen inmutables en sus hashes.
- [ ] `c-146` y `c-140` quedan archivados (delta specs sincronizados) y `openspec list` no reporta changes pendientes de la familia integrada.
