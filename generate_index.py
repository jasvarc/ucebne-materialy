#!/usr/bin/env python3
"""Vygeneruje rozcestníky (index.html) pre učebné materiály.

Spúšťa sa automaticky pri každom push (GitHub Actions), lokálne: python generate_index.py

Štruktúra: <oblast>/<rocnik>/<tema>/index.html   (napr. matematika/5-rocnik/zlomky/index.html)

Generuje sa:
- index.html                      všetky oblasti, ročníky a témy na jednej stránke
- <oblast>/index.html             ročníky danej oblasti s témami
- <oblast>/<rocnik>/index.html    témy daného ročníka

Pravidlá:
- téma = priečinok na tretej úrovni, v ktorom existuje index.html
- priečinky začínajúce na "." alebo "_" sa ignorujú (napr. _sablona)
- názov odkazu = <title> z index.html témy, inak názov priečinka
- ročník "5-rocnik" sa zobrazí ako "5. ročník", ročníky sa radia číselne
- už existujúci index.html, ktorý nevznikol týmto skriptom (chýba v ňom značka), sa neprepíše
- farby oblastí sú v assets/styl.css (atribút data-oblast), tu sú len názvy
"""
import html
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
MARK = "<!-- generate_index.py -->"
PAGE_TITLE = "Učebné materiály"
PAGE_SUB = "Výťahy z učiva – prehliadateľné na mobile, tablete aj počítači, vytlačiteľné na A4."
ANIMACIE_URL = "https://jasvarc.github.io/animacie/"

# Dobrovoľná podpora (Ko-fi), rovnaký box ako v animáciách – len na úvodnej stránke
SUPPORT_TEXT = "Robím to hlavne pre deti, ale môžete ma podporiť dobrovoľnou „kávou“ ☕"
SUPPORT_BTN = "☕ Podporiť kávou"
# Okno s platobným formulárom (Ko-fi embed). Ko-fi sa načíta až po kliknutí na tlačidlo.
KOFI_PAGE = "https://ko-fi.com/jasvarc"
KOFI_EMBED = "https://ko-fi.com/jasvarc/?hidefeed=true&widget=true&embed=true"
SUPPORT_JS = """  <script>
  (function () {
    var dlg = document.getElementById('kofi-dialog');
    var btn = document.getElementById('kofi-open');
    var frame = document.getElementById('kofi-frame');
    if (!dlg || !btn || !frame) return;
    if (typeof dlg.showModal !== 'function') {   // starý prehliadač: otvor Ko-fi v novej karte
      btn.addEventListener('click', function () {
        window.open(btn.getAttribute('data-page'), '_blank', 'noopener');
      });
      return;
    }
    btn.addEventListener('click', function () {
      if (!frame.getAttribute('src')) frame.setAttribute('src', frame.getAttribute('data-src'));
      dlg.showModal();
    });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    dlg.querySelector('.kofi-close').addEventListener('click', function () { dlg.close(); });
  })();
  </script>"""

# kľúč = názov priečinka oblasti (malými písmenami) -> zobrazovaný názov
# Čo tu nie je, dostane názov priečinka s veľkým prvým písmenom.
SUBJECTS = {
    "matematika": "Matematika",
    "slovensky-jazyk": "Slovenský jazyk",
    "anglicky-jazyk": "Anglický jazyk",
    "biologia": "Biológia",
    "geografia": "Geografia",
    "informatika": "Informatika",
    "fyzika": "Fyzika",
    "chemia": "Chémia",
    "dejepis": "Dejepis",
    "vlastiveda": "Vlastiveda",
    "prirodoveda": "Prírodoveda",
}


def fold(s: str) -> str:
    """Kľúč na radenie bez diakritiky a bez ohľadu na veľkosť písmen."""
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def pretty(name: str) -> str:
    s = re.sub(r"[-_]+", " ", name).strip()
    return s[:1].upper() + s[1:]


def oblast_label(key: str) -> str:
    return SUBJECTS.get(key.lower()) or pretty(key)


