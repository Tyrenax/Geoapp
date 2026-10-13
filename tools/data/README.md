# tools/data — données de Geo Atlas

Python : `C:\Users\Josca\.venvs\data\Scripts\python.exe` (requests, shapely, pyproj ; `npx mapshaper` pour la
topologie). Lancer depuis la racine du dépôt. Tout téléchargement va dans `cache/` (ignoré par git) et est relu
ensuite : relancer un script ne retélécharge rien (`--refresh` pour forcer quand l'option existe).

## Ordre

| # | script | produit |
|---|---|---|
| 1 | `fetch_wikidata.py` | `cache/wikidata/entities.json` : SPARQL Wikidata brut (noms, capitales P36, population, superficie, P47, drapeaux P41/P163…) |
| 2 | `build_geo.py` | `data/geo/world.topo.json` (objets `countries`, `other`, `land`) + `cache/geo/stats.json` (label, small, voisins) |
| 3 | `fetch_flags.py` | `data/flags/<ID>.svg` + `data/flags/LICENSES.json` |
| 4 | `build_countries.py` | `data/countries.json` (Wikidata + `curation.py` + géométrie + drapeaux) |
| 5 | `check_data.py` | `data/DATA_REPORT.md` ; code 1 s'il reste un désaccord non tranché |
| 6 | `build_web.py` | `web/public/data/` (régénéré entièrement) |

`identity.py` (appelé par `build_countries.py`) : carte d'identité (plaque, circulation, monnaies, langues, gentilé,
indicatif, domaine, point culminant, devise). `sources_en.py` lit deux tableaux de Wikipédia EN en wikitexte
(codes de plaque enregistrés à l'ONU, sens de circulation) ; `python tools/data/sources_en.py` les retélécharge.

`wiki_cache.py` : cache du texte brut des articles Wikipédia (`fetch`, `path`, `text`), voir `docs/ARCHITECTURE.md`.
`curation.py` : toutes les décisions éditoriales (capitales multiples, territoires, noms, superficies, décisions
de `check_data.py`). On corrige là, jamais dans les fichiers générés.

## Limite Wikimedia

Sans contact (URL ou e-mail) dans le User-Agent, Wikimedia limite un client à 10 requêtes/min (API et
upload.wikimedia.org), limite partagée par tous les processus de la machine. `wiki_cache.py` règle la cadence
pour tous (`cache/wiki/next_slot*`) et attend après un 429. Pour passer à 200 requêtes/min, il suffit d'écrire un
contact dans `cache/ua_contact.txt` (ou la variable `GEOATLAS_UA_CONTACT`) ; ne pas le faire sans l'accord de Josca.

## Sources et licences

| source | usage | licence |
|---|---|---|
| Wikidata | données structurées (source principale) | CC0 |
| Wikipédia FR/EN (API TextExtracts) | textes en cache, article défini, nom officiel, preuves des faits | CC BY-SA 4.0 |
| Wikimedia Commons | drapeaux SVG (licence de chaque fichier dans `data/flags/LICENSES.json`) | surtout domaine public |
| Natural Earth 10m (`admin_0_map_units`, `admin_0_disputed_areas`) | géométries | domaine public |
| lukes/ISO-3166-Countries-with-Regional-Codes | liste ISO 3166-1 et régions ONU (M49) → continent | CC BY-SA 4.0 |
| mledoze/countries | contrôle seulement (capitales, régions, voisins, superficie) | ODbL |
| anki-geo/ultimate-geography | contrôle des capitales ; `flag_similarity.csv` → `flag_similar.json` | domaine public |
| lipis/flag-icons | repli des drapeaux si Commons échoue (ratio 4:3, signalé) | MIT |

## Règles de géométrie

- Unités Natural Earth sans code ISO rattachées à notre id (`build_geo.NE_TO_ID`) : Somaliland → SOM, Chypre du
  Nord → CYP, Gaza + Cisjordanie → PSE, Jan Mayen → SJM, îles mineures → UMI…
- Zones disputées (`build_geo.DISPUTED_CARVE`) : le Sahara occidental garde toute son étendue (liste ONU des
  territoires non autonomes) ; la Crimée et le Golan passent dans la couche neutre `other`, non quizzable.
- `small` : la plus grande pièce de l'entité fait moins de 15 000 km² (≈ 5 × 5 px sur une carte du monde de
  1 600 px) → marqueur rond.
- `neighbors` : frontière terrestre, polygones Natural Earth 10m à moins de 500 m, plus `curation.NEIGHBORS_ADD`.

## Règles des drapeaux

- Source : P41 Wikidata (rang préféré, sans date de fin), sauf `curation.FLAG_OVERRIDE` (fichier corrigé,
  `flag_quizzable`, `flag_note_fr`). Fichier identique à celui de l'État souverain → `flag_shared_with`.
- Hors quiz : drapeaux partagés (DROM et collectivités sans drapeau officiel propre → France…), drapeaux disputés
  (ESH, AFG, NCL, IOT), Antarctique. Le tableau complet est dans `data/DATA_REPORT.md`.
- `fetch_flags.py --trust-existing` reprend les SVG déjà téléchargés si `LICENSES.json` manque (évite 30 min de
  téléchargement sous la limite Wikimedia) ; les licences Commons sont mises en cache dans `cache/flags/licences.json`.
