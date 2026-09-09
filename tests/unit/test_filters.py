"""Filtros Jinja de fecha y periodo, en español (FR-013)."""

from __future__ import annotations

from datetime import date

import pytest

from portafolio.filters import formato_mes, formato_periodo


@pytest.mark.parametrize(
    ("fecha", "esperado"),
    [
        (date(2025, 1, 15), "enero de 2025"),
        (date(2024, 8, 1), "agosto de 2024"),
        (date(2023, 12, 31), "diciembre de 2023"),
    ],
)
def test_formato_mes_en_espanol(fecha: date, esperado: str) -> None:
    assert formato_mes(fecha) == esperado


def test_periodo_cerrado() -> None:
    assert (
        formato_periodo(date(2021, 1, 15), date(2024, 2, 28)) == "enero de 2021 – febrero de 2024"
    )


def test_periodo_en_curso() -> None:
    """Sin fecha de fin, el periodo sigue abierto (data-model.md)."""
    assert formato_periodo(date(2024, 3, 1), None) == "marzo de 2024 – actualidad"


def test_periodo_del_mismo_mes_no_se_repite() -> None:
    assert formato_periodo(date(2025, 5, 1), date(2025, 5, 30)) == "mayo de 2025"


def test_no_depende_de_la_configuracion_regional_del_proceso() -> None:
    """El Principio II prohíbe pruebas que dependan del entorno."""
    assert formato_mes(date(2025, 3, 1)) == "marzo de 2025"
