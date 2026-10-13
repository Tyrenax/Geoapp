# Geo Atlas — architecture et contrat

Jeu local pour progresser en géographie : drapeaux, placement sur la carte, capitales,
avec des faits historiques sourcés et vérifiés. Tout en français.

Décisions de Josca (12 oct. 2026) :
- appli web locale, rendu « jeu » (pas un site vitrine) ;
- direction visuelle **atlas d'explorateur** (parchemin, encre, boussole, cartouches) ;
- périmètre : **~250 entités** = codes ISO 3166-1 (249) + Kosovo (XKX) ;
  états souverains par défaut, territoires activables ;
- progression : **révision espacée**, **stats par pays** (carte de maîtrise),
  **astuces pour retenir** quand on rate (position, drapeau, capitale).
  Pas d'XP, pas de chrono.

## Ce qui rend le jeu original (vision de Josca, à respecter)

Il existe déjà des quiz de géographie (Seterra, quiz de drapeaux, paquet Anki
« Ultimate Geography »). On ne les copie pas. Ce qu'on fait de différent :
- **La carte se dessine à mesure qu'on apprend.** Au départ, le monde est une
  *terra incognita* de parchemin : côtes à peine esquissées, pays non tracés.
  Chaque entité maîtrisée est « encrée » (contour, lavis de couleur, nom calligraphié).
  La carte de maîtrise n'est pas un écran de stats à part : c'est l'écran principal,
  ton atlas personnel. Les pays « à revoir » pâlissent comme une encre qui passe.
- **Chaque réponse apprend quelque chose de vrai** : un fait historique sourcé
  (citation vérifiée dans Wikipédia), « Approfondir », lien vers l'article.
- **Une erreur donne une astuce** pour retenir (position, drapeau, capitale), écrite pour le pays.
- Univers visuel d'**atlas d'explorateur** venu des cartes anciennes (gravure, hachures,
  cartouches, rose des vents, sceaux), pas d'un thème « parchemin » générique.

Lancement : `cd web && npm run build && python -m http.server -d dist 8405`
puis http://localhost:8405 (en dev : `npm run dev`).
Rien n'est publié en ligne.

## Arborescence et propriétaires

Un seul arbre de travail. **Chaque rôle n'écrit que dans ses dossiers.**
Les rôles ne commitent pas : c'est le coordinateur qui commite.

Rôles = sessions Claude (se joindre par SendMessage avec ces noms) :
- coordinateur : `documents-45`
- Données : `documents-71` — brief `docs/briefs/donnees.md`
- Front : `documents-a8` — brief `docs/briefs/front.md`
- Faits : `documents-5d` — brief `docs/briefs/faits.md`

| Dossier | Propriétaire | Contenu |
|---|---|---|
| `tools/data/` | Données | scripts Python de collecte, de construction et de contrôle |
| `data/countries.json`, `data/borders.json` | Données | données canoniques générées |
| `data/geo/` | Données | géométries (TopoJSON) |
| `data/flags/` | Données | SVG des drapeaux |
| `cache/` (ignoré par git) | Données | téléchargements bruts, textes Wikipédia en cache |
| `tools/facts/verify_facts.py` | Coordinateur | contrôle des faits (écrit par quelqu'un d'autre que le rédacteur) |
| `tools/facts/` (le reste) | Faits | outils de rédaction |
| `data/facts/<ID>.json` | Faits | faits, faits sur la capitale, astuces : un fichier par entité |
| `web/` sauf `web/public/data/` | Front | appli Vite + TypeScript |
| `web/public/data/` | Données (`tools/data/build_web.py`) | données servies au jeu, régénérées, jamais éditées à la main |
| `docs/` | Coordinateur | ce contrat, notes |

Python : `C:\Users\Josca\.venvs\data\Scripts\python.exe` (pandas, numpy, etc.).
Le Python système est nu. Node 24 et npm sont présents.

## Cache Wikipédia (`cache/wiki/`, propriété de Données)

- URL normalisée : `https://<lang>.wikipedia.org/wiki/<Titre>`, titre décodé (pas de `%xx`),
  espaces → `_`, après résolution des redirections. C'est cette URL qu'on met dans les sources.
