# Tasks — c-115-metodologia-y-limites-declarados

## 1. Metodología: criterio de fijación del tamaño muestral (rec. 9)

- [x] 1.1 Reescribir el párrafo del margen en `04-marco-metodologico.tex` (subsección población, muestra y corpus) para declarar que el corpus de 200 casos se fijó por disponibilidad operativa y que el `6,66 %` es la precisión implicada por ese tamaño con `N ≈ 2.646`, conservando la fórmula, los insumos y el resultado; verificar que `n ≈ 200` siga reproduciéndose con los insumos publicados y que no aparezca el `6,74 %` ni `N = 3.700`.
- [x] 1.2 Verificar por búsqueda que el texto no describa el margen como el valor elegido para reproducir el corpus (eliminar «el valor que reproduce de manera exacta el corpus de 200 casos» como enunciado central).

## 2. Limitaciones y conclusiones (dimensiones 6c / 7h)

- [x] 2.1 Agregar la dependencia entre etiquetadores de la verdad de referencia y operadores del brazo manual a la subsección de limitaciones del estudio en `08-discusion.tex`, en una o dos oraciones coherentes con la declaración de `04-marco-metodologico.tex`; verificar lectura y remisión cruzada.
- [x] 2.2 Reformular el párrafo de aportes en `09-conclusiones.tex`: retirar el calificativo «riguroso» sin matiz, acotar el aporte empírico por la independencia limitada del referente y llevar la limitación a las conclusiones con remisión a `subsec:limitaciones-estudio`; verificar que ya no exista un sobreclaim de rigor o independencia plena.

## 3. Compilación y verificación de integridad

- [x] 3.1 Compilar con `docker run --rm -v "<repo>/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex` y confirmar cero errores fatales.
- [x] 3.2 Registrar el conteo de páginas del PDF recompilado y confirmar que no supera el conteo previo al change (104); recortar la redacción a la variante más corta si lo aumenta.
- [x] 3.3 Verificar por búsqueda que no se reintrodujo ningún valor retirado (`6,74 %`, `3.700`, `45,0 h`, `9,5 %` como intervención) y que los valores canónicos vigentes (`2.646`, `6,66 %`, `200`) permanecen.
- [x] 3.4 Ejecutar `openspec validate c-115-metodologia-y-limites-declarados --strict` y confirmar resultado OK.