def rocnik_label(key: str) -> str:
    m = re.fullmatch(r"(\d+)-rocnik", key.lower())
    return f"{m.group(1)}. ročník" if m else pretty(key)


def rocnik_sort(key: str):
    m = re.fullmatch(r"(\d+)-rocnik", key.lower())
    return (0, int(m.group(1)), "") if m else (1, 0, fold(key))


def plural(n: int, one: str, few: str, many: str) -> str:
    if n == 1:
        return f"{n} {one}"
    if 2 <= n <= 4:
        return f"{n} {few}"
    return f"{n} {many}"


def visible_dirs(parent: Path):
    return sorted((d for d in parent.iterdir() if d.is_dir() and not d.name.startswith((".", "_"))),
                  key=lambda p: fold(p.name))


# ---------------------------------------------------------------- zber dát
# data[oblast][rocnik] = [(priecinok, nazov)]
data = {}
for o in visible_dirs(ROOT):
    for r in visible_dirs(o):
        for t in visible_dirs(r):
            page = t / "index.html"
            if not page.is_file():
                continue
            text = page.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
            title = " ".join(m.group(1).split()) if m else ""
            data.setdefault(o.name, {}).setdefault(r.name, []).append((t.name, title or t.name))

total = sum(len(ts) for rs in data.values() for ts in rs.values())
ordered_oblasti = sorted(data, key=lambda k: fold(oblast_label(k)))


def topics_of(o, r):
    return sorted(data[o][r], key=lambda it: fold(it[1]))


def count_of(o):
    return sum(len(ts) for ts in data[o].values())


# ---------------------------------------------------------------- HTML
def cards(items, prefix):
    return "\n".join(
        f'          <li><a class="card" href="{quote(prefix + name)}/">'
        f'<span class="t">{html.escape(title)}</span><span class="go" aria-hidden="true">→</span></a></li>'
        for name, title in items
    )


def rocnik_block(label, href, items, prefix):
    return (f'      <h3 class="rocnik"><a href="{quote(href)}/">{html.escape(label)}</a></h3>\n'
            f'      <ul>\n{cards(items, prefix)}\n      </ul>')


def section(o, inner, link=None):
    label = html.escape(oblast_label(o))
    head = f'<a href="{quote(link)}/">{label}</a>' if link else label
    return (f'    <section data-oblast="{html.escape(o)}">\n'
            f'      <h2><i></i>{head}<small>{count_of(o)}</small></h2>\n'
            f'{inner}\n'
            f'    </section>')


