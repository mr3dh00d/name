"""Historia P2 en un navegador real: exploración de un trabajo."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page


@pytest.mark.e2e
def test_desde_un_destacado_se_llega_a_su_ficha(page: Page, servidor: str) -> None:
    page.goto(f"{servidor}/")
    page.locator('.tarjeta-trabajo[data-slug="proyecto-1"] a').click()
    page.wait_for_url("**/trabajos/proyecto-1")
    assert page.locator("h1").inner_text() == "Proyecto Destacado 1"


@pytest.mark.e2e
def test_el_enlace_directo_funciona_en_una_sesion_nueva(page: Page, servidor: str) -> None:
    """Escenario 2 de P2: la ficha no depende de haber visitado la portada."""
    navegador = page.context.browser
    assert navegador is not None
    limpio = navegador.new_context()
    nueva = limpio.new_page()
    try:
        nueva.goto(f"{servidor}/trabajos/proyecto-2")
        assert nueva.locator("h1").inner_text() == "Proyecto Destacado 2"
    finally:
        limpio.close()


@pytest.mark.e2e
def test_los_enlaces_externos_abren_en_pestana_nueva(page: Page, servidor: str) -> None:
    """Escenario 3 de P2: el visitante no pierde el portafolio."""
    page.goto(f"{servidor}/trabajos/proyecto-1")
    enlace = page.locator('.ficha__enlaces a[href^="http"]').first
    assert enlace.get_attribute("target") == "_blank"
    assert "noopener" in str(enlace.get_attribute("rel"))


@pytest.mark.e2e
def test_la_vuelta_al_indice_funciona(page: Page, servidor: str) -> None:
    page.goto(f"{servidor}/trabajos/proyecto-1")
    page.locator(".ficha__volver a").click()
    page.wait_for_url("**/trabajos")
    assert page.locator(".tarjeta-trabajo").count() == 4


@pytest.mark.e2e
def test_un_slug_inexistente_muestra_la_pagina_de_error(page: Page, servidor: str) -> None:
    respuesta = page.goto(f"{servidor}/trabajos/no-existe")
    assert respuesta is not None
    assert respuesta.status == 404
    assert "no existe" in page.locator("h1").inner_text().lower()
    assert page.get_by_role("link", name="Ir al inicio").count() == 1
