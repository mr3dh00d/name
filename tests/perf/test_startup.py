"""Presupuesto de arranque de la aplicación (Principio IV, < 1 s).

Importa porque el arranque es exactamente lo que paga un arranque en frío de la
función, y de él depende el p99 < 500 ms.
"""

from __future__ import annotations

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from portafolio import create_app
from portafolio.config import cargar_config
from portafolio.content.loader import cargar_contenido
from tests.perf._medicion import media_segundos

PRESUPUESTO_ARRANQUE = 1.0
PRESUPUESTO_CARGA = 0.5

CONFIG = cargar_config()


@pytest.mark.perf
def test_arranque_con_el_contenido_real(benchmark: BenchmarkFixture) -> None:
    app = benchmark(
        lambda: create_app(
            directorio_contenido=CONFIG.directorio_contenido,
        )
    )
    assert app is not None

    media = media_segundos(benchmark)
    assert media < PRESUPUESTO_ARRANQUE, (
        f"create_app tarda {media:.3f} s, por encima de {PRESUPUESTO_ARRANQUE} s. "
        "Es el coste que paga cada arranque en frío de la función"
    )


@pytest.mark.perf
def test_carga_de_contenido(benchmark: BenchmarkFixture) -> None:
    contenido = benchmark(
        lambda: cargar_contenido(CONFIG.directorio_contenido, CONFIG.directorio_publico)
    )
    assert contenido.perfil is not None
    assert media_segundos(benchmark) < PRESUPUESTO_CARGA
