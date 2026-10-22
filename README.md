# Učebné materiály

Statické výťahy z učiva pre základnú školu. Nie sú interaktívne: dajú sa prehliadať na mobile, tablete aj počítači a vytlačiť na A4 na výšku.

Web: https://jasvarc.github.io/ucebne-materialy/

Interaktívne animácie sú v samostatnom repozitári: https://jasvarc.github.io/animacie/

## Štruktúra

```
generate_index.py                  generuje rozcestníky (spúšťa sa automaticky pri pushi)
.github/workflows/pages.yml        nasadenie na GitHub Pages
assets/styl.css                    spoločné štýly a farebná paleta (obrazovka aj tlač A4)
_sablona/index.html                prázdna šablóna výťahu na kopírovanie
matematika/5-rocnik/zlomky/        jedna téma = jeden priečinok s index.html
```

Cesta k téme má tvar `oblast/rocnik/tema/index.html`. Názvy priečinkov píš bez diakritiky a medzier, malými písmenami (`matematika`, `5-rocnik`, `zlomky`, viacslovné `slovensky-jazyk`).

## Rozcestníky sa generujú samé

Súbory `index.html` na úrovni koreňa, oblasti a ročníka sa **neukladajú do repozitára**. Pri každom pushi ich vytvorí `generate_index.py` v GitHub Action:

- `/` všetky oblasti, ročníky a témy na jednej stránke,
- `/matematika/` ročníky danej oblasti,
- `/matematika/5-rocnik/` témy daného ročníka.

Pravidlá:

- téma je každý priečinok na tretej úrovni, v ktorom je `index.html`,
- názov odkazu je `<title>` z `index.html` témy,
- ročník `5-rocnik` sa zobrazí ako „5. ročník“ a ročníky sa radia číselne,
- priečinky začínajúce na `_` alebo `.` sa ignorujú (`_sablona`),
- názov oblasti (napr. „Biológia“) je v zozname `SUBJECTS` v `generate_index.py`; neuvedená oblasť dostane názov z priečinka.

Lokálny náhľad: `python generate_index.py` (vygenerované súbory sú v `.gitignore`).

## Pridanie novej témy

1. Skopíruj `_sablona/index.html` do `oblast/rocnik/tema/index.html`.
2. Uprav `<title>`, nadpis, ročník a obsah. Cesty `../../../assets/styl.css` nemeň.
3. V `<body data-oblast="...">` nastav názov priečinka oblasti (určuje farbu akcentu).
4. Nahraj zmeny na GitHub. Stránka aj rozcestníky sa aktualizujú do 1–2 minút.

Rozcestník sa nikde ručne nemení.

## Farby

Paleta zodpovedá projektu animácie: tmavé pozadie, zlatý akcent a farba akcentu podľa oblasti. Všetko je v `assets/styl.css`. Farba oblasti je v pravidle `[data-oblast="..."]`. Nová oblasť bez pravidla dostane zlatý akcent; ak chceš inú farbu, pridaj riadok do `styl.css` (a názov do `SUBJECTS` v `generate_index.py`).

## Tlač na A4

Každá téma má tlačidlo **Vytlačiť**. Pri tlači sa použije svetlá verzia bez navigácie (tmavé pozadie by minulo toner). V okne tlače nastav:

- Papier: A4, orientácia na výšku
- Mierka: 100 %
- Hlavičky a päty: vypnúť
- Pozadie (grafika): zapnúť, inak sa nevytlačia farebné rámčeky

Na uloženie do PDF vyber v okne tlače tlačiareň „Uložiť ako PDF“.

## Nastavenie GitHub Pages (jednorazovo)

V repozitári: Settings → Pages → Build and deployment → Source: **GitHub Actions**. Bez toho sa rozcestníky nevygenerujú.
