# Tasks: Cerrar el residual de K-02 y la omision de A-02 en §1.8

Al final de cada tarea, entre parentesis, el requisito del change que cumple (nombre corto). Nombres cortos: `TD` (`tesis-document`) «Licitud», «§1.8», «Disposicion»; `OOS` (`evaluation-out-of-sample-validation`) «OOS-027». Las tareas de preparacion y cierre no llevan parentesis.

Este change es prosa LaTeX y documentacion, salvo la rama de retiro del repositorio, que ajusta pruebas y sumas. El ciclo TDD estricto NO aplica (no hay logica nueva); la red de seguridad es `verify_citations.py`, la bateria de `rg`, la compilacion de verificacion en un directorio temporal y la suite de `evaluation/` verde.

Gobernanza **ALTA**. Cada tarea marcada **[COMPUERTA]** no se ejecuta sin la respuesta escrita de los autores registrada en `docs/Tesis/Correcciones/dictamen-correcciones.md` (tabla de compuertas de c-240, con fecha). Cero llamadas a Gemini. No se tocan `.engram/`, `CHANGES.md`, ni los changes c-228..c-239 (salvo la coordinacion de orden con c-239). Los numeros de linea son de v1.5.2; si una edicion previa los desplaza, se repuntan por contenido.

## 0. Preparacion y linea base

- [ ] 0.1 Leer `proposal.md`, `design.md` (D1 a D4) y los dos specs delta; releer las secciones 2, 5 y 7 de `auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md` (K-02, A-02); confirmar que c-235 esta aplicado y que su §7.5, §1.8 y OOS-026 estan en el estado que este change presupone.
- [ ] 0.2 Capturar linea base: `git status`, `git rev-parse HEAD`, `git describe --tags`. Registrar modificaciones preexistentes ajenas y no tocarlas.
- [ ] 0.3 Red de seguridad: `cd "docs/Tesis/v10 (IA)" && python verify_citations.py` (`STATUS: PASS`); `python -m pytest evaluation -q` (registrar el conteo); `sha256sum -c evaluation/data/campana/analisis/SHA256SUMS.txt` (todo `OK`).

## 1. Compuertas de autores (CHECKPOINT de gobernanza ALTA)

- [ ] 1.1 **[COMPUERTA P4/P8]** Presentar a los autores las preguntas P4 y P8 (reabiertas de c-235) y registrar sus respuestas literales, con fecha, en la tabla de compuertas de c-240 en `dictamen-correcciones.md`: ¿los textos del corpus retirado son descripciones genericas de incidentes sin datos de terceros ni personales, o contienen datos de terceros/personales? Sin respuesta, la tarea 2.1 queda bloqueada. (TD «Licitud»)
- [ ] 1.2 **[COMPUERTA DP-01]** Registrar la decision de disposicion del repositorio publico: retirar (default K-02) o conservar+rotular con la decision de textos genericos. Sin respuesta, la rama por defecto es retirar. (TD «Disposicion», OOS «OOS-027»)
- [ ] 1.3 **[COMPUERTA DP-02]** Aprobar la redaccion del parrafo de §7.5 y de la frase reconciliada de §1.8 antes de escribirlas. (TD «Licitud», «§1.8»)

## 2. §7.5 — Parrafo de licitud y alcance

- [ ] 2.1 **[COMPUERTA P4/P8]** `11-aspectos-legales.tex` (`subsec:consentimiento-derechos`): agregar el parrafo de licitud y alcance de los datos del corpus retirado segun la rama registrada en 1.1. Rama (a): declarar que no hay datos de una tercera organizacion y que no se requiere autorizacion ni licitud, con remision a §7.3. Rama (b): declarar la autorizacion escrita, su base de licitud (Ley 25.326, articulo citado) y su alcance (uso, publicacion, transferencia), con remision a §7.3. Verificar que el parrafo existe (nunca por omision) y que no contiene nombres reales. (TD «Licitud»)
- [ ] 2.2 Verificar coherencia: §7.5 no contradice §7.3 (exacta por c-235) ni el requisito de «Sin tercera organizacion»; `rg -n "licitud" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"` devuelve al menos el parrafo nuevo. (TD «Licitud»)

## 3. §1.8 — Frase veraz

- [ ] 3.1 `01-introduccion.tex` (`subsec:alcance-delimitaciones`): retirar o reescribir la frase de L72 («La validacion experimental se realiza sobre un corpus... organizacion... de Mendoza») para presentar la validacion como dentro de la muestra sobre una sola organizacion. Conservar la delimitacion geografica de L76 a una unica organizacion como limitacion de validez externa vigente. (TD «§1.8»)
- [ ] 3.2 Verificar que §1.8 no menciona el corpus fuera de muestra retirado ("corpus independiente", "corpus arbitrado", "fuera de muestra") salvo una unica remision a la nota de versiones, coherente con §9.3/§10.2 y con el requisito de validez externa. (TD «§1.8»)

## 4. Disposicion del repositorio publico

- [ ] 4.1 **[COMPUERTA DP-01 = retiro]** En un commit propio separado: eliminar `evaluation/data/campana/corpus_independiente.json` y `corpus_independiente_arbitrado.json`, ajustar `evaluation/tests/test_linea_de_base.py`, `evaluation/tests/test_calibracion_gate.py` y `evaluation/monitoreo/test_monitor_deriva.py`, y actualizar las sumas SHA-256 de `evaluation/data/campana/analisis/SHA256SUMS.txt` y de las tablas del README de campana. Verificar `python -m pytest evaluation -q` verde. (OOS «OOS-027»)
- [ ] 4.2 **[COMPUERTA DP-01 = conservacion]** Verificar que los archivos se conservan sin alterar bytes y con el rotulado de OOS-026; `sha256sum -c evaluation/data/campana/analisis/SHA256SUMS.txt` intacto. Registrar la decision documentada de textos genericos sin datos de terceros. (OOS «OOS-027»)
- [ ] 4.3 `dictamen-correcciones.md`: agregar la entrada de c-240 con la tabla de compuertas (P4/P8, DP-01, DP-02: respuesta, fecha, responsable) y filas por observacion: K-02 (parrafo de licitud §7.5 y disposicion del repositorio, archivo:linea), A-02 (§1.8 reconciliada), con fragmento verificable. (TD «Disposicion»)

## 5. Verificacion de cierre

- [ ] 5.1 `git diff --stat`: confirmar que no cambiaron `App/`, `n8n/`, el corpus de 200 casos, `.engram/`, `CHANGES.md`, ni los directorios de c-228..c-239 (salvo el orden declarado).
- [ ] 5.2 Bateria de `rg` sobre §1.8, §7.5 y el repositorio para confirmar ausencia de corpus fuera de muestra fuera de la nota de versiones y presencia del parrafo de licitud.
- [ ] 5.3 Compilacion de verificacion en directorio temporal: 0 errores fatales, 0 referencias indefinidas.
- [ ] 5.4 Correr `openspec validate c-240-cerrar-el-residual-de-k-02 --strict` y `openspec validate --strict`; registrar el resultado sin conflictos con c-235/c-236.
- [ ] 5.5 No commitear, pushear ni sincronizar Engram sin instruccion de los autores; guardar en Engram el resumen del apply (`opsx/c-240-cerrar-el-residual-de-k-02/apply`) con compuertas resueltas y verificaciones.
