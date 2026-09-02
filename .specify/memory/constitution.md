<!--
SYNC IMPACT REPORT
==================
Version change: [CONSTITUTION_VERSION] (unfilled template) → 1.0.0
Bump rationale: MAJOR — initial ratification. The file previously contained only
placeholder tokens; this establishes the first binding governance baseline.

Modified principles:
  - [PRINCIPLE_1_NAME] → I. Test-First (NON-NEGOTIABLE)
  - [PRINCIPLE_2_NAME] → II. Estándares de Testing Verificables
  - [PRINCIPLE_3_NAME] → III. Calidad de Código Aplicada por Herramientas
  - [PRINCIPLE_4_NAME] → IV. Rendimiento con Presupuestos Medibles
  - [PRINCIPLE_5_NAME] → V. Simplicidad Explícita y Contenido como Datos

Added sections:
  - Restricciones Tecnológicas (Python)  [was SECTION_2_NAME]
  - Flujo de Desarrollo y Puertas de Calidad  [was SECTION_3_NAME]
  - Governance (rules populated)

Removed sections: none

Deferred TODOs:
  - TODO(RATIFICATION_DATE): se registró 2026-09-02 como fecha de adopción inicial
    por ser la fecha de creación de este documento. Corregir si el proyecto se
    considera adoptado en otra fecha.

Templates requiring review at runtime (not modified here):
  - .specify/templates/plan-template.md — Constitution Check debe cubrir los 5 principios
  - .specify/templates/tasks-template.md — el orden de tareas debe respetar Test-First
  - .specify/templates/spec-template.md — los criterios de aceptación deben ser medibles
-->

# Portafolio Personal Constitution

## Core Principles

### I. Test-First (NON-NEGOTIABLE)

Toda unidad de comportamiento se escribe primero como prueba que falla, luego se implementa
hasta que pasa, y solo después se refactoriza (Red-Green-Refactor). Un pull request que
introduce comportamiento nuevo sin una prueba que falle antes del cambio MUST ser rechazado.
Las correcciones de defectos MUST incluir una prueba de regresión que reproduzca el fallo
reportado antes de aplicar el arreglo.

Rationale: un portafolio es la prueba pública de cómo trabaja su autor; el historial de
commits debe demostrar la disciplina, no solo el resultado final.

### II. Estándares de Testing Verificables

Las pruebas MUST cumplir todos estos criterios objetivos:

- Cobertura de líneas y ramas ≥ 90% en el paquete de la aplicación; el umbral se aplica en CI
  con `--cov-fail-under=90` y solo puede bajarse mediante enmienda a esta constitución.
- Tres niveles obligatorios: unitarias (lógica pura, sin I/O), de integración (persistencia,
  renderizado, contratos HTTP), y end-to-end sobre las rutas públicas del portafolio.
- Determinismo total: prohibidas las pruebas que dependan de reloj real, red externa, orden de
  ejecución o estado compartido. El tiempo y la aleatoriedad MUST inyectarse o congelarse.
- Cero tolerancia a pruebas inestables: una prueba que falle de forma intermitente se corrige o
  se elimina en el mismo PR; MUST NOT marcarse como `skip` o `xfail` sin un issue enlazado.
- Toda ruta pública y todo endpoint MUST tener al menos una prueba de contrato que valide
  código de estado, forma de la respuesta y comportamiento ante entrada inválida.

Rationale: "tenemos tests" no es un estándar; los umbrales y las prohibiciones explícitas sí
son auditables.

### III. Calidad de Código Aplicada por Herramientas

La calidad se verifica con máquinas, no con opiniones. El repositorio MUST mantener en verde:

- `ruff check` y `ruff format --check` sin excepciones no justificadas; cada `# noqa` MUST
  llevar código de regla y comentario que explique el motivo.
- `mypy --strict` (o `pyright` en modo strict) sin errores. Prohibido `Any` implícito y
  `type: ignore` sin código de error específico y justificación en línea.
- Anotaciones de tipo completas en toda función y método públicos, y docstrings en todo módulo,
  clase y función pública.
- Complejidad ciclomática ≤ 10 por función y funciones ≤ 50 líneas; superar el límite exige
  refactorizar, no ajustar la configuración del linter.
- Sin secretos, credenciales ni rutas absolutas del entorno local en el código o los tests;
  la configuración se lee de variables de entorno con valores por defecto seguros.

Rationale: las reglas ejecutables sobreviven al cansancio del revisor y hacen que la calidad no
dependa de quién revisa.

### IV. Rendimiento con Presupuestos Medibles

El rendimiento es un requisito con números, no una aspiración. Se aplican estos presupuestos:

- Respuesta del servidor: p95 < 200 ms y p99 < 500 ms para cualquier ruta del portafolio bajo
  la carga de referencia definida en el plan de la funcionalidad.
- Experiencia percibida: LCP < 2.5 s, CLS < 0.1 e INP < 200 ms en la simulación móvil de
  Lighthouse; peso total de la página inicial ≤ 300 KB comprimidos.
