# Implementation Plan: Portafolio Personal

**Branch**: `001-portafolio-personal` | **Date**: 2026-09-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-portafolio-personal/spec.md`

## Summary

Portafolio profesional de solo lectura: perfil, capacidades, experiencia, trabajos con ficha
individual, descarga de CV y enlaces a perfiles externos. Sin contacto, sin artículos, monolingüe
en español (FR-006, FR-013).

**Enfoque técnico**: aplicación **Flask** desplegada en Vercel mediante su preset nativo de Python,
que la ejecuta como una única Vercel Function sobre Fluid Compute. El contenido vive en archivos
**TOML** bajo `content/`, se valida con **Pydantic** y se carga **una sola vez al arrancar** la
aplicación, de modo que la ruta de petición no hace ninguna E/S de disco. Todas las respuestas HTML
se emiten con cabeceras de caché de CDN de larga duración; como el contenido solo cambia al
desplegar, y cada despliegue invalida la caché, la práctica totalidad del tráfico real se sirve
desde el borde de la CDN y no llega a invocar la función. Los activos estáticos (CSS, imágenes, CV)
se sirven directamente desde `public/`, fuera de Flask. Cero JavaScript y tipografías del sistema:
el presupuesto de 300 KB y el LCP de 2,5 s se cumplen por construcción, no por optimización
posterior.

La validación del contenido se engancha al **build de Vercel** (`[tool.vercel.scripts] build`), de
forma que un TOML mal formado detiene la publicación señalando entrada y campo (FR-012).

## Technical Context

**Language/Version**: Python 3.13 (disponible en imagen de build y en runtime de Vercel; cumple el
mínimo de 3.12 de la constitución)

**Primary Dependencies**: Flask 3.x (mandato del propietario) · Jinja2 (incluido con Flask) ·
Pydantic 2.x (validación de contenido, FR-012) · `tomllib` de la biblioteca estándar (lectura de
contenido, sin dependencia externa). Sin framework CSS, sin JavaScript de cliente, sin tipografías
web.

**Storage**: archivos TOML versionados bajo `content/`, cargados en memoria al arrancar. Sin base de
datos: el sitio no acepta escrituras de ningún tipo (FR-006, FR-021).

**Testing**: pytest · pytest-cov (umbral 90%) · pytest-benchmark (Principio IV) · cliente de pruebas
de Flask (integración y contrato) · BeautifulSoup4 (aserciones estructurales sobre el HTML
renderizado) · Playwright para Python + axe-core (E2E, accesibilidad AA y operabilidad por teclado,
SC-003 y SC-004) · Lighthouse CI en integración continua (SC-002 y SC-003)

**Target Platform**: Vercel, preset nativo de Flask, Fluid Compute. Navegadores modernos de
escritorio y móvil; el contenido debe seguir siendo legible sin scripting (FR-017)

**Project Type**: aplicación web de servidor, un solo proyecto, sin frontend separado

**Performance Goals**: renderizado de plantilla < 20 ms por página en el proceso · página inicial
≤ 300 KB comprimidos · LCP < 2,5 s en móvil simulado · arranque de la aplicación < 1 s · suite de
pruebas completa < 60 s

**Constraints**: p95 < 200 ms y p99 < 500 ms (Principio IV) · sin E/S bloqueante en la ruta de
petición · sin seguimiento de terceros ni almacenamiento de datos del visitante (FR-021) ·
accesibilidad AA (FR-014) · operativo sin JavaScript (FR-017)

**Scale/Scope**: decenas de visitas diarias · < 100 entradas de contenido · 5 tipos de página
(inicio, índice de trabajos, ficha de trabajo, error, sitemap) · 4 entidades de contenido · 1 autor

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principio | Gate | Estado inicial | Estado post-diseño |
|---|-----------|------|----------------|--------------------|
| I | Test-First (NON-NEGOTIABLE) | Ninguna tarea de implementación precede a su prueba en rojo; los defectos llevan prueba de regresión | ✅ El desglose de `/speckit-tasks` ordenará prueba → implementación por cada unidad | ✅ Los contratos de `contracts/` están escritos para ser traducidos directamente a pruebas antes de existir código |
| II | Estándares de Testing Verificables | Cobertura ≥ 90% ramas y líneas; 3 niveles; determinismo; cero pruebas inestables; contrato por ruta pública | ✅ `--cov-fail-under=90` en configuración; `tests/{unit,integration,contract,e2e}` | ✅ 5 rutas públicas, todas con contrato definido en `contracts/routes.md`. Sin reloj, sin red, sin orden compartido: el contenido de prueba se inyecta por *fixture*, no se lee del `content/` real |
| III | Calidad de Código Aplicada por Herramientas | `ruff` + `ruff format` + `mypy --strict` en verde; tipos y docstrings públicos; complejidad ≤ 10; funciones ≤ 50 líneas; sin secretos | ✅ Herramientas fijadas en `pyproject.toml` y replicadas en `pre-commit` | ✅ Diseño sin funciones largas: vistas delgadas que solo seleccionan contenido ya cargado y eligen plantilla |
| IV | Rendimiento con Presupuestos Medibles | p95 < 200 ms · p99 < 500 ms · LCP < 2,5 s · ≤ 300 KB · arranque < 1 s · suite < 60 s · sin N+1 · sin E/S bloqueante en petición · optimizaciones con medición antes/después | ⚠️ Riesgo de arranque en frío frente a p99, ver *Riesgos* | ✅ Mitigado: contenido cargado una vez al arrancar (sin E/S por petición), respuestas cacheadas en CDN, activos fuera de la función, cero JS y tipografías del sistema |
| V | Simplicidad Explícita y Contenido como Datos | YAGNI; toda dependencia justificada frente a la biblioteca estándar; toda abstracción con ≥ 2 consumidores reales; contenido como datos validados por esquema, separado de la presentación | ✅ 2 dependencias de ejecución, ambas justificadas en *Complexity Tracking* | ✅ Contenido en TOML fuera del paquete, validado por esquema; las plantillas no contienen datos y los datos no contienen presentación |

**Veredicto**: el diseño pasa las cinco puertas. La única tensión real es el arranque en frío frente
al p99 del Principio IV; está registrada abajo como riesgo con umbral de decisión y salida
documentada, no como violación aceptada en silencio.

## Project Structure

### Documentation (this feature)

```text
specs/001-portafolio-personal/
├── plan.md              # Este archivo
├── research.md          # Fase 0 — decisiones técnicas y alternativas descartadas
├── data-model.md        # Fase 1 — entidades, campos, reglas de validación
├── quickstart.md        # Fase 1 — guía de arranque y validación end-to-end
├── contracts/
│   ├── routes.md        # Contrato de cada ruta pública
│   └── content-schema.md# Contrato del formato TOML que edita el propietario
├── checklists/
│   └── requirements.md  # Calidad de la especificación (16/16)
└── tasks.md             # Fase 2 — generado por /speckit-tasks, NO por este comando
```

### Source Code (repository root)

```text
src/portafolio/                 # Paquete de la aplicación: toda la lógica vive aquí
├── __init__.py                 # create_app(): factoría de la aplicación Flask
├── wsgi.py                     # app = create_app() — punto de entrada que resuelve Vercel
├── config.py                   # Configuración por entorno, leída de variables de entorno
├── content/
│   ├── __init__.py
│   ├── models.py               # Perfil, Trabajo, Experiencia, Capacidad (modelos Pydantic)
│   ├── loader.py               # TOML → modelos validados → Contenido inmutable en memoria
│   └── errors.py               # ContentValidationError: entrada + campo + motivo (FR-012)
├── views/
│   ├── __init__.py
│   ├── home.py                 # Blueprint: /
│   ├── projects.py             # Blueprint: /trabajos, /trabajos/<slug>
│   ├── seo.py                  # Blueprint: /sitemap.xml, /robots.txt
│   └── errors.py               # Manejador 404 (FR-018)
├── caching.py                  # Cabeceras Cache-Control de CDN por tipo de respuesta
├── filters.py                  # Filtros Jinja: fechas y periodos en español
└── templates/
    ├── base.html               # Documento con lang="es", metadatos OG, CSS en línea crítico
    ├── home.html
    ├── projects_index.html
    ├── project_detail.html
    ├── 404.html
    ├── sitemap.xml
    └── partials/               # perfil, capacidades, experiencia, tarjeta de trabajo, estado vacío

