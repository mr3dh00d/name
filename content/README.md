# Contenido del portafolio

Todo lo que se ve en el sitio sale de este directorio. **Editar estos archivos no
exige tocar una sola línea de código**: esa es la promesa de la historia de
usuario P3, y hay una prueba que la verifica.

El formato completo, campo por campo, está en
[`specs/001-portafolio-personal/contracts/content-schema.md`](../specs/001-portafolio-personal/contracts/content-schema.md).
Las reglas de validación están en
[`data-model.md`](../specs/001-portafolio-personal/data-model.md).

## Qué hay aquí

| Archivo | Qué contiene |
|---------|--------------|
| `perfil.toml` | Tu identidad: nombre, titular, resumen, CV y enlaces a perfiles externos |
| `capacidades.toml` | Habilidades y tecnologías, agrupadas por categoría |
| `experiencia.toml` | Historial profesional, en cualquier orden: el sitio lo ordena solo |
| `trabajos/<slug>.toml` | Un archivo por trabajo. **El nombre del archivo es la dirección pública** |

## Añadir un trabajo

1. Copia un archivo existente de `trabajos/` con el nombre que quieras:
   `trabajos/mi-proyecto.toml`.
2. Cambia `slug` para que coincida con el nombre del archivo. Se publicará en
   `/trabajos/mi-proyecto`.
3. Rellena el resto de campos. Si usas `capacidades`, cada valor debe existir en
   `capacidades.toml`.
4. Si añades imágenes, colócalas en `public/img/` y anota su **ancho y alto
   reales**. Son obligatorios: sin ellos el navegador no puede reservar el
   espacio y la página salta al cargar.
5. Comprueba el resultado antes de publicar:

   ```bash
   uv run python scripts/build.py
   ```

## Si algo falla

El validador no publica contenido roto. Te dirá exactamente dónde está el
problema:

```
✗ El contenido no es válido. La publicación se detiene.

  archivo : content/trabajos/mi-proyecto.toml
  entrada : mi-proyecto
  campo   : titulo
  motivo  : Field required
```

Es el mismo comando que ejecuta el despliegue, así que si pasa aquí, pasa allí.

## Reglas que sorprenden, y por qué existen

- **Un campo mal escrito es un error, no se ignora.** Si escribes `titluo`, el
  validador lo dice. Sin esta regla, una errata te dejaría el campo vacío en el
  sitio publicado sin ningún aviso.
- **Toda imagen necesita `alt`.** No es burocracia: es lo único que lee alguien
  que usa un lector de pantalla.
- **El texto de un enlace debe entenderse aislado.** «aquí» o «ver más» se
  rechazan, porque un lector de pantalla puede listar los enlaces fuera de su
  párrafo.
- **Renombrar un archivo de trabajo rompe los enlaces existentes** a esa ficha.
  Es la consecuencia esperada de que la dirección salga del nombre del archivo.
- **Tu perfil necesita al menos un enlace externo.** Este portafolio no tiene
  formulario de contacto por decisión de diseño, así que esos enlaces son la
  única forma que tiene alguien de escribirte.
