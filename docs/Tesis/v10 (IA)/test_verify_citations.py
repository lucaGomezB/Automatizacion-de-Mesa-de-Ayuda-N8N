"""Pruebas unitarias de verify_citations.py (c-139, D12).

Se ejecutan sin dependencias externas, desde esta carpeta:

    python -m unittest test_verify_citations -v
"""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify_citations  # noqa: E402
from verify_citations import count_unique_cited_keys  # noqa: E402


class CountUniqueCitedKeysTest(unittest.TestCase):
    def test_claves_compartidas_entre_archivos_se_cuentan_una_vez(self):
        file_keys = {"a.tex": {"k1", "k2"}, "b.tex": {"k1"}}
        self.assertEqual(count_unique_cited_keys(file_keys), 2)

    def test_claves_disjuntas_se_suman(self):
        file_keys = {"a.tex": {"k1"}, "b.tex": {"k2", "k3"}}
        self.assertEqual(count_unique_cited_keys(file_keys), 3)

    def test_sin_citas_devuelve_cero(self):
        self.assertEqual(count_unique_cited_keys({}), 0)


class MainOutputTest(unittest.TestCase):
    def test_main_informa_el_conteo_global_y_la_suma_por_archivo_rotulada(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sections = root / "sections"
            sections.mkdir()
            (sections / "a.tex").write_text(
                r"Texto \parencite{k1} y \textcite{k2}.", encoding="utf-8"
            )
            (sections / "b.tex").write_text(
                r"Otro texto \parencite{k1}.", encoding="utf-8"
            )
            bib = root / "refs.bib"
            bib.write_text(
                "@book{k1,\n  title = {Uno}\n}\n\n@book{k2,\n  title = {Dos}\n}\n",
                encoding="utf-8",
            )
            out = io.StringIO()
            with mock.patch.object(verify_citations, "SECTIONS_DIR", sections), \
                    mock.patch.object(verify_citations, "BIB_FILE", bib), \
                    contextlib.redirect_stdout(out):
                verify_citations.main()
        text = out.getvalue()
        self.assertIn("2 bibliography entries <-> 2 unique citation keys", text)
        self.assertIn("Total unique citation keys: 2", text)
        self.assertIn("Total key-file appearances: 3", text)
        self.assertIn("STATUS: PASS", text)


if __name__ == "__main__":
    unittest.main()
