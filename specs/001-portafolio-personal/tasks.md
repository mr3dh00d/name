---

description: "Task list for Portafolio Personal"
---

# Tasks: Portafolio Personal

**Input**: Design documents from `/specs/001-portafolio-personal/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/)

**Tests**: **OBLIGATORIOS Y PRIMERO.** El Principio I de la constitución es Test-First y está marcado
NON-NEGOTIABLE: toda unidad de comportamiento se escribe primero como prueba que falla. En este
documento, **toda tarea de implementación va precedida de su tarea de prueba**, y esa prueba debe
fallar antes de escribir el código que la satisface. El Principio II añade cobertura ≥ 90% de líneas y
ramas, tres niveles de prueba y contrato por cada ruta pública.

**Organization**: las tareas se agrupan por historia de usuario para que cada una se implemente,
pruebe y entregue de forma independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: historia a la que pertenece (US1, US2, US3)
- Toda descripción incluye la ruta exacta del archivo

## Path Conventions

Proyecto único con distribución `src/`, según `plan.md`: paquete en `src/portafolio/`, pruebas en
`tests/` reflejando el paquete, contenido editable en `content/`, activos de CDN en `public/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: dejar el repositorio con todas las puertas de calidad operativas **antes** de escribir
la primera prueba. El Principio III exige que las herramientas, no las opiniones, verifiquen la
calidad; si las puertas llegan tarde, el código nace incumpliéndolas.

