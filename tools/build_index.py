"""Construye index.html a partir del HTML exportado del sitio.

- Extrae las imágenes embebidas (base64) a assets/ y las referencia como archivos.
- Reemplaza la sección de votación por la versión con cuatro mesas (QR por mesa + resultados en vivo).
- Actualiza favicon, canonical y metadatos sociales a la URL de GitHub Pages.

Uso: python tools/build_index.py
"""
import base64
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "IX-Simposio-Anatomia-del-Presente.html")
OUT = os.path.join(ROOT, "index.html")
SITE = "https://osvaldomanan.github.io/IX-Simposio-DPIP/"

html = open(SRC, encoding="utf-8").read()

# ---------- 1. imágenes embebidas -> assets/ ----------
os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
paths = {}
start = html.find("const assets =")
end = html.find("};", start) + 2
assets_block = html[start:end]
for m in re.finditer(r'"(inline-asset:(\d+))":"data:([a-z/+\-.]+);base64,([A-Za-z0-9+/=]+)"', assets_block):
    token, n, mime, data = m.group(1), m.group(2), m.group(3), m.group(4)
    ext = mime.split("/")[1]
    fname = f"assets/img-{n}.{ext}"
    with open(os.path.join(ROOT, fname), "wb") as fh:
        fh.write(base64.b64decode(data))
    paths[token] = fname

