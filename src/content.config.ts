import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const especies = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/especies' }),
  schema: z.object({
    nombre_cientifico: z.string(),
    autor_taxon: z.string().nullable().default(null),
    familia: z.string(),
    nombres_comunes: z.array(z.string()).min(1),
    habito: z.enum(['árbol', 'arbusto', 'hierba', 'enredadera', 'cactus', 'epífita']),
    origen: z.enum(['nativa', 'endémica', 'exótica', 'exótica naturalizada']),
    region_origen: z.string().nullable().default(null),
    ambiente: z.array(z.enum(['vía pública', 'jardín particular', 'monte', 'banquina', 'baldío'])).default([]),
    floracion: z.array(z.number().int().min(1).max(12)).default([]),
    color_flor: z.string().nullable().default(null),
    conservacion: z.string().nullable().default(null),
    confianza_id: z.enum(['confirmada', 'probable', 'a revisar']),
    identificado_por: z.string(),
    flora_argentina: z.string().url().nullable().default(null),
    inaturalist: z.string().url().nullable().default(null),
    // Sin fotos la ficha se publica igual, con un recuadro de "sin foto todavía".
    fotos: z
      .array(
        z.object({
          archivo: z.string(), // id de la foto, p. ej. "20200906_171147" (carpeta public/fotos)
          parte: z.enum(['planta entera', 'flor', 'fruto', 'hoja', 'corteza', 'sin especificar']),
          autor: z.string(),
          fecha: z.coerce.date(),
          principal: z.boolean().default(false),
        }),
      )
      .default([]),
  }),
});

export const collections = { especies };
