# Phase 1 — Data Model: Portafolio Personal

**Fecha**: 2026-09-02 · **Plan**: [plan.md](./plan.md) · **Origen**: entidades de [spec.md](./spec.md)

Cuatro entidades, todas de solo lectura en ejecución. Se cargan desde `content/` y se validan una vez
al arrancar la aplicación y de nuevo en el build (FR-012). No hay persistencia, ni escrituras, ni
transiciones de estado: el contenido solo cambia mediante un despliegue nuevo.

**Convención de tipos**: `str!` marca cadena obligatoria y no vacía tras recortar espacios. `date` es
una fecha ISO `YYYY-MM-DD`. `slug` es una cadena que cumple `^[a-z0-9]+(-[a-z0-9]+)*$`.

---

## Contenido (agregado raíz)

Objeto inmutable que resulta de cargar todo `content/`. Es lo único que las vistas consultan; no
existe acceso a disco después del arranque.

| Campo | Tipo | Regla |
|-------|------|-------|
| `perfil` | `Perfil` | Obligatorio. Exactamente uno |
| `capacidades` | `tuple[Capacidad, ...]` | Puede estar vacío (FR-010) |
| `experiencia` | `tuple[Experiencia, ...]` | Puede estar vacío. Ordenado por `fecha_inicio` descendente al cargar |
| `trabajos` | `tuple[Trabajo, ...]` | Puede estar vacío. Ordenado por `orden` ascendente y, a igualdad, por `titulo` |

**Invariantes del agregado** (se comprueban tras cargar todas las entidades, no dentro de cada una):

- **INV-01**: todo `slug` de `trabajos` es único. Un duplicado detiene la carga nombrando ambos
  archivos.
- **INV-02**: toda `capacidad` referida por un trabajo existe en `capacidades`. Una referencia
  colgante detiene la carga nombrando el trabajo y la capacidad ausente.
- **INV-03**: como máximo un elemento de `experiencia` tiene `actual = true` — se admite más de uno
  solo si sus periodos no se solapan; en caso contrario la carga se detiene.
- **INV-04**: `perfil.cv` y toda `imagen` referenciada apuntan a un archivo existente bajo `public/`.
  Una referencia rota detiene el build (cubre el caso límite «recurso ausente»).

---

## Perfil

Identidad profesional del propietario. Único en el sistema. Origen: `content/perfil.toml`.

| Campo | Tipo | Obligatorio | Reglas de validación | Requisito |
|-------|------|-------------|----------------------|-----------|
| `nombre` | `str!` | Sí | 2–80 caracteres | FR-001 |
| `titular` | `str!` | Sí | 2–120 caracteres | FR-001 |
| `resumen` | `str!` | Sí | 40–600 caracteres; entre 1 y 3 frases | FR-001 |
| `ubicacion` | `str` | No | ≤ 120 caracteres | — |
| `disponibilidad` | `str` | No | ≤ 120 caracteres | — |
| `retrato` | `str` | No | Ruta relativa dentro de `public/`; el archivo debe existir | — |
| `retrato_alt` | `str` | Condicional | **Obligatorio si hay `retrato`**; 5–160 caracteres | FR-014 |
| `cv` | `str!` | Sí | Ruta relativa dentro de `public/`; el archivo debe existir | FR-004 |
| `enlaces` | `tuple[EnlaceExterno, ...]` | Sí | Al menos 1; máximo 8 | FR-005 |
| `og_imagen` | `str` | No | Ruta dentro de `public/`; imagen por defecto de vista previa social | FR-019 |

**Nota de diseño**: `enlaces` exige al menos un elemento porque, con la sección de contacto descartada
(FR-006), estos enlaces son la **única** vía por la que un visitante puede alcanzar al propietario. Un
perfil sin ninguno produciría un portafolio sin salida, así que la ausencia se trata como error de
contenido, no como estado vacío admisible.

### EnlaceExterno (objeto embebido)

| Campo | Tipo | Obligatorio | Reglas |
|-------|------|-------------|--------|
| `etiqueta` | `str!` | Sí | 2–40 caracteres. Texto visible y descriptivo por sí solo; se rechaza «aquí», «enlace», «click» |
| `url` | `str!` | Sí | Debe ser `https://` absoluta |
| `tipo` | `str` | No | Uno de `linkedin`, `github`, `web`, `otro`. Por defecto `otro` |

---

## Trabajo

Una pieza de trabajo demostrable. Origen: un archivo por trabajo en `content/trabajos/<slug>.toml`.

| Campo | Tipo | Obligatorio | Reglas de validación | Requisito |
|-------|------|-------------|----------------------|-----------|
| `slug` | `slug` | Sí | Único en la colección (INV-01). Debe coincidir con el nombre del archivo | FR-008 |
| `titulo` | `str!` | Sí | 2–100 caracteres | FR-007 |
| `resumen` | `str!` | Sí | 20–200 caracteres. Es la «descripción de una línea» de la tarjeta | FR-007 |
| `problema` | `str!` | Sí | 40–1200 caracteres. Qué problema abordaba | FR-008 |
| `rol` | `str!` | Sí | 2–120 caracteres. Rol desempeñado | FR-008 |
| `decisiones` | `tuple[str!, ...]` | Sí | Entre 1 y 10 elementos, 20–500 caracteres cada uno | FR-008 |
| `resultado` | `str!` | Sí | 20–800 caracteres. Preferiblemente medible | FR-008 |
| `descripcion` | `str` | No | ≤ 4000 caracteres. Desarrollo largo opcional | FR-008 |
| `capacidades` | `tuple[str!, ...]` | Sí | Entre 1 y 12. Cada valor debe existir en `capacidades` (INV-02) | FR-007 |
| `fecha_inicio` | `date` | Sí | No posterior a `fecha_fin` cuando ambas existen | — |
| `fecha_fin` | `date` | No | Ausente significa en curso | — |
| `destacado` | `bool` | No | Por defecto `false` | FR-009 |
| `orden` | `int` | No | ≥ 0, por defecto 100. Menor valor se presenta antes | FR-009 |
| `imagenes` | `tuple[Imagen, ...]` | No | Máximo 8 | — |
| `enlaces` | `tuple[EnlaceExterno, ...]` | No | Máximo 6. Código o versión publicada | FR-008 |
| `og_imagen` | `str` | No | Ruta dentro de `public/`; si falta se usa la del perfil | FR-019 |

