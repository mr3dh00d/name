"""Utilidades compartidas por las vistas.

Las vistas son deliberadamente delgadas: seleccionan del contenido ya cargado y
eligen plantilla. Toda la lógica de validación y orden vive en el cargador, y la
de presentación en las plantillas.
"""

from __future__ import annotations

from typing import Any, cast

from flask import current_app, request

from portafolio.config import Config
from portafolio.content.models import Contenido


def contenido() -> Contenido:
    """Contenido cargado al arrancar. Nunca toca el disco (Principio IV)."""
    # `create_app` es el unico escritor de esta clave y siempre guarda un
    # `Contenido` ya validado, asi que la conversion es segura por construccion.
    return cast(Contenido, current_app.extensions["contenido"])


def config() -> Config:
    """Configuración de la aplicación."""
    return cast(Config, current_app.config["SITIO"])


def url_absoluta(ruta: str | None = None) -> str:
    """Construye la dirección canónica absoluta de una ruta.

    Las redes sociales y los buscadores exigen URL absolutas (FR-019, FR-020), y
    la petición no siempre conoce el dominio público.
    """
    return f"{config().url_base}{ruta if ruta is not None else request.path}"


def contexto_base(**extra: Any) -> dict[str, Any]:  # noqa: ANN401
    """Variables que toda plantilla necesita, más las propias de la página."""
    cont = contenido()
    perfil = cont.perfil
    por_defecto = url_absoluta(f"/{perfil.og_imagen}") if perfil.og_imagen else ""
    return {
        "perfil": perfil,
        "contenido": cont,
        "url_absoluta": url_absoluta(),
        "og_imagen_por_defecto": por_defecto,
        **extra,
    }
