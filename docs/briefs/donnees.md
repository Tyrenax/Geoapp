# Brief — rôle Données (session `documents-71`)

Tu es le rôle **Données** du projet Geo Atlas (`C:\Users\Josca\Documents\geo-atlas`), un jeu local pour
apprendre la géographie (drapeaux, carte, capitales, faits historiques sourcés). Le coordinateur est la
session `documents-45`. Lis d'abord `docs/ARCHITECTURE.md` : c'est le contrat (schéma de `data/countries.json`,
format du cache Wikipédia, propriétaires des dossiers).

Tu n'écris QUE dans `tools/data/`, `data/countries.json`, `data/borders.json`, `data/geo/`, `data/flags/`,
`data/DATA_REPORT.md`, `cache/`, `web/public/data/`. Ne commite pas. Textes affichés en français.

Outils : Python `C:\Users\Josca\.venvs\data\Scripts\python.exe` (pandas, numpy… ; tu peux y `pip install`
ce qui manque, ex. shapely, requests). Le Python système est nu. Node 24 + npm (`npx mapshaper` utilisable).
Toutes les sources ci-dessous répondent (vérifié). User-Agent explicite (`GeoAtlas/0.1 (jeu d'étude local)`),
≤ 3 requêtes Wikimedia en parallèle, réessai sur 429. Tout téléchargement va dans `cache/` et les scripts
relisent le cache au lieu de retélécharger.

## Périmètre
~250 entités = les 249 codes ISO 3166-1 + Kosovo (`XKX`). `kind` = "etat" pour les 193 membres de l'ONU +
Vatican, Palestine, Kosovo, Taïwan (197) ; "territoire" pour le reste, avec `sovereign` et `status_fr`.
Antarctique (`ATA`) : `quizzable: false`. Sahara occidental : territoire au statut disputé, formulation neutre.
Les DROM français (GUF, REU, GLP, MTQ, MYT) ont leur propre géométrie (Natural Earth `admin_0_map_units` ou 10m).

## Étape 0 — en premier, ~15 min : le cache Wikipédia
`tools/data/wiki_cache.py`, conforme au contrat (section « Cache Wikipédia ») : texte brut par l'API
`action=query&prop=extracts&explaintext=1&redirects=1` (+ `revid`), CLI `fetch <url>…` (suit les redirections,
affiche le chemin) et `path <url>`. Teste-le sur 3 articles (dont un avec redirection et un titre accentué).
Dès qu'il marche, envoie un message à `documents-5d` (rôle Faits, qui en a besoin pour commencer) et à
`documents-45` : « wiki_cache.py prêt » + exemple d'appel.

## Étape 1 — puis préviens `documents-45` et `documents-5d`
1. `tools/data/fetch_wikidata.py` : SPARQL Wikidata → noms FR, nom officiel, ISO2/ISO3, capitale(s) actuelle(s)
   (P36 sans date de fin ; garde le rôle quand il y en a plusieurs : Bolivie, Afrique du Sud, Pays-Bas,
   Eswatini, Côte d'Ivoire…), coordonnées des capitales, population (la plus récente + année), superficie,
   frontières (P47), drapeau (P41), liens fr/en, article « Drapeau de … ».
2. `data/countries.json` conforme au contrat. `article_fr` (le/la/l'/les) et `aliases_fr` (variantes usuelles :
   « USA », « Grande-Bretagne »…, les accents sont gérés côté jeu). `label`, `small`, `continent` peuvent
   venir à l'étape 2.
3. Pré-remplis le cache pour toutes les entités : article FR du pays, article EN du pays, article FR
   « Histoire de/du/de la … » quand il existe (cherche le bon titre, ne devine pas), article FR de chaque
   capitale, article FR du drapeau. Écris `cache/wiki/by_entity/<ID>.json` = liste des URL en cache.
4. Contrôle à la main les capitales piégeuses : Bolivie, Pays-Bas, Afrique du Sud, Côte d'Ivoire, Sri Lanka,
   Nauru (pas de capitale officielle), Suisse (Berne « ville fédérale »), Israël/Palestine (formulation
   neutre), Myanmar, Kazakhstan, Indonésie (Jakarta / transfert vers Nusantara : vérifie l'état actuel et note-le).
   Message à `documents-45` et `documents-5d` : « étape 1 prête » + chiffres + pièges.

## Étape 2
5. Géométries Natural Earth (`https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/…`).
   Rattache chaque géométrie à notre `id` (attention aux `-99` : France, Norvège, Kosovo, Somaliland → SOM,
   Chypre du Nord → CYP, zones disputées → non quizzables et neutres). Simplifie avec mapshaper en gardant
   la topologie : `web/public/data/world.topo.json` < 1,5 Mo, objet `countries`, propriété `id`.
   Garde aussi une couche `land` (côtes) séparée : le jeu dessine les côtes même pour les pays pas encore
   « encrés ». Calcule `label` et `small` (trop petit pour être cliqué à l'échelle monde ; seuil documenté).
6. Drapeaux en vraies proportions depuis Wikimedia Commons via P41 (`Special:FilePath/<fichier>`) dans
   `data/flags/<ID>.svg`, licences dans `data/flags/LICENSES.json`. Repli `lipis/flag-icons` seulement si
   Commons échoue (faux ratio 4:3 : signale-le). Territoires sans drapeau propre (Bouvet, Heard,
   îles mineures US…) : `flag_shared_with` + `flag_quizzable: false`. Chaque SVG doit être valide.
7. `tools/data/check_data.py` : recoupement par `mledoze/countries` et par `anki-geo/ultimate-geography`
   (`src/data/capital.csv`, colonne `capital:fr`) : capitale, région, voisins, superficie (> 10 %).
   Contrôle géométrique : chaque capitale dans son polygone (ou < 25 km pour côtières/îles). Chaque entité a
   nom, capitale (sauf cas documentés), drapeau, géométrie ou label, article FR en cache.
   Sortie `data/DATA_REPORT.md` : chaque désaccord et **la décision prise**, avec la source qui tranche.
   Code de sortie non nul s'il reste un désaccord non tranché.
8. `tools/data/build_web.py` : génère `web/public/data/` (countries.json allégé, world.topo.json, flags/,
   facts/ copiés depuis `data/facts/*.json` — 0 ou N fichiers). Idempotent. Ajoute aussi
   `web/public/data/flag_similar.json` = groupes de sosies de drapeaux (depuis `flag_similarity.csv`,
   mappés sur nos id).
9. `tools/data/README.md` court : ordre des scripts, sources et licences.

## Règles
- Teste réellement chaque script avant de dire qu'il marche ; donne les chiffres.
- Blocage > ~20 min : note-le dans `data/DATA_REPORT.md` et passe à la suite.
- Fin : message à `documents-45` (court) : livré, chiffres (entités, drapeaux, taille topojson, articles en
  cache), désaccords tranchés, ce qui reste ouvert. Préviens aussi `documents-a8` (Front) que
  `web/public/data/` est prêt.
