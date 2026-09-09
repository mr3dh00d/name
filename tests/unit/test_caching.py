"""Cabeceras de caché de CDN (INV-H10 y Principio IV).

La caché de la CDN no es una optimización añadida: es el mecanismo del que
depende el p95 < 200 ms. Si estas cabeceras desaparecen, el presupuesto se
incumple aunque el renderizado siga siendo rápido.
"""

from __future__ import annotations

import pytest

from portafolio.caching import CACHE_ERROR, CACHE_PAGINA, aplicar_cache


@pytest.mark.parametrize("directiva", ["public", "s-maxage=", "stale-while-revalidate="])
def test_pagina_lleva_las_tres_directivas(directiva: str) -> None:
    assert directiva in CACHE_PAGINA


def test_error_no_lleva_cache_larga() -> None:
    """Una página de error cacheada durante un año sobreviviría a su propia causa."""
    assert "s-maxage=31536000" not in CACHE_ERROR
    assert "no-store" in CACHE_ERROR or "max-age=0" in CACHE_ERROR


def test_aplicar_cache_asigna_la_cabecera() -> None:
    class RespuestaFalsa:
        def __init__(self) -> None:
            self.headers: dict[str, str] = {}

    respuesta = RespuestaFalsa()
    aplicar_cache(respuesta, CACHE_PAGINA)
    assert respuesta.headers["Cache-Control"] == CACHE_PAGINA
