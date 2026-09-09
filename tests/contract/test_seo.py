"""Contrato de `/sitemap.xml` y `/robots.txt` (FR-020)."""

from __future__ import annotations

from xml.etree import ElementTree

from flask.testing import FlaskClient

from portafolio.content.models import Contenido

ESPACIO = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def locs(client: FlaskClient) -> list[str]:
    """Direcciones declaradas en el sitemap."""
    raiz = ElementTree.fromstring(client.get("/sitemap.xml").get_data(as_text=True))  # noqa: S314
    return [e.text or "" for e in raiz.iter(f"{ESPACIO}loc")]


def test_sitemap_responde_xml(client: FlaskClient) -> None:
    respuesta = client.get("/sitemap.xml")
    assert respuesta.status_code == 200
    assert "xml" in respuesta.content_type


def test_sitemap_esta_bien_formado(client: FlaskClient) -> None:
    assert locs(client), "el sitemap no declara ninguna dirección"


def test_sitemap_incluye_todas_las_paginas(
    client: FlaskClient, contenido_valido: Contenido
) -> None:
    rutas = {u.split("://", 1)[1].split("/", 1)[1] for u in locs(client)}
    esperadas = {"", "trabajos", *[f"trabajos/{t.slug}" for t in contenido_valido.trabajos]}
    assert rutas == esperadas


def test_sitemap_excluye_la_pagina_de_error(client: FlaskClient) -> None:
    assert not any("404" in u for u in locs(client))


def test_todas_las_direcciones_son_absolutas(client: FlaskClient) -> None:
    for url in locs(client):
        assert url.startswith("http"), f"dirección relativa en el sitemap: {url}"


def test_robots_responde_texto_plano(client: FlaskClient) -> None:
    respuesta = client.get("/robots.txt")
    assert respuesta.status_code == 200
    assert respuesta.content_type.startswith("text/plain")


def test_robots_permite_indexar_y_declara_el_sitemap(client: FlaskClient) -> None:
    cuerpo = client.get("/robots.txt").get_data(as_text=True)
    assert "Allow: /" in cuerpo
    assert "Sitemap: http" in cuerpo
    assert "/sitemap.xml" in cuerpo