- Arranque del proceso de la aplicación < 1 s; suite de pruebas completa < 60 s en CI.
- Prohibido el acceso a datos con patrón N+1 y el trabajo bloqueante de I/O en la ruta de
  petición; las operaciones lentas se precomputan, se cachean o se mueven fuera de la petición.
- Toda afirmación de optimización MUST respaldarse con una medición antes/después
  (`pytest-benchmark`, `time`, o traza de perfilado) incluida en la descripción del PR.

Un cambio que exceda cualquier presupuesto MUST NOT fusionarse hasta corregirse o hasta que se
enmiende el presupuesto en esta constitución con su justificación.

Rationale: sin umbrales numéricos, "es rápido" se degrada versión a versión sin que nadie lo
note.

### V. Simplicidad Explícita y Contenido como Datos

Se aplica YAGNI: se implementa lo que la especificación vigente exige, nada más. Toda dependencia
nueva de terceros MUST justificarse en el PR frente a la alternativa de la biblioteca estándar,
y toda capa de abstracción MUST tener al menos dos consumidores reales antes de introducirse.
El contenido del portafolio (proyectos, experiencia, artículos) MUST vivir como datos
estructurados y validados por esquema, separado del código de presentación, de modo que
actualizar el portafolio no requiera modificar lógica.

Rationale: un portafolio se actualiza a menudo y se mantiene una persona sola; cada abstracción
prematura es deuda que se paga en cada actualización.

## Restricciones Tecnológicas (Python)

- Lenguaje: Python 3.12 o superior, exclusivamente. Las funcionalidades del portafolio MUST
  implementarse en Python; JavaScript se limita a mejora progresiva del cliente y MUST NOT ser
  requisito para leer el contenido.
- Gestión de dependencias reproducible con `uv` (o `poetry`) y archivo de bloqueo commiteado;
  las versiones MUST estar fijadas.
- Herramientas obligatorias del proyecto: `pytest` (+ `pytest-cov`, `pytest-benchmark`), `ruff`,
  `mypy`, y `pre-commit` con los mismos comandos que ejecuta CI.
- Estructura: paquete de aplicación bajo `src/`, pruebas bajo `tests/` en espejo del paquete.
  MUST NOT existir lógica de negocio fuera del paquete.
- Elecciones abiertas al plan de cada funcionalidad (framework web, generador estático, capa de
  persistencia, plataforma de despliegue): se deciden en `/speckit-plan` y MUST cumplir todos
  los presupuestos del Principio IV para ser aceptables.

## Flujo de Desarrollo y Puertas de Calidad

1. Todo cambio parte de una especificación y un plan (`/speckit-specify` → `/speckit-plan` →
   `/speckit-tasks`); no se implementa contra un requisito no escrito.
2. El trabajo ocurre en ramas por funcionalidad. Prohibido el push directo a la rama principal.
3. CI MUST ejecutar, en este orden y como bloqueantes: `ruff format --check` → `ruff check` →
   `mypy --strict` → `pytest` con umbral de cobertura → auditoría de rendimiento contra los
   presupuestos del Principio IV.
4. Un PR MUST NOT fusionarse con CI en rojo. MUST NOT usarse `--no-verify` ni omitirse puertas
   de CI; una puerta rota se arregla, no se rodea.
5. La descripción de cada PR MUST declarar qué principios toca y, si introduce complejidad,
   por qué la alternativa simple es insuficiente.
6. La rama principal MUST permanecer desplegable en todo momento.

## Governance

Esta constitución prevalece sobre cualquier otra práctica, preferencia o costumbre del
repositorio. Ante conflicto entre este documento y cualquier guía, plantilla o configuración,
gana este documento y la otra fuente se corrige.

**Procedimiento de enmienda**: toda modificación se propone en un PR dedicado que MUST incluir
(a) el texto exacto que cambia, (b) la justificación, (c) el impacto sobre plantillas y flujos
dependientes, y (d) el plan de migración para el código que dejaría de cumplir. La enmienda entra
en vigor al fusionarse.

**Política de versionado** (semántico sobre la gobernanza, no sobre el producto):

- MAJOR: se elimina o redefine un principio de forma incompatible con el texto anterior.
- MINOR: se añade un principio o sección nueva, o se amplía materialmente una guía existente.
- PATCH: aclaraciones, redacción, correcciones tipográficas y refinamientos no semánticos.

**Revisión de cumplimiento**: toda revisión de código MUST verificar el cumplimiento de los cinco
principios; el revisor deja constancia explícita. Los umbrales numéricos (cobertura, presupuestos
de rendimiento) se revisan al cerrar cada funcionalidad y solo se relajan mediante enmienda con
justificación registrada. Cualquier desviación aceptada MUST documentarse en el PR con fecha y
condición de eliminación.

**Version**: 1.0.0 | **Ratified**: 2026-09-02 | **Last Amended**: 2026-09-02
