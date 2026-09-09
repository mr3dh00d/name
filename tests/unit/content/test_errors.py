"""ContentValidationError es contrato probado, no formato de mensaje (FR-012)."""

from __future__ import annotations

from portafolio.content.errors import ContentValidationError


def test_expone_los_cinco_datos_del_contrato() -> None:
    error = ContentValidationError(
        archivo="content/trabajos/x.toml",
        entrada="proyecto-1",
        campo="titulo",
        motivo="campo obligatorio ausente",
        valor_recibido=None,
    )
    assert error.archivo == "content/trabajos/x.toml"
    assert error.entrada == "proyecto-1"
    assert error.campo == "titulo"
    assert error.motivo == "campo obligatorio ausente"
    assert error.valor_recibido is None


def test_el_mensaje_nombra_archivo_entrada_y_campo() -> None:
    """FR-012 exige identificar la entrada y el campo defectuoso."""
    error = ContentValidationError(
        archivo="content/perfil.toml",
        entrada="perfil",
        campo="titular",
        motivo="campo obligatorio ausente",
    )
    mensaje = str(error)
    assert "content/perfil.toml" in mensaje
    assert "perfil" in mensaje
    assert "titular" in mensaje
    assert "campo obligatorio ausente" in mensaje


def test_es_una_excepcion() -> None:
    assert issubclass(ContentValidationError, Exception)


def test_valor_recibido_por_defecto_es_nulo() -> None:
    error = ContentValidationError(archivo="a.toml", entrada="e", campo="c", motivo="m")
    assert error.valor_recibido is None
