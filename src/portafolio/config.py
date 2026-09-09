"""Configuración de la aplicación, leída del entorno.

El Principio III prohíbe secretos y rutas absolutas del entorno local en el
código: todo valor sale de una variable de entorno con un valor por defecto
seguro. Este portafolio no maneja ningún secreto, así que la configuración se
limita a rutas y a la dirección canónica del sitio.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent.parent

SITIO_POR_DEFECTO = "http://localhost:5000"


@dataclass(frozen=True, slots=True)
class Config:
    """Parámetros de ejecución del portafolio."""

    directorio_contenido: Path
    directorio_publico: Path
    url_sitio: str
    testing: bool = False

    @property
    def url_base(self) -> str:
        """Dirección canónica sin barra final, para construir URLs absolutas."""
        return self.url_sitio.rstrip("/")


def _url_del_sitio() -> str:
    """Resuelve la dirección pública, prefiriendo la que expone Vercel."""
    explicita = os.environ.get("URL_SITIO")
    if explicita:
        return explicita
    # Vercel expone el dominio del despliegue sin esquema.
    vercel = os.environ.get("VERCEL_PROJECT_PRODUCTION_URL") or os.environ.get("VERCEL_URL")
    if vercel:
        return f"https://{vercel}"
    return SITIO_POR_DEFECTO


def cargar_config(testing: bool = False) -> Config:
    """Construye la configuración a partir del entorno."""
    return Config(
        directorio_contenido=Path(os.environ.get("DIR_CONTENIDO", RAIZ_PROYECTO / "content")),
        directorio_publico=Path(os.environ.get("DIR_PUBLICO", RAIZ_PROYECTO / "public")),
        url_sitio=_url_del_sitio(),
        testing=testing,
    )
