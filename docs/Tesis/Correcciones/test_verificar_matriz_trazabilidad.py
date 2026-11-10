"""Pruebas de verificar_matriz_trazabilidad.py (c-141, tarea 6.1)."""
import unittest

import verificar_matriz_trazabilidad as vmt

MATRIZ = """## Otro grupo

| x | y |
|---|---|
| a | b |

## Dictamen v10 / v1.1.0 (2026-10-22) - cobertura por change (FASE 36)

Texto previo.

| Rec | Sintesis | Change | Archivo:linea en v1.2.0 | Ancla | Fragmento verificable | Estado |
|---|---|---|---|---|---|---|
| A1 | Gate acotado | c-130 | `a/b.tex:3` | `subsec:uno` | `hola mundo` | cerrada |
| B16b | Version del repositorio | c-141 | `a/c.bib:7` | - | `1.2.0` | PENDIENTE: C1 |

### Rubrica

| Criterio | Peso | Puntaje | Descuento | Change | Estado | Evidencia |
|---|---|---|---|---|---|---|
| 1 Definicion | 15 | 8,5 | x | c-133 | aplicado | B5 |

## Siguiente seccion

| Rec | Sintesis | Change | Archivo:linea en v1.2.0 | Ancla | Fragmento verificable | Estado |
|---|---|---|---|---|---|---|
| Z9 | fuera | c-999 | `z.tex:1` | - | `no` | cerrada |
"""

ARCHIVOS = {
    "a/b.tex": ["linea uno", "\\label{subsec:uno}", "dice hola mundo aqui"],
    "a/c.bib": ["x"] * 8,
}


def leer(ruta):
    return ARCHIVOS[ruta]


class ParseTest(unittest.TestCase):
    def test_extrae_las_filas_de_toda_matriz_de_siete_columnas(self):
        filas = vmt.parsear_matriz(MATRIZ)
        self.assertEqual([f["rec"] for f in filas], ["A1", "B16b", "Z9"])

    def test_la_rubrica_sin_fragmento_verificable_no_se_parsea(self):
        recs = [f["rec"] for f in vmt.parsear_matriz(MATRIZ)]
        self.assertNotIn("1 Definicion", recs)

    def test_cada_fila_registra_su_seccion_de_origen(self):
        filas = vmt.parsear_matriz(MATRIZ)
        self.assertIn("cobertura por change", filas[0]["seccion"])
        self.assertEqual(filas[2]["seccion"], "Siguiente seccion")

    def test_separa_archivo_linea_y_limpia_los_acentos_graves(self):
        fila = vmt.parsear_matriz(MATRIZ)[0]
        self.assertEqual(fila["archivo"], "a/b.tex")
        self.assertEqual(fila["linea"], 3)
        self.assertEqual(fila["ancla"], "subsec:uno")
        self.assertEqual(fila["fragmento"], "hola mundo")


class VerificarTest(unittest.TestCase):
    def test_fila_correcta_pasa(self):
        fila = vmt.parsear_matriz(MATRIZ)[0]
        ok, _ = vmt.verificar_fila(fila, leer)
        self.assertTrue(ok)

    def test_fragmento_ausente_del_archivo_falla(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], fragmento="texto inexistente")
        ok, msg = vmt.verificar_fila(fila, leer)
        self.assertFalse(ok)
        self.assertIn("texto inexistente", msg)

    def test_ancla_inexistente_falla(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], ancla="subsec:otro")
        ok, msg = vmt.verificar_fila(fila, leer)
        self.assertFalse(ok)
        self.assertIn("ancla", msg)

    def test_linea_fuera_de_rango_con_fragmento_presente_es_desplazamiento(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], linea=99)
        ok, msg = vmt.verificar_fila(fila, leer)
        self.assertTrue(ok)
        self.assertIn("desplazada 99 -> 3", msg)

    def test_fila_pendiente_se_omite(self):
        fila = vmt.parsear_matriz(MATRIZ)[1]
        ok, msg = vmt.verificar_fila(fila, leer)
        self.assertTrue(ok)
        self.assertIn("omitida", msg)

    def test_ancla_con_guion_no_se_comprueba(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], ancla="-")
        ok, _ = vmt.verificar_fila(fila, leer)
        self.assertTrue(ok)


