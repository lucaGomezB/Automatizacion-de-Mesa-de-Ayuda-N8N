"""
Tests unitarios del clasificador determinístico basado en reglas (C-27, c-71).

Vocabulario canonico de 5 sectores. `Operaciones` deja de existir y sus
terminos se redistribuyen. Un sector debe ganar para cada caso canonico.

c-71 endurece la etapa determinista:
    - ASG-007: sin senal -> ausencia explicita de prediccion (no sector arbitrario).
    - ASG-008: empate -> ambiguedad marcada, sin ganador por orden del mapa.
    - ASG-009: confianza con conteo minimo de matches y margen sobre el segundo.

Strict TDD (c-71):
    1.2 RED   -> no-match no devuelve sector canonico arbitrario.
    1.5 RED   -> empate marca ambiguedad sin depender del orden.
    1.8 RED   -> contrato aditivo (sin_prediccion/ambiguo, sector opcional).
    3.2 RED   -> confianza no degenerada (min_matches + margen).
"""

import pytest

from app.classifiers.deterministic import DeterministicClassifier
from app.constants import SECTORES_CANONICOS
from app.schemas.clasificacion import ClasificacionResult


@pytest.fixture
def classifier() -> DeterministicClassifier:
    return DeterministicClassifier()


class TestRedistribucionSectores:
    @pytest.mark.asyncio
    async def test_todos_los_sectores_tienen_terminos(self, classifier):
        """Los cinco sectores canonicos tienen al menos un patron de keywords."""
        from app.classifiers.keywords import KEYWORD_MAP

        assert set(KEYWORD_MAP.keys()) == set(SECTORES_CANONICOS)
        for sector, patrones in KEYWORD_MAP.items():
            assert patrones, f"El sector {sector!r} no tiene terminos"

    @pytest.mark.asyncio
    async def test_hardware_clasifica_como_soporte_tecnico_hardware(self, classifier):
        """Un termino de hardware debe clasificar como `Soporte Tecnico Hardware`."""
        result = await classifier.classify(
            "Mi impresora no imprime. Sale papel atascado. Código de error 13."
        )
        assert result.sector_predicho == "Soporte Tecnico Hardware"
        assert result.confianza > 0.0
        assert result.etapa == "deterministic"

    @pytest.mark.asyncio
    async def test_ninguna_prediccion_es_operaciones(self, classifier):
        """Ninguna prediccion puede ser `Operaciones` (eliminada del dominio)."""
        textos = [
            "Necesitamos reservar una sala para una reunión de planificación.",
            "Trámite administrativo de continuidad operativa pendiente.",
            "El servidor no responde por un timeout en la red.",
            "La impresora no enciende.",
            "El backup de la base de datos falló.",
            "Detectamos phishing y malware.",
        ]
        for texto in textos:
            result = await classifier.classify(texto)
            assert result.sector_predicho != "Operaciones"
            # c-71: ante senal nula el sector es None (no un canonico arbitrario).
            assert result.sector_predicho is None or result.sector_predicho in SECTORES_CANONICOS


class TestCasosCanonicos:
    @pytest.mark.asyncio
    async def test_seguridad_informatica(self, classifier):
        result = await classifier.classify(
            "Detectamos un ataque de phishing y actividad de malware en la red."
        )
        assert result.sector_predicho == "Seguridad Informatica"

    @pytest.mark.asyncio
    async def test_soporte_tecnico_software(self, classifier):
        result = await classifier.classify(
            "No puedo abrir Outlook, la aplicación de escritorio se traba."
        )
        assert result.sector_predicho == "Soporte Tecnico Software"

    @pytest.mark.asyncio
    async def test_bases_de_datos(self, classifier):
        result = await classifier.classify(
            "El backup de la base de datos falló durante la replicación."
        )
        assert result.sector_predicho == "Bases de Datos"

    @pytest.mark.asyncio
    async def test_sistemas_servidor(self, classifier):
        result = await classifier.classify(
            "Se cayó el servidor de correo. Error SMTP timeout en la red."
        )
        assert result.sector_predicho == "Sistemas"

    @pytest.mark.asyncio
    async def test_termino_ambiguo_devuelve_sector_canonico(self, classifier):
        """Un texto con senal mixta devuelve uno de los 5 sectores, nunca Operaciones."""
        result = await classifier.classify(
            "El servidor de correo no responde y hay un firewall nuevo."
        )
        assert result.sector_predicho in SECTORES_CANONICOS


