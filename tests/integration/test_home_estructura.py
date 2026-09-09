"""Estructura del HTML de la página principal (FR-014, CLS)."""

from __future__ import annotations

import re
from itertools import pairwise

from bs4 import BeautifulSoup, Tag
from flask.testing import FlaskClient


def doc_de(client: FlaskClient) -> BeautifulSoup:
    """Analiza la página principal."""
    return BeautifulSoup(client.get("/").get_data(as_text=True), "html.parser")


def test_un_solo_h1(client: FlaskClient) -> None:
    assert len(doc_de(client).find_all("h1")) == 1


def test_jerarquia_de_encabezados_sin_saltos(client: FlaskClient) -> None:
    niveles = [int(e.name[1]) for e in doc_de(client).find_all(re.compile(r"^h[1-6]$"))]
    saltos = [(a, b) for a, b in pairwise(niveles) if b > a + 1]
    assert saltos == [], f"saltos de nivel: {saltos}"


def test_toda_imagen_lleva_alt_ancho_y_alto(client: FlaskClient) -> None:
    for img in doc_de(client).find_all("img"):
        assert img.get("alt") is not None
        assert img.get("width") and img.get("height")


def test_el_salto_al_contenido_es_el_primer_enlace(client: FlaskClient) -> None:
    """SC-004: quien navega con teclado debe poder saltar la navegación."""
    primero = doc_de(client).find("a")
    assert isinstance(primero, Tag)
    assert primero.get("href") == "#contenido"


def test_existe_el_destino_del_salto(client: FlaskClient) -> None:
    assert doc_de(client).find(id="contenido") is not None


def test_la_navegacion_esta_etiquetada(client: FlaskClient) -> None:
    navs = doc_de(client).find_all("nav")
    assert navs, "no hay elementos de navegación"
    for nav in navs:
        assert nav.get("aria-label"), "todo <nav> necesita etiqueta para distinguirse"


def test_el_retrato_tiene_alternativa_significativa(client: FlaskClient) -> None:
    retrato = doc_de(client).select_one(".perfil__retrato")
    if retrato is not None:
        assert len(str(retrato.get("alt", ""))) >= 5
