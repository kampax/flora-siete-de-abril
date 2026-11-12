# Flora de Siete de Abril

Sitio estático (Astro) con el relevamiento fotográfico de la flora de Siete de Abril. Se publica en GitHub Pages.

## Desarrollo

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # genera dist/
```

## Agregar una especie

1. Crear `src/content/especies/genero-especie.md` copiando una ficha existente. Astro valida los campos al compilar (ver `src/content.config.ts`).
2. Asignar fotos: agregar al archivo `datos/asignaciones.csv` (`archivo,especie,parte`, p. ej. `20200906_171147,prosopis-alba,flor`) y volver a correr `scripts/preparar_fotos.py`. Después, listar las fotos en el bloque `fotos:` de la ficha.

## Preparar las fotos

Los originales **no** van al repositorio. El script reduce (1600 px y miniatura de 480 px), corrige la orientación, **elimina el GPS** y escribe `src/data/fotos.json`:

```bash
python scripts/preparar_fotos.py "RUTA/A/LOS/ORIGINALES"
```

Requiere Python 3 con Pillow. Las coordenadas viven solo en `datos/inventario_fotos.csv` y en `fotos.json`; el mapa las redondea (`PRECISION_MAPA` en `src/lib.ts`).

## Publicación

1. Crear el repositorio público en GitHub y subir esta carpeta a la rama `main`.
2. En *Settings → Pages*, elegir *Source: GitHub Actions*.
3. Cada push a `main` ejecuta `.github/workflows/deploy.yml`.

## Licencias

Código: MIT. Fotos: CC BY-NC 4.0 (pendiente de acuerdo con la autora).