- [X] T001 Crear el árbol de directorios de `plan.md`: `src/portafolio/{content,views,templates/partials}/`, `content/trabajos/`, `public/{css,img,cv,og}/`, `scripts/`, `tests/{unit/content,integration,contract,e2e,perf,fixtures/content}/`, con `__init__.py` en cada paquete Python
- [X] T002 Crear `pyproject.toml` con `requires-python = ">=3.13"`, dependencias de ejecución (`flask`, `pydantic`), grupo de desarrollo (`pytest`, `pytest-cov`, `pytest-benchmark`, `beautifulsoup4`, `playwright`, `axe-playwright-python`, `ruff`, `mypy`, `pre-commit`), `[tool.vercel] entrypoint = "portafolio.wsgi:app"` y `[tool.vercel.scripts] build = "python scripts/build.py"`
- [X] T003 [P] Crear `.python-version` con `3.13`
- [X] T004 [P] Configurar ruff en `pyproject.toml`: reglas de estilo, complejidad ciclomática máxima 10, longitud máxima de función 50 líneas, y prohibición de `# noqa` sin código de regla
- [X] T005 [P] Configurar mypy en `pyproject.toml` en modo `strict`, con `disallow_any_explicit` y `warn_unused_ignores`, cubriendo `src` y `tests`
- [X] T006 [P] Configurar pytest y cobertura en `pyproject.toml`: `--cov=src/portafolio --cov-branch --cov-fail-under=90`, marcadores `unit`, `integration`, `contract`, `e2e`, `perf`, y `--strict-markers`
- [X] T007 [P] Crear `.pre-commit-config.yaml` con exactamente los mismos comandos que ejecutará CI, en el mismo orden
- [X] T008 [P] Crear `vercel.json` con `functions` clavado en el entrypoint resuelto, `excludeFiles` para excluir `tests/**`, `specs/**` y `content/**` no publicable, y cabeceras de caché de larga duración para `public/**`
- [X] T009 [P] Crear `.gitignore` para `.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `htmlcov/`, `.vercel/`
- [X] T010 Ejecutar `uv sync` y versionar `uv.lock` con las versiones fijadas
- [X] T011 [P] Crear `.github/workflows/ci.yml` con las puertas bloqueantes en el orden que fija la constitución: `ruff format --check` → `ruff check` → `mypy --strict` → `pytest` con umbral de cobertura → `python scripts/build.py`
- [X] T012 [P] Inicializar el repositorio git y crear la rama `001-portafolio-personal` (el directorio aún no está bajo control de versiones)

**Checkpoint**: `uv run ruff check .` y `uv run mypy --strict src tests` pasan sobre un árbol vacío.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: modelo de contenido, factoría de la aplicación y andamiaje de pruebas. Las tres
historias los necesitan, así que ninguna puede empezar antes.

**⚠️ CRITICAL**: ninguna historia de usuario puede comenzar hasta completar esta fase.

### Andamiaje de pruebas

- [X] T013 Crear `tests/fixtures/content/` con un conjunto TOML completo y válido (perfil con 2 enlaces, 3 capacidades, 2 experiencias, 4 trabajos de los cuales 3 destacados), independiente del `content/` real, según `contracts/content-schema.md`
- [X] T014 Crear `tests/fixtures/content_invalid/` con casos de fallo: campo obligatorio ausente, campo desconocido, slug que no coincide con el nombre del archivo, capacidad colgante, fechas incoherentes, imagen sin `alt`
- [X] T015 Crear `tests/conftest.py` con fixtures `contenido_valido`, `contenido_vacio`, `app` y `client`, que **siempre** cargan desde `tests/fixtures/`, nunca desde `content/`, para garantizar el determinismo que exige el Principio II

### Modelos de contenido (prueba → implementación)

- [X] T016 [P] Escribir `tests/unit/content/test_models_perfil.py`: obligatoriedad y límites de `nombre`, `titular`, `resumen`; `retrato_alt` obligatorio si hay `retrato`; al menos un enlace; rechazo de etiquetas no descriptivas («aquí», «enlace», «click»); rechazo de URL no `https://`
- [X] T017 [P] Escribir `tests/unit/content/test_models_capacidad.py`: obligatoriedad de `nombre` y `categoria`, valores admitidos de `nivel`, unicidad de `nombre`
- [X] T018 [P] Escribir `tests/unit/content/test_models_experiencia.py`: `fecha_fin` obligatoria salvo `actual = true`; `fecha_fin` no anterior a `fecha_inicio`; `fecha_inicio` no futura; `actual = true` incompatible con `fecha_fin`
- [X] T019 [P] Escribir `tests/unit/content/test_models_trabajo.py`: formato de `slug`; límites de todos los campos de texto; entre 1 y 10 `decisiones`; entre 1 y 12 `capacidades`; `Imagen` exige `alt`, `ancho` y `alto`; coherencia de fechas
- [X] T020 Implementar `src/portafolio/content/models.py` con los modelos Pydantic `Perfil`, `EnlaceExterno`, `Capacidad`, `Experiencia`, `Trabajo`, `Imagen` y `Contenido`, todos con `model_config` que **prohíbe campos desconocidos**, según `data-model.md`
- [X] T021 Escribir `tests/unit/content/test_errors.py`: `ContentValidationError` expone `archivo`, `entrada`, `campo`, `motivo` y `valor_recibido` — es contrato probado, no formato de mensaje (FR-012)
- [X] T022 Implementar `src/portafolio/content/errors.py` con `ContentValidationError`

### Cargador de contenido (prueba → implementación)

- [X] T023 Escribir `tests/unit/content/test_loader.py`: lectura de TOML a modelos; el `slug` debe coincidir con el nombre del archivo; un campo desconocido produce error; orden de `trabajos` por `orden` y luego `titulo`; orden de `experiencia` cronológico inverso con `actual` al frente; agrupación de capacidades por `categoria`
- [X] T024 Escribir `tests/unit/content/test_loader_invariantes.py` con un caso por invariante de `data-model.md`: INV-01 slug duplicado, INV-02 capacidad colgante, INV-03 periodos actuales solapados, INV-04 ruta inexistente bajo `public/`. Cada uno debe nombrar las entradas en conflicto
- [X] T025 Escribir `tests/unit/content/test_loader_vacio.py`: colecciones vacías cargan sin error; un `perfil.toml` ausente o inválido **sí** es error y detiene la carga
- [X] T026 Implementar `src/portafolio/content/loader.py`: `cargar_contenido(ruta) -> Contenido`, inmutable, con validación de invariantes del agregado y errores que identifican archivo, entrada y campo

### Aplicación y presentación base

