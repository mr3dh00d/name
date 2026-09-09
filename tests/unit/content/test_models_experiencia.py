"""Validacion del modelo Experiencia, incluida la coherencia de fechas."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest
from pydantic import ValidationError

from portafolio.content.models import Experiencia

BASE = {
    "organizacion": "Empresa",
    "rol": "Ingeniera",
    "fecha_inicio": date(2021, 1, 15),
    "fecha_fin": date(2024, 2, 28),
    "descripcion": "Desarrollo de servicios internos de facturacion y sus integraciones.",
}


def test_experiencia_valida() -> None:
    exp = Experiencia.model_validate(BASE)
    assert exp.actual is False


def test_actual_sin_fecha_fin_es_valido() -> None:
    datos = {k: v for k, v in BASE.items() if k != "fecha_fin"}
    assert Experiencia.model_validate({**datos, "actual": True}).actual is True


def test_fecha_fin_obligatoria_si_no_es_actual() -> None:
    datos = {k: v for k, v in BASE.items() if k != "fecha_fin"}
    with pytest.raises(ValidationError) as exc:
        Experiencia.model_validate(datos)
    assert "fecha_fin" in str(exc.value)


def test_actual_con_fecha_fin_falla() -> None:
    with pytest.raises(ValidationError):
        Experiencia.model_validate({**BASE, "actual": True})


def test_fecha_fin_anterior_a_inicio_falla() -> None:
    with pytest.raises(ValidationError) as exc:
        Experiencia.model_validate({**BASE, "fecha_fin": date(2020, 1, 1)})
    assert "fecha_fin" in str(exc.value)


def test_fecha_inicio_futura_falla() -> None:
    manana = datetime.now(UTC).date() + timedelta(days=1)
    with pytest.raises(ValidationError):
        Experiencia.model_validate({**BASE, "fecha_inicio": manana, "fecha_fin": manana})


def test_logros_opcionales() -> None:
    assert Experiencia.model_validate(BASE).logros == ()


def test_demasiados_logros_falla() -> None:
    with pytest.raises(ValidationError):
        Experiencia.model_validate(
            {**BASE, "logros": [f"Logro numero {i} del periodo" for i in range(9)]}
        )


def test_descripcion_demasiado_corta_falla() -> None:
    with pytest.raises(ValidationError):
        Experiencia.model_validate({**BASE, "descripcion": "Corta"})


def test_campo_desconocido_falla() -> None:
    with pytest.raises(ValidationError):
        Experiencia.model_validate({**BASE, "empresa": "errata"})
