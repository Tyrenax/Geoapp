# Style des faits — Geo Atlas

Le joueur lit un fait juste après avoir répondu : il doit apprendre une chose vraie, précise et
qu'il aura envie de raconter. Le jeu affiche déjà le nom, la capitale, le continent et le drapeau :
un fait ne les répète pas.

## Ton
- Français simple et vivant, phrases courtes, présent de narration permis. Pas d'emphase creuse
  (« fascinant », « incroyable », « riche histoire »), pas de point d'exclamation.
- Concret : un nom, une date, un lieu, une cause, une conséquence. Une idée par fait.
- Écrit avec nos mots : la citation prouve, elle ne se recopie pas dans le texte.
- Neutre sur les sujets disputés : on décrit qui revendique quoi, sans trancher.
- Rien de périssable : pas de dirigeant en poste, pas de population « actuelle », pas de « récemment ».

## Longueurs
| Champ | Longueur | Rôle |
|---|---|---|
| `title` | 3 à 9 mots | concret, pas une question, pas de point final |
| `short` | 1 à 2 phrases, ≤ 280 caractères | l'accroche montrée après la réponse |
| `long` | 1 à 3 paragraphes, ≤ 1 200 caractères | le contexte de « Approfondir » (au moins 2 faits sur 5) |
| `quote` | 1 à 3 phrases contiguës | la preuve, copiée par programme depuis le cache |

## Contenu d'une entité
- 4 à 6 faits, dont au moins 3 `histoire` ; puis géographie, culture, `drapeau`.
- 1 à 3 `capital_facts` : origine du nom, fondation, pourquoi elle est capitale.
- Tout nombre de 3 chiffres ou plus du texte figure dans une citation du même fait.
- `tips` : `position` (voisins, forme, mer, repère), `flag` (couleurs, ordre, motif, et ce qui le
  distingue de ses sosies), `capital` (image mnémotechnique, ludique mais vraie).

## Exemples
Mauvais (paraphrase du résumé, rien à retenir) :
> **La Bolivie, pays d'Amérique du Sud** — La Bolivie est un pays enclavé d'Amérique du Sud.

Bon (une cause, une date, une conséquence) :
> **Un pays nommé d'après son libérateur** — À l'indépendance, les députés donnent au pays le nom
> de Simón Bolívar, le général vénézuélien qui a mené la lutte contre l'Espagne.

Mauvaise astuce (vague) : « Le drapeau a trois bandes. »
Bonne astuce : « Rouge, jaune, vert de haut en bas. Le Ghana a les mêmes couleurs, mais avec une
étoile noire au centre là où la Bolivie a son blason, et seulement sur son drapeau d'État. »

## Méthode
1. Mettre l'article en cache (`tools/data/wiki_cache.py fetch <url>`), le lire.
2. Choisir les faits, puis trouver la citation avec `tools/facts/quote.py` (recherche dans le texte
   en cache et copie exacte, jamais retapée).
3. Rédiger, puis `tools/facts/verify_facts.py <ID>` à zéro erreur.

Sosies de drapeaux : `ref/flag_similarity.csv` (anki-geo/ultimate-geography, domaine public), seulement
43 drapeaux. Pour les autres, on cherche nous-mêmes les sosies, et chaque couleur ou ordre écrit dans
une astuce est contrôlé dans l'article du drapeau.
