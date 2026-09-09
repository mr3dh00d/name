"""La aplicación carga el contenido una sola vez, al arrancar (Principio IV)."""

from __future__ import annotations

import builtins
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from flask import Flask

from portafolio import create_app
from portafolio.content.errors import ContentValidationError
from portafolio.content.models import Contenido
from tests.conftest import CONTENIDO_VALIDO, PUBLICO


def test_la_aplicacion_se_construye(app: Flask) -> None:
    assert isinstance(app, Flask)


def test_el_contenido_queda_disponible(app: Flask, contenido_valido: Contenido) -> None:
    assert app.extensions["contenido"] is contenido_valido


def test_una_peticion_no_abre_ningun_archivo_de_contenido(
    app: Flask, monkeypatch: pytest.MonkeyPatch
) -> None:
    """El Principio IV prohíbe la E/S bloqueante en la ruta de petición.

    Esta es la prueba que lo hace verificable en lugar de aspiracional: si alguien
    introduce una lectura de disco en una vista, esta prueba falla.
    """
    abiertos: list[str] = []
    open_real: Callable[..., Any] = builtins.open

    def open_espia(archivo: Any, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        abiertos.append(str(archivo))
        return open_real(archivo, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", open_espia)
    with app.test_client() as client:
        client.get("/")

    del_contenido = [a for a in abiertos if a.endswith(".toml")]
    assert del_contenido == [], f"la petición leyó contenido del disco: {del_contenido}"


def test_carga_el_contenido_del_disco_si_no_se_le_inyecta() -> None:
    """En producción no se inyecta contenido: la factoría lo carga del disco."""
    app = create_app(
        directorio_contenido=CONTENIDO_VALIDO,
        directorio_publico=PUBLICO,
        testing=True,
    )
    assert app.extensions["contenido"].perfil.nombre == "Ada Prueba"


def test_contenido_invalido_impide_arrancar(tmp_path: Path) -> None:
    """Un contenido roto debe detener el arranque, no degradar el sitio (FR-012)."""
    (tmp_path / "perfil.toml").write_text('nombre = "Solo el nombre"\n', encoding="utf-8")
    with pytest.raises(ContentValidationError):
        create_app(directorio_contenido=tmp_path, directorio_publico=PUBLICO, testing=True)
