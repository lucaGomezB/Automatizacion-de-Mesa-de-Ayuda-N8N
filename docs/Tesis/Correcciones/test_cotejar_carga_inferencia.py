"""Pruebas de cotejar_carga_inferencia.py (c-243, tareas 1.1 a 1.5, Strict TDD).

Cubren la extraccion de las ocho filas de `tab:carga-inferencia`, el orden
capa/nivel, la corrida de origen y el n rotulados por fila, el redondeo por
columna, el cociente de inferencia recalculado, el veredicto del nivel derivado
del criterio por capa y el codigo de salida de la CLI. La tabla de referencia se
define una sola vez (`TABLA_VALIDA`) y las mutaciones se aplican sobre copias en
un directorio temporal.
"""
import tempfile
import unittest
from pathlib import Path

import cotejar_carga_inferencia as cci

RAIZ = Path(__file__).resolve().parents[3]
RUTA_TEX_REAL = RAIZ / "docs" / "Tesis" / "v10 (IA)" / "paper" / "sections" / "07-resultados.tex"
RUTA_AMPLIADA = RAIZ / "evaluation" / "evidence" / "load_test_inferencia_ampliada_2026-11-18.json"
RUTA_ORIGINAL = RAIZ / "evaluation" / "evidence" / "load_test_inferencia_2026-11-17.json"

# Tabla de referencia valida (opcion A: niveles 1 y 5 ampliados; 10 y 20 originales).
TABLA_VALIDA = r"""
\begin{table}[htbp]
\centering
\caption{Latencia del tramo compartido con inferencia incluida}
\label{tab:carga-inferencia}
\footnotesize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}llccccccccc@{}}
\toprule
\textbf{Capa} & \textbf{Corrida/n} & \textbf{Conc.} & \textbf{p50 (ms)} & \textbf{p95 (ms)} & \textbf{p99 (ms)} & \textbf{Throughput (sol./s)} & \textbf{Tasa de error} & \textbf{Escalados} & \textbf{\(r\)} & \textbf{Veredicto del nivel} \\
\midrule
Backend & ampl. 90 & 1 & 1007,6 & 2089,3 & 2330,6 & 0,93 & 0,0000 & 90/180 & 5,05 & no cumple (inferencia) \\
Backend & ampl. 90 & 5 & 1221,9 & 2708,4 & 3968,1 & 3,50 & 0,0000 & 90/180 & 3,74 & cumple \\
Backend & orig. 10 & 10 & 1182,9 & 2759,6 & 2763,9 & 6,03 & 0,0000 & 10/20 & 3,55 & cumple \\
Backend & orig. 10 & 20 & 2185,3 & 3424,2 & 3445,8 & 5,76 & 0,0000 & 10/20 & 1,93 & cumple \\
\midrule
\emph{Webhook} de N8N & ampl. 90 & 1 & 1757,9 & 2919,8 & 5033,4 & 0,56 & 0,0000 & 90/180 & 2,35 & cumple \\
\emph{Webhook} de N8N & ampl. 90 & 5 & 4307,7 & 7545,7 & 8684,4 & 1,07 & 0,0000 & 90/180 & 1,70 & no cumple (techo) \\
\emph{Webhook} de N8N & orig. 10 & 10 & 4519,8 & 8352,7 & 8596,7 & 1,83 & 0,0000 & 10/20 & 1,58 & no cumple (techo) \\
\emph{Webhook} de N8N & orig. 10 & 20 & 8378,2 & 10183,6 & 10197,6 & 1,96 & 0,0000 & 10/20 & 1,22 & no cumple (techo) \\
\bottomrule
\end{tabular}
\par\smallskip
{\footnotesize\textit{Nota:} latencia medida por el cliente. Fuente: los dos JSON de la sonda.}
\end{table}
"""


def _escribir_tex(texto):
    directorio = tempfile.mkdtemp()
    ruta = Path(directorio) / "07-resultados.tex"
    ruta.write_text(texto, encoding="utf-8")
    return ruta


class ExtraccionTest(unittest.TestCase):
    def test_extrae_las_ocho_filas(self):
        filas = cci.extraer_filas(TABLA_VALIDA)
        self.assertEqual(len(filas), 8)
        self.assertEqual(filas[0].capa, "backend")
        self.assertEqual(filas[4].capa, "n8n")

    def test_normaliza_capa_backend_y_webhook(self):
        self.assertEqual(cci.normalizar_capa("Backend"), "backend")
        self.assertEqual(cci.normalizar_capa(r"\emph{Webhook} de N8N"), "n8n")

    def test_parsea_corrida_y_n(self):
        self.assertEqual(cci.parsear_corrida("ampl. 90"), ("ampliada", 90))
        self.assertEqual(cci.parsear_corrida("orig. 10"), ("original", 10))

    def test_tabla_ausente_levanta(self):
        with self.assertRaises(cci.TablaAusente):
            cci.extraer_filas(r"\section{Sin tabla}")

    def test_formatea_con_coma_y_decimales(self):
        self.assertEqual(cci.formatear(1007.5981, 1), "1007,6")
        self.assertEqual(cci.formatear(0.9291003, 2), "0,93")
        self.assertEqual(cci.formatear(0.0, 4), "0,0000")


