"""Importa los abstracts en PDF de la carpeta Abstract/ (no versionada).

Cada PDF se llama "<posición>. <Autor>.pdf" y contiene en su texto "Mesa 0N", la sección
"Resumen", "Palabras clave:" y "Sobre el/la ponente principal". El script:
- copia cada PDF a abstracts/mesaN-PP-autor.pdf (nombres sin acentos ni espacios),
- une los 16 en abstracts/IX-Simposio-DPIP-2026-abstracts.pdf,
- escribe abstracts/abstracts.json (resumen, palabras clave, bio y archivo por código de ponencia),
  que tools/ajustes_editoriales.py inyecta en la sección de ponencias de index.html.

Uso: pip install pypdf && python tools/importar_abstracts.py
"""
import glob
import json
import os
import re
import shutil
import unicodedata

import pypdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "Abstract")
OUT = os.path.join(ROOT, "abstracts")
mesas = json.loads(re.search(r"window\.MESAS = (\[.*\]);", open(os.path.join(ROOT, "js/mesas.js"), encoding="utf-8").read(), re.S).group(1))


def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def clean(t):
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"(?<![\.\:;])\n(?!\n)", " ", t)
    t = re.sub(r" {2,}", " ", t)
    t = re.sub(r"\s*-\s(?=[a-záéíóú])", "", t)
    return t.strip()


os.makedirs(OUT, exist_ok=True)
out = {}
merged = pypdf.PdfWriter()
for f in sorted(glob.glob(os.path.join(SRC, "*.pdf"))):
    base = os.path.basename(f)
    pos = int(base.split(".")[0])
    reader = pypdf.PdfReader(f)
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    mesa = int(re.search(r"Mesa 0(\d)", text).group(1))
    paper = mesas[mesa - 1]["ponencias"][pos - 1]
    apellidos = [w for w in norm(paper["autor"]).split() if len(w) > 2]
    assert any(a in norm(base) for a in apellidos), (base, paper["autor"])
    res = re.search(r"\nResumen\s*\n(.*?)(?:\nPalabras clave\s*:?\s*(.*?))?\s*\n\s*Sobre (?:el|la) ponente", text, re.S)
    assert res, base
    abstract = clean(res.group(1))
    kw = res.group(2)
    keywords = [k.strip(" .;") for k in re.split(r"[;,]", clean(kw))] if kw else []
    keywords = [k for k in keywords if k]
    bio = re.search(r"Sobre (?:el|la) ponente principal\s*\*?\s*\n(.*)", text, re.S)
    bio = clean(bio.group(1)) if bio else ""
    fname = f"abstracts/mesa{mesa}-{pos:02d}-{norm(paper['autor']).replace(' ', '-')}.pdf"
    shutil.copyfile(f, os.path.join(ROOT, fname))
    for p in reader.pages:
        merged.add_page(p)
    out[paper["codigo"]] = {"mesa": mesa, "pos": pos, "autor": paper["autor"], "archivo": fname,
                            "resumen": abstract, "palabras_clave": keywords, "bio": bio}
    print(f"mesa{mesa} #{pos} {paper['autor']:30s} {len(abstract.split()):4d} palabras | kw={len(keywords)}")

merged.write(os.path.join(OUT, "IX-Simposio-DPIP-2026-abstracts.pdf"))
json.dump(out, open(os.path.join(OUT, "abstracts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out), "fichas importadas")
