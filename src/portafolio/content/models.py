"""Modelos de contenido del portafolio.

Cada modelo corresponde a una entidad de ``specs/001-portafolio-personal/data-model.md``
y es inmutable: el contenido es de solo lectura en ejecucion y solo cambia con un
despliegue nuevo.

Todos prohiben campos desconocidos. Es deliberado: una errata como ``titluo`` debe
ser un error ruidoso y no un campo que se ignora en silencio, tal y como promete
``contracts/content-schema.md``.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PATRON_SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _hoy() -> date:
    """Fecha actual en UTC, para que la validacion no dependa de la zona del proceso."""
    return datetime.now(UTC).date()


# Textos de enlace que no se entienden fuera de su contexto. Regla de
# accesibilidad (FR-014): un lector de pantalla puede listar los enlaces de la
# pagina aislados de su parrafo.
ETIQUETAS_NO_DESCRIPTIVAS = frozenset(
    {"aqui", "aca", "enlace", "link", "click", "clic", "clic aqui", "click here", "ver", "mas"}
)

Nivel = Literal["basico", "intermedio", "avanzado", "experto"]
TipoEnlace = Literal["linkedin", "github", "web", "otro"]

TextoCorto = Annotated[str, Field(min_length=1, max_length=120)]
RutaPublica = Annotated[str, Field(min_length=1, max_length=300)]


def _sin_acentos(texto: str) -> str:
    """Normaliza vocales acentuadas para comparar etiquetas de enlace."""
    tabla = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")
    return texto.translate(tabla)


class ModeloContenido(BaseModel):
    """Base comun: inmutable, sin campos desconocidos y con cadenas recortadas."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class EnlaceExterno(ModeloContenido):
    """Enlace a un recurso externo: un perfil profesional, un repositorio o una web."""

    etiqueta: Annotated[str, Field(min_length=2, max_length=40)]
    url: Annotated[str, Field(min_length=1, max_length=500)]
    tipo: TipoEnlace = "otro"

    @field_validator("url")
    @classmethod
    def _url_https(cls, valor: str) -> str:
        if not valor.startswith("https://"):
            msg = "la URL debe ser absoluta y empezar por 'https://'"
            raise ValueError(msg)
        return valor

    @field_validator("etiqueta")
    @classmethod
    def _etiqueta_descriptiva(cls, valor: str) -> str:
        normalizada = _sin_acentos(valor).lower().strip(" .!¡?¿")
        if normalizada in ETIQUETAS_NO_DESCRIPTIVAS:
            msg = (
                f"'{valor}' no describe su destino. El texto de un enlace debe entenderse "
                "aislado del texto que lo rodea (FR-014)"
            )
            raise ValueError(msg)
        return valor


class Imagen(ModeloContenido):
    """Imagen con alternativa textual y dimensiones conocidas.

    ``ancho`` y ``alto`` son obligatorios porque el presupuesto de CLS < 0,1 del
    Principio IV no se puede cumplir si el navegador desconoce la proporcion antes
    de descargar el archivo.
    """

    ruta: RutaPublica
    alt: Annotated[str, Field(min_length=5, max_length=200)]
    ancho: Annotated[int, Field(gt=0, le=10_000)]
    alto: Annotated[int, Field(gt=0, le=10_000)]


class Perfil(ModeloContenido):
    """Identidad profesional del propietario. Unica en el sistema."""

    nombre: Annotated[str, Field(min_length=2, max_length=80)]
    titular: Annotated[str, Field(min_length=2, max_length=120)]
    resumen: Annotated[str, Field(min_length=40, max_length=600)]
    ubicacion: TextoCorto | None = None
    disponibilidad: TextoCorto | None = None
    retrato: RutaPublica | None = None
    retrato_alt: Annotated[str, Field(min_length=5, max_length=160)] | None = None
    cv: RutaPublica
    enlaces: Annotated[tuple[EnlaceExterno, ...], Field(min_length=1, max_length=8)]
    og_imagen: RutaPublica | None = None

    @model_validator(mode="after")
    def _retrato_exige_alternativa(self) -> Self:
        if self.retrato and not self.retrato_alt:
            msg = "'retrato_alt' es obligatorio cuando hay 'retrato' (FR-014)"
            raise ValueError(msg)
        return self


class Capacidad(ModeloContenido):
    """Habilidad o tecnologia que el propietario declara dominar."""

    nombre: Annotated[str, Field(min_length=1, max_length=60)]
    categoria: Annotated[str, Field(min_length=2, max_length=60)]
    nivel: Nivel | None = None


