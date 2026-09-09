"""Presupuesto de renderizado por página (Principio IV, < 20 ms).

El p95 real lo sostiene la caché de CDN, no el renderizado. Pero un renderizado
que se degrada es la señal temprana de que algo hace trabajo de más en la ruta
de petición, y esta prueba lo detecta antes de que llegue a producción.
"""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient
from pytest_benchmark.fixture import BenchmarkFixture

from tests.perf._medicion import media_segundos

PRESUPUESTO_SEGUNDOS = 0.020

RUTAS = ["/", "/trabajos", "/trabajos/proyecto-1", "/sitemap.xml", "/no-existe"]


@pytest.mark.perf
@pytest.mark.parametrize("ruta", RUTAS)
def test_renderizado_dentro_del_presupuesto(
    benchmark: BenchmarkFixture, client: FlaskClient, ruta: str
) -> None:
    resultado = benchmark(lambda: client.get(ruta))
    assert resultado.status_code in (200, 404)

    media = media_segundos(benchmark)
    assert media < PRESUPUESTO_SEGUNDOS, (
        f"{ruta} tarda {media * 1000:.1f} ms de media, por encima del "
        f"presupuesto de {PRESUPUESTO_SEGUNDOS * 1000:.0f} ms"
    )