class ReubicarTest(unittest.TestCase):
    def test_encuentra_la_nueva_linea_del_fragmento(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], linea=1)
        self.assertEqual(vmt.reubicar_fila(fila, leer), 3)

    def test_sin_coincidencias_devuelve_none(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], fragmento="texto inexistente")
        self.assertIsNone(vmt.reubicar_fila(fila, leer))

    def test_actualiza_la_celda_del_registro(self):
        texto = "| A1 | s | c-130 | `a/b.tex:1` | `x` | `hola mundo` | cerrada |"
        nuevo = vmt.reemplazar_linea(texto, "a/b.tex", 1, 3)
        self.assertIn("`a/b.tex:3`", nuevo)
        self.assertNotIn("`a/b.tex:1`", nuevo)


class DesplazamientoTest(unittest.TestCase):
    def test_fragmento_en_otra_linea_pasa_con_aviso(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], linea=1)
        ok, msg = vmt.verificar_fila(fila, leer)
        self.assertTrue(ok)
        self.assertIn("desplazada 1 -> 3", msg)

    def test_otro_desplazamiento_informa_la_linea_real(self):
        archivos = {"a/b.tex": ["x", "x", "x", "x", "x", "\\label{subsec:uno}", "hola mundo"]}
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], linea=2)
        ok, msg = vmt.verificar_fila(fila, lambda r: archivos[r])
        self.assertTrue(ok)
        self.assertIn("desplazada 2 -> 7", msg)

    def test_estricto_exige_la_linea_exacta(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], linea=1)
        ok, msg = vmt.verificar_fila(fila, leer, estricto=True)
        self.assertFalse(ok)
        self.assertIn("linea", msg)

    def test_estricto_acepta_la_linea_exacta(self):
        fila = vmt.parsear_matriz(MATRIZ)[0]
        ok, msg = vmt.verificar_fila(fila, leer, estricto=True)
        self.assertTrue(ok)
        self.assertNotIn("desplazada", msg)

    def test_ancla_inexistente_falla_aunque_el_fragmento_este_desplazado(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], linea=1, ancla="subsec:otro")
        ok, msg = vmt.verificar_fila(fila, leer)
        self.assertFalse(ok)
        self.assertIn("ancla", msg)


class SuperadaTest(unittest.TestCase):
    def test_estado_superada_se_omite(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], estado="SUPERADA por c-187", fragmento="no esta")
        ok, msg = vmt.verificar_fila(fila, leer)
        self.assertTrue(ok)
        self.assertIn("omitida", msg)

    def test_superada_en_minusculas_tambien(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], estado="superada por c-160", fragmento="no esta")
        ok, _ = vmt.verificar_fila(fila, leer)
        self.assertTrue(ok)

    def test_superada_sin_change_se_rechaza(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], estado="SUPERADA", fragmento="no esta")
        ok, msg = vmt.verificar_fila(fila, leer)
        self.assertFalse(ok)
        self.assertIn("c-NNN", msg)


class RutaTest(unittest.TestCase):
    def test_nombre_suelto_de_seccion_se_resuelve_a_sections(self):
        self.assertEqual(
            vmt.resolver_ruta("05-arquitectura.tex"),
            "docs/Tesis/v10 (IA)/paper/sections/05-arquitectura.tex",
        )

    def test_ruta_completa_se_conserva(self):
        r = "docs/Tesis/v10 (IA)/paper/sections/02-marco-teorico.tex"
        self.assertEqual(vmt.resolver_ruta(r), r)

    def test_ruta_relativa_con_directorio_se_conserva(self):
        self.assertEqual(vmt.resolver_ruta("a/b.tex"), "a/b.tex")


class ResumenPorSeccionTest(unittest.TestCase):
    def test_cuenta_filas_avisos_y_fallas_por_seccion(self):
        resultados = [
            ("S1", True, "A: ok (x:1)"),
            ("S1", True, "B: ok desplazada 1 -> 3 (x)"),
            ("S1", False, "C: falla"),
            ("S2", True, "D: ok"),
        ]
        r = vmt.resumen_por_seccion(resultados)
        self.assertEqual(r["S1"], {"filas": 3, "avisos": 1, "fallas": 1})
        self.assertEqual(r["S2"], {"filas": 1, "avisos": 0, "fallas": 0})

    def test_sin_resultados_devuelve_vacio(self):
        self.assertEqual(vmt.resumen_por_seccion([]), {})

    def test_el_texto_del_resumen_nombra_cada_seccion(self):
        r = {"S1": {"filas": 3, "avisos": 1, "fallas": 1}}
        texto = vmt.formatear_resumen(r)
        self.assertIn("S1", texto)
        self.assertIn("filas: 3", texto)
        self.assertIn("fallas: 1", texto)

