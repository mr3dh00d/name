"""Sin desplazamiento horizontal de 320 px a 2560 px (FR-015, SC-008)."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

ANCHOS = [320, 375, 414, 768, 1024, 1280, 1920, 2560]
PAGINAS = ["/", "/trabajos", "/trabajos/proyecto-1", "/no-existe"]


@pytest.mark.e2e
@pytest.mark.parametrize("ancho", ANCHOS)
@pytest.mark.parametrize("ruta", PAGINAS)
def test_sin_desplazamiento_horizontal(page: Page, servidor: str, ruta: str, ancho: int) -> None:
    page.set_viewport_size({"width": ancho, "height": 900})
    page.goto(f"{servidor}{ruta}")

    desborde = page.evaluate(
        "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert desborde <= 0, f"{ruta} a {ancho} px desborda {desborde} px en horizontal"


@pytest.mark.e2e
@pytest.mark.parametrize("ancho", [320, 1280])
def test_el_contenido_principal_sigue_visible(page: Page, servidor: str, ancho: int) -> None:
    page.set_viewport_size({"width": ancho, "height": 900})
    page.goto(f"{servidor}/")
    assert page.locator("h1").is_visible()
    assert page.locator(".tarjeta-trabajo").first.is_visible()
