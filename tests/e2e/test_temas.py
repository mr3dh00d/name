"""El sitio respeta las preferencias del sistema del visitante (FR-016)."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page


def fondo(page: Page) -> str:
    """Color de fondo calculado del cuerpo."""
    return str(page.evaluate("() => getComputedStyle(document.body).backgroundColor"))


@pytest.mark.e2e
def test_el_tema_cambia_con_la_preferencia_del_sistema(page: Page, servidor: str) -> None:
    page.emulate_media(color_scheme="light")
    page.goto(f"{servidor}/")
    claro = fondo(page)

    page.emulate_media(color_scheme="dark")
    page.reload()
    oscuro = fondo(page)

    assert claro != oscuro, "el tema oscuro no cambia la presentación (FR-016)"


@pytest.mark.e2e
def test_no_hay_conmutador_de_tema(page: Page, servidor: str) -> None:
    """El conmutador exigiría JavaScript y almacenamiento, y nada lo pide."""
    page.goto(f"{servidor}/")
    assert page.locator("button").count() == 0


@pytest.mark.e2e
def test_se_respeta_la_reduccion_de_movimiento(page: Page, servidor: str) -> None:
    page.emulate_media(reduced_motion="reduce")
    page.goto(f"{servidor}/")
    duraciones = page.evaluate(
        "() => [...document.querySelectorAll('*')]"
        ".map(e => getComputedStyle(e).transitionDuration)"
        ".filter(d => d && d !== '0s' && parseFloat(d) > 0.05)"
    )
    assert duraciones == [], f"transiciones activas pese a prefers-reduced-motion: {duraciones}"