- `cache/wiki/<lang>/<Titre sûr pour Windows>.txt` : texte brut de l'article (UTF-8).
- `cache/wiki/index.json` : `{ "<url normalisée>": {"file": "cache/wiki/fr/….txt", "revid": 123, "fetched": "2026-10-12"} }`
  (chemin relatif à la racine du repo). Les URL d'avant redirection peuvent figurer aussi, pointant sur le même fichier.
- CLI : `python tools/data/wiki_cache.py fetch <url>…` et `… path <url>`.

## Sources de recoupement

- Wikidata (CC0) : source principale des données structurées.
- `mledoze/countries` (ODbL) : contrôle uniquement.
- `anki-geo/ultimate-geography` (domaine public, `src/data/*.csv`, colonnes `:fr`) :
  contrôle des capitales, et liste des sosies de drapeaux (`flag_similarity.csv`) à exploiter
  pour les distracteurs et les astuces drapeau. Nos textes restent les nôtres.

## Identifiant

`id` = code ISO 3166-1 alpha-3 en majuscules (`FRA`, `GRL`, `XKX` pour le Kosovo).
Il sert de nom de fichier partout : `data/facts/FRA.json`, `data/flags/FRA.svg`.

## `data/countries.json`

Tableau trié par `id`. Un objet par entité :

```jsonc
{
  "id": "BOL",
  "iso2": "BO",
  "qid": "Q750",                       // Wikidata
  "kind": "etat",                      // "etat" | "territoire"
  "sovereign": null,                   // territoire : id de l'État dont il dépend ("DNK" pour GRL)
  "status_fr": null,                   // territoire : « territoire autonome du Danemark », etc.
  "name_fr": "Bolivie",
  "name_official_fr": "État plurinational de Bolivie",
  "article_fr": "la",                  // article défini : le, la, l', les, "" (pour « la Bolivie »)
  "aliases_fr": ["Bolivie"],           // variantes acceptées en saisie libre (sans accents gérés côté jeu)
  "continent": "amerique-sud",         // afrique | amerique-nord | amerique-sud | asie | europe | oceanie | antarctique
  "subregion_fr": "Amérique du Sud",
  "capitals": [                        // au moins une ; plusieurs si cas réel (Bolivie, Afrique du Sud…)
    { "name_fr": "Sucre", "role_fr": "capitale constitutionnelle", "qid": "Q…", "lat": -19.04, "lon": -65.26,
      "aliases_fr": ["Sucre"], "wiki_fr": "https://fr.wikipedia.org/wiki/Sucre_(Bolivie)" },
    { "name_fr": "La Paz", "role_fr": "siège du gouvernement", "...": "..." }
  ],
  "quiz_capital": "Sucre",             // la réponse principale ; les autres capitales sont aussi acceptées
  "population": 12000000,
  "population_year": 2024,
  "area_km2": 1098581,
  // ---- carte d'identité : tous facultatifs, null si inconnu ou sans objet (jamais inventé)
  "plate_code": ["BOL"],               // code international des véhicules enregistré à l'ONU (Convention de Vienne) ;
                                       // null si aucun code enregistré ; un territoire ne reprend jamais celui de sa métropole
  "driving_side": "droite",            // "droite" | "gauche"
  "currencies": [{ "code": "BOB", "name_fr": "boliviano", "symbol": "Bs" }],  // monnaie(s) officielle(s) ; symbol peut être null
  "languages_fr": ["espagnol", "…"],   // langues officielles, en minuscules (langues des signes non listées)
  "demonym_fr": "Bolivien",            // gentilé, masculin singulier, chaque partie capitalisée (« Sud-Africain »)
  "calling_code": "+591",              // indicatif ; plusieurs séparés par « , »
  "tld": ".bo",                        // domaine national en lettres latines ; plusieurs séparés par « , »
  "highest_point": { "name_fr": "Nevado Sajama", "elevation_m": 6542 },  // seulement si Wikidata et l'article FR concordent ; générique français en minuscule (« mont Blanc »), générique étranger gardé (« Pico Duarte »)
  "motto_fr": null,                    // devise en français, si elle existe
  // ----
  "label": { "lat": -16.7, "lon": -64.7 },   // point d'étiquette / marqueur pour les petites entités
  "small": false,                      // trop petit pour être cliqué sur la carte → marqueur rond
  "neighbors": ["ARG", "BRA", "CHL", "PRY", "PER"],
  "wiki_fr": "https://fr.wikipedia.org/wiki/Bolivie",
  "wiki_en": "https://en.wikipedia.org/wiki/Bolivia",
  "flag": "flags/BOL.svg",
  "flag_wiki_fr": "https://fr.wikipedia.org/wiki/Drapeau_de_la_Bolivie",
  "quizzable": true                    // false : Antarctique, zones sans État…
}
```

