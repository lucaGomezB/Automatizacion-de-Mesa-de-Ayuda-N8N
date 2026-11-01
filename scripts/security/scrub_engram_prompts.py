#!/usr/bin/env python3
"""Redacta el contenido de los prompts de los chunks de Engram antes de versionarlos.

Por qué: los prompts crudos del chat pueden contener datos personales (nombres de
colaboradores, correos). El protocolo del proyecto exige que el mapeo
codigo-identidad de los sujetos quede FUERA del repositorio, que es publico.

Qué hace: por cada chunk (.jsonl.gz) reemplaza el campo `content` de cada prompt
por un marcador fijo. Conserva los metadatos (id, session_id, created_at, project)
para no perder la traza de que existio un prompt. No toca observaciones ni sesiones.
Es idempotente: un chunk ya redactado no se reescribe.

Uso:
    python3 scripts/security/scrub_engram_prompts.py <dir .engram> [chunk.jsonl.gz ...]

Sin rutas de chunk, procesa todos los `<dir>/chunks/*.jsonl.gz`. Exit 0 siempre
(salvo error de uso); imprime cuantos prompts redacto y en que archivos.
"""
from __future__ import annotations

import glob
import gzip
import json
import os
import sys

MARCADOR = "[contenido no versionado: privacidad]"


def limpiar_chunk(ruta: str) -> int:
    """Redacta los prompts de un chunk. Devuelve cuantos redacto (0 si no cambia)."""
    with gzip.open(ruta, "rt", encoding="utf-8") as fh:
        lineas = fh.read().splitlines()

    redactados = 0
    salida: list[str] = []
    for linea in lineas:
        if not linea.strip():
            salida.append(linea)
            continue
        obj = json.loads(linea)
        for prompt in obj.get("prompts") or []:
            if isinstance(prompt.get("content"), str) and prompt["content"] != MARCADOR:
                prompt["content"] = MARCADOR
                redactados += 1
        salida.append(json.dumps(obj, ensure_ascii=False))

    if redactados:
        datos = ("\n".join(salida) + "\n").encode("utf-8")
        with open(ruta, "wb") as fh:
            fh.write(gzip.compress(datos, mtime=0))
    return redactados


def main(argv: list[str]) -> int:
    if not argv:
        print(
            "uso: scrub_engram_prompts.py <dir .engram> [chunk.jsonl.gz ...]",
            file=sys.stderr,
        )
        return 2

    base = argv[0]
    rutas = argv[1:] or sorted(glob.glob(os.path.join(base, "chunks", "*.jsonl.gz")))

    total = 0
    tocados = 0
    for ruta in rutas:
        if not os.path.isfile(ruta):
            continue
        redactados = limpiar_chunk(ruta)
        if redactados:
            total += redactados
            tocados += 1
            print(f"redactados {redactados} prompts en {ruta}")
    print(f"total: {total} prompts redactados en {tocados} archivo(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
