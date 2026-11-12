#!/usr/bin/env python3
"""Aplica las identificaciones de datos/identificaciones_comentarios.csv.

1. Une cada comentario con su foto local por fecha/hora (tolerancia 2 s, gana la más cercana).
2. Escribe datos/asignaciones.csv (lo lee preparar_fotos.py) y actualiza src/data/fotos.json.
3. Para las identificadas a nivel especie crea (o actualiza el bloque `fotos:` de) su ficha .md.
   Los datos taxonómicos de las fichas nuevas están en FICHAS y son PROVISORIOS: hay que
   verificarlos contra Flora Argentina.
"""
import csv, json, re
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FMT = "%Y:%m:%d %H:%M:%S"

# slug: (familia, nombres comunes, hábito, origen, región de origen)
FICHAS = {
    "Argemone subfusiformis": ("Papaveraceae", ["Cardo amarillo"], "hierba", "nativa", None),
    "Clematis montevidensis": ("Ranunculaceae", ["Barba de chivo"], "enredadera", "nativa", None),
    "Lepidium bonariense": ("Brassicaceae", ["Mastuerzo"], "hierba", "nativa", None),
    "Nerium oleander": ("Apocynaceae", ["Adelfa", "Laurel de jardín"], "arbusto", "exótica", "región mediterránea"),
    "Dunalia brachyacantha": ("Solanaceae", ["Perilla", "Sacha pera"], "arbusto", "nativa", None),
    "Lycium cestroides": ("Solanaceae", ["Lycium cestroides"], "arbusto", "nativa", None),
    "Eucharis candida": ("Amaryllidaceae", ["Cebolleta"], "hierba", "exótica", "Colombia y Ecuador"),
    "Dieffenbachia seguine": ("Araceae", ["Dieffenbachia", "Hoja de coche"], "hierba", "exótica", "América tropical"),
    "Saccharum spontaneum": ("Poaceae", ["Caña silvestre"], "hierba", "exótica naturalizada", "Asia"),
    "Cynophalla retusa": ("Capparaceae", ["Sacha poroto"], "arbusto", "nativa", None),
    "Plumbago auriculata": ("Plumbaginaceae", ["Plumbago"], "arbusto", "exótica", "sur de África"),
    "Asclepias curassavica": ("Apocynaceae", ["Asclepias"], "hierba", "nativa", None),
    "Phoenix canariensis": ("Arecaceae", ["Palmera canaria"], "árbol", "exótica", "Islas Canarias"),
    "Prosopis kuntzei": ("Fabaceae", ["Itín"], "árbol", "nativa", None),
    "Trichocereus terscheckii": ("Cactaceae", ["Cardón"], "cactus", "nativa", None),
    "Leonurus sibiricus": ("Lamiaceae", ["Leonurus"], "hierba", "exótica naturalizada", "Asia"),
}
slug = lambda t: t.lower().replace(" ", "-")


def main():
    inv = list(csv.DictReader(open(RAIZ / "datos/inventario_fotos.csv", encoding="utf-8-sig")))
    asign = {}
    for r in csv.DictReader(open(RAIZ / "datos/identificaciones_comentarios.csv", encoding="utf-8")):
        t = datetime.strptime(r["fecha_hora"], FMT)
        cand = sorted((abs((datetime.strptime(i["fecha_hora"], FMT) - t).total_seconds()), i["archivo"]) for i in inv)
        d, archivo = cand[0]
        assert d <= 2, (r, cand[0])
        asign[archivo[:-4]] = r

    # asignaciones.csv
    filas = []
    for id_, r in sorted(asign.items()):
        es_sp = r["rango"] == "especie" and r["taxon"] in FICHAS
        filas.append({"archivo": id_, "especie": slug(r["taxon"]) if es_sp else "", "parte": "",
                      "taxon": r["taxon"], "rango": r["rango"], "confianza": r["confianza"]})
    with open(RAIZ / "datos/asignaciones.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["archivo", "especie", "parte", "taxon", "rango", "confianza"])
        w.writeheader(); w.writerows(filas)

    # fotos.json
    ruta = RAIZ / "src/data/fotos.json"
    fotos = json.loads(ruta.read_text(encoding="utf-8"))
    por_id = {f["archivo"]: f for f in filas}
    for ft in fotos:
        a = por_id.get(ft["id"])
        ft["especie"] = a["especie"] or None if a else None
        ft["taxon"], ft["rango"], ft["confianza"] = (a["taxon"], a["rango"], a["confianza"]) if a else (None, None, None)
    ruta.write_text(json.dumps(fotos, ensure_ascii=False, indent=1), encoding="utf-8")

    # fichas
    dest = RAIZ / "src/content/especies"
    for taxon, (fam, comunes, habito, origen, region) in FICHAS.items():
        s = slug(taxon)
        mis = [f for f in fotos if f["especie"] == s]
        if not mis:
            continue
        bloque = "fotos:\n" + "".join(
            f'  - archivo: "{f["id"]}"\n    parte: "sin especificar"\n    autor: "Natalia Paz"\n'
            f'    fecha: {f["fecha"][:10]}\n    principal: {"true" if i == 0 else "false"}\n'
            for i, f in enumerate(mis))
        md = dest / f"{s}.md"
        conf = next(r["confianza"] for r in asign.values() if r["taxon"] == taxon)
        if md.exists():
            txt = md.read_text(encoding="utf-8")
            txt = re.sub(r"fotos:\n(?:  .*\n)+", "", txt)
            txt = txt.replace("\n---\n", "\n" + bloque + "---\n", 1)
        else:
            reg = f'region_origen: "{region}"\n' if region else ""
            txt = (f'---\nnombre_cientifico: "{taxon}"\nautor_taxon: null\nfamilia: "{fam}"\n'
                   f'nombres_comunes: {json.dumps(comunes, ensure_ascii=False)}\nhabito: "{habito}"\n'
                   f'origen: "{origen}"\n{reg}confianza_id: "{"probable" if conf != "confirmada" else "confirmada"}"\n'
                   f'identificado_por: "Comentarios del álbum (Dante Loto, Alfredo Grau, Carlos Navarro)"\n'
                   f'{bloque}---\n**Ficha provisoria.** Nombre tomado de los comentarios del álbum de Google Fotos. '
                   f'Familia, origen y nombres populares por verificar contra Flora Argentina.\n')
        md.write_text(txt, encoding="utf-8")
    print(len(asign), "fotos con identificación;", sum(1 for f in filas if f["especie"]), "a nivel especie")


if __name__ == "__main__":
    main()
