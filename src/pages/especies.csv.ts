import { getCollection } from 'astro:content';

const esc = (v: unknown) => `"${String(v ?? '').replaceAll('"', '""')}"`;

export async function GET() {
  const cols = ['nombre_cientifico', 'autor_taxon', 'familia', 'nombres_comunes', 'habito', 'origen', 'region_origen', 'color_flor', 'floracion', 'confianza_id', 'flora_argentina'];
  const filas = (await getCollection('especies'))
    .sort((a, b) => a.data.nombre_cientifico.localeCompare(b.data.nombre_cientifico))
    .map((e) => cols.map((c) => esc(Array.isArray((e.data as any)[c]) ? (e.data as any)[c].join('; ') : (e.data as any)[c])).join(','));
  // BOM para que Excel lea bien las tildes
  return new Response('﻿' + [cols.join(','), ...filas].join('\r\n'), {
    headers: { 'Content-Type': 'text/csv; charset=utf-8' },
  });
}
