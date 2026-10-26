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
    def test_extrae_solo_las_filas_de_la_seccion_de_cobertura(self):
        filas = vmt.parsear_matriz(MATRIZ)
        self.assertEqual([f["rec"] for f in filas], ["A1", "B16b"])

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

    def test_fragmento_ausente_en_la_linea_falla(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], linea=1)
        ok, msg = vmt.verificar_fila(fila, leer)
        self.assertFalse(ok)
        self.assertIn("fragmento", msg)

    def test_ancla_inexistente_falla(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], ancla="subsec:otro")
        ok, msg = vmt.verificar_fila(fila, leer)
        self.assertFalse(ok)
        self.assertIn("ancla", msg)

    def test_linea_fuera_de_rango_falla(self):
        fila = dict(vmt.parsear_matriz(MATRIZ)[0], linea=99)
        ok, msg = vmt.verificar_fila(fila, leer)
        self.assertFalse(ok)
        self.assertIn("rango", msg)

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


if __name__ == "__main__":
    unittest.main()
