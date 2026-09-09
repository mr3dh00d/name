"""Toda ruta referenciada existe bajo public/ (INV-04, caso «recurso ausente»).

Esta prueba sí mira el contenido real del repositorio: es precisamente lo que
debe comprobar, porque un activo que falta en `content/` rompe el sitio publicado
aunque todas las demás pruebas pasen con sus fixtures.
"""

from __future__ import annotations

from portafolio.config import cargar_config
from portafolio.content.loader import cargar_contenido

CONFIG = cargar_config()


def test_el_contenido_real_carga_sin_errores() -> None:
    cargar_contenido(CONFIG.directorio_contenido, CONFIG.directorio_publico)


def test_el_cv_existe() -> None:
    contenido = cargar_contenido(CONFIG.directorio_contenido, CONFIG.directorio_publico)
    assert (CONFIG.directorio_publico / contenido.perfil.cv).is_file()


def test_toda_imagen_de_trabajo_existe() -> None:
    contenido = cargar_contenido(CONFIG.directorio_contenido, CONFIG.directorio_publico)
    for trabajo in contenido.trabajos:
        for imagen in trabajo.imagenes:
            assert (CONFIG.directorio_publico / imagen.ruta).is_file(), (
                f"{trabajo.slug}: falta {imagen.ruta}"
            )


def test_la_hoja_de_estilos_existe() -> None:
    """base.html la referencia de forma fija, así que su ausencia rompe el diseño."""
    assert (CONFIG.directorio_publico / "css" / "site.css").is_file()


def test_el_favicon_existe() -> None:
    assert (CONFIG.directorio_publico / "favicon.ico").is_file()
