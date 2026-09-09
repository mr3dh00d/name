"""Invariantes comunes a toda respuesta HTML (contracts/routes.md, INV-H01 a H10).

Cada contrato de ruta invoca ``verificar_invariantes`` en lugar de repetir las diez
comprobaciones. Es la única abstracción de la suite y tiene cinco consumidores
reales, que es lo que el Principio V exige para justificar una.
"""

from __future__ import annotations

import re
from itertools import pairwise

from bs4 import BeautifulSoup, Tag
from werkzeug.test import TestResponse

DOMINIOS_DE_SEGUIMIENTO = (
    "google-analytics.com",
    "googletagmanager.com",
    "facebook.net",
    "doubleclick.net",
    "hotjar.com",
    "segment.com",
    "mixpanel.com",
    "clarity.ms",
)

META_SOCIALES_OBLIGATORIOS = (
    ("property", "og:title"),
    ("property", "og:description"),
    ("property", "og:image"),
    ("property", "og:url"),
    ("name", "twitter:card"),
)


def sopa(respuesta: TestResponse) -> BeautifulSoup:
    """Analiza el cuerpo de la respuesta."""
    return BeautifulSoup(respuesta.get_data(as_text=True), "html.parser")


def _inv_h01_tipo_de_contenido(respuesta: TestResponse) -> None:
    assert respuesta.content_type.startswith("text/html"), respuesta.content_type
    assert "charset=utf-8" in respuesta.content_type.lower()


def _inv_h02_idioma(doc: BeautifulSoup) -> None:
    html = doc.find("html")
    assert isinstance(html, Tag), "falta el elemento <html>"
    assert html.get("lang") == "es", "FR-013: el documento debe declarar lang='es'"


def _inv_h03_encabezados(doc: BeautifulSoup) -> None:
    encabezados = doc.find_all(re.compile(r"^h[1-6]$"))
    h1 = [e for e in encabezados if e.name == "h1"]
    assert len(h1) == 1, f"debe haber exactamente un <h1>, hay {len(h1)}"

    niveles = [int(e.name[1]) for e in encabezados]
    for anterior, actual in pairwise(niveles):
        assert actual <= anterior + 1, (
            f"la jerarquía salta de h{anterior} a h{actual}: los lectores de "
            "pantalla usan estos niveles para navegar (FR-014)"
        )


def _inv_h04_imagenes(doc: BeautifulSoup) -> None:
    for img in doc.find_all("img"):
        assert img.get("alt") is not None, f"<img> sin alt: {img.get('src')}"
        assert img.get("width"), f"<img> sin width: {img.get('src')} (necesario para CLS)"
        assert img.get("height"), f"<img> sin height: {img.get('src')} (necesario para CLS)"


def _inv_h05_metadatos(doc: BeautifulSoup) -> None:
    titulo = doc.find("title")
    assert isinstance(titulo, Tag) and titulo.get_text(strip=True), "falta <title> con contenido"

    descripcion = doc.find("meta", attrs={"name": "description"})
    assert isinstance(descripcion, Tag) and descripcion.get("content")

    for atributo, valor in META_SOCIALES_OBLIGATORIOS:
        etiqueta = doc.find("meta", attrs={atributo: valor})
        assert isinstance(etiqueta, Tag), f"falta el metadato social {valor} (FR-019)"
        assert etiqueta.get("content"), f"el metadato {valor} está vacío"


def _inv_h06_enlaces_externos(doc: BeautifulSoup) -> None:
    for enlace in doc.find_all("a", href=True):
        href = str(enlace["href"])
        if not href.startswith("http"):
            continue
        rel = " ".join(enlace.get("rel") or [])
        assert "noopener" in rel and "noreferrer" in rel, f"enlace externo sin rel seguro: {href}"
        assert enlace.get("target") == "_blank", f"enlace externo sin target=_blank: {href}"


def _inv_h07_sin_javascript(doc: BeautifulSoup, cuerpo: str) -> None:
    """FR-017: el sitio no depende de scripting, y de hecho no lo usa en absoluto."""
    assert doc.find_all("script") == [], "el documento no debe referenciar JavaScript"
    manejadores = re.findall(r"\son(click|load|error|submit|change)\s*=", cuerpo, re.IGNORECASE)
    assert manejadores == [], f"manejadores de eventos en línea: {manejadores}"


def _inv_h08_sin_terceros(cuerpo: str) -> None:
    encontrados = [d for d in DOMINIOS_DE_SEGUIMIENTO if d in cuerpo]
    assert encontrados == [], f"dominios de seguimiento en la página (FR-021): {encontrados}"


def _inv_h09_enlaces_del_perfil(doc: BeautifulSoup) -> None:
    """Sin sección de contacto, estos enlaces son la única salida del sitio."""
    nav = doc.find("nav", class_="enlaces-externos")
    assert isinstance(nav, Tag), "faltan los enlaces a perfiles externos (FR-005, INV-H09)"
    assert nav.find_all("a", href=True), "la lista de perfiles externos está vacía"


def _inv_h10_cache(respuesta: TestResponse) -> None:
    cache = respuesta.headers.get("Cache-Control", "")
    assert "public" in cache, f"falta la caché pública de CDN: {cache!r}"
    assert "s-maxage=" in cache, f"falta s-maxage, del que depende el p95: {cache!r}"


def verificar_invariantes(respuesta: TestResponse, *, cachea: bool = True) -> BeautifulSoup:
    """Comprueba INV-H01 a INV-H10 y devuelve el documento ya analizado.

    Args:
        respuesta: Respuesta del cliente de pruebas de Flask.
        cachea: ``False`` para páginas de error, que no llevan caché larga.

    Returns:
        El árbol del documento, para que la prueba siga con sus aserciones propias.
    """
    cuerpo = respuesta.get_data(as_text=True)
    doc = BeautifulSoup(cuerpo, "html.parser")

    _inv_h01_tipo_de_contenido(respuesta)
    _inv_h02_idioma(doc)
    _inv_h03_encabezados(doc)
    _inv_h04_imagenes(doc)
    _inv_h05_metadatos(doc)
    _inv_h06_enlaces_externos(doc)
    _inv_h07_sin_javascript(doc, cuerpo)
    _inv_h08_sin_terceros(cuerpo)
    _inv_h09_enlaces_del_perfil(doc)
    if cachea:
        _inv_h10_cache(respuesta)
    return doc
