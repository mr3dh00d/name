"""La aplicación arranca aunque `public/` no esté en el paquete desplegado.

`public/` lo sirve la CDN, no la función. Que la plataforma incluya o no ese
directorio en el bundle de la función es un detalle de empaquetado del que el
arranque no debe depender: si dependiera, un cambio de empaquetado tumbaría el
sitio entero.

La comprobación de que los activos existen (INV-04) sigue siendo obligatoria,
pero es una puerta de **publicación**: la ejecuta `scripts/build.py` durante el
build, cuando el repositorio completo sí está presente.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from portafolio import create_app
from portafolio.content.errors import ContentValidationError
from portafolio.content.loader import cargar_contenido
from tests.conftest import CONTENIDO_VALIDO


def test_la_aplicacion_arranca_sin_directorio_de_activos(tmp_path: Path) -> None:
    contenido = tmp_path / "content"
    shutil.copytree(CONTENIDO_VALIDO, contenido)

    app = create_app(directorio_contenido=contenido, testing=True)
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        assert client.get("/trabajos/proyecto-1").status_code == 200


def test_sin_activos_no_se_valida_inv04(tmp_path: Path) -> None:
    contenido = tmp_path / "content"
    shutil.copytree(CONTENIDO_VALIDO, contenido)
    cargado = cargar_contenido(contenido, publico=None)
    assert cargado.perfil.cv == "cv/cv.pdf"


def test_con_activos_inv04_sigue_siendo_obligatorio(tmp_path: Path) -> None:
    """Desactivar la comprobación no puede convertirla en opcional donde importa."""
    contenido = tmp_path / "content"
    shutil.copytree(CONTENIDO_VALIDO, contenido)
    vacio = tmp_path / "public_vacio"
    vacio.mkdir()

    with pytest.raises(ContentValidationError) as exc:
        cargar_contenido(contenido, publico=vacio)
    assert exc.value.campo == "cv"
