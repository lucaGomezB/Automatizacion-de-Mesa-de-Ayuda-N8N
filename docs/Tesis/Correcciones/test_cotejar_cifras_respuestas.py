"""Pruebas de cotejar_cifras_respuestas.py (c-239, tarea 1.1 a 1.4, Strict TDD).

Cubren la extraccion, la exclusion de contextos, la normalizacion, el cotejo
contra el ejemplar, la lista blanca, los valores retirados, los restos de LaTeX
y el codigo de salida de la CLI.
"""
import tempfile
import unittest
from pathlib import Path

import cotejar_cifras_respuestas as ccr


class ExtraccionTest(unittest.TestCase):
    def test_extrae_decimal_porcentaje_fraccion_signo_y_millar(self):
        texto = "vale 0,7971 y 73,5 % y 110/138 y −0,05 y 2.646 casos"
        vals = {c.normalizado for c in ccr.extraer_cifras(texto)}
        self.assertEqual(vals, {"0,7971", "73,5", "110/138", "-0,05", "2646"})

    def test_extrae_porcentaje_con_escape_latex(self):
        vals = {c.normalizado for c in ccr.extraer_cifras("una reduccion del 71,2~\\% del tiempo")}
        self.assertEqual(vals, {"71,2"})

    def test_excluye_comillas_invertidas_encabezados_alias_y_secciones(self):
        texto = "Q14. ver `ruta/10.5/archivo.py` y P3 y E1 y O2 y §7.3 y subsección 4.4"
        vals = [c.normalizado for c in ccr.extraer_cifras(texto)]
        self.assertEqual(vals, [])

    def test_normaliza_llave_coma_y_menos_unicode(self):
        self.assertEqual(ccr.normalizar_cifra("0{,}5569"), "0,5569")
        self.assertEqual(ccr.normalizar_cifra("−0,05"), "-0,05")

    def test_millar_con_punto_y_sin_punto_son_equivalentes(self):
        self.assertEqual(ccr.normalizar_cifra("2.646"), ccr.normalizar_cifra("2646"))

    def test_extrae_entero_de_dos_o_mas_digitos_pero_no_de_uno(self):
        vals = {c.normalizado for c in ccr.extraer_cifras("los 3 canales y los 147 casos")}
        self.assertEqual(vals, {"147"})

    def test_la_extraccion_maneja_llave_coma_en_el_texto(self):
        vals = {c.normalizado for c in ccr.extraer_cifras("el kappa fue 0{,}5569 moderado")}
        self.assertEqual(vals, {"0,5569"})


