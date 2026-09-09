"""Todo el contenido y la interfaz están en español (FR-013, SC-010)."""

from __future__ import annotations

import re

import pytest
from bs4 import BeautifulSoup, Tag
from flask.testing import FlaskClient

PAGINAS = ["/", "/trabajos", "/trabajos/proyecto-1", "/no-existe"]

# Palabras de interfaz en inglés que delatarían una plantilla sin traducir.
RESIDUOS_EN_INGLES = re.compile(
    r"\b(home|read more|contact|about|skills|projects|experience|download cv|"
    r"back to|not found|page not found|search|submit)\b",
    re.IGNORECASE,
)


@pytest.mark.parametrize("ruta", PAGINAS)
def test_el_documento_declara_espanol(client: FlaskClient, ruta: str) -> None:
    doc = BeautifulSoup(client.get(ruta).get_data(as_text=True), "html.parser")
    html = doc.find("html")
    assert isinstance(html, Tag)
    assert html.get("lang") == "es"


@pytest.mark.parametrize("ruta", PAGINAS)
def test_sin_residuos_de_interfaz_en_ingles(client: FlaskClient, ruta: str) -> None:
    """Solo se inspecciona el texto de interfaz.

    Los nombres propios del contenido (una tecnología, una empresa) pueden estar
    en cualquier idioma; lo que no puede es la interfaz.
    """
    doc = BeautifulSoup(client.get(ruta).get_data(as_text=True), "html.parser")
    for elemento in doc.select("nav, footer, .estado-vacio, h1, h2, .boton, .error"):
        residuo = RESIDUOS_EN_INGLES.search(elemento.get_text(" ", strip=True))
        assert residuo is None, f"{ruta}: texto de interfaz en inglés '{residuo.group(0)}'"


@pytest.mark.parametrize("ruta", PAGINAS)
def test_la_locale_social_es_espanola(client: FlaskClient, ruta: str) -> None:
    doc = BeautifulSoup(client.get(ruta).get_data(as_text=True), "html.parser")
    locale = doc.find("meta", attrs={"property": "og:locale"})
    assert isinstance(locale, Tag)
    assert str(locale["content"]).startswith("es")
