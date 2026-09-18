## 1. Gate de revisión post-POST (implementado en 5efce4b)

- [x] 1.1 Renombrar el `if` pre-POST de `La informacion esta OK` a `Entrada valida` y dejarlo como validación de entrada con `confianza >= 0.70 OR revision_forzada == true`; verificar con la suite estructural `App/Backend/tests/test_n8n_workflow.py`
- [x] 1.2 Agregar el `if` post-POST `Requiere revision humana` que evalúa `{{ $json.requiere_revision_humana }} == true`; verificar que el nodo referencia el flag del backend y no `confianza`
- [x] 1.3 Cablear la rama verdadera a `Notificar operador designado` + `Registro de auditoria`, y la rama falsa a `Rutear por canal de origen` + `Registro de auditoria`; verificar las conexiones en el JSON exportado

## 2. Notificación al operador designado

- [x] 2.1 Agregar el nodo `Notificar operador designado` (`microsoftOutlook`, operación send) dirigido a `{{ $env.OPERATOR_EMAIL }}`; verificar que el nodo referencia la variable de entorno
- [x] 2.2 Definir `OPERATOR_EMAIL` en `docker-compose.yml` y `.env.example`; verificar que el servicio N8N la expone
- [x] 2.3 Marcar el correo como leído en la rama de revisión humana reutilizando `Es correo?`; verificar la alcanzabilidad a `Marcar correo como leido`

## 3. URLs del backend configurables por entorno

- [x] 3.1 Reemplazar el host hardcodeado `http://backend:8000` por `{{ $env.BACKEND_URL }}` en los nodos HTTP `Login operador` y `HTTP POST a MTM-SRU`; verificar que ningún nodo `httpRequest` contiene el literal del host
- [x] 3.2 Definir `BACKEND_URL` en `docker-compose.yml` y `.env.example`; verificar que el servicio N8N la expone

## 4. Documentación y verificación

- [x] 4.1 Actualizar `docs/n8n-workflow-guide.md` con el gate de dos capas y la notificación al operador
- [x] 4.2 Correr la suite estructural `cd App/Backend; pytest tests/test_n8n_workflow.py -q` y confirmar que pasa en verde
- [x] 4.3 Sincronizar la spec `n8n-workflow` al archivar el change; verificar que `openspec/specs/n8n-workflow/spec.md` refleje la compuerta de dos capas
