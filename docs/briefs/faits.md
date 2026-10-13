# Brief — rôle Faits (session `documents-5d`)

Tu es le rôle **Faits** du projet Geo Atlas (`C:\Users\Josca\Documents\geo-atlas`) : un jeu local pour apprendre
la géographie. Après chaque réponse, le joueur lit un fait vrai et intéressant sur le pays ; quand il se trompe,
il reçoit une astuce pour retenir. Le coordinateur est la session `documents-45`. Lis d'abord
`docs/ARCHITECTURE.md` : format de `data/facts/<ID>.json`, règles de vérité, format du cache Wikipédia.

Tu n'écris QUE dans `data/facts/` et `tools/facts/` (sauf `tools/facts/verify_facts.py`, écrit par le
coordinateur : c'est ton juge, ne le modifie pas ; s'il te semble faux, écris à `documents-45`). Ne commite pas.
Python : `C:\Users\Josca\.venvs\data\Scripts\python.exe`.

Josca veut **au moins 4-5 faits historiques par pays** (parfois une phrase, parfois plusieurs paragraphes),
**sourcés et vérifiés**, avec un renvoi vers Wikipédia, plus des faits sur les capitales. C'est le cœur de ce
qui distingue ce jeu des quiz existants : la qualité et la vérité des faits comptent plus que la vitesse.

## Sources et preuve
- Le rôle Données (`documents-71`) écrit `tools/data/wiki_cache.py` et te préviendra dès qu'il marche
  (quelques minutes). Utilise-le pour mettre en cache tout article que tu cites :
  `python tools/data/wiki_cache.py fetch <url>` puis lis le fichier texte indiqué. Plus tard, il pré-remplira
  le cache pour chaque entité (`cache/wiki/by_entity/<ID>.json` : pays FR et EN, Histoire de…, capitale, drapeau).
- Chaque fait porte une ou plusieurs `sources` : URL normalisée (voir contrat) + `quote` = extrait **exact**
  et contigu du texte en cache (1 à 3 phrases) qui prouve le fait. Copie la citation par programme depuis le
  fichier (ne la retape pas), sinon une apostrophe typographique ou une espace insécable te fera échouer.
- Préfère les articles FR ; un article EN est accepté quand le FR est pauvre (la citation reste en anglais).
- `python tools/facts/verify_facts.py [ID…]` doit passer à zéro erreur. Il vérifie : citations présentes
  mot pour mot dans le cache, nombres de `title/short/long` présents dans les citations du même fait,
  schéma, nombre minimal de faits, URL en cache.

## Ce qu'on attend d'un fait
- **Rédigé avec tes mots**, en bon français, vivant et précis. Pas de paraphrase plate du premier paragraphe
  Wikipédia (« X est un pays d'Afrique de l'Ouest… ») : ça, le jeu l'affiche déjà.
- Par entité : **4 à 6 faits**, dont **au moins 3 historiques** (origine du nom, peuplement ancien, empires,
  colonisation, indépendance, événement fondateur, frontières qui ont bougé, anecdote marquante). Le reste :
  géographie remarquable, culture, drapeau (`topic: "drapeau"` : symbolique, histoire du drapeau).
- `short` : 1-2 phrases qui donnent envie d'en savoir plus. `long` (au moins 2 faits sur 5) : 1 à 3
  paragraphes de contexte. `title` : court, concret.
- **1 à 3 `capital_facts`** : origine du nom, fondation, pourquoi c'est la capitale (transfert, compromis…).
- Pas de données périssables (président actuel, population exacte de l'année) ; formulation neutre sur les
  sujets disputés (Taïwan, Kosovo, Palestine, Sahara occidental, Chypre…) ; aucune affirmation sans citation.
- Territoires et îles inhabitées : 4 faits minimum aussi (découverte, statut, histoire, nature).

## Astuces (`tips`) — montrées quand le joueur se trompe
- `position` : comment retrouver le pays sur la carte (voisins connus, forme, mer, repère : « la botte »,
  « le fin ruban entre les Andes et le Pacifique »).
- `flag` : comment reconnaître le drapeau **et le distinguer de ses sosies**. La liste des sosies de
  `anki-geo/ultimate-geography` (domaine public) est une bonne piste :
  `https://raw.githubusercontent.com/anki-geo/ultimate-geography/master/src/data/flag_similarity.csv`
  (colonne `flag similarity:fr`). Vérifie chaque couleur/ordre contre l'article du drapeau ; écris tes propres phrases.
- `capital` : moyen mnémotechnique (jeu de mots, image, lien avec l'histoire). Ludique mais jamais faux.
- Les astuces n'ont pas de `sources` obligatoires, mais toute affirmation factuelle qu'elles contiennent doit être vraie.

## Méthode
1. Écris `tools/facts/STYLE.md` (court) : ton, longueurs, exemples d'un bon et d'un mauvais fait.
2. **Pilote sur 5 entités** : FRA, BOL, JPN, NRU, GRL. Fais passer `verify_facts.py`, puis envoie un message à
   `documents-45` et **attends son retour** avant la production (pour caler le niveau une fois, pas 250 fois).
3. Production par continent (liste d'entités dans `data/countries.json`, dès que le rôle Données l'a produit) :
   Europe, Asie, Amériques, Afrique, Océanie, puis territoires. Un fichier par entité, écrit dès qu'il est fini
   (le travail survit à une interruption). `verify_facts.py` vert à la fin de chaque continent.
4. Après chaque continent : message court à `documents-45` (nombre d'entités, de faits, cas difficiles).
   Le coordinateur peut confier une partie des continents à une autre session : il te le dira.

## Règles
- Ne cite jamais de mémoire : si la citation n'est pas dans le cache, le fait n'existe pas.
- Si une entité n'a vraiment pas assez de matière dans Wikipédia FR + EN pour 4 faits, écris ce que tu peux,
  ajoute `"thin": true` au fichier et signale-la.
- Blocage > ~20 min : note-le dans `tools/facts/BLOCAGES.md` et passe à l'entité suivante.
