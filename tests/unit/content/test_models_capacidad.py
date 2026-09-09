"""Validacion del modelo Capacidad (data-model.md)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from portafolio.content.models import Capacidad


def test_capacidad_valida() -> None:
    cap = Capacidad(nombre="Python", categoria="Lenguajes", nivel="avanzado")
    assert cap.nombre == "Python"


def test_nivel_es_opcional() -> None:
    assert Capacidad(nombre="Python", categoria="Lenguajes").nivel is None


@pytest.mark.parametrize("campo", ["nombre", "categoria"])
def test_campo_obligatorio_ausente_falla(campo: str) -> None:
    datos = {"nombre": "Python", "categoria": "Lenguajes"}
    del datos[campo]
    with pytest.raises(ValidationError):
        Capacidad.model_validate(datos)


@pytest.mark.parametrize("nivel", ["basico", "intermedio", "avanzado", "experto"])
def test_niveles_admitidos(nivel: str) -> None:
    assert (
        Capacidad.model_validate(
            {"nombre": "Python", "categoria": "Lenguajes", "nivel": nivel}
        ).nivel
        == nivel
    )


def test_nivel_invalido_falla() -> None:
    with pytest.raises(ValidationError):
        Capacidad.model_validate({"nombre": "Python", "categoria": "Lenguajes", "nivel": "dios"})


def test_nombre_demasiado_largo_falla() -> None:
    with pytest.raises(ValidationError):
        Capacidad.model_validate({"nombre": "x" * 61, "categoria": "Lenguajes"})


def test_campo_desconocido_falla() -> None:
    with pytest.raises(ValidationError):
        Capacidad.model_validate({"nombre": "Python", "categoria": "Lenguajes", "anios": 5})
