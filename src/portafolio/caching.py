"""Cabeceras de caché de CDN.

El contenido del portafolio es idéntico para todos los visitantes y solo cambia
al desplegar: no hay sesiones, ni personalización, ni datos por visitante
(FR-006, FR-021). Por eso cachear la respuesta completa en el borde es correcto
por construcción, no un compromiso.

Es además el mecanismo del que depende el presupuesto de p95 < 200 ms del
Principio IV: con la CDN delante, la práctica totalidad del tráfico no llega a
invocar la función.
"""

from __future__ import annotations

from typing import Protocol

UN_ANIO = 31_536_000
UN_DIA = 86_400

# Páginas de contenido: inmutables entre despliegues, y cada despliegue invalida
# la caché de la CDN. `max-age` del navegador se deja corto para que un visitante
# recurrente vea los cambios sin vaciar su caché (escenario 3 de la historia P3).
CACHE_PAGINA = f"public, max-age=0, s-maxage={UN_ANIO}, stale-while-revalidate={UN_DIA}"

# Recursos derivados del contenido, con la misma vida que las páginas.
CACHE_SEO = f"public, max-age=0, s-maxage={UN_DIA}, stale-while-revalidate={UN_DIA}"

# Los errores no se cachean: una dirección puede pasar a existir en el siguiente
# despliegue, y un 404 cacheado un año sobreviviría a su propia causa.
CACHE_ERROR = "public, max-age=0, s-maxage=0, must-revalidate"


class ConCabeceras(Protocol):
    """Cualquier objeto con un diccionario de cabeceras, como una respuesta Flask."""

    headers: dict[str, str]


def aplicar_cache(respuesta: ConCabeceras, directiva: str) -> None:
    """Fija ``Cache-Control`` en la respuesta."""
    respuesta.headers["Cache-Control"] = directiva
