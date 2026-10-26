"""Pruebas de build_tesis_para_agente.py (c-141, D8).

La release es un argumento obligatorio del script (sin valor por defecto) y la
lista ORDER debe coincidir con el orden de los \\input{sections/...} de main.tex.
Se ejecutan desde esta carpeta:

    python -m pytest test_build_tesis_para_agente.py -q -p no:cacheprovider
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import build_tesis_para_agente as build  # noqa: E402

SCRIPT = AQUI / "build_tesis_para_agente.py"
MAIN_TEX = AQUI / "paper" / "main.tex"
INPUT_RE = re.compile(r"^\\input\{sections/([^}]+)\}", re.M)


def correr(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, encoding="utf-8",
    )


# --- La release es obligatoria -------------------------------------------------

def test_sin_argumento_de_release_falla_y_no_escribe_nada():
    r = correr()
    assert r.returncode != 0
    assert r.stdout == ""
    assert "release" in r.stderr.lower()


def test_con_release_el_script_termina_bien():
    r = correr("v1.2.0")
    assert r.returncode == 0, r.stderr


def test_el_modulo_no_conserva_una_release_cableada():
    fuente = SCRIPT.read_text(encoding="utf-8")
    assert not re.search(r"v\d+\.\d+\.\d+", fuente)


# --- El encabezado declara la release recibida ---------------------------------

@pytest.mark.parametrize("release", ["v1.2.0", "v9.9.9"])
def test_encabezado_declara_la_release_recibida(release):
    encabezado = build.construir_encabezado(release)
    assert f"({build.WORKING_VERSION} / {release})" in encabezado
    assert f"release `{release}`" in encabezado


def test_la_salida_completa_empieza_con_el_encabezado_de_la_release():
    r = correr("v9.9.9")
    assert r.returncode == 0, r.stderr
    primera = r.stdout.splitlines()[0]
    assert primera.endswith("(v10 / v9.9.9)")
    assert "v1.1.1" not in r.stdout.split("---", 1)[0]


def test_dos_corridas_producen_la_misma_salida():
    a = correr("v1.2.0")
    b = correr("v1.2.0")
    assert a.returncode == 0 and b.returncode == 0
    assert a.stdout == b.stdout


# --- ORDER coincide con main.tex -----------------------------------------------

def test_order_coincide_con_los_input_de_main_tex_real():
    assert build.leer_inputs(MAIN_TEX) == build.ORDER
    build.verificar_orden(MAIN_TEX)  # no debe levantar


def test_leer_inputs_ignora_lineas_comentadas(tmp_path):
    main = tmp_path / "main.tex"
    main.write_text(
        "\\input{sections/a.tex}\n% \\input{sections/b.tex}\n"
        "\\input{sections/c.tex} % comentario\n",
        encoding="utf-8",
    )
    assert build.leer_inputs(main) == ["a.tex", "c.tex"]


def _main_con_orden(tmp_path, nombres):
    main = tmp_path / "main.tex"
    main.write_text(
        "\\begin{document}\n"
        + "\n".join(f"\\input{{sections/{n}}}" for n in nombres)
        + "\n\\end{document}\n",
        encoding="utf-8",
    )
    return main


def test_orden_alterado_en_main_tex_se_rechaza(tmp_path):
    alterado = list(build.ORDER)
    alterado[1], alterado[2] = alterado[2], alterado[1]
    with pytest.raises(ValueError) as e:
        build.verificar_orden(_main_con_orden(tmp_path, alterado))
    assert "main.tex" in str(e.value)


def test_seccion_faltante_en_main_tex_se_rechaza(tmp_path):
    with pytest.raises(ValueError):
        build.verificar_orden(_main_con_orden(tmp_path, build.ORDER[:-1]))


def test_seccion_sobrante_en_main_tex_se_rechaza(tmp_path):
    with pytest.raises(ValueError):
        build.verificar_orden(_main_con_orden(tmp_path, build.ORDER + ["13-nueva.tex"]))


# --- Triangulacion: otros casos de la misma conducta ---------------------------

def test_leer_inputs_acepta_fin_de_linea_crlf(tmp_path):
    main = tmp_path / "main.tex"
    main.write_bytes(b"\\input{sections/a.tex}\r\n\\input{sections/b.tex}\r\n")
    assert build.leer_inputs(main) == ["a.tex", "b.tex"]


def test_dos_argumentos_se_rechazan_sin_escribir_nada():
    r = correr("v1.2.0", "v1.2.1")
    assert r.returncode != 0
    assert r.stdout == ""


def test_main_con_orden_alterado_devuelve_error_y_no_escribe(tmp_path, monkeypatch, capsys):
    alterado = list(build.ORDER)
    alterado[0], alterado[-1] = alterado[-1], alterado[0]
    monkeypatch.setattr(build, "MAIN_TEX", _main_con_orden(tmp_path, alterado))
    assert build.main(["v1.2.0"]) == 1
    salida = capsys.readouterr()
    assert salida.out == ""
    assert "ORDER" in salida.err