ENCAB = "| Rec | Sintesis | Change | Archivo:linea | Ancla | Fragmento verificable | Estado |\n|---|---|---|---|---|---|---|\n"
FILA_OK = "| A1 | s | c-192 | `a/b.tex:3` | `subsec:uno` | `hola mundo` | cerrada |\n"


class SeccionesSinMatrizTest(unittest.TestCase):
    """c-195 A3: un ciclo de correcciones (change >= 190) sin matriz no pasa inadvertido."""

    def test_seccion_c192_sin_matriz_se_devuelve(self):
        texto = "## Dictamen v10 / v1.2.13 (2026-11-09) - c-192\n\n| a | b |\n|---|---|\n| 1 | 2 |\n"
        self.assertEqual(
            vmt.secciones_sin_matriz(texto),
            ["Dictamen v10 / v1.2.13 (2026-11-09) - c-192"],
        )

    def test_seccion_c192_con_matriz_no_se_devuelve(self):
        texto = "## Dictamen v10 / v1.2.13 (2026-11-09) - c-192\n\n" + ENCAB + FILA_OK
        self.assertEqual(vmt.secciones_sin_matriz(texto), [])

    def test_seccion_c188_sin_matriz_no_se_cuenta(self):
        texto = "## Dictamen v10 / v1.2.10 (2026-11-08) - c-188\n\ntexto\n"
        self.assertEqual(vmt.secciones_sin_matriz(texto), [])

    def test_titulo_sin_change_no_se_cuenta(self):
        texto = "## Dictamen v10 / v1.2.13 (2026-11-09)\n\ntexto\n"
        self.assertEqual(vmt.secciones_sin_matriz(texto), [])

    def test_dos_secciones_una_con_y_otra_sin_matriz(self):
        texto = (
            "## Dictamen v10 / v1.2.13 (2026-11-09) - c-192\n\n" + ENCAB + FILA_OK
            + "\n## Dictamen v10 / v1.2.13 (2026-11-09) - c-193 (nivel pago)\n\ntexto\n"
        )
        self.assertEqual(
            vmt.secciones_sin_matriz(texto),
            ["Dictamen v10 / v1.2.13 (2026-11-09) - c-193 (nivel pago)"],
        )

    def test_se_usa_el_ultimo_change_del_titulo_y_el_umbral_es_parametro(self):
        texto = "## Dictamen v10 / v1.2.13 - c-150 y c-195\n\ntexto\n"
        self.assertEqual(len(vmt.secciones_sin_matriz(texto)), 1)
        self.assertEqual(vmt.secciones_sin_matriz(texto, desde=196), [])


class MainSeccionSinMatrizTest(unittest.TestCase):
    def _correr(self, registro):
        import contextlib
        import io
        import tempfile
        from pathlib import Path
        from unittest import mock

        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "registro.md"
            ruta.write_text(registro, encoding="utf-8")
            salida = io.StringIO()
            with mock.patch.object(vmt, "REGISTRO", ruta), mock.patch.object(
                vmt, "_lector", lambda rev: leer
            ), contextlib.redirect_stdout(salida):
                codigo = vmt.main([])
        return codigo, salida.getvalue()

    def test_registro_con_seccion_c19x_sin_matriz_devuelve_1_y_la_nombra(self):
        registro = (
            "## Dictamen v10 / v1.2.13 (2026-11-09) - c-192\n\n" + ENCAB + FILA_OK
            + "\n## Dictamen v10 / v1.2.13 (2026-11-09) - c-194 (residuales C)\n\ntexto\n"
        )
        codigo, salida = self._correr(registro)
        self.assertEqual(codigo, 1)
        self.assertIn("seccion sin matriz", salida)
        self.assertIn("c-194 (residuales C)", salida)

    def test_registro_con_todas_las_secciones_con_matriz_devuelve_0(self):
        registro = "## Dictamen v10 / v1.2.13 (2026-11-09) - c-192\n\n" + ENCAB + FILA_OK
        codigo, _ = self._correr(registro)
        self.assertEqual(codigo, 0)


if __name__ == "__main__":
    unittest.main()