- [X] T027 [P] Escribir `tests/unit/test_caching.py`: las respuestas HTML válidas llevan `Cache-Control` público con `s-maxage` y `stale-while-revalidate`; las respuestas de error **no** llevan la duración larga (INV-H10 y contrato de 404)
- [X] T028 [P] Implementar `src/portafolio/caching.py` con los ayudantes de cabecera de caché por tipo de respuesta
- [X] T029 [P] Escribir `tests/unit/test_filters.py`: formato de fechas y periodos en español, incluido el caso «en curso» cuando falta `fecha_fin`
- [X] T030 [P] Implementar `src/portafolio/filters.py` con los filtros Jinja de fecha y periodo
- [X] T031 Escribir `tests/integration/test_app_factory.py`: `create_app()` carga el contenido **una sola vez** al arrancar; una petición posterior no abre ningún archivo de `content/` (Principio IV, sin E/S bloqueante en la ruta de petición)
- [X] T032 Implementar `src/portafolio/config.py` leyendo configuración de variables de entorno con valores por defecto seguros, sin secretos en el código (Principio III)
- [X] T033 Implementar `src/portafolio/__init__.py` con la factoría `create_app()`: carga el contenido, registra filtros, blueprints, manejadores de error y cabeceras de caché
- [X] T034 Implementar `src/portafolio/wsgi.py` con `app = create_app()`, el punto de entrada que resuelve Vercel
- [X] T035 Crear `tests/contract/invariantes.py`: ayudante reutilizable que verifica INV-H01 a INV-H10 de `contracts/routes.md` sobre cualquier respuesta HTML, para que cada contrato de ruta lo invoque en lugar de repetirlo
- [X] T036 Crear `src/portafolio/templates/base.html`: `lang="es"`, bloque de metadatos sociales, CSS crítico en línea, **sin ninguna referencia a JavaScript** (FR-017, INV-H07)
- [X] T037 [P] Crear `public/css/site.css` con la base de estilos: tipografías del sistema, tema claro y oscuro mediante `prefers-color-scheme`, respeto de `prefers-reduced-motion`, e indicador de foco visible (FR-016, SC-004)
- [X] T038 [P] Crear contenido de marcador de posición en `content/perfil.toml`, `content/capacidades.toml`, `content/experiencia.toml` y `content/trabajos/`, más los activos correspondientes en `public/`, para que el sitio arranque antes de disponer de los datos reales del propietario

**Checkpoint**: `create_app()` arranca, el contenido se valida al inicio y las pruebas unitarias del
modelo pasan. Ninguna ruta responde todavía.

---

## Phase 3: User Story 1 — Evaluación rápida del perfil (Priority: P1) 🎯 MVP

**Goal**: un reclutador identifica quién es el propietario, qué sabe hacer y dónde seguir su rastro
profesional, sin salir de la página principal.

**Independent Test**: cargar `/` en móvil y escritorio y comprobar que nombre, titular, resumen,
capacidades, trabajos destacados, descarga de CV y enlaces externos son visibles y utilizables sin
navegar fuera de esa página.

### Pruebas primero

- [X] T039 [US1] Escribir `tests/contract/test_home.py` cubriendo **todos** los casos de la tabla `GET /` de `contracts/routes.md`: éxito, identidad, capacidades agrupadas, experiencia en orden inverso, destacados filtrados y ordenados, enlace de CV, estados vacíos por sección, y `405` ante `POST`; invocando el ayudante de invariantes de T035
- [X] T040 [P] [US1] Escribir `tests/integration/test_home_estructura.py` con BeautifulSoup: un solo `<h1>`, jerarquía de encabezados sin saltos, toda `<img>` con `alt`, `width` y `height`, y enlaces externos con `rel="noopener noreferrer"`
- [X] T041 [P] [US1] Escribir `tests/e2e/test_p1_perfil.py` con Playwright: nombre, titular y resumen visibles sin desplazamiento a 1280×800 y a 375×667; el enlace de CV descarga en menos de 3 s; el sitio sigue legible y navegable con JavaScript deshabilitado

### Implementación

