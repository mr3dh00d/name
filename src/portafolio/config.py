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


def raiz_del_proyecto() -> Path:
    """Directorio que contiene ``content/`` y ``public/``.

    **No** se deriva de ``__file__``. En Vercel el paquete se instala en
    ``site-packages``, fuera del arbol del repositorio, asi que contar
    directorios hacia arriba desde este archivo apunta al interior del entorno
    virtual. Fue la causa del despliegue fallido ``dpl_3biTwCgV``:

        archivo : /vercel/path0/.vercel/python/.venv/lib/python3.13/content/perfil.toml
        motivo  : el archivo no existe

    La plataforma ejecuta el build y la funcion con el directorio de trabajo en
    la raiz del proyecto, que es el contrato documentado del que hay que
    depender. El arbol de fuentes queda como respaldo para quien ejecute desde
    un subdirectorio de un checkout.
    """
    actual = Path.cwd()
    if (actual / "content").is_dir():
        return actual

    desde_fuente = Path(__file__).resolve().parent.parent.parent
    if (desde_fuente / "content").is_dir():
        return desde_fuente

    return actual


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
    raiz = raiz_del_proyecto()
    return Config(
        directorio_contenido=Path(os.environ.get("DIR_CONTENIDO", raiz / "content")),
        directorio_publico=Path(os.environ.get("DIR_PUBLICO", raiz / "public")),
        url_sitio=_url_del_sitio(),
        testing=testing,
    )
