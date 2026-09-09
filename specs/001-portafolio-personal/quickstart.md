# Phase 1 — Quickstart y validación: Portafolio Personal

**Fecha**: 2026-09-02 · **Plan**: [plan.md](./plan.md) · **Contratos**: [contracts/](./contracts/)

Guía para levantar el proyecto y comprobar, extremo a extremo, que cumple lo que promete la
especificación. No contiene código de implementación: eso corresponde a `/speckit-tasks` y a la fase
de implementación.

> **Estado**: el repositorio aún no contiene código. Estos comandos describen el resultado esperado
> una vez ejecutada la implementación, y sirven de criterio de aceptación para ella.

---

## Prerrequisitos

| Requisito | Versión | Comprobación |
|-----------|---------|--------------|
| Python | 3.13 | `python --version` |
| uv | reciente | `uv --version` |
| Vercel CLI | ≥ 48.2.10 (necesaria para `vercel dev` con Flask) | `vercel --version` |
| Navegadores de Playwright | — | `uv run playwright install chromium` |

El aviso de arranque de esta sesión indica que la CLI de Vercel instalada está desactualizada.
Actualízala antes del primer despliegue: `npm i -g vercel@latest`.

**Contenido**: la implementación puede arrancar con contenido de marcador de posición en `content/`.
Para publicar en producción hacen falta los datos reales del propietario, que a fecha de este
documento no se han facilitado.

---

## Puesta en marcha

```bash
uv sync                       # instala dependencias desde uv.lock
uv run pre-commit install     # engancha las mismas puertas que ejecuta CI
```

---

## Ejecución local

```bash
uv run flask --app portafolio.wsgi run --debug   # servidor de desarrollo de Flask
```

Para reproducir el entorno de la plataforma, incluidos el servicio de `public/` desde la CDN
simulada y el enrutado real:

```bash
vercel dev
```

**Diferencia que importa**: con `flask run`, `public/` **no** se sirve — la hoja de estilos y las
imágenes darán 404. Es correcto y esperado: en producción esos archivos los sirve la CDN, no Flask
(ver `contracts/routes.md`, sección de activos). Usa `vercel dev` para ver el sitio completo.

---

## Puertas de calidad

