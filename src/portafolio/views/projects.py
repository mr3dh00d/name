"""Índice y ficha de trabajos: la historia de usuario P2."""

from __future__ import annotations

from flask import Blueprint, abort, render_template

from portafolio.views._comun import contenido, contexto_base, url_absoluta

bp = Blueprint("projects", __name__)


@bp.get("/trabajos")
def indice() -> str:
    """Lista todos los trabajos, destacados o no, en el orden del propietario."""
    return render_template("projects_index.html", **contexto_base(trabajos=contenido().trabajos))


@bp.get("/trabajos/<slug>")
def ficha(slug: str) -> str:
    """Muestra un trabajo por su slug.

    La búsqueda es contra la colección en memoria, nunca contra el sistema de
    archivos: por eso un slug con recorrido de rutas devuelve 404 en lugar de
    leer nada.
    """
    trabajo = contenido().trabajo_por_slug(slug)
    if trabajo is None:
        abort(404)
    og = trabajo.og_imagen or contenido().perfil.og_imagen
    return render_template(
        "project_detail.html",
        **contexto_base(
            trabajo=trabajo,
            og_imagen_trabajo=url_absoluta(f"/{og}") if og else "",
        ),
    )
