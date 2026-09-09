"""El script de build detiene la publicación ante contenido inválido (FR-012)."""

from __future__ import annotations

import pytest
from scripts.build import validar

from tests.conftest import CONTENIDO_INVALIDO, CONTENIDO_VALIDO, PUBLICO

VARIANTES = [
    ("campo_obligatorio_ausente", "titular"),
    ("campo_desconocido", "titluo"),
    ("slug_no_coincide", "slug"),
    ("capacidad_colgante", "capacidades"),
    ("fechas_incoherentes", "fecha_fin"),
    ("imagen_sin_alt", "alt"),
    ("actuales_solapadas", "actual"),
    ("ruta_inexistente", "cv"),
    ("enlace_no_descriptivo", "etiqueta"),
    ("url_no_https", "url"),
    ("perfil_sin_enlaces", "enlaces"),
    ("perfil_ausente", "perfil.toml"),
]


def test_contenido_valido_sale_con_cero(capsys: pytest.CaptureFixture[str]) -> None:
    assert validar(CONTENIDO_VALIDO, PUBLICO) == 0
    assert "válido" in capsys.readouterr().out


@pytest.mark.parametrize(("variante", "esperado"), VARIANTES)
def test_contenido_invalido_sale_con_error_y_senala_el_fallo(
    variante: str, esperado: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """No basta con fallar: FR-012 exige decir dónde está el problema."""
    codigo = validar(CONTENIDO_INVALIDO / variante, PUBLICO)
    salida = capsys.readouterr().err

    assert codigo != 0, f"la variante '{variante}' no detuvo la publicación"
    assert esperado in salida, f"el error de '{variante}' no menciona '{esperado}':\n{salida}"
    assert "archivo :" in salida
    assert "campo   :" in salida


def test_el_error_remite_al_contrato_del_formato(capsys: pytest.CaptureFixture[str]) -> None:
    validar(CONTENIDO_INVALIDO / "campo_desconocido", PUBLICO)
    assert "content-schema.md" in capsys.readouterr().err