class TestInvariantes:
    @pytest.mark.asyncio
    async def test_confidence_is_normalised(self, classifier):
        result = await classifier.classify(
            "impresora teclado mouse pantalla laptop periférico"
        )
        assert 0.0 <= result.confianza <= 1.0

    @pytest.mark.asyncio
    async def test_empty_description_returns_no_prediction(self, classifier):
        """c-71 (1.4): descripcion sin senal -> ausencia explicita, confianza 0.0."""
        result = await classifier.classify("x")
        assert result.sector_predicho is None
        assert result.sin_prediccion is True
        assert result.confianza == 0.0


# ---------------------------------------------------------------------------
# c-71 §1 — No-match: ausencia explicita de prediccion (ASG-007)
# ---------------------------------------------------------------------------
class TestNoMatch:
    @pytest.mark.asyncio
    async def test_sin_senal_no_inventa_sector(self, classifier):
        result = await classifier.classify(
            "Necesitamos reservar una sala para una reunion de planificacion."
        )
        assert result.sector_predicho is None
        assert result.sin_prediccion is True
        assert result.confianza == 0.0

    @pytest.mark.asyncio
    async def test_texto_vacio_no_inventa_sector(self, classifier):
        result = await classifier.classify("")
        assert result.sector_predicho is None
        assert result.sin_prediccion is True
        assert result.confianza == 0.0

    @pytest.mark.asyncio
    async def test_solo_terminos_genericos_no_inventa_sector(self, classifier):
        result = await classifier.classify(
            "El usuario reporta una novedad general sin detalle tecnico."
        )
        assert result.sector_predicho is None
        assert result.sin_prediccion is True
        assert result.confianza == 0.0

    @pytest.mark.asyncio
    async def test_unico_termino_tiene_senal_pero_no_cortocircuita(self, classifier):
        """Un unico match es senal (no ausencia) pero jamas alcanza el cortocircuito."""
        result = await classifier.classify("Se rompio el teclado.")
        assert result.sin_prediccion is False
        assert result.sector_predicho == "Soporte Tecnico Hardware"
        assert 0.0 <= result.confianza < classifier._threshold


# ---------------------------------------------------------------------------
# c-71 §1 — Empate: ambiguedad marcada, orden-independiente (ASG-008)
# ---------------------------------------------------------------------------
class TestTieBreak:
    @pytest.mark.asyncio
    async def test_empate_dos_vias_marca_ambiguedad(self, classifier):
        result = await classifier.classify("Hay un firewall y un servidor.")
        assert result.ambiguo is True
        assert result.sector_predicho is None
        assert result.confianza == 0.0

    @pytest.mark.asyncio
    async def test_empate_tres_vias_marca_ambiguedad(self, classifier):
        result = await classifier.classify(
            "Firewall, servidor e impresora reportan fallas."
        )
        assert result.ambiguo is True
        assert result.sector_predicho is None

    @pytest.mark.asyncio
    async def test_el_orden_del_mapa_no_decide_el_ganador(self, classifier):
        """Dos ordenes del mismo empate producen el MISMO resultado (sin ganador)."""
        resultado_a = await classifier.classify("firewall servidor")
        resultado_b = await classifier.classify("servidor firewall")
        assert resultado_a.ambiguo is True and resultado_b.ambiguo is True
        assert resultado_a.sector_predicho is None
        assert resultado_b.sector_predicho is None

    @pytest.mark.asyncio
    async def test_ganador_dominante_no_es_ambiguo(self, classifier):
        result = await classifier.classify("impresora imprime teclado mouse")
        assert result.ambiguo is False
        assert result.sector_predicho == "Soporte Tecnico Hardware"