- [X] T042 [US1] Implementar `src/portafolio/views/home.py` como blueprint de `/`, que solo selecciona del contenido ya cargado y elige plantilla (vista delgada, Principio III)
- [X] T043 [P] [US1] Crear `src/portafolio/templates/partials/perfil.html` con nombre, titular, resumen, retrato con `alt`, `width` y `height`, y descarga de CV
- [X] T044 [P] [US1] Crear `src/portafolio/templates/partials/enlaces_externos.html`, presente en todas las páginas mediante `base.html` (INV-H09, FR-005)
- [X] T045 [P] [US1] Crear `src/portafolio/templates/partials/capacidades.html` agrupando por `categoria`
- [X] T046 [P] [US1] Crear `src/portafolio/templates/partials/experiencia.html` en orden cronológico inverso
- [X] T047 [P] [US1] Crear `src/portafolio/templates/partials/tarjeta_trabajo.html` con título, resumen y capacidades, reutilizable por la historia US2
- [X] T048 [P] [US1] Crear `src/portafolio/templates/partials/estado_vacio.html`, el bloque explicativo que exige FR-010
- [X] T049 [US1] Crear `src/portafolio/templates/home.html` componiendo los parciales anteriores
- [X] T050 [US1] Añadir a `public/css/site.css` los estilos de la página principal, adaptables de 320 px a 2560 px sin desplazamiento horizontal (FR-015, SC-008)

**Checkpoint**: **MVP entregable.** `/` cumple su contrato completo y la historia P1 se puede
demostrar de forma independiente. El portafolio ya sirve su propósito aunque no exista nada más.

---

## Phase 4: User Story 2 — Exploración en profundidad de un trabajo (Priority: P2)

**Goal**: un visitante interesado entiende qué se construyó, qué problema resolvía, qué se decidió y
cuál fue el resultado.

**Independent Test**: abrir la ficha de cada trabajo por su enlace directo, sin pasar por la página
principal, y comprobar que muestra contexto, rol, decisiones, resultado y enlaces externos.

### Pruebas primero

- [X] T051 [US2] Escribir `tests/contract/test_projects_index.py` cubriendo la tabla `GET /trabajos`: éxito, completitud, orden, enlaces por slug, estado vacío y `405`
- [X] T052 [US2] Escribir `tests/contract/test_project_detail.py` cubriendo la tabla `GET /trabajos/<slug>`: éxito, contenido completo, enlace directo sin `Referer`, navegación de vuelta, enlaces externos, metadatos sociales propios de la ficha, **`404` ante slug inexistente**, **`404` ante slug malformado** con mayúsculas, espacios o recorrido de rutas — nunca `500` ni lectura fuera de `content/` — y `405`
- [X] T053 [P] [US2] Escribir `tests/contract/test_404.py`: ruta desconocida devuelve `404`, el cuerpo ofrece enlaces al inicio y al índice, **no** filtra traza de pila ni rutas del sistema de archivos, y no se cachea con la duración larga
- [X] T054 [P] [US2] Escribir `tests/e2e/test_p2_trabajo.py` con Playwright: navegación desde un destacado hasta su ficha, enlace directo en sesión nueva, enlaces externos que abren en pestaña nueva sin perder el portafolio

### Implementación

- [X] T055 [US2] Implementar `src/portafolio/views/projects.py` como blueprint de `/trabajos` y `/trabajos/<slug>`, resolviendo el slug **contra el contenido en memoria**, nunca contra el sistema de archivos, lo que hace estructuralmente imposible el recorrido de rutas
- [X] T056 [US2] Implementar `src/portafolio/views/errors.py` con el manejador `404` (FR-018)
- [X] T057 [P] [US2] Crear `src/portafolio/templates/projects_index.html` reutilizando `partials/tarjeta_trabajo.html`
- [X] T058 [P] [US2] Crear `src/portafolio/templates/project_detail.html` con problema, rol, decisiones, resultado, imágenes con dimensiones, enlaces externos y vuelta al índice
- [X] T059 [P] [US2] Crear `src/portafolio/templates/404.html` con rutas de navegación al contenido existente
- [X] T060 [US2] Extender el bloque de metadatos de `base.html` para que la ficha sobrescriba `og:title`, `og:description`, `og:image` y `og:url` con los del trabajo (FR-019)
- [X] T061 [US2] Añadir a `public/css/site.css` los estilos del índice, de la ficha y de la página de error

