"""Punto de entrada WSGI.

Vercel resuelve este módulo a través de ``tool.vercel.entrypoint`` en
``pyproject.toml`` y busca una instancia de Flask llamada ``app``. Es también el
objetivo de ``flask --app portafolio.wsgi run`` en desarrollo, de modo que local
y producción ejecutan exactamente el mismo código.
"""

from __future__ import annotations

from portafolio import create_app

app = create_app()