def doc(title, depth, heading, sub, summary, body, crumb=None, oblast=None):
    css = "../" * depth + "assets/styl.css"
    crumb_html = f'    <a class="crumb" href="{html.escape(crumb[1])}">← {html.escape(crumb[0])}</a>\n' if crumb else ""
    attr = f' data-oblast="{html.escape(oblast)}"' if oblast else ""
    sub_html = f'<p class="sub">{html.escape(sub)}</p>' if sub else ""
    foot = ""
    logo_html = ""
    aside_html = ""
    dialog_html = ""
    if depth == 0:
        foot = (f'    <p class="pata">Interaktívne animácie nájdeš na '
                f'<a href="{ANIMACIE_URL}">jasvarc.github.io/animacie</a>.</p>\n')
        logo_html = (f'      <img class="logo" src="logo.png" width="96" height="96" '
                     f'alt="Logo – učebné materiály, jasvarc.github.io/ucebne-materialy">\n')
        aside_html = (f'      <aside class="support card">\n'
                      f'        <p>{html.escape(SUPPORT_TEXT)}</p>\n'
                      f'        <button type="button" class="support-btn" id="kofi-open" aria-haspopup="dialog" '
                      f'data-page="{html.escape(KOFI_PAGE)}">{html.escape(SUPPORT_BTN)}</button>\n'
                      f'      </aside>\n')
        dialog_html = (f'  <dialog class="kofi" id="kofi-dialog" aria-label="Podporiť kávou">\n'
                       f'    <div class="kofi-box">\n'
                       f'      <div class="kofi-bar">\n'
                       f'        <span>Nezobrazuje sa formulár? <a href="{html.escape(KOFI_PAGE)}" target="_blank" '
                       f'rel="noopener">Otvoriť na Ko-fi</a></span>\n'
                       f'        <button type="button" class="kofi-close" aria-label="Zavrieť">×</button>\n'
                       f'      </div>\n'
                       f'      <iframe id="kofi-frame" title="Podporiť kávou – Ko-fi" allow="payment" '
                       f'data-src="{html.escape(KOFI_EMBED)}" loading="lazy"></iframe>\n'
                       f'    </div>\n'
                       f'  </dialog>\n{SUPPORT_JS}\n')
    icon = "../" * depth + "logo.png"
    return f"""<!DOCTYPE html>
{MARK}
<html lang="sk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#04060c">
  <title>{html.escape(title)}</title>
  <link rel="icon" href="{icon}">
  <link rel="stylesheet" href="{css}">
</head>
<body class="rozcestnik"{attr}>
  <div class="wrap">
{crumb_html}    <div class="hero">
      <header class="top card">
{logo_html}        <div>
          <h1>{html.escape(heading)}</h1>
          {sub_html}
          <p class="sum">{summary}</p>
        </div>
      </header>
{aside_html}    </div>
{body}
{foot}  </div>
{dialog_html}</body>
</html>
"""


def write(path: Path, text: str):
    if path.exists() and MARK not in path.read_text(encoding="utf-8", errors="ignore"):
        print(f"  preskakujem {path.relative_to(ROOT)} (ručne vytvorený súbor)")
        return False
    path.write_text(text, encoding="utf-8")
    return True


written = 0

# ---- koreň: všetko na jednej stránke
if data:
    sections = []
    for o in ordered_oblasti:
        blocks = "\n".join(
            rocnik_block(rocnik_label(r), f"{o}/{r}", topics_of(o, r), f"{o}/{r}/")
            for r in sorted(data[o], key=rocnik_sort)
        )
        sections.append(section(o, blocks, link=o))
    body = "\n".join(sections)
else:
    body = '    <p class="empty">Zatiaľ tu nie sú žiadne materiály.</p>'
summary = f"{plural(total, 'téma', 'témy', 'tém')} · {plural(len(data), 'oblasť', 'oblasti', 'oblastí')}"
written += write(ROOT / "index.html", doc(PAGE_TITLE, 0, PAGE_TITLE, PAGE_SUB, summary, body))

# ---- oblasť a ročník
for o in ordered_oblasti:
    olabel = oblast_label(o)
    rocniky = sorted(data[o], key=rocnik_sort)

    blocks = "\n".join(rocnik_block(rocnik_label(r), r, topics_of(o, r), f"{r}/") for r in rocniky)
    summ = f"{plural(count_of(o), 'téma', 'témy', 'tém')} · {plural(len(rocniky), 'ročník', 'ročníky', 'ročníkov')}"
    written += write(ROOT / o / "index.html",
                     doc(f"{olabel} – {PAGE_TITLE}", 1, olabel, "", summ, section(o, blocks),
                         crumb=("Všetky oblasti", "../"), oblast=o))

    for r in rocniky:
        rlabel = rocnik_label(r)
        items = topics_of(o, r)
        inner = f'      <ul>\n{cards(items, "")}\n      </ul>'
        body = (f'    <section data-oblast="{html.escape(o)}">\n{inner}\n    </section>')
        written += write(ROOT / o / r / "index.html",
                         doc(f"{olabel} – {rlabel} – {PAGE_TITLE}", 2, f"{olabel} · {rlabel}", "",
                             plural(len(items), "téma", "témy", "tém"), body,
                             crumb=(olabel, "../"), oblast=o))

print(f"rozcestníky vygenerované: {written} stránok, tém: {total}, oblastí: {len(data)}")