class CotejarTest(unittest.TestCase):
    def test_cifra_presente_en_el_ejemplar_pasa(self):
        self.assertEqual(ccr.cotejar("dice 0,7971", "el valor 0,7971 aqui"), [])

    def test_cifra_ausente_falla_con_su_linea(self):
        fallas = ccr.cotejar("linea uno\nlos 12345 casos", "sin esa cifra")
        self.assertEqual(len(fallas), 1)
        self.assertEqual(fallas[0].linea, 2)
        self.assertEqual(fallas[0].cifra, "12345")

    def test_cifra_en_lista_blanca_pasa(self):
        self.assertEqual(ccr.cotejar("los 12345 casos", "sin esa cifra", ["12345"]), [])

    def test_valor_retirado_fuera_de_oracion_de_retiro_falla(self):
        fallas = ccr.cotejar("el balance fue -18,5", "menciona -18,5", [])
        self.assertTrue(any(f.tipo == "retirada" for f in fallas))

    def test_valor_retirado_en_oracion_de_retiro_pasa(self):
        fallas = ccr.cotejar(
            "el balance de -18,5 queda retirado", "menciona -18,5", []
        )
        self.assertFalse(any(f.tipo == "retirada" for f in fallas))

    def test_valor_retirado_superado_en_oracion_pasa(self):
        fallas = ccr.cotejar(
            "el balance de -43,9 queda superado", "menciona -43,9", []
        )
        self.assertFalse(any(f.tipo == "retirada" for f in fallas))

    def test_resto_de_latex_falla(self):
        fallas = ccr.cotejar("un valor 73,5~\\%del total", "73,5", [])
        self.assertTrue(any(f.tipo == "latex" for f in fallas))

    def test_resto_llave_coma_falla(self):
        fallas = ccr.cotejar("kappa de 0{,}5569", "0,5569", [])
        self.assertTrue(any(f.tipo == "latex" for f in fallas))

    def test_cifra_numerada_en_la_lista_blanca_por_justificacion(self):
        fallas = ccr.cotejar("el 16 de noviembre", "sin fechas", ["16"])
        self.assertEqual(fallas, [])

    def test_millar_con_punto_equivale_al_entero_sin_punto(self):
        self.assertEqual(ccr.cotejar("los 2.646 incidentes", "el universo es 2646"), [])

    def test_206_como_evidencia_falla(self):
        fallas = ccr.cotejar("se evaluaron 206 casos", "los 206 textos")
        self.assertTrue(any(f.tipo == "retirada" and f.cifra == "206" for f in fallas))

    def test_206_en_oracion_de_retiro_pasa(self):
        fallas = ccr.cotejar("los 206 casos quedan retirados", "los 206 textos")
        self.assertFalse(any(f.tipo == "retirada" for f in fallas))

    def test_fraccion_retirada_falla(self):
        fallas = ccr.cotejar("la exactitud fue 142/206", "142/206")
        self.assertTrue(any(f.tipo == "retirada" for f in fallas))

    def test_documento_mixto_informa_solo_la_ausente(self):
        fallas = ccr.cotejar("0,7971 esta; el 98765 no esta", "contiene 0,7971")
        self.assertEqual([f.cifra for f in fallas], ["98765"])

    def test_identificadores_y_aliases_no_se_extraen(self):
        texto = "N-01, K-02, c-235, R001, I151, E3, E4, E5, T1, T2 y Anexo I.2"
        self.assertEqual(ccr.extraer_cifras(texto), [])


class ListaBlancaTest(unittest.TestCase):
    def test_lee_tsv_y_normaliza_las_cifras(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "lb.tsv"
            p.write_text("cifra\tjustificacion\n16\tfecha de la devolucion\n2.646\tuniverso\n", encoding="utf-8")
            self.assertEqual(ccr.leer_lista_blanca(p), {"16", "2646"})

    def test_ignora_encabezado_y_lineas_vacias(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "lb.tsv"
            p.write_text("cifra\tjustificacion\n\n11\tfecha\n", encoding="utf-8")
            self.assertEqual(ccr.leer_lista_blanca(p), {"11"})


class CliTest(unittest.TestCase):
    def _archivos(self, respuestas, ejemplar, lista=None):
        d = tempfile.mkdtemp()
        r = Path(d) / "respuestas.md"
        e = Path(d) / "ejemplar.txt"
        r.write_text(respuestas, encoding="utf-8")
        e.write_text(ejemplar, encoding="utf-8")
        args = ["--respuestas", str(r), "--ejemplar", str(e)]
        if lista is not None:
            lb = Path(d) / "lb.tsv"
            lb.write_text(lista, encoding="utf-8")
            args += ["--lista-blanca", str(lb)]
        return args

    def test_codigo_de_salida_0_sin_fallas(self):
        args = self._archivos("dice 0,7971", "el valor 0,7971")
        self.assertEqual(ccr.main(args), 0)

    def test_codigo_de_salida_1_con_fallas(self):
        args = self._archivos("dice 12345", "sin la cifra")
        self.assertEqual(ccr.main(args), 1)

    def test_codigo_de_salida_1_con_restos_de_latex(self):
        args = self._archivos("la reduccion fue 71,2~\\%", "71,2")
        self.assertEqual(ccr.main(args), 1)

    def test_lista_blanca_desde_la_cli(self):
        args = self._archivos("dice 12345", "sin la cifra", "cifra\tjustificacion\n12345\tcita del enunciado\n")
        self.assertEqual(ccr.main(args), 0)


if __name__ == "__main__":
    unittest.main()
