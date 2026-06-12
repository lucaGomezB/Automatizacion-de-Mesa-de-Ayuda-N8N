# Automatizacion-de-Mesa-de-Ayuda-N8N-

[![CI](https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N/actions/workflows/ci.yml/badge.svg)](https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N/actions/workflows/ci.yml)

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

## Hook anti-secretos (obligatorio al clonar)

El repo incluye un hook pre-commit en `.githooks/pre-commit` que bloquea commits con
API keys, claves privadas o archivos `.env` (en este proyecto ya se filtró una clave
real por commitear un `.env`). Activarlo una sola vez después de clonar:

```bash
git config core.hooksPath .githooks
```

Las claves reales van **solo** en `.env` (ignorado por git); al repo solo entran
plantillas `.env.example` con placeholders. Ante un falso positivo, agregar el
marcador `gitleaks:allow` en esa línea. Si además tenés [gitleaks](https://github.com/gitleaks/gitleaks)
instalado, el hook lo usa como capa extra de escaneo.

## Memoria compartida del proyecto (engram)

El directorio `.engram/` versiona la memoria técnica del proyecto (decisiones, bugs resueltos, convenciones) para que viaje con el código y sea recuperable por cualquier colaborador.

### Workflow

```bash
# Antes de hacer push — exportar la memoria nueva de ESTE proyecto:
engram sync
git add .engram && git commit -m "chore(engram): sync project memory"

# Después de clonar o hacer pull — importar la memoria al engram local:
engram sync --import
```

⚠️ **Nunca usar `engram sync --all`**: exportaría la memoria de TODOS los proyectos de la máquina a este repositorio. El comando sin flags filtra automáticamente por este proyecto.