"""Lectura tipada de las estadísticas de pytest-benchmark.

``benchmark.stats`` está anotado como ``Any | None`` en el paquete, lo que mypy
rechaza al indexarlo. Este ayudante concentra la conversión en un solo punto en
lugar de esparcir ignores por las pruebas.
"""

from __future__ import annotations

from typing import cast

from pytest_benchmark.fixture import BenchmarkFixture


def media_segundos(benchmark: BenchmarkFixture) -> float:
    """Duración media de la última medición, en segundos."""
    estadisticas = benchmark.stats
    assert estadisticas is not None, "no hay medición: ¿se llamó a benchmark(...)?"
    return float(cast(float, estadisticas["mean"]))
