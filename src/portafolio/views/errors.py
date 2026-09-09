"""Manejo de errores HTTP (FR-018).

Un enlace antiguo debe llevar a una página útil, no a una traza técnica. Y esa
página no se cachea con la vida larga de las demás: una dirección puede pasar a
existir en el siguiente despliegue.
"""

from __future__ import annotations

from flask import Flask, render_template
from werkzeug.exceptions import NotFound

from portafolio.caching import CACHE_ERROR
from portafolio.views._comun import contexto_base


def registrar(app: Flask) -> None:
    """Instala el manejador de 404 en la aplicación."""

    @app.errorhandler(NotFound)
    def no_encontrado(_error: NotFound) -> tuple[str, int, dict[str, str]]:
        cuerpo = render_template("404.html", **contexto_base())
        return cuerpo, 404, {"Cache-Control": CACHE_ERROR}
