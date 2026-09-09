"""Fixtures compartidas.

Todas cargan desde ``tests/fixtures/``, nunca desde ``content/``. El Principio II
exige determinismo total: una prueba que dependiera del contenido real fallaria
al editarlo, que es exactamente el tipo de prueba inestable que la constitucion
prohibe.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from portafolio import create_app
from portafolio.content.loader import cargar_contenido
from portafolio.content.models import Contenido

FIXTURES = Path(__file__).parent / "fixtures"
CONTENIDO_VALIDO = FIXTURES / "content"
CONTENIDO_VACIO = FIXTURES / "content_vacio"
CONTENIDO_INVALIDO = FIXTURES / "content_invalid"
PUBLICO = FIXTURES / "public"


@pytest.fixture(scope="session")
def contenido_valido() -> Contenido:
    """Contenido de prueba completo: perfil, 3 capacidades, 2 experiencias, 4 trabajos."""
    return cargar_contenido(CONTENIDO_VALIDO, PUBLICO)


@pytest.fixture(scope="session")
def contenido_vacio() -> Contenido:
    """Contenido con perfil valido y todas las colecciones vacias (FR-010)."""
    return cargar_contenido(CONTENIDO_VACIO, PUBLICO)


@pytest.fixture
def app(contenido_valido: Contenido) -> Flask:
    """Aplicacion Flask con el contenido de prueba ya cargado."""
    return create_app(contenido=contenido_valido, testing=True)


@pytest.fixture
def app_vacia(contenido_vacio: Contenido) -> Flask:
    """Aplicacion Flask sin capacidades, experiencia ni trabajos."""
    return create_app(contenido=contenido_vacio, testing=True)


@pytest.fixture
def client(app: Flask) -> Iterator[FlaskClient]:
    """Cliente de pruebas sobre la aplicacion con contenido completo."""
    with app.test_client() as c:
        yield c


@pytest.fixture
def client_vacio(app_vacia: Flask) -> Iterator[FlaskClient]:
    """Cliente de pruebas sobre la aplicacion con colecciones vacias."""
    with app_vacia.test_client() as c:
        yield c
