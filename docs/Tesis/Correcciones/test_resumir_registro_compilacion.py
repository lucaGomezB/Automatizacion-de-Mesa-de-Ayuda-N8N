"""Pruebas de resumir_registro_compilacion.py (c-188, tareas 3.3 y 3.4).

Se ejecutan desde docs/Tesis/Correcciones/:
    python -m unittest test_resumir_registro_compilacion -v
"""
import hashlib
import tempfile
import unittest
from pathlib import Path

import resumir_registro_compilacion as rrc

MOTOR = (
    "This is XeTeX, Version 3.141592653-2.6-0.999996 (TeX Live 2023/Debian) "
    "(preloaded format=xelatex 2024.1.1)  9 NOV 2026 12:00\n"
)

LOG_LIMPIO = MOTOR + (
    "LaTeX Warning: Label `x' multiply defined? no, solo texto de ejemplo.\n".replace(
        "multiply defined? no, solo texto de ejemplo", "texto de relleno"
    )
    + "Output written on main.xdv (118 pages, 1234567 bytes).\n"
)

LOG_CON_DEFECTOS = MOTOR + (
    "! Undefined control sequence.\n"
    "l.12 \\foo\n"
    "LaTeX Warning: Reference `sec:x' on page 3 undefined on input line 12.\n"
    "LaTeX Warning: Citation `Autor2020' on page 4 undefined on input line 30.\n"
    "LaTeX Warning: Label `fig:a' multiply defined.\n"
    "Overfull \\hbox (3.1pt too wide) in paragraph at lines 5--6\n"
    "Overfull \\hbox (12.4pt too wide) in paragraph at lines 9--10\n"
    "Underfull \\hbox (badness 10000) in paragraph at lines 1--2\n"
    "Output written on main.xdv (121 pages, 99 bytes).\n"
)

BLG_LIMPIO = (
    "[0] Config.pm:307> INFO - This is Biber 2.19\n"
    "[0] Config.pm:310> INFO - Logfile is 'main.blg'\n"
    "[7] Biber.pm:131> INFO - Found 150 citekeys in bib section 0\n"
)

BLG_CON_AVISOS = BLG_LIMPIO + (
    "[9] Utils.pm:200> WARN - Duplicate entry key 'x' in file 'a.bib'\n"
    "[9] Utils.pm:201> WARN - Entry 'y' has a bad date\n"
    "[9] Utils.pm:202> ERROR - Cannot find file 'z.bib'\n"
)


class ConteosDelLogTest(unittest.TestCase):
    def test_errores_fatales_limpio_y_con_defectos(self):
        self.assertEqual(rrc.contar_errores(LOG_LIMPIO), 0)
        self.assertEqual(rrc.contar_errores(LOG_CON_DEFECTOS), 1)

    def test_no_cuenta_signos_de_admiracion_que_no_abren_linea(self):
        self.assertEqual(rrc.contar_errores("texto con ! en medio\n"), 0)
        self.assertEqual(rrc.contar_errores("! A\n! B\n"), 2)

    def test_referencias_y_citas_indefinidas(self):
        self.assertEqual(rrc.contar_indefinidas(LOG_LIMPIO), (0, 0))
        self.assertEqual(rrc.contar_indefinidas(LOG_CON_DEFECTOS), (1, 1))

    def test_varias_citas_indefinidas(self):
        log = (
            "LaTeX Warning: Citation `A' on page 1 undefined on input line 1.\n"
            "LaTeX Warning: Citation `B' on page 1 undefined on input line 2.\n"
            "LaTeX Warning: Reference `r' on page 1 undefined on input line 3.\n"
        )
        self.assertEqual(rrc.contar_indefinidas(log), (1, 2))

    def test_etiquetas_duplicadas(self):
        self.assertEqual(rrc.contar_duplicadas(LOG_LIMPIO), 0)
        self.assertEqual(rrc.contar_duplicadas(LOG_CON_DEFECTOS), 1)

    def test_overfull_cantidad_y_maximo(self):
        self.assertEqual(rrc.analizar_overfull(LOG_LIMPIO), (0, 0.0))
        self.assertEqual(rrc.analizar_overfull(LOG_CON_DEFECTOS), (2, 12.4))

    def test_overfull_ignora_vbox_y_underfull(self):
        log = "Overfull \\vbox (50.0pt too high) has occurred\nUnderfull \\hbox (badness 1)\n"
        self.assertEqual(rrc.analizar_overfull(log), (0, 0.0))

    def test_paginas(self):
        self.assertEqual(rrc.paginas(LOG_LIMPIO), 118)
        self.assertEqual(rrc.paginas(LOG_CON_DEFECTOS), 121)

    def test_paginas_ausentes_devuelven_none(self):
        self.assertIsNone(rrc.paginas("sin salida\n"))

    def test_motor(self):
        self.assertEqual(
            rrc.version_motor(LOG_LIMPIO),
            "XeTeX 3.141592653-2.6-0.999996 (TeX Live 2023/Debian)",
        )

    def test_motor_ausente(self):
        self.assertEqual(rrc.version_motor("nada\n"), "no registrado")


