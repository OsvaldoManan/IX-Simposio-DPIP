"""Importa las fotografías de la carpeta Fotos-originales/ (no versionada; en Windows "Fotos" y "fotos" serían la misma carpeta) a fotos/ (versionada).

Nombre esperado: "NN Descripción.jpg" (el número ordena; la descripción es el pie de foto).
Genera para cada una: fotos/NN-slug.jpg (máx. 1600 px) y fotos/NN-slug-min.jpg (máx. 640 px),
y escribe fotos/fotos.json, que tools/ajustes_editoriales.py inserta en "Registro audiovisual".

Uso: pip install pillow && python tools/importar_fotos.py
"""
import glob
import json
import os
import re
import unicodedata

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "Fotos-originales")
OUT = os.path.join(ROOT, "fotos")
os.makedirs(OUT, exist_ok=True)


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


fotos = []
for f in sorted(glob.glob(os.path.join(SRC, "*.jp*g")) + glob.glob(os.path.join(SRC, "*.png"))):
    base = os.path.splitext(os.path.basename(f))[0]
    m = re.match(r"(\d+)\s*[-·.]?\s*(.*)", base)
    num, caption = (m.group(1), m.group(2).strip()) if m else ("00", base)
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    name = f"{int(num):02d}-{slug(caption)}"
    big = im.copy(); big.thumbnail((1600, 1600))
    big.save(os.path.join(OUT, name + ".jpg"), "JPEG", quality=84, optimize=True, progressive=True)
    small = im.copy(); small.thumbnail((640, 640))
    small.save(os.path.join(OUT, name + "-min.jpg"), "JPEG", quality=80, optimize=True)
    fotos.append({"archivo": f"fotos/{name}.jpg", "miniatura": f"fotos/{name}-min.jpg", "pie": caption,
                  "ancho": big.width, "alto": big.height})
    print(name, big.size)

json.dump(fotos, open(os.path.join(OUT, "fotos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(fotos), "fotografías")