Los mismos comandos que ejecuta la integración continua, en el mismo orden bloqueante que fija la
constitución:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy --strict src tests
uv run pytest --cov=src/portafolio --cov-branch --cov-fail-under=90
```

Un fallo en cualquiera de ellos detiene la publicación. No se rodean con `--no-verify`.

---

## Validación del contenido

```bash
uv run python scripts/build.py
```

Es el mismo comando que Vercel ejecuta durante el build. Carga y valida todo `content/` y termina con
código distinto de cero ante el primer error, indicando archivo, entrada y campo (FR-012).

**Escenario de validación** — comprobar que el fallo es ruidoso:

1. Elimina el campo `titulo` de cualquier archivo de `content/trabajos/`.
2. Ejecuta `uv run python scripts/build.py`.
3. **Esperado**: salida distinta de cero, con el nombre del archivo, la entrada y el campo `titulo`
   señalados. Si el comando pasa, FR-012 no se cumple.

---

## Escenarios de aceptación end-to-end

Cada bloque corresponde a una historia de la especificación. Todos deben pasar antes de considerar
completa la funcionalidad.

### P1 — Evaluación rápida del perfil

```bash
uv run pytest tests/contract/test_home.py tests/e2e/test_p1_perfil.py -v
```

| Comprobación | Criterio de éxito |
|--------------|-------------------|
| Identidad en la primera pantalla | Nombre, titular y resumen visibles sin desplazarse a 1280×800 y a 375×667 |
| Trabajos destacados | Al menos 3 visibles cuando el contenido los tiene, con título, resumen y capacidades |
| Descarga del CV | El enlace responde `200` y entrega el documento en menos de 3 s |
| Perfiles externos | Presentes y con `rel="noopener noreferrer"` |
| Lector de pantalla | Un solo `<h1>`, jerarquía sin saltos, toda imagen con alternativa textual |
| Sin scripting | Con JavaScript deshabilitado en el navegador, todo el contenido sigue legible y los enlaces funcionan |

### P2 — Ficha de trabajo

```bash
uv run pytest tests/contract/test_projects.py tests/e2e/test_p2_trabajo.py -v
```

| Comprobación | Criterio de éxito |
|--------------|-------------------|
| Navegación | Desde un destacado se llega a `/trabajos/<slug>` con su contenido completo |
| Enlace directo | La ficha carga en una sesión nueva, sin pasar por la página principal |
| Vuelta | Existe enlace a `/trabajos` |
| Slug inexistente | `404` con la página de error, sin traza técnica |
| Metadatos sociales | `og:title` es el del trabajo, `og:url` es la dirección canónica de la ficha |

### P3 — Actualización de contenido

```bash
uv run pytest tests/integration/test_content_reload.py -v
```

**Escenario manual, que es el que de verdad prueba la promesa de la historia**:

1. Copia un archivo existente de `content/trabajos/` a `content/trabajos/prueba-p3.toml`.
2. Cambia `slug` a `prueba-p3` y el `titulo`.
3. Reinicia el servidor de desarrollo.
4. **Esperado**: el trabajo aparece en `/trabajos` y su ficha responde en `/trabajos/prueba-p3`.
5. **Criterio de éxito de la historia**: no se ha modificado **ningún** archivo de `src/`. Verifícalo
   con `git status`.
6. Borra el archivo de prueba.

---

## Verificación de los presupuestos de rendimiento

```bash
uv run pytest tests/perf/ --benchmark-only
```

| Presupuesto | Umbral | Fuente |
|-------------|--------|--------|
| Renderizado por página | < 20 ms | `pytest-benchmark` |
| Arranque de la aplicación | < 1 s | `pytest-benchmark` sobre `create_app()` |
| Suite completa | < 60 s | Duración informada por pytest |

Sobre el despliegue de vista previa, y no en local, porque LCP y peso solo son medibles con la CDN
delante:

```bash
vercel deploy                                  # despliegue de vista previa
npx lighthouse <url-de-vista-previa> --preset=desktop --view
npx lighthouse <url-de-vista-previa> --form-factor=mobile --view
```

| Presupuesto | Umbral | Requisito |
|-------------|--------|-----------|
| LCP | < 2,5 s en móvil simulado | SC-002 |
| CLS | < 0,1 | Principio IV |
| INP | < 200 ms | Principio IV |
| Peso de la página inicial | ≤ 300 KB comprimidos | Principio IV |
| Accesibilidad y buenas prácticas | ≥ 95 / 100, sin infracciones AA | SC-003 |

---

## Despliegue

```bash
vercel deploy            # vista previa
vercel deploy --prod     # producción
```

### Comprobaciones de humo tras el primer despliegue

Estas tres no son opcionales: cubren los riesgos registrados en el plan.

1. **Resolución del punto de entrada**. La aplicación responde y no hay error de importación en los
   registros. Si falla, la alternativa documentada es un `src/wsgi.py` con `app` de nivel superior
   (ver `research.md`, R-001).
2. **Acierto de caché de CDN**. Pide dos veces la misma página y comprueba que la segunda responde con
   acierto de caché en la cabecera correspondiente. Es el mecanismo del que depende el p95 del
   Principio IV, así que un fallo aquí es un fallo de presupuesto, no un detalle.
3. **Activos desde `public/`**. La hoja de estilos, el retrato y el CV responden `200` en el
   despliegue, no solo en `vercel dev`.

Después, registra el p95 y el p99 reales desde las métricas de la plataforma. **Si el p99 supera 500 ms
de forma sostenida**, se activa la salida documentada en `research.md` R-001 alternativa B:
pre-renderizado en tiempo de build. Las vistas, las plantillas y el modelo de contenido no cambian;
solo el modo de publicación.
