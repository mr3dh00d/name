"""El sitio es operable solo con teclado, sin trampas de foco (SC-004)."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

PAGINAS = ["/", "/trabajos", "/trabajos/proyecto-1"]

MAX_TABULACIONES = 60


MARCAR_FOCUSABLES = """() => {
  const nodos = document.querySelectorAll('a[href], button, input, select, textarea');
  nodos.forEach((n, i) => n.setAttribute('data-foco-indice', String(i)));
  return nodos.length;
}"""

INDICE_ENFOCADO = """() => {
  const e = document.activeElement;
  return e ? e.getAttribute('data-foco-indice') : null;
}"""


@pytest.mark.e2e
@pytest.mark.parametrize("ruta", PAGINAS)
def test_se_recorren_todos_los_interactivos_sin_quedar_atrapado(
    page: Page, servidor: str, ruta: str
) -> None:
    """Cada elemento se identifica por su índice en el documento.

    Identificarlos por su destino no sirve: dos enlaces distintos pueden apuntar
    al mismo sitio (la navegación y el «volver al índice»), y colapsarían en uno.
    """
    page.goto(f"{servidor}{ruta}")
    esperados = int(page.evaluate(MARCAR_FOCUSABLES))

    alcanzados: set[str] = set()
    for _ in range(MAX_TABULACIONES):
        page.keyboard.press("Tab")
        indice = page.evaluate(INDICE_ENFOCADO)
        if indice is not None:
            alcanzados.add(str(indice))
        if len(alcanzados) == esperados:
            break

    faltan = {str(i) for i in range(esperados)} - alcanzados
    assert faltan == set(), (
        f"{ruta}: no se alcanzaron con el tabulador los elementos {sorted(faltan)} "
        f"de {esperados}. Puede haber una trampa de foco (SC-004)"
    )


@pytest.mark.e2e
def test_el_primer_tabulador_es_el_salto_al_contenido(page: Page, servidor: str) -> None:
    """Quien navega con teclado debe poder saltarse la navegación."""
    page.goto(f"{servidor}/")
    page.keyboard.press("Tab")
    assert page.evaluate("() => document.activeElement.getAttribute('href')") == "#contenido"


@pytest.mark.e2e
def test_el_indicador_de_foco_es_visible(page: Page, servidor: str) -> None:
    """Un foco invisible hace el sitio inutilizable con teclado aunque funcione."""
    page.goto(f"{servidor}/")
    page.keyboard.press("Tab")
    contorno = page.evaluate(
        "() => { const e = document.activeElement;"
        " const s = getComputedStyle(e);"
        " return { ancho: s.outlineWidth, estilo: s.outlineStyle }; }"
    )
    assert contorno["estilo"] != "none", "el elemento enfocado no muestra contorno"
    assert contorno["ancho"] not in ("0px", ""), "el contorno de foco tiene grosor cero"


@pytest.mark.e2e
def test_se_puede_navegar_a_una_ficha_solo_con_teclado(page: Page, servidor: str) -> None:
    page.goto(f"{servidor}/trabajos")
    page.get_by_role("link", name="Proyecto Destacado 1").first.focus()
    page.keyboard.press("Enter")
    page.wait_for_url("**/trabajos/proyecto-1")
    assert page.locator("h1").inner_text() == "Proyecto Destacado 1"