content/                        # Datos que edita el propietario. Sin lógica, sin presentación
├── perfil.toml
├── capacidades.toml
├── experiencia.toml
└── trabajos/
    └── <slug>.toml             # Un archivo por trabajo

public/                         # Servido por la CDN de Vercel, nunca por Flask
├── css/site.css
├── img/
├── cv/cv.pdf
├── favicon.ico
└── og/                         # Imágenes de vista previa social (FR-019)

scripts/
└── build.py                    # Valida todo el contenido; detiene el build de Vercel si falla

tests/
├── conftest.py                 # Fixtures: contenido de prueba, aplicación, cliente
├── fixtures/content/           # Contenido TOML controlado, independiente del real
├── unit/                       # Modelos, cargador, filtros, cabeceras de caché
│   └── content/
├── integration/                # Vistas con cliente de pruebas de Flask, plantillas renderizadas
├── contract/                   # Un módulo por ruta pública, según contracts/routes.md
├── e2e/                        # Playwright: teclado, accesibilidad AA, sin JavaScript
└── perf/                       # pytest-benchmark: renderizado y arranque

pyproject.toml                  # Dependencias, herramientas, entrypoint y build de Vercel
uv.lock                         # Bloqueo de versiones, versionado
vercel.json                     # Configuración de función, cabeceras y errores
.pre-commit-config.yaml         # Mismos comandos que ejecuta CI
.python-version                 # 3.13
```

**Structure Decision**: proyecto único con distribución `src/`, exigida por la constitución. Toda la
lógica reside en `src/portafolio/`; `scripts/build.py` es un envoltorio de línea de comandos de tres
líneas sobre `portafolio.content.loader`, sin lógica propia. `content/` y `public/` quedan
deliberadamente **fuera** del paquete: son datos y activos que el propietario edita sin tocar código,
lo que hace verificable el Principio V y la historia de usuario P3. `tests/` refleja la estructura
del paquete y añade los niveles de contrato, extremo a extremo y rendimiento que exige el Principio
II.

## Riesgos y umbrales de decisión

| Riesgo | Impacto | Mitigación adoptada | Umbral de reevaluación |
|--------|---------|---------------------|------------------------|
| Arranque en frío de la función frente a p99 < 500 ms | Incumplimiento del Principio IV en la primera visita de cada región | Contenido cargado en memoria al importar el módulo; sin conexiones externas; bundle mínimo mediante `excludeFiles`; bytecode precompilado por Vercel; caché de CDN que evita la mayoría de invocaciones | Si el p99 medido supera 500 ms de forma sostenida, se pasa a pre-renderizado en tiempo de build (ver `research.md`, alternativa B), que elimina la función por completo |
| El propietario aún no ha entregado su contenido real | Bloquea `/speckit-implement`, no la planificación | El contenido de prueba vive en `tests/fixtures/content/` y es independiente del real; se puede construir y validar todo el sitio con contenido de marcador de posición | Antes de publicar en producción |
| Resolución del punto de entrada con distribución `src/` | Fallo de despliegue en el primer intento | `tool.vercel.entrypoint = "portafolio.wsgi:app"` en `pyproject.toml`, con `src/wsgi.py` como alternativa documentada | Primer despliegue: hay una tarea de humo explícita para confirmarlo |

## Complexity Tracking

> El Principio V exige justificar toda dependencia frente a la biblioteca estándar y toda
> abstracción frente a la alternativa directa. No hay violaciones de las puertas; esta tabla
> registra las decisiones que el principio obliga a defender por escrito.

| Decisión | Por qué es necesaria | Alternativa más simple, y por qué se descartó |
|----------|----------------------|-----------------------------------------------|
| Flask como framework | Mandato explícito del propietario | Generación estática sin framework sería más rápida y simple, pero contradice la instrucción recibida. La decisión es del propietario y está tomada |
| Pydantic 2.x | FR-012 exige detener la publicación **identificando la entrada y el campo defectuoso**. Pydantic produce ese error con ruta de campo exacta y valida tipos, formatos y restricciones de forma declarativa | Validación a mano con `dataclasses` y `tomllib`: exigiría escribir y probar comprobaciones de tipo y de obligatoriedad para unos 30 campos en 4 entidades, con peores mensajes de error. Sería más código propio, no menos |
| TOML en lugar de YAML o JSON | `tomllib` está en la biblioteca estándar desde Python 3.11: cero dependencias. Formato cómodo para texto multilínea y menos frágil que YAML en cuanto a indentación | YAML exigiría `PyYAML`, una dependencia evitable. JSON no admite comentarios ni texto multilínea legible, y el propietario edita estos archivos a mano |
| Carga de contenido en memoria al arrancar | El Principio IV prohíbe la E/S bloqueante en la ruta de petición. Con menos de 100 entradas, el conjunto completo cabe holgadamente en memoria | Leer el TOML por petición: E/S en la ruta caliente, prohibida por la constitución, y sin ninguna ventaja porque el contenido no cambia sin un despliegue nuevo |
| Playwright en las pruebas | SC-003 y SC-004 exigen verificar accesibilidad AA y operabilidad completa por teclado, que no son observables desde el cliente de pruebas de Flask | Solo aserciones sobre el HTML: detectan la ausencia de un atributo, pero no una trampa de foco ni un contraste insuficiente. Es dependencia exclusiva de pruebas, nunca de ejecución |
| Sin JavaScript y sin framework CSS | Camino más corto a los presupuestos del Principio IV y a FR-017 | Un framework CSS añadiría peso, un paso de build y una dependencia, a cambio de nada que 5 plantillas no resuelvan con CSS escrito a mano |