**Checkpoint**: US1 y US2 funcionan de forma independiente. El portafolio está completo de cara al
visitante.

---

## Phase 5: User Story 3 — Actualización de contenido por el propietario (Priority: P3)

**Goal**: el propietario publica contenido nuevo sin tocar lógica ni presentación, y un archivo
defectuoso detiene la publicación señalando entrada y campo.

**Independent Test**: añadir una entrada de contenido nueva y comprobar que aparece publicada y
enlazada sin haber modificado ningún archivo de `src/`.

### Pruebas primero

- [X] T062 [US3] Escribir `tests/integration/test_build_script.py`: con contenido válido el script sale con código 0; con cada caso de `tests/fixtures/content_invalid/` sale con código distinto de cero e imprime archivo, entrada y campo (FR-012)
- [X] T063 [P] [US3] Escribir `tests/integration/test_content_reload.py`: añadir un trabajo al contenido de prueba lo hace aparecer en el índice y en su ficha tras reconstruir la aplicación, sin cambios en el código
- [X] T064 [P] [US3] Escribir `tests/integration/test_activos_referenciados.py`: toda ruta referenciada por `retrato`, `cv`, `imagenes` y `og_imagen` existe bajo `public/` (INV-04, caso límite «recurso ausente»)

### Implementación

- [X] T065 [US3] Implementar `scripts/build.py` como envoltorio de línea de comandos sobre `portafolio.content.loader`, **sin lógica propia**: carga, valida, informa y sale con código distinto de cero ante el primer error
- [X] T066 [US3] Verificar que `[tool.vercel.scripts] build` de `pyproject.toml` invoca `scripts/build.py` y que un contenido inválido **rompe el build de Vercel**, no solo el arranque local
- [X] T067 [P] [US3] Escribir `content/README.md`: cómo añadir un trabajo, una experiencia o una capacidad, con referencia a `contracts/content-schema.md` como fuente del formato

**Checkpoint**: las tres historias completas. El portafolio es mantenible por su propietario.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: difusión, presupuestos de rendimiento, accesibilidad verificada y despliegue. Nada aquí
pertenece a una sola historia.

### Difusión (FR-019, FR-020)

- [X] T068 [P] Escribir `tests/contract/test_seo.py` cubriendo las tablas `GET /sitemap.xml` y `GET /robots.txt`: XML bien formado, todas las direcciones públicas incluidas, la ruta de error excluida, `<loc>` absolutas, y sitemap declarado en `robots.txt`
- [X] T069 Implementar `src/portafolio/views/seo.py` y `src/portafolio/templates/sitemap.xml`
- [X] T070 [P] Escribir `tests/integration/test_metadatos_sociales.py`: cada página compartible expone `og:title`, `og:description`, `og:image`, `og:url` y `twitter:card` correctos (SC-007)
- [X] T071 [P] Crear las imágenes de vista previa social en `public/og/` y referenciarlas desde el contenido

### Rendimiento (Principio IV)

- [X] T072 [P] Escribir `tests/perf/test_render.py` con `pytest-benchmark`: renderizado de cada página por debajo de 20 ms
- [X] T073 [P] Escribir `tests/perf/test_startup.py` con `pytest-benchmark`: `create_app()` con el contenido real por debajo de 1 s
- [X] T074 Verificar que la suite completa se ejecuta en menos de 60 s y añadir la comprobación como puerta de CI en `.github/workflows/ci.yml`
- [X] T075 [P] Añadir el trabajo de Lighthouse CI a `.github/workflows/ci.yml` sobre el despliegue de vista previa, con umbrales que fallan el build: LCP < 2,5 s, CLS < 0,1, INP < 200 ms, peso de la página inicial ≤ 300 KB, accesibilidad y buenas prácticas ≥ 95 (SC-002, SC-003)
- [X] T076 Ajustar `excludeFiles` en `vercel.json` con el bundle real y registrar el tamaño resultante

### Accesibilidad y experiencia (FR-014, FR-016, SC-003, SC-004)

