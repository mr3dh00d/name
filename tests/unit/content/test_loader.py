"""Carga de contenido: TOML a modelos, orden de presentacion y agrupacion."""

from __future__ import annotations

from portafolio.content.loader import ordenar_trabajos
from portafolio.content.models import Contenido
from tests.unit.content.factorias import trabajo


def test_carga_el_perfil(contenido_valido: Contenido) -> None:
    assert contenido_valido.perfil.nombre == "Ada Prueba"
    assert contenido_valido.perfil.titular == "Ingeniera de Software"


def test_carga_todas_las_capacidades(contenido_valido: Contenido) -> None:
    assert {c.nombre for c in contenido_valido.capacidades} == {"Python", "Flask", "PostgreSQL"}


def test_carga_todos_los_trabajos(contenido_valido: Contenido) -> None:
    assert len(contenido_valido.trabajos) == 4


def test_trabajos_ordenados_por_orden_ascendente(contenido_valido: Contenido) -> None:
    ordenes = [t.orden for t in contenido_valido.trabajos]
    assert ordenes == sorted(ordenes)


def test_desempate_de_orden_por_titulo() -> None:
    """A igualdad de `orden`, el criterio estable es el titulo (contracts/routes.md)."""
    desordenados = (trabajo("b", orden=10), trabajo("a", orden=10), trabajo("c", orden=5))
    assert [t.slug for t in ordenar_trabajos(desordenados)] == ["c", "a", "b"]


def test_experiencia_en_orden_cronologico_inverso(contenido_valido: Contenido) -> None:
    fechas = [e.fecha_inicio for e in contenido_valido.experiencia]
    assert fechas == sorted(fechas, reverse=True)


def test_experiencia_actual_encabeza(contenido_valido: Contenido) -> None:
    assert contenido_valido.experiencia[0].actual is True


def test_destacados_filtra_correctamente(contenido_valido: Contenido) -> None:
    destacados = contenido_valido.destacados
    assert len(destacados) == 3
    assert all(t.destacado for t in destacados)


def test_capacidades_agrupadas_por_categoria(contenido_valido: Contenido) -> None:
    grupos = contenido_valido.capacidades_por_categoria()
    assert set(grupos) == {"Lenguajes", "Frameworks", "Datos"}
    assert [c.nombre for c in grupos["Lenguajes"]] == ["Python"]


def test_busqueda_por_slug_encuentra(contenido_valido: Contenido) -> None:
    trabajo = contenido_valido.trabajo_por_slug("proyecto-1")
    assert trabajo is not None
    assert trabajo.titulo == "Proyecto Destacado 1"


def test_busqueda_por_slug_inexistente_devuelve_nulo(contenido_valido: Contenido) -> None:
    assert contenido_valido.trabajo_por_slug("no-existe") is None


def test_busqueda_por_slug_no_toca_el_disco(contenido_valido: Contenido) -> None:
    """Un slug con recorrido de rutas no puede leer nada: la busqueda es en memoria."""
    assert contenido_valido.trabajo_por_slug("../../etc/passwd") is None


def test_contenido_es_inmutable(contenido_valido: Contenido) -> None:
    assert isinstance(contenido_valido.trabajos, tuple)
    assert isinstance(contenido_valido.capacidades, tuple)
