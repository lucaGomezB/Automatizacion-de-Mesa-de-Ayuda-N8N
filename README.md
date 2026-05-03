# Automatizacion-de-Mesa-de-Ayuda-N8N-
En este proyecto se busca una forma eficiente de facilitar el trabajo de la Mesa de Ayuda de cualquier empresa haciendo uso una automatizacion N8N

## Especificación Técnica

### Clasificación Automática
- **Modelo**: Google Gemini 2.5 Flash
- **Enfoque**: Híbrido (filtrado determinístico + LLM)
- **Documentación completa**: `docs/parameters_gemini.md` y `docs/ANEXO_H_Especificacion_Completa.md`
- **Prompt exacto**: `docs/prompt_gemini.txt`
- **Parámetros**: temperature=0.3, top_p=0.9, max_tokens=100, timeout=10s

### Reproducibilidad
El sistema puede ser replicado exactamente siguiendo:
1. Prompt: `docs/prompt_gemini.txt`
2. Parámetros: `docs/parameters_gemini.md`
3. Workflow: `Automatizacion_Mesa_de_Ayuda.json`
4. Código: `Gestion_Incidentes/`
5. Configuración: `docker-compose.yml`

**Nota**: El corpus de validación está disponible bajo `data/corpus_evaluacion_pseudonimizado.csv` con 200 casos etiquetados.