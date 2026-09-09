"""Filtros Jinja para presentar fechas y periodos en español.

Los nombres de mes están escritos en el módulo en lugar de obtenerse de la
configuración regional del sistema. Es deliberado: ``locale`` depende de qué
idiomas tenga instalados la máquina, y la función de Vercel no es la misma
máquina que el portátil de desarrollo. Una tabla de doce palabras elimina esa
dependencia y hace que las pruebas sean deterministas (Principio II).
"""

from __future__ import annotations

from datetime import date

MESES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)

GUION_LARGO = "–"


def formato_mes(fecha: date) -> str:
    """Devuelve el mes y el año de una fecha, por ejemplo ``enero de 2025``."""
    return f"{MESES[fecha.month - 1]} de {fecha.year}"


def formato_periodo(inicio: date, fin: date | None) -> str:
    """Formatea un periodo. Sin fecha de fin, se presenta como en curso."""
    desde = formato_mes(inicio)
    if fin is None:
        return f"{desde} {GUION_LARGO} actualidad"
    hasta = formato_mes(fin)
    if desde == hasta:
        return desde
    return f"{desde} {GUION_LARGO} {hasta}"


def formato_iso(fecha: date) -> str:
    """Fecha en formato ISO, para el atributo ``datetime`` de ``<time>``."""
    return fecha.isoformat()
