"""Metadatos de vista previa social en cada página compartible (FR-019, SC-007)."""

from __future__ import annotations

import pytest
from bs4 import BeautifulSoup, Tag
from flask.testing import FlaskClient

COMPARTIBLES = ["/", "/trabajos", "/trabajos/proyecto-1"]

OBLIGATORIOS = [
    ("property", "og:title"),
    ("property", "og:description"),
    ("property", "og:image"),
    ("property", "og:url"),
    ("property", "og:type"),
    ("property", "og:locale"),
    ("name", "twitter:card"),
]


def doc(client: FlaskClient, ruta: str) -> BeautifulSoup:
    """Analiza la página indicada."""
    return BeautifulSoup(client.get(ruta).get_data(as_text=True), "html.parser")


def meta(documento: BeautifulSoup, atributo: str, valor: str) -> str:
    """Devuelve el contenido de un metadato, o cadena vacía si no está."""
    etiqueta = documento.find("meta", attrs={atributo: valor})
    return str(etiqueta["content"]) if isinstance(etiqueta, Tag) else ""


@pytest.mark.parametrize("ruta", COMPARTIBLES)
@pytest.mark.parametrize(("atributo", "clave"), OBLIGATORIOS)
def test_metadato_presente_y_no_vacio(
    client: FlaskClient, ruta: str, atributo: str, clave: str
) -> None:
    assert meta(doc(client, ruta), atributo, clave), f"{ruta} no declara {clave}"


@pytest.mark.parametrize("ruta", COMPARTIBLES)
def test_og_url_coincide_con_la_ruta(client: FlaskClient, ruta: str) -> None:
    url = meta(doc(client, ruta), "property", "og:url")
    assert url.startswith("http")
    assert url.endswith(ruta if ruta != "/" else "/")


@pytest.mark.parametrize("ruta", COMPARTIBLES)
def test_og_image_es_absoluta(client: FlaskClient, ruta: str) -> None:
    """Las redes sociales descartan las imágenes con dirección relativa."""
    assert meta(doc(client, ruta), "property", "og:image").startswith("http")


@pytest.mark.parametrize("ruta", COMPARTIBLES)
def test_hay_enlace_canonico(client: FlaskClient, ruta: str) -> None:
    canonico = doc(client, ruta).find("link", attrs={"rel": "canonical"})
    assert isinstance(canonico, Tag)
    assert str(canonico["href"]).startswith("http")


def test_cada_pagina_tiene_titulo_distinto(client: FlaskClient) -> None:
    """Un título repetido hace que tres enlaces compartidos parezcan el mismo."""
    titulos = {meta(doc(client, r), "property", "og:title") for r in COMPARTIBLES}
    assert len(titulos) == len(COMPARTIBLES)
