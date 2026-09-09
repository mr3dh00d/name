"""Validacion de los modelos Trabajo e Imagen (data-model.md)."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from portafolio.content.models import Imagen, Trabajo

BASE = {
    "slug": "mi-proyecto",
    "titulo": "Mi Proyecto",
    "resumen": "Una descripcion breve que cabe en una sola linea de tarjeta.",
    "problema": "El equipo no observaba la latencia real y decidia por intuicion cada vez.",
    "rol": "Disenio e implementacion",
    "decisiones": ["Se eligio almacenamiento en columnas para que las consultas no crecieran."],
    "resultado": "La latencia p95 bajo de 900 ms a 180 ms de forma sostenida.",
    "capacidades": ["Python"],
    "fecha_inicio": date(2025, 3, 1),
}


def test_trabajo_valido() -> None:
    trabajo = Trabajo.model_validate(BASE)
    assert trabajo.destacado is False
    assert trabajo.orden == 100


@pytest.mark.parametrize(
    "slug", ["Mi-Proyecto", "mi proyecto", "mi_proyecto", "../secreto", "mi--proyecto", "-mi", ""]
)
def test_slug_malformado_falla(slug: str) -> None:
    """Un slug con recorrido de rutas nunca debe llegar al cargador."""
    with pytest.raises(ValidationError):
        Trabajo.model_validate({**BASE, "slug": slug})


@pytest.mark.parametrize("slug", ["mi-proyecto", "proyecto1", "a-b-c-1"])
def test_slug_valido(slug: str) -> None:
    assert Trabajo.model_validate({**BASE, "slug": slug}).slug == slug


@pytest.mark.parametrize(
    "campo",
    ["slug", "titulo", "resumen", "problema", "rol", "decisiones", "resultado", "capacidades"],
)
def test_campo_obligatorio_ausente_falla(campo: str) -> None:
    datos = {k: v for k, v in BASE.items() if k != campo}
    with pytest.raises(ValidationError):
        Trabajo.model_validate(datos)


def test_sin_decisiones_falla() -> None:
    with pytest.raises(ValidationError):
        Trabajo.model_validate({**BASE, "decisiones": []})


def test_demasiadas_decisiones_falla() -> None:
    with pytest.raises(ValidationError):
        Trabajo.model_validate(
            {
                **BASE,
                "decisiones": [f"Decision numero {i} tomada en el proyecto." for i in range(11)],
            }
        )


def test_sin_capacidades_falla() -> None:
    with pytest.raises(ValidationError):
        Trabajo.model_validate({**BASE, "capacidades": []})


def test_demasiadas_capacidades_falla() -> None:
    with pytest.raises(ValidationError):
        Trabajo.model_validate({**BASE, "capacidades": [f"Cap{i}" for i in range(13)]})


def test_fecha_fin_anterior_a_inicio_falla() -> None:
    with pytest.raises(ValidationError):
        Trabajo.model_validate({**BASE, "fecha_fin": date(2024, 1, 1)})


def test_sin_fecha_fin_significa_en_curso() -> None:
    assert Trabajo.model_validate(BASE).fecha_fin is None


def test_orden_negativo_falla() -> None:
    with pytest.raises(ValidationError):
        Trabajo.model_validate({**BASE, "orden": -1})


def test_campo_desconocido_falla() -> None:
    with pytest.raises(ValidationError) as exc:
        Trabajo.model_validate({**BASE, "titluo": "errata"})
    assert "titluo" in str(exc.value)


def test_imagen_valida() -> None:
    img = Imagen(ruta="img/a.png", alt="Captura del panel", ancho=1280, alto=720)
    assert img.ancho == 1280


@pytest.mark.parametrize("campo", ["ruta", "alt", "ancho", "alto"])
def test_imagen_campo_obligatorio_ausente_falla(campo: str) -> None:
    datos = {"ruta": "img/a.png", "alt": "Captura del panel", "ancho": 1280, "alto": 720}
    del datos[campo]
    with pytest.raises(ValidationError) as exc:
        Imagen.model_validate(datos)
    assert campo in str(exc.value)


@pytest.mark.parametrize("dimension", ["ancho", "alto"])
def test_imagen_dimension_no_positiva_falla(dimension: str) -> None:
    """CLS < 0,1 exige conocer la proporcion antes de descargar la imagen."""
    datos = {"ruta": "img/a.png", "alt": "Captura", "ancho": 1280, "alto": 720, dimension: 0}
    with pytest.raises(ValidationError):
        Imagen.model_validate(datos)


def test_imagen_alt_demasiado_corto_falla() -> None:
    with pytest.raises(ValidationError):
        Imagen.model_validate({"ruta": "img/a.png", "alt": "x", "ancho": 10, "alto": 10})