- [X] T077 [P] Escribir `tests/e2e/test_accesibilidad.py` con axe-core sobre `/`, `/trabajos`, una ficha y la página de error: cero infracciones de nivel AA
- [X] T078 [P] Escribir `tests/e2e/test_teclado.py`: recorrido completo por teclado de todas las páginas, sin trampas de foco, con indicador de foco siempre visible (SC-004)
- [X] T079 [P] Escribir `tests/e2e/test_temas.py`: la presentación responde a `prefers-color-scheme` claro y oscuro y a `prefers-reduced-motion` (FR-016)
- [X] T080 [P] Escribir `tests/e2e/test_responsive.py`: sin desplazamiento horizontal ni pérdida de contenido de 320 px a 2560 px (SC-008)
- [X] T081 [P] Escribir `tests/integration/test_sin_terceros.py`: ningún documento referencia dominios de seguimiento ni recursos de terceros (FR-021, SC-009, INV-H08)
- [X] T082 [P] Añadir a `public/css/site.css` los estilos de impresión, para que el contenido sea legible al imprimir o guardar como documento (caso límite «impresión»)
- [X] T083 [P] Escribir `tests/integration/test_idioma.py`: el documento declara `lang="es"` y no hay cadenas de interfaz en otro idioma (FR-013, SC-010)

### Despliegue

- [~] T084 🔧 **EJECUTADA: falló y se corrigió.** El entrypoint no resolvía con la distribución `src/`; ver `research.md` R-001 y `tests/integration/test_entrypoint_vercel.py`. Pendiente de confirmar en el siguiente despliegue. Primer despliegue de vista previa con `vercel deploy` y **comprobación de humo del punto de entrada**: la aplicación responde y no hay error de importación. Si `tool.vercel.entrypoint` no resuelve la distribución `src/`, aplicar la alternativa documentada en `research.md` R-001: `src/wsgi.py` con `app` de nivel superior
- [ ] T085 ⏸️ **BLOQUEADA por T084.** **Comprobación de humo de caché de CDN**: ejecutar `curl -sI <url-de-vista-previa>/` dos veces y confirmar acierto de caché en la cabecera `x-vercel-cache` de la segunda respuesta, verificando también las cabeceras que emite `src/portafolio/caching.py`. Es el mecanismo del que depende el p95 del Principio IV; un fallo aquí es un fallo de presupuesto, no un detalle de configuración
- [ ] T086 ⏸️ **BLOQUEADA por T084.** **Comprobación de humo de activos**: la hoja de estilos, el retrato y el CV responden `200` en el despliegue, no solo en `vercel dev`
- [ ] T087 ⏸️ **BLOQUEADA por T084.** Registrar el p95 y el p99 reales desde las métricas de la plataforma. **Si el p99 supera 500 ms de forma sostenida**, activar la salida documentada en `research.md` R-001 alternativa B (pre-renderizado en tiempo de build), que no altera vistas, plantillas ni modelo de contenido
- [X] T088 [P] Escribir `README.md` en la raíz con puesta en marcha, puertas de calidad y despliegue, remitiendo a `quickstart.md` para la validación completa
- [ ] T089 ⏸️ **BLOQUEADA: requiere los datos reales del propietario.** Sustituir el contenido de marcador de posición de `content/` y `public/` por los datos reales del propietario, y volver a ejecutar `scripts/build.py` y la suite completa antes de `vercel deploy --prod`

---

## Dependencies

### Orden entre fases

```text
Phase 1 (Setup)
   └─> Phase 2 (Foundational)  ← bloquea todo lo demás
          ├─> Phase 3 (US1, P1)  ← MVP entregable en solitario
          ├─> Phase 4 (US2, P2)  ← depende de Foundational; reutiliza T047 de US1
          ├─> Phase 5 (US3, P3)  ← depende solo de Foundational
          └─> Phase 6 (Polish)   ← requiere las rutas de US1 y US2 publicadas
```

### Dependencias entre historias

