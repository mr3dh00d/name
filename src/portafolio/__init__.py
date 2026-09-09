"""Factoría de la aplicación Flask del portafolio.

El contenido se carga y se valida **una sola vez**, al construir la aplicación.
A partir de ahí las vistas consultan un objeto en memoria y ninguna petición
vuelve a tocar el disco, como exige el Principio IV.

Un contenido inválido impide arrancar. Es intencionado: FR-012 pide que la
publicación se detenga, y un sitio que arranca con datos rotos ya está publicado.
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, Response

from portafolio.caching import CACHE_PAGINA
from portafolio.config import cargar_config
from portafolio.content.loader import cargar_contenido
from portafolio.content.models import Contenido
from portafolio.filters import formato_iso, formato_mes, formato_periodo
from portafolio.views import errors, home, projects, seo

__all__ = ["create_app"]


def _registrar_filtros(app: Flask) -> None:
    """Publica los filtros de fecha en el entorno Jinja."""
    app.jinja_env.filters["mes"] = formato_mes
    app.jinja_env.filters["periodo"] = formato_periodo
    app.jinja_env.filters["iso"] = formato_iso


def _registrar_blueprints(app: Flask) -> None:
    """Registra las vistas de cada blueprint."""
    app.register_blueprint(home.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(seo.bp)
    errors.registrar(app)


def _registrar_cache(app: Flask) -> None:
    """Aplica la caché de CDN a toda respuesta que no la haya fijado ya.

    Es el mecanismo del que depende el p95 del Principio IV, así que el valor por
    defecto es cachear; las excepciones (errores, recursos SEO) lo sobrescriben.
    """

    @app.after_request
    def _cabeceras(respuesta: Response) -> Response:
        respuesta.headers.setdefault("Cache-Control", CACHE_PAGINA)
        return respuesta


def create_app(
    contenido: Contenido | None = None,
    directorio_contenido: Path | None = None,
    directorio_publico: Path | None = None,
    testing: bool = False,
) -> Flask:
    """Construye la aplicación con su contenido ya validado.

    Args:
        contenido: Contenido ya cargado. Lo usan las pruebas para no depender del
            contenido real, que el Principio II exige por determinismo.
        directorio_contenido: Origen del contenido si no se inyecta uno cargado.
        directorio_publico: Directorio de activos, para validar las rutas (INV-04).
        testing: Activa el modo de pruebas de Flask.

    Returns:
        La aplicación lista para servir.

    Raises:
        ContentValidationError: Si el contenido del disco es inválido.
    """
    config = cargar_config(testing=testing)
    app = Flask(__name__)
    app.config["TESTING"] = testing
    app.config["SITIO"] = config

    if contenido is None:
        contenido = cargar_contenido(
            directorio_contenido or config.directorio_contenido,
            directorio_publico or config.directorio_publico,
        )
    app.extensions["contenido"] = contenido

    _registrar_filtros(app)
    _registrar_blueprints(app)
    _registrar_cache(app)
    return app