class VeredictoTest(unittest.TestCase):
    def test_backend_nivel_1_no_cumple_por_inferencia(self):
        datos = cci.cargar_json(RUTA_AMPLIADA)
        self.assertEqual(cci.derivar_veredicto_nivel(datos, "backend", 1), "no cumple (inferencia)")

    def test_backend_nivel_5_cumple(self):
        datos = cci.cargar_json(RUTA_AMPLIADA)
        self.assertEqual(cci.derivar_veredicto_nivel(datos, "backend", 5), "cumple")

    def test_n8n_nivel_5_no_cumple_por_techo(self):
        datos = cci.cargar_json(RUTA_AMPLIADA)
        self.assertEqual(cci.derivar_veredicto_nivel(datos, "n8n", 5), "no cumple (techo)")

    def test_n8n_nivel_20_no_cumple_por_techo(self):
        datos = cci.cargar_json(RUTA_ORIGINAL)
        self.assertEqual(cci.derivar_veredicto_nivel(datos, "n8n", 20), "no cumple (techo)")


class CotejoTest(unittest.TestCase):
    def _cotejar(self, texto):
        return cci.cotejar(_escribir_tex(texto), RUTA_AMPLIADA, RUTA_ORIGINAL)

    def test_tabla_valida_sin_fallas(self):
        self.assertEqual(self._cotejar(TABLA_VALIDA), [])

    def test_tabla_ausente_falla_con_mensaje(self):
        fallas = self._cotejar(r"\section{Sin tabla}")
        self.assertEqual(len(fallas), 1)
        self.assertIn("tabla ausente", fallas[0].mensaje)

    def test_fila_ausente_falla(self):
        mutada = TABLA_VALIDA.replace(
            "Backend & ampl. 90 & 5 & 1221,9 & 2708,4 & 3968,1 & 3,50 & 0,0000 & 90/180 & 3,74 & cumple ",
            "",
        )
        fallas = self._cotejar(mutada)
        self.assertTrue(any(f.campo in ("conteo", "fila") for f in fallas))
        self.assertTrue(any("ausente" in f.mensaje for f in fallas))

    def test_capa_invertida_falla(self):
        mutada = TABLA_VALIDA.replace(
            "Backend & orig. 10 & 10 &", r"\emph{Webhook} de N8N & orig. 10 & 10 &"
        )
        fallas = self._cotejar(mutada)
        self.assertTrue(any(f.campo == "orden" for f in fallas))

    def test_redondeo_erroneo_falla(self):
        mutada = TABLA_VALIDA.replace("1007,6 &", "1007,60 &")
        fallas = self._cotejar(mutada)
        self.assertTrue(any(f.campo == "p50" for f in fallas))

    def test_cociente_que_no_cierra_falla(self):
        mutada = TABLA_VALIDA.replace("& 5,05 &", "& 5,50 &")
        fallas = self._cotejar(mutada)
        self.assertTrue(any(f.campo == "r" for f in fallas))

    def test_tasa_de_error_distinta_de_cero_falla(self):
        mutada = TABLA_VALIDA.replace("0,0000 & 90/180", "0,0100 & 90/180", 1)
        fallas = self._cotejar(mutada)
        self.assertTrue(any(f.campo == "error" for f in fallas))

    def test_veredicto_incoherente_falla(self):
        mutada = TABLA_VALIDA.replace("no cumple (inferencia)", "cumple")
        fallas = self._cotejar(mutada)
        self.assertTrue(any(f.campo == "veredicto" for f in fallas))

    def test_corrida_de_origen_equivocada_falla(self):
        mutada = TABLA_VALIDA.replace(
            "Backend & ampl. 90 & 1 & 1007,6", "Backend & orig. 10 & 1 & 1007,6"
        )
        fallas = self._cotejar(mutada)
        self.assertTrue(any(f.campo == "corrida" for f in fallas))


class CliTest(unittest.TestCase):
    def test_codigo_0_con_tabla_valida(self):
        ruta = _escribir_tex(TABLA_VALIDA)
        codigo = cci.main(
            ["--tex", str(ruta), "--evidencia-ampliada", str(RUTA_AMPLIADA), "--evidencia-original", str(RUTA_ORIGINAL)]
        )
        self.assertEqual(codigo, 0)

    def test_codigo_1_con_copia_mutada(self):
        ruta = _escribir_tex(TABLA_VALIDA.replace("& 5,05 &", "& 5,50 &"))
        codigo = cci.main(
            ["--tex", str(ruta), "--evidencia-ampliada", str(RUTA_AMPLIADA), "--evidencia-original", str(RUTA_ORIGINAL)]
        )
        self.assertEqual(codigo, 1)

    def test_help_no_falla(self):
        with self.assertRaises(SystemExit) as contexto:
            cci.main(["--help"])
        self.assertEqual(contexto.exception.code, 0)


class TablaRealTest(unittest.TestCase):
    def test_tabla_real_coteja_sin_fallas_si_existe(self):
        if not RUTA_TEX_REAL.exists():
            self.skipTest("07-resultados.tex no esta disponible")
        if r"\label{tab:carga-inferencia}" not in RUTA_TEX_REAL.read_text(encoding="utf-8"):
            self.skipTest("la tabla tab:carga-inferencia aun no esta escrita")
        fallas = cci.cotejar(RUTA_TEX_REAL, RUTA_AMPLIADA, RUTA_ORIGINAL)
        self.assertEqual(fallas, [])


if __name__ == "__main__":
    unittest.main()
