"""Contrato de la página de error (FR-018)."""

from __future__ import annotations

from flask.testing import FlaskClient

from tests.contract.invariantes import verificar_invariantes

FUGAS_TECNICAS = ("Traceback", "werkzeug", "NotFound", "/Users/", "/var/task", 'File "')


def test_ruta_desconocida_devuelve_404(client: FlaskClient) -> None:
    respuesta = client.get("/no-existe")
    assert respuesta.status_code == 404
    verificar_invariantes(respuesta, cachea=False)


def test_ofrece_rutas_de_navegacion(client: FlaskClient) -> None:
    doc = verificar_invariantes(client.get("/no-existe"), cachea=False)
    assert doc.select_one('a[href="/"]') is not None
    assert doc.select_one('a[href="/trabajos"]') is not None


def test_no_filtra_detalles_tecnicos(client: FlaskClient) -> None:
    cuerpo = client.get("/no-existe").get_data(as_text=True)
    for fuga in FUGAS_TECNICAS:
        assert fuga not in cuerpo, f"la página de error filtra '{fuga}'"


def test_no_se_cachea_con_la_vida_larga(client: FlaskClient) -> None:
    """Una dirección puede pasar a existir en el siguiente despliegue."""
    cache = client.get("/no-existe").headers.get("Cache-Control", "")
    assert "s-maxage=31536000" not in cache
    assert "must-revalidate" in cache or "no-store" in cache


def test_conserva_la_identidad_del_sitio(client: FlaskClient) -> None:
    cuerpo = client.get("/no-existe").get_data(as_text=True)
    assert "Ada Prueba" in cuerpo
