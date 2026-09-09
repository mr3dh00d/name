"""Publicar contenido nuevo no exige tocar código (historia P3)."""

from __future__ import annotations

import shutil
from pathlib import Path

from portafolio import create_app
from portafolio.content.loader import cargar_contenido
from tests.conftest import CONTENIDO_VALIDO, PUBLICO

TRABAJO_NUEVO = """
slug = "trabajo-anadido"
titulo = "Trabajo Añadido"
resumen = "Un trabajo publicado sin modificar una sola línea de código."
problema = "Se necesitaba comprobar que publicar contenido no exige tocar la lógica del sitio."
rol = "Publicación de contenido"
decisiones = ["Se copió un archivo TOML al directorio de trabajos y nada más."]
resultado = "El trabajo aparece en el índice y en su ficha sin cambios en src/."
capacidades = ["Python"]
fecha_inicio = 2025-01-01
destacado = true
orden = 1
"""


def preparar(tmp_path: Path) -> Path:
    """Copia el contenido de prueba a un directorio temporal editable."""
    destino = tmp_path / "content"
    shutil.copytree(CONTENIDO_VALIDO, destino)
    return destino


def test_un_archivo_nuevo_se_publica(tmp_path: Path) -> None:
    contenido = preparar(tmp_path)
    (contenido / "trabajos" / "trabajo-anadido.toml").write_text(TRABAJO_NUEVO, encoding="utf-8")

    app = create_app(directorio_contenido=contenido, testing=True)
    with app.test_client() as client:
        assert "Trabajo Añadido" in client.get("/trabajos").get_data(as_text=True)
        assert client.get("/trabajos/trabajo-anadido").status_code == 200


def test_aparece_en_la_portada_si_es_destacado(tmp_path: Path) -> None:
    contenido = preparar(tmp_path)
    (contenido / "trabajos" / "trabajo-anadido.toml").write_text(TRABAJO_NUEVO, encoding="utf-8")

    app = create_app(directorio_contenido=contenido, testing=True)
    with app.test_client() as client:
        assert "Trabajo Añadido" in client.get("/").get_data(as_text=True)


def test_entra_en_el_sitemap(tmp_path: Path) -> None:
    contenido = preparar(tmp_path)
    (contenido / "trabajos" / "trabajo-anadido.toml").write_text(TRABAJO_NUEVO, encoding="utf-8")

    app = create_app(directorio_contenido=contenido, testing=True)
    with app.test_client() as client:
        assert "/trabajos/trabajo-anadido" in client.get("/sitemap.xml").get_data(as_text=True)


def test_retirar_un_archivo_lo_despublica(tmp_path: Path) -> None:
    contenido = preparar(tmp_path)
    (contenido / "trabajos" / "proyecto-1.toml").unlink()

    app = create_app(directorio_contenido=contenido, testing=True)
    with app.test_client() as client:
        assert client.get("/trabajos/proyecto-1").status_code == 404


def test_el_orden_lo_decide_el_contenido(tmp_path: Path) -> None:
    """El propietario controla la presentación desde los datos, no desde el código."""
    contenido = preparar(tmp_path)
    (contenido / "trabajos" / "trabajo-anadido.toml").write_text(TRABAJO_NUEVO, encoding="utf-8")

    cargado = cargar_contenido(contenido, PUBLICO)
    assert cargado.trabajos[0].slug == "trabajo-anadido", "orden = 1 debería colocarlo primero"
