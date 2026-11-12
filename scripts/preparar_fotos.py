#!/usr/bin/env python3
"""Prepara las fotos para publicar.

- Corrige la orientación, reduce (lado mayor 1600 px, JPEG calidad 80) y crea una miniatura (480 px).
- NO copia los metadatos EXIF: así los archivos publicados no llevan GPS.
- Une cada foto con datos/inventario_fotos.csv y agrupa las tomas consecutivas (misma cámara,
  menos de GAP segundos entre una y otra) como "una misma planta" de forma preliminar.
- Escribe src/data/fotos.json, que usan el mapa y la página "Por identificar".

Uso:
    python scripts/preparar_fotos.py "RUTA/A/LOS/ORIGINALES"
Si una foto ya fue asignada a una especie, se conserva en datos/asignaciones.csv
(columnas: archivo,especie,parte,taxon,rango,confianza). El script la toma de ahí.
"""
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
GAP = 90  # segundos entre fotos de una misma planta
GRANDE, MINI = 1600, 480

def reducir(img, lado):
    copia = img.copy()
    copia.thumbnail((lado, lado), Image.LANCZOS)
    return copia

def main(origen: Path):
    out_g = RAIZ / "public" / "fotos" / "grande"
    out_m = RAIZ / "public" / "fotos" / "mini"
    out_g.mkdir(parents=True, exist_ok=True)
    out_m.mkdir(parents=True, exist_ok=True)

    with open(RAIZ / "datos" / "inventario_fotos.csv", encoding="utf-8-sig") as f:
        filas = list(csv.DictReader(f))

    asign = {}
    ruta_asign = RAIZ / "datos" / "asignaciones.csv"
    if ruta_asign.exists():
        with open(ruta_asign, encoding="utf-8-sig") as f:
            asign = {r["archivo"]: r for r in csv.DictReader(f)}  # claves sin .jpg

    fotos = []
    for fila in sorted(filas, key=lambda r: (r["camara"], r["fecha_hora"])):
        src = origen / fila["archivo"]
        if not src.exists():
            print("falta:", src)
            continue
        stem = src.stem
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            ancho, alto = im.size
            reducir(im, GRANDE).save(out_g / f"{stem}.jpg", "JPEG", quality=80, optimize=True, progressive=True)
            reducir(im, MINI).save(out_m / f"{stem}.jpg", "JPEG", quality=75, optimize=True)
        a = asign.get(stem, {})
        fotos.append({
            "id": stem,
            "fecha": datetime.strptime(fila["fecha_hora"], "%Y:%m:%d %H:%M:%S").isoformat(),
            "lat": float(fila["lat"]) if fila["lat"] else None,
            "lon": float(fila["lon"]) if fila["lon"] else None,
            "camara": fila["camara"],
            "especie": a.get("especie") or None,
            "parte": a.get("parte") or None,
            "taxon": a.get("taxon") or None,
            "rango": a.get("rango") or None,
            "confianza": a.get("confianza") or None,
        })

    # Agrupar tomas consecutivas
    grupo, previo = 0, None
    for foto in fotos:
        t = datetime.fromisoformat(foto["fecha"])
        if previo is None or previo[0] != foto["camara"] or (t - previo[1]).total_seconds() > GAP:
            grupo += 1
        foto["grupo"] = grupo
        previo = (foto["camara"], t)

    fotos.sort(key=lambda f: f["fecha"])
    destino = RAIZ / "src" / "data" / "fotos.json"
    destino.write_text(json.dumps(fotos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(fotos)} fotos, {grupo} grupos, {sum(1 for f in fotos if f['lat'])} con GPS -> {destino}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(Path(sys.argv[1]))
