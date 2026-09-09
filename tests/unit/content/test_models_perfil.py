"""Validacion del modelo Perfil y de EnlaceExterno (data-model.md)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from portafolio.content.models import EnlaceExterno, Perfil

BASE = {
    "nombre": "Ada Prueba",
    "titular": "Ingeniera de Software",
    "resumen": "Construye sistemas fiables y bien probados, con atencion al rendimiento medible.",
    "cv": "cv/cv.pdf",
    "enlaces": [{"etiqueta": "LinkedIn", "url": "https://linkedin.com/in/ada", "tipo": "linkedin"}],
}


def test_perfil_valido_se_construye() -> None:
    perfil = Perfil.model_validate(BASE)
    assert perfil.nombre == "Ada Prueba"


@pytest.mark.parametrize("campo", ["nombre", "titular", "resumen", "cv", "enlaces"])
def test_campo_obligatorio_ausente_falla(campo: str) -> None:
    datos = {k: v for k, v in BASE.items() if k != campo}
    with pytest.raises(ValidationError) as exc:
        Perfil.model_validate(datos)
    assert campo in str(exc.value)


@pytest.mark.parametrize("campo", ["nombre", "titular", "resumen"])
def test_cadena_en_blanco_falla(campo: str) -> None:
    with pytest.raises(ValidationError):
        Perfil.model_validate({**BASE, campo: "   "})


def test_resumen_demasiado_corto_falla() -> None:
    with pytest.raises(ValidationError):
        Perfil.model_validate({**BASE, "resumen": "Corto"})


def test_resumen_demasiado_largo_falla() -> None:
    with pytest.raises(ValidationError):
        Perfil.model_validate({**BASE, "resumen": "x" * 601})


def test_retrato_sin_alt_falla() -> None:
    """FR-014: toda imagen necesita alternativa textual, sin excepcion."""
    with pytest.raises(ValidationError) as exc:
        Perfil.model_validate({**BASE, "retrato": "img/retrato.jpg"})
    assert "retrato_alt" in str(exc.value)


def test_retrato_con_alt_es_valido() -> None:
    perfil = Perfil.model_validate(
        {**BASE, "retrato": "img/r.jpg", "retrato_alt": "Retrato de Ada"}
    )
    assert perfil.retrato_alt == "Retrato de Ada"


def test_sin_enlaces_falla() -> None:
    """Sin seccion de contacto (FR-006), los enlaces son la unica via de contacto."""
    with pytest.raises(ValidationError):
        Perfil.model_validate({**BASE, "enlaces": []})


def test_demasiados_enlaces_falla() -> None:
    enlaces = [{"etiqueta": f"Perfil {i}", "url": f"https://e{i}.com"} for i in range(9)]
    with pytest.raises(ValidationError):
        Perfil.model_validate({**BASE, "enlaces": enlaces})


def test_campo_desconocido_falla() -> None:
    """Protege contra erratas silenciosas como `titluo`."""
    with pytest.raises(ValidationError) as exc:
        Perfil.model_validate({**BASE, "titluo": "errata"})
    assert "titluo" in str(exc.value)


@pytest.mark.parametrize("etiqueta", ["aqui", "aquí", "enlace", "Click", "clic aqui", "aqui!"])
def test_etiqueta_no_descriptiva_falla(etiqueta: str) -> None:
    """Regla de accesibilidad: el texto del enlace debe entenderse aislado (FR-014)."""
    with pytest.raises(ValidationError):
        EnlaceExterno.model_validate({"etiqueta": etiqueta, "url": "https://ejemplo.com"})


@pytest.mark.parametrize("url", ["http://ejemplo.com", "ftp://ejemplo.com", "/ruta", "ejemplo.com"])
def test_url_no_https_falla(url: str) -> None:
    with pytest.raises(ValidationError):
        EnlaceExterno.model_validate({"etiqueta": "Mi perfil", "url": url})


def test_tipo_por_defecto_es_otro() -> None:
    assert EnlaceExterno(etiqueta="Mi web", url="https://ejemplo.com").tipo == "otro"


def test_tipo_invalido_falla() -> None:
    with pytest.raises(ValidationError):
        EnlaceExterno.model_validate(
            {"etiqueta": "Mi web", "url": "https://ejemplo.com", "tipo": "mastodon"}
        )


def test_perfil_es_inmutable() -> None:
    """El contenido es de solo lectura en ejecucion (Principio V)."""
    perfil = Perfil.model_validate(BASE)
    campo = "nombre"
    with pytest.raises(ValidationError):
        setattr(perfil, campo, "Otra")
