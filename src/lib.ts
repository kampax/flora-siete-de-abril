import fotos from './data/fotos.json';

export const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

/** Enlace interno respetando el "base" de GitHub Pages. */
export const url = (ruta = '') => import.meta.env.BASE_URL + ruta.replace(/^\//, '');

/** Texto sin tildes ni mayúsculas, para buscar. */
export const normalizar = (s: string) =>
  s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

/**
 * Decimales de las coordenadas que se publican en el mapa.
 * 3 decimales ≈ 100 m (punto aproximado). 5 ≈ 1 m (punto exacto).
 * Pendiente de decidir (plan, sección 3.4): qué hacer con las plantas de casas particulares.
 */
export const PRECISION_MAPA = 3;

export type Foto = (typeof fotos)[number];
export const todasLasFotos: Foto[] = fotos;

export const fotoGrande = (id: string) => url(`fotos/grande/${id}.jpg`);
export const fotoMini = (id: string) => url(`fotos/mini/${id}.jpg`);

export function puntoPublico(f: { lat: number | null; lon: number | null }) {
  if (f.lat == null || f.lon == null) return null;
  const k = 10 ** PRECISION_MAPA;
  return [Math.round(f.lat * k) / k, Math.round(f.lon * k) / k] as [number, number];
}

export const slugDe = (id: string) => id.replace(/\.md$/, '');
