"""El sitio no contacta con terceros ni almacena datos del visitante.

FR-021 y SC-009. Con la sección de contacto descartada (FR-006), el portafolio no
recibe ni un solo dato del visitante, y esta prueba lo mantiene así.
"""

from __future__ import annotations

from urllib.parse import urlparse

import pytest
from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from portafolio.config import cargar_config

PAGINAS = ["/", "/trabajos", "/trabajos/proyecto-1", "/no-existe"]

DOMINIOS_PROHIBIDOS = (
    "google-analytics.com",
    "googletagmanager.com",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "cdn.jsdelivr.net",
    "cdnjs.cloudflare.com",
    "unpkg.com",
    "facebook.net",
    "doubleclick.net",
    "hotjar.com",
    "clarity.ms",
)

CONFIG = cargar_config()


@pytest.mark.parametrize("ruta", PAGINAS)
def test_sin_dominios_de_terceros(client: FlaskClient, ruta: str) -> None:
    cuerpo = client.get(ruta).get_data(as_text=True)
    encontrados = [d for d in DOMINIOS_PROHIBIDOS if d in cuerpo]
    assert encontrados == [], f"{ruta} carga recursos de terceros: {encontrados}"


@pytest.mark.parametrize("ruta", PAGINAS)
def test_ningun_recurso_se_carga_desde_otro_origen(client: FlaskClient, ruta: str) -> None:
    """Los enlaces externos son navegación; los recursos deben ser todos locales.

    Se comparan orígenes, no la simple presencia de una URL absoluta: el enlace
    canónico apunta al propio sitio y es correcto que sea absoluto.
    """
    doc = BeautifulSoup(client.get(ruta).get_data(as_text=True), "html.parser")
    propio = urlparse(CONFIG.url_base).netloc

    ajenos: list[str] = []
    for etiqueta in doc.find_all(["img", "script", "link", "iframe", "source", "video"]):
        destino = etiqueta.get("src") or etiqueta.get("href")
        if not destino:
            continue
        host = urlparse(str(destino)).netloc
        if host and host != propio:
            ajenos.append(str(destino))

    assert ajenos == [], f"{ruta} carga recursos de otro origen: {ajenos}"


@pytest.mark.parametrize("ruta", PAGINAS)
def test_no_se_fija_ninguna_cookie(client: FlaskClient, ruta: str) -> None:
    assert "Set-Cookie" not in client.get(ruta).headers


@pytest.mark.parametrize("ruta", PAGINAS)
def test_no_hay_formularios(client: FlaskClient, ruta: str) -> None:
    """FR-006: el sitio no recoge ninguna entrada del visitante."""
    cuerpo = client.get(ruta).get_data(as_text=True)
    assert "<form" not in cuerpo.lower()
    assert "<input" not in cuerpo.lower()
