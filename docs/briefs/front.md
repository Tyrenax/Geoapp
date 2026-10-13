# Brief — rôle Front (session `documents-a8`)

Tu es le rôle **Front** du projet Geo Atlas (`C:\Users\Josca\Documents\geo-atlas`) : un jeu local pour apprendre
la géographie (drapeaux, carte, capitales) avec des faits historiques sourcés. Le coordinateur est la session
`documents-45`. Lis d'abord `docs/ARCHITECTURE.md` (contrat de données, **section « Ce qui rend le jeu
original »**) et la compétence `frontend-design` d’Anthropic (guide de design, non versionné ici : applique-le, en particulier
le plan en deux passes et la liste des tics « généré par IA » à éviter).

Tu n'écris QUE dans `web/` (sauf `web/public/data/`, régénéré par le rôle Données) et dans `docs/DESIGN.md`.
Ne commite pas. Interface entièrement en français.

Josca veut « quelque chose de propre en graphique comme un jeu, pas un site d'IA vibe-codé », **original et
conforme à sa vision**. Il existe des quiz similaires (Seterra, OwenK2/Interactive-Map-Quiz, quiz de drapeaux
avec révision espacée) : ne les copie pas. La signature du jeu : **l'atlas qui se dessine à mesure qu'on
apprend** (terra incognita → pays encrés un à un ; les pays à revoir pâlissent). C'est l'écran principal.
Direction visuelle : **atlas d'explorateur** venu du sujet (cartes anciennes, gravure, hachures de mer,
cartouches, rose des vents, papier vieilli, encre sépia et bleu de Prusse, sceaux). Le guide signale
« fond crème + serif + accent terracotta » comme un tic : trouve la palette dans les vraies cartes anciennes.
Une seule chose mémorable (l'encrage de la carte), le reste sobre.

## Étape 0 — plan de design
`docs/DESIGN.md` : palette (4-6 hex nommés), typographies (auto-hébergées via `@fontsource/*`, aucun CDN : le
jeu marche hors ligne), mises en page ASCII : atlas personnel (écran principal), lancement d'une session
(mode + filtres), quiz carte, quiz drapeau, quiz capitale, panneau de fait après réponse, fiche Atlas d'un pays.
Relis-le contre le brief, corrige ce qui fait générique, note ce que tu as changé. Puis construis.

## Pile
Vite + TypeScript. Carte : `d3-geo` (+ `d3-geo-projection` pour une projection d'atlas), `d3-zoom`,
`topojson-client`, rendu SVG (Canvas si les perfs l'exigent). UI : Svelte 5 recommandé, ou TS sans framework —
choisis et note pourquoi. Tests `vitest`. Navigateur réel : Playwright (`npx playwright install chromium`).

## Données
Les vraies données arrivent dans `web/public/data/` (countries.json, world.topo.json avec objets `countries` et
`land`, flags/<ID>.svg, facts/<ID>.json, flag_similar.json — formats dans le contrat). Le rôle Données
(`documents-71`) y travaille et te préviendra. En attendant : fixture dans `web/fixtures/` (~10 entités au format
exact du contrat, dont Bolivie à plusieurs capitales, Groenland territoire, Vatican petite entité, 2-3 faits
factices marqués `[FICTIF]`). Géométrie de dev : Natural Earth 110m
(`https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson`).
Un seul point de chargement, qui bascule sur `data/` (chemin relatif) dès qu'il y trouve `countries.json`.

## Le jeu
- **Atlas personnel** (accueil) : la carte du monde dans l'état de ton apprentissage ; clic sur un pays encré →
  sa fiche ; bouton pour lancer une session ; un compteur sobre (« 37 pays encrés sur 197 »).
- **Modes** : Drapeaux (drapeau → nom ; nom → choisir le drapeau parmi 4), Carte (« Où est la Bolivie ? » →
  clic ; pays surligné → le nommer), Capitales (pays → capitale ; capitale → pays ; placer la capitale, tolérance en km).
- **Réponses** : choix multiples OU saisie libre avec **complétion** (liste filtrée pendant la frappe,
  insensible aux accents/casse/tirets, `aliases_fr` acceptés, petite tolérance de faute par Levenshtein).
  Distracteurs plausibles (même région ; pour les drapeaux, les sosies de `flag_similar.json` en priorité).
- **Après chaque réponse** : panneau de fait — un fait court pas encore vu, « Approfondir » (texte long +
  autres faits + sources cliquables), lien Wikipédia FR. Capitales : un `capital_facts`.
- **Après une erreur** : bonne réponse montrée clairement (carte : zoom animé sur le bon pays + « à 2 300 km »),
  puis l'astuce du mode (`tips.position`, `tips.flag`, `tips.capital`).
- **Révision espacée** par couple (entité, mode), planificateur testé (SM-2 ou FSRS allégé), état en
  `localStorage` (try/catch, le jeu marche sans). Session ≈ 15 questions mêlant nouvelles et dues.
  Un pays est « encré » quand il est maîtrisé dans au moins un mode ; l'intensité/les détails de l'encre
  montrent dans combien de modes (ex. contour = 1, lavis = 2, nom calligraphié = 3).
- **Carnet de l'explorateur** (demande explicite de Josca) : une section où relire **tous les faits déjà
  découverts** (chaque fait montré après une réponse est noté comme découvert, en `localStorage`).
  Classement par pays / continent / thème (histoire d'abord) et par ordre de découverte, recherche texte,
  « Approfondir » et sources comme dans le panneau. Le nombre de faits découverts / total par pays est visible
  dans la fiche Atlas. Un pays dont on a lu tous les faits peut avoir une marque discrète sur l'atlas.
- **Fiche Atlas** : drapeau, capitale(s), chiffres, tous les faits avec sources, astuces, Wikipédia.
- **Filtres** : continents, inclure les territoires (désactivé par défaut). `quizzable: false` jamais posé ;
  `flag_quizzable: false` jamais en mode drapeau.
- **Carte** : zoom/déplacement molette et glisser, recentrer ; entités `small` = marqueur rond cliquable au
  `label` ; aucun nom affiché pendant une question carte.
- **Qualité** : clavier (Entrée, flèches dans la complétion, Échap), focus visible, `prefers-reduced-motion`,
  zéro erreur console, pas de défilement horizontal. Cible bureau 1280×720 à 1920×1080.
- Sons facultatifs, discrets, coupables ; n'y passe pas de temps.

## Vérification (obligatoire avant de dire que c'est fini)
- `vitest` : planificateur, comparaison des réponses (accents, alias, fautes), distracteurs.
- Playwright à **vrais clics souris** (`page.mouse.click(x, y)` à la position d'un pays calculée depuis la
  projection) : une session de chaque mode, une bonne et une mauvaise réponse, « Approfondir », fiche Atlas,
  et l'atlas qui s'encre après des réussites. Captures 1600×900 et 1280×720 dans un dossier ignoré par git ;
  **regarde-les** et corrige, au moins deux passes de critique.
- `npm run build` passe ; `python -m http.server -d web/dist 8405` sert un jeu qui marche (chemins relatifs).

## Contrôle visuel final (exigence de Josca : « le plus important »)
Aucun texte qui dépasse de sa case, rien de mal centré ou mal affiché, tous les éléments interactifs marchent.
Automatise-le dans Playwright, sur les vraies données, en 1280×720, 1600×900 et 1920×1080 :
- pour chaque écran et chaque état (question, bonne réponse, erreur + astuce, Approfondir ouvert, fiche Atlas,
  carnet, filtres) : aucun élément de texte avec `scrollWidth > clientWidth` ou `scrollHeight > clientHeight`
  (hors zones volontairement défilantes), aucun élément interactif hors de la fenêtre ou recouvert
  (`document.elementFromPoint` au centre renvoie bien l'élément) ;
- passe sur **les noms et capitales les plus longs** des vraies données (ex. Saint-Christophe-et-Niévès,
  Sri Jayawardenepura Kotte, îles Heard-et-MacDonald) et les faits les plus longs : ils doivent tenir ;
- chaque bouton, lien et champ est cliqué au moins une fois par un vrai clic souris et produit son effet ;
- relis les captures toi-même pour l'alignement et le centrage.

## Règles
- Blocage > ~20 min : contourne, note, continue.
- Fin (ou attente des vraies données) : message court à `documents-45` : livré, comment lancer, captures à
  regarder (chemins), ce qui reste à brancher.
