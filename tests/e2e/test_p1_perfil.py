"""Historia P1 en un navegador real: evaluación rápida del perfil."""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import Page

ESCRITORIO = {"width": 1280, "height": 800}
MOVIL = {"width": 375, "height": 667}


@pytest.mark.e2e
@pytest.mark.parametrize("pantalla", [ESCRITORIO, MOVIL], ids=["escritorio", "movil"])
def test_la_identidad_se_ve_sin_desplazarse(
    page: Page, servidor: str, pantalla: dict[str, int]
) -> None:
    """El escenario 1 de P1: nombre, titular y resumen en la primera pantalla."""
    page.set_viewport_size(pantalla)  # type: ignore[arg-type]
    page.goto(f"{servidor}/")

    for selector in ("h1", ".perfil__titular", ".perfil__resumen"):
        caja = page.locator(selector).bounding_box()
        assert caja is not None, f"{selector} no se renderiza"
        assert caja["y"] < pantalla["height"], (
            f"{selector} queda por debajo de la primera pantalla en "
            f"{pantalla['width']}×{pantalla['height']}"
        )


@pytest.mark.e2e
def test_hay_al_menos_tres_trabajos_destacados(page: Page, servidor: str) -> None:
    page.goto(f"{servidor}/")
    assert page.locator(".tarjeta-trabajo").count() >= 3


@pytest.mark.e2e
def test_el_cv_se_descarga_en_menos_de_tres_segundos(page: Page, servidor: str) -> None:
    page.goto(f"{servidor}/")
    inicio = time.perf_counter()
    respuesta = page.request.get(f"{servidor}/cv/cv.pdf")
    transcurrido = time.perf_counter() - inicio

    assert respuesta.status == 200
    assert transcurrido < 3.0, f"el CV tardó {transcurrido:.2f} s"


@pytest.mark.e2e
def test_los_perfiles_externos_estan_en_todas_las_paginas(page: Page, servidor: str) -> None:
    """Sin sección de contacto, son la única salida del sitio (FR-005, FR-006)."""
    for ruta in ("/", "/trabajos", "/trabajos/proyecto-1", "/no-existe"):
        page.goto(f"{servidor}{ruta}")
        assert page.locator(".enlaces-externos a").count() >= 1, f"{ruta} sin enlaces de perfil"


@pytest.mark.e2e
def test_el_contenido_sigue_siendo_legible_sin_javascript(page: Page, servidor: str) -> None:
    """FR-017: el sitio no usa scripting, así que deshabilitarlo no cambia nada."""
    contexto = page.context.browser
    assert contexto is not None
    sin_js = contexto.new_context(java_script_enabled=False)
    pagina = sin_js.new_page()
    try:
        pagina.goto(f"{servidor}/")
        assert pagina.locator("h1").inner_text() == "Ada Prueba"
        assert pagina.locator(".tarjeta-trabajo").count() >= 3
        pagina.get_by_role("link", name="Ver todos los trabajos").click()
        pagina.wait_for_url("**/trabajos")
        assert pagina.locator("h1").inner_text() == "Trabajos"
    finally:
        sin_js.close()
