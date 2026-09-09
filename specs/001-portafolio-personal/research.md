# Phase 0 — Research: Portafolio Personal

**Fecha**: 2026-09-02 · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

Todas las incógnitas del Contexto Técnico quedan resueltas aquí. No queda ningún
`NEEDS CLARIFICATION` abierto.

---

## R-001 · Modelo de despliegue de Flask en Vercel

**Decisión**: usar el **preset nativo de Python/Flask de Vercel**, que detecta la aplicación por una
instancia `Flask` llamada `app` y la ejecuta como una única Vercel Function sobre Fluid Compute. El
punto de entrada se declara explícitamente en `pyproject.toml`:

```toml
[tool.vercel]
entrypoint = "portafolio.wsgi:app"
```

**Rationale**: es el camino oficial y sin configuración para Flask en la plataforma. Mantiene la
aplicación idéntica en local (`flask run` / `vercel dev`) y en producción, lo que hace que las
pruebas de integración con el cliente de Flask prueben exactamente el código desplegado. La
declaración explícita del punto de entrada evita la ambigüedad de la detección por nombre de archivo,
que no contempla de forma directa una distribución `src/` con paquete.

**Alternativas consideradas**:

- **A. Funciones basadas en archivos bajo `/api`**: patrón heredado; obliga a partir la aplicación en
  manejadores por archivo y a duplicar el enrutado que Flask ya resuelve. Descartada.
- **B. Pre-renderizado en tiempo de build (Frozen-Flask o equivalente) y despliegue solo estático**:
  técnicamente **superior en rendimiento** — elimina la función, y con ella el arranque en frío, de
  modo que cada petición se sirve desde la CDN. Descartada como diseño principal porque el propietario
  pidió expresamente usar Flask como framework de la aplicación, y esta variante lo degrada a un
  generador de HTML en tiempo de build. **Se conserva como salida documentada**: si el p99 medido
  incumple el Principio IV, migrar a esta alternativa es un cambio contenido, ya que las vistas, las
  plantillas y el modelo de contenido no cambian; solo se sustituye el modo de publicación.
- **C. Contenedor Docker con Flask**: control total sobre el sistema base, a cambio de gestionar la
  imagen, su tamaño y su ciclo de vida. Complejidad no justificada para 5 rutas estáticas.

**Verificación pendiente en el primer despliegue**: confirmar que `tool.vercel.entrypoint` resuelve el
módulo `portafolio.wsgi` con la distribución `src/`. Alternativa documentada si no lo hiciera: un
`src/wsgi.py` con `app` de nivel superior, que es una de las rutas de detección nativas de la
plataforma. Existe una tarea de humo explícita para este punto.

---

## R-002 · Cómo cumplir p95 < 200 ms con una función de servidor

**Decisión**: **caché de CDN como mecanismo primario de rendimiento**, no como optimización añadida.
Toda respuesta HTML se emite con `Cache-Control: public, s-maxage=<larga>, stale-while-revalidate`, y
cada despliegue invalida la caché de la CDN.

**Rationale**: el contenido del portafolio es inmutable entre despliegues — no hay sesiones, ni
personalización, ni datos por visitante (FR-006, FR-021). Cachear la respuesta completa en el borde
es por tanto correcto por construcción, no un compromiso. El resultado es que la práctica totalidad
del tráfico real se sirve desde el borde en milisegundos de un solo dígito, y la función solo se
invoca ante una caché fría por región. Esto convierte el p95 en una métrica de CDN, no de función.

Medidas complementarias, todas verificables:

1. **Contenido cargado una vez al importar el módulo**, nunca por petición. Elimina toda E/S de disco
   de la ruta caliente, como exige el Principio IV.
2. **Activos estáticos en `public/`**, servidos por la CDN sin pasar por Flask. La documentación de la
   plataforma es explícita en no usar `app.static_folder` en Vercel.
3. **`excludeFiles` en `vercel.json`** para dejar fuera del bundle las pruebas, los *fixtures* y el
   contenido de desarrollo, reduciendo el tiempo de inicialización.
4. **Cero JavaScript y tipografías del sistema**: ninguna petición de red secundaria bloquea el
   renderizado, lo que sitúa el LCP muy por debajo de 2,5 s sin trabajo adicional.

