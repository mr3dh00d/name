# Portafolio personal

Portafolio profesional en **Python y Flask**, desplegable en **Vercel**.
Construido con Spec Kit: cada decisión está escrita antes que el código, en
[`specs/001-portafolio-personal/`](specs/001-portafolio-personal/).

## Qué lo caracteriza

- **Solo lectura de principio a fin.** Sin formularios, sin cuentas, sin cookies,
  sin rastreadores. El sitio no recibe ni un solo dato del visitante.
- **El contenido son datos.** Vive en TOML validado por esquema, separado de la
  presentación. Publicar no exige tocar código, y hay una prueba que lo verifica.
- **Presupuestos de rendimiento con números.** p95 < 200 ms, LCP < 2,5 s, página
  inicial ≤ 300 KB, arranque < 1 s, suite < 60 s. Medidos, no prometidos.
- **Cero JavaScript.** Tipografías del sistema, tema claro y oscuro por
  preferencia del sistema. El presupuesto de peso se cumple por construcción.
- **Accesibilidad AA verificada** con axe-core en un navegador real, no por
  inspección visual.

## Puesta en marcha

```bash
uv sync --all-extras
uv run pre-commit install
uv run playwright install chromium   # solo para las pruebas extremo a extremo
```

## Desarrollo

```bash
uv run flask --app portafolio.wsgi run --debug   # servidor de Flask
vercel dev                                        # entorno de la plataforma
```

Con `flask run`, `public/` **no** se sirve: la hoja de estilos y las imágenes
darán 404. Es correcto — en producción esos archivos los sirve la CDN, no Flask.
Usa `vercel dev` para ver el sitio completo.

## Puertas de calidad

Los mismos comandos que ejecuta CI, en el mismo orden bloqueante:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest -m "not e2e" --cov --cov-fail-under=90
uv run python scripts/build.py
uv run pytest -m e2e
```

Un fallo en cualquiera detiene la publicación. No se rodean con `--no-verify`.

## Estructura

```text
src/portafolio/     Aplicación: modelos, cargador, vistas, plantillas
content/            Contenido editable en TOML  → ver content/README.md
public/             Activos servidos por la CDN, nunca por Flask
scripts/build.py    Validación que rompe el build si el contenido es inválido
tests/              unit · integration · contract · e2e · perf
specs/              Especificación, plan, contratos y tareas
```

## Despliegue

```bash
vercel deploy          # vista previa
vercel deploy --prod   # producción
```

Vercel detecta la aplicación por `tool.vercel.entrypoint` en `pyproject.toml` y
la ejecuta como una Vercel Function sobre Fluid Compute. La validación de
contenido corre en el build: un TOML roto no llega a producción.

Guía completa de validación y comprobaciones de humo:
[`specs/001-portafolio-personal/quickstart.md`](specs/001-portafolio-personal/quickstart.md).

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [Constitución](.specify/memory/constitution.md) | Los cinco principios que gobiernan este código |
| [Especificación](specs/001-portafolio-personal/spec.md) | Qué hace el portafolio y por qué |
| [Plan](specs/001-portafolio-personal/plan.md) | Decisiones técnicas y riesgos |
| [Investigación](specs/001-portafolio-personal/research.md) | Alternativas evaluadas y descartadas |
| [Contenido](content/README.md) | Cómo publicar sin tocar código |
