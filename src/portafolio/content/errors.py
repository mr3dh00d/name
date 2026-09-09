"""Errores de validacion de contenido.

FR-012 exige que la publicacion se detenga **identificando la entrada y el campo
defectuoso**. Por eso ``archivo``, ``entrada``, ``campo``, ``motivo`` y
``valor_recibido`` son atributos del contrato, no partes de un mensaje de texto:
estan probados y ``scripts/build.py`` los usa para informar al propietario.
"""

from __future__ import annotations


class ContentValidationError(Exception):
    """Un archivo de contenido incumple el contrato de ``contracts/content-schema.md``.

    Attributes:
        archivo: Ruta del archivo de contenido, relativa a la raiz del repositorio.
        entrada: Identificador de la entrada defectuosa dentro del archivo.
        campo: Nombre del campo que incumple la validacion.
        motivo: Explicacion legible de por que el valor no es valido.
        valor_recibido: Valor que se leyo, o ``None`` si el campo estaba ausente.
    """

    def __init__(
        self,
        archivo: str,
        entrada: str,
        campo: str,
        motivo: str,
        valor_recibido: object = None,
    ) -> None:
        """Construye el error con los cinco datos que exige FR-012."""
        self.archivo = archivo
        self.entrada = entrada
        self.campo = campo
        self.motivo = motivo
        self.valor_recibido = valor_recibido
        super().__init__(self._mensaje())

    def _mensaje(self) -> str:
        partes = [f"{self.archivo}: entrada '{self.entrada}', campo '{self.campo}': {self.motivo}"]
        if self.valor_recibido is not None:
            partes.append(f"  valor recibido: {self.valor_recibido!r}")
        return "\n".join(partes)
