# Feature Specification: Portafolio Personal

**Feature Branch**: `001-portafolio-personal`

**Created**: 2026-09-02

**Status**: Ready for planning

**Input**: User description: "Crear un portafolio para mi persona en python que sea desplegable en vercel. Si tienes alguna duda para mejorar tu contexto puedes hacermela."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Evaluación rápida del perfil por un reclutador (Priority: P1)

Una persona que evalúa candidatos (reclutador, hiring manager o cliente potencial) llega al
portafolio desde un enlace en LinkedIn, un CV o un correo. En menos de dos minutos necesita
responder tres preguntas: quién es esta persona, qué sabe hacer, y dónde puedo seguir su rastro
profesional. Ve una presentación breve, un resumen de capacidades, una selección de trabajos
destacados, la descarga del CV y los enlaces a sus perfiles profesionales externos, sin tener que
navegar a ninguna otra página.

**Why this priority**: es el 80% del tráfico real de un portafolio y el único recorrido cuyo
fracaso invalida el producto completo. Entregado en solitario, ya cumple el propósito del
portafolio; el resto son mejoras.

**Independent Test**: se puede probar íntegramente cargando la página principal en un dispositivo
móvil y de escritorio y verificando que nombre, titular profesional, resumen, capacidades,
trabajos destacados, acceso al CV y enlaces a perfiles externos son visibles y utilizables sin
navegar fuera de esa página.

**Acceptance Scenarios**:

1. **Given** un visitante que nunca ha visto el sitio, **When** abre la página principal,
   **Then** ve el nombre, el titular profesional y un resumen de una a tres frases dentro de la
   primera pantalla, sin desplazarse.
2. **Given** un visitante en la página principal, **When** se desplaza por la página, **Then**
   encuentra al menos tres trabajos destacados, cada uno con título, descripción de una línea y
   las tecnologías o disciplinas aplicadas.
3. **Given** un visitante que quiere el CV, **When** activa la acción de descarga, **Then**
   obtiene un documento en un formato portátil de uso universal en menos de 3 segundos.
4. **Given** un visitante que quiere verificar la trayectoria, **When** activa un enlace a un
   perfil profesional externo, **Then** el destino se abre sin descartar la sesión del portafolio.
5. **Given** un visitante con lector de pantalla, **When** recorre la página principal, **Then**
   la jerarquía de encabezados es correcta y todo elemento no textual tiene alternativa textual.
6. **Given** un visitante con las capacidades de scripting del navegador deshabilitadas,
   **When** abre la página principal, **Then** todo el contenido informativo sigue siendo legible
   y los enlaces siguen funcionando.

---

### User Story 2 - Exploración en profundidad de un trabajo (Priority: P2)

Un visitante interesado por un trabajo destacado quiere entender qué se construyó, qué problema
resolvía, qué decisiones se tomaron y cuál fue el resultado. Abre la ficha del trabajo y encuentra
una descripción estructurada con contexto, rol desempeñado, decisiones relevantes, resultado
medible y enlaces al código o a la versión publicada cuando existan.

**Why this priority**: convierte una impresión favorable en credibilidad demostrada. Depende de
que exista la página principal (P1), pero es la diferencia entre una lista de nombres y una prueba
de criterio profesional.

**Independent Test**: se puede probar abriendo la ficha de cada trabajo mediante su enlace directo
y verificando que muestra contexto, rol, decisiones, resultado y enlaces externos, y que el
enlace directo funciona sin haber pasado antes por la página principal.

**Acceptance Scenarios**:

1. **Given** un visitante en la página principal, **When** activa un trabajo destacado, **Then**
   llega a su ficha detallada con el contenido completo de ese trabajo.
2. **Given** un enlace directo a la ficha de un trabajo compartido por un tercero, **When** se
   abre en una sesión nueva, **Then** la ficha carga correctamente y ofrece navegación de vuelta
   al índice de trabajos.
3. **Given** una ficha de trabajo con enlace a código o versión publicada, **When** el visitante
   lo activa, **Then** el destino se abre en una pestaña nueva sin perder el portafolio.
