"""Un caso por invariante del agregado (data-model.md, INV-01 a INV-04).

Cada fallo debe nombrar la entrada y el campo en conflicto. FR-012 no pide que la
carga falle: pide que diga **donde** esta el problema.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from portafolio.content.errors import ContentValidationError
from portafolio.content.loader import cargar_contenido, validar_invariantes
from portafolio.content.models import Contenido
from tests.conftest import CONTENIDO_INVALIDO, PUBLICO
from tests.unit.content.factorias import capacidad, perfil, trabajo


def cargar_invalido(variante: str) -> ContentValidationError:
    """Carga una variante defectuosa y devuelve el error que produce."""
    with pytest.raises(ContentValidationError) as exc:
        cargar_contenido(CONTENIDO_INVALIDO / variante, PUBLICO)
    return exc.value


def test_inv01_slug_duplicado() -> None:
    """INV-01: dos trabajos no pueden compartir slug."""
    contenido = Contenido(
        perfil=perfil(),
        capacidades=(capacidad("Python"),),
        trabajos=(trabajo("repetido"), trabajo("repetido")),
    )
    with pytest.raises(ContentValidationError) as exc:
        validar_invariantes(contenido, Path("content"), PUBLICO)
    assert exc.value.campo == "slug"
    assert "repetido" in str(exc.value)


def test_inv02_capacidad_colgante() -> None:
    """INV-02: un trabajo no puede referir una capacidad que no existe."""
    error = cargar_invalido("capacidad_colgante")
    assert error.campo == "capacidades"
    assert "Cobol" in str(error)
    assert "proyecto-1" in str(error)


def test_inv03_periodos_actuales_solapados() -> None:
    """INV-03: no puede haber dos experiencias actuales con periodos solapados."""
    error = cargar_invalido("actuales_solapadas")
    assert error.campo == "actual"


def test_inv04_ruta_inexistente_bajo_public() -> None:
    """INV-04: toda ruta referenciada debe existir en public/."""
    error = cargar_invalido("ruta_inexistente")
    assert error.campo == "cv"
    assert "no-existe.pdf" in str(error)


def test_slug_debe_coincidir_con_el_nombre_del_archivo() -> None:
    error = cargar_invalido("slug_no_coincide")
    assert error.campo == "slug"
    assert "proyecto-1" in error.archivo


def test_campo_obligatorio_ausente_nombra_el_campo() -> None:
    error = cargar_invalido("campo_obligatorio_ausente")
    assert error.campo == "titular"
    assert "perfil.toml" in error.archivo


def test_campo_desconocido_nombra_la_errata() -> None:
    error = cargar_invalido("campo_desconocido")
    assert "titluo" in error.campo


def test_fechas_incoherentes() -> None:
    error = cargar_invalido("fechas_incoherentes")
    assert "fecha_fin" in error.campo


def test_imagen_sin_alt() -> None:
    error = cargar_invalido("imagen_sin_alt")
    assert "alt" in error.campo


def test_enlace_no_descriptivo() -> None:
    error = cargar_invalido("enlace_no_descriptivo")
    assert "etiqueta" in error.campo


def test_url_no_https() -> None:
    error = cargar_invalido("url_no_https")
    assert "url" in error.campo


def test_perfil_sin_enlaces() -> None:
    """Sin seccion de contacto, un perfil sin enlaces deja el sitio sin salida."""
    error = cargar_invalido("perfil_sin_enlaces")
    assert "enlaces" in error.campo


def test_perfil_ausente_detiene_la_carga() -> None:
    error = cargar_invalido("perfil_ausente")
    assert "perfil.toml" in error.archivo
