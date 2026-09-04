"""Genera los códigos QR de votación (uno por mesa) y el de resultados.

Uso:  python tools/generar_qr.py [URL_BASE]
Por defecto usa la URL de GitHub Pages del repositorio. Si el sitio se publica
en otro dominio, vuelve a ejecutarlo con la nueva URL base (con barra final).
Requiere: pip install segno
"""
import os
import sys

import segno

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://osvaldomanan.github.io/IX-Simposio-DPIP/"
if not BASE.endswith("/"):
    BASE += "/"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "qr")
os.makedirs(OUT, exist_ok=True)

INK = "#0e0c0c"

targets = {f"mesa-{n}": f"{BASE}votar.html?mesa={n}" for n in range(1, 5)}
targets["resultados"] = f"{BASE}resultados.html"

for name, url in targets.items():
    qr = segno.make(url, error="m")
    qr.save(os.path.join(OUT, f"{name}.svg"), scale=12, dark=INK, light=None, border=2, xmldecl=False, svgclass=None, lineclass=None)
    qr.save(os.path.join(OUT, f"{name}.png"), scale=24, dark=INK, light="#ffffff", border=3)
    print(f"{name}: {url}")

with open(os.path.join(OUT, "URLS.txt"), "w", encoding="utf-8") as fh:
    for name, url in targets.items():
        fh.write(f"{name}\t{url}\n")