# Optimización opcional (requiere Pillow): héroe a WebP, íconos a 256px.
try:
    from PIL import Image

    hero = os.path.join(ROOT, "assets/img-0.png")
    if os.path.exists(hero):
        im = Image.open(hero)
        im.save(os.path.join(ROOT, "assets/img-0.webp"), "WEBP", quality=82, method=6)
        paths["inline-asset:0"] = "assets/img-0.webp"
        og = Image.new("RGB", (1200, 630), "#0e0c0c")
        fit = im.convert("RGBA").copy()
        fit.thumbnail((1200, 630))
        og.paste(fit, ((1200 - fit.width) // 2, (630 - fit.height) // 2), fit)
        og.save(os.path.join(ROOT, "assets/og-simposio.jpg"), "JPEG", quality=85)
        os.remove(hero)
    for n in (2, 3, 4, 5):
        p = os.path.join(ROOT, f"assets/img-{n}.png")
        if os.path.exists(p):
            im = Image.open(p)
            if im.width > 256:
                im.thumbnail((256, 256))
                im.save(p, "PNG", optimize=True)
    # El QR antiguo del formulario de Google ya no se usa.
    old_qr = os.path.join(ROOT, "assets/img-6.png")
    if os.path.exists(old_qr):
        os.remove(old_qr)
except ImportError:
    print("Pillow no disponible: se conservan los PNG originales.")

html = html[:start] + "const assets = {};" + html[end:]
for token, fname in paths.items():
    html = html.replace(token, fname)

# ---------- 2. sección de votación ----------
mesas = json.loads(re.search(r"window\.MESAS = (\[.*\]);", open(os.path.join(ROOT, "js/mesas.js"), encoding="utf-8").read(), re.S).group(1))

def esc(v):
    return str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

cards = "".join(
    f'<a class="vote-qr vote-qr-mesa" href="votar.html?mesa={m["numero"]}" aria-label="Votar por la mejor ponencia de la Mesa {m["numero"]}: {esc(m["titulo"])}">'
    f'<span class="vote-qr-frame"><img src="qr/mesa-{m["numero"]}.svg" alt="Código QR para votar en la Mesa {m["numero"]}" width="300" height="300" loading="lazy" decoding="async"/></span>'
    f'<strong>Mesa {m["numero"]}</strong><small>{esc(m["titulo"])}</small>'
    f'<span class="vote-mesa-cta">Votar en esta mesa</span></a>'
    for m in mesas
)

ICON_VOTE = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M7 15v-4"></path><path d="M12 15V7"></path><path d="M17 15v-7"></path></svg>'
ICON_QR = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="5" height="5" x="3" y="3" rx="1"></rect><rect width="5" height="5" x="16" y="3" rx="1"></rect><rect width="5" height="5" x="3" y="16" rx="1"></rect><path d="M21 16h-3a2 2 0 0 0-2 2v3"></path><path d="M21 21v.01"></path><path d="M12 7v3a2 2 0 0 1-2 2H7"></path><path d="M3 12h.01"></path><path d="M12 3h.01"></path><path d="M12 16v.01"></path><path d="M16 12h1"></path><path d="M21 12v.01"></path><path d="M12 21v-1"></path></svg>'
ICON_CHECK = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><path d="m9 12 2 2 4-4"></path></svg>'

vote_section = (
    '<section class="vote-section section-shell" id="votacion">'
    '<div class="vote-card vote-card-mesas">'
    '<div class="vote-copy">'
    '<div class="section-status-line"><p class="eyebrow">06 · Participación</p><span class="upcoming-badge vote-live-badge"><span class="vote-live-dot" aria-hidden="true"></span>Votación en vivo</span></div>'
    '<h2>Vota por la mejor ponencia de cada mesa.</h2>'
    '<p>Cada mesa tiene su propio código QR. Escanéalo desde tu teléfono al término de las presentaciones o toca la tarjeta de la mesa para votar. Se admite un voto por mesa; la votación es anónima y considera la claridad expositiva, la solidez argumentativa y la contribución de la ponencia al debate.</p>'
    f'<div class="vote-actions"><a class="button button-light" href="resultados.html">{ICON_VOTE} Ver resultados en vivo</a>'
    f'<a class="button button-outline" href="qr.html">{ICON_QR} Hoja de códigos QR</a></div>'
    f'<p class="vote-result-note">{ICON_CHECK} Los resultados se actualizan en tiempo real y se darán a conocer en la conversación de cierre de la jornada.</p>'
    '</div>'
    f'<div class="vote-mesas-grid">{cards}</div>'
    '</div></section>'
)

sec_start = html.find('<section class="vote-section section-shell" id="votacion">')
sec_end = html.find("</section>", sec_start) + len("</section>")
assert sec_start > 0, "No se encontró la sección de votación"
html = html[:sec_start] + vote_section + html[sec_end:]

# ---------- 3. cabecera: favicon, canonical, og ----------
html = re.sub(r'<link rel="shortcut icon" href="[^"]*"/>', '<link rel="shortcut icon" href="favicon.svg"/>', html)
html = re.sub(r'<link rel="icon" href="[^"]*"/>', '<link rel="icon" href="favicon.svg" type="image/svg+xml"/>', html)
html = re.sub(r'<link rel="canonical" href="[^"]*"/>', f'<link rel="canonical" href="{SITE}"/>', html)
html = re.sub(r'<meta property="og:url" content="[^"]*"/>', f'<meta property="og:url" content="{SITE}"/>', html)
if os.path.exists(os.path.join(ROOT, "assets/og-simposio.jpg")):
    html = re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=")[^"]*(")', rf"\g<1>{SITE}assets/og-simposio.jpg\2", html)

extra_css = """
<style id="votacion-mesas">
.vote-card.vote-card-mesas{grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:clamp(36px,5vw,72px);align-items:start}
.vote-mesas-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.vote-qr.vote-qr-mesa{width:100%;max-width:none;justify-self:stretch;text-decoration:none;display:flex;flex-direction:column;padding:12px 12px 16px}
.vote-qr-mesa .vote-qr-frame{padding:0}
.vote-qr-mesa img{image-rendering:auto}
.vote-qr-mesa strong{font-size:20px;margin-top:12px}
.vote-qr-mesa small{min-height:2.8em;font-size:11.5px;line-height:1.4;margin-top:6px;color:#6f5b60}
.vote-mesa-cta{display:inline-block;margin-top:12px;font-size:10px;font-weight:900;letter-spacing:.14em;text-transform:uppercase;border-top:1px solid #0d090b30;padding-top:10px;color:#0e0c0c}
.vote-actions{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.vote-actions .button{margin-top:16px}
.button-outline{color:#fff;background:transparent;border-color:#ffffff8a}
.button-outline:hover{background:#ffffff14}
.vote-live-dot{width:7px;height:7px;border-radius:50%;background:#0e0c0c;display:inline-block;margin-right:8px;animation:votepulse 1.4s ease-in-out infinite}
@keyframes votepulse{0%,100%{opacity:1}50%{opacity:.3}}
@media (max-width:1100px){.vote-card.vote-card-mesas{grid-template-columns:1fr}}
@media (max-width:520px){.vote-mesas-grid{grid-template-columns:1fr}.vote-qr.vote-qr-mesa{max-width:320px;margin:0 auto}.vote-actions .button{width:100%}}
</style>
"""
html = html.replace("</head>", extra_css + "</head>", 1)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(html)
print(f"index.html: {os.path.getsize(OUT)/1024:.0f} KB")
for f in sorted(os.listdir(os.path.join(ROOT, "assets"))):
    print(" ", f, f"{os.path.getsize(os.path.join(ROOT, 'assets', f))/1024:.0f} KB")