# ---------------------------------------------------------------------------
# c-71 §3 — Confianza con conteo minimo y margen (ASG-009)
# ---------------------------------------------------------------------------
class TestConfianzaConMinMatchesYMargen:
    @pytest.mark.asyncio
    async def test_un_solo_match_no_alcanza_confianza_alta(self, classifier):
        result = await classifier.classify("teclado")
        assert result.confianza == 0.0

    @pytest.mark.asyncio
    async def test_ganador_dominante_alcanza_confianza_alta(self, classifier):
        result = await classifier.classify(
            "impresora imprime teclado mouse monitor pantalla laptop"
        )
        assert result.confianza >= classifier._threshold
        assert classifier.is_confident(result) is True

    @pytest.mark.asyncio
    async def test_empate_da_confianza_nula(self, classifier):
        result = await classifier.classify("firewall servidor")
        assert result.confianza == 0.0

    @pytest.mark.asyncio
    async def test_justo_en_min_matches_no_es_confianza_maxima(self, classifier):
        """winner == min_matches (2) con segundo en 0 no llega a 1.0."""
        result = await classifier.classify("impresora teclado")
        assert 0.0 < result.confianza < 1.0

    @pytest.mark.asyncio
    async def test_por_debajo_de_min_matches_es_cero(self, classifier):
        assert classifier._min_matches >= 2
        result = await classifier.classify("teclado")
        assert result.confianza == 0.0

    @pytest.mark.asyncio
    async def test_confianza_acotada_en_todos_los_casos(self, classifier):
        for texto in (
            "",
            "x",
            "teclado",
            "impresora teclado mouse pantalla laptop periférico",
            "firewall servidor",
            "backup base de datos replicacion postgresql mysql oracle",
        ):
            result = await classifier.classify(texto)
            assert 0.0 <= result.confianza <= 1.0


# ---------------------------------------------------------------------------
# c-71 §1.8 — Contrato aditivo de ClasificacionResult
# ---------------------------------------------------------------------------
class TestContratoClasificacionResult:
    def test_permite_ausencia_de_sector_y_defaults_seguros(self):
        result = ClasificacionResult(
            sector_predicho=None,
            confianza=0.0,
            etapa="deterministic",
            requiere_revision_humana=False,
        )
        assert result.sector_predicho is None
        assert result.sin_prediccion is False
        assert result.ambiguo is False

    def test_campos_aditivos_explicitos(self):
        result = ClasificacionResult(
            sector_predicho=None,
            confianza=0.0,
            etapa="deterministic",
            requiere_revision_humana=True,
            sin_prediccion=True,
            ambiguo=True,
        )
        assert result.sin_prediccion is True
        assert result.ambiguo is True


# ---------------------------------------------------------------------------
# c-71 §2 — Ampliacion del vocabulario guiada por el corpus (TAX-002)
# ---------------------------------------------------------------------------
HARDWARE_BASELINE = 20
SOFTWARE_BASELINE = 21


