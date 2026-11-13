"""
Tests del reporte fuera de muestra del corpus arbitrado (c-206, tarea 6.2).

Prueban el camino de codigo documentado en el runbook con los artefactos SINTETICOS del
fixture de la campana (12 casos out-of-sample): reutiliza `evaluar_fuera_de_muestra` y
`resumen_exactitud`, no reclasifica y no llama a Gemini.
"""

from __future__ import annotations


from evaluation.tests import helpers_campana as h


def test_reporta_el_n_efectivo_sin_exclusion_y_las_clases_estimables():
    from evaluation.reporte_arbitrado import resumir_fuera_de_muestra_arbitrado

    reporte = resumir_fuera_de_muestra_arbitrado(
        h.PREDICCIONES_IN_SAMPLE,
        h.CORPUS_CAMPANA,
        h.PREDICCIONES_INDEPENDIENTE,
        h.CORPUS_INDEPENDIENTE,
    )

    assert reporte.obtenido is True
    assert reporte.n_efectivo == 12
    assert sum(clase.n for clase in reporte.por_clase) == 12
    assert all(clase.estimable for clase in reporte.por_clase)
    assert {clase.sector for clase in reporte.por_clase} == {
        "Seguridad Informatica",
        "Soporte Tecnico Hardware",
        "Soporte Tecnico Software",
        "Bases de Datos",
        "Sistemas",
    }


def test_formatea_el_n_efectivo_y_la_estimabilidad_por_clase():
    from evaluation.reporte_arbitrado import (
        formatear_reporte,
        resumir_fuera_de_muestra_arbitrado,
    )

    reporte = resumir_fuera_de_muestra_arbitrado(
        h.PREDICCIONES_IN_SAMPLE,
        h.CORPUS_CAMPANA,
        h.PREDICCIONES_INDEPENDIENTE,
        h.CORPUS_INDEPENDIENTE,
    )

    texto = formatear_reporte(reporte)

    assert "n efectivo (sin exclusion): 12" in texto
    assert "metricas por clase" in texto
    assert texto.count("estimable") >= 5


def test_sin_el_cache_arbitrado_declara_no_obtenido_y_nombra_el_artefacto(tmp_path):
    from evaluation.reporte_arbitrado import resumir_fuera_de_muestra_arbitrado

    reporte = resumir_fuera_de_muestra_arbitrado(
        h.PREDICCIONES_IN_SAMPLE,
        h.CORPUS_CAMPANA,
        tmp_path / "predicciones_arbitrado.json",
        h.CORPUS_INDEPENDIENTE,
    )

    assert reporte.obtenido is False
    assert "predicciones_arbitrado.json" in (reporte.motivo or "")
    assert reporte.n_efectivo == 0


def test_main_sale_con_dos_cuando_no_se_obtuvo(tmp_path, capsys):
    from evaluation.reporte_arbitrado import main

    codigo = main(
        [
            "--predicciones-in-sample",
            str(h.PREDICCIONES_IN_SAMPLE),
            "--corpus-ajuste",
            str(h.CORPUS_CAMPANA),
            "--predicciones-arbitrado",
            str(tmp_path / "no.json"),
            "--corpus-arbitrado",
            str(h.CORPUS_INDEPENDIENTE),
        ]
    )

    assert codigo == 2
    assert "no se obtuvo" in capsys.readouterr().out


def test_main_sale_con_cero_con_los_artefactos_completos(capsys):
    from evaluation.reporte_arbitrado import main

    codigo = main(
        [
            "--predicciones-in-sample",
            str(h.PREDICCIONES_IN_SAMPLE),
            "--corpus-ajuste",
            str(h.CORPUS_CAMPANA),
            "--predicciones-arbitrado",
            str(h.PREDICCIONES_INDEPENDIENTE),
            "--corpus-arbitrado",
            str(h.CORPUS_INDEPENDIENTE),
        ]
    )

    salida = capsys.readouterr().out
    assert codigo == 0
    assert "n efectivo (sin exclusion): 12" in salida
