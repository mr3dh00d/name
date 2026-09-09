"""Cero infracciones de nivel AA en todas las páginas (SC-003, FR-014)."""

from __future__ import annotations

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page

PAGINAS = ["/", "/trabajos", "/trabajos/proyecto-1", "/no-existe"]

NIVELES = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]


@pytest.mark.e2e
@pytest.mark.parametrize("ruta", PAGINAS)
def test_sin_infracciones_aa(page: Page, servidor: str, ruta: str) -> None:
    page.goto(f"{servidor}{ruta}")
    resultados = Axe().run(page, options={"runOnly": {"type": "tag", "values": NIVELES}})

    infracciones = resultados.response["violations"]
    detalle = [
        f"{v['id']} ({v['impact']}): {v['help']}"
        for v in infracciones
        if v["impact"] in ("serious", "critical", "moderate")
    ]
    assert detalle == [], f"{ruta} incumple accesibilidad AA:\n" + "\n".join(detalle)
