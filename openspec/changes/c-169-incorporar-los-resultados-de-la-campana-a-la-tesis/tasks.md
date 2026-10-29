## 0. Gate de campaña (ejecución condicional)

- [ ] 0.1 Verificar que existan los artefactos de campaña (brazo manual, registro de intervención, tabla de doble etiquetado, análisis de c-167). Si faltan, detener: tareas planificadas, no ejecutadas
- [ ] 0.2 Verificar que c-165, c-166, c-167 y c-168 estén aplicados, y registrar en `CHANGES.md` la dependencia y la FASE de c-169

## 1. Números canónicos (primero: fuente de toda cifra)

- [ ] 1.1 Registrar en `docs/Tesis/Correcciones/numeros-canonicos.md` la exactitud del brazo manual y su IC, con procedencia y estado `vigente`
- [ ] 1.2 Registrar la tasa de intervención humana y su IC con la definición rotulada y procedencia
- [ ] 1.3 Computar y registrar el IC del kappa (bootstrap, semilla fija) y reemplazar la entrada "no computable" (`:198-209`) por el IC con método y semilla
- [ ] 1.4 Registrar el efecto de orden y su estadístico, y el resultado de la validación fuera de muestra

## 2. Marco metodológico (`04-marco-metodologico.tex`)

- [ ] 2.1 En 4.4, agregar el doble etiquetado y el IC del kappa (método y semilla); actualizar `:45`, `:55`
- [ ] 2.2 En 4.5, documentar el procedimiento de campaña: brazo manual, orden contrabalanceado e instrumentación de intervención
- [ ] 2.3 En 4.7, reportar las métricas e instrumentos de exactitud manual y tasa de intervención; retirar "no medido" (`:65-69`)
- [ ] 2.4 En 4.8, agregar el análisis del efecto de orden y el método del IC del kappa

## 3. Resultados (`07-resultados.tex`)

- [ ] 3.1 Reportar exactitud manual, tasa de intervención, efecto de orden y kappa+IC como resultados nuevos (con IC)
- [ ] 3.2 Actualizar el estado de la sub-hipótesis 2 (`:157-163`): de "no contrastada" a contrastada; ajustar el título de `subsec:reduccion-intervencion`

## 4. Discusión y recomendaciones (`08-discusion.tex`, `10-recomendaciones.tex`)

- [ ] 4.1 Actualizar las limitaciones donde se declararon no medidos (`08-discusion.tex:58`) y la procedencia fuera de muestra
- [ ] 4.2 Retirar la corrección de la medición de intervención de las líneas futuras ya saldadas (`10-recomendaciones.tex`)

## 5. Resumen y abstract (`00-resumen.tex`)

- [ ] 5.1 Actualizar estados/frases clave manteniendo el tope de 250 palabras en ES y EN (`:11,27`)

## 6. Tracking y verificación

- [ ] 6.1 Registrar los valores en `docs/Tesis/Correcciones/dictamen-correcciones.md` y cerrar los ítems de auditoría (a)-(e)
- [ ] 6.2 Verificar que no subsistan declaraciones "no medido / no contrastado / no estimable" superadas, y señalar las páginas agregadas
- [ ] 6.3 Ejecutar `openspec validate "c-169-incorporar-los-resultados-de-la-campana-a-la-tesis" --strict --no-interactive` y verificar que pasa
