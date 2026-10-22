# Učebné materiály

Statické výťahy z učiva pre základnú školu. Nie sú interaktívne: dajú sa prehliadať na mobile, tablete aj počítači a vytlačiť na A4 na výšku.

Web: https://jasvarc.github.io/ucebne-materialy/

Interaktívne animácie sú v samostatnom repozitári: https://jasvarc.github.io/animacie/

## Štruktúra

```
index.html                         rozcestník (zoznam tém podľa oblasti a ročníka)
assets/styl.css                    spoločné štýly (obrazovka aj tlač A4)
_sablona/index.html                prázdna šablóna výťahu na kopírovanie
matematika/5-rocnik/zlomky/        jedna téma = jeden priečinok s index.html
```

Cesta k téme má tvar `oblast/rocnik/tema/index.html`. Názvy priečinkov píš bez diakritiky a medzier, malými písmenami (`matematika`, `5-rocnik`, `zlomky`).

## Pridanie novej témy

1. Skopíruj `_sablona/index.html` do `oblast/rocnik/tema/index.html`.
2. Uprav názov, ročník a obsah. Cesty `../../../assets/styl.css` nemeň.
3. V `index.html` v rozcestníku pridaj riadok s odkazom na novú tému.
4. Nahraj zmeny na GitHub. Stránka sa aktualizuje do 1–2 minút.

## Tlač na A4

Každá stránka má tlačidlo **Vytlačiť**. V okne tlače nastav:

- Papier: A4, orientácia na výšku
- Mierka: 100 %
- Hlavičky a päty: vypnúť
- Pozadie (grafika): zapnúť, inak sa nevytlačia farebné rámčeky

Na uloženie do PDF vyber v okne tlače tlačiareň „Uložiť ako PDF“.
