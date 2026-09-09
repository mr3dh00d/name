"""Contrato de `GET /trabajos/<slug>` (contracts/routes.md).

Incluye los casos que separan una ficha correcta de una vulnerabilidad: un slug
inexistente y un slug malformado deben devolver 404, nunca 500 ni una lectura
fuera de `content/`.
"""

from __future__ import annotations

from bs4 import Tag
from flask.testing import FlaskClient

from portafolio.content.models import Contenido
from tests.contract.invariantes import verificar_invariantes

SLUGS_MALFORMADOS = [
    "Proyecto-1",
    "proyecto 1",
    "proyecto_1",
    "../perfil",
    "..%2Fperfil",
    "proyecto-1.toml",
    "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "proyecto-1/../../secreto",
]


def test_responde_200_y_cumple_los_invariantes(client: FlaskClient) -> None:
    respuesta = client.get("/trabajos/proyecto-1")
    assert respuesta.status_code == 200
    verificar_invariantes(respuesta)


def test_muestra_el_contenido_completo(client: FlaskClient, contenido_valido: Contenido) -> None:
    trabajo = contenido_valido.trabajo_por_slug("proyecto-1")
    assert trabajo is not None
    cuerpo = client.get("/trabajos/proyecto-1").get_data(as_text=True)
    assert trabajo.problema in cuerpo
    assert trabajo.rol in cuerpo
    assert trabajo.resultado in cuerpo
    for decision in trabajo.decisiones:
        assert decision in cuerpo


def test_enlace_directo_sin_referer(client: FlaskClient) -> None:
    """La ficha no depende de haber visitado antes la página principal."""
    respuesta = client.get("/trabajos/proyecto-2", headers={})
    assert respuesta.status_code == 200
    assert "Referer" not in respuesta.request.headers


def test_ofrece_vuelta_al_indice(client: FlaskClient) -> None:
    doc = verificar_invariantes(client.get("/trabajos/proyecto-1"))
    assert doc.select_one('a[href="/trabajos"]') is not None


def test_los_enlaces_externos_son_seguros(client: FlaskClient) -> None:
    doc = verificar_invariantes(client.get("/trabajos/proyecto-1"))
    externos = [
        a for a in doc.select(".ficha__enlaces a[href]") if str(a["href"]).startswith("http")
    ]
    assert externos, "el trabajo de prueba tiene enlaces externos"
    for enlace in externos:
        assert enlace.get("target") == "_blank"
        assert "noopener" in " ".join(enlace.get("rel") or [])


def test_og_title_es_el_del_trabajo(client: FlaskClient, contenido_valido: Contenido) -> None:
    """FR-019: compartir una ficha debe mostrar la ficha, no el sitio."""
    doc = verificar_invariantes(client.get("/trabajos/proyecto-1"))
    og = doc.find("meta", attrs={"property": "og:title"})
    assert isinstance(og, Tag)
    trabajo = contenido_valido.trabajo_por_slug("proyecto-1")
    assert trabajo is not None
    assert og["content"] == trabajo.titulo


def test_og_url_es_la_direccion_canonica_de_la_ficha(client: FlaskClient) -> None:
    doc = verificar_invariantes(client.get("/trabajos/proyecto-1"))
    og = doc.find("meta", attrs={"property": "og:url"})
    assert isinstance(og, Tag)
    assert str(og["content"]).endswith("/trabajos/proyecto-1")


def test_slug_inexistente_devuelve_404(client: FlaskClient) -> None:
    respuesta = client.get("/trabajos/no-existe")
    assert respuesta.status_code == 404
    assert "Traceback" not in respuesta.get_data(as_text=True)


def test_slug_malformado_nunca_produce_error_del_servidor(client: FlaskClient) -> None:
    """El slug se resuelve en memoria, así que el recorrido de rutas no lee nada."""
    for slug in SLUGS_MALFORMADOS:
        respuesta = client.get(f"/trabajos/{slug}")
        assert respuesta.status_code == 404, f"{slug} devolvió {respuesta.status_code}"
        cuerpo = respuesta.get_data(as_text=True)
        assert "root:" not in cuerpo
        assert "nombre =" not in cuerpo


def test_metodo_no_admitido(client: FlaskClient) -> None:
    assert client.post("/trabajos/proyecto-1").status_code == 405