| Historia | Depende de | Naturaleza de la dependencia |
|----------|-----------|------------------------------|
| US1 (P1) | Solo Fase 2 | Ninguna dependencia de otra historia. Es el MVP |
| US2 (P2) | Fase 2, y T047 de US1 | Reutiliza la tarjeta de trabajo. Si se implementara US2 antes que US1, T047 se movería a US2. La dependencia es de conveniencia, no estructural |
| US3 (P3) | Solo Fase 2 | Totalmente independiente de US1 y US2: valida contenido, no páginas. **Puede desarrollarse en paralelo a ambas** |

### Dependencias críticas dentro de las fases

- **Test-First**: en cada par prueba/implementación, la prueba debe existir y **fallar** antes de
  escribir el código. Esto no es una preferencia de orden: el Principio I lo marca NON-NEGOTIABLE y un
  PR que lo incumpla debe ser rechazado.
- T020 (modelos) bloquea T023–T026 (cargador), que a su vez bloquean T031–T034 (aplicación).
- T035 (ayudante de invariantes) bloquea T039, T051, T052, T053 y T068: todos los contratos de ruta lo
  invocan.
- T036 (`base.html`) bloquea toda plantilla.
- T060 (metadatos por página) depende de que exista `project_detail.html` (T058).
- T084 bloquea T085, T086 y T087: no hay nada que medir sin despliegue.
- T089 es la última tarea y depende de un dato externo que el propietario aún no ha entregado.

---

## Parallel Execution Examples

### Fase 1 — configuración

T003 a T009 y T011 a T012 tocan archivos distintos y no dependen entre sí. Solo T002 y T010 son
secuenciales, porque `uv sync` necesita el `pyproject.toml` completo.

### Fase 2 — pruebas de modelos

T016, T017, T018 y T019 son cuatro archivos de prueba independientes y pueden escribirse a la vez.
Convergen en T020, que implementa todos los modelos y hace pasar las cuatro.

Igualmente T027–T028 (caché) y T029–T030 (filtros) son dos pares independientes que pueden avanzar en
paralelo.

### Fase 3 — plantillas de US1

T043 a T048 son seis parciales en archivos distintos: paralelizables por completo una vez existe
`base.html` (T036) y la vista los alimenta (T042).

### Entre historias

**US3 (Fase 5) es independiente de US1 y US2**. En cuanto termina la Fase 2, un segundo frente de
trabajo puede llevar toda la historia de actualización de contenido mientras el primero construye la
página principal.

### Fase 6 — verificación

T077 a T083 son siete archivos de prueba independientes, todos paralelizables una vez las rutas
responden.

---

## Implementation Strategy

### MVP: solo la Fase 3

**Fase 1 → Fase 2 → Fase 3** produce un portafolio publicable: una página principal completa con
identidad, capacidades, experiencia, trabajos destacados, CV y enlaces profesionales. Es exactamente
lo que la especificación identifica como el 80% del tráfico real y el único recorrido cuyo fracaso
invalidaría el producto.

Detenerse ahí y desplegar es una decisión legítima. Conviene ejecutar antes las tareas de despliegue
T084 a T086, porque son las que confirman los supuestos de la plataforma.

### Entrega incremental

| Incremento | Fases | Qué añade |
|------------|-------|-----------|
| 1 · MVP | 1, 2, 3 | Portafolio de una página, demostrable y desplegable |
| 2 · Profundidad | 4 | Índice y fichas de trabajo, página de error |
| 3 · Mantenibilidad | 5 | Publicación segura de contenido por el propietario |
| 4 · Calidad verificada | 6 | Difusión, presupuestos medidos, accesibilidad demostrada |

Cada incremento deja la rama principal desplegable, como exige el flujo de desarrollo de la
constitución.

### Dos advertencias sobre el orden

**No pospongas la Fase 6 pensando que es cosmética.** Contiene la verificación de los presupuestos del
Principio IV y de la accesibilidad AA, que son requisitos con umbrales numéricos, no acabados. Si
T075 o T077 fallan tarde, el rediseño cuesta mucho más que haber medido antes. Ejecuta T072, T073,
T077 y T078 en cuanto la Fase 3 responda, sin esperar a la Fase 4.

**T089 depende de ti, no del código.** El contenido real del propietario aún no se ha facilitado. Todo
lo demás puede completarse con el contenido de marcador de posición de T038, pero producción no debe
publicarse con él.