class ConteosDelBlgTest(unittest.TestCase):
    def test_version_de_biber(self):
        self.assertEqual(rrc.version_biber(BLG_LIMPIO), "2.19")
        self.assertEqual(rrc.version_biber("nada\n"), "no registrada")

    def test_avisos_limpio_y_con_avisos(self):
        self.assertEqual(rrc.contar_avisos_blg(BLG_LIMPIO), (0, 0))
        self.assertEqual(rrc.contar_avisos_blg(BLG_CON_AVISOS), (2, 1))


class Sha256Test(unittest.TestCase):
    def test_bytes_conocidos(self):
        self.assertEqual(
            rrc.sha256_bytes(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_bytes_vacios(self):
        self.assertEqual(rrc.sha256_bytes(b""), hashlib.sha256(b"").hexdigest())


class ResumirYMarkdownTest(unittest.TestCase):
    def test_resumir_limpio(self):
        r = rrc.resumir(LOG_LIMPIO, BLG_LIMPIO, b"pdf", "arbol de trabajo sobre abc1234")
        self.assertEqual(r["paginas"], 118)
        self.assertEqual(r["errores"], 0)
        self.assertEqual(r["fuente"], "arbol de trabajo sobre abc1234")
        self.assertEqual(r["sha256"], hashlib.sha256(b"pdf").hexdigest())
        self.assertEqual(r["biber"], "2.19")

    def test_resumir_con_defectos(self):
        r = rrc.resumir(LOG_CON_DEFECTOS, BLG_CON_AVISOS, b"otro", "f")
        self.assertEqual(
            (r["errores"], r["referencias_indefinidas"], r["citas_indefinidas"]),
            (1, 1, 1),
        )
        self.assertEqual(r["duplicadas"], 1)
        self.assertEqual((r["overfull"], r["overfull_max_pt"]), (2, 12.4))
        self.assertEqual((r["blg_warn"], r["blg_error"]), (2, 1))
        self.assertEqual(r["paginas"], 121)

    def test_markdown_contiene_las_cifras(self):
        r = rrc.resumir(LOG_CON_DEFECTOS, BLG_CON_AVISOS, b"otro", "fuente X")
        md = rrc.a_markdown(r)
        self.assertIn("fuente X", md)
        self.assertIn("121", md)
        self.assertIn("12,4 pt", md)
        self.assertIn(hashlib.sha256(b"otro").hexdigest(), md)
        self.assertIn("2.19", md)

    def test_markdown_limpio_informa_ceros(self):
        r = rrc.resumir(LOG_LIMPIO, BLG_LIMPIO, b"pdf", "f")
        md = rrc.a_markdown(r)
        self.assertIn("118", md)
        self.assertIn("| Errores fatales | 0 |", md)
        self.assertIn("| Overfull \\hbox (maximo) | 0 (0,0 pt) |", md)

    def test_markdown_es_determinista_y_sin_fecha(self):
        r = rrc.resumir(LOG_LIMPIO, BLG_LIMPIO, b"pdf", "f")
        a, b = rrc.a_markdown(r), rrc.a_markdown(dict(r))
        self.assertEqual(a, b)
        self.assertNotIn("2026-11", a)
        self.assertFalse(a.endswith("\n\n"))
        self.assertTrue(a.endswith("\n"))


class MainTest(unittest.TestCase):
    def _escribir(self, carpeta, log, blg, pdf):
        (carpeta / "main.log").write_text(log, encoding="utf-8")
        (carpeta / "main.blg").write_text(blg, encoding="utf-8")
        (carpeta / "main.pdf").write_bytes(pdf)

    def test_main_escribe_el_resumen_y_es_reproducible(self):
        with tempfile.TemporaryDirectory() as d:
            c = Path(d)
            self._escribir(c, LOG_CON_DEFECTOS, BLG_CON_AVISOS, b"%PDF-x")
            salida = c / "compilacion.md"
            args = [
                "--log", str(c / "main.log"),
                "--blg", str(c / "main.blg"),
                "--pdf", str(c / "main.pdf"),
                "--fuente", "f",
                "--salida", str(salida),
            ]
            self.assertEqual(rrc.main(args), 0)
            primero = salida.read_bytes()
            self.assertEqual(rrc.main(args), 0)
            self.assertEqual(salida.read_bytes(), primero)
            self.assertIn(hashlib.sha256(b"%PDF-x").hexdigest(), primero.decode("utf-8"))

    def test_main_usa_lf_y_utf8(self):
        with tempfile.TemporaryDirectory() as d:
            c = Path(d)
            self._escribir(c, LOG_LIMPIO, BLG_LIMPIO, b"pdf")
            salida = c / "s.md"
            rrc.main(
                ["--log", str(c / "main.log"), "--blg", str(c / "main.blg"),
                 "--pdf", str(c / "main.pdf"), "--fuente", "árbol", "--salida", str(salida)]
            )
            datos = salida.read_bytes()
            self.assertNotIn(b"\r\n", datos)
            self.assertIn("árbol".encode("utf-8"), datos)

    def test_main_falla_si_falta_un_archivo(self):
        with tempfile.TemporaryDirectory() as d:
            c = Path(d)
            args = ["--log", str(c / "no.log"), "--blg", str(c / "no.blg"),
                    "--pdf", str(c / "no.pdf"), "--fuente", "f", "--salida", str(c / "s.md")]
            self.assertEqual(rrc.main(args), 2)
            self.assertFalse((c / "s.md").exists())


if __name__ == "__main__":
    unittest.main()
