"""Resolución de la raíz del proyecto.

Existe por un fallo real de despliegue. `config.py` derivaba la raíz de
`Path(__file__).parent.parent.parent`, lo que asume que el paquete vive dentro
del árbol del repositorio. En Vercel el paquete se instala en `site-packages`,
así que esa cuenta apuntaba al interior del entorno virtual:

    archivo : /vercel/path0/.vercel/python/.venv/lib/python3.13/content/perfil.toml
    motivo  : el archivo no existe

La plataforma ejecuta el build y la función con el directorio de trabajo en la
raíz del proyecto, que es el contrato del que hay que depender.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from portafolio.config import cargar_config, raiz_del_proyecto


def test_usa_el_directorio_de_trabajo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "content").mkdir()
    monkeypatch.chdir(tmp_path)
    assert raiz_del_proyecto() == tmp_path


def test_no_deriva_la_raiz_de_la_ubicacion_del_paquete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """La regresión exacta del despliegue fallido.

    Con el paquete instalado fuera del repositorio, la raíz no puede salir de
    `__file__`: la respuesta correcta está en el directorio de trabajo.
    """
    (tmp_path / "content").mkdir()
    monkeypatch.chdir(tmp_path)

    desde_el_paquete = Path(cargar_config.__module__ and __file__).resolve()
    assert raiz_del_proyecto() not in desde_el_paquete.parents


def test_recurre_al_arbol_de_fuentes_si_el_cwd_no_sirve(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ejecutar desde un subdirectorio de un checkout debe seguir funcionando."""
    vacio = tmp_path / "sin_contenido"
    vacio.mkdir()
    monkeypatch.chdir(vacio)
    assert (raiz_del_proyecto() / "content").is_dir()


def test_las_variables_de_entorno_mandan(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DIR_CONTENIDO", str(tmp_path / "otro"))
    monkeypatch.setenv("DIR_PUBLICO", str(tmp_path / "activos"))
    config = cargar_config()
    assert config.directorio_contenido == tmp_path / "otro"
    assert config.directorio_publico == tmp_path / "activos"


def test_la_url_del_sitio_prefiere_la_explicita(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("URL_SITIO", "https://ejemplo.test")
    assert cargar_config().url_base == "https://ejemplo.test"


def test_la_url_del_sitio_usa_el_dominio_de_vercel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("URL_SITIO", raising=False)
    monkeypatch.setenv("VERCEL_PROJECT_PRODUCTION_URL", "portafolio.vercel.app")
    assert cargar_config().url_base == "https://portafolio.vercel.app"


def test_la_url_base_no_lleva_barra_final(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("URL_SITIO", "https://ejemplo.test/")
    assert cargar_config().url_base == "https://ejemplo.test"


def test_sin_entorno_cae_en_localhost(monkeypatch: pytest.MonkeyPatch) -> None:
    for clave in ("URL_SITIO", "VERCEL_PROJECT_PRODUCTION_URL", "VERCEL_URL"):
        monkeypatch.delenv(clave, raising=False)
    assert cargar_config().url_base.startswith("http://localhost")


def test_el_entorno_de_prueba_no_deja_residuos() -> None:
    assert "DIR_CONTENIDO" not in os.environ or Path(os.environ["DIR_CONTENIDO"]).exists()
