# Contract — Formato de contenido editable

**Fecha**: 2026-09-02 · **Modelo**: [../data-model.md](../data-model.md)

Este es el contrato entre el propietario y la aplicación. Es la superficie que la historia de usuario
P3 promete estable: mientras un archivo cumpla este formato, publicarlo no exige tocar código.

Toda regla de validación vive en [`data-model.md`](../data-model.md). Aquí se fija **la forma de los
archivos**, que es lo que el propietario edita.

## Disposición

```text
content/
├── perfil.toml              # Exactamente uno. Obligatorio
├── capacidades.toml         # Uno. Puede tener cero entradas
├── experiencia.toml         # Uno. Puede tener cero entradas
└── trabajos/
    ├── <slug>.toml          # Un archivo por trabajo. El nombre del archivo ES el slug
    └── ...
```

El nombre del archivo de un trabajo determina su dirección pública: `content/trabajos/mi-proyecto.toml`
se publica en `/trabajos/mi-proyecto`. **Renombrar un archivo rompe los enlaces existentes** a esa
ficha; es la consecuencia esperada, y por eso el slug se valida contra el nombre del archivo en lugar
de derivarse del título.

## `content/perfil.toml`

```toml
nombre = "..."
titular = "..."
resumen = """..."""
ubicacion = "..."          # opcional
disponibilidad = "..."     # opcional
retrato = "img/retrato.jpg"        # opcional, relativo a public/
retrato_alt = "..."                # obligatorio si hay retrato
cv = "cv/cv.pdf"                   # relativo a public/
og_imagen = "og/inicio.png"        # opcional

[[enlaces]]                # al menos uno
etiqueta = "LinkedIn"
url = "https://..."
tipo = "linkedin"          # linkedin | github | web | otro
```

## `content/capacidades.toml`

```toml
[[item]]
nombre = "Python"
categoria = "Lenguajes"
nivel = "avanzado"         # opcional: basico | intermedio | avanzado | experto
```

## `content/experiencia.toml`

```toml
[[item]]
organizacion = "..."
rol = "..."
fecha_inicio = 2024-01-15
fecha_fin = 2025-06-30     # omitir si actual = true
actual = false
ubicacion = "..."          # opcional
descripcion = """..."""
logros = ["...", "..."]    # opcional
```

## `content/trabajos/<slug>.toml`

```toml
slug = "mi-proyecto"       # debe coincidir con el nombre del archivo
titulo = "..."
resumen = "..."            # una línea, es lo que se ve en la tarjeta
problema = """..."""
rol = "..."
decisiones = ["...", "..."]
resultado = """..."""
descripcion = """..."""    # opcional, desarrollo largo
capacidades = ["Python", "Flask"]   # deben existir en capacidades.toml
fecha_inicio = 2025-03-01
fecha_fin = 2025-09-30     # omitir si sigue en curso
destacado = true
orden = 10                 # menor valor, antes
og_imagen = "og/mi-proyecto.png"    # opcional

[[imagenes]]               # opcional
ruta = "img/trabajos/mi-proyecto-1.png"
alt = "..."                # obligatorio
ancho = 1280
alto = 720

[[enlaces]]                # opcional
etiqueta = "Código en GitHub"
url = "https://..."
tipo = "github"
```

## Garantías del contrato

| Garantía | Significado |
|----------|-------------|
| **Aditivo por defecto** | Añadir un archivo a `content/trabajos/` lo publica. No hay registro que actualizar |
| **Fallo ruidoso** | Un archivo que incumpla este formato detiene el build señalando archivo, entrada y campo. Nunca se publica a medias |
| **Campos desconocidos rechazados** | Un campo no declarado aquí es un error, no se ignora. Protege contra erratas silenciosas como `titluo` |
| **Sin presentación en los datos** | No se admite HTML ni marcado en los valores; el formato de presentación lo deciden las plantillas |
| **Sin datos en las plantillas** | Ningún texto de contenido vive en las plantillas, salvo los mensajes de interfaz y de estado vacío |
