"""Contrato de `GET /trabajos` (contracts/routes.md)."""

from __future__ import annotations

from bs4 import Tag
from flask.testing import FlaskClient

from portafolio.content.models import Contenido
from tests.contract.invariantes import verificar_invariantes


def test_responde_200_y_cumple_los_invariantes(client: FlaskClient) -> None:
    respuesta = client.get("/trabajos")
    assert respuesta.status_code == 200
    verificar_invariantes(respuesta)


def test_muestra_todos_los_trabajos(client: FlaskClient, contenido_valido: Contenido) -> None:
    """A diferencia de la portada, el índice no filtra por destacado."""
    doc = verificar_invariantes(client.get("/trabajos"))
    slugs = {str(t.get("data-slug")) for t in doc.select(".tarjeta-trabajo")}
    assert slugs == {t.slug for t in contenido_valido.trabajos}
    assert "proyecto-secundario" in slugs


def test_orden_ascendente_por_orden(client: FlaskClient, contenido_valido: Contenido) -> None:
    doc = verificar_invariantes(client.get("/trabajos"))
    presentados = [str(t.get("data-slug")) for t in doc.select(".tarjeta-trabajo")]
    assert presentados == [t.slug for t in contenido_valido.trabajos]


def test_cada_elemento_enlaza_a_su_ficha(client: FlaskClient, contenido_valido: Contenido) -> None:
    doc = verificar_invariantes(client.get("/trabajos"))
    for trabajo in contenido_valido.trabajos:
        tarjeta = doc.select_one(f'.tarjeta-trabajo[data-slug="{trabajo.slug}"]')
        assert isinstance(tarjeta, Tag)
        enlace = tarjeta.find("a", href=True)
        assert isinstance(enlace, Tag)
        assert enlace["href"] == f"/trabajos/{trabajo.slug}"


def test_estado_vacio(client_vacio: FlaskClient) -> None:
    respuesta = client_vacio.get("/trabajos")
    assert respuesta.status_code == 200
    doc = verificar_invariantes(respuesta)
    assert doc.select_one(".estado-vacio") is not None


def test_metodo_no_admitido(client: FlaskClient) -> None:
    assert client.post("/trabajos").status_code == 405
