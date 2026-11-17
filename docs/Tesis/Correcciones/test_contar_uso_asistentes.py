"""Pruebas de contar_uso_asistentes.py (c-237, tareas 1.1 a 1.7).

Se ejecutan desde docs/Tesis/Correcciones/:
    python -m unittest test_contar_uso_asistentes -v

Estilo de `test_resumir_registro_compilacion.py`: funciones puras, I/O de git
aislado por `_git` (parcheable en las pruebas), sin datos personales.
"""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import contar_uso_asistentes as cua

# Log sintetico con el formato que produce main:
#   %H%x09%ad%x09%(trailers:key=Co-Authored-By,valueonly,separator=|)
LOG_SIN_TRAILERS = (
    "aaaaaaa\t2026-04-06\t\n"
    "bbbbbbb\t2026-04-07\t\n"
)

LOG_CON_TRAILERS = (
    "ccccccc\t2026-05-21\tClaude Fable 5.1 <noreply@example.com>\n"
    "ddddddd\t2026-05-22\tClaude Opus 5.5 <noreply@example.com>\n"
    "eeeeeee\t2026-05-23\tClaude Fable 5.1 <noreply@example.com>\n"
    "fffffff\t2026-05-24\t\n"
)

# Caso no observado en el repositorio: un commit con dos marcas de asistente.
LOG_CON_VARIOS_EN_UN_COMMIT = (
    "9999999\t2026-05-27\tClaude Fable 5.1 <noreply@example.com>|Claude Sonnet 4.6 <noreply@example.com>\n"
)

LOG_CON_HUMANO = (
    "1111111\t2026-05-25\tClaude Fable 5.2 <noreply@example.com>\n"
    "2222222\t2026-05-26\tRevisor Humano <revisor@example.com>\n"
)


class ParsearLogTest(unittest.TestCase):
    def test_log_sin_trailers(self):
        commits = cua.parsear_log(LOG_SIN_TRAILERS)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].hash, "aaaaaaa")
        self.assertEqual(commits[0].fecha, "2026-04-06")
        self.assertEqual(commits[0].coautores, ())

    def test_log_con_trailers_de_varios_modelos(self):
        commits = cua.parsear_log(LOG_CON_TRAILERS)
        self.assertEqual([c.hash for c in commits], ["ccccccc", "ddddddd", "eeeeeee", "fffffff"])
        self.assertEqual(commits[0].coautores, ("Claude Fable 5.1",))
        self.assertEqual(commits[1].coautores, ("Claude Opus 5.5",))
        self.assertEqual(commits[3].coautores, ())

    def test_varios_trailers_en_un_commit(self):
        commits = cua.parsear_log(LOG_CON_VARIOS_EN_UN_COMMIT)
        self.assertEqual(
            commits[0].coautores, ("Claude Fable 5.1", "Claude Sonnet 4.6")
        )

    def test_no_expone_correos(self):
        commits = cua.parsear_log(LOG_CON_TRAILERS)
        for commit in commits:
            for nombre in commit.coautores:
                self.assertNotIn("@", nombre)

    def test_linea_vacia_o_malformada_se_ignora(self):
        texto = "\n" + LOG_SIN_TRAILERS + "solo_dos_campos\t2026-01-01\n\t\t\n"
        commits = cua.parsear_log(texto)
        self.assertEqual(len(commits), 2)

    def test_log_vacio(self):
        self.assertEqual(cua.parsear_log(""), [])


class ContarTest(unittest.TestCase):
    def test_total_con_y_sin_trailer(self):
        conteo = cua.contar(cua.parsear_log(LOG_CON_TRAILERS))
        self.assertEqual(conteo.total, 4)
        self.assertEqual(conteo.con_trailer, 3)
        self.assertEqual(conteo.sin_trailer, 1)

    def test_desglose_por_modelo_suma_el_total_marcado(self):
        conteo = cua.contar(cua.parsear_log(LOG_CON_TRAILERS))
        self.assertEqual(conteo.por_modelo["Claude Fable 5.1"], 2)
        self.assertEqual(conteo.por_modelo["Claude Opus 5.5"], 1)
        self.assertEqual(sum(conteo.por_modelo.values()), conteo.con_trailer)

    def test_commit_con_dos_asistentes_cuenta_una_vez_y_en_ambos_modelos(self):
        conteo = cua.contar(cua.parsear_log(LOG_CON_VARIOS_EN_UN_COMMIT))
        self.assertEqual(conteo.con_trailer, 1)
        self.assertEqual(conteo.por_modelo["Claude Fable 5.1"], 1)
        self.assertEqual(conteo.por_modelo["Claude Sonnet 4.6"], 1)

    def test_coautor_humano_va_a_otros_y_no_cuenta_como_asistencia(self):
        conteo = cua.contar(cua.parsear_log(LOG_CON_HUMANO))
        self.assertEqual(conteo.con_trailer, 1)
        self.assertEqual(conteo.por_modelo, {"Claude Fable 5.2": 1})
        self.assertEqual(conteo.otros_coautores, {"Revisor Humano": 1})

    def test_log_vacio(self):
        conteo = cua.contar([])
        self.assertEqual((conteo.total, conteo.con_trailer, conteo.sin_trailer), (0, 0, 0))
        self.assertEqual(conteo.por_modelo, {})
        self.assertEqual(conteo.otros_coautores, {})

    def test_es_asistente(self):
        self.assertTrue(cua.es_asistente("Claude Fable 5"))
        self.assertTrue(cua.es_asistente("Gemini 3.1"))
        self.assertFalse(cua.es_asistente("Revisor Humano"))
        self.assertFalse(cua.es_asistente("Claudia Ejemplo"))