**Alternativas consideradas**:

- **Sin caché, confiando en Fluid Compute**: cada visita pagaría el renderizado y, en el peor caso, un
  arranque en frío. Innecesario cuando la respuesta es idéntica para todos.
- **Caché en memoria dentro de la función**: no ayuda a la primera petición de cada instancia y no
  evita la invocación. La caché de CDN domina en ambos aspectos.

---

## R-003 · Formato y validación del contenido

**Decisión**: contenido en **TOML** bajo `content/`, validado con **Pydantic 2.x** contra los modelos
de `data-model.md`, cargado y validado íntegramente al arrancar la aplicación y también en el build de
Vercel.

**Rationale**: `tomllib` forma parte de la biblioteca estándar, así que el formato no cuesta ninguna
dependencia. TOML admite comentarios y texto multilínea legible, y no es sensible a la indentación
como YAML — importa porque el propietario edita estos archivos a mano (historia P3). Pydantic aporta
exactamente lo que exige FR-012: un error que identifica la entrada y el campo defectuoso, con
validación declarativa de tipos, obligatoriedad, formatos de fecha y restricciones de longitud.

**Alternativas consideradas**:

- **YAML**: requeriría `PyYAML`, una dependencia evitable, y su sensibilidad a la indentación produce
  errores sutiles en edición manual.
- **JSON**: sin comentarios y con texto multilínea ilegible. Mal formato para que una persona edite
  descripciones largas de proyectos.
- **Markdown con front matter**: atractivo para prosa larga, pero introduce un analizador de Markdown
  y una segunda gramática. El contenido actual son campos estructurados cortos, no artículos — y los
  artículos quedaron fuera de alcance.
- **Validación manual con `dataclasses`**: unos 30 campos entre 4 entidades exigirían escribir y
  probar a mano comprobaciones de tipo, obligatoriedad y formato, con mensajes de error peores. Más
  código propio, no menos.

---

## R-004 · Detener la publicación ante contenido inválido (FR-012)

**Decisión**: enganchar la validación al **build de Vercel** mediante el script de build de Python del
preset:

```toml
[tool.vercel.scripts]
build = "python scripts/build.py"
```

`scripts/build.py` carga y valida todo el contenido y termina con código distinto de cero ante el
primer error, imprimiendo archivo, entrada y campo. El mismo comando se ejecuta en `pre-commit` y en
integración continua.

**Rationale**: FR-012 exige que la publicación **se detenga**, no que se advierta. El script de build
del preset se ejecuta después de instalar dependencias y antes de desplegar, que es exactamente el
punto donde un fallo impide que el contenido roto llegue a producción. Ejecutar el mismo comando en
`pre-commit` adelanta el error al momento de la edición, sin duplicar lógica: ambos invocan el mismo
cargador del paquete.

**Alternativas consideradas**:

- **Validar solo al arrancar la aplicación**: el despliegue tendría éxito y el sitio caería en
  producción. Contradice el requisito.
- **Validar solo en integración continua**: no protege un despliegue lanzado desde la CLI.

---

## R-005 · Accesibilidad AA y operabilidad por teclado verificables

**Decisión**: dos niveles complementarios. Aserciones estructurales sobre el HTML renderizado con
**BeautifulSoup4** en las pruebas de integración (jerarquía de encabezados, `lang` del documento,
alternativa textual en toda imagen, metadatos sociales, marca de destino de los enlaces externos), y
pruebas **extremo a extremo con Playwright para Python más axe-core** para lo que solo es observable
en un navegador real: recorrido completo por teclado sin trampas de foco, indicador de foco visible,
contraste y ausencia de infracciones AA.

**Rationale**: SC-003 y SC-004 son criterios verificables solo en un navegador. El cliente de pruebas
de Flask demuestra que un atributo existe, no que el foco sea alcanzable ni que el contraste sea
suficiente. Playwright ofrece enlaces oficiales para Python, con lo que la suite completa sigue siendo
Python, coherente con la constitución. Es dependencia exclusiva de pruebas: nunca entra en el bundle
de ejecución.

**Alternativas consideradas**:

- **Solo aserciones sobre HTML**: baratas y rápidas, pero incapaces de detectar precisamente los
  fallos que SC-003 y SC-004 nombran.
