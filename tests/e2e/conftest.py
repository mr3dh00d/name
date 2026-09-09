"""Servidor real y navegador para las pruebas extremo a extremo.

El cliente de pruebas de Flask demuestra que un atributo existe; no demuestra que
el foco sea alcanzable ni que el contraste baste. SC-003 y SC-004 solo son
verificables en un navegador de verdad, así que estas pruebas levantan la
aplicación en un hilo y la visitan con Playwright.

Los activos de ``public/`` los sirve la CDN en producción, no Flask
(``contracts/routes.md``). Aquí se montan en el servidor de prueba para que el
navegador vea la misma página que verá un visitante.
"""

from __future__ import annotations

import socket
import threading
from collections.abc import Iterator
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, make_server

import pytest
from flask import Flask, Response, abort, send_from_directory

from portafolio import create_app
from portafolio.config import cargar_config
from portafolio.content.models import Contenido
from tests.conftest import PUBLICO

PUBLICO_REAL = cargar_config().directorio_publico


class HandlerSilencioso(WSGIRequestHandler):
    """Evita que cada petición ensucie la salida de pytest."""

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """No registra nada."""


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _con_activos(app: Flask, *directorios: Path) -> Flask:
    """Sirve los activos desde la aplicación, como hará la CDN en producción.

    Se consultan varios directorios en orden: los activos de prueba primero, y la
    ``public/`` real después, de donde salen la hoja de estilos y el favicon que
    ``base.html`` referencia de forma fija.
    """

    @app.get("/<path:recurso>")
    def activo(recurso: str) -> Response:
        for directorio in directorios:
            if (directorio / recurso).is_file():
                return send_from_directory(directorio, recurso)
        return abort(404)

    return app


@pytest.fixture(scope="session")
def servidor(contenido_valido: Contenido) -> Iterator[str]:
    """Levanta la aplicación en un hilo y devuelve su dirección base."""
    puerto = _puerto_libre()
    app = _con_activos(create_app(contenido=contenido_valido), PUBLICO, PUBLICO_REAL)
    httpd = make_server("127.0.0.1", puerto, app, handler_class=HandlerSilencioso)
    hilo = threading.Thread(target=httpd.serve_forever, daemon=True)
    hilo.start()
    try:
        yield f"http://127.0.0.1:{puerto}"
    finally:
        httpd.shutdown()
        hilo.join(timeout=5)