class ClasificarChangeTest(unittest.TestCase):
    def test_prosa_tex(self):
        self.assertEqual(
            cua.clasificar_change("Editar `docs/Tesis/v10 (IA)/paper/sections/12.tex`"),
            {"prosa"},
        )

    def test_codigo_app(self):
        self.assertEqual(
            cua.clasificar_change("Crear `App/Backend/app/services/x.py`"), {"codigo"}
        )

    def test_analisis_evaluation_y_correcciones(self):
        self.assertEqual(
            cua.clasificar_change("Correr `evaluation/scripts/medir.py`"), {"analisis"}
        )
        self.assertEqual(
            cua.clasificar_change("Crear `docs/Tesis/Correcciones/contar.py`"), {"analisis"}
        )

    def test_n8n_workflow(self):
        self.assertEqual(
            cua.clasificar_change("Importar `n8n/workflow.json`"), {"n8n"}
        )

    def test_sin_rutas(self):
        self.assertEqual(cua.clasificar_change("Revisar la redaccion del resumen"), set())

    def test_varios_ambitos(self):
        texto = "Tocar `App/Frontend/src/x.tsx`, `n8n/workflow.json` y un `.py` en `evaluation/`"
        self.assertEqual(
            cua.clasificar_change(texto), {"codigo", "analisis", "n8n"}
        )


class RenderizarMarkdownTest(unittest.TestCase):
    def _periodos(self):
        return [
            {
                "etiqueta": "Historial hasta v1.5.2",
                "ref": "v1.5.2",
                "conteo": cua.contar(cua.parsear_log(LOG_CON_TRAILERS)),
            },
        ]

    def test_contiene_las_cifras(self):
        md = cua.renderizar_markdown(self._periodos(), {"prosa": ["c-222"]})
        self.assertIn("4", md)
        self.assertIn("Claude Fable 5.1", md)
        self.assertIn("c-222", md)

    def test_es_determinista_y_sin_arroba(self):
        a = cua.renderizar_markdown(self._periodos(), {"prosa": ["c-222"]})
        b = cua.renderizar_markdown(self._periodos(), {"prosa": ["c-222"]})
        self.assertEqual(a, b)
        self.assertNotIn("@", a)
        self.assertTrue(a.endswith("\n"))

    def test_orden_estable_de_modelos(self):
        periodos = self._periodos() + [
            {
                "etiqueta": "Multi",
                "ref": "x",
                "conteo": cua.contar(cua.parsear_log(LOG_CON_VARIOS_EN_UN_COMMIT)),
            }
        ]
        md = cua.renderizar_markdown(periodos, {})
        self.assertLess(md.index("Claude Fable 5.1"), md.index("Claude Opus 5.5"))
        self.assertLess(md.index("Claude Opus 5.5"), md.index("Claude Sonnet 4.6"))


class MainTest(unittest.TestCase):
    def _preparar(self, carpeta):
        archivo = carpeta / "archive"
        (archivo / "2026-01-01-c-001-x").mkdir(parents=True)
        (archivo / "2026-01-01-c-001-x" / "tasks.md").write_text(
            "## Prosa de la tesis\ndocs/Tesis/x.tex\n", encoding="utf-8"
        )
        (archivo / "2026-01-02-c-002-y").mkdir(parents=True)
        (archivo / "2026-01-02-c-002-y" / "tasks.md").write_text(
            "App/Backend/app/main.py\n", encoding="utf-8"
        )
        return archivo

    def test_main_escribe_y_es_reproducible(self):
        with tempfile.TemporaryDirectory() as d:
            carpeta = Path(d)
            archivo = self._preparar(carpeta)
            salida = carpeta / "frag.md"
            args = [
                "--ref", "v1.5.2", "--archivo-changes", str(archivo),
                "--salida", str(salida),
            ]
            with mock.patch.object(cua, "_git", return_value=LOG_CON_TRAILERS):
                self.assertEqual(cua.main(args), 0)
                primero = salida.read_bytes()
                self.assertEqual(cua.main(args), 0)
                self.assertEqual(salida.read_bytes(), primero)
            texto = primero.decode("utf-8")
            self.assertEqual(texto.count("@"), 0)
            self.assertIn("v1.5.2", texto)
            self.assertIn("c-001-x", texto)

    def test_main_con_desde_ref(self):
        with tempfile.TemporaryDirectory() as d:
            carpeta = Path(d)
            archivo = self._preparar(carpeta)
            salida = carpeta / "frag.md"
            llamadas = []

            def falso_git(args):
                llamadas.append(args)
                return LOG_CON_TRAILERS

            with mock.patch.object(cua, "_git", side_effect=falso_git):
                cua.main([
                    "--ref", "v1.5.2", "--desde-ref", "v1.2.18",
                    "--archivo-changes", str(archivo), "--salida", str(salida),
                ])
            self.assertTrue(any("v1.2.18..v1.5.2" in a for a in llamadas))
            self.assertIn("v1.2.18", salida.read_text(encoding="utf-8"))

    def test_main_falla_si_falta_el_arbol(self):
        with tempfile.TemporaryDirectory() as d:
            carpeta = Path(d)
            args = [
                "--ref", "v1.5.2",
                "--archivo-changes", str(carpeta / "no-existe"),
                "--salida", str(carpeta / "frag.md"),
            ]
            with mock.patch.object(cua, "_git", return_value=LOG_SIN_TRAILERS):
                self.assertEqual(cua.main(args), 2)
            self.assertFalse((carpeta / "frag.md").exists())


if __name__ == "__main__":
    unittest.main()
