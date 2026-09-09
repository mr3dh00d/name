"""Página principal: la historia de usuario P1 completa en una sola vista."""

from __future__ import annotations

from flask import Blueprint, render_template

from portafolio.views._comun import contenido, contexto_base

bp = Blueprint("home", __name__)


@bp.get("/")
def inicio() -> str:
    """Presenta identidad, capacidades, experiencia y trabajos destacados."""
    cont = contenido()
    return render_template(
        "home.html",
        **contexto_base(
            capacidades=cont.capacidades_por_categoria(),
            experiencia=cont.experiencia,
            destacados=cont.destacados,
        ),
    )
