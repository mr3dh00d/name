"""Recursos de difusión: sitemap y robots (FR-020)."""

from __future__ import annotations

from flask import Blueprint, Response, render_template

from portafolio.caching import CACHE_SEO
from portafolio.views._comun import contenido, url_absoluta

bp = Blueprint("seo", __name__)


@bp.get("/sitemap.xml")
def sitemap() -> Response:
    """Índice de todas las direcciones públicas, con URL absolutas."""
    rutas = ["/", "/trabajos", *[f"/trabajos/{t.slug}" for t in contenido().trabajos]]
    cuerpo = render_template("sitemap.xml", urls=[url_absoluta(r) for r in rutas])
    return Response(
        cuerpo,
        mimetype="application/xml",
        headers={"Cache-Control": CACHE_SEO},
    )


@bp.get("/robots.txt")
def robots() -> Response:
    """Permite la indexación y declara la dirección absoluta del sitemap."""
    cuerpo = f"User-agent: *\nAllow: /\n\nSitemap: {url_absoluta('/sitemap.xml')}\n"
    return Response(cuerpo, mimetype="text/plain", headers={"Cache-Control": CACHE_SEO})
