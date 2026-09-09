"""Valida todo el contenido y detiene la publicación si algo incumple (FR-012).

Es el mismo comando que ejecuta Vercel durante el build
(``[tool.vercel.scripts] build`` en ``pyproject.toml``), que ``pre-commit`` al
tocar ``content/`` y que la integración continua. Un solo camino, tres momentos.

Este archivo es un envoltorio de línea de comandos: **toda** la lógica vive en
``portafolio.content.loader``, como exige la constitución al prohibir lógica de
negocio fuera del paquete.
"""

from __future__ import annotations

import sys
from pathlib import Path

from portafolio.config import cargar_config
from portafolio.content.errors import ContentValidationError
from portafolio.content.loader import cargar_contenido


def validar(contenido: Path, publico: Path) -> int:
    """Valida el contenido y devuelve el código de salida del proceso."""
    try:
        cargado = cargar_contenido(contenido, publico)
    except ContentValidationError as error:
        print("\n✗ El contenido no es válido. La publicación se detiene.\n", file=sys.stderr)
        print(f"  archivo : {error.archivo}", file=sys.stderr)
        print(f"  entrada : {error.entrada}", file=sys.stderr)
        print(f"  campo   : {error.campo}", file=sys.stderr)
        print(f"  motivo  : {error.motivo}", file=sys.stderr)
        if error.valor_recibido is not None:
            print(f"  recibido: {error.valor_recibido!r}", file=sys.stderr)
        print(
            "\n  El formato esperado está en "
            "specs/001-portafolio-personal/contracts/content-schema.md\n",
            file=sys.stderr,
        )
        return 1

    print(
        f"✓ Contenido válido: {len(cargado.trabajos)} trabajos "
        f"({len(cargado.destacados)} destacados), "
        f"{len(cargado.capacidades)} capacidades, "
        f"{len(cargado.experiencia)} periodos de experiencia."
    )
    return 0


def main() -> int:
    """Punto de entrada del script de build."""
    config = cargar_config()
    return validar(config.directorio_contenido, config.directorio_publico)


if __name__ == "__main__":
    sys.exit(main())
