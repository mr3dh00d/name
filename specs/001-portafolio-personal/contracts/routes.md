# Contract — Rutas públicas

**Fecha**: 2026-09-02 · **Plan**: [../plan.md](../plan.md)

Cada ruta de este documento se traduce a un módulo de `tests/contract/`. El Principio II exige que
toda ruta pública tenga al menos una prueba de contrato que valide código de estado, forma de la
respuesta y comportamiento ante entrada inválida. **Estas pruebas se escriben antes que las vistas**
(Principio I).

## Invariantes comunes a toda respuesta HTML

Se verifican en un módulo compartido y se aplican a `/`, `/trabajos`, `/trabajos/<slug>` y a la
página de error.

| ID | Invariante | Requisito |
|----|------------|-----------|
| INV-H01 | `Content-Type: text/html; charset=utf-8` | — |
| INV-H02 | El elemento raíz declara `lang="es"` | FR-013 |
| INV-H03 | Exactamente un `<h1>`, y la jerarquía de encabezados no salta niveles | FR-014 |
| INV-H04 | Toda `<img>` tiene atributo `alt`, y `width` y `height` | FR-014, CLS |
| INV-H05 | Existen `<title>`, `<meta name="description">`, `og:title`, `og:description`, `og:image`, `og:url` y `twitter:card` | FR-019 |
| INV-H06 | Todo enlace externo lleva `rel="noopener noreferrer"` y `target="_blank"` | FR-005, escenario 3 de P2 |
| INV-H07 | El documento no referencia ningún archivo ni bloque de JavaScript | FR-017 |
| INV-H08 | El documento no contiene peticiones a dominios de seguimiento de terceros | FR-021 |
| INV-H09 | Los enlaces a perfiles externos del perfil están presentes en **todas** las páginas | FR-005 |
| INV-H10 | La respuesta lleva `Cache-Control` público con `s-maxage` y `stale-while-revalidate` | Principio IV |

---

## `GET /` — Página principal

**Requisitos cubiertos**: FR-001 a FR-005, FR-007, FR-010, FR-019 · **Historia**: P1

| Caso | Entrada | Respuesta esperada |
|------|---------|--------------------|
| Éxito | — | `200`, HTML, cumple todos los invariantes comunes |
| Identidad | — | El cuerpo contiene `perfil.nombre`, `perfil.titular` y `perfil.resumen` |
| Capacidades | Contenido con capacidades | Todas presentes, agrupadas por `categoria` |
| Experiencia | Contenido con experiencia | Presente en orden cronológico inverso |
| Trabajos destacados | Contenido con ≥ 1 destacado | Solo aparecen los de `destacado = true`, en orden `orden` ascendente; cada uno con título, resumen y capacidades |
| CV | — | Existe un enlace de descarga al `perfil.cv`, resoluble bajo `public/` |
| Estado vacío | Contenido sin capacidades / sin experiencia / sin trabajos | `200`; cada sección afectada muestra su texto de estado vacío y **no** desaparece |
| Método no admitido | `POST /` | `405` |

---

## `GET /trabajos` — Índice de trabajos

**Requisitos cubiertos**: FR-007, FR-009, FR-010 · **Historia**: P2

| Caso | Entrada | Respuesta esperada |
|------|---------|--------------------|
| Éxito | — | `200`, HTML, invariantes comunes |
| Completitud | Contenido con N trabajos | Aparecen los N, destacados y no destacados |
| Orden | Trabajos con distinto `orden` | Presentados por `orden` ascendente; a igualdad, por `titulo` |
| Enlaces | — | Cada elemento enlaza a `/trabajos/<slug>` con su slug exacto |
| Estado vacío | Sin trabajos | `200` con texto de estado vacío |
| Método no admitido | `POST` | `405` |

---

## `GET /trabajos/<slug>` — Ficha de un trabajo

**Requisitos cubiertos**: FR-008, FR-018, FR-019 · **Historia**: P2

| Caso | Entrada | Respuesta esperada |
|------|---------|--------------------|
| Éxito | `slug` existente | `200`, HTML, invariantes comunes |
| Contenido | `slug` existente | El cuerpo contiene `problema`, `rol`, todas las `decisiones` y `resultado` |
| Enlace directo | Petición sin `Referer` | `200`. La ficha no depende de haber visitado la página principal |
| Navegación de vuelta | — | Existe un enlace a `/trabajos` |
| Enlaces externos | Trabajo con enlaces | Cada uno cumple INV-H06 |
| Metadatos sociales | — | `og:title` es el título del trabajo, no el del sitio; `og:url` es la dirección canónica de la ficha |
| **Slug inexistente** | `slug` que no existe | `404` con la plantilla de error, **no** una traza técnica |
| **Slug malformado** | Slug con mayúsculas, espacios o caracteres de recorrido de rutas | `404`. Nunca `500`, nunca lectura fuera de `content/` |
| Método no admitido | `POST` | `405` |

---

## `GET /<cualquier-ruta-inexistente>` — Error 404

**Requisitos cubiertos**: FR-018 · **Caso límite**: enlace roto o antiguo

| Caso | Entrada | Respuesta esperada |
|------|---------|--------------------|
| Ruta desconocida | `/no-existe` | `404`, HTML, invariantes comunes |
| Utilidad | — | El cuerpo ofrece enlaces al inicio y al índice de trabajos |
| Sin fuga técnica | — | El cuerpo no contiene traza de pila, ni nombre de excepción, ni ruta del sistema de archivos |
| Caché | — | La respuesta de error **no** se cachea con la duración larga de las páginas válidas |

---

## `GET /sitemap.xml`

**Requisitos cubiertos**: FR-020

| Caso | Entrada | Respuesta esperada |
|------|---------|--------------------|
| Éxito | — | `200`, `Content-Type: application/xml`, XML bien formado |
| Completitud | — | Contiene `/`, `/trabajos` y una entrada por cada trabajo existente |
| Exclusión | — | **No** contiene la ruta de error ni ninguna dirección inexistente |
| Absolutas | — | Toda `<loc>` es una URL absoluta con el dominio configurado |

---

## `GET /robots.txt`

**Requisitos cubiertos**: FR-020

| Caso | Entrada | Respuesta esperada |
|------|---------|--------------------|
| Éxito | — | `200`, `Content-Type: text/plain` |
| Contenido | — | Permite la indexación y declara la dirección absoluta del sitemap |

---

## Activos servidos fuera de Flask

`public/**` lo sirve la CDN de la plataforma, no la aplicación. Por tanto **no** se prueban con el
cliente de Flask. Su verificación corresponde a:

- **INV-04 del modelo de datos**: toda ruta referenciada existe en `public/` en tiempo de build.
- **Pruebas extremo a extremo**: la hoja de estilos, el retrato y el CV se descargan con `200` en el
  despliegue de vista previa.

Este reparto es deliberado: una prueba que pidiera `/css/site.css` al cliente de Flask pasaría en
local y no diría nada sobre producción, donde esa ruta jamás llega a la aplicación.
