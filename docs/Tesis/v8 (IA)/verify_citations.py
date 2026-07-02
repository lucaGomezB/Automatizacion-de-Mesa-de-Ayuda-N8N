#!/usr/bin/env python3
"""
Citation Cross-Reference Verification Script
=============================================
Extracts all \\cite{}, \\textcite{}, and \\parencite{} keys from the 14 section
.tex files and cross-references them against @entry keys in Bibliography_base.bib.

Reports:
  - Orphan citations (cited in .tex but missing from .bib)
  - Unused bibliography entries (present in .bib but never cited)
  - Citation counts per entry

Usage:
  python verify_citations.py
"""

import re
import sys
from pathlib import Path

# --- Configuration ---
PAPER_DIR = Path(__file__).resolve().parent / "paper"
SECTIONS_DIR = PAPER_DIR / "sections"
BIB_FILE = Path(__file__).resolve().parent / "Bibliography_base.bib"

# --- Step 1: Extract all @entry keys from Bibliography_base.bib ---
def extract_bib_keys(bib_path: Path) -> set[str]:
    """Extract all @entry keys from the .bib file."""
    keys: set[str] = set()
    if not bib_path.exists():
        print(f"ERROR: Bibliography file not found: {bib_path}")
        sys.exit(1)

    content = bib_path.read_text(encoding="utf-8")
    # Match @type{key, ...} where type is article, book, manual, misc, etc.
    pattern = re.compile(r"@\w+\{(\w+)", re.MULTILINE)
    for match in pattern.finditer(content):
        keys.add(match.group(1))

    return keys


# --- Step 2: Extract all citation keys from .tex files ---
def extract_citation_keys(sections_dir: Path) -> dict[str, set[str]]:
    """
    Extract all \\cite{}, \\textcite{}, and \\parencite{} keys from .tex files.
    Returns: {filename: set_of_keys}
    """
    # Regex to match \cite{key}, \textcite{key}, \parencite{key}, \textcite[prefix]{key}
    # Handles multiple keys separated by commas: \cite{key1,key2}
    cite_pattern = re.compile(
        r"\\(?:textcite|parencite|cite|Cite|Textcite|Parencite)"
        r"(?:\[[^\]]*\])*"  # optional [prefix][suffix]
        r"\{([^}]+)\}"
    )

    file_keys: dict[str, set[str]] = {}

    tex_files = sorted(sections_dir.glob("*.tex"))
    if not tex_files:
        print(f"ERROR: No .tex files found in {sections_dir}")
        sys.exit(1)

    for tex_file in tex_files:
        content = tex_file.read_text(encoding="utf-8")
        keys: set[str] = set()

        for match in cite_pattern.finditer(content):
            key_list = match.group(1)
            # Split multiple keys: \cite{key1,key2}
            for key in key_list.split(","):
                key = key.strip()
                if key:
                    keys.add(key)

        if keys:
            file_keys[tex_file.name] = keys

    return file_keys


# --- Step 3: Cross-reference and report ---
def cross_reference(
    bib_keys: set[str],
    file_keys: dict[str, set[str]],
) -> tuple[set[str], set[str]]:
    """Cross-reference citation keys against bibliography keys."""
    all_cited: set[str] = set()
    for keys in file_keys.values():
        all_cited.update(keys)

    orphan_citations = all_cited - bib_keys
    unused_entries = bib_keys - all_cited

    return orphan_citations, unused_entries


# --- Main ---
def main() -> None:
    print("=" * 72)
    print("  Citation Cross-Reference Verification")
    print("  Thesis: Automatizacion de Mesa de Ayuda con N8N y NLP")
    print("=" * 72)

    # Extract
    print("\n[1/3] Extracting bibliography keys from Bibliography_base.bib ...")
    bib_keys = extract_bib_keys(BIB_FILE)
    print(f"      Found {len(bib_keys)} bibliography entries.")

    print("\n[2/3] Extracting citation keys from section .tex files ...")
    file_keys = extract_citation_keys(SECTIONS_DIR)
    total_citation_occurrences = sum(len(keys) for keys in file_keys.values())

    # Count each citation command invocation (not unique keys)
    total_commands = 0
    for tex_file in sorted(SECTIONS_DIR.glob("*.tex")):
        content = tex_file.read_text(encoding="utf-8")
        commands = re.findall(
            r"\\(?:textcite|parencite|cite|Cite|Textcite|Parencite)(?:\[[^\]]*\])*\{[^}]+\}",
            content,
        )
        if commands:
            print(f"      {tex_file.name}: {len(commands)} citation commands, "
                  f"{len(file_keys.get(tex_file.name, set()))} unique keys")
            total_commands += len(commands)

    print(f"\n      Total: {total_commands} citation commands across "
          f"{len(file_keys)} files")
    print(f"      Total unique citation keys: {total_citation_occurrences}")

    # Cross-reference
    print("\n[3/3] Cross-referencing citations against bibliography ...")
    orphan_citations, unused_entries = cross_reference(bib_keys, file_keys)

    # Report
    print("\n" + "=" * 72)
    print("  RESULTS")
    print("=" * 72)

    if not orphan_citations and not unused_entries:
        print("\n  ALL CITATIONS VERIFIED. Zero orphan citations, "
              "zero unused bibliography entries.")
        print(f"  {len(bib_keys)} bibliography entries <-> "
              f"{total_citation_occurrences} unique citation keys match perfectly.")
    else:
        if orphan_citations:
            print(f"\n  ORPHAN CITATIONS ({len(orphan_citations)}):")
            print("  These keys are cited in .tex files but NOT found in "
                  "Bibliography_base.bib:")
            for key in sorted(orphan_citations):
                # Find which files cite this key
                citing_files = [
                    fname for fname, keys in file_keys.items() if key in keys
                ]
                print(f"    - {key}")
                for f in citing_files:
                    print(f"      cited in: {f}")

        if unused_entries:
            print(f"\n  UNUSED BIBLIOGRAPHY ENTRIES ({len(unused_entries)}):")
            print("  These entries exist in Bibliography_base.bib but are NEVER "
                  "cited in any .tex file:")
            for key in sorted(unused_entries):
                print(f"    - {key}")

    # Detail: citation count per entry
    all_cited: dict[str, int] = {}
    for keys in file_keys.values():
        for key in keys:
            all_cited[key] = all_cited.get(key, 0) + 1

    print("\n" + "-" * 72)
    print("  Citation Frequency (unique keys per file appearance):")
    for key in sorted(all_cited.keys()):
        count = all_cited[key]
        indicator = " " if count > 1 else ""
        print(f"    {key}: cited in {count} file(s){indicator}")

    print("\n" + "-" * 72)
    print(f"  Summary: {len(bib_keys)} bib entries, "
          f"{len(all_cited)} unique keys cited, "
          f"{total_commands} total citation commands")
    print(f"  Orphan citations: {len(orphan_citations)}")
    print(f"  Unused entries:   {len(unused_entries)}")
    print(f"  STATUS: {'PASS' if not orphan_citations and not unused_entries else 'FAIL'}")
    print("=" * 72)


if __name__ == "__main__":
    main()
