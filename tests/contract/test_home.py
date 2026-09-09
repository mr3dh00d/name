"""Contrato de `GET /` (contracts/routes.md).

Cubre toda la tabla de la página principal: éxito, identidad, capacidades,
experiencia, destacados, CV, estados vacíos y método no admitido.
"""

from __future__ import annotations

from bs4 import Tag
from flask.testing import FlaskClient

from portafolio.content.models import Contenido
from tests.contract.invariantes import verificar_invariantes


def test_responde_200_y_cumple_los_invariantes(client: FlaskClient) -> None:
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    verificar_invariantes(respuesta)


def test_muestra_la_identidad(client: FlaskClient, contenido_valido: Contenido) -> None:
    cuerpo = client.get("/").get_data(as_text=True)
    perfil = contenido_valido.perfil
    assert perfil.nombre in cuerpo
    assert perfil.titular in cuerpo
    assert perfil.resumen in cuerpo


def test_el_h1_es_el_nombre(client: FlaskClient, contenido_valido: Contenido) -> None:
    doc = verificar_invariantes(client.get("/"))
    h1 = doc.find("h1")
    assert isinstance(h1, Tag)
    assert contenido_valido.perfil.nombre in h1.get_text()


def test_muestra_todas_las_capacidades_agrupadas(
    client: FlaskClient, contenido_valido: Contenido
) -> None:
    cuerpo = client.get("/").get_data(as_text=True)
    for capacidad in contenido_valido.capacidades:
        assert capacidad.nombre in cuerpo
    for categoria in contenido_valido.capacidades_por_categoria():
        assert categoria in cuerpo


def test_muestra_la_experiencia_en_orden_inverso(
    client: FlaskClient, contenido_valido: Contenido
) -> None:
    cuerpo = client.get("/").get_data(as_text=True)
    posiciones = [cuerpo.index(e.organizacion) for e in contenido_valido.experiencia]
    assert posiciones == sorted(posiciones), (
        "la experiencia no aparece en orden cronológico inverso"
    )


def test_solo_muestra_los_trabajos_destacados(
    client: FlaskClient, contenido_valido: Contenido
) -> None:
    doc = verificar_invariantes(client.get("/"))
    tarjetas = doc.select(".tarjeta-trabajo")
    slugs = {str(t.get("data-slug")) for t in tarjetas}
    assert slugs == {t.slug for t in contenido_valido.destacados}
    assert "proyecto-secundario" not in slugs


def test_los_destacados_van_en_orden(client: FlaskClient, contenido_valido: Contenido) -> None:
    doc = verificar_invariantes(client.get("/"))
    presentados = [str(t.get("data-slug")) for t in doc.select(".tarjeta-trabajo")]
    assert presentados == [t.slug for t in contenido_valido.destacados]


def test_cada_tarjeta_lleva_titulo_resumen_y_capacidades(
    client: FlaskClient, contenido_valido: Contenido
) -> None:
    doc = verificar_invariantes(client.get("/"))
    for trabajo in contenido_valido.destacados:
        tarjeta = doc.select_one(f'.tarjeta-trabajo[data-slug="{trabajo.slug}"]')
        assert isinstance(tarjeta, Tag)
        texto = tarjeta.get_text()
        assert trabajo.titulo in texto
        assert trabajo.resumen in texto
        for capacidad in trabajo.capacidades:
            assert capacidad in texto


def test_ofrece_la_descarga_del_cv(client: FlaskClient, contenido_valido: Contenido) -> None:
    doc = verificar_invariantes(client.get("/"))
    enlace = doc.select_one('a[href*="cv"]')
    assert isinstance(enlace, Tag), "no hay enlace de descarga del CV (FR-004)"
    assert str(enlace["href"]).endswith(contenido_valido.perfil.cv)


def test_incluye_los_enlaces_a_perfiles_externos(
    client: FlaskClient, contenido_valido: Contenido
) -> None:
    cuerpo = client.get("/").get_data(as_text=True)
    for enlace in contenido_valido.perfil.enlaces:
        assert enlace.url in cuerpo
        assert enlace.etiqueta in cuerpo


def test_estado_vacio_por_seccion(client_vacio: FlaskClient) -> None:
    """FR-010: una sección sin contenido se explica, no desaparece."""
    respuesta = client_vacio.get("/")
    assert respuesta.status_code == 200
    doc = verificar_invariantes(respuesta)
    vacios = doc.select(".estado-vacio")
    assert len(vacios) >= 3, "faltan estados vacíos para capacidades, experiencia y trabajos"


def test_estado_vacio_conserva_la_identidad(
    client_vacio: FlaskClient, contenido_vacio: Contenido
) -> None:
    cuerpo = client_vacio.get("/").get_data(as_text=True)
    assert contenido_vacio.perfil.nombre in cuerpo


def test_metodo_no_admitido(client: FlaskClient) -> None:
    assert client.post("/").status_code == 405