- **Auditoría manual**: no es reproducible ni ejecutable en integración continua, y el Principio II
  exige puertas automáticas.

---

## R-006 · Medición de los presupuestos de rendimiento

**Decisión**: cada presupuesto del Principio IV se asigna a una medición concreta y automatizable.

| Presupuesto | Cómo se mide | Dónde se ejecuta |
|-------------|--------------|------------------|
| Renderizado por página < 20 ms | `pytest-benchmark` sobre la vista con el cliente de pruebas | `tests/perf/`, en cada CI |
| Arranque de la aplicación < 1 s | Medición del tiempo de `create_app()` con el contenido real | `tests/perf/`, en cada CI |
| Suite de pruebas < 60 s | Duración total informada por pytest | Puerta de CI |
| LCP < 2,5 s · CLS < 0,1 · INP < 200 ms | Lighthouse CI en móvil simulado sobre el despliegue de vista previa | CI, tras el despliegue |
| Página inicial ≤ 300 KB comprimidos | Suma del peso de transferencia informada por Lighthouse | CI, tras el despliegue |
| p95 < 200 ms · p99 < 500 ms | Métricas de la plataforma sobre el despliegue de vista previa, más una comprobación de que la respuesta llega con acierto de caché de CDN | Manual en el primer despliegue, después continuo |

**Rationale**: el Principio IV exige respaldar toda afirmación de rendimiento con una medición
antes/después. Definir de antemano la herramienta de cada presupuesto evita que la puerta se convierta
en una opinión. Lighthouse se ejecuta como herramienta de integración continua sobre el sitio ya
desplegado; no es una dependencia de la aplicación y no contradice la restricción de Python del
proyecto.

**Alternativas consideradas**:

- **Confiar en la analítica de producción**: llegaría tarde y el sitio no recoge datos de visitantes
  (FR-021).
- **Pruebas de carga sintéticas**: desproporcionadas para decenas de visitas diarias, y engañosas
  frente a una respuesta servida por CDN.

---

## R-007 · Presentación: CSS, tema y tipografía

**Decisión**: CSS propio en un único archivo bajo `public/css/`, con el CSS crítico de la primera
pantalla en línea dentro de `base.html`. Tema claro y oscuro exclusivamente mediante
`prefers-color-scheme`, y respeto de `prefers-reduced-motion`. Tipografías del sistema. Cero
JavaScript.

**Rationale**: FR-016 exige respetar las preferencias del sistema, no ofrecer un conmutador — y un
conmutador exigiría JavaScript y almacenamiento, que FR-017 y FR-021 desaconsejan. Las tipografías del
sistema eliminan la descarga de fuentes, la principal causa de texto invisible durante la carga y una
fracción grande del peso típico de una página. Con 5 plantillas, un framework CSS añadiría peso y un
paso de build a cambio de nada.

**Alternativas consideradas**:

- **Framework CSS**: peso y dependencia injustificados a esta escala.
- **Conmutador de tema con JavaScript**: contradice FR-017 y no lo pide ningún requisito.
- **Tipografías web**: coste de red directo contra el presupuesto de 300 KB y contra el LCP.

---

## R-008 · Versión de Python y gestión de dependencias

**Decisión**: **Python 3.13**, fijado en `.python-version` y en `requires-python` de `pyproject.toml`.
Dependencias gestionadas con **uv** y `uv.lock` versionado.

**Rationale**: la constitución exige 3.12 o superior. Vercel ofrece 3.12, 3.13 y 3.14 tanto en la
imagen de build como en ejecución; 3.13 aporta mejoras de rendimiento del intérprete sobre la versión
por defecto sin la novedad de 3.14, y en 2026 cuenta con soporte maduro en ruff, mypy y pytest. uv
está disponible en los builds de la plataforma sin configuración, y el archivo de bloqueo versionado
satisface la exigencia de reproducibilidad de la constitución.

**Alternativas consideradas**:

- **3.12**: es el valor por defecto de la plataforma y funcionaría, pero renuncia a mejoras de
  rendimiento gratuitas.
- **3.14**: demasiado reciente para dar por sentado el soporte de todo el instrumental de calidad; sin
  ventaja para esta carga de trabajo.
- **Poetry o pip-tools**: válidos, pero uv es más rápido y la plataforma lo reconoce sin
  configuración.
