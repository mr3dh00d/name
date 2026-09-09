"""Colecciones vacias cargan sin error; un perfil ausente no (FR-010)."""

from __future__ import annotations

from portafolio.content.models import Contenido


def test_colecciones_vacias_son_validas(contenido_vacio: Contenido) -> None:
    assert contenido_vacio.capacidades == ()
    assert contenido_vacio.experiencia == ()
    assert contenido_vacio.trabajos == ()


def test_el_perfil_sigue_presente(contenido_vacio: Contenido) -> None:
    """Un contenido vacio no es un contenido sin identidad."""
    assert contenido_vacio.perfil.nombre


def test_destacados_vacio_no_falla(contenido_vacio: Contenido) -> None:
    assert contenido_vacio.destacados == ()


def test_agrupacion_vacia_no_falla(contenido_vacio: Contenido) -> None:
    assert contenido_vacio.capacidades_por_categoria() == {}
