"""Constructores de modelos validos para pruebas que necesitan variar un campo."""

from __future__ import annotations

from datetime import date

from portafolio.content.models import Capacidad, Perfil, Trabajo


def perfil(**cambios: object) -> Perfil:
    """Perfil valido, con los cambios indicados aplicados encima."""
    base: dict[str, object] = {
        "nombre": "Ada Prueba",
        "titular": "Ingeniera",
        "resumen": "Construye sistemas fiables y bien probados, con rendimiento medible.",
        "cv": "cv/cv.pdf",
        "enlaces": [{"etiqueta": "LinkedIn", "url": "https://li.com/ada"}],
    }
    return Perfil.model_validate(base | cambios)


def trabajo(slug: str, **cambios: object) -> Trabajo:
    """Trabajo valido identificado por su slug."""
    base: dict[str, object] = {
        "slug": slug,
        "titulo": f"Trabajo {slug}",
        "resumen": "Una descripcion breve que cabe en una sola linea de tarjeta.",
        "problema": "El equipo no observaba la latencia real y decidia por intuicion cada vez.",
        "rol": "Disenio e implementacion",
        "decisiones": ["Se eligio almacenamiento en columnas para no crecer con el volumen."],
        "resultado": "La latencia p95 bajo de 900 ms a 180 ms de forma sostenida.",
        "capacidades": ["Python"],
        "fecha_inicio": date(2025, 1, 1),
    }
    return Trabajo.model_validate(base | cambios)


def capacidad(nombre: str, categoria: str = "Lenguajes") -> Capacidad:
    """Capacidad valida."""
    return Capacidad(nombre=nombre, categoria=categoria)
