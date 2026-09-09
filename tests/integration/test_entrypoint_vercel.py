"""El contrato del punto de entrada que resuelve Vercel.

Existe por un fallo real: el primer despliegue de producción murió con

    Error: "tool.vercel.entrypoint" in "pyproject.toml" is "portafolio.wsgi:app"
    but no matching module file was found.

Vercel traduce el módulo del entrypoint a una **ruta de archivo relativa a la
raíz del repositorio**, y con la distribución ``src/`` esa traducción no
encontraba nada. Estas pruebas convierten ese conocimiento en una puerta de CI:
si alguien mueve o renombra el entrypoint, falla aquí y no en producción.

Referencia: `specs/001-portafolio-personal/research.md`, R-001.
"""

from __future__ import annotations

import importlib.util
import json
import tomllib
from pathlib import Path

import pytest
from flask import Flask

RAIZ = Path(__file__).resolve().parent.parent.parent

# Rutas donde Vercel busca un entrypoint por si solo, segun su documentacion.
NOMBRES_DETECTADOS = ("app.py", "index.py", "server.py", "main.py", "wsgi.py", "asgi.py")
DIRECTORIOS_DETECTADOS = ("", "src", "app")


def entrypoints_detectables() -> list[Path]:
    """Archivos del repositorio que Vercel encontraria por deteccion automatica."""
    return [
        RAIZ / directorio / nombre
        for directorio in DIRECTORIOS_DETECTADOS
        for nombre in NOMBRES_DETECTADOS
        if (RAIZ / directorio / nombre).is_file()
    ]


def test_existe_un_entrypoint_en_una_ruta_que_vercel_detecta() -> None:
    encontrados = entrypoints_detectables()
    assert encontrados, (
        "Vercel no encontrara la aplicacion. Necesita un archivo llamado "
        f"{' o '.join(NOMBRES_DETECTADOS)} en la raiz, en src/ o en app/"
    )


def test_el_entrypoint_expone_una_instancia_de_flask() -> None:
    """Vercel toma una variable de nivel superior llamada exactamente ``app``."""
    for ruta in entrypoints_detectables():
        spec = importlib.util.spec_from_file_location(f"_entrypoint_{ruta.stem}", ruta)
        assert spec is not None and spec.loader is not None
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)

        app = getattr(modulo, "app", None)
        assert isinstance(app, Flask), f"{ruta} no expone una instancia de Flask llamada 'app'"


def test_el_entrypoint_sirve_las_rutas_publicas() -> None:
    """No basta con que importe: debe ser la aplicacion completa."""
    ruta = RAIZ / "src" / "wsgi.py"
    spec = importlib.util.spec_from_file_location("_entrypoint_verificacion", ruta)
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    reglas = {r.rule for r in modulo.app.url_map.iter_rules()}
    for esperada in ("/", "/trabajos", "/trabajos/<slug>", "/sitemap.xml", "/robots.txt"):
        assert esperada in reglas, f"el entrypoint no sirve {esperada}"


def test_si_se_declara_un_entrypoint_explicito_su_archivo_debe_existir() -> None:
    """La causa exacta del despliegue fallido.

    Vercel convierte ``paquete.modulo:objeto`` en ``paquete/modulo.py`` relativo
    a la raiz del repositorio. Declarar un modulo que solo es importable, pero
    cuyo archivo no esta en esa ruta, rompe el build.
    """
    config = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    entrypoint = config.get("tool", {}).get("vercel", {}).get("entrypoint")
    if entrypoint is None:
        pytest.skip("no hay entrypoint explicito: se usa la deteccion automatica")

    modulo = entrypoint.split(":")[0]
    archivo = RAIZ / Path(*modulo.split("."))
    assert archivo.with_suffix(".py").is_file() or (archivo / "__init__.py").is_file(), (
        f"'{entrypoint}' se traduce a '{archivo.with_suffix('.py')}', que no existe. "
        "Vercel resuelve el entrypoint por ruta de archivo, no por importabilidad"
    )


def test_la_clave_de_functions_apunta_al_entrypoint_real() -> None:
    """`vercel.json` configura la funcion por su archivo de entrypoint resuelto."""
    funciones = json.loads((RAIZ / "vercel.json").read_text(encoding="utf-8"))["functions"]
    for clave in funciones:
        assert (RAIZ / clave).is_file(), (
            f"vercel.json configura '{clave}', que no existe. La clave de "
            "'functions' debe ser el archivo de entrypoint resuelto"
        )