class TestVocabularioAmpliado:
    def test_hardware_y_software_no_pierden_terminos(self):
        """La ampliacion es aditiva: Hardware y Software crecen (TAX-002)."""
        from app.classifiers.keywords import KEYWORD_MAP

        assert len(KEYWORD_MAP["Soporte Tecnico Hardware"]) >= HARDWARE_BASELINE
        assert len(KEYWORD_MAP["Soporte Tecnico Software"]) >= SOFTWARE_BASELINE
        # Al menos una de las dos prioridades crece estrictamente.
        assert (
            len(KEYWORD_MAP["Soporte Tecnico Hardware"]) > HARDWARE_BASELINE
            or len(KEYWORD_MAP["Soporte Tecnico Software"]) > SOFTWARE_BASELINE
        )

    @pytest.mark.asyncio
    async def test_hardware_telefonia_y_perifericos(self, classifier):
        """Terminos de telefonia/perifericos del corpus (verdad Hardware)."""
        casos = [
            "No funcionan las lineas telefonicas.",
            "Solicitud de auriculares nuevo.",
            "Se le esta acabando el toner de la impresora.",
            "Solicita un raton inalambrico nuevo.",
            "La computadora hace un ruido fuerte al encender.",
        ]
        for texto in casos:
            result = await classifier.classify(texto)
            assert result.sin_prediccion is False, f"sin senal: {texto!r}"
            assert result.sector_predicho == "Soporte Tecnico Hardware", texto

    @pytest.mark.asyncio
    async def test_software_ofimatica_y_correo(self, classifier):
        """Terminos de ofimatica/correo del corpus (verdad Software)."""
        casos = [
            "No puede abrir archivos excel ni word.",
            "Toco algo y ahora tiene Adobe PDF Reader en ruso.",
            "No puede acceder a su correo electronico empresarial.",
            "Solicita la reinstalacion de Microsoft Word.",
        ]
        for texto in casos:
            result = await classifier.classify(texto)
            assert result.sin_prediccion is False, f"sin senal: {texto!r}"
            assert result.sector_predicho == "Soporte Tecnico Software", texto

    @pytest.mark.asyncio
    async def test_seguridad_accesos_y_politicas(self, classifier):
        casos = [
            "Solicita un desbloqueo de usuario de dominio.",
            "Le sale acceso denegado al abrir carpetas compartidas.",
        ]
        for texto in casos:
            result = await classifier.classify(texto)
            assert result.sin_prediccion is False, f"sin senal: {texto!r}"
            assert result.sector_predicho == "Seguridad Informatica", texto

    @pytest.mark.asyncio
    async def test_sistemas_redes(self, classifier):
        casos = [
            "Tiene fallos de roaming wifi entre puntos de acceso.",
            "Le sale error de direccion IP duplicada en la red.",
        ]
        for texto in casos:
            result = await classifier.classify(texto)
            assert result.sin_prediccion is False, f"sin senal: {texto!r}"
            assert result.sector_predicho == "Sistemas", texto

    def test_terminos_nuevos_son_regex_validos(self):
        import re

        from app.classifiers.keywords import KEYWORD_MAP

        for sector, patrones in KEYWORD_MAP.items():
            for patron in patrones:
                re.compile(patron)  # no debe lanzar re.error


# ---------------------------------------------------------------------------
# c-71 §4.6 / §5.3 — Tests estructurales de invariantes
# ---------------------------------------------------------------------------
class TestInvariantesEstructurales:
    def test_los_cinco_strings_canonicos_no_cambiaron(self):
        from app.constants import SECTORES_CANONICOS

        assert SECTORES_CANONICOS == (
            "Seguridad Informatica",
            "Soporte Tecnico Hardware",
            "Soporte Tecnico Software",
            "Bases de Datos",
            "Sistemas",
        )
        for sector in SECTORES_CANONICOS:
            assert "á" not in sector and "é" not in sector and "í" not in sector
            assert "ó" not in sector and "ú" not in sector

    def test_claves_del_mapa_igualan_sectores_canonicos(self):
        from app.classifiers.keywords import KEYWORD_MAP
        from app.constants import SECTORES_CANONICOS

        assert set(KEYWORD_MAP.keys()) == set(SECTORES_CANONICOS)
        assert len(KEYWORD_MAP) == 5
        assert "Operaciones" not in KEYWORD_MAP

    def test_min_matches_y_umbral_configurados(self):
        from app.config.settings import get_settings

        settings = get_settings()
        assert settings.deterministic_min_matches >= 2
        assert 0.0 <= settings.deterministic_confidence_threshold <= 1.0
