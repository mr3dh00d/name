"""Punto de entrada que resuelve Vercel.

Vercel localiza la aplicación buscando un **archivo** en una de sus rutas
conocidas — ``app.py``, ``index.py``, ``server.py``, ``main.py``, ``wsgi.py`` o
``asgi.py``, en la raíz o dentro de ``src/`` — y toma de él una variable de nivel
superior llamada ``app``.

Por eso este archivo existe. El primer despliegue declaraba
``tool.vercel.entrypoint = "portafolio.wsgi:app"``, que Vercel traduce a la ruta
``portafolio/wsgi.py`` **relativa a la raíz del repositorio**. Con la
distribución ``src/`` que exige la constitución, ese archivo está en
``src/portafolio/wsgi.py``, así que la comprobación fallaba antes incluso de
intentar importar nada:

    Error: "tool.vercel.entrypoint" in "pyproject.toml" is "portafolio.wsgi:app"
    but no matching module file was found.

``src/wsgi.py`` sí es una de las rutas que Vercel reconoce por sí solo, de modo
que la detección automática lo encuentra sin configuración.

La aplicación real se construye en :mod:`portafolio.wsgi`, que sigue siendo el
objetivo de ``flask --app portafolio.wsgi run`` en desarrollo. Aquí solo se
reexporta, para que local y producción compartan un único objeto.
"""

from __future__ import annotations

import sys
from pathlib import Path

# El paquete se importa desde `src/`. Que ese directorio esté en la ruta de
# busqueda depende de si el proyecto quedó instalado durante el build, y no
# conviene que el despliegue dependa de ese detalle: la comprobación es de un
# solo uso y elimina toda una clase de fallo de arranque.
_SRC = str(Path(__file__).resolve().parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from portafolio.wsgi import app  # noqa: E402  (debe ir tras ajustar sys.path)

__all__ = ["app"]
