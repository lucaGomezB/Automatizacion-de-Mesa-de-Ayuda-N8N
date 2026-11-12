#!/usr/bin/env python3
"""Lista oraciones largas por archivo:linea (solo lectura) para el pase de c-197."""
import sys
from pathlib import Path
import sent_c197 as m

base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/Tesis/v10 (IA)/paper/sections")
threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 40
for p in sorted(base.glob("*.tex")):
    if not p.name[:2].isdigit():
        continue
    lines = p.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("%"):
            continue
        text = m.clean(line)
        for s in m.split_sentences(text):
            c = m.word_count(s)
            if c > threshold:
                print(f"{p.name}:{i}\t{c}\t{s[:300]}")