4. **Given** un enlace a un trabajo inexistente o retirado, **When** se abre, **Then** el sitio
   muestra una página de error comprensible con rutas de navegación hacia el contenido existente,
   en lugar de un error técnico.

---

### User Story 3 - Actualización de contenido por el propietario (Priority: P3)

El propietario del portafolio añade un trabajo nuevo, actualiza su experiencia o corrige un dato.
Modifica el contenido en su representación estructurada, verifica el resultado en una vista previa
y publica, sin necesidad de alterar la lógica ni el diseño del sitio.

**Why this priority**: determina si el portafolio sigue vivo a los seis meses. No bloquea el
lanzamiento, pero su ausencia garantiza el abandono del sitio.

**Independent Test**: se puede probar añadiendo una entrada de contenido nueva y comprobando que
aparece publicada y correctamente enlazada sin haber modificado ningún archivo de lógica o de
presentación.

**Acceptance Scenarios**:

1. **Given** el propietario con una entrada de contenido nueva, **When** la añade a la fuente de
   contenido estructurado, **Then** aparece en el sitio publicado sin cambios en la lógica.
2. **Given** una entrada de contenido con campos obligatorios ausentes o de tipo incorrecto,
   **When** se intenta publicar, **Then** la publicación se detiene con un error que identifica la
   entrada y el campo defectuoso.
3. **Given** un cambio de contenido publicado, **When** un visitante recarga el sitio, **Then**
   ve la versión actualizada sin acciones manuales de limpieza de caché.

---

### Edge Cases

- **Sin contenido**: ¿qué muestra cada sección cuando aún no hay trabajos o experiencia cargados?
  El sitio debe presentar un estado vacío intencional, nunca una sección rota o vacía sin
  explicación.
- **Volumen alto**: ¿qué ocurre cuando el número de trabajos supera lo que cabe razonablemente en
  una página? Debe existir un criterio explícito de selección de destacados y un índice completo.
- **Recurso ausente**: ¿cómo se comporta el sitio si una imagen, el documento de CV o un enlace
  externo no está disponible?
- **Enlace roto o antiguo**: ¿qué ve un visitante que llega desde un enlace a una dirección que ya
  no existe? Debe recibir una página de error útil, no un fallo técnico.
- **Red lenta**: ¿el contenido es legible en una conexión móvil degradada antes de que terminen de
  cargar imágenes y recursos secundarios?
- **Accesibilidad**: ¿es el sitio operable únicamente con teclado y comprensible con lector de
  pantalla, incluida la navegación entre secciones y fichas?
- **Preferencias del visitante**: ¿respeta el sitio las preferencias del sistema de tema (claro y
  oscuro) y de reducción de movimiento?
- **Compartición social**: ¿qué se muestra al pegar un enlace del portafolio en una red social o
  un mensajero? Debe generar una vista previa con título, descripción e imagen correctos.
- **Impresión**: ¿es legible el contenido si un reclutador imprime la página o la guarda como
  documento?

## Requirements *(mandatory)*

### Functional Requirements

#### Identidad y presentación

- **FR-001**: El sistema MUST mostrar en la página principal el nombre completo del propietario,
  su titular profesional y un resumen personal de entre 1 y 3 frases.
- **FR-002**: El sistema MUST mostrar un conjunto de capacidades profesionales agrupadas por
  categoría, cada una identificable de forma individual.
- **FR-003**: El sistema MUST mostrar el historial de experiencia profesional en orden cronológico
  inverso, con organización, rol, periodo y descripción de responsabilidades o logros.
- **FR-004**: El sistema MUST ofrecer al visitante la obtención del CV del propietario como
  documento descargable en un formato portátil de uso universal.
- **FR-005**: El sistema MUST enlazar a los perfiles profesionales externos del propietario, de
  forma alcanzable desde cualquier página del sitio, y cada enlace externo MUST abrirse sin
  descartar la sesión de navegación del portafolio.
- **FR-006**: El sistema MUST NOT incluir formularios, canales de mensajería ni ninguna otra
  sección de contacto; los enlaces a perfiles externos de FR-005 son la única vía de contacto
  ofrecida.