### Imagen (objeto embebido)

| Campo | Tipo | Obligatorio | Reglas |
|-------|------|-------------|--------|
| `ruta` | `str!` | Sí | Relativa dentro de `public/`; el archivo debe existir (INV-04) |
| `alt` | `str!` | Sí | 5–200 caracteres. **Sin excepción**: FR-014 y el escenario 5 de la historia P1 lo exigen |
| `ancho` | `int` | Sí | > 0. Necesario para reservar espacio y evitar desplazamiento de diseño (CLS < 0,1) |
| `alto` | `int` | Sí | > 0. Mismo motivo |

**Nota de diseño**: `ancho` y `alto` son obligatorios porque el presupuesto de CLS del Principio IV no
se puede cumplir de forma fiable si el navegador desconoce la proporción de la imagen antes de
descargarla. Es una regla de contenido con una razón de rendimiento medible detrás.

---

## Experiencia

Un periodo de actividad profesional o formativa. Origen: `content/experiencia.toml`, tabla `[[item]]`.

| Campo | Tipo | Obligatorio | Reglas de validación | Requisito |
|-------|------|-------------|----------------------|-----------|
| `organizacion` | `str!` | Sí | 2–120 caracteres | FR-003 |
| `rol` | `str!` | Sí | 2–120 caracteres | FR-003 |
| `fecha_inicio` | `date` | Sí | No futura | FR-003 |
| `fecha_fin` | `date` | Condicional | **Obligatoria salvo que `actual` sea `true`**. No anterior a `fecha_inicio` | FR-003 |
| `actual` | `bool` | No | Por defecto `false`. Si es `true`, `fecha_fin` debe estar ausente | FR-003 |
| `ubicacion` | `str` | No | ≤ 120 caracteres | — |
| `descripcion` | `str!` | Sí | 20–1200 caracteres | FR-003 |
| `logros` | `tuple[str!, ...]` | No | Máximo 8, 10–400 caracteres cada uno | FR-003 |

Orden de presentación: cronológico inverso por `fecha_inicio`. Los elementos con `actual = true`
encabezan la lista.

---

## Capacidad

Una habilidad o tecnología declarada. Origen: `content/capacidades.toml`, tabla `[[item]]`.

| Campo | Tipo | Obligatorio | Reglas de validación | Requisito |
|-------|------|-------------|----------------------|-----------|
| `nombre` | `str!` | Sí | 1–60 caracteres. Único en la colección | FR-002 |
| `categoria` | `str!` | Sí | 2–60 caracteres. Criterio de agrupación en la presentación | FR-002 |
| `nivel` | `str` | No | Uno de `basico`, `intermedio`, `avanzado`, `experto` | FR-002 |

Las capacidades se agrupan por `categoria` conservando el orden de aparición dentro de cada grupo.

---

## Reglas de validación transversales

| Regla | Alcance | Comportamiento ante fallo |
|-------|---------|---------------------------|
| Tipos y obligatoriedad declarados arriba | Toda entidad | Se detiene la carga indicando archivo, entrada y campo (FR-012) |
| Rutas de archivo bajo `public/` existentes | `retrato`, `cv`, `imagenes`, `og_imagen` | Se detiene el build (INV-04) |
| URLs externas absolutas y `https://` | Todo `EnlaceExterno` | Se detiene la carga |
| Texto de enlace descriptivo por sí solo | Todo `EnlaceExterno.etiqueta` | Se detiene la carga. Regla de accesibilidad (FR-014) |
| Alternativa textual presente en toda imagen | `Imagen.alt`, `retrato_alt` | Se detiene la carga. FR-014 |
| Unicidad de `slug` y de `nombre` de capacidad | Colecciones | Se detiene la carga nombrando ambas entradas en conflicto |
| Coherencia de fechas | `Trabajo`, `Experiencia` | Se detiene la carga |

**Error de validación** (`ContentValidationError`): expone `archivo`, `entrada`, `campo`, `motivo` y
`valor_recibido`. FR-012 exige identificar la entrada y el campo, así que estos datos forman parte del
contrato del error y se prueban, no son un detalle del mensaje.

---

## Estados vacíos (FR-010)

| Colección vacía | Comportamiento de la presentación |
|-----------------|-----------------------------------|
| `capacidades` | La sección se muestra con un texto explicativo, nunca se omite en silencio |
| `experiencia` | Ídem |
| `trabajos` | La sección de destacados y el índice muestran estado vacío explicativo; `/trabajos/<slug>` responde 404 para cualquier slug |
| `perfil` ausente o inválido | **No es un estado vacío**: es un error de contenido que detiene el arranque y el build |
