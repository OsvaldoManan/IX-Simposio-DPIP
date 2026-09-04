"""Ajustes editoriales sobre index.html (se aplican después de build_index.py).

1. Cronograma según "Cronograma preliminar - Simposio 2026.docx".
2. Se elimina la sección "El sentido del nombre".
3. Distinción visual entre invitados principales (Chernilo, Rovira, Bellolio) y moderaciones.
4. Cargo de Javiera Campos: candidata a doctora.
5. Estado de la votación (abierta/cerrada) controlado por js/config-votacion.js.
6. Sección de ponencias compacta y estática (sin columna fija ni centrado vertical).

Uso: python tools/ajustes_editoriales.py   (idempotente)
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "index.html")
html = open(OUT, encoding="utf-8").read()

if "<!-- ajustes-editoriales -->" in html:
    raise SystemExit("index.html ya tiene los ajustes aplicados; reconstruye con tools/build_index.py para reaplicar.")

# ---------------------------------------------------------------- 1. cronograma
MESAS_TIT = {
    1: "Desigualdad, bienestar y comportamiento político",
    2: "Inteligencia artificial, lenguaje y esfera pública",
    3: "Capitalismo, Estado y desigualdad",
    4: "Nación, territorio y orden político",
}
MESAS_HORA = {1: ("10:25", "11:45"), 2: ("11:45", "13:05"), 3: ("14:30", "15:50"), 4: ("16:05", "17:25")}

schedule = [
    {"time": "08:30", "end": "09:00", "title": "Acreditación", "type": "Recepción"},
    {"time": "09:00", "end": "09:15", "title": "Ceremonia de inauguración", "type": "Apertura"},
    {"time": "09:15", "end": "10:15", "title": "Conferencia inaugural · Daniel Chernilo", "type": "Magistral"},
    {"time": "10:15", "end": "10:25", "title": "Pausa", "type": "Pausa"},
    {"time": "10:25", "end": "11:45", "title": "Mesa 1 · " + MESAS_TIT[1], "type": "Mesa"},
    {"time": "11:45", "end": "13:05", "title": "Mesa 2 · " + MESAS_TIT[2], "type": "Mesa"},
    {"time": "13:05", "end": "14:30", "title": "Almuerzo", "type": "Pausa"},
    {"time": "14:30", "end": "15:50", "title": "Mesa 3 · " + MESAS_TIT[3], "type": "Mesa"},
    {"time": "15:50", "end": "16:05", "title": "Pausa café", "type": "Pausa"},
    {"time": "16:05", "end": "17:25", "title": "Mesa 4 · " + MESAS_TIT[4], "type": "Mesa"},
    {"time": "17:25", "end": "17:35", "title": "Pausa", "type": "Pausa"},
    {"time": "17:35", "end": "18:45", "title": "Panel de expertos · Populismo y democracia", "type": "Cierre"},
    {"time": "18:45", "end": "19:00", "title": "Ceremonia de clausura y premiación", "type": "Ceremonia"},
    {"time": "19:00", "end": "20:30", "title": "Cóctel de cierre (desde las 19:00)", "type": "Cierre"},
]

# Plantilla: primera fila existente (conserva el ícono de calendario).
m = re.search(r'<article class="schedule-row .*?</article>', html, re.S)
assert m, "No se encontró la primera fila del programa"
template = m.group(0)
template = re.sub(r'class="schedule-row [^"]*"', 'class="schedule-row __CLS__"', template)
template = re.sub(r'<span class="schedule-index">\d+</span>', '<span class="schedule-index">__IDX__</span>', template)
template = re.sub(r'<time>\d\d:\d\d<small>\d\d:\d\d</small></time>', '<time>__T1__<small>__T2__</small></time>', template)
template = re.sub(r'<div class="schedule-description"><span>[^<]*</span><h3>[^<]*</h3>', '<div class="schedule-description"><span>__TYPE__</span><h3>__TITLE__</h3>', template)
template = re.sub(r'aria-label="Agregar al calendario: [^"]*"', 'aria-label="Agregar al calendario: __TITLE__"', template)

def esc(v):
    return v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

rows = []
for i, it in enumerate(schedule, 1):
    cls = "schedule-" + it["type"].lower() + " schedule-state-scheduled"
    rows.append(template.replace("__CLS__", cls).replace("__IDX__", f"{i:02d}").replace("__T1__", it["time"])
                .replace("__T2__", it["end"]).replace("__TYPE__", esc(it["type"])).replace("__TITLE__", esc(it["title"])))
matches = list(re.finditer(r'<article class="schedule-row.*?</article>', html, re.S))
assert matches, "No hay filas de programa"
html = html[:matches[0].start()] + "".join(rows) + html[matches[-1].end():]

# Arreglo JS del programa (misma cantidad y orden que las filas).
html = re.sub(r"const schedule = \[.*?\];", "const schedule = " + json.dumps(schedule, ensure_ascii=False) + ";", html, count=1, flags=re.S)
html = html.replace('new Date("2026-09-24T08:45:00-03:00")', 'new Date("2026-09-24T08:30:00-03:00")')
html = html.replace('new Date("2026-09-24T18:30:00-03:00")', 'new Date("2026-09-24T20:30:00-03:00")')
html = html.replace('dateTime="2026-09-24T08:45:00-03:00">24 SEP 2026 · 08:45', 'dateTime="2026-09-24T08:30:00-03:00">24 SEP 2026 · 08:30')

# Invitados principales: etiquetas y horas.
html = html.replace("CONFERENCIA MAGISTRAL · 09:25", "CONFERENCIA INAUGURAL · 09:15")
html = html.replace("CONVERSACIÓN DE CIERRE · 17:15", "PANEL DE EXPERTOS · 17:35")
html = html.replace("Conferencia magistral · 09:25", "Conferencia inaugural · 09:15")
html = html.replace("Conversación de cierre · 17:15", "Panel de expertos · 17:35")
html = html.replace("La programación reúne una conferencia magistral, una conversación de cierre y cuatro moderaciones.",
                    "La programación reúne una conferencia inaugural, un panel de expertos de cierre y cuatro moderaciones de mesa.")
html = html.replace("Conferencia magistral</span>", "Conferencia inaugural</span>")

# Horarios de las mesas (encabezado de cada panel y arreglo JS de paneles).
OLD_HORA = {1: "10:45–11:55", 2: "12:05–13:15", 3: "14:25–15:35", 4: "15:55–17:05"}
for n, (a, b) in MESAS_HORA.items():
    html = html.replace(OLD_HORA[n], f"{a}–{b}")

# ---------------------------------------------------------------- enlace del botón "Compartir"
html = html.replace('url: "https://sitio-simposio.osvaldomanan-chile.chatgpt.site"', 'url: "https://osvaldomanan.github.io/IX-Simposio-DPIP/"')

# ---------------------------------------------------------------- 2. sección "El sentido del nombre"
i = html.find('<section class="questions section-shell" id="preguntas">')
if i > 0:
    j = html.find("</section>", i) + len("</section>")
    html = html[:i] + html[j:]

# ---------------------------------------------------------------- 4. Javiera Campos
html = html.replace("Magíster en Ciencia Política, doctoranda del DPIP, Escuela de Gobierno UAI.",
                    "Magíster en Ciencia Política, candidata a doctora del DPIP, Escuela de Gobierno UAI.")

# ---------------------------------------------------------------- 3. invitados principales vs. moderaciones
def marcar(card_html):
    if "Conferencia inaugural" in card_html or "Panel de expertos" in card_html:
        return card_html.replace('class="participant-card"', 'class="participant-card participant-keynote"', 1)
    return card_html.replace('class="participant-card"', 'class="participant-card participant-moderator"', 1)

html = re.sub(r'<article class="participant-card">.*?</article>', lambda mm: marcar(mm.group(0)), html, flags=re.S)
html = html.replace('<div class="participant-copy"><small>Conferencia inaugural · 09:15</small>',
                    '<div class="participant-copy"><small><b class="participant-role">Invitado principal</b>Conferencia inaugural · 09:15</small>')
html = html.replace('<div class="participant-copy"><small>Panel de expertos · 17:35</small>',
                    '<div class="participant-copy"><small><b class="participant-role">Invitado principal</b>Panel de expertos · 17:35</small>')
for n in (1, 2, 3, 4):
    html = html.replace(f'<div class="participant-copy"><small>Moderación · Mesa {n}</small>',
                        f'<div class="participant-copy"><small><b class="participant-role participant-role-mod">Moderación</b>Mesa {n} · {MESAS_HORA[n][0]}</small>')
leyenda = ('<div class="participants-legend" aria-label="Tipos de participación">'
           '<span><i class="legend-keynote"></i>Invitados principales: conferencia inaugural y panel de expertos</span>'
           '<span><i class="legend-mod"></i>Moderación de mesas</span></div>')
html = html.replace('<div class="participants-grid">', leyenda + '<div class="participants-grid">', 1)

# ---------------------------------------------------------------- 5. estado de la votación (index)
html = html.replace("</head>", '<script src="js/config-votacion.js"></script></head>', 1)
vote_js = """
<script>
(function () {
  if (window.VOTACION_HABILITADA !== false) return;
  var sec = document.getElementById("votacion");
  if (sec) {
    sec.classList.add("vote-closed");
    var badge = sec.querySelector(".vote-live-badge");
    if (badge) { badge.classList.remove("vote-live-badge"); badge.textContent = "Se habilita el 24 de septiembre"; }
    var note = sec.querySelector(".vote-result-note");
    if (note) note.lastChild.textContent = " La votación se abrirá durante la jornada, al término de cada mesa. Los códigos QR estarán activos ese día.";
    sec.querySelectorAll("a.vote-qr-mesa, a.button").forEach(function (a) {
      a.setAttribute("aria-disabled", "true");
      a.setAttribute("tabindex", "-1");
      a.addEventListener("click", function (e) { e.preventDefault(); });
    });
  }
  document.querySelectorAll('a[href="#votacion"]').forEach(function (a) {
    if (a.closest(".quick-nav")) return;
    a.classList.add("vote-nav-closed");
    a.setAttribute("aria-disabled", "true");
    a.title = "La votación se habilita el 24 de septiembre";
    a.addEventListener("click", function (e) { e.preventDefault(); });
  });
})();
</script>
"""
html = html.replace("</body>", vote_js + "</body>", 1)

css = """
<!-- ajustes-editoriales -->
<style id="ajustes-editoriales">
.participants-legend{display:flex;flex-wrap:wrap;gap:10px 26px;max-width:1320px;margin:0 auto 18px;font-size:10px;letter-spacing:.12em;text-transform:uppercase;font-weight:800;color:#ffffffb0}
.participants-legend span{display:inline-flex;align-items:center;gap:9px}
.participants-legend i{width:12px;height:12px;border-radius:50%;display:inline-block;border:1px solid var(--rose)}
.participants-legend .legend-keynote{background:var(--rose)}
.participant-role{display:block;margin-bottom:5px;font-size:8px;letter-spacing:.16em;color:var(--ink);background:var(--rose);padding:3px 7px;width:fit-content;border-radius:2px}
.participant-role-mod{color:#ffffffc9;background:transparent;border:1px solid #ffffff55}
.participant-card.participant-keynote{border-color:var(--rose);background:linear-gradient(160deg,#c2818d26,#ffffff09 55%)}
.participant-card.participant-keynote .participant-avatar{background:var(--rose);color:var(--ink);border-color:var(--rose);font-style:normal;font-weight:700}
.participant-card.participant-keynote:after{border-color:var(--rose)}
.participant-card.participant-keynote .participant-number{color:var(--rose)}
.participant-card.participant-moderator .participant-avatar{border-style:dashed;border-color:#ffffff8a;color:#fff}
.participant-card.participant-moderator .participant-copy>small{color:#ffffffb3}
.vote-closed .vote-qr-mesa{opacity:.55;filter:grayscale(1);cursor:not-allowed;pointer-events:none}
.vote-closed .vote-qr-mesa .vote-mesa-cta{text-decoration:line-through}
.vote-closed .vote-actions .button{opacity:.5;cursor:not-allowed;pointer-events:none}
.vote-closed .upcoming-badge{border-color:#ffffff8a;color:#fff;background:transparent}
.vote-nav-closed{opacity:.55;cursor:not-allowed}
/* Ponencias: bloque compacto y estático (sin columna fija ni centrado vertical). */
.panels{min-height:0;align-items:start}
.panel-index{position:static;min-height:auto;padding-block:56px}
.panel-index h2{font-size:clamp(30px,3vw,40px);margin-bottom:22px}
.panel-detail{justify-content:flex-start;padding-block:56px}
.panel-detail-top{margin-bottom:0}
.panel-detail h3{font-size:clamp(26px,2.6vw,36px);margin:12px 0 10px;max-width:none;line-height:1.08}
.panel-focus{font-size:14px;margin:0 0 8px}
.panel-description{font-size:13px;line-height:1.55;max-width:72ch;margin:0 0 14px}
.panel-moderator{margin:0 0 12px}
.panel-tags{margin:0 0 18px}
.paper-status-grid{display:none}
.panel-detail ol.paper-list{gap:8px}
.paper-list li.paper-card{padding:12px 14px!important}
.paper-card-top{margin-bottom:6px}
.paper-heading strong{font-size:14px;line-height:1.3}
.paper-heading{gap:3px}
@media (max-width:900px){.panel-index,.panel-detail{padding-block:40px}}
</style>
"""
html = html.replace("</head>", css + "</head>", 1)

open(OUT, "w", encoding="utf-8").write(html)
print("ajustes aplicados:", len(schedule), "filas de programa")