class Experiencia(ModeloContenido):
    """Periodo de actividad profesional o formativa."""

    organizacion: Annotated[str, Field(min_length=2, max_length=120)]
    rol: Annotated[str, Field(min_length=2, max_length=120)]
    fecha_inicio: date
    fecha_fin: date | None = None
    actual: bool = False
    ubicacion: TextoCorto | None = None
    descripcion: Annotated[str, Field(min_length=20, max_length=1200)]
    logros: Annotated[
        tuple[Annotated[str, Field(min_length=10, max_length=400)], ...], Field(max_length=8)
    ] = ()

    @field_validator("fecha_inicio")
    @classmethod
    def _inicio_no_futuro(cls, valor: date) -> date:
        if valor > _hoy():
            msg = "'fecha_inicio' no puede estar en el futuro"
            raise ValueError(msg)
        return valor

    @model_validator(mode="after")
    def _coherencia_de_fechas(self) -> Self:
        if self.actual and self.fecha_fin is not None:
            msg = "'fecha_fin' no puede coexistir con 'actual = true'"
            raise ValueError(msg)
        if not self.actual and self.fecha_fin is None:
            msg = "'fecha_fin' es obligatoria salvo que 'actual' sea true"
            raise ValueError(msg)
        if self.fecha_fin is not None and self.fecha_fin < self.fecha_inicio:
            msg = "'fecha_fin' no puede ser anterior a 'fecha_inicio'"
            raise ValueError(msg)
        return self


class Trabajo(ModeloContenido):
    """Pieza de trabajo demostrable, con ficha propia y direccion estable."""

    slug: Annotated[str, Field(min_length=1, max_length=80)]
    titulo: Annotated[str, Field(min_length=2, max_length=100)]
    resumen: Annotated[str, Field(min_length=20, max_length=200)]
    problema: Annotated[str, Field(min_length=40, max_length=1200)]
    rol: Annotated[str, Field(min_length=2, max_length=120)]
    decisiones: Annotated[
        tuple[Annotated[str, Field(min_length=20, max_length=500)], ...],
        Field(min_length=1, max_length=10),
    ]
    resultado: Annotated[str, Field(min_length=20, max_length=800)]
    descripcion: Annotated[str, Field(max_length=4000)] | None = None
    capacidades: Annotated[tuple[str, ...], Field(min_length=1, max_length=12)]
    fecha_inicio: date
    fecha_fin: date | None = None
    destacado: bool = False
    orden: Annotated[int, Field(ge=0, le=10_000)] = 100
    imagenes: Annotated[tuple[Imagen, ...], Field(max_length=8)] = ()
    enlaces: Annotated[tuple[EnlaceExterno, ...], Field(max_length=6)] = ()
    og_imagen: RutaPublica | None = None

    @field_validator("slug")
    @classmethod
    def _slug_bien_formado(cls, valor: str) -> str:
        if not PATRON_SLUG.match(valor):
            msg = (
                f"'{valor}' no es un slug valido. Debe ser minusculas, digitos y guiones "
                "simples, por ejemplo 'mi-proyecto'"
            )
            raise ValueError(msg)
        return valor

    @model_validator(mode="after")
    def _coherencia_de_fechas(self) -> Self:
        if self.fecha_fin is not None and self.fecha_fin < self.fecha_inicio:
            msg = "'fecha_fin' no puede ser anterior a 'fecha_inicio'"
            raise ValueError(msg)
        return self

    @property
    def en_curso(self) -> bool:
        """Indica si el trabajo sigue activo, es decir, no tiene fecha de fin."""
        return self.fecha_fin is None


class Contenido(ModeloContenido):
    """Agregado raiz: todo el contenido del portafolio, ya validado y ordenado.

    Es lo unico que consultan las vistas. Se construye al arrancar la aplicacion y
    no vuelve a tocar el disco, como exige el Principio IV.
    """

    perfil: Perfil
    capacidades: tuple[Capacidad, ...] = ()
    experiencia: tuple[Experiencia, ...] = ()
    trabajos: tuple[Trabajo, ...] = ()

    @property
    def destacados(self) -> tuple[Trabajo, ...]:
        """Trabajos marcados como destacados, en el orden de presentacion."""
        return tuple(t for t in self.trabajos if t.destacado)

    def trabajo_por_slug(self, slug: str) -> Trabajo | None:
        """Busca un trabajo en memoria por su slug.

        La busqueda es contra la coleccion cargada, nunca contra el sistema de
        archivos, lo que hace estructuralmente imposible el recorrido de rutas.
        """
        return next((t for t in self.trabajos if t.slug == slug), None)

    def capacidades_por_categoria(self) -> dict[str, tuple[Capacidad, ...]]:
        """Agrupa las capacidades por categoria conservando el orden de aparicion."""
        grupos: dict[str, list[Capacidad]] = {}
        for capacidad in self.capacidades:
            grupos.setdefault(capacidad.categoria, []).append(capacidad)
        return {categoria: tuple(items) for categoria, items in grupos.items()}
