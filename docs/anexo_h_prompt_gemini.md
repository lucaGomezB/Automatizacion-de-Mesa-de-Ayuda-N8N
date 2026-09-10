# ANEXO H: Especificación del Prompt de Gemini 2.5 Flash y Parámetros de Configuración

## H.1. Estructura y contenido del prompt

El prompt enviado al modelo Gemini 2.5 Flash sigue una estructura fija en lenguaje natural español organizada en cinco componentes funcionales:

### (1) Instrucción de rol
Define explícitamente que el modelo actúa como **"agente especializado en clasificación de incidentes técnicos en español rioplatense"**. Esta instrucción ancla el comportamiento del modelo en el dominio y el dialecto específico del estudio.

### (2) Definición de categorías
Presenta de forma concisa los tres sectores responsables:
- **Sistemas**: infraestructura, redes, servidores, bases de datos, ciberseguridad
- **Operaciones**: procesos compartidos, gestión de servicios, planificación, continuidad operativa
- **Soporte Técnico**: equipamiento de usuarios, periféricos, software cliente, asistencia remota

Se incluyen dos ejemplos balanceados de incidentes representativos por clase, extraídos del dominio real:
- Ejemplo Sistemas: "Se cayó el servidor de correo. No pueden conectarse los clientes de Outlook. Error SMTP timeout."
- Ejemplo Operaciones: "Necesitamos reservar sala para reunión de 15 personas el próximo miércoles 14hs."
- Ejemplo Soporte Técnico: "Mi impresora no imprime. Papel atascado. Código de error 13."

### (3) Definición de formato de respuesta
Solicita explícitamente un JSON válido con **exactamente dos campos**:
- `"categoría"` (string): valor estrictamente en `{Sistemas, Operaciones, Soporte Técnico}`
- `"confianza"` (number): flotante entre 0.0 y 1.0 indicando nivel de seguridad

Instrucción explícita: **"Devuelve siempre un JSON válido sin texto adicional, comentarios o explicaciones. Ejemplo: {"categoría": "Sistemas", "confianza": 0.95}"**

### (4) Instrucción de lógica de decisión
**"Analiza la descripción del incidente y asigna una categoría única de las tres opciones listadas. Si la descripción contiene elementos de múltiples categorías, elige la que sea dominante."**

Esta instrucción maneja el caso ambiguo de incidentes borderline que podrían clasificarse en múltiples categorías.

### (5) Validación sintáctica
**"Valida que tu respuesta JSON sea sintácticamente correcta antes de devolverla. Si no puedes clasificar con confianza >0.5, devuelve confianza menor."**

---

## H.2. Parámetros de configuración de Gemini 2.5 Flash

La invocación del modelo se realiza mediante la API `google-generativeai` versión 0.8, con la siguiente configuración de hiperparámetros optimizada para equilibrar exactitud, latencia y costo de inferencia:

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| **temperature** | 0.3 | Valor bajo que reduce variabilidad en generación de texto. Mejora consistencia en tareas de clasificación determinística. Mitiga alucinaciones. |
| **top_p** | 0.9 | Nucleus sampling que permite variantes léxicas válidas en español rioplatense (ej., "se cayó" vs "colapsó") sin sacrificar coherencia. |
| **max_tokens** | 100 | Límite suficiente para respuesta JSON (~10-15 tokens) con margen para variaciones. Evita truncamiento. |
| **candidate_count** | 1 | Genera respuesta única sin resampling. Optimiza latencia para procesamiento en tiempo real. |
| **safety_settings** | Parcialmente desactivados | Desactiva filtros que podrían rechazar descripciones de incidentes legítimas (palabras como "cayó", "atasco", "corte"). Mantiene filtros contra contenido verdaderamente tóxico. |
| **timeout** | 10 segundos | Límite máximo de latencia. Tras excederse, clasificador devuelve confianza 0.0 y marca para revisión humana. |
| **API version** | google-generativeai 0.8 | Versión vigente marzo 2026. Documentada para reproducibilidad. |

### Implementación en Python

```python
import google.generativeai as genai

def clasificar_con_gemini(descripcion: str) -> dict:
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    response = model.generate_content(
        prompt + descripcion,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            top_p=0.9,
            max_output_tokens=100,
            candidate_count=1,
        ),
        safety_settings=[
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            # ... otros settings
        ],
        request_options={"timeout": 10}
    )
    
    return json.loads(response.text)
```

---

## H.3. Validación de formato de respuesta

**Antes de aceptar la respuesta del modelo**, el módulo Python valida las siguientes condiciones:

1. **Validez JSON**: La respuesta se parsea con `json.loads()`. Si falla, se rechaza.

2. **Presencia de campos**: Verificación de existencia de exactamente dos claves: `"categoría"` y `"confianza"`.

3. **Validez de categoría**: 
   - Tipo: string no vacío
   - Valor: exactamente en `{Sistemas, Operaciones, Soporte Técnico}`
   - Caso-sensibilidad: mayúscula inicial obligatoria

4. **Validez de confianza**:
   - Tipo: número (int o float)
   - Rango: [0.0, 1.0] inclusive

### Procedimiento de rechazo

Si la respuesta falla **cualquiera** de estas validaciones:
1. Se registra la excepción con detalles de respuesta malformada
2. Se asigna `confianza = 0.0`
3. Se marca el incidente para revisión humana
4. **No se propagan estados inconsistentes** a la base de datos

Este procedimiento **garantiza confiabilidad operativa**: errores de formato o alucinaciones del modelo no corrompen el sistema.

### Ejemplo de validación en Python

```python
def validar_respuesta_gemini(response_text: str) -> tuple[bool, dict]:
    """
    Valida respuesta de Gemini.
    Retorna (es_valida, datos_validados o error)
    """
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        return False, {"error": f"JSON inválido: {e}"}
    
    # Verificar categoría
    if "categoría" not in data:
        return False, {"error": "Falta campo 'categoría'"}
    
    categoria = data["categoría"]
    if categoria not in {"Sistemas", "Operaciones", "Soporte Técnico"}:
        return False, {"error": f"Categoría inválida: {categoria}"}
    
    # Verificar confianza
    if "confianza" not in data:
        return False, {"error": "Falta campo 'confianza'"}
    
    confianza = data["confianza"]
    if not isinstance(confianza, (int, float)) or not (0.0 <= confianza <= 1.0):
        return False, {"error": f"Confianza inválida: {confianza}"}
    
    return True, data
```

---

## H.4. Iteración y mejora del prompt

El prompt ha sido validado y ajustado iterativamente sobre un conjunto de ~100 incidentes representativos en entornos de preproducción, **sin exposición al corpus de validación de 200 casos** utilizado en el estudio.

Versiones históricas del prompt se mantienen en el repositorio bajo `docs/prompt_gemini_history/` para auditoría y posible rollback.

---

## H.5. Recomendaciones para futuras iteraciones

Si las métricas se degradan con cambios en el modelo Gemini, se recomienda:

1. **Profundizar ejemplos por clase**: aumentar de 2 a 4-5 ejemplos por categoría
2. **Agregar contraejemplos**: mostrar incidentes limítrofes y cómo clasificarlos
3. **Especificar umbrales de confianza**: "Si tu confianza es menor a 0.6, devuelve explícitamente confianza baja"
4. **Incluir diccionario de términos clave** por categoría
5. **Migrar a modelo fine-tuned** una vez se acumule corpus de 5,000+ casos etiquetados

---

**Fecha de creación**: Marzo 2026  
**Última actualización**: Marzo 2026  
**Estado**: Versión 1.0 del prompt utilizada en evaluación de tesis