Chaque valeur clé (capitale, continent, voisins, drapeau) est **recoupée par une seconde
source** dans `tools/data/check_data.py` ; les désaccords sont listés dans
`data/DATA_REPORT.md` et tranchés, pas ignorés.

Carte d'identité (`tools/data/identity.py`) : Wikidata en source principale (P1622, P38, P37, P1549, P474, P78,
P610/P2044, P1451), sauf la plaque, prise dans la liste des codes enregistrés à l'ONU (tableau Wikipédia EN
« International vehicle registration code »). Recoupements : mledoze/countries (monnaies, langues, gentilé,
indicatif, domaine ; il ne fournit jamais de valeur), Wikipédia EN « Left- and right-hand traffic » (sens de
circulation), article Wikipédia FR de l'entité (point culminant : nom et altitude à 1 % près, altitude de l'article
retenue). Corrections motivées dans `curation.IDENTITY_OVERRIDE`.

## `data/facts/<ID>.json`

```jsonc
{
  "id": "BOL",
  "facts": [                           // au moins 4, cible 5-6
    {
      "id": "BOL-1",
      "topic": "histoire",             // histoire | geographie | culture | politique | economie | drapeau
      "era": "1825",                   // optionnel : année ou période, pour trier
      "title": "Un pays nommé d'après Simón Bolívar",
      "short": "1 à 2 phrases, montrées juste après une réponse.",
      "long": "Optionnel : un ou plusieurs paragraphes pour « Approfondir ».",
      "sources": [
        {
          "url": "https://fr.wikipedia.org/wiki/Bolivie",
          "quote": "extrait EXACT du texte en cache qui prouve le fait (langue de l'article)"
        }
      ]
    }
  ],
  "capital_facts": [ /* même format, 1 à 3 faits sur la capitale ; id "BOL-C1" */ ],
  "tips": {
    "position": "Astuce pour retrouver le pays sur la carte (voisins, forme, repères).",
    "flag": "Astuce pour reconnaître le drapeau, et le distinguer de ses sosies.",
    "capital": "Moyen mnémotechnique pour la capitale."
  }
}
```

Règles de vérité, contrôlées par `tools/facts/verify_facts.py` :
1. chaque `quote` se trouve **mot pour mot** (espaces normalisés) dans le texte en cache de l'article `url` ;
2. chaque nombre de 3 chiffres ou plus (années, chiffres) présent dans `title`, `short` ou `long`
   apparaît dans au moins une `quote` du même fait ;
3. les faits sont **rédigés avec nos mots** (pas de copier-coller de Wikipédia au-delà des citations de preuve) ;
4. pas de fait sans source ; pas de source hors du cache (le cache est la preuve rejouable).

## `web/public/data/` (généré par `tools/data/build_web.py`)

- `countries.json` : copie allégée de `data/countries.json` ;
- `world.topo.json` : géométries simplifiées, objet `countries`, propriété `id` = notre id ;
- `flags/<ID>.svg` ;
- `facts/<ID>.json` : chargés à la demande.

## Le jeu (vue d'ensemble, détails au Front)

- **Drapeaux** : drapeau → nom (choix multiple ou saisie avec complétion), et nom → drapeau.
- **Carte** : « Où est la Bolivie ? » → cliquer ; et pays surligné → le nommer.
- **Capitales** : pays → capitale, capitale → pays, placer la capitale.
- Après chaque réponse : un fait court, « Approfondir » (texte long + autres faits), lien Wikipédia.
- Après une erreur : l'astuce du mode (position, drapeau ou capitale) et la bonne réponse montrée.
- Révision espacée par couple (entité, mode), stockée en `localStorage`.
- Carte de maîtrise : chaque pays coloré selon son taux de réussite, par mode.
- Atlas : fiche consultable de chaque entité (tous les faits, sources, liens).
- Filtres : continent, inclure les territoires.