#### Trabajos y contenido

- **FR-007**: El sistema MUST presentar en la página principal una selección de trabajos
  destacados, cada uno con título, descripción breve y las tecnologías o disciplinas aplicadas.
- **FR-008**: El sistema MUST ofrecer una ficha individual por trabajo, accesible mediante una
  dirección estable y compartible, con contexto, rol desempeñado, decisiones relevantes, resultado
  y enlaces externos cuando existan.
- **FR-009**: El sistema MUST permitir marcar un trabajo como destacado o no destacado, y MUST
  respetar un orden de presentación definido explícitamente por el propietario.
- **FR-010**: El sistema MUST presentar cada sección en un estado vacío explicativo cuando no
  exista contenido para ella, en lugar de omitirla silenciosamente o mostrarla incompleta.

#### Contenido gestionable

- **FR-011**: El sistema MUST mantener todo el contenido del portafolio en una representación
  estructurada e independiente de la presentación, de modo que actualizarlo no exija modificar la
  lógica del sitio.
- **FR-012**: El sistema MUST validar la estructura y los tipos de todo el contenido antes de
  publicarlo, y MUST detener la publicación identificando la entrada y el campo defectuoso cuando
  la validación falle.

#### Idioma, accesibilidad y calidad de la experiencia

- **FR-013**: El sistema MUST presentar todo el contenido y toda la interfaz en español, y MUST
  declarar el idioma del documento de forma que los lectores de pantalla lo pronuncien
  correctamente.
- **FR-014**: El sistema MUST ser completamente operable mediante teclado y MUST cumplir el nivel
  AA de las pautas de accesibilidad para contenido web vigentes.
- **FR-015**: El sistema MUST adaptar su presentación a pantallas desde 320 px de ancho hasta
  escritorio, sin desplazamiento horizontal ni pérdida de contenido.
- **FR-016**: El sistema MUST respetar las preferencias del sistema del visitante en cuanto a tema
  claro u oscuro y a reducción de movimiento.
- **FR-017**: El sistema MUST mantener todo el contenido informativo legible y todos los enlaces
  operativos cuando las capacidades de scripting del navegador estén deshabilitadas.
- **FR-018**: El sistema MUST responder a una dirección inexistente con una página de error
  comprensible que ofrezca rutas de navegación hacia el contenido existente.

#### Difusión

- **FR-019**: El sistema MUST proporcionar, para cada página compartible, los metadatos de título,
  descripción e imagen de vista previa que emplean redes sociales y mensajeros.
- **FR-020**: El sistema MUST exponer la información necesaria para que los buscadores indexen el
  portafolio, incluido un índice de las direcciones públicas del sitio.
- **FR-021**: El sistema MUST NOT recopilar datos personales del visitante ni emplear seguimiento
  publicitario de terceros.

### Key Entities

- **Perfil**: la identidad profesional del propietario. Atributos: nombre completo, titular
  profesional, resumen, ubicación, disponibilidad, imagen de retrato, enlaces a perfiles externos
  y referencia al documento de CV. Es único en el sistema.
- **Trabajo**: una pieza de trabajo demostrable. Atributos: título, identificador estable para su
  dirección, descripción breve, descripción extensa, problema abordado, rol desempeñado, periodo,
  resultado, indicador de destacado, orden de presentación, imágenes y enlaces externos. Se
  relaciona con Capacidad (las que aplica).
- **Experiencia**: un periodo de actividad profesional o formativa. Atributos: organización, rol,
  fecha de inicio, fecha de fin o indicador de actualidad, ubicación, descripción y logros. Se
  ordena cronológicamente de forma inversa.
- **Capacidad**: una habilidad o tecnología que el propietario declara dominar. Atributos: nombre,
  categoría y nivel de dominio. Se relaciona con Trabajo y con Experiencia.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un visitante que ve el portafolio por primera vez puede identificar quién es el
  propietario, qué hace y dónde consultar su trayectoria completa en menos de 30 segundos desde la
  carga de la página principal.
- **SC-002**: El contenido principal de cualquier página resulta legible en menos de 2,5 segundos
  sobre una conexión móvil de gama media, medido en una simulación reproducible.
