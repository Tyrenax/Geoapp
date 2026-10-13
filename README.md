# Geo Atlas

Un jeu pour apprendre la géographie du monde, dans le style d'un atlas d'explorateur : drapeaux, position des pays
sur la carte et capitales, pour environ 250 pays et territoires. Chaque pays a une fiche (carte d'identité, lettres
de plaque, faits historiques) et un carnet garde tous les faits découverts. La révision espacée ramène ce qu'on
oublie, et chaque erreur s'accompagne d'une astuce pour retenir.

Les faits historiques (plus de 1 700) sont tirés de Wikipédia, avec la citation exacte de l'article et son lien.

## Jouer

Il faut [Node.js](https://nodejs.org) (version 22 ou plus) et [Python 3](https://www.python.org).

**Windows** : double-cliquer sur `Lancer-Geo-Atlas.bat`. Au premier lancement, il installe et compile le jeu
(une minute environ), puis l'ouvre dans le navigateur à l'adresse http://127.0.0.1:8405. Fermer la fenêtre noire
arrête le jeu.

**Autres systèmes** :

```sh
cd web
npm ci
npm run build
python3 -m http.server 8405 --bind 127.0.0.1 --directory dist
```

puis ouvrir http://127.0.0.1:8405.

La progression est enregistrée dans le navigateur, pour cette adresse : garder toujours la même.

## Développement

- `web/` : le jeu (Vite, TypeScript, Svelte 5, d3-geo). `npm run dev`, `npm test` (unitaires), `npm run e2e`
  (Playwright), `npm run check` (types).
- `data/` : pays, géométries, drapeaux et faits ; `tools/data/build_web.py` les copie dans `web/public/data`.
- `tools/data/` : construction des données (voir `tools/data/README.md`).
- `tools/facts/` : rédaction et vérification des faits ; `verify_facts.py` contrôle que chaque citation figure mot
  pour mot dans l'article Wikipédia.
- `docs/` : architecture et choix de design.

## Sources et licences des données

| source | usage | licence |
|---|---|---|
| Wikipédia FR/EN | textes des faits (citations), noms, plaques d'immatriculation | CC BY-SA 4.0 |
| Wikidata | données structurées | CC0 |
| Wikimedia Commons | drapeaux SVG (licence de chaque fichier dans `data/flags/LICENSES.json`) | surtout domaine public |
| Natural Earth | géométries des pays | domaine public |
| lukes/ISO-3166-Countries-with-Regional-Codes | liste ISO 3166-1 et régions | CC BY-SA 4.0 |
| mledoze/countries | contrôle des données | ODbL |
| anki-geo/ultimate-geography | contrôle des capitales, drapeaux qui se ressemblent | domaine public |

Les textes issus de Wikipédia restent sous CC BY-SA 4.0 ; chaque fait indique l'article d'où il vient.
