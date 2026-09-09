"""Carga y validacion del contenido del portafolio.

Lee los archivos TOML de ``content/``, los valida contra los modelos y comprueba
los invariantes del agregado. Se ejecuta **una sola vez al arrancar** la aplicacion
y de nuevo en el build de Vercel: el Principio IV prohibe la E/S bloqueante en la
ruta de peticion, y FR-012 exige que un contenido invalido detenga la publicacion.

Todo fallo se traduce a :class:`ContentValidationError`, que nombra archivo,
entrada y campo.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails

from portafolio.content.errors import ContentValidationError
from portafolio.content.models import (
    Capacidad,
    Contenido,
    Experiencia,
    Perfil,
    Trabajo,
)

# El TOML es una frontera sin tipos: los valores llegan como `object` y solo son
# seguros despues de que Pydantic los valide. Usar `object` en lugar de `Any`
# obliga a esa validacion en lugar de confiar en ella.
type DatosCrudos = dict[str, object]

ARCHIVO_PERFIL = "perfil.toml"
ARCHIVO_CAPACIDADES = "capacidades.toml"
ARCHIVO_EXPERIENCIA = "experiencia.toml"
DIRECTORIO_TRABAJOS = "trabajos"


def _leer_toml(ruta: Path, entrada: str) -> DatosCrudos:
    """Lee un archivo TOML y traduce cualquier fallo a un error de contenido."""
    try:
        with ruta.open("rb") as f:
            return tomllib.load(f)
    except FileNotFoundError as exc:
        raise ContentValidationError(
            archivo=str(ruta),
            entrada=entrada,
            campo="(archivo)",
            motivo="el archivo no existe",
        ) from exc
    except tomllib.TOMLDecodeError as exc:
        raise ContentValidationError(
            archivo=str(ruta),
            entrada=entrada,
            campo="(sintaxis)",
            motivo=f"TOML mal formado: {exc}",
        ) from exc


CAMPO_ENTRECOMILLADO = re.compile(r"'([a-z_]+)'")


def _detalle_mas_util(exc: ValidationError) -> ErrorDetails:
    """Elige el fallo que mejor explica la causa.

    Un campo desconocido casi siempre viene acompañado de un "falta el campo X":
    son el mismo error visto por sus dos caras, y el nombre mal escrito es el que
    permite corregirlo. Por eso se prioriza, tal y como promete
    ``contracts/content-schema.md`` al hablar de erratas silenciosas.
    """
    errores = exc.errors()
    extra = next((e for e in errores if e["type"] == "extra_forbidden"), None)
    return extra or errores[0]


def _primer_error(exc: ValidationError) -> tuple[str, str, object]:
    """Extrae campo, motivo y valor del fallo más informativo."""
    detalle = _detalle_mas_util(exc)
    campo = ".".join(str(p) for p in detalle["loc"])
    mensaje = detalle["msg"]
    if not campo:
        # Los validadores de modelo no tienen `loc`, pero sus mensajes nombran el
        # campo entre comillas simples. FR-012 exige identificarlo.
        encontrado = CAMPO_ENTRECOMILLADO.search(mensaje)
        campo = encontrado.group(1) if encontrado else "(raíz)"
    return campo, mensaje, detalle.get("input")


def _construir[M: BaseModel](modelo: type[M], datos: DatosCrudos, archivo: Path, entrada: str) -> M:
    """Construye un modelo, traduciendo el fallo de validacion a un error de contenido."""
    try:
        return modelo.model_validate(datos)
    except ValidationError as exc:
        campo, motivo, valor = _primer_error(exc)
        raise ContentValidationError(
            archivo=str(archivo),
            entrada=entrada,
            campo=campo,
            motivo=motivo,
            valor_recibido=valor,
        ) from exc


def _cargar_perfil(raiz: Path) -> Perfil:
    archivo = raiz / ARCHIVO_PERFIL
    return _construir(Perfil, _leer_toml(archivo, "perfil"), archivo, "perfil")


def _cargar_lista[M: BaseModel](
    raiz: Path, nombre: str, modelo: type[M], etiqueta: str
) -> tuple[M, ...]:
    """Carga un archivo con una lista de tablas ``[[item]]``."""
    archivo = raiz / nombre
    if not archivo.exists():
        return ()
    datos = _leer_toml(archivo, etiqueta)
    items = _lista_de_tablas(datos)
    return tuple(
        _construir(modelo, item, archivo, f"{etiqueta}[{i}]") for i, item in enumerate(items)
    )


def _lista_de_tablas(datos: DatosCrudos) -> list[DatosCrudos]:
    """Extrae la lista de tablas ``[[item]]``, o una lista vacia si no hay ninguna."""
    items = datos.get("item", [])
    if not isinstance(items, list):
        return []
    return [i for i in items if isinstance(i, dict)]


def _cargar_trabajos(raiz: Path) -> tuple[Trabajo, ...]:
    """Carga un trabajo por archivo, exigiendo que el slug coincida con el nombre."""
    directorio = raiz / DIRECTORIO_TRABAJOS
    if not directorio.is_dir():
        return ()
    trabajos: list[Trabajo] = []
    for archivo in sorted(directorio.glob("*.toml")):
        esperado = archivo.stem
        trabajo = _construir(Trabajo, _leer_toml(archivo, esperado), archivo, esperado)
        if trabajo.slug != esperado:
            raise ContentValidationError(
                archivo=str(archivo),
                entrada=esperado,
                campo="slug",
                motivo=(
                    f"el slug debe coincidir con el nombre del archivo ('{esperado}'). "
                    "La direccion publica se deriva del nombre del archivo"
                ),
                valor_recibido=trabajo.slug,
            )
        trabajos.append(trabajo)
    return tuple(trabajos)


def ordenar_trabajos(trabajos: tuple[Trabajo, ...]) -> tuple[Trabajo, ...]:
    """Ordena por ``orden`` ascendente y, a igualdad, por titulo."""
    return tuple(sorted(trabajos, key=lambda t: (t.orden, t.titulo)))


def ordenar_experiencia(items: tuple[Experiencia, ...]) -> tuple[Experiencia, ...]:
    """Ordena cronologicamente al reves, con los periodos actuales en cabeza."""
    return tuple(sorted(items, key=lambda e: (e.actual, e.fecha_inicio), reverse=True))


def _validar_slugs_unicos(contenido: Contenido, raiz: Path) -> None:
    """INV-01."""
    vistos: set[str] = set()
    for trabajo in contenido.trabajos:
        if trabajo.slug in vistos:
            raise ContentValidationError(
                archivo=str(raiz / DIRECTORIO_TRABAJOS / f"{trabajo.slug}.toml"),
                entrada=trabajo.slug,
                campo="slug",
                motivo=f"el slug '{trabajo.slug}' esta repetido en mas de un trabajo",
                valor_recibido=trabajo.slug,
            )
        vistos.add(trabajo.slug)


def _validar_capacidades_referidas(contenido: Contenido, raiz: Path) -> None:
    """INV-02."""
    declaradas = {c.nombre for c in contenido.capacidades}
    for trabajo in contenido.trabajos:
        colgantes = [c for c in trabajo.capacidades if c not in declaradas]
        if colgantes:
            raise ContentValidationError(
                archivo=str(raiz / DIRECTORIO_TRABAJOS / f"{trabajo.slug}.toml"),
                entrada=trabajo.slug,
                campo="capacidades",
                motivo=(
                    f"no existen en capacidades.toml: {', '.join(colgantes)}. "
                    "Anadelas alli o corrige el nombre"
                ),
                valor_recibido=list(trabajo.capacidades),
            )


def _validar_experiencias_actuales(contenido: Contenido, raiz: Path) -> None:
    """INV-03: varias experiencias actuales solo se admiten si no se solapan."""
    actuales = [e for e in contenido.experiencia if e.actual]
    if len(actuales) <= 1:
        return
    raise ContentValidationError(
        archivo=str(raiz / ARCHIVO_EXPERIENCIA),
        entrada=", ".join(e.organizacion for e in actuales),
        campo="actual",
        motivo=(
            f"hay {len(actuales)} experiencias marcadas como actuales y sus periodos se "
            "solapan. Cierra las anteriores con 'fecha_fin'"
        ),
    )


def _rutas_referenciadas(contenido: Contenido) -> list[tuple[str, str, str]]:
    """Devuelve las ternas (entrada, campo, ruta) de todo activo referenciado."""
    perfil = contenido.perfil
    rutas: list[tuple[str, str, str]] = [("perfil", "cv", perfil.cv)]
    if perfil.retrato:
        rutas.append(("perfil", "retrato", perfil.retrato))
    if perfil.og_imagen:
        rutas.append(("perfil", "og_imagen", perfil.og_imagen))
    for trabajo in contenido.trabajos:
        if trabajo.og_imagen:
            rutas.append((trabajo.slug, "og_imagen", trabajo.og_imagen))
        rutas.extend((trabajo.slug, "imagenes.ruta", img.ruta) for img in trabajo.imagenes)
    return rutas


def _validar_activos(contenido: Contenido, raiz: Path, publico: Path) -> None:
    """INV-04: toda ruta referenciada existe bajo ``public/``."""
    for entrada, campo, ruta in _rutas_referenciadas(contenido):
        if not (publico / ruta).is_file():
            raise ContentValidationError(
                archivo=str(raiz / ARCHIVO_PERFIL if entrada == "perfil" else raiz),
                entrada=entrada,
                campo=campo,
                motivo=f"el archivo '{publico / ruta}' no existe bajo public/",
                valor_recibido=ruta,
            )


def validar_invariantes(contenido: Contenido, raiz: Path, publico: Path) -> None:
    """Comprueba los cuatro invariantes del agregado descritos en data-model.md."""
    _validar_slugs_unicos(contenido, raiz)
    _validar_capacidades_referidas(contenido, raiz)
    _validar_experiencias_actuales(contenido, raiz)
    _validar_activos(contenido, raiz, publico)


def cargar_contenido(raiz: Path, publico: Path) -> Contenido:
    """Carga, valida y ordena todo el contenido del portafolio.

    Args:
        raiz: Directorio que contiene ``perfil.toml`` y el resto del contenido.
        publico: Directorio de activos, para comprobar las rutas referenciadas.

    Returns:
        El agregado inmutable que consultan las vistas.

    Raises:
        ContentValidationError: Si cualquier archivo o invariante incumple el
            contrato. El error nombra archivo, entrada y campo (FR-012).
    """
    contenido = Contenido(
        perfil=_cargar_perfil(raiz),
        capacidades=_cargar_lista(raiz, ARCHIVO_CAPACIDADES, Capacidad, "capacidades"),
        experiencia=ordenar_experiencia(
            _cargar_lista(raiz, ARCHIVO_EXPERIENCIA, Experiencia, "experiencia")
        ),
        trabajos=ordenar_trabajos(_cargar_trabajos(raiz)),
    )
    validar_invariantes(contenido, raiz, publico)
    return contenido