- **SC-003**: El 100% de las páginas públicas alcanza al menos 95 sobre 100 en las auditorías
  automatizadas de accesibilidad y de buenas prácticas web, sin errores de nivel AA pendientes.
- **SC-004**: Un visitante que usa exclusivamente el teclado puede alcanzar y activar todos los
  elementos interactivos del sitio sin quedar atrapado en ningún punto.
- **SC-005**: El propietario puede publicar un trabajo nuevo completo en menos de 10 minutos y sin
  modificar ningún archivo de lógica o de presentación.
- **SC-006**: El 100% de las direcciones públicas del sitio responde correctamente; ninguna
  devuelve un fallo técnico, y las direcciones inexistentes devuelven la página de error prevista.
- **SC-007**: Un enlace a cualquier página del portafolio, pegado en una red social o mensajero,
  genera una vista previa con título, descripción e imagen correctos en el 100% de los casos.
- **SC-008**: El sitio se muestra sin desplazamiento horizontal ni pérdida de contenido en anchos
  de pantalla desde 320 px hasta 2560 px.
- **SC-009**: El sitio no realiza ninguna petición a servicios de seguimiento publicitario de
  terceros ni almacena datos del visitante, verificable en la traza de red de una visita completa.
- **SC-010**: El 100% del contenido y de los textos de interfaz publicados está en español, sin
  cadenas sin traducir ni residuos en otro idioma.

## Assumptions

- **Contenido**: el propietario aporta el contenido real (datos de perfil, trabajos, experiencia,
  documento de CV e imágenes). El alcance de esta funcionalidad cubre la estructura, la validación
  y la presentación de ese contenido, no su redacción. A la fecha de esta especificación, los
  datos de identidad del propietario aún no se han facilitado y son un requisito previo a la
  implementación, no a la planificación.
- **Audiencia**: el público objetivo son reclutadores, responsables de contratación y clientes
  potenciales hispanohablantes; se asume tráfico mayoritariamente móvil y sesiones breves.
- **Escala**: se asume un volumen del orden de decenas de visitas diarias y menos de cien entradas
  de contenido en total. No se diseña para tráfico masivo ni para múltiples autores.
- **Sin sección de contacto** (decisión del propietario): no hay formulario, ni recepción de
  mensajes, ni entrega de correo, ni protección antiabuso, ni almacenamiento de datos de
  visitantes. El contacto ocurre fuera del sitio, a través de los perfiles profesionales externos
  enlazados en FR-005. Esta decisión permite que el portafolio sea de solo lectura de principio a
  fin y elimina toda dependencia de servicios externos de envío.
- **Monolingüe en español** (decisión del propietario): el modelo de contenido almacena un único
  valor por campo de texto. Añadir un segundo idioma más adelante exigiría rediseñar el modelo de
  contenido y las direcciones del sitio; se acepta ese coste futuro a cambio de simplicidad ahora.
- **Sin artículos ni blog** (decisión del propietario): no existe entidad de publicación escrita,
  ni listado, ni sindicación. Incorporarlo más adelante es aditivo y no invalida el modelo actual.
- **Sin cuentas de usuario**: el portafolio es de solo lectura para el público. No existen
  registro, inicio de sesión, roles ni área privada.
- **Sin panel de administración**: la gestión de contenido ocurre sobre la fuente de contenido
  estructurado y su flujo de publicación, no mediante una interfaz de administración en el sitio.
- **Analítica**: no se incorpora medición de audiencia; de hacerlo en el futuro, deberá ser
  agregada y sin identificación personal, coherente con FR-021.
- **Dominio**: se asume la disponibilidad de un dominio propio para la publicación; su compra y
  configuración quedan fuera del alcance de esta especificación.
- **Restricciones técnicas ya decididas**: el propietario ha fijado el lenguaje de implementación
  y la plataforma de publicación. Estas decisiones se documentan y se justifican en el plan
  técnico, no en esta especificación, y quedan sujetas a los presupuestos de rendimiento y a los
  estándares de calidad y pruebas de la constitución del proyecto.
